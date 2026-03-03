"""
STAGE 6: ESCALATION PATH & ALERT SYSTEM (ENHANCED)
Determines appropriate action and escalation level based on risk
Author: [Your Team Name]
ENHANCED VERSION with emergency handling and master engine compatibility
"""

from datetime import datetime
from enum import Enum

class EscalationLevel(Enum):
    """Escalation priority levels"""
    NO_ACTION = 0
    LOW_PRIORITY = 1
    MEDIUM_PRIORITY = 2
    HIGH_PRIORITY = 3
    CRITICAL = 4

class AlertType(Enum):
    """Types of alerts that can be triggered"""
    SMS_ALERT = "sms"
    EMAIL_ALERT = "email"
    PUSH_NOTIFICATION = "push"
    BANK_NOTIFICATION = "bank"
    FREEZE_ACCOUNT = "freeze"
    MANUAL_REVIEW = "review"
    LAW_ENFORCEMENT = "police"

class EscalationPathEngine:
    """
    Stage 6: Escalation Path & Alert Management
    
    Determines:
    1. Escalation priority level
    2. Alert channels to trigger
    3. Follow-up actions required
    4. Stakeholder notifications
    
    NEW ENHANCEMENTS:
    - get_escalation_path() method for master engine
    - Enhanced emergency flag handling
    - Improved senior citizen escalation
    """
    
    def __init__(self):
        print("🚨 Initializing Escalation Path Engine")
        
        # Escalation thresholds
        self.CRITICAL_THRESHOLD = 0.85
        self.HIGH_THRESHOLD = 0.70
        self.MEDIUM_THRESHOLD = 0.50
        self.LOW_THRESHOLD = 0.30
        
        # Senior citizen has lower thresholds
        self.SENIOR_CRITICAL_THRESHOLD = 0.70
        self.SENIOR_HIGH_THRESHOLD = 0.55
        
        print("✅ Escalation Path Engine Ready")
    
    def _determine_escalation_level(self, risk_score, is_senior, amount, blocked_stages, is_emergency=False):
        """
        Determine appropriate escalation level
        
        NEW: Added is_emergency parameter for critical scenarios
        """
        
        # NEW: Emergency scenarios automatically escalate to CRITICAL
        if is_emergency and (is_senior or amount > 10000):
            return EscalationLevel.CRITICAL
        
        # Critical escalation scenarios
        if risk_score >= self.CRITICAL_THRESHOLD:
            return EscalationLevel.CRITICAL
        
        # Senior citizens - more protective
        if is_senior:
            if risk_score >= self.SENIOR_CRITICAL_THRESHOLD:
                return EscalationLevel.CRITICAL
            elif risk_score >= self.SENIOR_HIGH_THRESHOLD:
                return EscalationLevel.HIGH_PRIORITY
            elif risk_score >= self.MEDIUM_THRESHOLD:
                return EscalationLevel.MEDIUM_PRIORITY
            else:
                return EscalationLevel.LOW_PRIORITY
        
        # High-value transactions
        if amount > 50000 and risk_score >= self.HIGH_THRESHOLD:
            return EscalationLevel.CRITICAL
        
        # Standard thresholds
        if risk_score >= self.HIGH_THRESHOLD:
            return EscalationLevel.HIGH_PRIORITY
        elif risk_score >= self.MEDIUM_THRESHOLD:
            return EscalationLevel.MEDIUM_PRIORITY
        elif risk_score >= self.LOW_THRESHOLD:
            return EscalationLevel.LOW_PRIORITY
        else:
            return EscalationLevel.NO_ACTION
    
    def _select_alert_channels(self, escalation_level, is_senior, blocked_stages):
        """Select appropriate alert channels based on escalation level"""
        alerts = []
        
        if escalation_level == EscalationLevel.CRITICAL:
            # All channels + freeze account
            alerts = [
                AlertType.SMS_ALERT,
                AlertType.EMAIL_ALERT,
                AlertType.PUSH_NOTIFICATION,
                AlertType.BANK_NOTIFICATION,
                AlertType.FREEZE_ACCOUNT,
                AlertType.MANUAL_REVIEW
            ]
            
            # If senior citizen is targeted
            if is_senior:
                alerts.append(AlertType.LAW_ENFORCEMENT)
        
        elif escalation_level == EscalationLevel.HIGH_PRIORITY:
            alerts = [
                AlertType.SMS_ALERT,
                AlertType.EMAIL_ALERT,
                AlertType.PUSH_NOTIFICATION,
                AlertType.BANK_NOTIFICATION,
                AlertType.MANUAL_REVIEW
            ]
        
        elif escalation_level == EscalationLevel.MEDIUM_PRIORITY:
            alerts = [
                AlertType.PUSH_NOTIFICATION,
                AlertType.EMAIL_ALERT,
                AlertType.BANK_NOTIFICATION
            ]
        
        elif escalation_level == EscalationLevel.LOW_PRIORITY:
            alerts = [
                AlertType.PUSH_NOTIFICATION
            ]
        
        return alerts
    
    def _generate_user_message(self, escalation_level, blocked_stages, risk_factors):
        """Generate user-facing message"""
        
        if escalation_level == EscalationLevel.CRITICAL:
            message = {
                'title': '🚨 CRITICAL SECURITY ALERT',
                'body': 'Your transaction has been blocked due to multiple high-risk fraud indicators. Your account has been temporarily frozen for your protection.',
                'action': 'Please contact customer support immediately: 1800-XXX-XXXX',
                'severity': 'critical'
            }
        
        elif escalation_level == EscalationLevel.HIGH_PRIORITY:
            message = {
                'title': '⚠️ SECURITY WARNING',
                'body': 'We detected suspicious activity in your transaction. This payment has been blocked for your safety.',
                'action': 'If this was you, please verify via SMS OTP. Otherwise, contact support.',
                'severity': 'high'
            }
        
        elif escalation_level == EscalationLevel.MEDIUM_PRIORITY:
            message = {
                'title': '⚠️ Transaction Alert',
                'body': 'We noticed some unusual patterns. Please review the transaction details carefully.',
                'action': 'Confirm via OTP to proceed, or cancel if not initiated by you.',
                'severity': 'medium'
            }
        
        elif escalation_level == EscalationLevel.LOW_PRIORITY:
            message = {
                'title': 'ℹ️ Security Notice',
                'body': 'This transaction has minor security flags. Please confirm it\'s you.',
                'action': 'Tap to confirm and proceed.',
                'severity': 'low'
            }
        
        else:
            message = {
                'title': '✅ Transaction Verified',
                'body': 'All security checks passed.',
                'action': 'Proceed to enter PIN.',
                'severity': 'none'
            }
        
        # Add specific risk factors
        if risk_factors:
            message['risk_factors'] = risk_factors[:3]  # Top 3 risks
        
        return message
    
    def _generate_stakeholder_alerts(self, escalation_level, transaction_data, user_profile):
        """Generate alerts for different stakeholders"""
        
        stakeholder_alerts = {
            'user': {},
            'bank_fraud_team': {},
            'customer_support': {},
            'law_enforcement': None
        }
        
        # User alert
        stakeholder_alerts['user'] = {
            'channels': ['sms', 'push', 'email'],
            'message': f"Transaction of ₹{transaction_data['amount']:.2f} blocked due to security concerns.",
            'action_required': escalation_level.value >= EscalationLevel.HIGH_PRIORITY.value
        }
        
        # Bank fraud team
        if escalation_level.value >= EscalationLevel.MEDIUM_PRIORITY.value:
            stakeholder_alerts['bank_fraud_team'] = {
                'priority': escalation_level.name,
                'transaction_id': transaction_data.get('transaction_id'),
                'user_id': transaction_data.get('user_id'),
                'amount': transaction_data.get('amount'),
                'risk_score': transaction_data.get('risk_score', 0),
                'action': 'Manual review required'
            }
        
        # Customer support
        if escalation_level.value >= EscalationLevel.HIGH_PRIORITY.value:
            stakeholder_alerts['customer_support'] = {
                'priority': 'urgent',
                'expected_user_call': True,
                'talking_points': [
                    'Transaction blocked for security',
                    'Multiple fraud indicators detected',
                    'Account temporarily restricted'
                ]
            }
        
        # Law enforcement (only for critical cases with seniors)
        if (escalation_level == EscalationLevel.CRITICAL and 
            user_profile.get('age', 0) >= 65):
            stakeholder_alerts['law_enforcement'] = {
                'cyber_crime_unit': True,
                'senior_citizen_targeted': True,
                'amount': transaction_data.get('amount'),
                'fraud_type': 'targeted_senior_fraud'
            }
        
        return stakeholder_alerts
    
    def _determine_follow_up_actions(self, escalation_level, is_senior):
        """Determine required follow-up actions"""
        
        actions = []
        
        if escalation_level == EscalationLevel.CRITICAL:
            actions = [
                {'action': 'freeze_account', 'duration': '24_hours', 'priority': 'immediate'},
                {'action': 'send_otp_verification', 'priority': 'immediate'},
                {'action': 'flag_for_review', 'assigned_to': 'fraud_team', 'sla': '1_hour'},
                {'action': 'notify_registered_contacts', 'priority': 'immediate'},
                {'action': 'log_incident', 'database': 'fraud_incidents', 'priority': 'immediate'}
            ]
            
            if is_senior:
                actions.append({
                    'action': 'initiate_wellness_check',
                    'assigned_to': 'customer_care',
                    'priority': 'urgent'
                })
        
        elif escalation_level == EscalationLevel.HIGH_PRIORITY:
            actions = [
                {'action': 'require_additional_authentication', 'method': 'otp', 'priority': 'immediate'},
                {'action': 'flag_for_review', 'assigned_to': 'fraud_team', 'sla': '4_hours'},
                {'action': 'send_alert_notifications', 'priority': 'high'},
                {'action': 'log_incident', 'database': 'fraud_incidents', 'priority': 'high'}
            ]
        
        elif escalation_level == EscalationLevel.MEDIUM_PRIORITY:
            actions = [
                {'action': 'require_otp_confirmation', 'priority': 'normal'},
                {'action': 'send_notification', 'channel': 'push', 'priority': 'normal'},
                {'action': 'log_incident', 'database': 'security_logs', 'priority': 'normal'}
            ]
        
        elif escalation_level == EscalationLevel.LOW_PRIORITY:
            actions = [
                {'action': 'log_for_analytics', 'database': 'security_logs', 'priority': 'low'}
            ]
        
        return actions
    
    # ========================================================================
    # NEW: get_escalation_path() method for master engine compatibility
    # ========================================================================
    
    def get_escalation_path(self, risk_score, is_emergency=False, fraud_indicators=None):
        """
        NEW: Simplified method for master engine
        Determine escalation level and alerts based on risk score
        
        Returns: dict with level, alerts, actions
        """
        if is_emergency or risk_score >= 0.9:
            return {
                'level': EscalationLevel.CRITICAL,
                'level_name': 'LEVEL 4: CRITICAL',
                'action': 'HARD_BLOCK',
                'alerts': [
                    AlertType.FREEZE_ACCOUNT,
                    AlertType.LAW_ENFORCEMENT,
                    AlertType.SMS_ALERT,
                    AlertType.PUSH_NOTIFICATION,
                    AlertType.BANK_NOTIFICATION
                ],
                'message': '🚨 CRITICAL: Transaction blocked and account frozen. Police notified.',
                'require_manual_review': True
            }
        
        elif risk_score >= 0.7:
            return {
                'level': EscalationLevel.HIGH_PRIORITY,
                'level_name': 'LEVEL 3: HIGH PRIORITY',
                'action': 'ESCROW_FREEZE',
                'alerts': [
                    AlertType.MANUAL_REVIEW,
                    AlertType.SMS_ALERT,
                    AlertType.PUSH_NOTIFICATION,
                    AlertType.BANK_NOTIFICATION
                ],
                'message': '⚠️ HIGH RISK: Transaction frozen. Manual review required.',
                'require_manual_review': True
            }
        
        elif risk_score >= 0.4:
            return {
                'level': EscalationLevel.MEDIUM_PRIORITY,
                'level_name': 'LEVEL 2: MEDIUM PRIORITY',
                'action': 'STEP_UP_AUTH',
                'alerts': [
                    AlertType.PUSH_NOTIFICATION,
                    AlertType.SMS_ALERT
                ],
                'message': '⚠️ Additional authentication required (biometric/OTP).',
                'require_manual_review': False
            }
        
        elif risk_score >= 0.2:
            return {
                'level': EscalationLevel.LOW_PRIORITY,
                'level_name': 'LEVEL 1: LOW PRIORITY',
                'action': 'LOG_ONLY',
                'alerts': [
                    AlertType.PUSH_NOTIFICATION
                ],
                'message': 'ℹ️ Transaction flagged for monitoring.',
                'require_manual_review': False
            }
        
        else:
            return {
                'level': EscalationLevel.NO_ACTION,
                'level_name': 'LEVEL 0: NO ACTION',
                'action': 'APPROVE',
                'alerts': [],
                'message': '✅ Transaction approved.',
                'require_manual_review': False
            }
    
    def create_escalation_path(self, analysis_results, transaction_data, user_profile):
        """
        Create complete escalation path based on fraud analysis
        
        Args:
            analysis_results: dict from master fraud detection system
            transaction_data: dict with transaction details
            user_profile: dict with user information
        
        Returns:
            Complete escalation plan with all actions and alerts
        """
        
        print("\n" + "="*70)
        print("🚨 STAGE 6: ESCALATION PATH DETERMINATION")
        print("="*70)
        
        # Extract key information
        overall_risk = analysis_results.get('overall_risk_score', 0)
        final_decision = analysis_results.get('final_decision', 'ALLOW')
        stopped_at = analysis_results.get('stopped_at')
        is_senior = user_profile.get('age', 0) >= 65
        amount = transaction_data.get('amount', 0)
        
        # NEW: Check for emergency flag
        is_emergency = transaction_data.get('is_emergency', False)
        if isinstance(is_emergency, int):
            is_emergency = bool(is_emergency)
        
        # Collect all risk factors
        risk_factors = []
        for stage in ['stage1', 'stage2', 'stage3', 'stage4', 'stage5']:
            if stage in analysis_results:
                flags = analysis_results[stage].get('flags', [])
                risk_factors.extend([f for f in flags if '🚨' in f or '⚠️' in f])
        
        blocked_stages = []
        if stopped_at:
            blocked_stages.append(stopped_at)
        
        # ====================================================================
        # STEP 1: Determine Escalation Level (with emergency handling)
        # ====================================================================
        
        escalation_level = self._determine_escalation_level(
            overall_risk, is_senior, amount, blocked_stages, is_emergency
        )
        
        print(f"\n🎯 Escalation Level: {escalation_level.name}")
        print(f"   Priority: {'⭐' * (escalation_level.value + 1)}")
        
        # NEW: Show if emergency escalation
        if is_emergency:
            print(f"   🚨 EMERGENCY FLAG: Auto-escalated to {escalation_level.name}")
        
        # ====================================================================
        # STEP 2: Select Alert Channels
        # ====================================================================
        
        alert_channels = self._select_alert_channels(
            escalation_level, is_senior, blocked_stages
        )
        
        print(f"\n📢 Alert Channels ({len(alert_channels)}):")
        for channel in alert_channels:
            print(f"   • {channel.value.upper()}")
        
        # ====================================================================
        # STEP 3: Generate User Message
        # ====================================================================
        
        user_message = self._generate_user_message(
            escalation_level, blocked_stages, risk_factors
        )
        
        print(f"\n💬 User Message:")
        print(f"   Title: {user_message['title']}")
        print(f"   Body: {user_message['body'][:80]}...")
        
        # ====================================================================
        # STEP 4: Generate Stakeholder Alerts
        # ====================================================================
        
        stakeholder_alerts = self._generate_stakeholder_alerts(
            escalation_level, transaction_data, user_profile
        )
        
        print(f"\n👥 Stakeholder Notifications:")
        for stakeholder, alert in stakeholder_alerts.items():
            if alert:
                print(f"   • {stakeholder.replace('_', ' ').title()}: ✓")
        
        # ====================================================================
        # STEP 5: Determine Follow-up Actions
        # ====================================================================
        
        follow_up_actions = self._determine_follow_up_actions(
            escalation_level, is_senior
        )
        
        print(f"\n📋 Follow-up Actions ({len(follow_up_actions)}):")
        for action in follow_up_actions[:3]:  # Show first 3
            priority = action.get('priority', 'normal')
            print(f"   • {action['action'].replace('_', ' ').title()} [{priority}]")
        
        # ====================================================================
        # RETURN COMPLETE ESCALATION PATH
        # ====================================================================
        
        escalation_path = {
            'escalation_level': escalation_level.name,
            'priority': escalation_level.value,
            'alert_channels': [ch.value for ch in alert_channels],
            'user_message': user_message,
            'stakeholder_alerts': stakeholder_alerts,
            'follow_up_actions': follow_up_actions,
            'requires_manual_review': escalation_level.value >= EscalationLevel.HIGH_PRIORITY.value,
            'account_action': 'freeze' if escalation_level == EscalationLevel.CRITICAL else 'monitor',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'is_emergency_escalation': is_emergency  # NEW
        }
        
        print("\n" + "="*70)
        
        return escalation_path
    
    def get_escalation_report(self, escalation_path):
        """Generate detailed escalation path report"""
        
        report = "="*70 + "\n"
        report += "🚨 ESCALATION PATH REPORT\n"
        report += "="*70 + "\n\n"
        
        report += f"Escalation Level: {escalation_path['escalation_level']}\n"
        report += f"Priority: {'⭐' * (escalation_path['priority'] + 1)}\n"
        
        # NEW: Show emergency escalation
        if escalation_path.get('is_emergency_escalation'):
            report += f"🚨 EMERGENCY ESCALATION: Auto-escalated due to emergency flag\n"
        
        report += "\nAlert Channels:\n"
        for channel in escalation_path['alert_channels']:
            report += f"  • {channel.upper()}\n"
        
        report += f"\nUser Message:\n"
        report += f"  {escalation_path['user_message']['title']}\n"
        report += f"  {escalation_path['user_message']['body']}\n"
        
        report += f"\nManual Review Required: {'YES' if escalation_path['requires_manual_review'] else 'NO'}\n"
        report += f"Account Action: {escalation_path['account_action'].upper()}\n"
        
        report += "\n" + "="*70 + "\n"
        
        return report


