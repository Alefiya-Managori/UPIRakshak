"""
FOCUSED UPI FRAUD DETECTION DATASET GENERATOR
Only 18-20 REALISTIC parameters that UPI backend can capture
Optimized for enhanced fraud detection features
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Configuration
NUM_TRANSACTIONS = 150
FRAUD_RATE = 0.02  # 2% fraud rate
NUM_USERS = 50
NUM_MERCHANTS = 60

np.random.seed(42)
random.seed(42)

print("="*80)
print("📊 FOCUSED UPI FRAUD DETECTION DATASET (18 PARAMETERS)")
print("="*80)
print(f"Generating {NUM_TRANSACTIONS} transactions with {FRAUD_RATE*100}% fraud rate")
print("="*80)

# ============================================================================
# REALISTIC DATA FOR INDIA
# ============================================================================

indian_cities = ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Kolkata']

merchant_names = [
    # Legitimate (50)
    'Swiggy', 'Zomato', 'Amazon', 'Flipkart', 'BigBazaar', 'DMart',
    'Apollo Pharmacy', 'BookMyShow', 'Ola', 'Uber', 'PayTM Mall',
    'Reliance Digital', 'Dominos', 'McDonalds', 'KFC', 'Starbucks',
    'PVR Cinemas', 'MedPlus', 'Croma', 'Shoppers Stop', 'Pantaloons',
    'Myntra', 'Ajio', 'Nykaa', 'FirstCry', 'BigBasket', 'Grofers',
    'BookMyShow', 'RedBus', 'MakeMyTrip', 'GoIbibo', 'Cleartrip',
    'Decathlon', 'Woodland', 'Bata', 'Nike', 'Adidas', 'Puma',
    'Tanishq', 'Kalyan Jewellers', 'More Supermarket', 'Spencer',
    'FabIndia', 'Westside', 'Lifestyle', 'Central', 'Max Fashion',
    'HomeCenter', 'IKEA', 'Urban Ladder', 'Pepperfry', 'FabFurnish',
    # Suspicious (10)
    'KBC Lottery', 'Prize Winner', 'Urgent KYC', 'Police Verification',
    'Income Tax Refund', 'Quick Cash', 'Paytm Support', 'Amazon Prize',
    'Lucky Draw Winner', 'Bank Update'
]

banks = ['HDFC', 'SBI']  # Only 2 banks as requested

# ============================================================================
# 18 CRITICAL PARAMETERS (Backend can capture these)
# ============================================================================
"""
PARAMETER LIST (18 Total):

