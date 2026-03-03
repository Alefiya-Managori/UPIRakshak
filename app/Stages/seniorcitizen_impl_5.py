"""
STAGE 5: SENIOR CITIZEN PROTECTION MODULE (ENHANCED)
Enhanced fraud protection for elderly users (65+ years)
Author: [Your Team Name]
ENHANCED VERSION with vishing detection and ML integration
"""

import numpy as np
import pickle
import os
from datetime import datetime, timedelta

class SeniorCitizenProtectionEngine:
    """
    Stage 5: Senior Citizen Fraud Protection
    
    Rationale: 60-70% of UPI fraud targets senior citizens
    
    Checks:
    1. User age-based risk assessment
    2. High-value transaction alerts for seniors
    3. New merchant warnings
    4. Social engineering pattern detection
    5. Unusual beneficiary detection
    
    NEW ENHANCEMENTS:
    - VISHING detection (is_on_call_during_transaction)
    - Emergency flag handling (is_emergency)
    - ML model integration
    - analyze() method for master engine compatibility
    """
    
    def __init__(self):
        print("👴 Initializing Senior Citizen Protection Engine")
        
        # Age thresholds
        self.SENIOR_AGE_THRESHOLD = 65  # 65+ years
        self.ELDERLY_AGE_THRESHOLD = 75  # 75+ years (extra protection)
        
        # Amount thresholds for seniors (lower than general population)
        self.SENIOR_HIGH_AMOUNT_THRESHOLD = 10000  # ₹10,000
        self.SENIOR_VERY_HIGH_AMOUNT = 25000  # ₹25,000
        self.ELDERLY_HIGH_AMOUNT_THRESHOLD = 5000  # ₹5,000 for 75+
        
        # Social engineering indicators
        self.SOCIAL_ENGINEERING_KEYWORDS = [
            'kbc', 'lottery', 'prize', 'income tax', 'refund',
            'aadhaar', 'pan', 'kyc', 'update', 'verify',
            'police', 'court', 'legal', 'arrest', 'urgent',
            'nephew', 'grandson', 'relative', 'hospital', 'emergency'
        ]
        
        # NEW: Load trained ML model
        self.ml_model = self._load_trained_model()
        self.encoders = self._load_encoders()
        
        print("✅ Senior Citizen Protection Engine Ready")
    
    def _load_trained_model(self):
        """NEW: Load trained ML model from training script"""
        model_path = 'models/stage5/senior_protection_model.pkl'
        if os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    return pickle.load(f)
            except:
                pass
        return None
    
    def _load_encoders(self):
        """NEW: Load label encoders"""
        encoder_path = 'models/label_encoders.pkl'
        if os.path.exists(encoder_path):
            try:
                with open(encoder_path, 'rb') as f:
                    return pickle.load(f)
            except:
                pass
        return None
    
    def _calculate_age(self, date_of_birth):
        """Calculate age from date of birth"""
        if isinstance(date_of_birth, str):
            dob = datetime.strptime(date_of_birth, '%Y-%m-%d')
        else:
            dob = date_of_birth
        
        today = datetime.now()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        
        return age
    
    def _is_senior_citizen(self, age):
        """Check if user is senior citizen"""
        return age >= self.SENIOR_AGE_THRESHOLD
    
    def _is_elderly(self, age):
        """Check if user is elderly (75+)"""
        return age >= self.ELDERLY_AGE_THRESHOLD
    
    def _check_age_based_risk(self, user_age):
        """Assess base risk based on user age"""
        risk_score = 0.0
        flags = []
        protection_level = 'standard'
        
        if user_age >= self.ELDERLY_AGE_THRESHOLD:
            risk_score += 0.2  # Not fraud risk, but monitoring level
            flags.append(f"🛡️ ELDERLY USER ({user_age} years) - Enhanced protection enabled")
            protection_level = 'high'
        elif user_age >= self.SENIOR_AGE_THRESHOLD:
            risk_score += 0.1
            flags.append(f"🛡️ SENIOR CITIZEN ({user_age} years) - Additional safeguards active")
            protection_level = 'medium'
        else:
            flags.append(f"✅ Standard user ({user_age} years)")
            protection_level = 'standard'
        
        return risk_score, flags, protection_level
    
    def _check_amount_for_seniors(self, amount, user_age):
        """Check if amount is unusually high for senior citizens"""
        risk_score = 0.0
        flags = []
        
        if user_age >= self.ELDERLY_AGE_THRESHOLD:
            # Elderly (75+) - Stricter limits
            if amount >= self.SENIOR_VERY_HIGH_AMOUNT:
                risk_score += 0.7
                flags.append(f"🚨 VERY HIGH AMOUNT for elderly: ₹{amount:.2f}")
                flags.append(f"   Recommended limit: ₹{self.ELDERLY_HIGH_AMOUNT_THRESHOLD}")
            elif amount >= self.ELDERLY_HIGH_AMOUNT_THRESHOLD:
                risk_score += 0.4
                flags.append(f"⚠️ High amount for elderly user: ₹{amount:.2f}")
        
        elif user_age >= self.SENIOR_AGE_THRESHOLD:
            # Senior (65-74) - Moderate limits
            if amount >= self.SENIOR_VERY_HIGH_AMOUNT:
                risk_score += 0.6
                flags.append(f"🚨 VERY HIGH AMOUNT for senior: ₹{amount:.2f}")
            elif amount >= self.SENIOR_HIGH_AMOUNT_THRESHOLD:
                risk_score += 0.3
                flags.append(f"⚠️ High amount for senior citizen: ₹{amount:.2f}")
        
        if risk_score == 0:
            flags.append(f"✅ Amount within safe range: ₹{amount:.2f}")
        
        return risk_score, flags
    
    def _check_new_merchant_for_seniors(self, merchant_name, merchant_history, user_age):
        """Check if senior is paying a new/unknown merchant"""
        risk_score = 0.0
        flags = []
        
        # Only apply to seniors
        if user_age < self.SENIOR_AGE_THRESHOLD:
            return 0.0, []
        
        # Check if merchant is in user's history
        if not merchant_history or len(merchant_history) == 0:
            if user_age >= self.ELDERLY_AGE_THRESHOLD:
                risk_score += 0.5
                flags.append(f"⚠️ NEW MERCHANT for elderly user: {merchant_name}")
                flags.append("   Elderly users targeted via fake merchants")
            else:
                risk_score += 0.3
                flags.append(f"⚠️ First time paying: {merchant_name}")
        else:
            # Check if this specific merchant was paid before
            known_merchants = {m['merchant_name'] for m in merchant_history}
            
            if merchant_name not in known_merchants:
                if user_age >= self.ELDERLY_AGE_THRESHOLD:
                    risk_score += 0.4
                    flags.append(f"⚠️ NEW MERCHANT for elderly: {merchant_name}")
                else:
                    risk_score += 0.2
                    flags.append(f"⚠️ New merchant: {merchant_name}")
            else:
                flags.append(f"✅ Known merchant: {merchant_name}")
        
        return risk_score, flags
    
    # ========================================================================
    # NEW FEATURE: VISHING Detection (on-call during transaction)
    # ========================================================================
    
    def check_vishing_attack(self, is_on_call, is_senior, amount):
        """
        NEW: Detect VISHING attack (voice phishing)
        Senior citizen on call during high-value transaction = RED FLAG
        
        Returns: (is_vishing: bool, risk_score: float, reason: str)
        """
        if is_on_call and is_senior:
            if amount > 10000:
                return True, 0.9, 'VISHING ATTACK: Senior citizen on call during high-value transaction'
            else:
                return True, 0.7, 'VISHING risk: Senior on call during transaction'
        return False, 0.0, ''
    
    def check_social_engineering(self, notes):
        """
        NEW: Standalone social engineering check
        Returns: (is_social_eng: bool, risk_score: float)
        """
        if not notes:
            return False, 0.0
        
        notes_lower = notes.lower()
        for keyword in self.SOCIAL_ENGINEERING_KEYWORDS:
            if keyword in notes_lower:
                return True, 0.8
        return False, 0.0
    
    def _detect_social_engineering(self, merchant_name, transaction_notes):
        """Detect social engineering fraud patterns"""
        risk_score = 0.0
        flags = []
        detected_keywords = []
        
        # Combine merchant name and notes for analysis
        text_to_check = f"{merchant_name} {transaction_notes}".lower()
        
        # Check for social engineering keywords
        for keyword in self.SOCIAL_ENGINEERING_KEYWORDS:
            if keyword in text_to_check:
                detected_keywords.append(keyword)
        
        if detected_keywords:
            risk_score += min(0.8, len(detected_keywords) * 0.3)
            flags.append(f"🚨 SOCIAL ENGINEERING DETECTED")
            flags.append(f"   Suspicious keywords: {', '.join(detected_keywords[:3])}")
            flags.append("   Common scams: KYC update, lottery, police threat, relative emergency")
        
        return risk_score, flags
    
    def _check_transaction_time_for_seniors(self, transaction_time, user_age):
        """Check if transaction time is unusual for seniors"""
        risk_score = 0.0
        flags = []
        
        # Only apply to seniors
        if user_age < self.SENIOR_AGE_THRESHOLD:
            return 0.0, []
        
        if isinstance(transaction_time, str):
            transaction_time = datetime.strptime(transaction_time, '%Y-%m-%d %H:%M:%S')
        
        hour = transaction_time.hour
        
        # Seniors less likely to transact very late
        if 22 <= hour or hour < 6:
            risk_score += 0.5
            flags.append(f"⚠️ LATE NIGHT transaction for senior: {transaction_time.strftime('%I:%M %p')}")
            flags.append("   Scammers often pressure seniors at night")
        
        return risk_score, flags
    
    def _check_recipient_type(self, recipient_type, user_age):
        """Check if recipient is unusual for senior"""
        risk_score = 0.0
        flags = []
        
        # Only apply to seniors
        if user_age < self.SENIOR_AGE_THRESHOLD:
            return 0.0, []
        
        # High-risk recipient types for seniors
        if recipient_type in ['unknown_individual', 'new_merchant', 'unverified']:
            risk_score += 0.4
            flags.append(f"⚠️ Payment to {recipient_type} (Common fraud pattern)")
        elif recipient_type == 'verified_merchant':
            flags.append(f"✅ Payment to verified merchant")
        
        return risk_score, flags
    
    def analyze_senior_protection(self, transaction_data, user_profile, user_history=None):
        """
        Main analysis function for senior citizen protection
        
        Args:
            transaction_data: dict with keys:
                - amount: float
                - merchant_name: str
                - merchant_id: str
                - transaction_notes: str
                - timestamp: str or datetime
                - recipient_type: str
                - is_on_call_during_transaction: int (0 or 1) - NEW
                - is_emergency: int (0 or 1) - NEW
            user_profile: dict with keys:
                - date_of_birth: str or datetime
                - age: int (optional, calculated if not provided)
            user_history: list of past transactions (optional)
        
        Returns:
            dict with:
                - risk_score: float (0-1)
                - decision: str ('ALLOW', 'WARN', 'BLOCK')
                - flags: list of issues detected
                - protection_level: str ('standard', 'medium', 'high')
                - details: dict with analysis details
        """
        
        risk_score = 0.0
        flags = []
        details = {}
        
        # Calculate or get user age
        if 'age' in user_profile:
            user_age = user_profile['age']
        else:
            user_age = self._calculate_age(user_profile['date_of_birth'])
        
        details['user_age'] = user_age
        
        # Extract transaction data
        amount = transaction_data.get('amount', 0)
        merchant_name = transaction_data.get('merchant_name', 'Unknown')
        transaction_notes = transaction_data.get('transaction_notes', '')
        transaction_time = transaction_data.get('timestamp', datetime.now())
        recipient_type = transaction_data.get('recipient_type', 'unknown')
        
        # NEW: Extract vishing and emergency flags
        is_on_call = transaction_data.get('is_on_call_during_transaction', False)
        if isinstance(is_on_call, int):
            is_on_call = bool(is_on_call)
        
        is_emergency = transaction_data.get('is_emergency', False)
        if isinstance(is_emergency, int):
            is_emergency = bool(is_emergency)
        
        # ====================================================================
        # CHECK 1: Age-Based Risk Assessment
        # ====================================================================
        
        age_risk, age_flags, protection_level = self._check_age_based_risk(user_age)
        risk_score += age_risk
        flags.extend(age_flags)
        details['protection_level'] = protection_level
        
        # If not a senior, return early with low risk
        if not self._is_senior_citizen(user_age):
            return {
                'risk_score': round(risk_score, 3),
                'decision': 'ALLOW',
                'flags': flags,
                'protection_level': protection_level,
                'details': details,
                'is_senior': False
            }
        
        # Continue with senior-specific checks
        details['is_senior'] = True
        
        # ====================================================================
        # NEW: CHECK 2A: VISHING ATTACK DETECTION (CRITICAL!)
        # ====================================================================
        
        is_vishing, vishing_risk, vishing_reason = self.check_vishing_attack(
            is_on_call, True, amount
        )
        
        if is_vishing:
            risk_score += vishing_risk
            flags.append(f"🚨 {vishing_reason}")
            details['vishing_detected'] = True
            
            # VISHING is critical - immediate block recommendation
            if vishing_risk >= 0.9:
                flags.append("   IMMEDIATE ACTION: Contact user via registered number")
        else:
            details['vishing_detected'] = False
        
        # ====================================================================
        # NEW: CHECK 2B: EMERGENCY FLAG
        # ====================================================================
        
        if is_emergency and amount > 10000:
            risk_score += 0.85
            flags.append(f"🚨 EMERGENCY FRAUD: Senior targeted with urgent/emergency scenario")
            flags.append("   Common scam: Fake relative emergency, police threats")
            details['emergency_fraud_detected'] = True
        
        # ====================================================================
        # CHECK 3: Amount Check for Seniors
        # ====================================================================
        
        amount_risk, amount_flags = self._check_amount_for_seniors(amount, user_age)
        risk_score += amount_risk
        flags.extend(amount_flags)
        
        # ====================================================================
        # CHECK 4: New Merchant Warning
        # ====================================================================
        
        merchant_history = []
        if user_history:
            merchant_history = [
                {'merchant_name': txn.get('merchant_name', '')}
                for txn in user_history
            ]
        
        merchant_risk, merchant_flags = self._check_new_merchant_for_seniors(
            merchant_name, merchant_history, user_age
        )
        risk_score += merchant_risk
        flags.extend(merchant_flags)
        
        # ====================================================================
        # CHECK 5: Social Engineering Detection
        # ====================================================================
        
        social_risk, social_flags = self._detect_social_engineering(
            merchant_name, transaction_notes
        )
        risk_score += social_risk
        flags.extend(social_flags)
        
        # ====================================================================
        # CHECK 6: Transaction Time Check
        # ====================================================================
        
        time_risk, time_flags = self._check_transaction_time_for_seniors(
            transaction_time, user_age
        )
        risk_score += time_risk
        flags.extend(time_flags)
        
        # ====================================================================
        # CHECK 7: Recipient Type Check
        # ====================================================================
        
        recipient_risk, recipient_flags = self._check_recipient_type(
            recipient_type, user_age
        )
        risk_score += recipient_risk
        flags.extend(recipient_flags)
        
        # ====================================================================
        # NEW: ML Model Prediction
        # ====================================================================
        
        if self.ml_model and self.encoders:
            try:
                recipient_encoded = self.encoders['recipient_type'].transform([recipient_type])[0]
                
                features = [[
                    user_age,
                    int(self._is_senior_citizen(user_age)),
                    amount,
                    int(is_on_call),
                    int(is_emergency),
                    recipient_encoded,
                    int(transaction_data.get('is_new_device', False))
                ]]
                ml_risk = self.ml_model.predict_proba(features)[0][1]
                
                # Combine rule-based and ML
                combined_risk = 0.6 * risk_score + 0.4 * ml_risk
                details['ml_risk_score'] = round(ml_risk, 3)
                details['rule_based_score'] = round(risk_score, 3)
                
                risk_score = combined_risk
                flags.append(f"🤖 ML Model: Risk {ml_risk:.3f}")
            except:
                pass
        
        # ====================================================================
        # FINAL DECISION (Stricter for seniors)
        # ====================================================================
        
        # Cap risk score at 1.0
        risk_score = min(risk_score, 1.0)
        
        # Stricter thresholds for seniors
        if self._is_elderly(user_age):
            # Elderly - Most protective
            if risk_score >= 0.5:
                decision = 'BLOCK'
            elif risk_score >= 0.3:
                decision = 'WARN'
            else:
                decision = 'ALLOW'
        elif self._is_senior_citizen(user_age):
            # Senior - Protective
            if risk_score >= 0.6:
                decision = 'BLOCK'
            elif risk_score >= 0.35:
                decision = 'WARN'
            else:
                decision = 'ALLOW'
        else:
            # Standard thresholds
            if risk_score >= 0.7:
                decision = 'BLOCK'
            elif risk_score >= 0.4:
                decision = 'WARN'
            else:
                decision = 'ALLOW'
        
        return {
            'risk_score': round(risk_score, 3),
            'decision': decision,
            'flags': flags,
            'protection_level': protection_level,
            'details': details,
            'is_senior': True
        }
    
    # ========================================================================
    # NEW: Simple analyze() method for master engine compatibility
    # ========================================================================
    
    def analyze(self, transaction):
        """
        NEW: Simplified analyze method for master engine
        Returns: (decision, risk_score, reason)
        """
        user_age = transaction.get('user_age', 30)
        is_senior = transaction.get('is_senior_citizen', False) or user_age >= 60
        amount = transaction.get('amount', 0)
        is_on_call = transaction.get('is_on_call_during_transaction', False)
        is_emergency = transaction.get('is_emergency', False)
        notes = transaction.get('transaction_notes', '')
        recipient_type = transaction.get('recipient_type', 'verified_merchant')
        
        # Rule 1: VISHING ATTACK (on call during transaction)
        if is_on_call and is_senior:
            return 'BLOCK', 0.9, 'VISHING ATTACK: Senior citizen on call during high-value transaction'
        
        # Rule 2: Emergency flag with senior
        if is_emergency and is_senior and amount > 10000:
            return 'BLOCK', 0.85, 'Emergency fraud targeting senior citizen'
        
        # Rule 3: Social engineering detection
        is_social_eng, social_risk = self.check_social_engineering(notes)
        
        if is_social_eng and is_senior:
            risk = 0.8
            reason = f'Social engineering detected targeting senior: "{notes}"'
        elif is_senior and amount > 15000 and recipient_type == 'unknown_individual':
            risk = 0.7
            reason = 'High-value transfer to unknown recipient by senior citizen'
        elif is_senior and amount > 20000:
            risk = 0.6
            reason = 'Very high amount transaction by senior citizen'
        else:
            risk = 0.1
            reason = 'No senior citizen risk detected'
        
        # ML prediction (if available)
        if self.ml_model and self.encoders:
            try:
                recipient_encoded = self.encoders['recipient_type'].transform([recipient_type])[0]
                
                features = [[
                    user_age,
                    int(is_senior),
                    amount,
                    int(is_on_call),
                    int(is_emergency),
                    recipient_encoded,
                    int(transaction.get('is_new_device', False))
                ]]
                ml_risk = self.ml_model.predict_proba(features)[0][1]
                risk = 0.6 * risk + 0.4 * ml_risk
            except:
                pass
        
        if risk > 0.7:
            return 'BLOCK', risk, reason
        elif risk > 0.5:
            return 'WARN', risk, reason
        else:
            return 'ALLOW', risk, reason
    
    def get_senior_protection_report(self, transaction_data, user_profile, user_history=None):
        """Generate detailed senior citizen protection report"""
        result = self.analyze_senior_protection(transaction_data, user_profile, user_history)
        
        report = "="*70 + "\n"
        report += "👴 STAGE 5: SENIOR CITIZEN PROTECTION REPORT\n"
        report += "="*70 + "\n\n"
        
        report += f"User Age: {result['details']['user_age']} years\n"
        report += f"Protection Level: {result['protection_level'].upper()}\n"
        report += f"Is Senior Citizen: {'YES' if result.get('is_senior', False) else 'NO'}\n"
        
        # NEW: Show vishing/emergency detection
        if result['details'].get('vishing_detected'):
            report += f"🚨 VISHING DETECTED: User on call during transaction\n"
        if result['details'].get('emergency_fraud_detected'):
            report += f"🚨 EMERGENCY FRAUD: Urgent scenario scam\n"
        
        report += f"\nTransaction Amount: ₹{transaction_data.get('amount', 0):.2f}\n"
        report += f"Merchant: {transaction_data.get('merchant_name', 'Unknown')}\n"
        report += f"Transaction Time: {transaction_data.get('timestamp', 'Unknown')}\n\n"
        
        # NEW: Show ML model contribution
        if 'ml_risk_score' in result['details']:
            report += f"ML Model Risk: {result['details']['ml_risk_score']:.3f}\n"
            report += f"Rule-Based Risk: {result['details']['rule_based_score']:.3f}\n\n"
        
        report += f"Risk Score: {result['risk_score']:.3f}\n"
        report += f"Decision: {result['decision']}\n\n"
        
        report += "Protection Flags:\n"
        for flag in result['flags']:
            report += f"  • {flag}\n"
        
        if result.get('is_senior', False):
            report += "\n🛡️ SENIOR CITIZEN SAFEGUARDS ACTIVE:\n"
            report += "  • Lower transaction thresholds\n"
            report += "  • Enhanced merchant verification\n"
            report += "  • Social engineering detection\n"
            report += "  • Time-based risk assessment\n"
            report += "  • VISHING attack detection\n"  # NEW
            report += "  • Emergency scenario fraud detection\n"  # NEW
        
        report += "\n" + "="*70 + "\n"
        
        return report


