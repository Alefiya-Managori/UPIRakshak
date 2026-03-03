import psycopg2
import datetime
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- CONFIGURATION ---
DB_HOST = "localhost"
DB_NAME = "bank_central"
DB_USER = "postgres"
DB_PASS = "hajra" 
FRAUD_ENGINE_URL = "http://localhost:8000/feedback" 

def get_db_connection():
    return psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)

# --- UNIFIED DATABASE SETUP ---
def init_db():
    try:
        conn = get_db_connection(); c = conn.cursor()
        # Account Table
        c.execute('''CREATE TABLE IF NOT EXISTS npci_accounts 
                     (upi_id TEXT PRIMARY KEY, name TEXT, balance REAL, bank_name TEXT)''')
        
        # Transaction Ledger
        c.execute('''CREATE TABLE IF NOT EXISTS transactions 
                     (id SERIAL PRIMARY KEY, sender TEXT, receiver TEXT, 
                      amount REAL, timestamp TEXT, status TEXT)''')
        
        c.execute("SELECT count(*) FROM npci_accounts")
        if c.fetchone()[0] == 0:
            # Seed data
            c.execute("INSERT INTO npci_accounts VALUES (%s, %s, %s, %s)", ('user@upi', 'Jury Demo User', 50000.0, 'NPCI'))
            c.execute("INSERT INTO npci_accounts VALUES (%s, %s, %s, %s)", ('raj@hdfc', 'Raj (HDFC)', 8000.0, 'HDFC'))
            c.execute("INSERT INTO npci_accounts VALUES (%s, %s, %s, %s)", ('store@merchant', 'Central Mart', 2000.0, 'NPCI'))
        
        conn.commit(); c.close(); conn.close()
        print("✅ NPCI Central Portal Initialized")
    except Exception as e: print(f"❌ DB Error: {e}")

init_db()

# --- UNIFIED NPCI DASHBOARD ---
@app.route('/')
def npci_dashboard():
    conn = get_db_connection(); c = conn.cursor()
    c.execute("SELECT * FROM npci_accounts"); accounts = c.fetchall()
    c.execute("SELECT * FROM transactions ORDER BY id DESC"); txns = c.fetchall()
    conn.close()

    acc_html = "".join([f"""
        <div style="background:white; padding:15px; border-radius:10px; width:220px; color:black; border-left: 5px solid #2563eb;">
            <h4 style="margin:0; color:#1e40af">{a[1]}</h4>
            <p style="font-size:1.4rem; font-weight:bold; margin:5px 0;">₹{a[2]}</p>
            <small style="color:gray">{a[0]} ({a[3]})</small>
        </div>""" for a in accounts])

    txn_rows = "".join([f"""
        <tr>
            <td style="padding:10px; border-bottom:1px solid #eee">{t[4]}</td>
            <td>{t[1]}</td><td>{t[2]}</td>
            <td style="font-weight:bold">₹{t[3]}</td>
            <td style="color:{'green' if t[5]=='SUCCESS' else 'red'}">{t[5]}</td>
        </tr>""" for t in txns])

    return f"""
    <!DOCTYPE html>
    <html><head><title>NPCI Portal</title><meta http-equiv="refresh" content="2">
    <style>body {{ font-family: sans-serif; background: #f8fafc; padding: 30px; }}
    table {{ width:100%; background:white; border-radius:10px; overflow:hidden; border-collapse:collapse; box-shadow:0 4px 6px -1px rgb(0 0 0 / 0.1); }}
    th {{ background:#1e40af; color:white; padding:12px; text-align:left; }} td {{ padding:12px; }}</style></head>
    <body>
        <h1 style="color:#1e40af">🏦 NPCI Central Payment Gateway</h1>
        <div style="display:flex; gap:20px; margin-bottom:30px;">{acc_html}</div>
        <table><tr><th>Time</th><th>Sender</th><th>Receiver</th><th>Amount</th><th>Status</th></tr>{txn_rows}</table>
    </body></html>"""

@app.route('/api/pay', methods=['POST'])
def process_payment():
    data = request.json
    sender = data.get('sender')
    receiver = data.get('receiver')
    amount = float(data.get('amount'))
    
    # FIX 1: Capture the status verdict from main.py
    status = data.get('status', 'SUCCESS') 
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")

    conn = get_db_connection(); c = conn.cursor()
    
    # Check balance
    c.execute("SELECT balance FROM npci_accounts WHERE upi_id=%s", (sender,))
    row = c.fetchone()

    if not row:
        status = "FAILED (User Not Found)"
    elif row[0] < amount:
        status = "FAILED (Low Balance)"
    
    # FIX 2: Only move money if status is NOT 'BLOCKED'
    if status == "SUCCESS":
        c.execute("UPDATE npci_accounts SET balance = balance - %s WHERE upi_id = %s", (amount, sender))
        c.execute("UPDATE npci_accounts SET balance = balance + %s WHERE upi_id = %s", (amount, receiver))
    
    # Record in ledger (Fixes the 'None' display)
    c.execute("INSERT INTO transactions (sender, receiver, amount, timestamp, status) VALUES (%s,%s,%s,%s,%s)", 
              (sender, receiver, amount, timestamp, status))
    
    conn.commit(); c.close(); conn.close()
    return jsonify({"status": status.lower()}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)