import pandas as pd      
from lime import lime_tabular

class UPIDecisionExplainer:
    def __init__(self, engine):
        self.engine = engine
        # Define the features exactly as they appear in your River numeric_features
        self.feature_names = [
            'amount', 'hour_of_day', 'pin_entry_time_ms', 
            'is_rooted', 'is_emulator', 'mock_location_enabled', 
            'is_on_call', 'is_malicious_link'
        ]
        
    def explain(self, tx_dict):
        """Generates a text-based explanation of the risk score"""
        # Convert dict to list for LIME
        data_row = [float(tx_dict.get(f, 0)) for f in self.feature_names]
        
        # Simple logic-based explanation for the demo
        reasons = []
        if tx_dict.get('amount', 0) > 50000: reasons.append("High Transaction Value")
        if tx_dict.get('is_on_call') == 1: reasons.append("Vishing Risk (Active Call)")
        if tx_dict.get('is_rooted') == 1: reasons.append("Device Integrity Compromised")
        if tx_dict.get('is_malicious_link') == 1: reasons.append("Malicious QR/Link Detected")
        
        return " | ".join(reasons) if reasons else "Pattern-based Anomaly"