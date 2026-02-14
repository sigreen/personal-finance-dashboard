.PHONY: help build-all load-images deploy-all get-ips clean logs-* setup-minikube

# Default target
help:
	@echo "Personal Finance Dashboard - Makefile Commands"
	@echo ""
	@echo "Setup Commands:"
	@echo "  make setup-minikube    - Start and configure minikube cluster"
	@echo "  make verify-setup      - Verify minikube and prerequisites"
	@echo ""
	@echo "Build Commands:"
	@echo "  make build-all         - Build all container images with Podman"
	@echo "  make build-etl         - Build ETL service image"
	@echo "  make build-mcp         - Build MCP server image"
	@echo "  make build-frontend    - Build frontend image"
	@echo ""
	@echo "Deploy Commands:"
	@echo "  make load-images       - Load all images into minikube"
	@echo "  make deploy-all        - Deploy all services to Kubernetes"
	@echo "  make deploy-db         - Deploy PostgreSQL"
	@echo "  make run-migrations    - Run database migrations"
	@echo "  make build-migration   - Build migration container image"
	@echo "  make deploy-etl        - Deploy ETL service"
	@echo "  make deploy-mcp        - Deploy MCP server"
	@echo "  make deploy-frontend   - Deploy frontend"
	@echo ""
	@echo "Info Commands:"
	@echo "  make get-ips           - Show all LoadBalancer IPs"
	@echo "  make status            - Show status of all pods and services"
	@echo "  make logs-etl          - Tail ETL service logs"
	@echo "  make logs-mcp          - Tail MCP server logs"
	@echo "  make logs-frontend     - Tail frontend logs"
	@echo "  make logs-db           - Tail PostgreSQL logs"
	@echo ""
	@echo "Utility Commands:"
	@echo "  make port-forward-mcp  - Port forward MCP server to localhost:8081"
	@echo "  make shell-db          - Open psql shell in database pod"
	@echo "  make clean             - Delete all deployments"
	@echo "  make clean-all         - Stop minikube and clean everything"
	@echo ""

# Setup minikube cluster
setup-minikube:
	@echo "Configuring minikube for rootless Podman..."
	@minikube config set rootless true
	@echo "Starting minikube cluster..."
	minikube start --cpus=4 --memory=8192 --driver=podman --container-runtime=cri-o
	@echo ""
	@echo "Enabling storage provisioner..."
	minikube addons enable storage-provisioner || true
	@echo ""
	@echo "Installing metrics-server (manual installation)..."
	@kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml >/dev/null
	@echo "Patching metrics-server for minikube..."
	@kubectl patch deployment metrics-server -n kube-system --type='json' -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]' >/dev/null
	@echo ""
	@echo "Installing MetalLB (manual installation)..."
	@kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.14.9/config/manifests/metallb-native.yaml
	@echo "Waiting for MetalLB deployment to be created..."
	@until kubectl get deployment -n metallb-system controller >/dev/null 2>&1; do sleep 1; done
	@echo "Waiting for MetalLB to be ready..."
	@kubectl rollout status deployment/controller -n metallb-system --timeout=90s
	@kubectl rollout status daemonset/speaker -n metallb-system --timeout=90s
	@echo ""
	@echo "Configuring MetalLB IP pool..."
	@MINIKUBE_IP=$$(minikube ip); \
	IP_PREFIX=$$(echo $$MINIKUBE_IP | cut -d'.' -f1-3); \
	printf 'apiVersion: metallb.io/v1beta1\nkind: IPAddressPool\nmetadata:\n  name: default-pool\n  namespace: metallb-system\nspec:\n  addresses:\n  - %s.100-%s.110\n---\napiVersion: metallb.io/v1beta1\nkind: L2Advertisement\nmetadata:\n  name: default\n  namespace: metallb-system\nspec:\n  ipAddressPools:\n  - default-pool\n' "$$IP_PREFIX" "$$IP_PREFIX" | kubectl apply -f - >/dev/null
	@echo ""
	@echo "======================================"
	@echo "✓ Setup Complete!"
	@echo "======================================"
	@echo ""
	@echo "Minikube IP: $$(minikube ip)"
	@echo "MetalLB IP range: $$(minikube ip | cut -d'.' -f1-3).100-$$(minikube ip | cut -d'.' -f1-3).110"
	@echo ""
	@echo "Verify setup with:"
	@echo "  make verify-setup"
	@echo ""

# Verify setup
verify-setup:
	@echo "Checking prerequisites..."
	@which podman > /dev/null || (echo "ERROR: Podman not found" && exit 1)
	@which minikube > /dev/null || (echo "ERROR: Minikube not found" && exit 1)
	@which kubectl > /dev/null || (echo "ERROR: kubectl not found" && exit 1)
	@echo "✓ Podman: $$(podman --version)"
	@echo "✓ Minikube: $$(minikube version --short)"
	@echo "✓ kubectl: $$(kubectl version --client --short 2>/dev/null || echo 'installed')"
	@echo ""
	@echo "Checking minikube status..."
	@if minikube status >/dev/null 2>&1; then \
		echo "✓ Minikube is running"; \
		echo ""; \
		echo "Checking addons..."; \
		minikube addons list | grep -E "metallb|storage-provisioner|metrics-server"; \
		echo ""; \
		echo "✓ Setup verification complete!"; \
	else \
		echo "✗ Minikube not running. Run 'make setup-minikube' to start it."; \
		echo ""; \
	fi

