"""
STAGE 5: DEVICE INTEGRITY & TRUST ENGINE
Detects Rooting, Emulators, and Debugging Tools
"""

# ============================================================================
# BRIDGE FUNCTION FOR MAIN.PY
# ============================================================================
def check_device(tx):
    """
    REQUIRED BY MAIN.PY: Entry point for Stage 5.
    Returns a risk score between 0.0 and 1.0.
    """
    engine = DeviceIntegrityEngine()
    return engine.analyze_device(tx)

# ============================================================================
# CORE ENGINE CLASS
# ============================================================================
class DeviceIntegrityEngine:
    def __init__(self):
        # Weightage for different device compromises
        self.risk_weights = {
            'is_rooted': 0.8,      # High risk: System files accessible
            'is_emulator': 0.9,    # Critical: Running on PC/Server instead of phone
            'is_on_call': 0.4,     # Social engineering risk (Senior Mode)
            'developer_mode': 0.3  # Moderate risk: ADB debugging active
        }

    def analyze_device(self, tx):
        """
        Calculates device risk based on hardware/software flags sent by Flutter.
        """
        risk_score = 0.0
        
        # 1. EMULATOR DETECTION (Critical)
        # Scammers use emulators to bypass hardware-bound UPI locks.
        if tx.get('is_emulator') == 1:
            risk_score = max(risk_score, self.risk_weights['is_emulator'])

        # 2. ROOT/JAILBREAK DETECTION
        # Allows malicious apps to read PINs or intercept SMS.
        if tx.get('is_rooted') == 1:
            risk_score = max(risk_score, self.risk_weights['is_rooted'])

        # 3. SENIOR MODE / VISHING SHIELD (Active Call)
        # If user is on a call while paying, it's a high risk of 'Digital Arrest' scams.
        if tx.get('is_on_call') == 1:
            risk_score += self.risk_weights['is_on_call']

        # 4. DEVELOPER OPTIONS
        if tx.get('developer_mode') == 1:
            risk_score += self.risk_weights['developer_mode']

        # Ensure risk is capped at 1.0
        return min(risk_score, 1.0)

# ============================================================================
# LOCAL TEST
# ============================================================================
if __name__ == "__main__":
    test_device = {'is_rooted': 1, 'is_on_call': 1}
    print(f"Device Risk Score: {check_device(test_device)}") # Should be 1.0 (capped)