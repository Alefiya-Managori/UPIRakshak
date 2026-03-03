"""
STAGE 3: BEHAVIORAL ANALYSIS MODULE (ENHANCED)
Analyzes user transaction behavior patterns
Author: [Your Team Name]
"""

import numpy as np
import joblib
import pickle
import os
from datetime import datetime, timedelta
from sklearn.ensemble import IsolationForest

class BehavioralAnalysisEngine:
    """
    Stage 3: User Behavior Analysis
    
    Checks:
    1. Transaction amount patterns (normal vs anomaly)
    2. Transaction velocity (frequency)
    3. Time-of-day patterns
    4. Device consistency
    5. ML-based anomaly detection
    
    NEW ENHANCEMENTS:
    - Integration with trained ML model from train_models.py
    - analyze() method for master engine compatibility
    - Enhanced merchant analysis (typical vs new merchants)
    """
    
    def __init__(self):
        print("🧠 Initializing Behavioral Analysis Engine")
        
        # Load ML model if exists
        self.isolation_forest = self._load_isolation_forest()
        
        # NEW: Load trained model from training script
        self.trained_model = self._load_trained_model()
        
        # Thresholds
        self.HIGH_AMOUNT_MULTIPLIER = 5  # 5x average is suspicious
        self.EXTREME_AMOUNT_MULTIPLIER = 10  # 10x average is high risk
        self.VELOCITY_THRESHOLD_1H = 5  # Max transactions per hour
        self.VELOCITY_THRESHOLD_24H = 20  # Max transactions per day
        
        print("✅ Behavioral Analysis Engine Ready")
    
    def _load_isolation_forest(self):
        """Load pre-trained Isolation Forest model"""
        # Try new path first
        model_path = 'models/stage3/behavioral_anomaly_model.pkl'
        if os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    return pickle.load(f)
            except:
                pass
        
        # Try old path
        old_path = 'models/stage3/isolation_forest.pkl'
        if os.path.exists(old_path):
            return joblib.load(old_path)
        
        # Create default model if not exists
        print("⚠️  Isolation Forest model not found, creating default")
        return IsolationForest(contamination=0.02, random_state=42)
    
    def _load_trained_model(self):
        """NEW: Load trained ML model from training script"""
        model_path = 'models/stage3/behavioral_anomaly_model.pkl'
        if os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    return pickle.load(f)
            except:
                pass
        return None
    
    def _calculate_user_statistics(self, user_history):
        """Calculate user's historical transaction statistics"""
        if not user_history or len(user_history) == 0:
            return {
                'avg_amount': 2000,  # Default assumption
                'std_amount': 500,
                'max_amount': 5000,
                'min_amount': 100,
                'transaction_count': 0,
                'avg_time_between_txns': None
            }
        
        amounts = [txn['amount'] for txn in user_history]
        
        stats = {
            'avg_amount': np.mean(amounts),
            'std_amount': np.std(amounts),
            'max_amount': np.max(amounts),
            'min_amount': np.min(amounts),
            'transaction_count': len(user_history)
        }
        
        # Calculate average time between transactions
        if len(user_history) > 1:
            times = []
            for i in range(1, len(user_history)):
                t1 = user_history[i-1]['timestamp']
                t2 = user_history[i]['timestamp']
                
                if isinstance(t1, str):
                    t1 = datetime.strptime(t1, '%Y-%m-%d %H:%M:%S')
                if isinstance(t2, str):
                    t2 = datetime.strptime(t2, '%Y-%m-%d %H:%M:%S')
                
                time_diff = (t2 - t1).total_seconds() / 3600  # hours
                times.append(time_diff)
            
            stats['avg_time_between_txns'] = np.mean(times)
        else:
            stats['avg_time_between_txns'] = None
        
        return stats
    
    def _check_amount_anomaly(self, current_amount, user_stats):
        """Check if transaction amount is anomalous"""
        risk_score = 0.0
        flags = []
        
        avg_amount = user_stats['avg_amount']
        std_amount = user_stats['std_amount']
        max_amount = user_stats['max_amount']
        
        # Check 1: Z-score (standard deviations from mean)
        if std_amount > 0:
            z_score = (current_amount - avg_amount) / std_amount
            
            if z_score > 5:
                risk_score += 0.7
                flags.append(f"🚨 Amount is {z_score:.1f} standard deviations above normal")
            elif z_score > 3:
                risk_score += 0.4
                flags.append(f"⚠️ Amount is {z_score:.1f} standard deviations above average")
        
        # Check 2: Multiplier check
        ratio = current_amount / avg_amount if avg_amount > 0 else 1
        
        if ratio > self.EXTREME_AMOUNT_MULTIPLIER:
            risk_score += 0.8
            flags.append(f"🚨 Amount is {ratio:.1f}x your average (₹{avg_amount:.2f})")
        elif ratio > self.HIGH_AMOUNT_MULTIPLIER:
            risk_score += 0.5
            flags.append(f"⚠️ Amount is {ratio:.1f}x your average (₹{avg_amount:.2f})")
        
        # Check 3: Exceeds previous maximum significantly
        if current_amount > max_amount * 2:
            risk_score += 0.4
            percent_increase = ((current_amount / max_amount) - 1) * 100
            flags.append(f"⚠️ Amount exceeds previous maximum by {percent_increase:.0f}%")
        
        # Positive indicators
        if ratio < 2 and (std_amount == 0 or z_score < 2):
            flags.append("✅ Amount within normal range")
        
        return risk_score, flags
    
    def _check_transaction_velocity(self, current_time, user_history):
        """Check transaction frequency (velocity abuse)"""
        risk_score = 0.0
        flags = []
        
        if not user_history or len(user_history) == 0:
            return 0.0, ["✅ First transaction - no velocity check possible"]
        
        # Parse current time
        if isinstance(current_time, str):
            current_time = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S')
        
        # Count transactions in last 1 hour
        count_1h = 0
        count_24h = 0
        
        for txn in user_history:
            txn_time = txn['timestamp']
            if isinstance(txn_time, str):
                txn_time = datetime.strptime(txn_time, '%Y-%m-%d %H:%M:%S')
            
            time_diff = (current_time - txn_time).total_seconds() / 3600
            
            if time_diff <= 1:
                count_1h += 1
            if time_diff <= 24:
                count_24h += 1
        
        # Check velocity thresholds
        if count_1h >= self.VELOCITY_THRESHOLD_1H:
            risk_score += 0.8
            flags.append(f"🚨 HIGH VELOCITY: {count_1h + 1} transactions in last hour")
        elif count_1h >= 3:
            risk_score += 0.4
            flags.append(f"⚠️ Elevated velocity: {count_1h + 1} transactions in last hour")
        
        if count_24h >= self.VELOCITY_THRESHOLD_24H:
            risk_score += 0.5
            flags.append(f"⚠️ HIGH DAILY VOLUME: {count_24h + 1} transactions today")
        elif count_24h >= 10:
            risk_score += 0.2
            flags.append(f"⚠️ Elevated daily volume: {count_24h + 1} transactions today")
        
        # Check for rapid succession
        if len(user_history) > 0:
            last_txn_time = user_history[-1]['timestamp']
            if isinstance(last_txn_time, str):
                last_txn_time = datetime.strptime(last_txn_time, '%Y-%m-%d %H:%M:%S')
            
            minutes_since_last = (current_time - last_txn_time).total_seconds() / 60
            
            if minutes_since_last < 2:
                risk_score += 0.6
                flags.append(f"🚨 Transaction within {minutes_since_last:.0f} minutes of previous")
            elif minutes_since_last < 5:
                risk_score += 0.3
                flags.append(f"⚠️ Transaction within {minutes_since_last:.0f} minutes of previous")
        
        if risk_score == 0:
            flags.append("✅ Transaction velocity is normal")
        
        return risk_score, flags
    
    def _check_time_of_day(self, transaction_time):
        """Check if transaction time is unusual"""
        risk_score = 0.0
        flags = []
        
        if isinstance(transaction_time, str):
            transaction_time = datetime.strptime(transaction_time, '%Y-%m-%d %H:%M:%S')
        
        hour = transaction_time.hour
        
        # Late night / early morning transactions are suspicious
        if 0 <= hour < 5:
            risk_score += 0.4
            flags.append(f"⚠️ Unusual time: {transaction_time.strftime('%I:%M %p')} (late night)")
        elif 5 <= hour < 7:
            risk_score += 0.2
            flags.append(f"⚠️ Early morning transaction: {transaction_time.strftime('%I:%M %p')}")
        elif hour >= 23:
            risk_score += 0.3
            flags.append(f"⚠️ Late evening transaction: {transaction_time.strftime('%I:%M %p')}")
        else:
            flags.append(f"✅ Normal transaction time: {transaction_time.strftime('%I:%M %p')}")
        
        return risk_score, flags
    
    def _check_device_consistency(self, current_device, user_history):
        """Check if device is consistent with user's history"""
        risk_score = 0.0
        flags = []
        
        if not user_history or len(user_history) == 0:
            return 0.2, ["⚠️ New user - device consistency cannot be verified"]
        
        # Extract devices from history
        historical_devices = set()
        for txn in user_history:
            if 'device_id' in txn:
                historical_devices.add(txn['device_id'])
        
        if current_device not in historical_devices:
            risk_score += 0.3
            flags.append(f"⚠️ New/unknown device detected")
        else:
            flags.append(f"✅ Device recognized from history")
        
        return risk_score, flags
    
    # ========================================================================
    # NEW FEATURE: Merchant Analysis
    # ========================================================================
    
    def _check_merchant_familiarity(self, current_merchant, user_history, current_amount):
        """
        NEW: Check if merchant is familiar to user
        High amounts to new merchants are suspicious
        """
        risk_score = 0.0
        flags = []
        
        if not user_history or len(user_history) == 0:
            return 0.1, ["⚠️ New user - merchant check skipped"]
        
        # Extract merchants from history
        historical_merchants = set()
        for txn in user_history:
            if 'merchant_name' in txn:
                historical_merchants.add(txn['merchant_name'])
        
        is_typical_merchant = current_merchant in historical_merchants
        
        # NEW MERCHANTS with HIGH AMOUNTS are risky
        if not is_typical_merchant and current_amount > 5000:
            risk_score += 0.5
            flags.append(f"⚠️ Large payment to new merchant: {current_merchant}")
        elif not is_typical_merchant:
            risk_score += 0.2
            flags.append(f"⚠️ New merchant: {current_merchant}")
        else:
            flags.append(f"✅ Familiar merchant: {current_merchant}")
        
        return risk_score, flags, is_typical_merchant
    
    def _ml_anomaly_detection(self, current_amount, hour_of_day, user_stats):
        """Use Isolation Forest for anomaly detection"""
        try:
            # Prepare features
            amount_normalized = (current_amount - user_stats['avg_amount']) / (user_stats['std_amount'] + 1)
            hour_sin = np.sin(2 * np.pi * hour_of_day / 24)
            hour_cos = np.cos(2 * np.pi * hour_of_day / 24)
            
            features = np.array([[amount_normalized, hour_sin, hour_cos]])
            
            # Predict
            prediction = self.isolation_forest.predict(features)[0]
            
            if prediction == -1:
                # Anomaly detected
                return 0.6, ["🚨 ML model flagged transaction as anomaly"]
            else:
                return 0.0, ["✅ ML model confirms normal behavior"]
        
        except Exception as e:
            # If ML fails, return neutral
            return 0.0, ["⚠️ ML analysis unavailable"]
    
    def analyze_behavior(self, transaction_data, user_history=None):
        """
        Main analysis function for behavioral patterns
        
        Args:
            transaction_data: dict with keys:
                - amount: float
                - timestamp: str or datetime
                - device_id: str
                - hour_of_day: int (optional)
                - merchant_name: str (optional) - NEW
                - is_typical_merchant: bool (optional) - NEW
                - amount_to_avg_ratio: float (optional) - NEW
        user_history: list of past transactions (optional)
        
        Returns:
            dict with:
                - risk_score: float (0-1)
                - decision: str ('ALLOW', 'WARN', 'BLOCK')
                - flags: list of issues detected
                - details: dict with analysis details
        """
        
        risk_score = 0.0
        flags = []
        details = {}
        
        # Extract data
        current_amount = transaction_data.get('amount', 0)
        current_time = transaction_data.get('timestamp', datetime.now())
        current_device = transaction_data.get('device_id', 'unknown')
        current_merchant = transaction_data.get('merchant_name', 'unknown')
        
        if isinstance(current_time, str):
            current_time = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S')
        
        hour_of_day = transaction_data.get('hour_of_day', current_time.hour)
        
        # Calculate user statistics
        user_stats = self._calculate_user_statistics(user_history)
        details['user_stats'] = user_stats
        
        # ====================================================================
        # CHECK 1: Amount Anomaly Detection
        # ====================================================================
        
        amount_risk, amount_flags = self._check_amount_anomaly(current_amount, user_stats)
        risk_score += amount_risk
        flags.extend(amount_flags)
        details['amount_analysis'] = {
            'risk': amount_risk,
            'flags': amount_flags
        }
        
        # ====================================================================
        # CHECK 2: Transaction Velocity
        # ====================================================================
        
        velocity_risk, velocity_flags = self._check_transaction_velocity(current_time, user_history)
        risk_score += velocity_risk
        flags.extend(velocity_flags)
        details['velocity_analysis'] = {
            'risk': velocity_risk,
            'flags': velocity_flags
        }
        
        # ====================================================================
        # CHECK 3: Time of Day
        # ====================================================================
        
        time_risk, time_flags = self._check_time_of_day(current_time)
        risk_score += time_risk
        flags.extend(time_flags)
        details['time_analysis'] = {
            'risk': time_risk,
            'flags': time_flags
        }
        
        # ====================================================================
        # CHECK 4: Device Consistency
        # ====================================================================
        
        device_risk, device_flags = self._check_device_consistency(current_device, user_history)
        risk_score += device_risk
        flags.extend(device_flags)
        details['device_analysis'] = {
            'risk': device_risk,
            'flags': device_flags
        }
        
        # ====================================================================
        # NEW: CHECK 5: Merchant Familiarity
        # ====================================================================
        
        merchant_risk, merchant_flags, is_typical = self._check_merchant_familiarity(
            current_merchant, user_history, current_amount
        )
        risk_score += merchant_risk
        flags.extend(merchant_flags)
        details['merchant_analysis'] = {
            'risk': merchant_risk,
            'flags': merchant_flags,
            'is_typical_merchant': is_typical
        }
        
        # ====================================================================
        # CHECK 6: ML-Based Anomaly Detection
        # ====================================================================
        
        ml_risk, ml_flags = self._ml_anomaly_detection(current_amount, hour_of_day, user_stats)
        risk_score += ml_risk
        flags.extend(ml_flags)
        details['ml_analysis'] = {
            'risk': ml_risk,
            'flags': ml_flags
        }
        
        # ====================================================================
        # FINAL DECISION
        # ====================================================================
        
        # Cap risk score at 1.0
        risk_score = min(risk_score, 1.0)
        
        # Determine decision
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
            'details': details
        }
    
    # ========================================================================
    # NEW: Simple analyze() method for master engine compatibility
    # ========================================================================
    
    def analyze(self, transaction):
        """
        NEW: Simplified analyze method for master engine
        Returns: (decision, risk_score, reason)
        
        This matches the interface expected by the master engine
        """
        # Feature extraction
        amount = transaction.get('amount', 0)
        amount_to_avg_ratio = transaction.get('amount_to_avg_ratio', 1.0)
        is_typical_merchant = transaction.get('is_typical_merchant', False)
        hour = transaction.get('hour_of_day', 12)
        
        risk = 0.0
        reasons = []
        
        # Rule 1: Unusual amount
        if amount_to_avg_ratio > 10:
            risk = max(risk, 0.8)
            reasons.append('Amount 10x higher than user average')
        elif amount_to_avg_ratio > 5:
            risk = max(risk, 0.6)
            reasons.append('Amount unusually high')
        
        # Rule 2: New/untrusted merchant
        if not is_typical_merchant and amount > 5000:
            risk = max(risk, 0.5)
            reasons.append('Large payment to new merchant')
        
        # Rule 3: Unusual time
        if hour < 6 or hour > 23:
            risk = max(risk, 0.4)
            reasons.append('Transaction at unusual hour')
        
        # ML Anomaly Detection (if model available)
        if self.trained_model:
            try:
                features = [[
                    amount,
                    hour,
                    transaction.get('time_since_last_txn_hours', 0),
                    transaction.get('user_transaction_count', 0),
                    int(is_typical_merchant),
                    amount_to_avg_ratio
                ]]
                anomaly_score = self.trained_model.score_samples(features)[0]
                prediction = self.trained_model.predict(features)[0]
                
                if prediction == -1:  # Anomaly
                    risk = max(risk, 0.7)
                    reasons.append('ML anomaly detected')
            except:
                pass
        
        reason = '; '.join(reasons) if reasons else 'Normal behavior'
        
        if risk > 0.7:
            return 'BLOCK', risk, reason
        elif risk > 0.4:
            return 'WARN', risk, reason
        else:
            return 'ALLOW', risk, reason
    
    def get_behavior_report(self, transaction_data, user_history=None):
        """
        Generate detailed behavioral analysis report
        
        Args:
            transaction_data: dict with transaction details
            user_history: list of past transactions
        
        Returns:
            Formatted string report
        """
        result = self.analyze_behavior(transaction_data, user_history)
        
        report = "="*70 + "\n"
        report += "🧠 STAGE 3: BEHAVIORAL ANALYSIS REPORT\n"
        report += "="*70 + "\n\n"
        
        report += f"Transaction Amount: ₹{transaction_data.get('amount', 0):.2f}\n"
        report += f"Transaction Time: {transaction_data.get('timestamp', 'Unknown')}\n"
        report += f"Device ID: {transaction_data.get('device_id', 'Unknown')}\n"
        report += f"Merchant: {transaction_data.get('merchant_name', 'Unknown')}\n\n"
        
        # User statistics
        user_stats = result['details']['user_stats']
        report += "User Historical Statistics:\n"
        report += f"  • Average Amount: ₹{user_stats['avg_amount']:.2f}\n"
        report += f"  • Max Amount: ₹{user_stats['max_amount']:.2f}\n"
        report += f"  • Transaction Count: {user_stats['transaction_count']}\n\n"
        
        report += f"Risk Score: {result['risk_score']:.3f}\n"
        report += f"Decision: {result['decision']}\n\n"
        
        report += "Flags Detected:\n"
        for flag in result['flags']:
            report += f"  • {flag}\n"
        
        report += "\n" + "="*70 + "\n"
        
        return report


