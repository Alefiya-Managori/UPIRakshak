"""
STAGE 4: TYPING SPEED ANALYSIS MODULE (ENHANCED)
Detects automated bots and suspicious data entry patterns
Author: [Your Team Name]
ENHANCED VERSION with ML integration and master engine compatibility
"""

import numpy as np
import pickle
import os
from datetime import datetime

class TypingSpeedAnalysisEngine:
    """
    Stage 4: Typing Speed & Input Pattern Analysis
    
    Checks:
    1. PIN entry speed (too fast = bot, too slow = suspicious)
    2. Input consistency
    3. Human-like typing patterns
    4. Copy-paste detection
    
    NEW ENHANCEMENTS:
    - Integration with trained ML model
    - analyze() method for master engine compatibility
    - Enhanced erratic typing detection
    - Typing pattern classification (bot/erratic/normal)
    """
    
    def __init__(self):
        print("⌨️  Initializing Typing Speed Analysis Engine")
        
        # Normal human typing speed ranges (milliseconds per character)
        self.MIN_HUMAN_SPEED_MS = 100  # 100ms per character (very fast human)
        self.MAX_HUMAN_SPEED_MS = 1500  # 1.5s per character (slow typer)
        
        # PIN entry specific (4-6 digits)
        self.MIN_PIN_TIME_MS = 800  # Minimum time to enter PIN (800ms = 0.8s)
        self.MAX_PIN_TIME_MS = 15000  # Maximum reasonable time (15s)
        
        # Perfect consistency threshold
        self.PERFECT_CONSISTENCY_THRESHOLD = 0.05  # Standard deviation too low = bot
        
        # NEW: Load trained ML model
        self.ml_model = self._load_trained_model()
        self.encoders = self._load_encoders()
        
        print("✅ Typing Speed Analysis Engine Ready")
    
    def _load_trained_model(self):
        """NEW: Load trained ML model from training script"""
        model_path = 'models/stage4/typing_speed_model.pkl'
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
    
    def _calculate_typing_speed(self, input_length, time_taken_ms):
        """Calculate characters per second"""
        if time_taken_ms <= 0:
            return 0
        
        time_seconds = time_taken_ms / 1000
        chars_per_second = input_length / time_seconds
        
        return chars_per_second
    
    def _check_bot_speed(self, time_taken_ms, input_length):
        """Detect bot-like instantaneous input"""
        risk_score = 0.0
        flags = []
        
        avg_time_per_char = time_taken_ms / input_length if input_length > 0 else 0
        
        # Too fast = Bot
        if avg_time_per_char < self.MIN_HUMAN_SPEED_MS:
            risk_score += 0.9
            flags.append(f"🚨 BOT DETECTED: Input too fast ({avg_time_per_char:.0f}ms/char)")
            flags.append(f"   Human typing: >{self.MIN_HUMAN_SPEED_MS}ms/char")
        
        # Instantaneous (< 50ms total)
        if time_taken_ms < 50:
            risk_score += 1.0
            flags.append("🚨 INSTANT INPUT: Likely automated script")
        
        return risk_score, flags
    
    def _check_suspicious_slow(self, time_taken_ms, input_length):
        """Detect suspiciously slow input (hesitation, manual reading)"""
        risk_score = 0.0
        flags = []
        
        avg_time_per_char = time_taken_ms / input_length if input_length > 0 else 0
        
        # Too slow = Reading from paper/screen
        if avg_time_per_char > self.MAX_HUMAN_SPEED_MS:
            risk_score += 0.5
            flags.append(f"⚠️ SLOW INPUT: {avg_time_per_char:.0f}ms/char (copying from source?)")
        
        # Extremely slow for PIN
        if time_taken_ms > self.MAX_PIN_TIME_MS:
            risk_score += 0.4
            flags.append(f"⚠️ EXCESSIVE TIME: {time_taken_ms/1000:.1f}s to enter PIN")
            flags.append("   (May indicate uncertainty or stolen credentials)")
        
        return risk_score, flags
    
    def _check_perfect_consistency(self, keystroke_intervals):
        """Detect perfectly consistent timing (bot signature)"""
        risk_score = 0.0
        flags = []
        
        if not keystroke_intervals or len(keystroke_intervals) < 2:
            return 0.0, []
        
        # Calculate standard deviation
        std_dev = np.std(keystroke_intervals)
        mean_interval = np.mean(keystroke_intervals)
        
        # Coefficient of variation (CV)
        if mean_interval > 0:
            cv = std_dev / mean_interval
        else:
            cv = 0
        
        # Humans have variation, bots don't
        if cv < self.PERFECT_CONSISTENCY_THRESHOLD:
            risk_score += 0.8
            flags.append(f"🚨 PERFECT CONSISTENCY: CV={cv:.3f} (Bot signature)")
            flags.append("   Humans show natural variation in typing speed")
        elif cv < 0.1:
            risk_score += 0.4
            flags.append(f"⚠️ LOW VARIATION: CV={cv:.3f} (Suspiciously consistent)")
        else:
            flags.append(f"✅ Natural typing variation: CV={cv:.3f}")
        
        return risk_score, flags
    
    def _detect_copy_paste(self, input_method):
        """Detect if input was copy-pasted"""
        risk_score = 0.0
        flags = []
        
        if input_method == 'paste':
            risk_score += 0.7
            flags.append("🚨 COPY-PASTE DETECTED: PIN should be memorized")
        elif input_method == 'autofill':
            risk_score += 0.5
            flags.append("⚠️ AUTO-FILL DETECTED: Could indicate compromised device")
        elif input_method == 'keyboard':
            flags.append("✅ Manual keyboard input")
        
        return risk_score, flags
    
    # ========================================================================
    # NEW FEATURE: Detect typing patterns (bot/erratic/normal)
    # ========================================================================
    
    def _detect_typing_pattern(self, pin_entry_time, avg_keystroke):
        """
        NEW: Classify typing pattern as bot, erratic, or normal
        Returns: str ('bot', 'erratic', 'normal')
        """
        # Bot pattern: Too fast
        if pin_entry_time < 100 or avg_keystroke < 50:
            return 'bot'
        
        # Erratic pattern: Too slow (senior/social engineering)
        if pin_entry_time > 10000:
            return 'erratic'
        
        # Normal pattern
        return 'normal'
    
    def analyze_typing_speed(self, transaction_data):
        """
        Main analysis function for typing speed patterns
        
        Args:
            transaction_data: dict with keys:
                - pin_entry_time_ms: int (milliseconds to enter PIN)
                - pin_length: int (number of digits in PIN, usually 4 or 6)
                - keystroke_intervals: list of ints (ms between each keystroke)
                - input_method: str ('keyboard', 'paste', 'autofill')
                - pin_attempts: int (number of attempts)
                - typing_pattern: str (optional) - NEW: 'bot', 'erratic', 'normal'
                - avg_keystroke_interval: int (optional) - NEW
        
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
        pin_entry_time = transaction_data.get('pin_entry_time_ms', 0)
        pin_length = transaction_data.get('pin_length', 4)
        keystroke_intervals = transaction_data.get('keystroke_intervals', [])
        input_method = transaction_data.get('input_method', 'keyboard')
        pin_attempts = transaction_data.get('pin_attempts', 1)
        
        # NEW: Get or calculate average keystroke interval
        if keystroke_intervals:
            avg_keystroke = int(np.mean(keystroke_intervals))
        else:
            avg_keystroke = transaction_data.get('avg_keystroke_interval', 500)
        
        # NEW: Get or detect typing pattern
        typing_pattern = transaction_data.get('typing_pattern')
        if not typing_pattern:
            typing_pattern = self._detect_typing_pattern(pin_entry_time, avg_keystroke)
        
        details['typing_pattern'] = typing_pattern
        details['avg_keystroke_interval'] = avg_keystroke
        
        # Calculate typing speed
        typing_speed = self._calculate_typing_speed(pin_length, pin_entry_time)
        details['typing_speed_cps'] = round(typing_speed, 2)
        details['time_per_char_ms'] = round(pin_entry_time / pin_length, 2) if pin_length > 0 else 0
        
        # ====================================================================
        # CHECK 1: Bot-like Speed (Too Fast)
        # ====================================================================
        
        bot_risk, bot_flags = self._check_bot_speed(pin_entry_time, pin_length)
        risk_score += bot_risk
        flags.extend(bot_flags)
        
        # ====================================================================
        # CHECK 2: Suspicious Slow Speed (Erratic)
        # ====================================================================
        
        slow_risk, slow_flags = self._check_suspicious_slow(pin_entry_time, pin_length)
        risk_score += slow_risk
        flags.extend(slow_flags)
        
        # ====================================================================
        # CHECK 3: Perfect Consistency (Bot Signature)
        # ====================================================================
        
        if keystroke_intervals:
            consistency_risk, consistency_flags = self._check_perfect_consistency(keystroke_intervals)
            risk_score += consistency_risk
            flags.extend(consistency_flags)
            details['keystroke_consistency'] = {
                'std_dev': float(np.std(keystroke_intervals)),
                'mean': float(np.mean(keystroke_intervals))
            }
        
        # ====================================================================
        # CHECK 4: Copy-Paste Detection
        # ====================================================================
        
        paste_risk, paste_flags = self._detect_copy_paste(input_method)
        risk_score += paste_risk
        flags.extend(paste_flags)
        details['input_method'] = input_method
        
        # ====================================================================
        # CHECK 5: Multiple Failed Attempts
        # ====================================================================
        
        if pin_attempts > 1:
            if pin_attempts >= 3:
                risk_score += 0.6
                flags.append(f"🚨 {pin_attempts} PIN attempts (Unauthorized access?)")
            elif pin_attempts == 2:
                risk_score += 0.3
                flags.append(f"⚠️ {pin_attempts} PIN attempts")
        else:
            flags.append("✅ First attempt successful")
        
        # ====================================================================
        # NEW: ML Model Prediction
        # ====================================================================
        
        if self.ml_model and self.encoders:
            try:
                input_encoded = self.encoders['input_method'].transform([input_method])[0]
                pattern_encoded = self.encoders['typing_pattern'].transform([typing_pattern])[0]
                
                features = [[
                    pin_entry_time,
                    avg_keystroke,
                    input_encoded,
                    pin_attempts,
                    pattern_encoded
                ]]
                ml_risk = self.ml_model.predict_proba(features)[0][1]
                
                # Combine rule-based and ML scores
                combined_risk = 0.7 * risk_score + 0.3 * ml_risk
                details['ml_risk_score'] = round(ml_risk, 3)
                details['rule_based_score'] = round(risk_score, 3)
                
                risk_score = combined_risk
                flags.append(f"🤖 ML Model: Risk {ml_risk:.3f}")
            except:
                pass
        
        # ====================================================================
        # Positive Indicators
        # ====================================================================
        
        if (self.MIN_HUMAN_SPEED_MS * pin_length <= pin_entry_time <= self.MAX_HUMAN_SPEED_MS * pin_length 
            and input_method == 'keyboard' and pin_attempts == 1):
            flags.append("✅ Normal human typing pattern detected")
        
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
        pin_entry_time = transaction.get('pin_entry_time_ms', 2000)
        avg_keystroke = transaction.get('avg_keystroke_interval', 500)
        input_method = transaction.get('input_method', 'keyboard')
        typing_pattern = transaction.get('typing_pattern', 'normal')
        
        risk = 0.0
        
        # Rule 1: BOT DETECTION (too fast)
        if pin_entry_time < 100 or avg_keystroke < 50:
            return 'BLOCK', 0.95, 'Bot attack detected (superhuman typing speed)'
        
        if input_method in ['paste', 'autofill'] and pin_entry_time < 300:
            return 'BLOCK', 0.9, 'Automated PIN entry detected'
        
        # Rule 2: ERRATIC TYPING (suspicious)
        if typing_pattern == 'erratic' or pin_entry_time > 10000:
            risk = 0.6
            reason = 'Erratic typing pattern (possible social engineering)'
        elif typing_pattern == 'bot':
            risk = 0.9
            reason = 'Bot-like typing detected'
        else:
            risk = 0.1
            reason = 'Normal typing pattern'
        
        # ML prediction
        if self.ml_model and self.encoders:
            try:
                input_encoded = self.encoders['input_method'].transform([input_method])[0]
                pattern_encoded = self.encoders['typing_pattern'].transform([typing_pattern])[0]
                
                features = [[
                    pin_entry_time,
                    avg_keystroke,
                    input_encoded,
                    transaction.get('pin_attempts', 1),
                    pattern_encoded
                ]]
                ml_risk = self.ml_model.predict_proba(features)[0][1]
                risk = 0.7 * risk + 0.3 * ml_risk
            except:
                pass
        
        if risk > 0.8:
            return 'BLOCK', risk, reason
        elif risk > 0.5:
            return 'WARN', risk, reason
        else:
            return 'ALLOW', risk, reason
    
    def get_typing_report(self, transaction_data):
        """Generate detailed typing speed analysis report"""
        result = self.analyze_typing_speed(transaction_data)
        
        report = "="*70 + "\n"
        report += "⌨️  STAGE 4: TYPING SPEED ANALYSIS REPORT\n"
        report += "="*70 + "\n\n"
        
        report += f"PIN Entry Time: {transaction_data.get('pin_entry_time_ms', 0)}ms\n"
        report += f"PIN Length: {transaction_data.get('pin_length', 4)} digits\n"
        report += f"Input Method: {transaction_data.get('input_method', 'Unknown')}\n"
        report += f"PIN Attempts: {transaction_data.get('pin_attempts', 1)}\n"
        report += f"Typing Pattern: {result['details'].get('typing_pattern', 'Unknown')}\n\n"
        
        report += f"Typing Speed: {result['details'].get('typing_speed_cps', 0):.2f} chars/second\n"
        report += f"Time per Character: {result['details'].get('time_per_char_ms', 0):.0f}ms\n\n"
        
        # NEW: Show ML model contribution if available
        if 'ml_risk_score' in result['details']:
            report += f"ML Model Risk: {result['details']['ml_risk_score']:.3f}\n"
            report += f"Rule-Based Risk: {result['details']['rule_based_score']:.3f}\n\n"
        
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
    print("🧪 TESTING ENHANCED TYPING SPEED ANALYSIS ENGINE")
    print("="*70)
    
    # Initialize engine
    engine = TypingSpeedAnalysisEngine()
    
    # Test Case 1: Normal Human Typing
    print("\n\nTEST CASE 1: Normal Human Typing")
    print("-"*70)
    test1 = {
        'pin_entry_time_ms': 2400,
        'pin_length': 4,
        'keystroke_intervals': [650, 580, 620, 550],
        'input_method': 'keyboard',
        'pin_attempts': 1,
        'typing_pattern': 'normal'
    }
    result1 = engine.analyze_typing_speed(test1)
    print(engine.get_typing_report(test1))
    
    # Test Case 2: BOT DETECTED (Too Fast)
    print("\n\nTEST CASE 2: 🚨 BOT DETECTED (Instantaneous)")
    print("-"*70)
    test2 = {
        'pin_entry_time_ms': 45,
        'pin_length': 4,
        'keystroke_intervals': [10, 10, 10, 15],
        'input_method': 'keyboard',
        'pin_attempts': 1,
        'typing_pattern': 'bot'
    }
    result2 = engine.analyze_typing_speed(test2)
    print(engine.get_typing_report(test2))
    
    # Test Case 3: Copy-Paste Attack
    print("\n\nTEST CASE 3: 🚨 COPY-PASTE ATTACK")
    print("-"*70)
    test3 = {
        'pin_entry_time_ms': 150,
        'pin_length': 4,
        'keystroke_intervals': [],
        'input_method': 'paste',
        'pin_attempts': 1
    }
    result3 = engine.analyze_typing_speed(test3)
    print(engine.get_typing_report(test3))
    
    # Test Case 4: Erratic Typing (Social Engineering)
    print("\n\nTEST CASE 4: ⚠️ ERRATIC TYPING (Reading from paper?)")
    print("-"*70)
    test4 = {
        'pin_entry_time_ms': 18000,
        'pin_length': 4,
        'keystroke_intervals': [4500, 4800, 4300, 4400],
        'input_method': 'keyboard',
        'pin_attempts': 1,
        'typing_pattern': 'erratic'
    }
    result4 = engine.analyze_typing_speed(test4)
    print(engine.get_typing_report(test4))
    
    # Test Case 5: Multiple Failed Attempts
    print("\n\nTEST CASE 5: 🚨 MULTIPLE FAILED ATTEMPTS")
    print("-"*70)
    test5 = {
        'pin_entry_time_ms': 3000,
        'pin_length': 4,
        'keystroke_intervals': [700, 750, 800, 750],
        'input_method': 'keyboard',
        'pin_attempts': 3
    }
    result5 = engine.analyze_typing_speed(test5)
    print(engine.get_typing_report(test5))
    
    # NEW: Test analyze() method for master engine
    print("\n\nTEST CASE 6: Testing analyze() method for master engine")
    print("-"*70)
    test6 = {
        'pin_entry_time_ms': 45,
        'avg_keystroke_interval': 11,
        'input_method': 'paste',
        'typing_pattern': 'bot'
    }
    decision, risk, reason = engine.analyze(test6)
    print(f"Decision: {decision}")
    print(f"Risk Score: {risk:.3f}")
    print(f"Reason: {reason}")
    
    print("\n" + "="*70)
    print("✅ ENHANCED TYPING SPEED ANALYSIS ENGINE TESTS COMPLETE")
    print("="*70)