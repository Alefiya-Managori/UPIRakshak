"""
MASTER UPI FRAUD DETECTION ENGINE
Orchestrates all 7 stages with sequential early termination
Author: [Your Team Name]
"""

import time
from datetime import datetime

# Import all stage engines
from source_impl_1 import SourceVerificationEngine
from location_impl_2 import LocationGeoRiskEngine
from behavorial_impl_3 import BehavioralAnalysisEngine
from typingspeed_impl_4 import TypingSpeedAnalysisEngine
from seniorcitizen_impl_5 import SeniorCitizenProtectionEngine
from escalationpath_impl_6 import EscalationPathEngine
from finaldecision import FinalDecisionEngine

class MasterFraudDetectionEngine:
    """
    MASTER UPI FRAUD DETECTION ENGINE
    
    7-Stage Sequential Pipeline with Early Termination:
    Stage 1: Source Verification → If BLOCK, stop
    Stage 2: Location & Geo Risk → If BLOCK, stop
    Stage 3: Behavioral Analysis → If BLOCK, stop
    Stage 4: Typing Speed Analysis → If BLOCK, stop
    Stage 5: Senior Citizen Protection → If BLOCK, stop
    
    If ALL 5 stages pass:
    Stage 6: Escalation Path → Determine alerts
    Stage 7: Final Decision Engine → Ensemble verdict
    
    Target: < 500ms processing time
    """
    
    def __init__(self):
        print("="*80)
        print("🚀 INITIALIZING MASTER FRAUD DETECTION ENGINE")
        print("="*80)
        
        # Initialize all 7 stage engines
        self.source_engine = SourceVerificationEngine()
        self.location_engine = LocationGeoRiskEngine()
        self.behavioral_engine = BehavioralAnalysisEngine()
        self.typing_engine = TypingSpeedAnalysisEngine()
        self.senior_engine = SeniorCitizenProtectionEngine()
        self.escalation_engine = EscalationPathEngine()
        self.final_engine = FinalDecisionEngine()
        
        print("\n" + "="*80)
        print("✅ ALL ENGINES INITIALIZED - READY FOR FRAUD DETECTION")
        print("="*80)
    
    def analyze_transaction(self, transaction, user_history=None):
        """
        Complete fraud detection pipeline
        
        Args:
            transaction: dict with all transaction parameters (18 fields)
            user_history: optional list of user's past transactions
        
        Returns:
            Complete analysis results with decision and timing
        """
        
        start_time = time.time()
        
        results = {
            'transaction_id': transaction.get('transaction_id', 'UNKNOWN'),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'stages': {},
            'final_decision': None,
            'stopped_at': None,
            'processing_time_ms': 0
        }
        
        stage_scores = {}
        
        print("\n" + "="*80)
        print(f"🔍 ANALYZING TRANSACTION: {results['transaction_id']}")
        print("="*80)
        
        # ====================================================================
        # STAGE 1: SOURCE VERIFICATION
        # ====================================================================
        print("\n🔹 STAGE 1: Source Verification")
        stage1_decision, stage1_risk, stage1_reason = self.source_engine.analyze(transaction)
        
        results['stages']['stage1_source'] = {
            'decision': stage1_decision,
            'risk_score': round(stage1_risk, 3),
            'reason': stage1_reason
        }
        stage_scores['source'] = stage1_risk
        
        print(f"   Decision: {stage1_decision} | Risk: {stage1_risk:.3f}")
        print(f"   {stage1_reason}")
        
        if stage1_decision == 'BLOCK':
            results['stopped_at'] = 'stage1'
            results['final_decision'] = self._create_final_decision(
                'BLOCKED', stage1_risk, f'Stage 1: {stage1_reason}', 
                results['stages'], transaction
            )
            results['processing_time_ms'] = round((time.time() - start_time) * 1000, 2)
            return results
        
        # ====================================================================
        # STAGE 2: LOCATION & GEO RISK
        # ====================================================================
        print("\n🔹 STAGE 2: Location & Geo Risk")
        stage2_decision, stage2_risk, stage2_reason = self.location_engine.analyze(
            transaction, user_history
        )
        
        results['stages']['stage2_location'] = {
            'decision': stage2_decision,
            'risk_score': round(stage2_risk, 3),
            'reason': stage2_reason
        }
        stage_scores['location'] = stage2_risk
        
        print(f"   Decision: {stage2_decision} | Risk: {stage2_risk:.3f}")
        print(f"   {stage2_reason}")
        
        if stage2_decision == 'BLOCK':
            results['stopped_at'] = 'stage2'
            results['final_decision'] = self._create_final_decision(
                'BLOCKED', stage2_risk, f'Stage 2: {stage2_reason}',
                results['stages'], transaction
            )
            results['processing_time_ms'] = round((time.time() - start_time) * 1000, 2)
            return results
        
        # ====================================================================
        # STAGE 3: BEHAVIORAL ANALYSIS
        # ====================================================================
        print("\n🔹 STAGE 3: Behavioral Analysis")
        stage3_decision, stage3_risk, stage3_reason = self.behavioral_engine.analyze(transaction)
        
        results['stages']['stage3_behavioral'] = {
            'decision': stage3_decision,
            'risk_score': round(stage3_risk, 3),
            'reason': stage3_reason
        }
        stage_scores['behavioral'] = stage3_risk
        
        print(f"   Decision: {stage3_decision} | Risk: {stage3_risk:.3f}")
        print(f"   {stage3_reason}")
        
        if stage3_decision == 'BLOCK':
            results['stopped_at'] = 'stage3'
            results['final_decision'] = self._create_final_decision(
                'BLOCKED', stage3_risk, f'Stage 3: {stage3_reason}',
                results['stages'], transaction
            )
            results['processing_time_ms'] = round((time.time() - start_time) * 1000, 2)
            return results
        
        # ====================================================================
        # STAGE 4: TYPING SPEED ANALYSIS
        # ====================================================================
        print("\n🔹 STAGE 4: Typing Speed Analysis")
        stage4_decision, stage4_risk, stage4_reason = self.typing_engine.analyze(transaction)
        
        results['stages']['stage4_typing'] = {
            'decision': stage4_decision,
            'risk_score': round(stage4_risk, 3),
            'reason': stage4_reason
        }
        stage_scores['typing'] = stage4_risk
        
        print(f"   Decision: {stage4_decision} | Risk: {stage4_risk:.3f}")
        print(f"   {stage4_reason}")
        
        if stage4_decision == 'BLOCK':
            results['stopped_at'] = 'stage4'
            results['final_decision'] = self._create_final_decision(
                'BLOCKED', stage4_risk, f'Stage 4: {stage4_reason}',
                results['stages'], transaction
            )
            results['processing_time_ms'] = round((time.time() - start_time) * 1000, 2)
            return results
        
        # ====================================================================
        # STAGE 5: SENIOR CITIZEN PROTECTION
        # ====================================================================
        print("\n🔹 STAGE 5: Senior Citizen Protection")
        stage5_decision, stage5_risk, stage5_reason = self.senior_engine.analyze(transaction)
        
        results['stages']['stage5_senior'] = {
            'decision': stage5_decision,
            'risk_score': round(stage5_risk, 3),
            'reason': stage5_reason
        }
        stage_scores['senior'] = stage5_risk
        
        print(f"   Decision: {stage5_decision} | Risk: {stage5_risk:.3f}")
        print(f"   {stage5_reason}")
        
        if stage5_decision == 'BLOCK':
            results['stopped_at'] = 'stage5'
            results['final_decision'] = self._create_final_decision(
                'BLOCKED', stage5_risk, f'Stage 5: {stage5_reason}',
                results['stages'], transaction
            )
            results['processing_time_ms'] = round((time.time() - start_time) * 1000, 2)
            return results
        
        # ====================================================================
        # ALL STAGES PASSED - PROCEED TO ENSEMBLE DECISION
        # ====================================================================
        
        print("\n" + "="*80)
        print("✅ ALL 5 STAGES PASSED - PROCEEDING TO FINAL DECISION")
        print("="*80)
        
        # ====================================================================
        # STAGE 7: FINAL ENSEMBLE DECISION
        # ====================================================================
        print("\n🔹 STAGE 7: Final Decision Engine")
        final_decision, final_risk, confidence = self.final_engine.make_decision(
            stage_scores, transaction
        )
        
        summary = self.final_engine.get_decision_summary(
            final_decision, final_risk, confidence, stage_scores
        )
        
        results['stages']['stage7_ensemble'] = {
            'decision': final_decision,
            'risk_score': round(final_risk, 3),
            'confidence': round(confidence, 3),
            'summary': summary
        }
        
        print(f"   Decision: {final_decision} | Risk: {final_risk:.3f} | Confidence: {confidence:.3f}")
        
        # ====================================================================
        # STAGE 6: ESCALATION PATH
        # ====================================================================
        print("\n🔹 STAGE 6: Escalation Path")
        
        is_emergency = transaction.get('is_emergency', False) or \
                      transaction.get('is_on_call_during_transaction', False)
        
        escalation = self.escalation_engine.get_escalation_path(
            final_risk, is_emergency
        )
        
        results['stages']['stage6_escalation'] = {
            'level': escalation['level_name'],
            'action': escalation['action'],
            'alerts': (
        [alert.value for alert in escalation['alerts']]
        if escalation['alerts'] and hasattr(escalation['alerts'][0], 'value')
        else escalation['alerts']
    ),
            'message': escalation['message'],
            'manual_review_required': escalation['require_manual_review']
        }
        
        print(f"   Level: {escalation['level_name']}")
        print(f"   Action: {escalation['action']}")
        
        # ====================================================================
        # FINAL RESULT
        # ====================================================================
        
        if final_decision == 'BLOCK':
            verdict = 'BLOCKED'
            reason = f"Ensemble model blocked (risk: {final_risk:.2f})"
        elif final_decision == 'WARN':
            verdict = 'WARNING'
            reason = f"Medium risk detected (risk: {final_risk:.2f}) - {escalation['message']}"
        else:
            verdict = 'APPROVED'
            reason = f"All checks passed (risk: {final_risk:.2f})"
        
        results['final_decision'] = self._create_final_decision(
            verdict, final_risk, reason, results['stages'], transaction
        )
        
        results['processing_time_ms'] = round((time.time() - start_time) * 1000, 2)
        
        return results
    
    def _create_final_decision(self, verdict, risk_score, reason, stages, transaction):
        """Create final decision summary"""
        return {
            'verdict': verdict,
            'risk_score': round(risk_score, 3),
            'reason': reason,
            'transaction_amount': transaction.get('amount', 0),
            'merchant_name': transaction.get('merchant_name', 'Unknown'),
            'user_id': transaction.get('user_id', 'Unknown'),
            'user_age': transaction.get('user_age', 0),
            'recommended_action': self._get_recommended_action(verdict, risk_score),
            'stages_summary': {
                stage: data.get('decision', 'N/A') for stage, data in stages.items()
            }
        }
    
    def _get_recommended_action(self, verdict, risk_score):
        """Get recommended action"""
        if verdict == 'BLOCKED':
            if risk_score >= 0.9:
                return "🚨 HARD BLOCK - Freeze account and notify authorities"
            else:
                return "⛔ BLOCK - Reject transaction and alert user"
        elif verdict == 'WARNING':
            return "⚠️ ADDITIONAL AUTH - Request step-up authentication"
        else:
            return "✅ APPROVE - Process transaction normally"
    
    def print_analysis_report(self, results):
        """Print formatted analysis report"""
        print("\n" + "="*80)
        print("📊 FRAUD DETECTION ANALYSIS REPORT")
        print("="*80)
        print(f"Transaction ID: {results['transaction_id']}")
        print(f"Analysis Time: {results['timestamp']}")
        print(f"Processing Time: {results['processing_time_ms']}ms")
        
        if results['stopped_at']:
            print(f"⚠️  STOPPED AT: {results['stopped_at'].upper()}")
        
        print("\n" + "-"*80)
        print("STAGE-BY-STAGE ANALYSIS:")
        print("-"*80)
        
        for stage_name, stage_data in results['stages'].items():
            stage_num = stage_name.split('_')[0].replace('stage', 'Stage ')
            print(f"\n{stage_num}: {stage_name.split('_', 1)[1].upper()}")
            print(f"   Decision: {stage_data.get('decision', 'N/A')}")
            print(f"   Risk: {stage_data.get('risk_score', 'N/A')}")
            if 'reason' in stage_data:
                print(f"   Reason: {stage_data['reason']}")
            if 'level' in stage_data:
                print(f"   Escalation: {stage_data['level']}")
                print(f"   Action: {stage_data['action']}")
        
        print("\n" + "="*80)
        print("🎯 FINAL DECISION")
        print("="*80)
        
        decision = results['final_decision']
        verdict_emoji = {
            'BLOCKED': '🚨',
            'WARNING': '⚠️',
            'APPROVED': '✅'
        }
        
        print(f"\n{verdict_emoji.get(decision['verdict'], '❓')} VERDICT: {decision['verdict']}")
        print(f"Risk Score: {decision['risk_score']:.3f}")
        print(f"Reason: {decision['reason']}")
        print(f"\nTransaction Details:")
        print(f"   Amount: ₹{decision['transaction_amount']}")
        print(f"   Merchant: {decision['merchant_name']}")
        print(f"   User: {decision['user_id']} (Age: {decision['user_age']})")
        print(f"\nRecommended Action:")
        print(f"   {decision['recommended_action']}")
        print("\n" + "="*80)