1. transaction_id - Unique identifier
2. user_id - User identifier
3. amount - Transaction amount
4. merchant_name - Payee name
5. timestamp - Transaction datetime
6. hour_of_day - Hour (0-23)
7. user_age - User age (from KYC)
8. payment_source - How initiated (qr/link/sms/whatsapp/direct)
9. is_malicious_link - Detected phishing (0/1)
10. ip_country - IP-based country
11. gps_country - GPS-based country
12. is_rooted - Rooted/jailbroken device (0/1)
13. is_emulator - Emulator detection (0/1)
14. mock_location_enabled - Fake GPS detected (0/1)
15. pin_entry_time_ms - Time to enter PIN (milliseconds)
16. input_method - How PIN entered (keyboard/paste/autofill)
17. is_on_call - User on phone call during txn (0/1)
18. sender_bank - User's bank
"""

def calculate_age_from_year(birth_year):
    """Calculate age from birth year"""
    return datetime.now().year - birth_year

def generate_realistic_amount(category='normal'):
    """Generate realistic Indian UPI amounts"""
    if category == 'normal':
        cat = np.random.choice(['micro', 'small', 'medium'], p=[0.50, 0.35, 0.15])
        if cat == 'micro':
            return round(np.random.uniform(50, 500), 2)
        elif cat == 'small':
            return round(np.random.uniform(500, 2000), 2)
        else:
            return round(np.random.uniform(2000, 5000), 2)
    else:
        return round(np.random.uniform(8000, 40000), 2)

# Generate user profiles (with ages)
user_profiles = {}
for i in range(1, NUM_USERS + 1):
    # Age distribution: 60% young (25-45), 30% middle (46-64), 10% senior (65+)
    age_category = np.random.choice(['young', 'middle', 'senior'], p=[0.60, 0.30, 0.10])
    
    if age_category == 'young':
        age = random.randint(25, 45)
    elif age_category == 'middle':
        age = random.randint(46, 64)
    else:
        age = random.randint(65, 82)
    
    user_profiles[f'user_{i:03d}'] = {
        'age': age,
        'preferred_city': random.choice(indian_cities),
        'avg_amount': random.uniform(800, 2500),
        'transaction_count': 0
    }

# Calculate fraud count
num_fraud = max(1, int(NUM_TRANSACTIONS * FRAUD_RATE))
num_legit = NUM_TRANSACTIONS - num_fraud

print(f"\n📊 Distribution:")
print(f"   ✅ Legitimate: {num_legit} ({num_legit/NUM_TRANSACTIONS*100:.1f}%)")
print(f"   🚨 Fraudulent: {num_fraud} ({num_fraud/NUM_TRANSACTIONS*100:.1f}%)")

transaction_types = ['legitimate'] * num_legit + ['fraudulent'] * num_fraud
random.shuffle(transaction_types)

base_time = datetime.now() - timedelta(days=30)
transactions = []

for idx, txn_type in enumerate(transaction_types, 1):
    user_id = f'user_{random.randint(1, NUM_USERS):03d}'
    user_info = user_profiles[user_id]
    
    # Generate timestamp with realistic hour distribution
    hour_weights = [0.01]*6 + [0.03]*3 + [0.08]*9 + [0.06]*6
    hour = int(np.random.choice(range(24), p=np.array(hour_weights)/sum(hour_weights)))
    
    timestamp = base_time + timedelta(
        days=random.randint(0, 30),
        hours=hour,
        minutes=random.randint(0, 59)
    )
    
    if txn_type == 'legitimate':
        # ====================================================================
        # LEGITIMATE TRANSACTION
        # ====================================================================
        amount = generate_realistic_amount('normal')
        merchant_num = random.randint(1, 50)
        merchant_name = merchant_names[merchant_num - 1]
        
        # Payment source (most are QR or direct UPI)
        payment_source = random.choices(
            ['qr_scan', 'direct_upi', 'link'],
            weights=[0.60, 0.30, 0.10]
        )[0]
        
        # Safe parameters
        is_malicious_link = 0
        ip_country = 'India'
        gps_country = 'India'
        is_rooted = 0
        is_emulator = 0
        mock_location_enabled = 0
        
        # Normal typing (400-600ms per character, 4 digits = 1600-2400ms)
        pin_entry_time = random.randint(1600, 2800)
        input_method = 'keyboard'
        
        # Not on call
        is_on_call = 0
        
        is_fraud = 0
        fraud_type = 'none'
    
    else:
        # ====================================================================
        # FRAUDULENT TRANSACTION
        # ====================================================================
        fraud_pattern = random.choice([
            'phishing_link',      # Malicious link
            'bot_attack',         # Superhuman typing
            'vishing_senior',     # Senior on call
            'location_spoof',     # GPS faker
            'high_amount'         # Unusually high
        ])
        
        if fraud_pattern == 'phishing_link':
            # Phishing via SMS/WhatsApp link
            amount = round(np.random.uniform(10000, 30000), 2)
            merchant_num = random.randint(51, 60)
            merchant_name = merchant_names[merchant_num - 1]
            payment_source = random.choice(['sms', 'whatsapp', 'link'])
            
            is_malicious_link = 1  # PHISHING!
            ip_country = random.choice(['USA', 'China', 'Russia'])
            gps_country = 'India'
            is_rooted = random.choice([0, 1])
            is_emulator = random.choice([0, 1])
            mock_location_enabled = 0
            
            pin_entry_time = random.randint(1800, 3000)
            input_method = 'keyboard'
            is_on_call = 0
            fraud_type = 'phishing_link'
        
        elif fraud_pattern == 'bot_attack':
            # Automated bot with superhuman speed
            amount = round(np.random.uniform(5000, 15000), 2)
            merchant_num = random.randint(1, 60)
            merchant_name = merchant_names[merchant_num - 1]
            payment_source = random.choice(['qr_scan', 'direct_upi'])
            
            is_malicious_link = 0
            ip_country = 'India'
            gps_country = 'India'
            is_rooted = 1
            is_emulator = 1
            mock_location_enabled = 0
            
            # BOT - VERY FAST (30-80ms total)
            pin_entry_time = random.randint(30, 80)
            input_method = random.choice(['paste', 'autofill'])
            is_on_call = 0
            fraud_type = 'bot_attack'
        
        elif fraud_pattern == 'vishing_senior':
            # VISHING - Senior on call being scammed
            senior_users = [uid for uid, info in user_profiles.items() if info['age'] >= 65]
            if senior_users:
                user_id = random.choice(senior_users)
                user_info = user_profiles[user_id]
            
            amount = round(np.random.uniform(15000, 40000), 2)
            merchant_num = random.randint(51, 60)
            merchant_name = merchant_names[merchant_num - 1]
            payment_source = random.choice(['sms', 'whatsapp'])
            
            is_malicious_link = random.choice([0, 1])
            ip_country = 'India'
            gps_country = 'India'
            is_rooted = 0
            is_emulator = 0
            mock_location_enabled = 0
            
            # Slow typing (reading PIN from paper: 8-15 seconds)
            pin_entry_time = random.randint(8000, 15000)
            input_method = 'keyboard'
            is_on_call = 1  # ON CALL - VISHING!
            fraud_type = 'vishing_senior'
        
        elif fraud_pattern == 'location_spoof':
            # GPS spoofing / Mock location
            amount = round(np.random.uniform(8000, 20000), 2)
            merchant_num = random.randint(1, 60)
            merchant_name = merchant_names[merchant_num - 1]
            payment_source = 'qr_scan'
            
            is_malicious_link = 0
            ip_country = random.choice(['USA', 'UK', 'China'])
            gps_country = random.choice(['USA', 'UK', 'China'])
            is_rooted = 1
            is_emulator = 0
            mock_location_enabled = 1  # FAKE GPS!
            
            pin_entry_time = random.randint(1600, 2800)
            input_method = 'keyboard'
            is_on_call = 0
            fraud_type = 'location_spoof'
        
        else:  # high_amount
            amount = round(user_info['avg_amount'] * random.uniform(10, 20), 2)
            merchant_num = random.randint(51, 60)
            merchant_name = merchant_names[merchant_num - 1]
            payment_source = random.choice(['link', 'sms'])
            
            is_malicious_link = 1
            ip_country = 'India'
            gps_country = 'India'
            is_rooted = 0
            is_emulator = 0
            mock_location_enabled = 0
            
            pin_entry_time = random.randint(1800, 3000)
            input_method = 'keyboard'
            is_on_call = 0
            fraud_type = 'high_amount'
        
        is_fraud = 1
    
    # Update user stats
    user_info['transaction_count'] += 1
    
    # ========================================================================
    # CREATE TRANSACTION WITH ONLY 18 CRITICAL PARAMETERS
    # ========================================================================
    transaction = {
        # 1. Transaction ID
        'transaction_id': f'TXN{idx:04d}',
        
        # 2. User ID
        'user_id': user_id,
        
        # 3. Amount
        'amount': amount,
        
        # 4. Merchant Name
        'merchant_name': merchant_name,
        
        # 5. Timestamp
        'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        
        # 6. Hour of Day
        'hour_of_day': timestamp.hour,
        
        # 7. User Age (from KYC)
        'user_age': user_info['age'],
        
        # 8. Payment Source
        'payment_source': payment_source,
        
        # 9. Malicious Link Flag
        'is_malicious_link': is_malicious_link,
        
        # 10. IP Country
        'ip_country': ip_country,
        
        # 11. GPS Country
        'gps_country': gps_country,
        
        # 12. Rooted Device
        'is_rooted': is_rooted,
        
        # 13. Emulator Detection
        'is_emulator': is_emulator,
        
        # 14. Mock Location
        'mock_location_enabled': mock_location_enabled,
        
        # 15. PIN Entry Time
        'pin_entry_time_ms': pin_entry_time,
        
        # 16. Input Method
        'input_method': input_method,
        
        # 17. On Call Flag (VISHING)
        'is_on_call_during_transaction': is_on_call,
        
        # 18. Sender Bank
        'sender_bank': random.choice(banks),
        
        # Labels
        'is_fraud': is_fraud,
        'fraud_type': fraud_type
    }
    
    transactions.append(transaction)

# Create DataFrame
df = pd.DataFrame(transactions)
df = df.sort_values('timestamp').reset_index(drop=True)

# Save to CSV
filename = 'upi_fraud_dataset.csv'
df.to_csv(filename, index=False)

# ============================================================================
# STATISTICS
# ============================================================================
print("\n" + "="*80)
print("📊 DATASET STATISTICS")
print("="*80)
print(f"Total Transactions: {len(df)}")
print(f"Total Parameters: {len(df.columns) - 2}")  # Exclude labels
print(f"\nLegitimate: {len(df[df['is_fraud']==0])} ({len(df[df['is_fraud']==0])/len(df)*100:.1f}%)")
print(f"Fraudulent: {len(df[df['is_fraud']==1])} ({len(df[df['is_fraud']==1])/len(df)*100:.1f}%)")

print(f"\n🚨 Fraud Distribution:")
fraud_counts = df[df['is_fraud']==1]['fraud_type'].value_counts()
for fraud_type, count in fraud_counts.items():
    print(f"  • {fraud_type}: {count}")

print(f"\n👥 User Statistics:")
print(f"  • Total Users: {df['user_id'].nunique()}")
print(f"  • Senior Citizens (65+): {len(df[df['user_age'] >= 65])}")
print(f"  • Average Age: {df['user_age'].mean():.1f} years")

print(f"\n💰 Amount Statistics:")
print(f"  • Average: ₹{df['amount'].mean():.2f}")
print(f"  • Median: ₹{df['amount'].median():.2f}")
print(f"  • Max: ₹{df['amount'].max():.2f}")

print(f"\n🚨 Fraud Indicators Detected:")
print(f"  • Malicious Links: {df['is_malicious_link'].sum()}")
print(f"  • Vishing Attacks (on call): {df['is_on_call_during_transaction'].sum()}")
print(f"  • Bot Attacks (fast typing): {len(df[df['pin_entry_time_ms'] < 100])}")
print(f"  • Location Spoofing: {df['mock_location_enabled'].sum()}")
print(f"  • Rooted Devices: {df['is_rooted'].sum()}")
print(f"  • Emulators: {df['is_emulator'].sum()}")

print(f"\n📱 Payment Sources:")
for source, count in df['payment_source'].value_counts().items():
    print(f"  • {source}: {count}")

print(f"\n⌨️  Input Methods:")
for method, count in df['input_method'].value_counts().items():
    print(f"  • {method}: {count}")

print(f"\n✅ Dataset saved as '{filename}'")
print("="*80)

print("\n📋 Sample Legitimate Transactions:")
print(df[df['is_fraud']==0][['transaction_id', 'amount', 'merchant_name', 'user_age', 'payment_source']].head(5).to_string(index=False))

print("\n🚨 Sample Fraudulent Transactions:")
fraud_df = df[df['is_fraud']==1][['transaction_id', 'amount', 'merchant_name', 'fraud_type', 'is_malicious_link', 'is_on_call_during_transaction']]
print(fraud_df.to_string(index=False))

print("\n" + "="*80)
print("✅ FOCUSED DATASET GENERATION COMPLETE!")
print("="*80)
print("\n💡 This dataset contains ONLY parameters that:")
print("   1. UPI backend can actually capture")
print("   2. Are critical for fraud detection")
print("   3. Support all your enhanced features")
print("   4. Are realistic and implementable")
print("="*80)