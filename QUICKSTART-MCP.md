# Personal Finance MCP Server - Quick Start Guide

## Overview

The Personal Finance MCP Server exposes your financial data from PostgreSQL for querying by Claude Code and other AI assistants using the Model Context Protocol (MCP).

## Status

✅ **MCP Server is running at**: `http://127.0.0.1:8081/sse`
✅ **Health Check**: `http://127.0.0.1:8081/health`
✅ **Database**: Connected to PostgreSQL in Kubernetes

## Quick Start

### 1. Start the MCP Server

The easiest way to start the server:

```bash
./scripts/start-mcp-server.sh
```

This script will:
- Start PostgreSQL port-forward (if needed)
- Create/activate Python virtual environment
- Install dependencies
- Run the MCP server

### 2. Stop the MCP Server

```bash
./scripts/stop-mcp-server.sh
```

This will stop both the MCP server and PostgreSQL port-forward.

### 3. Manual Start (if needed)

If you prefer to start manually:

```bash
# Start PostgreSQL port-forward
kubectl port-forward svc/postgres 5432:5432 -n default &

# Navigate to MCP server directory
cd backend/mcp-server

# Activate virtual environment
source venv/bin/activate

# Run server
python main.py
```

## Using with Claude Code

The MCP server is already configured in `.mcp.json`:

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

Once the server is running, Claude Code will automatically connect to it.

## Available Tools

You can ask Claude Code questions like:

### Account Queries
- "Show me all my accounts"
- "What's my total balance across all accounts?"
- "Give me details about my checking account"

### Transaction Queries
- "Show me my last 50 transactions"
- "Find all transactions for Starbucks"
- "Show me transactions over $100 from last month"
- "Search for 'grocery' in my transactions"

### Analytics
- "What did I spend by category this month?"
- "Show me my top 10 merchants by spending"
- "What's my cash flow for the last 3 months?"
- "How am I doing against my budgets?"

## Testing the Server

### Health Check

```bash
curl http://127.0.0.1:8081/health
```

Expected response:
```json
{"status":"healthy","server":"personal-finance-mcp"}
```

### View Logs

```bash
tail -f /tmp/mcp-server.log
```

### Check Processes

```bash
# Check if server is running
lsof -i:8081

# Check if PostgreSQL port-forward is running
lsof -i:5432
```

## Troubleshooting

### Server won't start

1. Check if port 8081 is already in use:
   ```bash
   lsof -i:8081
   ```

2. Check PostgreSQL connection:
   ```bash
   kubectl get svc postgres
   kubectl port-forward svc/postgres 5432:5432
   ```

3. View server logs:
   ```bash
   cat /tmp/mcp-server.log
   ```

### Database connection errors

1. Verify PostgreSQL is running:
   ```bash
   kubectl get pods -l app=postgres
   ```

2. Test database connection:
   ```bash
   cd backend/mcp-server
   source venv/bin/activate
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

### Claude Code not connecting

1. Restart Claude Code
2. Check that the server is running:
   ```bash
   curl http://127.0.0.1:8081/health
   ```
3. Verify `.mcp.json` configuration
4. Check Claude Code logs for connection errors

## Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌──────────────┐
│  Claude Code    │◄────►│  MCP Server      │◄────►│  PostgreSQL  │
│  (MCP Client)   │ SSE  │  (localhost:8081)│      │  (k8s)       │
└─────────────────┘      └──────────────────┘      └──────────────┘
                                                           ▲
                                                           │
                                                    kubectl port-forward
                                                           │
                                                      localhost:5432
```

## Next Steps

1. **Try querying your data**: Ask Claude Code questions about your finances
2. **Add more data**: Import transactions through the web UI
3. **Create budgets**: Set up budgets and track spending
4. **Customize tools**: Add new MCP tools in `backend/mcp-server/src/tools/`

## Resources

- MCP Documentation: https://modelcontextprotocol.io
- Server Code: `backend/mcp-server/`
- Configuration: `.mcp.json`
- Logs: `/tmp/mcp-server.log`
