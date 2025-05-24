#!/usr/bin/env python3
"""
test_domain.py - Tests domain SSL/TLS security using a trained model

This script:
1. Asks for a domain name
2. Runs sslscan to get the domain's SSL/TLS configuration
3. Uses a pre-trained model to predict if the configuration is secure
"""

import pickle
import subprocess
import re
import pandas as pd
import sys

def run_sslscan(domain):
    """Run sslscan on the domain and return the output"""
    print(f"Running sslscan on {domain}...")
    try:
        result = subprocess.run(
            ['sslscan', '--no-colour', domain],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error scanning {domain}: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: sslscan not found. Please install it:")
        print("  Ubuntu/Debian: sudo apt-get install sslscan")
        print("  CentOS/RHEL: sudo yum install sslscan")
        print("  macOS: brew install sslscan")
        sys.exit(1)

def extract_features(scan_output):
    """Extract security features from sslscan output"""
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
    
    # Protocol checks
    if re.search(r'SSLv2\s+enabled', scan_output, re.IGNORECASE):
        features['sslv2_supported'] = True
    
    if re.search(r'SSLv3\s+enabled', scan_output, re.IGNORECASE):
        features['sslv3_supported'] = True
    
    if re.search(r'TLSv1.0\s+enabled', scan_output, re.IGNORECASE):
        features['tlsv1_0_supported'] = True
    
    if re.search(r'TLSv1.1\s+enabled', scan_output, re.IGNORECASE):
        features['tlsv1_1_supported'] = True
    
    if re.search(r'TLSv1.2\s+enabled', scan_output, re.IGNORECASE):
        features['tlsv1_2_supported'] = True
    
    if re.search(r'TLSv1.3\s+enabled', scan_output, re.IGNORECASE):
        features['tlsv1_3_supported'] = True
    
    # Vulnerabilities
    if re.search(r'heartbleed.*vulnerable', scan_output, re.IGNORECASE):
        features['heartbleed_vulnerable'] = True
    
    if re.search(r'poodle.*vulnerable', scan_output, re.IGNORECASE):
        features['poodle_vulnerable'] = True
    
    if re.search(r'secure renegotiation.*not supported', scan_output, re.IGNORECASE):
        features['secure_renegotiation'] = False
    
    # Weak ciphers
    if re.search(r'weak\s+ciphers', scan_output, re.IGNORECASE) or re.search(r'64 bits', scan_output, re.IGNORECASE):
        features['weak_ciphers'] = True
    
    if re.search(r'RC4', scan_output, re.IGNORECASE):
        features['rc4_ciphers'] = True
    
    if re.search(r'DES', scan_output, re.IGNORECASE) or re.search(r'3DES', scan_output, re.IGNORECASE):
        features['des_ciphers'] = True
    
    # Certificate expiry
    expiry_match = re.search(r'Not valid after:\s+(.+)', scan_output)
    if expiry_match:
        try:
            import datetime
            expiry_date = expiry_match.group(1).strip()
            # Try various date formats
            for fmt in ('%b %d %H:%M:%S %Y GMT', '%Y-%m-%d', '%d %b %Y %H:%M:%S', '%b %d %Y'):
                try:
                    expiry = datetime.datetime.strptime(expiry_date, fmt)
                    days_remaining = (expiry - datetime.datetime.now()).days
                    features['cert_expiry_days'] = max(0, days_remaining)
                    break
                except ValueError:
                    continue
        except Exception:
            pass
    
    # Certificate bits
    bits_match = re.search(r'RSA (\d+) bits', scan_output) or re.search(r'ECC (\d+) bits', scan_output)
    if bits_match:
        features['cert_bits'] = int(bits_match.group(1))
    
    return features

def get_security_recommendations(features):
    """Generate security recommendations based on the detected configuration"""
    recommendations = []
    
    if features['sslv2_supported']:
        recommendations.append("Disable SSLv2 - it has serious security flaws")
    
    if features['sslv3_supported']:
        recommendations.append("Disable SSLv3 - vulnerable to POODLE attack")
    
    if features['tlsv1_0_supported']:
        recommendations.append("Consider disabling TLSv1.0 - it has vulnerabilities")
    
    if features['tlsv1_1_supported']:
        recommendations.append("Consider disabling TLSv1.1 - newer protocols are more secure")
    
    if not features['tlsv1_2_supported']:
        recommendations.append("Enable TLSv1.2 - needed for good security & compatibility")
    
    if not features['tlsv1_3_supported']:
        recommendations.append("Enable TLSv1.3 - best security and performance")
    
    if features['heartbleed_vulnerable']:
        recommendations.append("CRITICAL: Patch OpenSSL to fix Heartbleed vulnerability")
    
    if features['poodle_vulnerable']:
        recommendations.append("Update SSL/TLS to address POODLE vulnerability")
    
    if not features['secure_renegotiation']:
        recommendations.append("Enable secure renegotiation to prevent MitM attacks")
    
    if features['weak_ciphers']:
        recommendations.append("Remove weak cipher suites")
    
    if features['rc4_ciphers']:
        recommendations.append("Disable RC4 cipher suites - they are broken")
    
    if features['des_ciphers']:
        recommendations.append("Disable DES/3DES cipher suites - they are weak")
    
    if features['cert_expiry_days'] < 30:
        recommendations.append(f"URGENT: Certificate expires in {features['cert_expiry_days']} days")
    
    if features['cert_bits'] < 2048:
        recommendations.append("Use a stronger certificate (at least 2048 bits)")
    
    return recommendations

def main():
    # Load the model
    try:
        print("Loading SSL security model...")
        with open('ssl_security_model.pkl', 'rb') as f:
            model = pickle.load(f)
        with open('model_features.pkl', 'rb') as f:
            features_list = pickle.load(f)
    except FileNotFoundError:
        print("Error: Model files not found. Run train_model.py first.")
        sys.exit(1)
    
    # Get domain from user
    while True:
        print("\nEnter domain to check (or 'quit' to exit):")
        domain = input("> ").strip()
        
        if domain.lower() in ('quit', 'exit', 'q'):
            break
        
        if not domain:
            continue
        
        # Add protocol if not specified
        if not domain.startswith(('http://', 'https://')):
            domain = f"https://{domain}"
        
        # Extract hostname
        hostname = domain.split('://')[-1].split('/')[0]
        
        # Run sslscan
        scan_output = run_sslscan(hostname)
        
        # Extract features
        features = extract_features(scan_output)
        
        # Prepare features for prediction
        features_df = pd.DataFrame([features])
        features_df = features_df[features_list]  # Ensure correct order
        
        # Make prediction
        prediction = model.predict(features_df)[0]
        probability = model.predict_proba(features_df)[0].max()
        
        # Display results
        print("\n=== SECURITY ANALYSIS RESULTS ===")
        print(f"Domain: {hostname}")
        if prediction:
            print("Verdict: SECURE ✓")
        else:
            print("Verdict: INSECURE ✗")
        print(f"Confidence: {probability:.2f}")
        
        # Show key configuration details
        print("\nKey Configuration Details:")
        security_issues = []
        
        if features['sslv2_supported'] or features['sslv3_supported']:
            security_issues.append("- Old SSL protocols enabled (major security risk)")
        
        if features['heartbleed_vulnerable']:
            security_issues.append("- Vulnerable to Heartbleed")
        
        if features['poodle_vulnerable']:
            security_issues.append("- Vulnerable to POODLE")
        
        if not features['secure_renegotiation']:
            security_issues.append("- Insecure renegotiation allowed")
        
        if features['weak_ciphers'] or features['rc4_ciphers'] or features['des_ciphers']:
            security_issues.append("- Weak cipher suites enabled")
        
        if features['cert_bits'] < 2048:
            security_issues.append(f"- Weak certificate ({features['cert_bits']} bits)")
        
        if features['cert_expiry_days'] < 30:
            security_issues.append(f"- Certificate expires soon ({features['cert_expiry_days']} days)")
        
        if not security_issues:
            print("No major security issues detected.")
        else:
            for issue in security_issues:
                print(issue)
        
        # Show recommendations
        recommendations = get_security_recommendations(features)
        if recommendations:
            print("\nRecommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec}")
        else:
            print("\nNo security recommendations - configuration looks good!")

if __name__ == "__main__":
    print("SSL/TLS Security Analyzer")
    print("=========================")
    main()
    print("\nThanks for using the SSL/TLS Security Analyzer!")
