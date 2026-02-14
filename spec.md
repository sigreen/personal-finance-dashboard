# Personal Finance Dashboard - Technical Specification

## Project Overview
A personal finance management system that imports financial data from CSV files (banking, brokerage, credit card statements), stores them in a normalized PostgreSQL database, and exposes the data through an MCP (Model Context Protocol) server for querying by Claude and other AI models.

## Architecture Overview

### High-Level Components
1. **Web UI** - Browser-based interface for initiating imports
2. **ETL Service** - Processes CSV files and imports data into database
3. **PostgreSQL Database** - Normalized financial data storage
4. **MCP Server** - Exposes financial data for AI model queries
5. **Kubernetes** - Orchestration platform (minikube for local development)
6. **File Storage** - Persistent volume for CSV uploads

### Data Flow
```
CSV Files → Web UI → ETL Service → PostgreSQL → MCP Server → Claude/AI Models
```
---

## Step-by-Step Implementation Plan

### Phase 1: Environment Setup & Infrastructure

#### Step 1.1: Initialize Project Repository
- Create project directory structure:
  ```
  personal-finance-dashboard/
  ├── backend/
  │   ├── etl-service/
  │   ├── mcp-server/
  │   └── shared/
  ├── frontend/
  ├── database/
  │   ├── migrations/
  │   └── schemas/
  ├── k8s/
  │   ├── dev/
  │   └── base/
  ├── containers/
  └── docs/
  ```
- Initialize git repository
- Create .gitignore (exclude CSV files, credentials, local configs)

#### Step 1.2: Setup Minikube & Kubernetes
- Install minikube
- Start minikube cluster: `minikube start --cpus=4 --memory=8192 --driver=podman --container-runtime=cri-o`
- Enable required addons:
  - `minikube addons enable metallb`
  - `minikube addons enable storage-provisioner`
  - `minikube addons enable metrics-server`
- Configure MetalLB IP address pool:
  - Get minikube IP range: `minikube ip`
  - Configure MetalLB: `minikube addons configure metallb`
  - Provide IP range (e.g., 192.168.49.100-192.168.49.110)
- Verify cluster: `kubectl cluster-info`

#### Step 1.3: Container Registry Setup
- Configure Podman to push images to minikube:
  - Option 1: Use minikube's image load: `minikube image load <image-name>`
  - Option 2: Set up local registry and configure minikube to use it
  - Option 3: Build directly in minikube: `eval $(minikube podman-env)`
- Verify Podman installation: `podman version`

---

### Phase 2: Database Design & Deployment

#### Step 2.1: Design Database Schema

**Core Tables:**

1. **accounts**
   - id (PK)
   - account_type (enum: checking, savings, credit_card, brokerage, loan)
   - institution_name
   - account_name
   - account_number_last4
   - currency (default: USD)
   - created_at
   - updated_at

2. **transactions**
   - id (PK)
   - account_id (FK)
   - transaction_date
   - post_date
   - description
   - amount (decimal)
   - transaction_type (enum: debit, credit)
   - category_id (FK, nullable)
   - merchant
   - notes
   - original_description
   - created_at
   - updated_at

3. **categories**
   - id (PK)
   - name
   - parent_category_id (FK, nullable - for subcategories)
   - category_type (enum: income, expense, transfer)
   - icon
   - color
   - created_at

4. **budgets**
   - id (PK)
   - category_id (FK)
   - amount
   - period (enum: monthly, quarterly, yearly)
   - start_date
   - end_date
   - created_at

5. **import_logs**
   - id (PK)
   - filename
   - account_id (FK)
   - import_status (enum: pending, processing, completed, failed)
   - rows_processed
   - rows_imported
   - rows_failed
   - error_details (jsonb)
   - started_at
   - completed_at

6. **holdings** (for brokerage accounts)
   - id (PK)
   - account_id (FK)
   - symbol
   - quantity
   - cost_basis
   - current_price
   - as_of_date
   - created_at

7. **csv_mapping_rules**
   - id (PK)
   - institution_name
   - account_type
   - column_mappings (jsonb)
   - date_format
   - amount_format
   - created_at

