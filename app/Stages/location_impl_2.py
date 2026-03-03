"""
LOCATION CONSISTENCY & GEO-RISK ENGINE (ENHANCED)
Module: Stage 2 - Location Verification
"""

import numpy as np
import os
from datetime import datetime, timedelta
from math import radians, sin, cos, sqrt, atan2

# ============================================================================
# BRIDGE FUNCTION FOR MAIN.PY
# ============================================================================
def check_location(transaction_data):
    """
    REQUIRED BY MAIN.PY: Entry point for Stage 2.
    Returns a risk score between 0.0 and 1.0.
    """
    engine = LocationGeoRiskEngine()
    
    # We use a simplified version for the demo to ensure 100% stability
    # In the demo, mock_location is the highest signal for Layer 2.
    res = engine.analyze(transaction_data)
    # res[1] is the risk_score from the analyze() method
    return res[1]

# ============================================================================
# CORE ENGINE CLASS
# ============================================================================
class LocationGeoRiskEngine:
    def __init__(self):
        # Weights for final risk score
        self.layer_weights = {
            'geo_velocity': 0.4,
            'ip_mismatch': 0.2,
            'device_risk': 0.2,
            'historical_anomaly': 0.2
        }

    def haversine_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance in kilometers"""
        R = 6371 
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat, dlon = lat2 - lat1, lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return R * c

    def check_location_consistency(self, ip_country, sim_country, gps_country):
        """Check if IP, SIM, and GPS locations match"""
        locations = [ip_country, sim_country, gps_country]
        if len(set(locations)) > 1:
            return True, 0.7 
        return False, 0.0

    def analyze(self, transaction, user_history=None):
        """
        Simplified analyze method for master engine compatibility
        """
        risk = 0.0
        reason = "Location verified"

        # 1. Mock location/Fake GPS app detected (Highest Risk)
        if transaction.get('mock_location_enabled') == 1 or transaction.get('mock_location') == 1:
            return 'BLOCK', 1.0, 'Mock location/Fake GPS detected'

        # 2. Impossible travel velocity (e.g. > 900 km/h)
        velocity = transaction.get('velocity_kmph', 0)
        if velocity > 900 or transaction.get('is_impossible_travel') == 1:
            return 'BLOCK', 0.95, 'Impossible travel velocity detected'

        # 3. Location source mismatch (IP vs GPS)
        ip_c = transaction.get('ip_country', 'India')
        gps_c = transaction.get('gps_country', 'India')
        if ip_c != gps_c:
            risk = 0.6
            reason = 'Location mismatch (VPN/Proxy Suspected)'

        # 4. Device integrity check
        if transaction.get('is_rooted') == 1:
            risk = max(risk, 0.4)

        decision = 'BLOCK' if risk > 0.7 else 'WARN' if risk > 0.4 else 'ALLOW'
        return decision, risk, reason

# ============================================================================
# LOCAL TEST
# ============================================================================
if __name__ == "__main__":
    test_txn = {'mock_location_enabled': 1, 'amount': 500}
    print(f"Risk Result: {check_location(test_txn)}") # Should be 1.0