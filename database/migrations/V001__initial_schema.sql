-- Personal Finance Dashboard - Initial Schema
-- Version: 001
-- Description: Create core tables for accounts, transactions, categories, budgets, and import tracking

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create ENUM types
CREATE TYPE account_type AS ENUM (
    'checking',
    'savings',
    'credit_card',
    'brokerage',
    'loan'
);

CREATE TYPE transaction_type AS ENUM (
    'debit',
    'credit'
);

CREATE TYPE category_type AS ENUM (
    'income',
    'expense',
    'transfer'
);

CREATE TYPE import_status AS ENUM (
    'pending',
    'processing',
    'completed',
    'failed'
);

CREATE TYPE budget_period AS ENUM (
    'monthly',
    'quarterly',
    'yearly'
);

-- ===================================================
-- ACCOUNTS TABLE
-- ===================================================
CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_type account_type NOT NULL,
    institution_name VARCHAR(255) NOT NULL,
    account_name VARCHAR(255) NOT NULL,
    account_number_last4 VARCHAR(4),
    currency VARCHAR(3) DEFAULT 'USD',
    is_active BOOLEAN DEFAULT true,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for common queries
CREATE INDEX idx_accounts_institution ON accounts(institution_name);
CREATE INDEX idx_accounts_type ON accounts(account_type);
CREATE INDEX idx_accounts_active ON accounts(is_active);

-- ===================================================
-- CATEGORIES TABLE
-- ===================================================
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    parent_category_id UUID REFERENCES categories(id) ON DELETE SET NULL,
    category_type category_type NOT NULL,
    icon VARCHAR(50),
    color VARCHAR(7), -- Hex color code
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for hierarchy queries
CREATE INDEX idx_categories_parent ON categories(parent_category_id);
CREATE INDEX idx_categories_type ON categories(category_type);

-- ===================================================
-- TRANSACTIONS TABLE
-- ===================================================
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    transaction_date DATE NOT NULL,
    post_date DATE,
    description TEXT NOT NULL,
    original_description TEXT,
    amount DECIMAL(15, 2) NOT NULL,
    transaction_type transaction_type NOT NULL,
    category_id UUID REFERENCES categories(id) ON DELETE SET NULL,
    merchant VARCHAR(255),
    notes TEXT,
    is_duplicate BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_transactions_account ON transactions(account_id);
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_transactions_account_date ON transactions(account_id, transaction_date DESC);
CREATE INDEX idx_transactions_category ON transactions(category_id);
CREATE INDEX idx_transactions_merchant ON transactions(merchant);
CREATE INDEX idx_transactions_amount ON transactions(amount);

-- Index for duplicate detection
CREATE INDEX idx_transactions_duplicate_check ON transactions(
    account_id,
    transaction_date,
    amount,
    description
);

-- ===================================================
-- BUDGETS TABLE
-- ===================================================
CREATE TABLE budgets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_id UUID NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    amount DECIMAL(15, 2) NOT NULL CHECK (amount >= 0),
    period budget_period NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    is_active BOOLEAN DEFAULT true,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_date_range CHECK (end_date IS NULL OR end_date >= start_date)
);

-- Index for budget queries
CREATE INDEX idx_budgets_category ON budgets(category_id);
CREATE INDEX idx_budgets_period ON budgets(period);
CREATE INDEX idx_budgets_dates ON budgets(start_date, end_date);
CREATE INDEX idx_budgets_active ON budgets(is_active);

-- ===================================================
-- IMPORT_LOGS TABLE
-- ===================================================
CREATE TABLE import_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename VARCHAR(255) NOT NULL,
    account_id UUID REFERENCES accounts(id) ON DELETE SET NULL,
    import_status import_status NOT NULL DEFAULT 'pending',
    rows_processed INTEGER DEFAULT 0,
    rows_imported INTEGER DEFAULT 0,
    rows_failed INTEGER DEFAULT 0,
    rows_duplicate INTEGER DEFAULT 0,
    error_details JSONB,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for import history
CREATE INDEX idx_import_logs_account ON import_logs(account_id);
CREATE INDEX idx_import_logs_status ON import_logs(import_status);
CREATE INDEX idx_import_logs_started ON import_logs(started_at DESC);

