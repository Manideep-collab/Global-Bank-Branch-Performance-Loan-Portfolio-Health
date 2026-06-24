"""
Solenne International Bank — Global Branch Performance Data Generator
=======================================================================
Fictional multinational bank. 18 branches across 6 global regions,
tiered by branch size (flagship/large/standard/small) to reflect
realistic scale differences between major financial hubs and
smaller regional branches.
"""

import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime
import os

np.random.seed(42)
random.seed(42)

fakers = {
    "North America":      Faker('en_US'),
    "Europe":              Faker('en_GB'),
    "Europe_DE":           Faker('de_DE'),
    "Europe_FR":           Faker('fr_FR'),
    "APAC_JP":             Faker('ja_JP'),
    "APAC_CN":             Faker('zh_CN'),
    "APAC_EN":             Faker('en_US'),
    "Middle_East":         Faker('ar_AE'),
    "Latin_America":       Faker('es_MX'),
    "Latin_America_BR":    Faker('pt_BR'),
    "Africa":              Faker('en_GB'),
}

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
NUM_CUSTOMERS    = 50000
NUM_LOANS        = 130000
NUM_TRANSACTIONS = 1500000
START_DATE       = datetime(2022, 1, 1)
END_DATE         = datetime(2024, 6, 30)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Branch size scaling — drives staff count, loan officer count,
# and relative customer volume per branch
STAFF_RANGE = {
    "flagship": (150, 300),
    "large":    (80, 150),
    "standard": (40, 80),
    "small":    (15, 40),
}
OFFICER_COUNT = {"flagship": 12, "large": 8, "standard": 5, "small": 3}
CUSTOMER_WEIGHT = {"flagship": 5, "large": 3, "standard": 2, "small": 1}


# ─────────────────────────────────────────
# TABLE 1: BRANCHES
# ─────────────────────────────────────────
def generate_branches():
    # (branch_name, city, region, locale_key, performance_tier, branch_size)
    branch_data = [
        ("Manhattan Branch",            "New York",     "North America",  "North America",     "high",   "flagship"),
        ("Chicago Loop Branch",         "Chicago",      "North America",  "North America",     "medium", "standard"),
        ("Toronto Bay St. Branch",      "Toronto",      "North America",  "North America",     "low",    "small"),
        ("Canary Wharf Branch",         "London",       "Europe",         "Europe",             "high",   "flagship"),
        ("Frankfurt Main Branch",       "Frankfurt",    "Europe",         "Europe_DE",          "medium", "large"),
        ("Zurich Branch",               "Zurich",       "Europe",         "Europe_DE",          "high",   "large"),
        ("Paris La Defense Branch",     "Paris",        "Europe",         "Europe_FR",          "medium", "standard"),
        ("Madrid Branch",                "Madrid",       "Europe",         "Europe_FR",          "low",    "small"),
        ("Singapore Marina Branch",     "Singapore",    "APAC",           "APAC_EN",            "high",   "flagship"),
        ("Hong Kong Central Branch",    "Hong Kong",    "APAC",           "APAC_CN",            "high",   "flagship"),
        ("Tokyo Shinjuku Branch",       "Tokyo",        "APAC",           "APAC_JP",            "medium", "large"),
        ("Sydney CBD Branch",           "Sydney",       "APAC",           "APAC_EN",            "medium", "large"),
        ("Shanghai Pudong Branch",      "Shanghai",     "APAC",           "APAC_CN",            "low",    "standard"),
        ("Dubai DIFC Branch",            "Dubai",        "Middle East",    "Middle_East",        "high",   "flagship"),
        ("Riyadh Branch",                "Riyadh",       "Middle East",    "Middle_East",        "low",    "standard"),
        ("Sao Paulo Faria Lima Branch", "Sao Paulo",    "Latin America",  "Latin_America_BR",   "medium", "large"),
        ("Mexico City Polanco Branch",  "Mexico City",  "Latin America",  "Latin_America",      "low",    "small"),
        ("Johannesburg Sandton Branch", "Johannesburg", "Africa",         "Africa",             "medium", "standard"),
    ]

    branches = []
    for i, (name, city, region, locale_key, tier, size) in enumerate(branch_data, start=1):
        lo, hi = STAFF_RANGE[size]
        branches.append({
            "branch_id":        f"BR{i:03d}",
            "branch_name":      name,
            "city":             city,
            "region":           region,
            "locale_key":       locale_key,
            "performance_tier": tier,
            "branch_size":      size,
            "established_year": random.randint(1985, 2015),
            "total_staff":      random.randint(lo, hi),
        })

    return pd.DataFrame(branches)