# ============================================================================
# DEMO / TEST
# ============================================================================

if __name__ == "__main__":
    print("="*70)
    print("🧪 TESTING ENHANCED SENIOR CITIZEN PROTECTION ENGINE")
    print("="*70)
    
    # Initialize engine
    engine = SeniorCitizenProtectionEngine()
    
    # Sample history
    user_history = [
        {'merchant_name': 'BigBazaar', 'amount': 2000},
        {'merchant_name': 'Apollo Pharmacy', 'amount': 500},
        {'merchant_name': 'DMart', 'amount': 1500}
    ]
    
    # Test Case 1: Young User (No special protection)
    print("\n\nTEST CASE 1: Young User (30 years)")
    print("-"*70)
    user1 = {'age': 30}
    txn1 = {
        'amount': 15000,
        'merchant_name': 'Flipkart',
        'transaction_notes': 'Phone purchase',
        'timestamp': '2024-12-25 14:00:00',
        'recipient_type': 'verified_merchant',
        'is_on_call_during_transaction': False,
        'is_emergency': False
    }
    result1 = engine.analyze_senior_protection(txn1, user1, user_history)
    print(engine.get_senior_protection_report(txn1, user1, user_history))
    
    # Test Case 2: Senior Citizen - Normal Transaction
    print("\n\nTEST CASE 2: Senior Citizen (68 years) - Normal")
    print("-"*70)
    user2 = {'age': 68}
    txn2 = {
        'amount': 3000,
        'merchant_name': 'Apollo Pharmacy',
        'transaction_notes': 'Medicine',
        'timestamp': '2024-12-25 10:00:00',
        'recipient_type': 'verified_merchant',
        'is_on_call_during_transaction': False,
        'is_emergency': False
    }
    result2 = engine.analyze_senior_protection(txn2, user2, user_history)
    print(engine.get_senior_protection_report(txn2, user2, user_history))
    
    # NEW TEST CASE 3: VISHING ATTACK
    print("\n\nTEST CASE 3: 🚨 VISHING ATTACK - Senior On Call")
    print("-"*70)
    user3 = {'age': 70}
    txn3 = {
        'amount': 25000,
        'merchant_name': 'Unknown Merchant',
        'transaction_notes': 'Urgent payment required',
        'timestamp': '2024-12-25 15:00:00',
        'recipient_type': 'unknown_individual',
        'is_on_call_during_transaction': True,  # ON CALL!
        'is_emergency': False
    }
    result3 = engine.analyze_senior_protection(txn3, user3, user_history)
    print(engine.get_senior_protection_report(txn3, user3, user_history))
    
    # Test Case 4: Elderly - High Amount + New Merchant
    print("\n\nTEST CASE 4: 🚨 ELDERLY (78 years) - HIGH AMOUNT + NEW MERCHANT")
    print("-"*70)
    user4 = {'age': 78}
    txn4 = {
        'amount': 30000,
        'merchant_name': 'Unknown Electronics Store',
        'transaction_notes': 'Urgent payment',
        'timestamp': '2024-12-25 23:00:00',
        'recipient_type': 'new_merchant',
        'is_on_call_during_transaction': False,
        'is_emergency': False
    }
    result4 = engine.analyze_senior_protection(txn4, user4, user_history)
    print(engine.get_senior_protection_report(txn4, user4, user_history))
    
    # Test Case 5: Social Engineering + Emergency
    print("\n\nTEST CASE 5: 🚨 SOCIAL ENGINEERING + EMERGENCY")
    print("-"*70)
    user5 = {'age': 72}
    txn5 = {
        'amount': 15000,
        'merchant_name': 'KBC Lottery Winner',
        'transaction_notes': 'Prize claim - urgent KYC update required',
        'timestamp': '2024-12-25 22:30:00',
        'recipient_type': 'unknown_individual',
        'is_on_call_during_transaction': False,
        'is_emergency': True  # EMERGENCY FLAG!
    }
    result5 = engine.analyze_senior_protection(txn5, user5)
    print(engine.get_senior_protection_report(txn5, user5))
    
    # NEW: Test analyze() method for master engine
    print("\n\nTEST CASE 6: Testing analyze() method for master engine")
    print("-"*70)
    user6 = {'age' : 72}
    test6 = {
        'is_senior_citizen': True,
        'amount': 25000,
        'is_on_call_during_transaction': True,
        'is_emergency': True,
        'transaction_notes' : 'Grandson hospital emergency',
        'recipient_type' : 'unknown individual',
        'is_new_device' : True
    }

    result6 = engine.analyze_senior_protection(test6, user6)
    print(engine.get_senior_protection_report(test6,user6))

    print("\n" + "="*70)
    print("✅ ENHANCED SENIOR CITIZEN PROTECTION ENGINE TESTS COMPLETE")
    print("="*70)