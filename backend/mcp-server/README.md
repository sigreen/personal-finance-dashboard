# Personal Finance MCP Server

MCP (Model Context Protocol) server that exposes personal financial data from PostgreSQL for AI-powered querying via Claude Code and other LLM providers.

## Features

- **SSE Protocol**: Server-Sent Events for real-time communication
- **Direct Database Access**: Connects to PostgreSQL in Kubernetes cluster
- **8 Financial Tools**: Comprehensive querying capabilities
- **Python + asyncpg**: Fast async PostgreSQL queries
- **Docker Ready**: Containerized for Kubernetes deployment

## Quick Start

### Local Development

1. **Install dependencies**:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your database connection
```

3. **Start PostgreSQL port-forward** (if using Kubernetes):
```bash
kubectl port-forward svc/postgres 5432:5432 &
```

4. **Run the server**:
```bash
python main.py
```

Server will start on `http://127.0.0.1:8081`

### Using the Convenience Script

```bash
# From project root
./scripts/start-mcp-server.sh
```

This automatically:
- Starts PostgreSQL port-forward if needed
- Creates virtual environment
- Installs dependencies
- Runs the server

## Configuration

### Environment Variables

```bash
# Database connection
DATABASE_URL=postgresql://finance_user:password@localhost:5432/finance_db

# Server configuration
HOST=127.0.0.1  # or 0.0.0.0 for Kubernetes
PORT=8081
```

### Claude Code Integration

Add to `.mcp.json` in your project root:

```json
{
  "mcpServers": {
    "personal-finance": {
      "url": "http://localhost:8081/sse",
      "type": "sse"
    }
  }
}
```

Then restart Claude Code to connect.

## Available Tools

### Account Management
1. **get_account_summary**
   - Returns all accounts with balances
   - Optional date range filtering
   - Example: "Show me all my accounts"

2. **get_account_details**
   - Detailed info for specific account
   - Transaction statistics
   - Example: "Tell me about my Chase account"

### Transactions
3. **get_transactions**
   - Query with filters (date, amount, category, search)
   - Pagination support (up to 1000 results)
   - Example: "Show me my last 50 transactions"

4. **search_transactions**
   - Full-text search across descriptions, merchants, notes
   - Example: "Find all Starbucks purchases"

### Analytics
5. **get_spending_by_category**
   - Aggregate spending by category
   - Filter by date range, account, category type
   - Example: "What did I spend by category last month?"

6. **get_merchant_spending**
   - Top merchants by spending amount
   - Configurable top N results
   - Example: "Show me my top 10 merchants"

7. **get_cash_flow**
   - Income vs expenses over time
   - Multiple granularities (daily, weekly, monthly, yearly)
   - Example: "Show my cash flow for Q4 2025"

8. **get_budget_status**
   - Budget vs actual spending
   - Current month/quarter/year
   - Example: "How am I doing against my budgets?"

## API Endpoints

- **GET /health** - Health check (returns JSON status)
- **GET /sse** - SSE endpoint for MCP connections
- **POST /messages/** - Message handling endpoint

## Project Structure

```
backend/mcp-server/
├── src/
│   ├── __init__.py
│   ├── server.py              # Main MCP server with SSE
│   ├── database/
│   │   ├── __init__.py
│   │   └── connection.py      # asyncpg connection pool
│   └── tools/
│       ├── __init__.py
│       ├── accounts.py         # Account tools
│       ├── transactions.py     # Transaction tools
│       └── analytics.py        # Analytics tools
├── tests/
│   └── test_mcp_connection.py # Connection tests
├── main.py                    # Entry point
├── requirements.txt           # Python dependencies
├── Containerfile             # Docker/Podman container
├── .env.example              # Environment template
└── README.md
```

## Development

### Running Tests

```bash
python tests/test_mcp_connection.py
```

### Viewing Logs

```bash
# Local server
tail -f /tmp/mcp-server-local.log

# Kubernetes
kubectl logs -f -l app=mcp-server
```

### Database Connection Test

```bash
python -c "
import asyncio
from src.database import DatabaseConnection

async def test():
    db = DatabaseConnection()
    await db.connect()
    result = await db.execute_query('SELECT COUNT(*) FROM accounts')
    print(f'Accounts: {result[0][\"count\"]}')
    await db.disconnect()

asyncio.run(test())
"
```

## Kubernetes Deployment

### Build and Deploy

```bash
# From project root
./scripts/build-and-deploy-mcp.sh
```

This will:
1. Build container image with Podman
2. Load into minikube
3. Deploy to Kubernetes
4. Set up LoadBalancer service

### Manual Deployment

```bash
# Build image
podman build -t finance-mcp:latest -f Containerfile .

# Load into minikube
minikube image load finance-mcp:latest

# Deploy
kubectl apply -f ../../k8s/base/mcp-server-deployment.yaml

# Check status
kubectl get pods -l app=mcp-server
kubectl logs -l app=mcp-server
```

## Troubleshooting

### Connection Issues

1. **Server won't start**:
   ```bash
   # Check if port is in use
   lsof -i:8081

   # Check environment variables
   cat .env
   ```

2. **Database connection failed**:
   ```bash
   # Verify PostgreSQL is accessible
   psql $DATABASE_URL -c "SELECT 1"

   # Check port-forward
   lsof -i:5432
   ```

3. **Claude Code can't connect**:
   - Verify server is running: `curl http://localhost:8081/health`
   - Check SSE endpoint: `curl -N http://localhost:8081/sse`
   - Restart Claude Code completely
   - Check `.mcp.json` configuration

### Common Issues

**"DATABASE_URL must be provided"**:
- Ensure `.env` file exists with DATABASE_URL
- Or export it: `export DATABASE_URL=postgresql://...`

**"Connection refused"**:
- Start PostgreSQL port-forward: `kubectl port-forward svc/postgres 5432:5432 &`
- Verify server is running: `ps aux | grep "python.*main.py"`

**"Module not found"**:
- Activate virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

## Performance

- **Connection pooling**: 2-10 connections via asyncpg
- **Query timeout**: 60 seconds
- **Result limits**: Up to 1000 transactions per query
- **Indexes**: Optimized for account_id, date, category, merchant queries

## Security

For local development only:
- ⚠️ No authentication/authorization
- ⚠️ Binds to 127.0.0.1 (localhost only)
- ⚠️ Database credentials in .env file

For production:
- Add authentication (API keys, OAuth)
- Use HTTPS/TLS
- Implement rate limiting
- Store secrets securely (Kubernetes secrets, vault)
- Validate all inputs
- Audit logging

## Dependencies

- **mcp** - Model Context Protocol SDK
- **asyncpg** - Async PostgreSQL driver
- **uvicorn** - ASGI server
- **starlette** - Web framework
- **sse-starlette** - SSE support
- **python-dotenv** - Environment management

## License

Part of the Personal Finance Dashboard project.

---

**Current Status**: ✅ Working
**Version**: 0.2.0
**Protocol**: SSE (Server-Sent Events)
**Python**: 3.11+
