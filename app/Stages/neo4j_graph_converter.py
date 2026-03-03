"""
UPI FRAUD DETECTION - GRAPH DATABASE CONVERTER
Converts CSV dataset into Neo4j Graph Database
Optimized for GNN-based fraud detection
Author: [Your Team Name]
"""

import pandas as pd
from neo4j import GraphDatabase
import json
from datetime import datetime
import numpy as np

# ============================================================================
# NEO4J GRAPH BUILDER
# ============================================================================

class UPIFraudGraphBuilder:
    """
    Converts UPI transaction data into Neo4j graph structure
    
    Graph Schema:
    - Nodes: User, Transaction, Merchant, Device, Location, Bank
    - Relationships: MADE, PAID_TO, USED_DEVICE, FROM_LOCATION, etc.
    """
    
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password"):
        """
        Initialize Neo4j connection
        
        Args:
            uri: Neo4j database URI
            user: Username
            password: Password
        """
        print("🔌 Connecting to Neo4j...")
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            # Test connection
            with self.driver.session() as session:
                result = session.run("RETURN 1")
                result.single()
            print("✅ Connected to Neo4j successfully!")
        except Exception as e:
            print(f"❌ Failed to connect to Neo4j: {e}")
            print("\n💡 Make sure Neo4j is running!")
            print("   Quick start: docker run -p 7474:7474 -p 7687:7687 neo4j")
            raise
    
    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
            print("🔌 Neo4j connection closed")
    
    def clear_database(self):
        """Clear all existing data (use with caution!)"""
        print("🗑️  Clearing existing database...")
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        print("✅ Database cleared")
    
    def create_constraints_and_indexes(self):
        """Create uniqueness constraints and indexes for performance"""
        print("📋 Creating constraints and indexes...")
        
        constraints = [
            "CREATE CONSTRAINT user_id_unique IF NOT EXISTS FOR (u:User) REQUIRE u.user_id IS UNIQUE",
            "CREATE CONSTRAINT transaction_id_unique IF NOT EXISTS FOR (t:Transaction) REQUIRE t.transaction_id IS UNIQUE",
            "CREATE CONSTRAINT merchant_name_unique IF NOT EXISTS FOR (m:Merchant) REQUIRE m.name IS UNIQUE",
            "CREATE CONSTRAINT device_id_unique IF NOT EXISTS FOR (d:Device) REQUIRE d.device_id IS UNIQUE",
            "CREATE CONSTRAINT bank_name_unique IF NOT EXISTS FOR (b:Bank) REQUIRE b.name IS UNIQUE"
        ]
        
        indexes = [
            "CREATE INDEX user_age_idx IF NOT EXISTS FOR (u:User) ON (u.age)",
            "CREATE INDEX transaction_amount_idx IF NOT EXISTS FOR (t:Transaction) ON (t.amount)",
            "CREATE INDEX transaction_timestamp_idx IF NOT EXISTS FOR (t:Transaction) ON (t.timestamp)",
            "CREATE INDEX transaction_fraud_idx IF NOT EXISTS FOR (t:Transaction) ON (t.is_fraud)",
            "CREATE INDEX merchant_suspicious_idx IF NOT EXISTS FOR (m:Merchant) ON (m.is_suspicious)"
        ]
        
        with self.driver.session() as session:
            for constraint in constraints:
                try:
                    session.run(constraint)
                except:
                    pass  # Constraint might already exist
            
            for index in indexes:
                try:
                    session.run(index)
                except:
                    pass  # Index might already exist
        
        print("✅ Constraints and indexes created")
    
    def load_csv_data(self, csv_file):
        """Load CSV data"""
        print(f"📂 Loading data from {csv_file}...")
        self.df = pd.read_csv(csv_file)
        print(f"✅ Loaded {len(self.df)} transactions")
        return self.df
    
    def create_users(self):
        """Create User nodes"""
        print("\n👥 Creating User nodes...")
        
        # Get unique users with their attributes
        users = self.df.groupby('user_id').agg({
            'user_age': 'first',
            'amount': ['mean', 'sum', 'count'],
            'is_fraud': 'sum'
        }).reset_index()
        
        users.columns = ['user_id', 'age', 'avg_amount', 'total_amount', 'transaction_count', 'fraud_count']
        
        query = """
        UNWIND $users AS user
        CREATE (u:User {
            user_id: user.user_id,
            age: user.age,
            is_senior: user.age >= 65,
            age_group: CASE 
                WHEN user.age < 30 THEN 'young'
                WHEN user.age < 50 THEN 'middle'
                WHEN user.age < 65 THEN 'mature'
                ELSE 'senior'
            END,
            avg_transaction_amount: user.avg_amount,
            total_transaction_amount: user.total_amount,
            transaction_count: user.transaction_count,
            fraud_count: user.fraud_count,
            fraud_rate: CASE 
                WHEN user.transaction_count > 0 
                THEN toFloat(user.fraud_count) / user.transaction_count 
                ELSE 0.0 
            END,
            risk_level: CASE 
                WHEN user.fraud_count > 0 THEN 'high'
                WHEN user.age >= 65 THEN 'medium'
                ELSE 'low'
            END
        })
        """
        
        with self.driver.session() as session:
            session.run(query, users=users.to_dict('records'))
        
        print(f"✅ Created {len(users)} User nodes")
    
    def create_merchants(self):
        """Create Merchant nodes"""
        print("\n🏪 Creating Merchant nodes...")
        
        # Suspicious merchant keywords
        suspicious_keywords = ['lottery', 'prize', 'kyc', 'police', 'tax', 'refund', 
                              'cash', 'support', 'winner', 'update']
        
        merchants = self.df.groupby('merchant_name').agg({
            'amount': ['mean', 'sum', 'count'],
            'is_fraud': 'sum'
        }).reset_index()
        
        merchants.columns = ['name', 'avg_amount', 'total_amount', 'transaction_count', 'fraud_count']
        
        # Determine if merchant is suspicious
        merchants['is_suspicious'] = merchants['name'].apply(
            lambda x: any(keyword in x.lower() for keyword in suspicious_keywords)
        )
        merchants['fraud_rate'] = merchants['fraud_count'] / merchants['transaction_count']
        
        query = """
        UNWIND $merchants AS merchant
        CREATE (m:Merchant {
            name: merchant.name,
            avg_transaction_amount: merchant.avg_amount,
            total_transaction_amount: merchant.total_amount,
            transaction_count: merchant.transaction_count,
            fraud_count: merchant.fraud_count,
            fraud_rate: merchant.fraud_rate,
            is_suspicious: merchant.is_suspicious,
            risk_level: CASE 
                WHEN merchant.fraud_rate > 0.5 THEN 'critical'
                WHEN merchant.fraud_rate > 0.2 THEN 'high'
                WHEN merchant.is_suspicious THEN 'medium'
                ELSE 'low'
            END
        })
        """
        
        with self.driver.session() as session:
            session.run(query, merchants=merchants.to_dict('records'))
        
        print(f"✅ Created {len(merchants)} Merchant nodes")
        print(f"   🚨 Suspicious merchants: {merchants['is_suspicious'].sum()}")
    
    def create_banks(self):
        """Create Bank nodes"""
        print("\n🏦 Creating Bank nodes...")
        
        banks = self.df.groupby('sender_bank').agg({
            'amount': ['sum', 'count'],
            'is_fraud': 'sum'
        }).reset_index()
        
        banks.columns = ['name', 'total_amount', 'transaction_count', 'fraud_count']
        banks['fraud_rate'] = banks['fraud_count'] / banks['transaction_count']
        
        query = """
        UNWIND $banks AS bank
        CREATE (b:Bank {
            name: bank.name,
            total_transaction_amount: bank.total_amount,
            transaction_count: bank.transaction_count,
            fraud_count: bank.fraud_count,
            fraud_rate: bank.fraud_rate
        })
        """
        
        with self.driver.session() as session:
            session.run(query, banks=banks.to_dict('records'))
        
        print(f"✅ Created {len(banks)} Bank nodes")
    
    def create_devices(self):
        """Create Device nodes (synthetic based on user + security flags)"""
        print("\n📱 Creating Device nodes...")
        
        # Generate device IDs based on user + security characteristics
        devices_data = []
        for _, row in self.df.iterrows():
            device_id = f"device_{row['user_id']}_{row['is_rooted']}_{row['is_emulator']}"
            devices_data.append({
                'device_id': device_id,
                'is_rooted': row['is_rooted'],
                'is_emulator': row['is_emulator'],
                'mock_location_enabled': row['mock_location_enabled'],
                'user_id': row['user_id']
            })
        
        devices_df = pd.DataFrame(devices_data)
        devices = devices_df.groupby('device_id').agg({
            'is_rooted': 'max',
            'is_emulator': 'max',
            'mock_location_enabled': 'max',
            'user_id': 'first'
        }).reset_index()
        
        devices['risk_score'] = (
            devices['is_rooted'] * 0.4 + 
            devices['is_emulator'] * 0.4 + 
            devices['mock_location_enabled'] * 0.2
        )
        
        query = """
        UNWIND $devices AS device
        CREATE (d:Device {
            device_id: device.device_id,
            is_rooted: device.is_rooted = 1,
            is_emulator: device.is_emulator = 1,
            mock_location_enabled: device.mock_location_enabled = 1,
            risk_score: device.risk_score,
            is_compromised: device.is_rooted = 1 OR device.is_emulator = 1,
            trust_level: CASE 
                WHEN device.risk_score >= 0.6 THEN 'untrusted'
                WHEN device.risk_score >= 0.3 THEN 'suspicious'
                ELSE 'trusted'
            END
        })
        """
        
        with self.driver.session() as session:
            session.run(query, devices=devices.to_dict('records'))
        
        print(f"✅ Created {len(devices)} Device nodes")
        print(f"   🚨 Compromised devices: {(devices['risk_score'] >= 0.6).sum()}")
    
    def create_locations(self):
        """Create Location nodes"""
        print("\n📍 Creating Location nodes...")
        
        # Create unique location combinations
        locations = self.df.groupby(['ip_country', 'gps_country']).agg({
            'is_fraud': ['sum', 'count']
        }).reset_index()
        
        locations.columns = ['ip_country', 'gps_country', 'fraud_count', 'transaction_count']
        locations['location_id'] = locations['ip_country'] + '_' + locations['gps_country']
        locations['is_mismatch'] = locations['ip_country'] != locations['gps_country']
        locations['fraud_rate'] = locations['fraud_count'] / locations['transaction_count']
        
        query = """
        UNWIND $locations AS loc
        CREATE (l:Location {
            location_id: loc.location_id,
            ip_country: loc.ip_country,
            gps_country: loc.gps_country,
            is_mismatch: loc.is_mismatch,
            fraud_count: loc.fraud_count,
            transaction_count: loc.transaction_count,
            fraud_rate: loc.fraud_rate,
            is_foreign: loc.ip_country <> 'India' OR loc.gps_country <> 'India',
            risk_level: CASE 
                WHEN loc.is_mismatch THEN 'high'
                WHEN loc.ip_country <> 'India' THEN 'medium'
                ELSE 'low'
            END
        })
        """
        
        with self.driver.session() as session:
            session.run(query, locations=locations.to_dict('records'))
        
        print(f"✅ Created {len(locations)} Location nodes")
        print(f"   🚨 Location mismatches: {locations['is_mismatch'].sum()}")
    
    def create_transactions(self):
        """Create Transaction nodes with all attributes"""
        print("\n💳 Creating Transaction nodes...")
        
        # Prepare transaction data
        transactions = self.df.copy()
        transactions['device_id'] = transactions.apply(
            lambda x: f"device_{x['user_id']}_{x['is_rooted']}_{x['is_emulator']}", 
            axis=1
        )
        transactions['location_id'] = transactions['ip_country'] + '_' + transactions['gps_country']
        
        # Calculate risk scores for each transaction
        transactions['typing_anomaly_score'] = transactions['pin_entry_time_ms'].apply(
            lambda x: 1.0 if x < 100 else (0.8 if x > 8000 else 0.0)
        )
        
        query = """
        UNWIND $transactions AS txn
CREATE (t:Transaction {
    transaction_id: txn.transaction_id,
    amount: txn.amount,
    timestamp: datetime(replace(txn.timestamp, ' ', 'T')),
    hour_of_day: txn.hour_of_day,
    payment_source: txn.payment_source,
    is_malicious_link: txn.is_malicious_link = 1,
    pin_entry_time_ms: txn.pin_entry_time_ms,
    input_method: txn.input_method,
    is_on_call: txn.is_on_call_during_transaction = 1,
    is_fraud: txn.is_fraud = 1,
    fraud_type: txn.fraud_type,
    typing_anomaly_score: txn.typing_anomaly_score,
    is_night_transaction: txn.hour_of_day >= 22 OR txn.hour_of_day <= 5,
    is_high_amount: txn.amount > 10000,

    risk_indicators:
        (CASE WHEN txn.is_malicious_link = 1 THEN ['malicious_link'] ELSE [] END) +
        (CASE WHEN txn.is_on_call_during_transaction = 1 THEN ['on_call'] ELSE [] END) +
        (CASE WHEN txn.pin_entry_time_ms < 100 THEN ['bot_typing'] ELSE [] END) +
        (CASE WHEN txn.pin_entry_time_ms > 8000 THEN ['slow_typing'] ELSE [] END) +
        (CASE WHEN txn.input_method <> 'keyboard' THEN ['suspicious_input'] ELSE [] END)
})

        """
        
        batch_size = 100
        total_batches = (len(transactions) + batch_size - 1) // batch_size
        
        with self.driver.session() as session:
            for i in range(0, len(transactions), batch_size):
                batch = transactions[i:i+batch_size]
                session.run(query, transactions=batch.to_dict('records'))
                print(f"   Progress: {min(i+batch_size, len(transactions))}/{len(transactions)} transactions", end='\r')
        
        print(f"\n✅ Created {len(transactions)} Transaction nodes")
    
    def create_relationships(self):
        """Create all relationships between nodes"""
        print("\n🔗 Creating relationships...")
        
        relationships = [
            # User -> Transaction (MADE)
            {
                'name': 'MADE',
                'query': """
                MATCH (u:User), (t:Transaction)
                WHERE u.user_id = substring(t.transaction_id, 3, 4)
                CREATE (u)-[:MADE {
                    timestamp: t.timestamp,
                    amount: t.amount
                }]->(t)
                """
            },
            # User -> Bank (BANKS_WITH)
            {
                'name': 'BANKS_WITH',
                'query': """
                MATCH (u:User), (b:Bank)
                WHERE u.user_id IN [txn IN [(u)-[:MADE]->(t:Transaction) | t][0..1] | txn.transaction_id[4..7]]
                WITH u, b
                MATCH (u)-[:MADE]->(t:Transaction)
                WITH u, b, COUNT(t) as txn_count
                WHERE txn_count > 0
                MERGE (u)-[:BANKS_WITH {
                    transaction_count: txn_count
                }]->(b)
                """
            },
            # Transaction -> Merchant (PAID_TO)
            {
                'name': 'PAID_TO',
                'query': """
                UNWIND $data AS row
                MATCH (t:Transaction {transaction_id: row.transaction_id})
                MATCH (m:Merchant {name: row.merchant_name})
                CREATE (t)-[:PAID_TO {
                    amount: row.amount,
                    timestamp: datetime(replace(row.timestamp, ' ', 'T'))
                }]->(m)
                """
            },
            # Transaction -> Device (USED_DEVICE)
            {
                'name': 'USED_DEVICE',
                'query': """
                UNWIND $data AS row
                MATCH (t:Transaction {transaction_id: row.transaction_id})
                MATCH (d:Device {device_id: row.device_id})
                CREATE (t)-[:USED_DEVICE]->(d)
                """
            },
            # Transaction -> Location (FROM_LOCATION)
            {
                'name': 'FROM_LOCATION',
                'query': """
                UNWIND $data AS row
                MATCH (t:Transaction {transaction_id: row.transaction_id})
                MATCH (l:Location {location_id: row.location_id})
                CREATE (t)-[:FROM_LOCATION]->(l)
                """
            },
            # User -> Device (OWNS)
            {
                'name': 'OWNS',
                'query': """
                MATCH (u:User)-[:MADE]->(t:Transaction)-[:USED_DEVICE]->(d:Device)
                WITH u, d, COUNT(t) as usage_count
                CREATE (u)-[:OWNS {
                    usage_count: usage_count
                }]->(d)
                """
            }
        ]
        
        # Prepare data for relationships that need it
        rel_data = self.df.copy()
        rel_data['device_id'] = rel_data.apply(
            lambda x: f"device_{x['user_id']}_{x['is_rooted']}_{x['is_emulator']}", 
            axis=1
        )
        rel_data['location_id'] = rel_data['ip_country'] + '_' + rel_data['gps_country']
        
        with self.driver.session() as session:
            for rel in relationships:
                print(f"   Creating {rel['name']} relationships...")
                try:
                    if '$data' in rel['query']:
                        session.run(rel['query'], data=rel_data.to_dict('records'))
                    else:
                        session.run(rel['query'])
                except Exception as e:
                    print(f"   ⚠️  Error creating {rel['name']}: {e}")
        
        print("✅ All relationships created")
    
    def create_fraud_pattern_relationships(self):
        """Create additional relationships for fraud pattern detection"""
        print("\n🔍 Creating fraud pattern relationships...")
        
        patterns = [
            # Fraud ring detection: Users using same device
            {
                'name': 'SHARES_DEVICE_WITH',
                'query': """
                MATCH (u1:User)-[:OWNS]->(d:Device)<-[:OWNS]-(u2:User)
                WHERE u1.user_id < u2.user_id
                CREATE (u1)-[:SHARES_DEVICE_WITH {
                    device_id: d.device_id,
                    risk_level: d.trust_level
                }]->(u2)
                """
            },
            # Same merchant fraud pattern
            {
                'name': 'COMMON_MERCHANT',
                'query': """
                MATCH (u1:User)-[:MADE]->(t1:Transaction)-[:PAID_TO]->(m:Merchant)<-[:PAID_TO]-(t2:Transaction)<-[:MADE]-(u2:User)
                WHERE u1.user_id < u2.user_id AND m.is_suspicious = true
                WITH u1, u2, m, COUNT(*) as txn_count
                WHERE txn_count >= 2
                CREATE (u1)-[:COMMON_MERCHANT {
                    merchant: m.name,
                    transaction_count: txn_count
                }]->(u2)
                """
            },
            # Sequential fraud (transactions within 5 minutes)
            {
                'name': 'FOLLOWED_BY',
                'query': """
                MATCH (t1:Transaction), (t2:Transaction)
                WHERE t1.timestamp < t2.timestamp 
                  AND duration.between(t1.timestamp, t2.timestamp).minutes < 5
                  AND (t1.is_fraud = true OR t2.is_fraud = true)
                CREATE (t1)-[:FOLLOWED_BY {
                    time_diff_minutes: duration.between(t1.timestamp, t2.timestamp).minutes
                }]->(t2)
                """
            }
        ]
        
        with self.driver.session() as session:
            for pattern in patterns:
                try:
                    print(f"   Creating {pattern['name']} pattern...")
                    session.run(pattern['query'])
                except Exception as e:
                    print(f"   ⚠️  Error: {e}")
        
        print("✅ Fraud pattern relationships created")
    
    def get_statistics(self):
        """Get database statistics"""
        print("\n📊 Database Statistics:")
        print("="*70)
        
        queries = {
            "Total Nodes": "MATCH (n) RETURN count(n) as count",
            "Total Relationships": "MATCH ()-[r]->() RETURN count(r) as count",
            "Users": "MATCH (u:User) RETURN count(u) as count",
            "Transactions": "MATCH (t:Transaction) RETURN count(t) as count",
            "Merchants": "MATCH (m:Merchant) RETURN count(m) as count",
            "Devices": "MATCH (d:Device) RETURN count(d) as count",
            "Locations": "MATCH (l:Location) RETURN count(l) as count",
            "Banks": "MATCH (b:Bank) RETURN count(b) as count",
            "Fraudulent Transactions": "MATCH (t:Transaction {is_fraud: true}) RETURN count(t) as count",
            "Suspicious Merchants": "MATCH (m:Merchant {is_suspicious: true}) RETURN count(m) as count",
            "Compromised Devices": "MATCH (d:Device) WHERE d.risk_score >= 0.6 RETURN count(d) as count",
            "High-Risk Users": "MATCH (u:User {risk_level: 'high'}) RETURN count(u) as count"
        }
        
        with self.driver.session() as session:
            for name, query in queries.items():
                result = session.run(query)
                count = result.single()['count']
                print(f"   {name}: {count}")
        
        print("="*70)
    
    def build_complete_graph(self, csv_file, clear_existing=True):
        """
        Complete pipeline to build graph from CSV
        
        Args:
            csv_file: Path to CSV file
            clear_existing: Whether to clear existing data
        """
        print("\n" + "="*70)
        print("🚀 BUILDING UPI FRAUD DETECTION GRAPH DATABASE")
        print("="*70)
        
        # Load data
        self.load_csv_data(csv_file)
        
        # Clear if requested
        if clear_existing:
            self.clear_database()
        
        # Create constraints
        self.create_constraints_and_indexes()
        
        # Create nodes
        self.create_users()
        self.create_merchants()
        self.create_banks()
        self.create_devices()
        self.create_locations()
        self.create_transactions()
        
        # Create relationships
        self.create_relationships()
        self.create_fraud_pattern_relationships()
        
        # Show statistics
        self.get_statistics()
        
        print("\n" + "="*70)
        print("✅ GRAPH DATABASE BUILD COMPLETE!")
        print("="*70)
        print("\n💡 Access Neo4j Browser at: http://localhost:7474")
        print("   Username: neo4j")
        print("   Password: password (or your custom password)")
        print("\n🔍 Try these Cypher queries:")
        print("   1. MATCH (n) RETURN n LIMIT 50")
        print("   2. MATCH (u:User)-[:MADE]->(t:Transaction {is_fraud: true}) RETURN u, t LIMIT 10")
        print("   3. MATCH (m:Merchant {is_suspicious: true})<-[:PAID_TO]-(t:Transaction) RETURN m, t")
        print("="*70)


