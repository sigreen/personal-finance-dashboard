# Personal Finance Dashboard

A personal finance management system that imports financial data from CSV files, stores them in a PostgreSQL database, and exposes the data through an MCP (Model Context Protocol) server for querying by Claude and other AI models.

## TL;DR - Quick Start

```bash
# 1. Verify prerequisites are installed
make verify-setup

# 2. Set up the infrastructure (one command!)
make setup-minikube

# 3. That's it! You're ready for Phase 2
```

**What this does:**
- Configures and starts minikube with rootless Podman
- Installs MetalLB load balancer
- Configures IP address pool automatically
- Sets up storage provisioner

**Next:** Follow the [spec.md](spec.md) to implement Phase 2 (Database) and beyond.

---

## Architecture

- **Web UI**: React-based interface for CSV uploads and data visualization
- **ETL Service**: Python/FastAPI service for CSV parsing and data import
- **PostgreSQL Database**: Normalized financial data storage
- **MCP Server**: Exposes financial data tools for AI model queries
- **Kubernetes**: Orchestration platform (minikube for local development)

## Technology Stack

- **Container Runtime**: Podman
- **Orchestration**: Kubernetes (minikube with CRI-O)
- **Load Balancer**: MetalLB
- **Backend**: Python 3.11+ with FastAPI
- **Frontend**: React 18+ with TypeScript
- **Database**: PostgreSQL 15+

## Prerequisites

Before you begin, ensure you have the following installed:

- **Podman** (4.0+): [Installation Guide](https://podman.io/getting-started/installation)
- **Minikube** (1.30+): [Installation Guide](https://minikube.sigs.k8s.io/docs/start/)
- **kubectl**: [Installation Guide](https://kubernetes.io/docs/tasks/tools/)
- **Python** (3.11+): For backend development
- **Node.js** (18+): For frontend development

## Available Scripts

The project includes several utility scripts in the `scripts/` directory:

### Setup Scripts

- **`./scripts/setup-minikube.sh`** - Complete automated setup (minikube + MetalLB)
- **`./scripts/build-all.sh`** - Build all container images with Podman
- **`./scripts/load-images.sh`** - Load built images into minikube

### Usage Examples

```bash
# Complete infrastructure setup
./scripts/setup-minikube.sh

# Build all services
./scripts/build-all.sh

# Load images into minikube
./scripts/load-images.sh
```

### Network Access Scripts

- **`sudo ./scripts/enable-metallb.sh`** - Enable MetalLB LoadBalancer access (includes nginx reverse proxy for home network)
- **`sudo ./scripts/disable-metallb.sh`** - Disable LoadBalancer access and clean up
- **`./scripts/setup-nginx-reverse-proxy.sh`** - Set up nginx reverse proxy only (standalone)
- **`./scripts/remove-nginx-reverse-proxy.sh`** - Remove nginx reverse proxy

#### Accessing the Dashboard

After deploying the frontend and running `enable-metallb.sh`, you can access the dashboard:

**Local Access:**
```bash
# Access via MetalLB LoadBalancer IP
http://192.168.49.100/
```

**Home Network Access:**
```bash
# Access from any device on your local network (e.g., phone, tablet, another computer)
http://11.11.2.65:8080/
```

The `enable-metallb.sh` script automatically sets up:
1. Dummy network interface for MetalLB IP
2. SSH tunnel through minikube
3. iptables rules for routing
4. Nginx reverse proxy for home network access on port 8080

## Makefile Commands

A comprehensive Makefile is provided for all common operations:

### Setup Commands
```bash
make setup-minikube    # Start and configure minikube cluster
make verify-setup      # Verify prerequisites and setup
```

### Build Commands
```bash
make build-all         # Build all container images
make build-etl         # Build ETL service only
make build-mcp         # Build MCP server only
make build-frontend    # Build frontend only
```

### Deploy Commands
```bash
make load-images       # Load all images into minikube
make deploy-all        # Deploy all services to Kubernetes
make deploy-db         # Deploy PostgreSQL only
make deploy-etl        # Deploy ETL service only
make deploy-mcp        # Deploy MCP server only
make deploy-frontend   # Deploy frontend only
```

### Info Commands
```bash
make get-ips           # Show all LoadBalancer IPs
make status            # Show status of all pods and services
```

### Log Commands
```bash
make logs-etl          # Tail ETL service logs
make logs-mcp          # Tail MCP server logs
make logs-frontend     # Tail frontend logs
make logs-db           # Tail PostgreSQL logs
```

### Utility Commands
```bash
make port-forward-mcp  # Port forward MCP server to localhost:8081
make shell-db          # Open psql shell in database pod
make clean             # Delete all deployments
make clean-all         # Stop minikube and clean everything
```

### Get Help
```bash
make help              # Show all available commands
```

## Project Structure

```
personal-finance-dashboard/
├── backend/
│   ├── etl-service/          # CSV import and processing service
│   ├── mcp-server/           # MCP server for AI queries
│   └── shared/               # Shared models and utilities
├── frontend/                 # React web application
├── database/
│   ├── migrations/           # Database schema migrations
│   └── seeds/                # Initial data (categories, etc.)
├── k8s/
│   ├── base/                 # Base Kubernetes manifests
│   └── overlays/             # Environment-specific configs
├── containers/               # Containerfiles
├── scripts/                  # Utility scripts
├── docs/                     # Documentation
└── sample-data/              # Sample CSV files for testing
```

## Next Steps

1. **Phase 2**: Design and deploy PostgreSQL database
2. **Phase 3**: Develop ETL service
3. **Phase 4**: Build web frontend
4. **Phase 5**: Implement MCP server
5. **Phase 6**: Integration testing
6. **Phase 7**: Production readiness (monitoring, backups, etc.)

See `spec.md` for detailed implementation plan.

## Common Commands

### Minikube Management
```bash
# Start minikube
minikube start

# Stop minikube
minikube stop

# Delete cluster
minikube delete

# Access minikube dashboard
minikube dashboard

# SSH into minikube
minikube ssh
```

### Kubernetes Operations
```bash
# View all resources
kubectl get all -A

# View services with external IPs
kubectl get svc -A

# View pods
kubectl get pods -A

# View logs
kubectl logs -f <pod-name>

# Port forward a service
kubectl port-forward svc/<service-name> 8080:8080

# Execute command in pod
kubectl exec -it <pod-name> -- /bin/bash
```

### Podman Commands
```bash
# Build an image
podman build -t <image-name>:<tag> <path>

# List images
podman images

# Run a container
podman run -p 8080:8080 <image-name>

# List running containers
podman ps

# Stop a container
podman stop <container-id>

# Remove an image
podman rmi <image-name>
```

## Troubleshooting

### Minikube won't start
```bash
# Delete and recreate
minikube delete
make setup-minikube
# OR
./scripts/setup-minikube.sh
```

### Images not found in minikube
```bash
# Verify images are loaded
minikube image ls

# Reload image
minikube image load <image-name>
```

### MetalLB not assigning IPs
```bash
# Check MetalLB pods
kubectl get pods -n metallb-system

# Check IP address pool configuration
kubectl get ipaddresspool -n metallb-system

# Reinstall MetalLB if needed
kubectl delete namespace metallb-system
make setup-minikube
```

### Services pending external IP
```bash
# Check MetalLB pods
kubectl get pods -n metallb-system

# Check service
kubectl describe svc <service-name>
```

## Documentation

- [Full Specification](spec.md) - Complete technical specification
- [Quick Start Guide](docs/quick-start.md) - Fast setup and common tasks
- [Architecture Docs](docs/architecture.md) - System architecture details (to be created)
- [Database Schema](docs/database-schema.md) - Database design (to be created)
- [API Documentation](docs/api.md) - REST API endpoints (to be created)
- [MCP Tools](docs/mcp-tools.md) - Available MCP tools and usage (to be created)

## Contributing

This is a personal project for local deployment. For production use:
- Add authentication and authorization
- Implement multi-tenancy
- Add data encryption
- Comply with financial data regulations (PCI-DSS, etc.)

## License

This project is for personal use. See LICENSE file for details.

## Security Notice

This application handles sensitive financial data. Ensure:
- Kubernetes secrets are properly configured
- CSV files are not committed to version control
- Database credentials are secure
- Services are not exposed to public internet without authentication
- Regular backups of financial data
