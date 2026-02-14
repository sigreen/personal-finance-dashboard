# Quick Start Guide

This guide will help you get the Personal Finance Dashboard up and running quickly.

## Prerequisites Check

Run this command to verify all prerequisites are installed:

```bash
make verify-setup
```

If anything is missing, refer to the [README.md](../README.md) for installation instructions.

## Setup Steps

### Step 1: Start Minikube Cluster

Use the automated setup script:

```bash
./scripts/setup-minikube.sh
```

Or use the Makefile:

```bash
make setup-minikube
```

This will:
- Start minikube with CRI-O runtime
- Enable MetalLB addon
- Enable storage provisioner
- Enable metrics server

### Step 2: Verify MetalLB Installation

MetalLB is automatically installed and configured by the setup script. Verify it's running:

```bash
# Check MetalLB pods
kubectl get pods -n metallb-system

# Check IP pool configuration
kubectl get ipaddresspool -n metallb-system
```

### Step 3: Verify Setup

```bash
# Check cluster status
kubectl cluster-info

# Check nodes
kubectl get nodes

# Check MetalLB is running
kubectl get pods -n metallb-system

# Check enabled addons
minikube addons list | grep enabled
```

You should see:
- ✅ minikube master running
- ✅ metallb-controller and metallb-speaker pods running
- ✅ metallb, storage-provisioner, metrics-server enabled

## Next Steps

Once the infrastructure is set up, proceed to Phase 2:

1. [Database Design & Deployment](database-setup.md)
2. [ETL Service Development](etl-service.md)
3. [Frontend Development](frontend.md)
4. [MCP Server Implementation](mcp-server.md)

## Common Issues

### Issue: Minikube won't start

**Solution:**
```bash
# Delete existing cluster and start fresh
minikube delete
minikube start --cpus=4 --memory=8192 --driver=podman --container-runtime=cri-o
```

### Issue: MetalLB pods not running

**Solution:**
```bash
# Check MetalLB status
kubectl get pods -n metallb-system

# Reinstall MetalLB
kubectl delete namespace metallb-system
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.14.9/config/manifests/metallb-native.yaml
kubectl wait --namespace metallb-system --for=condition=ready pod --selector=app=metallb --timeout=90s

# Reconfigure IP pool
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

### Issue: Out of disk space

**Solution:**
```bash
# Clean up unused Podman images
podman system prune -a

# Clean up minikube
minikube ssh "docker system prune -a"
```

### Issue: Podman command not found

**Solution:**
Install Podman for your distribution:

**Fedora/RHEL:**
```bash
sudo dnf install -y podman
```

**Ubuntu/Debian:**
```bash
sudo apt-get install -y podman
```

## Useful Commands

```bash
# View all resources
kubectl get all -A

# View cluster info
minikube status
kubectl cluster-info

# Access Kubernetes dashboard
minikube dashboard

# Get minikube IP
minikube ip

# SSH into minikube
minikube ssh

# View logs from a pod
kubectl logs <pod-name>

# Port forward a service
kubectl port-forward svc/<service-name> 8080:8080
```

## Development Workflow

1. **Make code changes**
2. **Build images**: `make build-all` or `./scripts/build-all.sh`
3. **Load into minikube**: `make load-images` or `./scripts/load-images.sh`
4. **Deploy**: `make deploy-all`
5. **Check status**: `make status`
6. **View logs**: `make logs-<service>`
7. **Get IPs**: `make get-ips`

## Testing

After deployment, test each component:

```bash
# Check PostgreSQL
make shell-db
# In psql shell: \dt

# Check ETL service
kubectl port-forward svc/etl-service 8080:8080
# Visit http://localhost:8080/docs

# Check MCP server
kubectl port-forward svc/mcp-server 8081:8081
# Test MCP connection

# Check Frontend
# Get LoadBalancer IP: make get-ips
# Visit http://<EXTERNAL-IP>
```

## Cleanup

To clean up the environment:

```bash
# Remove all deployments
make clean

# Stop minikube (preserves data)
minikube stop

# Complete cleanup (removes everything)
make clean-all
```

## Getting Help

- Review the [full specification](../spec.model)
- Check the [README](../README.md)
- Review Kubernetes logs: `kubectl logs <pod-name>`
- Check minikube logs: `minikube logs`