# ============================================================================
# DEMO / TEST
# ============================================================================

if __name__ == "__main__":
    print("="*70)
    print("🧪 TESTING ENHANCED BEHAVIORAL ANALYSIS ENGINE")
    print("="*70)
    
    # Initialize engine
    engine = BehavioralAnalysisEngine()
    
    # Sample user history
    user_history = [
        {'amount': 500, 'timestamp': '2024-12-01 10:30:00', 'device_id': 'device_001', 'merchant_name': 'Swiggy'},
        {'amount': 1200, 'timestamp': '2024-12-05 14:20:00', 'device_id': 'device_001', 'merchant_name': 'Amazon'},
        {'amount': 800, 'timestamp': '2024-12-10 16:45:00', 'device_id': 'device_001', 'merchant_name': 'Swiggy'},
        {'amount': 1500, 'timestamp': '2024-12-15 11:00:00', 'device_id': 'device_001', 'merchant_name': 'Flipkart'},
        {'amount': 950, 'timestamp': '2024-12-20 13:30:00', 'device_id': 'device_001', 'merchant_name': 'Amazon'}
    ]
    
    # Test Case 1: Normal Transaction
    print("\n\nTEST CASE 1: Normal Transaction")
    print("-"*70)
    test1 = {
        'amount': 1100,
        'timestamp': '2024-12-25 12:00:00',
        'device_id': 'device_001',
        'merchant_name': 'Swiggy'
    }
    result1 = engine.analyze_behavior(test1, user_history)
    print(engine.get_behavior_report(test1, user_history))
    
    # Test Case 2: High Amount (5x average)
    print("\n\nTEST CASE 2: 🚨 HIGH AMOUNT ANOMALY")
    print("-"*70)
    test2 = {
        'amount': 50000,
        'timestamp': '2024-12-25 14:00:00',
        'device_id': 'device_001',
        'merchant_name': 'Amazon'
    }
    result2 = engine.analyze_behavior(test2, user_history)
    print(engine.get_behavior_report(test2, user_history))
    
    # NEW TEST CASE: Large amount to new merchant
    print("\n\nTEST CASE 2B: 🚨 LARGE PAYMENT TO NEW MERCHANT")
    print("-"*70)
    test2b = {
        'amount': 15000,
        'timestamp': '2024-12-25 15:00:00',
        'device_id': 'device_001',
        'merchant_name': 'Suspicious Store'  # NEW merchant!
    }
    result2b = engine.analyze_behavior(test2b, user_history)
    print(engine.get_behavior_report(test2b, user_history))
    
    # Test Case 3: Velocity Abuse (rapid transactions)
    print("\n\nTEST CASE 3: ⚠️ VELOCITY ABUSE")
    print("-"*70)
    
    # Add recent rapid transactions to history
    rapid_history = user_history + [
        {'amount': 500, 'timestamp': '2024-12-25 13:50:00', 'device_id': 'device_001', 'merchant_name': 'Swiggy'},
        {'amount': 600, 'timestamp': '2024-12-25 13:52:00', 'device_id': 'device_001', 'merchant_name': 'Swiggy'},
        {'amount': 700, 'timestamp': '2024-12-25 13:54:00', 'device_id': 'device_001', 'merchant_name': 'Amazon'},
        {'amount': 800, 'timestamp': '2024-12-25 13:56:00', 'device_id': 'device_001', 'merchant_name': 'Flipkart'},
        {'amount': 900, 'timestamp': '2024-12-25 13:58:00', 'device_id': 'device_001', 'merchant_name': 'Swiggy'}
    ]
    
    test3 = {
        'amount': 1000,
        'timestamp': '2024-12-25 13:59:00',
        'device_id': 'device_001',
        'merchant_name': 'Amazon'
    }
    result3 = engine.analyze_behavior(test3, rapid_history)
    print(engine.get_behavior_report(test3, rapid_history))
    
    # Test Case 4: Late Night Transaction
    print("\n\nTEST CASE 4: ⚠️ LATE NIGHT TRANSACTION")
    print("-"*70)
    test4 = {
        'amount': 1200,
        'timestamp': '2024-12-25 02:30:00',
        'device_id': 'device_001',
        'merchant_name': 'Swiggy'
    }
    result4 = engine.analyze_behavior(test4, user_history)
    print(engine.get_behavior_report(test4, user_history))
    
    # NEW: Test simple analyze() method
    print("\n\nTEST CASE 5: Testing analyze() method for master engine")
    print("-"*70)
    test5 = {
        'amount': 20000,
        'amount_to_avg_ratio': 15.0,
        'is_typical_merchant': False,
        'hour_of_day': 2
    }
    decision, risk, reason = engine.analyze(test5)
    print(f"Decision: {decision}")
    print(f"Risk Score: {risk:.3f}")
    print(f"Reason: {reason}")
    
    print("\n" + "="*70)
    print("✅ ENHANCED BEHAVIORAL ANALYSIS ENGINE TESTS COMPLETE")
    print("="*70)