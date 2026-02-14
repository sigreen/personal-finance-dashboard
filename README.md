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

### Installation Commands

#### Fedora/RHEL
```bash
# Install Podman
sudo dnf install -y podman podman-compose

# Install kubectl
sudo dnf install -y kubectl

# Install minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-latest.x86_64.rpm
sudo rpm -Uvh minikube-latest.x86_64.rpm
```

#### Ubuntu/Debian
```bash
# Install Podman
sudo apt-get update
sudo apt-get -y install podman

# Install kubectl
sudo apt-get install -y kubectl

# Install minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube_latest_amd64.deb
sudo dpkg -i minikube_latest_amd64.deb
```

## Quick Setup (Recommended)

### Option 1: Automated Setup Script

The easiest way to get started:

```bash
# Run the automated setup script
./scripts/setup-minikube.sh
```

This script will:
- Configure minikube for rootless Podman
- Start minikube cluster with Podman driver and CRI-O runtime
- Enable storage provisioner
- Install and configure MetalLB (manual installation)
- Configure IP address pool automatically

### Option 2: Using Makefile

```bash
# Run complete setup
make setup-minikube

# Verify everything is working
make verify-setup
```

The Makefile provides the same automated setup as the script, plus additional commands for building, deploying, and managing the application.

### Verify Setup

After running either setup method:

```bash
# Check cluster status
kubectl cluster-info

# Check MetalLB installation
kubectl get pods -n metallb-system
kubectl get ipaddresspool -n metallb-system

# Check all resources
kubectl get all -A
```

You should see:
- ✅ Minikube cluster running
- ✅ MetalLB controller and speaker pods running
- ✅ IP address pool configured (e.g., 192.168.49.100-192.168.49.110)

---

## Manual Setup (Alternative)

If you prefer to set up each component manually:

### 1. Configure Rootless Podman

```bash
minikube config set rootless true
```

### 2. Start Minikube

```bash
# Start minikube with Podman driver and CRI-O container runtime
minikube start --cpus=4 --memory=8192 --driver=podman --container-runtime=cri-o

# Verify cluster is running
kubectl cluster-info
```

### 3. Install and Configure MetalLB

```bash
# Install MetalLB
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.14.9/config/manifests/metallb-native.yaml

# Wait for deployment to be created
until kubectl get deployment -n metallb-system controller >/dev/null 2>&1; do sleep 1; done

# Wait for MetalLB to be ready
kubectl rollout status deployment/controller -n metallb-system --timeout=90s
kubectl rollout status daemonset/speaker -n metallb-system --timeout=90s

# Configure IP pool (auto-detects minikube IP range)
MINIKUBE_IP=$(minikube ip)
IP_PREFIX=$(echo $MINIKUBE_IP | cut -d'.' -f1-3)

cat <<EOF | kubectl apply -f -
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: default-pool
  namespace: metallb-system
spec:
  addresses:
  - ${IP_PREFIX}.100-${IP_PREFIX}.110
---
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: default
  namespace: metallb-system
spec:
  ipAddressPools:
  - default-pool
EOF
```

---

## Working with Podman and Minikube

### Configure Podman for Minikube

You have three options to use Podman with minikube:

#### Option A: Build and Load (Recommended for development)
```bash
# Build images with Podman
podman build -t finance-etl:latest ./backend/etl-service

# Load into minikube
minikube image load finance-etl:latest
```

#### Option B: Build Directly in Minikube Environment
```bash
# Set environment to use minikube's container runtime
eval $(minikube podman-env)

# Build images (they'll be available directly in minikube)
podman build -t finance-etl:latest ./backend/etl-service
```

#### Option C: Use Local Registry
```bash
# Start a local registry
podman run -d -p 5000:5000 --name registry registry:2

# Tag and push images
podman build -t localhost:5000/finance-etl:latest ./backend/etl-service
podman push localhost:5000/finance-etl:latest
```

---

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
