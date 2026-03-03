"""
STAGE 1: SOURCE VERIFICATION MODULE (ENHANCED)
Verifies if payment source is legitimate
"""

import re
import os

# ============================================================================
# BRIDGE FUNCTION FOR MAIN.PY
# ============================================================================
def check_source(transaction_data):
    """
    Entry point used by main.py for the 7-Layer Shield.
    Returns a risk score between 0.0 and 1.0.
    """
    engine = SourceVerificationEngine()
    result = engine.analyze_source(transaction_data)
    return result['risk_score']

# ============================================================================
# CORE ENGINE CLASS
# ============================================================================
class SourceVerificationEngine:
    def __init__(self):
        # Known Phishing Domains for Demo
        self.blacklisted_domains = {
            'phishing-upi.tk', 'fake-paytm.ml', 'scam-gpay.ga',
            'fraudulent-pay.cf', 'suspicious-link.tk', 'fake-phonepe.gq',
            'scam-upi.ml', 'phishing-pay.tk', 'kbc-lottery.tk', 
            'prize-winner.ml', 'urgent-kyc.com', 'police-fine.net'
        }
        
        # Recognized Safe Merchants
        self.legitimate_domains = {
            'paytm.com', 'phonepe.com', 'googlepay.com', 
            'amazon.in', 'flipkart.com', 'swiggy.com'
        }
        
        self.suspicious_keywords = [
            'urgent', 'prize', 'winner', 'lottery', 'claim', 
            'verify account', 'suspended', 'act now'
        ]

    def _extract_domain(self, url):
        if not url or url == 'NA':
            return None
        try:
            # Clean protocol and extract the base domain
            url = url.replace('https://', '').replace('http://', '')
            return url.split('/')[0].lower()
        except:
            return None

    def analyze_source(self, transaction_data):
        """
        Main analysis logic
        """
        risk_score = 0.0
        payment_source = transaction_data.get('payment_source', 'unknown')
        source_url = transaction_data.get('source_url', 'NA')
        
        # 1. Source Type Risk
        if payment_source == 'qr_scan':
            risk_score = 0.05  # QR is generally safe
        elif payment_source in ['link', 'sms', 'whatsapp']:
            risk_score = 0.4   # Links have higher base risk
            
            # 2. Domain Reputation Check
            domain = self._extract_domain(source_url)
            if domain:
                if domain in self.blacklisted_domains:
                    risk_score = 1.0  # Instant block for blacklisted
                elif domain in self.legitimate_domains:
                    risk_score = 0.0  # Safe domain

            # 3. Keyword Pattern Analysis (Digital Arrest / Lottery Scams)
            if any(kw in source_url.lower() for kw in self.suspicious_keywords):
                risk_score = max(risk_score, 0.8)

        # 4. UPI Deep Link Format Check
        deep_link = transaction_data.get('deep_link', 'NA')
        if deep_link != 'NA' and not str(deep_link).startswith('upi://pay'):
            risk_score = max(risk_score, 0.9)

        return {'risk_score': round(risk_score, 2)}

# ============================================================================
# LOCAL TEST (Run this file directly to verify)
# ============================================================================
if __name__ == "__main__":
    test_scam = {
        'payment_source': 'whatsapp',
        'source_url': 'https://kbc-lottery.tk/win',
        'is_malicious_link': 1
    }
    score = check_source(test_scam)
    print(f"Test Scam Score: {score}") # Should be 1.0