# ============================================================================
# EXAMPLE CYPHER QUERIES FOR GNN TRAINING
# ============================================================================

def save_example_queries():
    """Save example Cypher queries to file"""
    queries = """
# ============================================================================
# USEFUL CYPHER QUERIES FOR GNN-BASED FRAUD DETECTION
# ============================================================================

# 1. Get all fraud transactions with context
MATCH (u:User)-[:MADE]->(t:Transaction {is_fraud: true})-[:PAID_TO]->(m:Merchant)
MATCH (t)-[:USED_DEVICE]->(d:Device)
MATCH (t)-[:FROM_LOCATION]->(l:Location)
RETURN u, t, m, d, l
LIMIT 20;

# 2. Find fraud rings (users sharing devices)
MATCH (u1:User)-[:SHARES_DEVICE_WITH]->(u2:User)
MATCH (u1)-[:MADE]->(t1:Transaction {is_fraud: true})
MATCH (u2)-[:MADE]->(t2:Transaction {is_fraud: true})
RETURN u1, u2, t1, t2;

# 3. High-risk senior citizens
MATCH (u:User {is_senior: true})-[:MADE]->(t:Transaction)
WHERE t.is_fraud = true OR t.is_on_call = true
RETURN u, t
ORDER BY t.amount DESC;

# 4. Suspicious merchant network
MATCH (m:Merchant {is_suspicious: true})<-[:PAID_TO]-(t:Transaction)-[:USED_DEVICE]->(d:Device)
WHERE d.is_compromised = true
RETURN m, t, d;

# 5. Location mismatch fraud
MATCH (t:Transaction)-[:FROM_LOCATION]->(l:Location {is_mismatch: true})
WHERE t.is_fraud = true
RETURN t, l;

# 6. Export graph data for GNN training
MATCH (u:User)-[:MADE]->(t:Transaction)-[:PAID_TO]->(m:Merchant)
MATCH (t)-[:USED_DEVICE]->(d:Device)
MATCH (t)-[:FROM_LOCATION]->(l:Location)
RETURN 
    u.user_id, u.age, u.fraud_rate,
    t.transaction_id, t.amount, t.is_fraud, t.fraud_type,
    m.name, m.is_suspicious,
    d.device_id, d.is_rooted, d.is_emulator,
    l.ip_country, l.gps_country, l.is_mismatch
LIMIT 1000;

# 7. Calculate graph features for ML
MATCH (u:User)
OPTIONAL MATCH (u)-[:MADE]->(t:Transaction {is_fraud: true})
WITH u, count(t) as fraud_count
OPTIONAL MATCH (u)-[:MADE]->(all_t:Transaction)
RETURN 
    u.user_id,
    u.age,
    count(all_t) as total_transactions,
    fraud_count,
    toFloat(fraud_count) / count(all_t) as fraud_rate;

# 8. Find temporal fraud patterns
MATCH (t1:Transaction)-[:FOLLOWED_BY*1..3]->(t2:Transaction)
WHERE t1.is_fraud = true AND t2.is_fraud = true
RETURN t1, t2;
"""
    
    with open('neo4j_example_queries.cypher', 'w') as f:
        f.write(queries)
    print("\n💾 Saved example queries to 'neo4j_example_queries.cypher'")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Configuration
    CSV_FILE = 'upi_fraud_dataset.csv'
    NEO4J_URI = "bolt://localhost:7687"
    NEO4J_USER = "neo4j"
    NEO4J_PASSWORD = "password123"  # Change this to your Neo4j password
    
    try:
        # Initialize graph builder
        builder = UPIFraudGraphBuilder(
            uri=NEO4J_URI,
            user=NEO4J_USER,
            password=NEO4J_PASSWORD
        )
        
        # Build complete graph
        builder.build_complete_graph(
            csv_file=CSV_FILE,
            clear_existing=True  # Set to False to append to existing data
        )
        
        # Save example queries
        save_example_queries()
        
        # Close connection
        builder.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Make sure Neo4j is running")
        print("   2. Check your connection details (URI, username, password)")
        print("   3. Install neo4j driver: pip install neo4j")
        print("   4. Start Neo4j: docker run -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j")