# Build all images
build-all: build-etl build-mcp build-frontend

build-etl:
	@echo "Building ETL service image..."
	@if [ -f backend/etl-service/Containerfile ]; then \
		podman build -t finance-etl:latest ./backend/etl-service; \
	else \
		echo "Containerfile not found. Skipping ETL service build."; \
	fi

build-mcp:
	@echo "Building MCP server image..."
	@if [ -f backend/mcp-server/Containerfile ]; then \
		podman build -t finance-mcp:latest ./backend/mcp-server; \
	else \
		echo "Containerfile not found. Skipping MCP server build."; \
	fi

build-frontend:
	@echo "Building frontend image..."
	@if [ -f frontend/Containerfile ]; then \
		podman build -t finance-frontend:latest ./frontend; \
	else \
		echo "Containerfile not found. Skipping frontend build."; \
	fi

# Load images into minikube
load-images:
	@echo "Loading images into minikube..."
	@if podman images | grep -q finance-etl; then \
		minikube image load finance-etl:latest; \
	fi
	@if podman images | grep -q finance-mcp; then \
		minikube image load finance-mcp:latest; \
	fi
	@if podman images | grep -q finance-frontend; then \
		minikube image load finance-frontend:latest; \
	fi
	@echo "Verifying loaded images..."
	@minikube image ls | grep finance || echo "No finance images found"

# Deploy all services
deploy-all: deploy-db deploy-etl deploy-mcp deploy-frontend

deploy-db:
	@echo "Deploying PostgreSQL..."
	@./scripts/deploy-database.sh

run-migrations:
	@echo "Running database migrations..."
	@./scripts/run-migrations.sh

build-migration:
	@echo "Building migration container..."
	@podman build -t localhost/finance-db-migration:latest -f database/Containerfile database/
	@echo "Loading image into minikube..."
	@podman save localhost/finance-db-migration:latest -o /tmp/finance-db-migration.tar
	@minikube image load /tmp/finance-db-migration.tar
	@rm /tmp/finance-db-migration.tar

deploy-etl:
	@echo "Deploying ETL service..."
	@if [ -d k8s/base/etl-service ]; then \
		kubectl apply -f k8s/base/etl-service/; \
	else \
		echo "ETL service manifests not found. Skipping."; \
	fi

deploy-mcp:
	@echo "Deploying MCP server..."
	@if [ -d k8s/base/mcp-server ]; then \
		kubectl apply -f k8s/base/mcp-server/; \
	else \
		echo "MCP server manifests not found. Skipping."; \
	fi

deploy-frontend:
	@echo "Deploying frontend..."
	@if [ -d k8s/base/frontend ]; then \
		kubectl apply -f k8s/base/frontend/; \
	else \
		echo "Frontend manifests not found. Skipping."; \
	fi

# Get LoadBalancer IPs
get-ips:
	@echo "Service LoadBalancer IPs:"
	@echo "=========================="
	@kubectl get svc --all-namespaces -o wide | grep LoadBalancer || echo "No LoadBalancer services found"

# Show status
status:
	@echo "Pods Status:"
	@echo "============"
	@kubectl get pods -A
	@echo ""
	@echo "Services:"
	@echo "========="
	@kubectl get svc -A
	@echo ""
	@echo "PersistentVolumeClaims:"
	@echo "======================="
	@kubectl get pvc -A

# Log commands
logs-etl:
	@kubectl logs -f -l app=etl-service --tail=100

logs-mcp:
	@kubectl logs -f -l app=mcp-server --tail=100

logs-frontend:
	@kubectl logs -f -l app=frontend --tail=100

logs-db:
	@kubectl logs -f -l app=postgres --tail=100

# Port forwarding
port-forward-mcp:
	@echo "Port forwarding MCP server to localhost:8081..."
	@kubectl port-forward svc/mcp-server 8081:8081

port-forward-etl:
	@echo "Port forwarding ETL service to localhost:8080..."
	@kubectl port-forward svc/etl-service 8080:8080

# Database shell
shell-db:
	@kubectl exec -it $$(kubectl get pod -l app=postgres -o jsonpath='{.items[0].metadata.name}') -- psql -U postgres

# Clean up
clean:
	@echo "Deleting all deployments..."
	-kubectl delete all --all
	-kubectl delete pvc --all
	@echo "Cleanup complete"

clean-all: clean
	@echo "Stopping minikube..."
	minikube stop
	@echo "Deleting minikube cluster..."
	minikube delete
	@echo "Complete cleanup done"

# Development helpers
dev-env:
	@echo "Setting up development environment..."
	@echo ""
	@echo "Minikube IP: $$(minikube ip)"
	@echo ""
	@echo "Add to /etc/hosts:"
	@echo "$$(minikube ip) finance.local"
	@echo ""
	@echo "To use minikube's Podman environment:"
	@echo "eval \$$(minikube podman-env)"
