from fastapi import FastAPI, BackgroundTasks
from .river_engine import RiverAdaptiveEngine
from .database import SessionLocal 
from .Stages import source_impl_1, location_impl_2, device_impl_5 
from .explain_engine import UPIDecisionExplainer # NEW: Import Explainer
from sqlalchemy import text 
import httpx 
import datetime

app = FastAPI(title="UPIRakshak 7-Layer Backend")
engine = RiverAdaptiveEngine()
explainer = UPIDecisionExplainer(engine) # NEW: Initialize LIME Explainer

@app.post("/verify")
async def verify_transaction(tx: dict, background_tasks: BackgroundTasks):
    amount = float(tx.get('amount', 0))
    river_risk = engine.get_risk_score(tx)
    
    # Header log for the jury
    print(f"\n--- TRANSACTION LOG: {datetime.datetime.now().strftime('%H:%M:%S')} ---")
    print(f"Initial River Risk Assessment: {river_risk:.4f} for ₹{amount}")

    # --- FIX 1: HIGH-AMOUNT FRAUD GUARD ---
    if amount > 50000:
        print(f"🚩 High-value transaction (₹{amount}) detected. Forcing Deep Shield.")
        river_risk = max(river_risk, 0.55) 

    # --- FIX 2: SMALL-AMOUNT LENIENCY ---
    if amount < 500 and river_risk < 0.45:
        print(f"✅ FAST PATH: Small normal transaction approved (₹{amount}).")
        background_tasks.add_task(engine.learn_one, tx, 0) 
        return {"decision": "ALLOW", "confidence": 1 - river_risk, "path": "FAST"}

    # SEQUENTIAL EARLY TERMINATION
    if river_risk < 0.20:
        print("✅ FAST PATH: Normal behavior detected. Auto-Approving.")
        background_tasks.add_task(engine.learn_one, tx, 0) 
        return {"decision": "ALLOW", "confidence": 1 - river_risk, "path": "FAST"}

    # --- 7-LAYER DEEP ANALYSIS ---
    print("⚠️ DEEP SHIELD TRIGGERED: Escalating to Multi-Layer Analysis...")
    
    s1 = source_impl_1.check_source(tx) # Layer 1
    s2 = location_impl_2.check_location(tx) # Layer 2
    s5 = device_impl_5.check_device(tx) # Layer 5
    
    # Aggregate deep risk score
    final_avg_risk = (s1 + s2 + s5 + river_risk) / 4
    
    print(f"L1: {s1} | L2: {s2} | L5: {s5} | ML: {river_risk:.2f}")
    print(f"Final 7-Layer Risk: {final_avg_risk:.4f}")

    # Decision Thresholds
    decision = "BLOCK" if final_avg_risk > 0.50 else "WARN" if final_avg_risk > 0.35 else "ALLOW"
    
    # --- NEW: LIME XAI EXPLANATION LOGGING ---
    reason = ""
    if decision != "ALLOW":
        reason = explainer.explain(tx) # Generates the "Why"
        print(f"🔍 XAI EXPLANATION: {reason}") # Matches terminal photo
    
    print(f"DECISION: {decision}")
    
    return {
        "decision": decision, 
        "risk_score": final_avg_risk, 
        "reason": reason, # Send this back to your Flutter app
        "path": "DEEP"
    }

@app.post("/feedback")
async def process_feedback(feedback: dict):
    if 'tx' not in feedback:
        return {"error": "Missing 'tx' key"}

    transaction_data = feedback['tx']
    is_fraud = feedback.get('is_fraud', 0)

    # 1. Update River ML Model
    engine.learn_one(transaction_data, is_fraud)

    # 2. Update ML Research Database (PostgreSQL)
    try:
        db = SessionLocal()
        query = text("""
            INSERT INTO upi_dataset (user_id, amount, is_fraud, risk_score, timestamp) 
            VALUES (:u, :a, :f, :r, :t)
        """)
        db.execute(query, {
            "u": transaction_data.get('user_id'),
            "a": transaction_data.get('amount'),
            "f": is_fraud,
            "r": engine.get_risk_score(transaction_data),
            "t": datetime.datetime.now()
        })
        db.commit()
        db.close()
        print("✅ ML Database Update: SUCCESS")
    except Exception as e: 
        print(f"❌ ML Database Log Failed: {e}")

    # 3. Notify NPCI Central Portal (bank.py)
    status_for_bank = "BLOCKED" if is_fraud == 1 else "SUCCESS"
    
    async with httpx.AsyncClient() as client:
        try:
            await client.post("http://127.0.0.1:5000/api/pay", json={
                "sender": transaction_data.get('user_id'),
                "receiver": transaction_data.get('merchant_name'),
                "amount": transaction_data.get('amount'),
                "status": status_for_bank 
            })
            print(f"✅ NPCI Portal Updated with Status: {status_for_bank}")
        except Exception as e: 
            print(f"❌ NPCI Sync Error: {e}")

    return {"status": "Complete", "drift": engine.drifter.drift_detected}