# ─────────────────────────────────────────
# TABLE 2: CUSTOMERS — weighted toward larger branches
# ─────────────────────────────────────────
def generate_customers(branches_df):
    """
    50,000 customers, distributed with weighted probability so flagship
    branches (Manhattan, London, Singapore, HK, Dubai) realistically hold
    far more customers than small regional branches (Toronto, Madrid).
    """

    segments      = ["Retail", "SME", "Corporate"]
    segment_probs = [0.70, 0.22, 0.08]

    branch_records = branches_df.to_dict("records")
    weights = [CUSTOMER_WEIGHT[b["branch_size"]] for b in branch_records]

    customers = []
    for i in range(1, NUM_CUSTOMERS + 1):
        branch = random.choices(branch_records, weights=weights, k=1)[0]
        locale_key = branch["locale_key"]
        fkr = fakers[locale_key]

        customers.append({
            "customer_id":   f"CUST{i:06d}",
            "customer_name": fkr.name(),
            "email":         fkr.email(),
            "phone":         fkr.phone_number(),
            "city":          branch["city"],
            "segment":       np.random.choice(segments, p=segment_probs),
            "branch_id":     branch["branch_id"],
            "join_date":     fkr.date_between(start_date="-6y", end_date="-6m"),
            "credit_score":  int(np.clip(np.random.normal(680, 80), 300, 900)),
        })

    return pd.DataFrame(customers)


# ─────────────────────────────────────────
# TABLE 3: LOANS — officer pool size scales with branch size
# ─────────────────────────────────────────
def generate_loans(branches_df, customers_df):
    npl_prob = {"high": 0.06, "medium": 0.12, "low": 0.18}

    loan_ranges = {
        "Retail":    (5_000,      150_000),
        "SME":       (50_000,     2_000_000),
        "Corporate": (1_000_000,  50_000_000),
    }

    loan_types = ["Mortgage", "Personal Loan", "Auto Loan", "Business Loan",
                  "Working Capital Loan", "Trade Finance Loan", "Education Loan"]
    loan_type_probs = [0.28, 0.22, 0.15, 0.12, 0.10, 0.08, 0.05]

    branch_tier_map      = dict(zip(branches_df["branch_id"], branches_df["performance_tier"]))
    branch_size_map      = dict(zip(branches_df["branch_id"], branches_df["branch_size"]))
    customer_segment_map = dict(zip(customers_df["customer_id"], customers_df["segment"]))
    customer_branch_map  = dict(zip(customers_df["customer_id"], customers_df["branch_id"]))
    customer_ids         = customers_df["customer_id"].tolist()

    # Officer pool per branch, sized according to branch size
    officer_pool = {
        bid: [f"{bid}_LO{j}" for j in range(1, OFFICER_COUNT[branch_size_map[bid]] + 1)]
        for bid in branches_df["branch_id"]
    }

    loans = []
    for i in range(1, NUM_LOANS + 1):
        cust_id   = random.choice(customer_ids)
        branch_id = customer_branch_map[cust_id]
        segment   = customer_segment_map[cust_id]
        tier      = branch_tier_map[branch_id]

        lo_key    = random.choice(officer_pool[branch_id])
        loan_type = np.random.choice(loan_types, p=loan_type_probs)

        lo, hi    = loan_ranges[segment]
        loan_amt  = round(np.random.lognormal(mean=np.log((lo + hi) / 2), sigma=0.6))
        loan_amt  = int(np.clip(loan_amt, lo, hi))

        disburse_date = pd.Timestamp(
            np.random.choice(pd.date_range(START_DATE, END_DATE, freq='D'))
        ).date()
        tenure_months = random.choice([12, 24, 36, 48, 60, 84, 120, 180, 240])
        interest_rate = round(random.uniform(3.5, 14.5), 2)

        is_npl = random.random() < npl_prob[tier]
        if is_npl:
            status       = "NPL"
            overdue_days = int(np.random.exponential(scale=120)) + 91
        else:
            roll = random.random()
            if roll < 0.78:
                status, overdue_days = "Active", 0
            elif roll < 0.89:
                status, overdue_days = "Closed", 0
            elif roll < 0.94:
                status, overdue_days = "Overdue_30", random.randint(1, 30)
            else:
                status, overdue_days = "Overdue_60", random.randint(31, 90)

        loans.append({
            "loan_id":       f"LN{i:07d}",
            "customer_id":   cust_id,
            "branch_id":     branch_id,
            "officer_id":    lo_key,
            "loan_type":     loan_type,
            "loan_amount":   loan_amt,
            "tenure_months": tenure_months,
            "interest_rate": interest_rate,
            "disburse_date": disburse_date,
            "status":        status,
            "overdue_days":  overdue_days,
        })

    return pd.DataFrame(loans)


