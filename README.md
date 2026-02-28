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

- **k3d** (Kubernetes in Docker)
- **kubectl**
- **podman** or **docker**
- **Python 3.11+**
- **Node.js 18+**

### 1. Build and Deploy to Kubernetes

```bash
# Build container images and import into k3d
./scripts/build-k3d.sh

# Deploy all services to Kubernetes
./scripts/deploy-k3d.sh
```

This will deploy:
- PostgreSQL database
- ETL Service (CSV import)
- Frontend (React dashboard)
- MCP Server (in Kubernetes)

### 2. Access Services

- **Web Dashboard**: `http://finance.local` (via Gateway API)
- **MCP Server**: `http://finance-mcp.localtest.me:8080/mcp` (for Claude Code)
- **ETL Service**: Internal to cluster

## 💬 Using with Claude Code

The MCP server allows you to query your financial data using natural language.

### Setup

The MCP server runs in Kubernetes and is accessible at `http://finance-mcp.localtest.me:8080/mcp`. Configure it in your Claude Code settings to connect.

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

### Kubernetes

```bash
# Check all services
kubectl get all -n personal-finance

# View logs
kubectl logs -f -l app=postgres -n personal-finance
kubectl logs -f -l app=etl-service -n personal-finance
kubectl logs -f -l app=frontend -n personal-finance

# Restart a service
kubectl rollout restart deployment/etl-service -n personal-finance
```

### Database

```bash
# Access PostgreSQL (via port-forward)
kubectl port-forward svc/postgres 5432:5432 -n personal-finance &
psql postgresql://finance_user:finance_dev_password_change_me@localhost:5432/finance_db
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
- **[backend/mcp-server/README.md](backend/mcp-server/README.md)** - MCP server details

## 🔒 Security Notes

This is configured for **local development only**:

- Default passwords in use (change for production)
- No authentication on local MCP server
- Services exposed via Gateway API
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
- **Infrastructure**: Kubernetes (k3d), Podman/Docker
- **MCP**: Model Context Protocol (SSE transport)
- **AI**: Claude Code integration

---

**Status**: ✅ Operational
**Last Updated**: 2026-02-27
**Version**: 0.3.0
