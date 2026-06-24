"""
Load CSVs into PostgreSQL using native COPY
=============================================
Uses PostgreSQL's COPY command via psycopg2 instead of row-by-row
or multi-row INSERT statements. Faster, and avoids parameter-binding
edge cases entirely — COPY streams the file directly.
"""

import psycopg2
import os

# ── UPDATE THESE WITH YOUR POSTGRES CREDENTIALS ──
DB_USER     = "postgres"
DB_PASSWORD = "Mandy@3112"   # raw password here, NOT url-encoded
DB_HOST     = "localhost"
DB_PORT     = "5432"
DB_NAME     = "bank_dashboard"
# ─────────────────────────────────────────────────

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')

conn = psycopg2.connect(
    dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
    host=DB_HOST, port=DB_PORT
)
conn.set_client_encoding('UTF8')
cur = conn.cursor()

print("Clearing existing data...")
cur.execute("TRUNCATE TABLE transactions, loans, customers, branches CASCADE;")
conn.commit()
print("Cleared.\n")

tables = [
    ("branches",     "branches.csv"),
    ("customers",    "customers.csv"),
    ("loans",        "loans.csv"),
    ("transactions", "transactions.csv"),
]

for table_name, file_name in tables:
    filepath = os.path.join(DATA_DIR, file_name)
    print(f"Loading {file_name} into {table_name}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        cur.copy_expert(
            f"COPY {table_name} FROM STDIN WITH (FORMAT csv, HEADER true)",
            f
        )
    conn.commit()
    cur.execute(f"SELECT COUNT(*) FROM {table_name};")
    count = cur.fetchone()[0]
    print(f"  ✓ {count:,} rows now in {table_name}")

cur.close()
conn.close()
print("\n✅ All tables loaded successfully.")