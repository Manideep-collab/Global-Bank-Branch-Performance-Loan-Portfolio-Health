DROP TABLE IF EXISTS transactions, loans, customers, branches CASCADE;

CREATE TABLE branches (
    branch_id        VARCHAR(10) PRIMARY KEY,
    branch_name      VARCHAR(100),
    city             VARCHAR(50),
    region           VARCHAR(20),
    performance_tier VARCHAR(10),
    branch_size      VARCHAR(10),
    established_year INT,
    total_staff      INT
);

CREATE TABLE customers (
    customer_id   VARCHAR(15) PRIMARY KEY,
    customer_name VARCHAR(100),
    email         VARCHAR(100),
    phone         VARCHAR(30),    -- widened from 20
    city          VARCHAR(50),
    segment       VARCHAR(20),
    branch_id     VARCHAR(10) REFERENCES branches(branch_id),
    join_date     DATE,
    credit_score  INT
);

CREATE TABLE loans (
    loan_id        VARCHAR(15) PRIMARY KEY,
    customer_id    VARCHAR(15) REFERENCES customers(customer_id),
    branch_id      VARCHAR(10) REFERENCES branches(branch_id),
    officer_id     VARCHAR(20),
    loan_type      VARCHAR(30),
    loan_amount    BIGINT,
    tenure_months  INT,
    interest_rate  NUMERIC(5,2),
    disburse_date  DATE,
    status         VARCHAR(20),
    overdue_days   INT
);

CREATE TABLE transactions (
    txn_id      VARCHAR(15) PRIMARY KEY,
    branch_id   VARCHAR(10) REFERENCES branches(branch_id),
    customer_id VARCHAR(15) REFERENCES customers(customer_id),
    txn_type    VARCHAR(20),
    amount      BIGINT,
    txn_date    DATE,
    channel     VARCHAR(20)
);

-- Verification
SELECT 'branches'    AS tbl, COUNT(*) FROM branches
UNION ALL
SELECT 'customers',          COUNT(*) FROM customers
UNION ALL
SELECT 'loans',              COUNT(*) FROM loans
UNION ALL
SELECT 'transactions',       COUNT(*) FROM transactions;


SELECT * FROM loans;
SELECT * FROM transactions;

TRUNCATE TABLE transactions, loans, customers, branches CASCADE;