-- ===================================================
-- HOLDINGS TABLE (for brokerage accounts)
-- ===================================================
CREATE TABLE holdings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,
    quantity DECIMAL(18, 6) NOT NULL,
    cost_basis DECIMAL(15, 2),
    current_price DECIMAL(15, 2),
    as_of_date DATE NOT NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for holdings
CREATE INDEX idx_holdings_account ON holdings(account_id);
CREATE INDEX idx_holdings_symbol ON holdings(symbol);
CREATE INDEX idx_holdings_date ON holdings(as_of_date DESC);

-- Unique constraint to prevent duplicate holdings on same date
CREATE UNIQUE INDEX idx_holdings_unique ON holdings(account_id, symbol, as_of_date);

-- ===================================================
-- CSV_MAPPING_RULES TABLE
-- ===================================================
CREATE TABLE csv_mapping_rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_name VARCHAR(255) NOT NULL,
    account_type account_type NOT NULL,
    column_mappings JSONB NOT NULL,
    date_format VARCHAR(50) DEFAULT 'MM/DD/YYYY',
    amount_format VARCHAR(50) DEFAULT 'US',
    has_header BOOLEAN DEFAULT true,
    delimiter VARCHAR(1) DEFAULT ',',
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for mapping lookup
CREATE INDEX idx_csv_mapping_institution ON csv_mapping_rules(institution_name);
CREATE INDEX idx_csv_mapping_type ON csv_mapping_rules(account_type);

-- Unique constraint for institution + account_type combination
CREATE UNIQUE INDEX idx_csv_mapping_unique ON csv_mapping_rules(institution_name, account_type);

-- ===================================================
-- TRIGGERS
-- ===================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at trigger to relevant tables
CREATE TRIGGER update_accounts_updated_at BEFORE UPDATE ON accounts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_transactions_updated_at BEFORE UPDATE ON transactions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_budgets_updated_at BEFORE UPDATE ON budgets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_holdings_updated_at BEFORE UPDATE ON holdings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_csv_mapping_rules_updated_at BEFORE UPDATE ON csv_mapping_rules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ===================================================
-- VIEWS
-- ===================================================

-- View for transaction summary by category
CREATE VIEW transaction_summary_by_category AS
SELECT
    c.id as category_id,
    c.name as category_name,
    c.category_type,
    COUNT(t.id) as transaction_count,
    SUM(CASE WHEN t.transaction_type = 'debit' THEN -t.amount ELSE t.amount END) as net_amount,
    MIN(t.transaction_date) as first_transaction,
    MAX(t.transaction_date) as last_transaction
FROM categories c
LEFT JOIN transactions t ON c.id = t.category_id
GROUP BY c.id, c.name, c.category_type;

-- View for account balances
CREATE VIEW account_balances AS
SELECT
    a.id as account_id,
    a.account_name,
    a.institution_name,
    a.account_type,
    COUNT(t.id) as transaction_count,
    SUM(CASE WHEN t.transaction_type = 'credit' THEN t.amount ELSE -t.amount END) as balance,
    MAX(t.transaction_date) as last_transaction_date
FROM accounts a
LEFT JOIN transactions t ON a.id = t.account_id
WHERE a.is_active = true
GROUP BY a.id, a.account_name, a.institution_name, a.account_type;

-- ===================================================
-- COMMENTS
-- ===================================================

COMMENT ON TABLE accounts IS 'Financial accounts (checking, savings, credit cards, brokerage, loans)';
COMMENT ON TABLE transactions IS 'Individual financial transactions';
COMMENT ON TABLE categories IS 'Transaction categories with hierarchical support';
COMMENT ON TABLE budgets IS 'Budget allocations by category and time period';
COMMENT ON TABLE import_logs IS 'History of CSV import operations';
COMMENT ON TABLE holdings IS 'Investment holdings for brokerage accounts';
COMMENT ON TABLE csv_mapping_rules IS 'CSV column mapping rules by institution';

COMMENT ON COLUMN transactions.amount IS 'Always positive; use transaction_type to indicate debit/credit';
COMMENT ON COLUMN transactions.is_duplicate IS 'Flag for potential duplicate transactions';
COMMENT ON COLUMN budgets.amount IS 'Budget amount in account currency';
COMMENT ON COLUMN csv_mapping_rules.column_mappings IS 'JSON mapping of CSV columns to database fields';
