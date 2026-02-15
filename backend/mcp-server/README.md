# Personal Finance MCP Server

This MCP (Model Context Protocol) server exposes financial data from the PostgreSQL database for querying by Claude and other AI models.

## Available Tools

### get_account_summary
Get summary of all financial accounts with transaction statistics.

**Parameters:**
- `start_date` (optional): Start date for statistics (YYYY-MM-DD format)
- `end_date` (optional): End date for statistics (YYYY-MM-DD format)

### get_transactions
Get transactions with optional filters.

**Parameters:**
- `account_ids` (optional): List of account UUIDs to filter by
- `start_date` (optional): Start date (YYYY-MM-DD)
- `end_date` (optional): End date (YYYY-MM-DD)
- `category` (optional): Category name to filter by
- `min_amount` (optional): Minimum transaction amount
- `max_amount` (optional): Maximum transaction amount
- `search_query` (optional): Search term for description/merchant
- `limit` (optional): Maximum number of results (default: 100)
- `offset` (optional): Pagination offset (default: 0)

### search_transactions
Full-text search across transaction descriptions and merchants.

**Parameters:**
- `query` (required): Search query string
- `account_ids` (optional): List of account UUIDs to filter by
- `start_date` (optional): Start date (YYYY-MM-DD)
- `end_date` (optional): End date (YYYY-MM-DD)
- `limit` (optional): Maximum number of results (default: 50)

### get_spending_by_category
Get spending aggregated and grouped by category.

**Parameters:**
- `start_date` (optional): Start date (YYYY-MM-DD)
- `end_date` (optional): End date (YYYY-MM-DD)
- `account_ids` (optional): List of account UUIDs
- `category_type` (optional): Filter by 'income' or 'expense'

### get_merchant_spending
Get spending grouped by merchant/vendor.

**Parameters:**
- `start_date` (optional): Start date (YYYY-MM-DD)
- `end_date` (optional): End date (YYYY-MM-DD)
- `top_n` (optional): Number of top merchants to return (default: 20)

### get_cash_flow
Get income vs expenses over time with configurable granularity.

**Parameters:**
- `start_date` (optional): Start date (YYYY-MM-DD)
- `end_date` (optional): End date (YYYY-MM-DD)
- `granularity` (optional): Time granularity - 'daily', 'weekly', or 'monthly' (default: 'monthly')

## Development

### Local Testing

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=finance
export DB_USER=finance_user
export DB_PASSWORD=finance_password
```

3. Run the server:
```bash
python main.py
```

### Docker Build

```bash
podman build -t finance-mcp:latest .
```

### Kubernetes Deployment

Deploy to Kubernetes:
```bash
kubectl apply -f ../../k8s/base/mcp-server-deployment.yaml
```

Check deployment status:
```bash
kubectl get pods -l app=mcp-server
kubectl logs -l app=mcp-server
```

### Using with Claude Desktop

To use this MCP server with Claude Desktop, add it to your Claude Desktop configuration:

**On macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**On Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

Since the server is deployed in Kubernetes, you'll need to port-forward it first:

```bash
kubectl port-forward svc/mcp-server 8081:8081
```

Then add to your Claude Desktop config:
```json
{
  "mcpServers": {
    "personal-finance": {
      "command": "kubectl",
      "args": ["exec", "-i", "deployment/mcp-server", "--", "python", "main.py"]
    }
  }
}
```

### Testing via kubectl exec

You can test the MCP server directly using kubectl exec:

```bash
# Get a shell in the MCP server pod
kubectl exec -it deployment/mcp-server -- /bin/bash

# Run the MCP server interactively
python main.py
```

## Architecture

- **Language:** Python 3.11+
- **Framework:** MCP SDK (Model Context Protocol)
- **Database:** PostgreSQL via SQLAlchemy
- **Transport:** stdio (standard input/output)

## Environment Variables

- `DB_HOST` - PostgreSQL host (default: postgresql)
- `DB_PORT` - PostgreSQL port (default: 5432)
- `DB_NAME` - Database name (default: finance)
- `DB_USER` - Database user (default: finance_user)
- `DB_PASSWORD` - Database password (default: finance_password)
- `LOG_LEVEL` - Logging level (default: INFO)