# ============================================================================
# DEMO / TEST
# ============================================================================

if __name__ == "__main__":
    print("="*70)
    print("🧪 TESTING ENHANCED ESCALATION PATH ENGINE")
    print("="*70)
    
    # Initialize engine
    engine = EscalationPathEngine()
    
    # Test Case 1: Critical Fraud - Senior Citizen
    print("\n\nTEST CASE 1: 🚨 CRITICAL FRAUD - Senior Citizen Targeted")
    print("-"*70)
    
    analysis1 = {
        'overall_risk_score': 0.89,
        'final_decision': 'BLOCK',
        'stopped_at': 'stage1',
        'stage1': {
            'flags': ['🚨 Blacklisted domain detected', '⚠️ Suspicious keywords found']
        },
        'stage5': {
            'flags': ['🚨 SOCIAL ENGINEERING DETECTED', '⚠️ NEW MERCHANT for elderly']
        }
    }
    
    txn1 = {
        'transaction_id': 'TXN_FRAUD_001',
        'user_id': 'user_senior_001',
        'amount': 50000,
        'risk_score': 0.89,
        'is_emergency': False
    }
    
    user1 = {'age': 72}
    
    escalation1 = engine.create_escalation_path(analysis1, txn1, user1)
    print(engine.get_escalation_report(escalation1))
    
    # NEW TEST CASE 2: Emergency Escalation
    print("\n\nTEST CASE 2: 🚨 EMERGENCY ESCALATION")
    print("-"*70)
    
    analysis2 = {
        'overall_risk_score': 0.65,  # Not critical normally
        'final_decision': 'WARN',
        'stopped_at': 'stage5',
        'stage5': {
            'flags': ['🚨 VISHING ATTACK', '⚠️ Senior on call']
        }
    }
    
    txn2 = {
        'transaction_id': 'TXN_EMERGENCY_001',
        'user_id': 'user_senior_002',
        'amount': 20000,
        'risk_score': 0.65,
        'is_emergency': True  # EMERGENCY FLAG!
    }
    
    user2 = {'age': 75}
    
    escalation2 = engine.create_escalation_path(analysis2, txn2, user2)
    print(engine.get_escalation_report(escalation2))
    
    # Test Case 3: Medium Risk - Standard User
    print("\n\nTEST CASE 3: ⚠️ MEDIUM RISK - Standard User")
    print("-"*70)
    
    analysis3 = {
        'overall_risk_score': 0.52,
        'final_decision': 'WARN',
        'stopped_at': None,
        'stage2': {
            'flags': ['⚠️ Elevated velocity', '⚠️ New device']
        }
    }
    
    txn3 = {
        'transaction_id': 'TXN_WARN_001',
        'user_id': 'user_regular_001',
        'amount': 8000,
        'risk_score': 0.52,
        'is_emergency': False
    }
    
    user3 = {'age': 35}
    
    escalation3 = engine.create_escalation_path(analysis3, txn3, user3)
    print(engine.get_escalation_report(escalation3))
    
    # NEW: Test get_escalation_path() method for master engine
    print("\n\nTEST CASE 4: Testing get_escalation_path() method")
    print("-"*70)
    
    # Test with high risk + emergency
    path1 = engine.get_escalation_path(risk_score=0.75, is_emergency=True)
    print(f"Risk 0.75 + Emergency: {path1['level_name']}")
    print(f"Action: {path1['action']}")
    print(f"Message: {path1['message']}")
    
    # Test with medium risk
    path2 = engine.get_escalation_path(risk_score=0.55, is_emergency=False)
    print(f"\nRisk 0.55: {path2['level_name']}")
    print(f"Action: {path2['action']}")
    
    print("\n" + "="*70)
    print("✅ ENHANCED ESCALATION PATH ENGINE TESTS COMPLETE")
    print("="*70)