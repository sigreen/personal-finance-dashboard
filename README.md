# Personal Finance Dashboard

A personal finance management system that imports financial data from CSV files, stores them in PostgreSQL, and exposes the data through an MCP (Model Context Protocol) server for AI-powered querying.

## 🎯 Features

- **CSV Import**: Import transactions from bank, credit card, and brokerage statements
- **PostgreSQL Database**: Normalized storage with 838+ transactions across 2 accounts
- **Web Dashboard**: React-based UI for data visualization and management
- **MCP Server**: Query your financial data using natural language via Claude Code
- **Kubernetes**: All services run in minikube for local development

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌──────────────┐
│  Claude Code    │────▶│  MCP Server      │────▶│  PostgreSQL  │
│  (AI Queries)   │ SSE │  (localhost:8081)│     │  (Kubernetes)│
└─────────────────┘     └──────────────────┘     └──────────────┘
                                                          ▲
                                                          │
                        ┌─────────────────────────────────┘
                        │
                ┌───────▼────────┐          ┌──────────────┐
                │  ETL Service   │──────────│  Web UI      │
                │  (CSV Import)  │          │  (React)     │
                └────────────────┘          └──────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **minikube** (with podman driver)
- **kubectl**
- **podman**
- **Python 3.11+**
- **Node.js 18+**

### 1. Setup Infrastructure

```bash
# Start minikube
minikube start --cpus=4 --memory=8192 --driver=podman --container-runtime=cri-o

# Enable MetalLB
./scripts/enable-metallb.sh

# Deploy PostgreSQL
./scripts/deploy-database.sh

# Run migrations
./scripts/run-migrations.sh
```

### 2. Deploy Services

```bash
# Build and deploy all services
./scripts/build-all.sh
./scripts/load-images.sh

# Deploy to Kubernetes
kubectl apply -f k8s/base/
```

### 3. Start MCP Server

```bash
# Start the MCP server (for Claude Code integration)
./scripts/start-mcp-server.sh
```

This will:
- Start PostgreSQL port-forward (localhost:5432)
- Start MCP server (localhost:8081)
- Show health status

### 4. Access Services

- **Web Dashboard**: `http://192.168.49.100` (via MetalLB LoadBalancer)
- **MCP Server**: `http://localhost:8081` (local Python server)
- **ETL Service**: Internal to cluster

## 💬 Using with Claude Code

The MCP server allows you to query your financial data using natural language.

### Setup

The MCP server is already configured in `.mcp.json`. Just restart Claude Code after starting the server.

### Example Queries

Ask Claude Code:

**Accounts:**
- "Show me all my accounts and their balances"
- "What's my total balance across all accounts?"

**Transactions:**
- "Show me my last 20 transactions"
- "Find all Starbucks purchases"
- "Show me transactions over $100 from December 2025"

**Analytics:**
- "What did I spend by category in 2025?"
- "Show me my top 10 merchants by spending"
- "What's my cash flow for the last 6 months?"

### Available MCP Tools

1. **get_account_summary** - Account balances and statistics
2. **get_account_details** - Detailed account information
3. **get_transactions** - Query transactions with filters
4. **search_transactions** - Full-text search
5. **get_spending_by_category** - Category spending analysis
6. **get_merchant_spending** - Top merchants by spending
7. **get_cash_flow** - Income vs expenses over time
8. **get_budget_status** - Budget tracking

See [QUICKSTART-MCP.md](QUICKSTART-MCP.md) for detailed MCP setup and [MCP-WORKING.md](MCP-WORKING.md) for current status.

## 📁 Project Structure

```
personal-finance-dashboard/
├── backend/
│   ├── etl-service/           # CSV import service (FastAPI + pandas)
│   └── mcp-server/            # MCP server (Python + SSE)
│       ├── src/
│       │   ├── server.py      # Main MCP server
│       │   ├── database/      # Database connection
│       │   └── tools/         # MCP tools (accounts, transactions, analytics)
│       └── README.md
├── frontend/                   # React dashboard
├── database/
│   └── migrations/            # Database schema (PostgreSQL)
├── k8s/
│   └── base/                  # Kubernetes manifests
├── scripts/                   # Deployment and utility scripts
└── docs/
```

## 🛠️ Management Commands

### MCP Server

```bash
# Start MCP server (recommended)
./scripts/start-mcp-server.sh

# Stop MCP server
./scripts/stop-mcp-server.sh

# View logs
tail -f /tmp/mcp-server-local.log
```

### Kubernetes

```bash
# Check all services
kubectl get all

# View logs
kubectl logs -f -l app=postgres
kubectl logs -f -l app=etl-service
kubectl logs -f -l app=frontend

# Restart a service
kubectl rollout restart deployment/etl-service
```

### Database

```bash
# Access PostgreSQL (via port-forward)
kubectl port-forward svc/postgres 5432:5432 &
psql postgresql://finance_user:finance_dev_password_change_me@localhost:5432/finance_db

# Run migrations
./scripts/run-migrations.sh
```

## 📊 Current Data

- **Accounts**: 2 (American Express Platinum, Chase Hyatt)
- **Transactions**: 838 total
- **Date Range**: Through 2025-12-31
- **Categories**: Income, Expense, Transfer
- **Balance**: -$2,551.36 total

## 🔧 Development

### ETL Service

```bash
cd backend/etl-service
npm install
npm run dev
```

### Frontend

```bash
cd frontend
npm install
npm start
```

### MCP Server

```bash
cd backend/mcp-server
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## 📖 Documentation

- **[spec.md](spec.md)** - Complete technical specification
- **[QUICKSTART-MCP.md](QUICKSTART-MCP.md)** - MCP server setup guide
- **[MCP-WORKING.md](MCP-WORKING.md)** - Current MCP server status
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Kubernetes deployment guide
- **[MINIKUBE-ACCESS.md](MINIKUBE-ACCESS.md)** - Network access configuration
- **[backend/mcp-server/README.md](backend/mcp-server/README.md)** - MCP server details

## 🔒 Security Notes

This is configured for **local development only**:

- Default passwords in use (change for production)
- No authentication on MCP server
- Services exposed via MetalLB on local network
- Database credentials in Kubernetes secrets

## 🎯 Roadmap

- [ ] Machine learning auto-categorization
- [ ] Budget tracking and alerts
- [ ] Investment portfolio tracking
- [ ] Tax reporting features
- [ ] Mobile app (React Native)
- [ ] Direct bank API integration (Plaid)

## 📝 License

Personal project - Not licensed for distribution

## 🙏 Technologies Used

- **Backend**: Python (FastAPI), Node.js (Express)
- **Frontend**: React, TypeScript, Material-UI
- **Database**: PostgreSQL 15+
- **Infrastructure**: Kubernetes (minikube), Podman, MetalLB
- **MCP**: Model Context Protocol (SSE transport)
- **AI**: Claude Code integration

---

**Status**: ✅ Operational
**Last Updated**: 2026-02-15
**Version**: 0.2.0