#### Step 2.2: Create Database Migrations
- Choose migration tool: Flyway, Liquibase, or Alembic (if using Python)
- Create initial schema migration files
- Add indexes on frequently queried columns:
  - transactions(account_id, transaction_date)
  - transactions(category_id)
  - accounts(institution_name)

#### Step 2.3: Deploy PostgreSQL on Kubernetes
- Create Kubernetes manifests:
  - **PersistentVolumeClaim** (PVC) for database storage
  - **ConfigMap** for PostgreSQL configuration
  - **Secret** for database credentials
  - **StatefulSet** for PostgreSQL deployment
  - **Service** for database access within cluster

- Apply manifests: `kubectl apply -f k8s/base/postgres/`
- Verify deployment: `kubectl get pods -l app=postgres`
- Run migrations to initialize schema

---

### Phase 3: ETL Service Development

#### Step 3.1: Design ETL Service Architecture
**Technology Stack:**
- Language: Python (with pandas for CSV processing) or Node.js
- Framework: FastAPI (Python) or Express.js (Node.js)
- Libraries: pandas, sqlalchemy, psycopg2

**Core Components:**
- File upload handler
- CSV parser and validator
- Data transformer (normalization, deduplication)
- Database loader
- Error handler and logger

#### Step 3.2: Implement CSV Parsing Logic
- Support multiple CSV formats from different institutions
- Detect CSV structure automatically or use mapping rules
- Handle various date formats (MM/DD/YYYY, DD/MM/YYYY, ISO 8601)
- Parse amount formats (negative for debits vs separate debit/credit columns)
- Extract merchant names from descriptions
- Validate required fields (date, amount, description)

#### Step 3.3: Implement Data Transformation
- Normalize transaction types (debit/credit)
- Standardize date formats
- Clean and deduplicate merchant names
- Detect duplicate transactions (same date, amount, description)
- Handle multi-currency transactions
- Auto-categorize transactions (using rule-based or ML approach)

#### Step 3.4: Implement Database Loading
- Batch insert for performance
- Transaction support (rollback on errors)
- Upsert logic for duplicate detection
- Create or link to existing accounts
- Update import_logs table with progress

#### Step 3.5: Create ETL API Endpoints
- POST /api/upload - Upload CSV file
- POST /api/import/{import_id}/process - Trigger import processing
- GET /api/import/{import_id}/status - Check import status
- GET /api/imports - List all imports
- POST /api/mapping-rules - Create/update CSV mapping rules
- GET /api/accounts - List accounts
- DELETE /api/transactions/{id} - Delete transaction (manual cleanup)

#### Step 3.6: Containerize ETL Service
- Create Containerfile (Dockerfile):
  - Base image (python:3.11-slim or node:20-alpine)
  - Install dependencies
  - Copy application code
  - Expose port (8080)
  - Define entrypoint
- Build image: `podman build -t finance-etl:latest ./backend/etl-service`
- Load into minikube: `minikube image load finance-etl:latest`
- Test locally before Kubernetes deployment: `podman run -p 8080:8080 finance-etl:latest`

#### Step 3.7: Deploy ETL Service to Kubernetes
- Create Kubernetes manifests:
  - **Deployment** with replica count, resource limits
  - **Service** (ClusterIP) for internal access
  - **ConfigMap** for application configuration
  - **Secret** for database credentials
  - **PersistentVolumeClaim** for CSV file storage
- Apply manifests: `kubectl apply -f k8s/base/etl-service/`

---

### Phase 4: Web Frontend Development

#### Step 4.1: Choose Frontend Technology
**Recommended Stack:**
- Framework: React with TypeScript or Vue.js
- UI Library: Material-UI, Ant Design, or Tailwind CSS
- State Management: React Context/Redux or Vuex
- File Upload: react-dropzone or similar
- Charts: Chart.js, Recharts, or D3.js

#### Step 4.2: Implement Core UI Components
1. **Dashboard View**
   - Account summary cards (balances, total assets/liabilities)
   - Recent transactions list
   - Spending by category (pie/donut chart)
   - Monthly spending trend (line chart)
   - Budget vs actual (bar chart)

2. **Import Page**
   - File upload dropzone (drag & drop)
   - Account selection dropdown
   - CSV preview table
   - Column mapping interface (if auto-detection fails)
   - Import progress indicator
   - Import history table

