# MCP Server Testing Guide

## Current Status

✅ **Server Running**: `http://127.0.0.1:8081`
✅ **Database Connected**: 2 accounts with 838 total transactions
✅ **All Tools Operational**: 8 financial data tools available

## Manual Tool Testing

### Test Account Summary

```bash
cd backend/mcp-server
source venv/bin/activate
export $(cat .env | grep -v '^#' | xargs)

python -c "
import asyncio
import json
from src.database import DatabaseConnection
from src.tools import accounts

async def test():
    db = DatabaseConnection()
    await db.connect()
    result = await accounts.get_account_summary(db)
    print(json.dumps(result, indent=2))
    await db.disconnect()

asyncio.run(test())
"
```

### Test Transactions Query

```bash
python -c "
import asyncio
import json
from src.database import DatabaseConnection
from src.tools import transactions

async def test():
    db = DatabaseConnection()
    await db.connect()
    result = await transactions.get_transactions(db, limit=10)
    print(json.dumps(result, indent=2))
    await db.disconnect()

asyncio.run(test())
"
```

### Test Spending by Category

```bash
python -c "
import asyncio
import json
from src.database import DatabaseConnection
from src.tools import analytics

async def test():
    db = DatabaseConnection()
    await db.connect()
    result = await analytics.get_spending_by_category(
        db,
        start_date='2025-01-01',
        end_date='2025-12-31'
    )
    print(json.dumps(result, indent=2))
    await db.disconnect()

asyncio.run(test())
"
```

### Test Merchant Spending

```bash
python -c "
import asyncio
import json
from src.database import DatabaseConnection
from src.tools import analytics

async def test():
    db = DatabaseConnection()
    await db.connect()
    result = await analytics.get_merchant_spending(
        db,
        start_date='2025-01-01',
        end_date='2025-12-31',
        top_n=10
    )
    print(json.dumps(result, indent=2))
    await db.disconnect()

asyncio.run(test())
"
```

### Test Cash Flow

```bash
python -c "
import asyncio
import json
from src.database import DatabaseConnection
from src.tools import analytics

async def test():
    db = DatabaseConnection()
    await db.connect()
    result = await analytics.get_cash_flow(
        db,
        start_date='2025-01-01',
        end_date='2025-12-31',
        granularity='monthly'
    )
    print(json.dumps(result, indent=2))
    await db.disconnect()

asyncio.run(test())
"
```

## Example Queries with Claude Code

Once connected, try these natural language queries:

### Basic Queries
- "Show me all my accounts and their balances"
- "What's my total balance across all accounts?"
- "Show me my recent transactions"

### Filtered Queries
- "Find all transactions from Starbucks"
- "Show me transactions over $100 from December 2025"
- "What did I spend at restaurants last month?"

### Analytics Queries
- "Show me my spending by category for 2025"
- "What are my top 10 merchants by spending?"
- "Show me my cash flow for the last 6 months"
- "How much did I spend on groceries vs restaurants?"

### Search Queries
- "Find all transactions containing 'coffee'"
- "Show me all Amazon purchases"
- "Search for 'gas' or 'fuel' in my transactions"

## Tool Details

### 1. get_account_summary
**Purpose**: Get all accounts with current balances

**Parameters**:
- `date_range` (optional): Filter by date range "YYYY-MM-DD,YYYY-MM-DD"

**Example Response**:
```json
{
  "accounts": [...],
  "total_accounts": 2,
  "total_balance": -2551.36
}
```

### 2. get_account_details
**Purpose**: Get detailed info about a specific account

**Parameters**:
- `account_id` (required): UUID of the account

### 3. get_transactions
**Purpose**: Query transactions with flexible filters

**Parameters**:
- `account_ids`: Comma-separated UUIDs
- `start_date`: Start date (YYYY-MM-DD)
- `end_date`: End date (YYYY-MM-DD)
- `category`: Category name or UUID
- `min_amount`: Minimum amount
- `max_amount`: Maximum amount
- `search_query`: Search text
- `limit`: Max results (default 100, max 1000)
- `offset`: Results to skip

### 4. search_transactions
**Purpose**: Full-text search across transactions

**Parameters**:
- `query` (required): Search term
- `account_ids`: Filter by accounts
- `date_range`: Date range "YYYY-MM-DD,YYYY-MM-DD"
- `limit`: Max results (default 50)

### 5. get_spending_by_category
**Purpose**: Aggregate spending by category

**Parameters**:
- `start_date`: Start date
- `end_date`: End date
- `account_ids`: Filter by accounts
- `category_type`: Filter by type (income/expense/transfer)

### 6. get_merchant_spending
**Purpose**: Top merchants by spending

**Parameters**:
- `start_date`: Start date
- `end_date`: End date
- `top_n`: Number of merchants (default 20)

### 7. get_cash_flow
**Purpose**: Income vs expenses over time

**Parameters**:
- `start_date` (required): Start date
- `end_date` (required): End date
- `granularity`: Time grouping (daily/weekly/monthly/yearly)

### 8. get_budget_status
**Purpose**: Budget vs actual spending

**Parameters**:
- `period`: Time period (current_month/current_quarter/current_year)

## Debugging

### Check Server Logs
```bash
tail -f /tmp/mcp-server.log
```

### Test Database Connection
```bash
psql postgresql://finance_user:finance_dev_password_change_me@localhost:5432/finance_db -c "SELECT COUNT(*) FROM transactions;"
```

### Verify Port Forwards
```bash
# PostgreSQL
lsof -i:5432

# MCP Server
lsof -i:8081
```

### Check Server Health
```bash
curl http://127.0.0.1:8081/health
```

Expected response:
```json
{"status":"healthy","server":"personal-finance-mcp"}
```

## Performance Notes

- Transactions are indexed on account_id, transaction_date, category_id, merchant
- Large queries (1000+ results) may be slow
- Use pagination (limit/offset) for large result sets
- Date range filters improve query performance
- Search queries use ILIKE (case-insensitive pattern matching)

## Security Notes

This server is configured for local development only:
- Binds to 127.0.0.1 (localhost only)
- No authentication/authorization
- Database credentials in .env file
- Not suitable for production without hardening