# ============================================================================
# DEMO / TEST
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("🧪 TESTING MASTER FRAUD DETECTION ENGINE")
    print("="*80)
    
    # Initialize master engine
    system = MasterFraudDetectionEngine()
    
    # ========================================================================
    # TEST CASE 1: VISHING ATTACK (Senior on call)
    # ========================================================================
    print("\n\n" + "="*80)
    print("TEST CASE 1: 🚨 VISHING ATTACK - Senior Citizen On Call")
    print("="*80)
    
    test_vishing = {
        'transaction_id': 'TXN_TEST_001',
        'user_id': 'user_001',
        'amount': 25000,
        'merchant_name': 'KBC Lottery',
        'timestamp': '2025-01-21 22:30:00',
        'hour_of_day': 22,
        'user_age': 72,
        'payment_source': 'whatsapp',
        'is_malicious_link': 1,
        'ip_country': 'India',
        'gps_country': 'India',
        'is_rooted': 0,
        'is_emulator': 0,
        'mock_location_enabled': 0,
        'pin_entry_time_ms': 12000,  # Slow typing
        'input_method': 'keyboard',
        'is_on_call_during_transaction': 1,  # VISHING!
        'sender_bank': 'HDFC'
    }
    
    result1 = system.analyze_transaction(test_vishing)
    system.print_analysis_report(result1)
    
    # ========================================================================
    # TEST CASE 2: BOT ATTACK (Superhuman typing)
    # ========================================================================
    print("\n\n" + "="*80)
    print("TEST CASE 2: 🚨 BOT ATTACK - Superhuman Typing Speed")
    print("="*80)
    
    test_bot = {
        'transaction_id': 'TXN_TEST_002',
        'user_id': 'user_002',
        'amount': 8000,
        'merchant_name': 'Amazon',
        'timestamp': '2025-01-21 14:00:00',
        'hour_of_day': 14,
        'user_age': 35,
        'payment_source': 'qr_scan',
        'is_malicious_link': 0,
        'ip_country': 'India',
        'gps_country': 'India',
        'is_rooted': 1,
        'is_emulator': 1,
        'mock_location_enabled': 0,
        'pin_entry_time_ms': 45,  # BOT!
        'input_method': 'paste',
        'is_on_call_during_transaction': 0,
        'sender_bank': 'SBI'
    }
    
    result2 = system.analyze_transaction(test_bot)
    system.print_analysis_report(result2)
    
    # ========================================================================
    # TEST CASE 3: LEGITIMATE TRANSACTION
    # ========================================================================
    print("\n\n" + "="*80)
    print("TEST CASE 3: ✅ LEGITIMATE TRANSACTION")
    print("="*80)
    
    test_legit = {
        'transaction_id': 'TXN_TEST_003',
        'user_id': 'user_003',
        'amount': 850,
        'merchant_name': 'Swiggy',
        'timestamp': '2025-01-21 13:00:00',
        'hour_of_day': 13,
        'user_age': 28,
        'payment_source': 'direct_upi',
        'is_malicious_link': 0,
        'ip_country': 'India',
        'gps_country': 'India',
        'is_rooted': 0,
        'is_emulator': 0,
        'mock_location_enabled': 0,
        'pin_entry_time_ms': 2200,
        'input_method': 'keyboard',
        'is_on_call_during_transaction': 0,
        'sender_bank': 'HDFC'
    }
    
    result3 = system.analyze_transaction(test_legit)
    system.print_analysis_report(result3)
    
    print("\n" + "="*80)
    print("✅ ALL MASTER ENGINE TESTS COMPLETED")
    print("="*80)