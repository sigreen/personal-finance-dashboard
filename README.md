# Personal Finance Dashboard

A personal finance management system that imports financial data from CSV files, stores them in a PostgreSQL database, and exposes the data through an MCP (Model Context Protocol) server for querying by Claude and other AI models.

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

## Setup Instructions

### 1. Clone and Navigate to Repository

```bash
cd /home/simon/Workspace/personal-finance-dashboard
```

### 2. Start Minikube with CRI-O Runtime

```bash
# Start minikube with CRI-O container runtime
minikube start --cpus=4 --memory=8192 --container-runtime=cri-o

# Verify cluster is running
kubectl cluster-info
```

### 3. Enable and Configure MetalLB

```bash
# Enable MetalLB addon
minikube addons enable metallb

# Get minikube IP to determine IP range
minikube ip

# Configure MetalLB (interactive)
minikube addons configure metallb
# Enter IP range when prompted (e.g., 192.168.49.100-192.168.49.110)
```

### 4. Enable Other Required Addons

```bash
# Enable storage provisioner
minikube addons enable storage-provisioner

# Enable metrics server
minikube addons enable metrics-server

# Verify addons
minikube addons list
```

### 5. Configure Podman for Minikube

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

### 6. Verify Setup

```bash
# Check cluster status
kubectl get nodes

# Check enabled addons
minikube addons list | grep enabled

# Verify MetalLB is running
kubectl get pods -n metallb-system

# Check available storage classes
kubectl get sc
```

## Quick Start with Makefile

A Makefile is provided for common operations:

```bash
# Build all container images
make build-all

# Load images into minikube
make load-images

# Deploy all services
make deploy-all

# Get LoadBalancer IPs
make get-ips

# View logs
make logs-etl
make logs-mcp
make logs-frontend

# Clean up
make clean
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

See `spec.model` for detailed implementation plan.

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
minikube start --cpus=4 --memory=8192 --container-runtime=cri-o
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
# Check MetalLB configuration
kubectl get configmap -n metallb-system config -o yaml

# Reconfigure MetalLB
minikube addons disable metallb
minikube addons enable metallb
minikube addons configure metallb
```

### Services pending external IP
```bash
# Check MetalLB pods
kubectl get pods -n metallb-system

# Check service
kubectl describe svc <service-name>
```

## Documentation

- [Full Specification](spec.model) - Complete technical specification
- [Architecture Docs](docs/architecture.md) - System architecture details
- [Database Schema](docs/database-schema.md) - Database design
- [API Documentation](docs/api.md) - REST API endpoints
- [MCP Tools](docs/mcp-tools.md) - Available MCP tools and usage

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