# ─────────────────────────────────────────
# TABLE 4: TRANSACTIONS
# ─────────────────────────────────────────
def generate_transactions(branches_df, customers_df):
    branch_ids   = branches_df["branch_id"].tolist()
    customer_ids = customers_df["customer_id"].tolist()
    tier_map     = dict(zip(branches_df["branch_id"], branches_df["performance_tier"]))

    txn_types      = ["deposit", "withdrawal"]
    txn_type_probs = [0.60, 0.40]

    tier_amount_base = {"high": 9000, "medium": 5000, "low": 2500}

    date_range = pd.date_range(START_DATE, END_DATE, freq='D').tolist()
    n = NUM_TRANSACTIONS

    txn_branch_ids   = np.random.choice(branch_ids, size=n)
    txn_customer_ids = np.random.choice(customer_ids, size=n)
    txn_dates        = np.random.choice(date_range, size=n)
    txn_type_arr     = np.random.choice(txn_types, size=n, p=txn_type_probs)

    tier_arr = np.array([tier_map[b] for b in txn_branch_ids])
    base_arr = np.array([tier_amount_base[t] for t in tier_arr])
    amounts = np.round(np.random.lognormal(mean=np.log(base_arr), sigma=0.8)).astype(int)
    amounts = np.clip(amounts, 50, 500_000)

    months = pd.to_datetime(txn_dates).month
    multiplier = np.where(np.isin(months, [11, 12]), 1.30,
                  np.where(months == 4, 1.20,
                  np.where(np.isin(months, [1, 8]), 0.85, 1.0)))
    seasonal_amounts = (amounts * multiplier).astype(int)

    transactions = pd.DataFrame({
        "txn_id":      [f"TXN{i:08d}" for i in range(1, n + 1)],
        "branch_id":   txn_branch_ids,
        "customer_id": txn_customer_ids,
        "txn_type":    txn_type_arr,
        "amount":      seasonal_amounts,
        "txn_date":    pd.to_datetime(txn_dates).date,
        "channel":     np.random.choice(
                           ["Branch", "ATM", "OnlineBanking", "MobileApp", "WireTransfer"],
                           size=n,
                           p=[0.15, 0.20, 0.25, 0.30, 0.10]
                       ),
    })

    return transactions


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
if __name__ == "__main__":
    print("Generating branches...")
    branches = generate_branches()
    branches.drop(columns=["locale_key"]).to_csv(f"{OUTPUT_DIR}/branches.csv", index=False)
    print(f"  done — {len(branches)} branches across {branches['region'].nunique()} regions")

    print("Generating customers...")
    customers = generate_customers(branches)
    customers.to_csv(f"{OUTPUT_DIR}/customers.csv", index=False)
    print(f"  done — {len(customers)} customers")

    print("Generating loans...")
    loans = generate_loans(branches, customers)
    loans.to_csv(f"{OUTPUT_DIR}/loans.csv", index=False)
    print(f"  done — {len(loans)} loans")

    print("Generating transactions (this takes ~1-2 minutes)...")
    transactions = generate_transactions(branches, customers)
    transactions.to_csv(f"{OUTPUT_DIR}/transactions.csv", index=False)
    print(f"  done — {len(transactions)} transactions")

    print("\nAll files saved to data/raw/")
    print("\nSanity check:")
    print(f"  NPL rate: {(loans['status'] == 'NPL').mean() * 100:.2f}%")
    print(f"  Avg loan amount: ${loans['loan_amount'].mean():,.0f}")
    print(f"  Customers per branch (flagship vs small):")
    print(customers['branch_id'].value_counts().head(3))
    print(customers['branch_id'].value_counts().tail(3))
    print(f"  Deposit/Withdrawal split: {(transactions['txn_type']=='deposit').mean()*100:.1f}% / {(transactions['txn_type']=='withdrawal').mean()*100:.1f}%")