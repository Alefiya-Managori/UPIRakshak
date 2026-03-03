import csv
import os
from .river_engine import RiverAdaptiveEngine
from .database import engine as db_engine, Base  # Import standardized DB tools

def preload_model():
    print("🚀 Starting UPIRakshak Cold Start...")
    
    # 1. Initialize Database Tables
    # Automatically creates 'transactions' table in upirakshak_db
    print("📂 Initializing database tables...")
    Base.metadata.create_all(bind=db_engine)
    
    # 2. Initialize River Engine
    engine = RiverAdaptiveEngine()
    csv_path = 'data/upi_fraud_dataset.csv'
    
    if not os.path.exists(csv_path):
        print(f"❌ Error: {csv_path} not found. Ensure the file is in the data/ folder.")
        return

    print("🧠 Warming up the ML Engine (Filtering non-numeric data)...")
    
    try:
        with open(csv_path, mode='r') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                # A. Extract the ground truth label
                is_fraud = int(row.pop('is_fraud')) 
                
                # B. Create a numeric-only dictionary for the ML model
                # This prevents crashes caused by strings like 'HDFC' or 'Merchant_Name'
                numeric_txn = {}
                for k, v in row.items():
                    try:
                        numeric_txn[k] = float(v)
                    except ValueError:
                        # Skip text-based columns that River's MinMaxScaler can't process
                        continue 
                
                # C. Train the model only with numeric features
                engine.learn_one(numeric_txn, is_fraud)
                
                count += 1
                if count % 1000 == 0:
                    print(f"   Processed {count} rows...")

        print(f"✅ Successfully processed {count} transactions.")
        print("✅ System Warmed Up: River is ready for the live demo!")
        
    except Exception as e:
        print(f"❌ Cold Start Failed: {e}")

if __name__ == "__main__":
    preload_model()