3. **Transactions Page**
   - Filterable/sortable transaction table
   - Search by description, merchant, amount
   - Date range picker
   - Category filter
   - Export to CSV
   - Manual categorization
   - Bulk operations

4. **Accounts Page**
   - Account list with balances
   - Add/edit/archive accounts
   - Account-specific transaction history

5. **Categories Page**
   - Category tree view
   - Add/edit/delete categories
   - Category rules management

6. **Budgets Page**
   - Budget creation/editing
   - Budget tracking visualization
   - Alerts for overspending

#### Step 4.3: Implement File Upload Flow
- Select account or create new account
- Upload CSV file to backend
- Display CSV preview with column detection
- Allow manual column mapping if needed
- Trigger import processing
- Show real-time progress updates (polling or WebSocket)
- Display import results (success/error counts)

#### Step 4.4: Containerize Frontend
- Create production build
- Create Containerfile (Dockerfile) with nginx to serve static files
- Build image: `podman build -t finance-frontend:latest ./frontend`
- Load into minikube: `minikube image load finance-frontend:latest`

#### Step 4.5: Deploy Frontend to Kubernetes
- Create Kubernetes manifests:
  - **Deployment** for frontend pods
  - **Service** (LoadBalancer) for external access via MetalLB
  - **ConfigMap** for nginx configuration
