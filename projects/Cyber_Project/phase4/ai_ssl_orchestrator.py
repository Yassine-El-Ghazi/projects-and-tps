#!/usr/bin/env python3
"""
ai_ssl_orchestrator.py - AI-Powered SSL/TLS Attack Orchestrator

This script uses the trained ML model from Phase 3 to automatically
detect SSL/TLS vulnerabilities and launch appropriate attacks.
"""

import pickle
import subprocess
import pandas as pd
import argparse
import time
import os
import sys
import re
from datetime import datetime

class AISSLOrchestrator:
    def __init__(self):  # Fixed method name from _init_ to __init__
        self.model = None
        self.features_list = None
        self.vulnerability_map = {
            'ssl_downgrade': ['sslv2_supported', 'sslv3_supported', 'tlsv1_0_supported'],
            'cipher_downgrade': ['weak_ciphers', 'rc4_ciphers', 'des_ciphers'],
            'ssl_strip': ['secure_renegotiation', 'tlsv1_2_supported'],
            'mitm_attack': ['cert_expiry_days', 'cert_bits']
        }
        
    def load_ai_model(self):
        """Load the trained SSL security model"""
        try:
            print("[INFO] Loading AI security model...")
            with open('ssl_security_model.pkl', 'rb') as f:
                self.model = pickle.load(f)
            with open('model_features.pkl', 'rb') as f:
                self.features_list = pickle.load(f)
            print("[SUCCESS] AI model loaded successfully")
            return True
        except FileNotFoundError:
            print("[ERROR] AI model files not found. Run train_model.py first.")
            return False
        except Exception as e:
            print(f"[ERROR] Failed to load AI model: {e}")
            return False
    
    def run_sslscan(self, domain):
        """Run sslscan on the target domain"""
        print(f"[INFO] Scanning {domain} with sslscan...")
        try:
            result = subprocess.run(
                ['sslscan', '--no-colour', domain],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
                timeout=60
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] sslscan failed: {e}")
            return None
        except subprocess.TimeoutExpired:
            print("[ERROR] sslscan timeout")
            return None
        except FileNotFoundError:
            print("[ERROR] sslscan not found. Please install it:")
            print("  Ubuntu/Debian: sudo apt-get install sslscan")
            print("  CentOS/RHEL: sudo yum install sslscan")
            print("  macOS: brew install sslscan")
            return None
    
    def extract_vulnerability_features(self, scan_output):
        """Extract vulnerability features from sslscan output"""
        features = {
            'sslv2_supported': False,
            'sslv3_supported': False,
            'tlsv1_0_supported': False,
            'tlsv1_1_supported': False,
            'tlsv1_2_supported': False,
            'tlsv1_3_supported': False,
            'heartbleed_vulnerable': False,
            'poodle_vulnerable': False,
            'secure_renegotiation': True,
            'weak_ciphers': False,
            'rc4_ciphers': False,
            'des_ciphers': False,
            'cert_expiry_days': 90,
            'cert_bits': 2048
        }
        
        if not scan_output:
            return features
        
        # Protocol detection
        if re.search(r'SSLv2\s+enabled', scan_output, re.IGNORECASE):
            features['sslv2_supported'] = True
        
        if re.search(r'SSLv3\s+enabled', scan_output, re.IGNORECASE):
            features['sslv3_supported'] = True
        
        if re.search(r'TLSv1\.0\s+enabled', scan_output, re.IGNORECASE):
            features['tlsv1_0_supported'] = True
        
        if re.search(r'TLSv1\.1\s+enabled', scan_output, re.IGNORECASE):
            features['tlsv1_1_supported'] = True
        
        if re.search(r'TLSv1\.2\s+enabled', scan_output, re.IGNORECASE):
            features['tlsv1_2_supported'] = True
        
        if re.search(r'TLSv1\.3\s+enabled', scan_output, re.IGNORECASE):
            features['tlsv1_3_supported'] = True
        
        # Vulnerability detection
        if re.search(r'heartbleed.*vulnerable', scan_output, re.IGNORECASE):
            features['heartbleed_vulnerable'] = True
        
        if re.search(r'poodle.*vulnerable', scan_output, re.IGNORECASE):
            features['poodle_vulnerable'] = True
        
        if re.search(r'secure renegotiation.*not supported', scan_output, re.IGNORECASE):
            features['secure_renegotiation'] = False
        
        # Cipher analysis
        if re.search(r'weak\s+cipher|64\s+bits', scan_output, re.IGNORECASE):
            features['weak_ciphers'] = True
        
        if re.search(r'RC4', scan_output, re.IGNORECASE):
            features['rc4_ciphers'] = True
        
        if re.search(r'DES|3DES', scan_output, re.IGNORECASE):
            features['des_ciphers'] = True
        
        # Certificate analysis
        expiry_match = re.search(r'Not valid after:\s+(.+)', scan_output)
        if expiry_match:
            try:
                import datetime
                expiry_date = expiry_match.group(1).strip()
                for fmt in ('%b %d %H:%M:%S %Y GMT', '%Y-%m-%d', '%d %b %Y %H:%M:%S'):
                    try:
                        expiry = datetime.datetime.strptime(expiry_date, fmt)
                        days_remaining = (expiry - datetime.datetime.now()).days
                        features['cert_expiry_days'] = max(0, days_remaining)
                        break
                    except ValueError:
                        continue
            except Exception:
                pass
        
        bits_match = re.search(r'RSA (\d+) bits|ECC (\d+) bits', scan_output)
        if bits_match:
            features['cert_bits'] = int(bits_match.group(1) or bits_match.group(2))
        
        return features
    
    def analyze_vulnerabilities(self, features):
        """Use AI model to analyze vulnerabilities and recommend attacks"""
        if not self.model or not self.features_list:
            print("[ERROR] AI model not loaded")
            return None
        
        # Prepare features for prediction
        features_df = pd.DataFrame([features])
        features_df = features_df[self.features_list]
        
        # Get AI prediction
        is_secure = self.model.predict(features_df)[0]
        confidence = self.model.predict_proba(features_df)[0].max()
        
        print(f"\n[AI ANALYSIS] Security Status: {'SECURE' if is_secure else 'VULNERABLE'}")
        print(f"[AI ANALYSIS] Confidence: {confidence:.2f}")
        
        if is_secure:
            print("[AI RECOMMENDATION] Target appears secure - limited attack surface")
            return []
        
        # Determine specific vulnerabilities and recommend attacks
        recommended_attacks = []
        
        # Check for SSL/TLS version vulnerabilities
        if features['sslv2_supported'] or features['sslv3_supported'] or features['tlsv1_0_supported']:
            recommended_attacks.append({
                'attack': 'ssl_downgrade',
                'reason': 'Old SSL/TLS versions supported',
                'severity': 'HIGH',
                'script': 'ssl_downgrade.py'
            })
        
        # Check for weak cipher vulnerabilities
        if features['weak_ciphers'] or features['rc4_ciphers'] or features['des_ciphers']:
            recommended_attacks.append({
                'attack': 'cipher_downgrade',
                'reason': 'Weak cipher suites supported',
                'severity': 'HIGH',
                'script': 'cipher_downgrade.py'
            })
        
        # Check for SSL stripping vulnerabilities
        if not features['secure_renegotiation'] or not features['tlsv1_2_supported']:
            recommended_attacks.append({
                'attack': 'ssl_strip',
                'reason': 'Insecure renegotiation or missing TLS 1.2',
                'severity': 'MEDIUM',
                'script': 'ssl_strip.py'
            })
        
        # Check for MITM vulnerabilities
        if features['cert_expiry_days'] < 30 or features['cert_bits'] < 2048:
            recommended_attacks.append({
                'attack': 'mitm_attack',
                'reason': 'Weak or expiring certificate',
                'severity': 'MEDIUM',
                'script': 'mitm_attack.py'
            })
        
        # Check for critical vulnerabilities
        if features['heartbleed_vulnerable']:
            recommended_attacks.append({
                'attack': 'heartbleed_exploit',
                'reason': 'Heartbleed vulnerability detected',
                'severity': 'CRITICAL',
                'script': 'heartbleed_exploit.py'
            })
        
        if features['poodle_vulnerable']:
            recommended_attacks.append({
                'attack': 'poodle_exploit',
                'reason': 'POODLE vulnerability detected',
                'severity': 'HIGH',
                'script': 'ssl_downgrade.py'
            })
        
        return recommended_attacks
    
    def display_recommendations(self, attacks):
        """Display attack recommendations"""
        if not attacks:
            print("\n[AI RECOMMENDATION] No specific attacks recommended")
            return
        
        print(f"\n{'='*60}")
        print("AI-POWERED ATTACK RECOMMENDATIONS")
        print(f"{'='*60}")
        
        # Sort by severity
        severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        attacks.sort(key=lambda x: severity_order.get(x['severity'], 4))
        
        for i, attack in enumerate(attacks, 1):
            print(f"\n{i}. {attack['attack'].upper()} ATTACK")
            print(f"   Severity: {attack['severity']}")
            print(f"   Reason: {attack['reason']}")
            print(f"   Script: {attack['script']}")
    
    def execute_attack(self, attack_info, target, port=443):
        """Execute the recommended attack"""
        script_name = attack_info['script']
        
        if not os.path.exists(script_name):
            print(f"[ERROR] Attack script {script_name} not found")
            return False
        
        print(f"\n[ATTACK] Executing {attack_info['attack']} against {target}")
        print(f"[ATTACK] Reason: {attack_info['reason']}")
        
        try:
            # Build command
            cmd = ['python3', script_name, target, '-p', str(port)]
            
            # Add test flag for initial reconnaissance
            cmd.append('--test')
            
            print(f"[INFO] Running: {' '.join(cmd)}")
            
            # Execute attack script
            result = subprocess.run(cmd, timeout=300)
            
            if result.returncode == 0:
                print(f"[SUCCESS] Attack {attack_info['attack']} completed")
                return True
            else:
                print(f"[ERROR] Attack {attack_info['attack']} failed")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"[ERROR] Attack {attack_info['attack']} timed out")
            return False
        except Exception as e:
            print(f"[ERROR] Failed to execute attack: {e}")
            return False
    
    def interactive_attack_menu(self, attacks, target, port):
        """Interactive menu for selecting attacks"""
        while True:
            print(f"\n{'='*50}")
            print("ATTACK SELECTION MENU")
            print(f"{'='*50}")
            print(f"Target: {target}:{port}")
            print("\nAvailable attacks:")
            
            for i, attack in enumerate(attacks, 1):
                print(f"{i}. {attack['attack'].upper()} - {attack['severity']} - {attack['reason']}")
            
            print("\nOptions:")
            print("a. Run all attacks sequentially")
            print("r. Rescan target")
            print("v. View detailed vulnerabilities")
            print("q. Quit")
            
            choice = input("\nEnter your choice (number, a, r, v, q): ").strip().lower()
            
            if choice == 'q':
                print("[INFO] Exiting attack menu...")
                return False
            elif choice == 'r':
                print("[INFO] Initiating rescan of target...")
                return 'rescan'
            elif choice == 'v':
                self._display_detailed_vulnerabilities(target)
                continue
            elif choice == 'a':
                print("[INFO] Executing all attacks sequentially...")
                executed_attacks = []
                for attack in attacks:
                    if self.execute_attack(attack, target, port):
                        executed_attacks.append(attack)
                
                if executed_attacks:
                    print(f"[SUCCESS] Completed {len(executed_attacks)} attack(s)")
                else:
                    print("[WARNING] No attacks were successfully executed")
            elif choice.isdigit() and 1 <= int(choice) <= len(attacks):
                attack_index = int(choice) - 1
                self.execute_attack(attacks[attack_index], target, port)
            else:
                print("[ERROR] Invalid selection. Please try again.")
    
    def _display_detailed_vulnerabilities(self, target):
        """Display detailed vulnerability information about the target"""
        print(f"\n{'='*60}")
        print(f"DETAILED VULNERABILITY REPORT FOR {target}")
        print(f"{'='*60}")
        
        # Run more detailed scan commands
        print("[INFO] Running detailed vulnerability scans...")
        
        # Additional nmap scan for comprehensive SSL/TLS info
        try:
            print("\n[SCAN] Running Nmap SSL scan...")
            nmap_result = subprocess.run(
                ['nmap', '--script', 'ssl-enum-ciphers,ssl-heartbleed,ssl-poodle,ssl-ccs-injection', '-p', '443', target],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=180
            )
            if nmap_result.returncode == 0:
                print("\nNmap SSL Scan Results:")
                print("-" * 40)
                print(nmap_result.stdout)
            else:
                print("[WARNING] Nmap scan failed or not available")
        except (subprocess.SubprocessError, FileNotFoundError):
            print("[WARNING] Nmap scan failed or not available")
        
        # Wait for user acknowledgment
        input("\nPress Enter to return to the attack menu...")
    
    def generate_report(self, target, features, attacks_executed=None):
        """Generate a comprehensive security report"""
        if attacks_executed is None:
            attacks_executed = []
            
        report_dir = "reports"
        os.makedirs(report_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(report_dir, f"{target}_security_report_{timestamp}.txt")
        
        with open(report_file, 'w') as f:
            f.write(f"{'='*80}\n")
            f.write(f"SSL/TLS SECURITY ASSESSMENT REPORT\n")
            f.write(f"{'='*80}\n\n")
            
            f.write(f"Target: {target}\n")
            f.write(f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Report ID: {timestamp}\n\n")
            
            f.write(f"{'='*80}\n")
            f.write(f"VULNERABILITY ASSESSMENT\n")
            f.write(f"{'='*80}\n\n")
            
            # Write protocol support
            f.write("Protocol Support:\n")
            f.write(f"  - SSLv2: {'Supported (VULNERABLE)' if features['sslv2_supported'] else 'Not Supported (SECURE)'}\n")
            f.write(f"  - SSLv3: {'Supported (VULNERABLE)' if features['sslv3_supported'] else 'Not Supported (SECURE)'}\n")
            f.write(f"  - TLSv1.0: {'Supported (VULNERABLE)' if features['tlsv1_0_supported'] else 'Not Supported (SECURE)'}\n")
            f.write(f"  - TLSv1.1: {'Supported (MODERATE RISK)' if features['tlsv1_1_supported'] else 'Not Supported'}\n")
            f.write(f"  - TLSv1.2: {'Supported (SECURE)' if features['tlsv1_2_supported'] else 'Not Supported (VULNERABLE)'}\n")
            f.write(f"  - TLSv1.3: {'Supported (SECURE)' if features['tlsv1_3_supported'] else 'Not Supported'}\n\n")
            
            # Write cipher information
            f.write("Cipher Security:\n")
            f.write(f"  - Weak Ciphers: {'Present (VULNERABLE)' if features['weak_ciphers'] else 'Not Present (SECURE)'}\n")
            f.write(f"  - RC4 Ciphers: {'Present (VULNERABLE)' if features['rc4_ciphers'] else 'Not Present (SECURE)'}\n")
            f.write(f"  - DES/3DES Ciphers: {'Present (VULNERABLE)' if features['des_ciphers'] else 'Not Present (SECURE)'}\n\n")
            
            # Write certificate information
            f.write("Certificate Security:\n")
            f.write(f"  - Key Strength: {features['cert_bits']} bits ")
            if features['cert_bits'] >= 2048:
                f.write("(SECURE)\n")
            else:
                f.write("(VULNERABLE)\n")
            
            f.write(f"  - Days Until Expiry: {features['cert_expiry_days']} days ")
            if features['cert_expiry_days'] > 30:
                f.write("(SECURE)\n")
            else:
                f.write("(AT RISK)\n\n")
            
            # Write known vulnerabilities
            f.write("Known Vulnerabilities:\n")
            f.write(f"  - Heartbleed: {'VULNERABLE' if features['heartbleed_vulnerable'] else 'Not Vulnerable'}\n")
            f.write(f"  - POODLE: {'VULNERABLE' if features['poodle_vulnerable'] else 'Not Vulnerable'}\n")
            f.write(f"  - Secure Renegotiation: {'Supported (SECURE)' if features['secure_renegotiation'] else 'Not Supported (VULNERABLE)'}\n\n")
            
            # Overall security assessment
            security_score = 0
            max_score = 100
            
            # Calculate security score based on features
            if not features['sslv2_supported']: security_score += 10
            if not features['sslv3_supported']: security_score += 10
            if not features['tlsv1_0_supported']: security_score += 5
            if features['tlsv1_2_supported']: security_score += 10
            if features['tlsv1_3_supported']: security_score += 10
            if not features['weak_ciphers']: security_score += 10
            if not features['rc4_ciphers']: security_score += 5
            if not features['des_ciphers']: security_score += 5
            if features['cert_bits'] >= 2048: security_score += 10
            if features['cert_expiry_days'] > 30: security_score += 5
            if not features['heartbleed_vulnerable']: security_score += 10
            if not features['poodle_vulnerable']: security_score += 5
            if features['secure_renegotiation']: security_score += 5
            
            f.write(f"{'='*80}\n")
            f.write(f"SECURITY ASSESSMENT SUMMARY\n")
            f.write(f"{'='*80}\n\n")
            
            f.write(f"Security Score: {security_score}/{max_score}\n")
            
            if security_score >= 80:
                rating = "GOOD - Target has strong SSL/TLS configuration"
            elif security_score >= 60:
                rating = "MODERATE - Some improvements needed"
            elif security_score >= 40:
                rating = "POOR - Significant security issues detected"
            else:
                rating = "CRITICAL - Immediate remediation required"
                
            f.write(f"Security Rating: {rating}\n\n")
            
            # Attack recommendations
            if attacks_executed:
                f.write(f"{'='*80}\n")
                f.write(f"EXECUTED ATTACKS\n")
                f.write(f"{'='*80}\n\n")
                
                for attack in attacks_executed:
                    f.write(f"Attack: {attack['attack'].upper()}\n")
                    f.write(f"Severity: {attack['severity']}\n")
                    f.write(f"Reason: {attack['reason']}\n")
                    f.write(f"Script: {attack['script']}\n\n")
            
            # Recommendations
            f.write(f"{'='*80}\n")
            f.write(f"SECURITY RECOMMENDATIONS\n")
            f.write(f"{'='*80}\n\n")
            
            if features['sslv2_supported'] or features['sslv3_supported']:
                f.write("- Disable SSLv2 and SSLv3 protocols as they are insecure\n")
            
            if features['tlsv1_0_supported']:
                f.write("- Consider disabling TLSv1.0 as it has known vulnerabilities\n")
            
            if not features['tlsv1_2_supported']:
                f.write("- Enable TLSv1.2 to improve security\n")
            
            if not features['tlsv1_3_supported']:
                f.write("- Consider enabling TLSv1.3 for improved security and performance\n")
            
            if features['weak_ciphers'] or features['rc4_ciphers'] or features['des_ciphers']:
                f.write("- Remove support for weak cipher suites including RC4 and DES\n")
            
            if features['cert_bits'] < 2048:
                f.write("- Upgrade certificate to use at least 2048-bit keys\n")
            
            if features['cert_expiry_days'] < 30:
                f.write("- Renew SSL certificate before expiration\n")
            
            if not features['secure_renegotiation']:
                f.write("- Enable secure renegotiation\n")
            
            f.write("\n")
            f.write("For detailed remediation guidance, visit: https://ssl-config.mozilla.org/\n")
        
        print(f"[SUCCESS] Report generated: {report_file}")
        return report_file
    
    def check_attack_scripts(self):
        """Check if all required attack scripts are present"""
        required_scripts = [
            'ssl_downgrade.py',
            'cipher_downgrade.py', 
            'ssl_strip.py',
            'mitm_attack.py',
            'heartbleed_exploit.py'
        ]
        
        missing_scripts = []
        for script in required_scripts:
            if not os.path.exists(script):
                missing_scripts.append(script)
        
        if missing_scripts:
            print("[WARNING] The following attack scripts are missing:")
            for script in missing_scripts:
                print(f"  - {script}")
            print("[INFO] You may need to download or create these scripts before executing attacks.")
            return False
        
        return True

def main():
    """Main function to orchestrate SSL/TLS vulnerability scanning and attacks"""
    parser = argparse.ArgumentParser(description='AI-Powered SSL/TLS Attack Orchestrator')
    parser.add_argument('target', help='Target domain or IP address')
    parser.add_argument('-p', '--port', type=int, default=443, help='Target port (default: 443)')
    parser.add_argument('-o', '--output', help='Output report file')
    parser.add_argument('-a', '--auto', action='store_true', help='Automatically execute recommended attacks')
    parser.add_argument('-t', '--test', action='store_true', help='Test mode (do not execute actual attacks)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    args = parser.parse_args()
    
    print(f"\n{'='*70}")
    print("AI-POWERED SSL/TLS ATTACK ORCHESTRATOR")
    print(f"{'='*70}")
    print(f"Target: {args.target}:{args.port}")
    print(f"{'='*70}\n")
    
    orchestrator = AISSLOrchestrator()
    
    # Check if attack scripts are available
    orchestrator.check_attack_scripts()
    
    # Load AI model
    if not orchestrator.load_ai_model():
        print("[ERROR] Failed to load AI security model. Exiting.")
        sys.exit(1)
    
    # Track executed attacks for reporting
    executed_attacks = []
    
    # Main processing loop
    while True:
        # Run SSL scan
        scan_output = orchestrator.run_sslscan(args.target)
        if not scan_output:
            print("[ERROR] Failed to scan target. Exiting.")
            sys.exit(1)
        
        # Extract vulnerability features
        features = orchestrator.extract_vulnerability_features(scan_output)
        
        # Print verbose output if requested
        if args.verbose:
            print("\n[VERBOSE] Extracted features:")
            for feature, value in features.items():
                print(f"  - {feature}: {value}")
        
        # Analyze vulnerabilities and get attack recommendations
        recommended_attacks = orchestrator.analyze_vulnerabilities(features)
        
        # Display attack recommendations
        orchestrator.display_recommendations(recommended_attacks)
        
        if not recommended_attacks:
            print("\n[INFO] No vulnerabilities detected that can be exploited. Target appears secure.")
            break
        
        # Handle attack execution
        if args.auto:
            # Auto mode - execute all recommended attacks
            print("\n[AUTO MODE] Executing recommended attacks...")
            for attack in recommended_attacks:
                if args.test:
                    print(f"[TEST MODE] Would execute {attack['attack']} attack")
                    executed_attacks.append(attack)
                else:
                    if orchestrator.execute_attack(attack, args.target, args.port):
                        executed_attacks.append(attack)
            break
        else:
            # Interactive mode
            result = orchestrator.interactive_attack_menu(recommended_attacks, args.target, args.port)
            if result == 'rescan':
                print("[INFO] Rescanning target...")
                continue
            else:
                break
    
    # Generate final report
    report_file = orchestrator.generate_report(args.target, features, executed_attacks)
    
    print("\n[COMPLETE] SSL/TLS security assessment completed.")
    print(f"[REPORT] Final report generated: {report_file}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] An unexpected error occurred: {e}")
        sys.exit(1)
