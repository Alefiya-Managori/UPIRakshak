
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