- Apply manifests: `kubectl apply -f k8s/base/frontend/`
- Get external IP: `kubectl get svc frontend-service`
- Access frontend via the LoadBalancer IP address (e.g., http://192.168.49.100)
- Optional: Add entry to /etc/hosts for friendly hostname (e.g., `192.168.49.100 finance.local`)

---

### Phase 5: MCP Server Implementation

#### Step 5.1: Understand MCP Protocol
- Review MCP specification at modelcontextprotocol.io
- Understand JSON-RPC 2.0 message format
- Study example MCP servers (SQLite, Filesystem, etc.)

#### Step 5.2: Design MCP Server Capabilities
**Exposed Tools:**
1. **get_account_summary**
   - Returns list of accounts with current balances
   - Parameters: date_range (optional)

2. **get_transactions**
   - Returns transactions with filters
   - Parameters: account_ids, start_date, end_date, category, min_amount, max_amount, search_query, limit, offset

3. **get_spending_by_category**
   - Returns aggregated spending grouped by category
   - Parameters: start_date, end_date, account_ids, category_type

4. **get_budget_status**
   - Returns budget vs actual spending
   - Parameters: period (current_month, current_quarter, current_year)

5. **search_transactions**
   - Full-text search across transactions
   - Parameters: query, account_ids, date_range

6. **get_merchant_spending**
   - Returns spending grouped by merchant
   - Parameters: start_date, end_date, top_n

7. **get_cash_flow**
   - Returns income vs expenses over time
   - Parameters: start_date, end_date, granularity (daily, weekly, monthly)

8. **get_net_worth_timeline**
   - Returns net worth over time (for brokerage accounts)
   - Parameters: start_date, end_date

**Exposed Resources:**
- accounts:// - List of all accounts
- transactions://recent - Recent transactions
- categories:// - Category hierarchy

**Exposed Prompts:**
- analyze-spending - Analyze spending patterns
- budget-recommendations - Suggest budget allocations
- expense-forecast - Forecast future expenses

#### Step 5.3: Implement MCP Server
**Technology Stack:**
- Language: Python or Node.js/TypeScript
- MCP SDK: Use official MCP SDK
- Database: PostgreSQL connection via sqlalchemy or pg

**Implementation Steps:**
1. Initialize MCP server with metadata
2. Implement database connection pool
3. Create SQL query builders for each tool
4. Implement tool handlers with parameter validation
5. Implement resource handlers
6. Implement prompt handlers
7. Add error handling and logging
8. Add connection lifecycle management

**Sample Server Structure (Python):**
```python
from mcp.server import Server
from mcp.types import Tool, Resource, Prompt

server = Server("personal-finance-mcp")

@server.tool()
async def get_transactions(
    account_ids: list[str] | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    category: str | None = None,
    limit: int = 100
):
    # Query database and return transactions
    pass

# Additional tools...
```

#### Step 5.4: Test MCP Server Locally
- Use MCP Inspector tool for testing
- Verify all tools work correctly
- Test with Claude Desktop or API
- Validate error handling

#### Step 5.5: Containerize MCP Server
- Create Containerfile (Dockerfile)
- Build image: `podman build -t finance-mcp:latest ./backend/mcp-server`
- Load into minikube: `minikube image load finance-mcp:latest`

#### Step 5.6: Deploy MCP Server to Kubernetes
- Create Kubernetes manifests:
  - **Deployment**
  - **Service** (ClusterIP for internal access, or LoadBalancer for external access via MetalLB)
  - **ConfigMap** for server configuration
  - **Secret** for database credentials
- For external access options:
  - **LoadBalancer service** with MetalLB (recommended for persistent external access)
  - **Port-forwarding** for local testing: `kubectl port-forward svc/mcp-server 8081:8081`
- Apply manifests: `kubectl apply -f k8s/base/mcp-server/`
- If using LoadBalancer, get external IP: `kubectl get svc mcp-server`

#### Step 5.7: Configure MCP Client Access
**Option 1: Claude Desktop**
- Update Claude Desktop MCP configuration
- Add server with stdio or HTTP transport
- For Kubernetes: use `kubectl port-forward` to expose locally

**Option 2: Direct API Access**
- Expose MCP server via LoadBalancer or NodePort
- Configure authentication (API key, OAuth)
- Update client configuration with server URL

---

### Phase 6: Integration & Testing

#### Step 6.1: End-to-End Testing
1. **Import Flow Test:**
   - Prepare sample CSV files from different institutions
   - Upload through web UI
   - Verify data in database
   - Check import_logs for success status

2. **MCP Query Test:**
   - Connect Claude to MCP server
   - Test each tool with various parameters
   - Verify responses match database state
   - Test error scenarios

3. **Dashboard Test:**
   - Verify all visualizations render correctly
   - Test filtering and search
   - Verify data accuracy

#### Step 6.2: Data Quality Validation
- Check for duplicate transactions
- Verify category assignments
- Validate date parsing (no future dates)
- Check amount calculations (debits as negative, credits as positive)
- Verify account balances match source statements

#### Step 6.3: Performance Testing
- Test large CSV imports (10k+ rows)
- Measure query response times
- Test concurrent imports
- Monitor database performance
- Check Kubernetes resource usage

#### Step 6.4: Security Testing
- Verify file upload restrictions (CSV only, size limits)
- Test SQL injection prevention
- Check authentication/authorization (if implemented)
- Validate input sanitization
- Test CORS configuration

---

### Phase 7: Production Readiness

#### Step 7.1: Add Monitoring & Logging
- **Logging:**
  - Structured logging (JSON format)
  - Log levels (DEBUG, INFO, WARNING, ERROR)
  - Log aggregation (ELK stack or Loki)

- **Monitoring:**
  - Deploy Prometheus for metrics collection
  - Configure Grafana dashboards
  - Monitor: CPU, memory, disk, database connections
  - Application metrics: import success rate, query latency

- **Alerting:**
  - Failed imports
  - Database connection errors
  - Disk space warnings

#### Step 7.2: Implement Backup Strategy
- **Database Backups:**
  - Automated pg_dump to persistent volume
  - Schedule daily backups (CronJob)
  - Test restore procedure

- **CSV File Backups:**
  - Retain original uploaded files
  - Consider archiving to S3-compatible storage

#### Step 7.3: Add Authentication & Authorization
- Implement user authentication (if multi-user)
- Options: OAuth2, JWT tokens, session-based
- Secure MCP server access
- Add API rate limiting

#### Step 7.4: Documentation
- **User Documentation:**
  - How to prepare CSV files
  - Import instructions
  - Troubleshooting guide
  - MCP query examples

- **Developer Documentation:**
  - Architecture diagrams
  - Database schema documentation
  - API documentation (OpenAPI/Swagger)
  - Deployment guide
  - Contributing guide

- **Operations Documentation:**
  - Kubernetes deployment guide
  - Backup and restore procedures
  - Monitoring and alerting setup
  - Troubleshooting runbook

#### Step 7.5: Create Deployment Scripts
- Makefile or shell scripts for common tasks:
  - Build all images (using Podman)
  - Load images into minikube
  - Deploy all services
  - Run database migrations
  - Tail logs
  - Port forwarding setup
  - Get LoadBalancer IPs
  - Cleanup/teardown

**Sample Makefile targets:**
```makefile
build-all:
	podman build -t finance-etl:latest ./backend/etl-service
	podman build -t finance-mcp:latest ./backend/mcp-server
	podman build -t finance-frontend:latest ./frontend

load-images:
	minikube image load finance-etl:latest
	minikube image load finance-mcp:latest
	minikube image load finance-frontend:latest

deploy-all:
	kubectl apply -f k8s/base/postgres/
	kubectl apply -f k8s/base/etl-service/
	kubectl apply -f k8s/base/mcp-server/
	kubectl apply -f k8s/base/frontend/

get-ips:
	@echo "Service IPs:"
	@kubectl get svc -o wide | grep LoadBalancer
```

---

### Phase 8: Enhancements (Future)

#### Step 8.1: Advanced Features
- **Machine Learning:**
  - Auto-categorization using ML models
  - Anomaly detection (fraud, unusual spending)
  - Spending predictions

- **Integrations:**
  - Direct bank API connections (Plaid, Yodlee)
  - Email parsing for e-receipts
  - Investment portfolio tracking with real-time prices

- **Advanced Analytics:**
  - Custom report builder
  - Tax reporting features
  - Investment performance metrics (IRR, CAGR)
  - Goal tracking (savings goals, debt payoff)

- **Mobile App:**
  - React Native or Flutter app
  - Same backend/MCP server

#### Step 8.2: Scalability Improvements
- Database read replicas
- Caching layer (Redis)
- Message queue for async processing (RabbitMQ, Kafka)
- Horizontal pod autoscaling

---

## Technology Stack Summary

### Backend
- **ETL Service:** Python 3.11+ with FastAPI, pandas, sqlalchemy
- **MCP Server:** Python with MCP SDK or TypeScript with @modelcontextprotocol/sdk
- **Database:** PostgreSQL 15+
- **Migration Tool:** Alembic (Python) or Flyway

### Frontend
- **Framework:** React 18+ with TypeScript
- **Build Tool:** Vite or Create React App
- **UI Library:** Material-UI or Tailwind CSS
- **Charts:** Recharts or Chart.js
- **HTTP Client:** axios or fetch

### Infrastructure
- **Orchestration:** Kubernetes (minikube for local)
- **Container Runtime:** Podman
- **Container Engine (minikube):** CRI-O
- **Load Balancer:** MetalLB
- **Monitoring:** Prometheus + Grafana
- **Logging:** Loki or ELK stack

---

## File Structure

```
personal-finance-dashboard/
├── backend/
│   ├── etl-service/
│   │   ├── src/
│   │   │   ├── api/
│   │   │   ├── parsers/
│   │   │   ├── transformers/
│   │   │   ├── loaders/
│   │   │   └── main.py
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── README.md
│   ├── mcp-server/
│   │   ├── src/
│   │   │   ├── tools/
│   │   │   ├── resources/
│   │   │   ├── database/
│   │   │   └── server.py
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── README.md
│   └── shared/
│       └── models/
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   └── App.tsx
│   ├── Dockerfile
│   ├── package.json
│   └── README.md
├── database/
│   ├── migrations/
│   │   ├── V001__initial_schema.sql
│   │   ├── V002__add_holdings.sql
│   │   └── ...
│   └── seeds/
│       └── categories.sql
├── k8s/
│   ├── base/
│   │   ├── postgres/
│   │   │   ├── statefulset.yaml
│   │   │   ├── service.yaml
│   │   │   ├── pvc.yaml
│   │   │   └── secrets.yaml
│   │   ├── etl-service/
│   │   │   ├── deployment.yaml
│   │   │   ├── service.yaml
│   │   │   └── configmap.yaml
│   │   ├── mcp-server/
│   │   │   ├── deployment.yaml
│   │   │   ├── service.yaml
│   │   │   └── configmap.yaml
│   │   └── frontend/
│   │       ├── deployment.yaml
│   │       └── service.yaml (LoadBalancer type)
│   └── overlays/
│       ├── dev/
│       └── prod/
├── scripts/
│   ├── build-all.sh
│   ├── deploy-all.sh
│   ├── port-forward.sh
│   └── backup-db.sh
├── docs/
│   ├── architecture.md
│   ├── user-guide.md
│   └── deployment.md
├── sample-data/
│   ├── chase-checking-sample.csv
│   ├── amex-sample.csv
│   └── vanguard-sample.csv
├── Makefile
├── README.md
└── .gitignore
```

---

## Development Timeline Estimate

**Phase 1:** Environment Setup - 1-2 days
**Phase 2:** Database Design - 2-3 days
**Phase 3:** ETL Service - 1-2 weeks
**Phase 4:** Web Frontend - 2-3 weeks
**Phase 5:** MCP Server - 1 week
**Phase 6:** Integration & Testing - 1 week
**Phase 7:** Production Readiness - 1 week

**Total:** 8-12 weeks for complete implementation

---

## Security Considerations

1. **Data Security:**
   - Encrypt sensitive data at rest (database encryption)
   - Use Kubernetes secrets for credentials
   - Implement RBAC in Kubernetes
   - Regular security updates for dependencies

2. **File Upload Security:**
   - Validate file types (CSV only)
   - Limit file sizes (e.g., 50MB max)
   - Scan for malware
   - Isolate file processing

3. **Database Security:**
   - Use connection pooling with limited connections
   - Parameterized queries (prevent SQL injection)
   - Regular backups with encryption
   - Database user with minimal privileges

4. **API Security:**
   - Input validation and sanitization
   - Rate limiting
   - CORS configuration
   - Authentication tokens with expiration

5. **MCP Server Security:**
   - Authenticate client connections
   - Validate all parameters
   - Limit query result sizes
   - Audit logging

---

## Getting Started Checklist

- [ ] Install Podman and podman-compose
- [ ] Install minikube and kubectl
- [ ] Start minikube cluster with CRI-O runtime
- [ ] Enable and configure MetalLB addon
- [ ] Initialize git repository
- [ ] Create project directory structure
- [ ] Design and document database schema
- [ ] Deploy PostgreSQL to Kubernetes
- [ ] Create sample CSV files for testing
- [ ] Implement basic ETL service
- [ ] Build simple web UI for file upload
- [ ] Test end-to-end import flow
- [ ] Implement MCP server with basic tools
- [ ] Test MCP server with Claude
- [ ] Add monitoring and logging
- [ ] Document deployment process
- [ ] Create backup strategy

---

## Resources & References

- **MCP Documentation:** https://modelcontextprotocol.io
- **Kubernetes Documentation:** https://kubernetes.io/docs/
- **Minikube Guide:** https://minikube.sigs.k8s.io/docs/
- **Podman Documentation:** https://docs.podman.io/
- **MetalLB Documentation:** https://metallb.universe.tf/
- **PostgreSQL Documentation:** https://www.postgresql.org/docs/
- **FastAPI Documentation:** https://fastapi.tiangolo.com/
- **React Documentation:** https://react.dev/

---

## Notes

- This specification assumes single-user deployment (local only)
- For production multi-user deployment, add authentication layer
- Consider data privacy regulations if storing financial data
- Keep CSV files in uploads directory as backup
- Use consistent date/currency formats throughout application
- Implement soft deletes for transactions (don't hard delete)
- Add audit trail for manual edits to transactions

### Podman Usage Notes
- Podman is used as a drop-in replacement for Docker (daemonless, rootless containers)
- Containerfiles are compatible with Dockerfiles (same syntax)
- Use `podman build`, `podman run`, `podman push` commands (same as Docker)
- To build images for minikube, use `minikube image load` after building with Podman
- Alternative: Use `eval $(minikube podman-env)` to build directly in minikube's environment
- Podman Desktop can be used as a GUI alternative

### MetalLB Usage Notes
- MetalLB provides LoadBalancer service type support for bare-metal/local Kubernetes
- Allocates external IPs from a configured IP pool
- Services with type=LoadBalancer will receive an IP from the MetalLB pool
- No need for Ingress controllers for simple external access
- For advanced routing (path-based, host-based), can still add Ingress controller on top of MetalLB
- Monitor IP allocation: `kubectl get svc -A` to see EXTERNAL-IP column
