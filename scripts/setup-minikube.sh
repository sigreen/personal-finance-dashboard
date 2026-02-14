#!/bin/bash

set -e

echo "======================================"
echo "Personal Finance Dashboard Setup"
echo "======================================"
echo ""

# Check prerequisites
echo "Checking prerequisites..."
command -v podman >/dev/null 2>&1 || { echo "ERROR: Podman is not installed. Please install Podman first."; exit 1; }
command -v minikube >/dev/null 2>&1 || { echo "ERROR: Minikube is not installed. Please install Minikube first."; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo "ERROR: kubectl is not installed. Please install kubectl first."; exit 1; }

echo "✓ Podman installed: $(podman --version)"
echo "✓ Minikube installed: $(minikube version --short)"
echo "✓ kubectl installed"
echo ""

# Start minikube
echo "Starting minikube cluster with Podman driver and CRI-O runtime..."
minikube start --cpus=4 --memory=8192 --driver=podman --container-runtime=cri-o

echo ""
echo "✓ Minikube cluster started"
echo ""

# Enable MetalLB
echo "Enabling MetalLB addon..."
minikube addons enable metallb

echo ""
echo "✓ MetalLB enabled"
echo ""

# Enable storage provisioner
echo "Enabling storage provisioner..."
minikube addons enable storage-provisioner

echo ""
echo "✓ Storage provisioner enabled"
echo ""

# Enable metrics server
echo "Enabling metrics server..."
minikube addons enable metrics-server

echo ""
echo "✓ Metrics server enabled"
echo ""

# Get minikube IP
MINIKUBE_IP=$(minikube ip)
echo "Minikube IP: $MINIKUBE_IP"
echo ""

# Calculate IP range for MetalLB
IP_PREFIX=$(echo $MINIKUBE_IP | cut -d'.' -f1-3)
IP_START="${IP_PREFIX}.100"
IP_END="${IP_PREFIX}.110"

echo "======================================"
echo "MetalLB Configuration Required"
echo "======================================"
echo ""
echo "Please configure MetalLB with the following command:"
echo ""
echo "  minikube addons configure metallb"
echo ""
echo "When prompted, enter:"
echo "  Start IP: $IP_START"
echo "  End IP:   $IP_END"
echo ""
echo "Or run this command to configure automatically:"
echo ""
echo "  kubectl create configmap config -n metallb-system --from-literal=config='"
echo "  apiVersion: v1"
echo "  kind: ConfigMap"
echo "  metadata:"
echo "    namespace: metallb-system"
echo "    name: config"
echo "  data:"
echo "    config: |"
echo "      address-pools:"
echo "      - name: default"
echo "        protocol: layer2"
echo "        addresses:"
echo "        - $IP_START-$IP_END'"
echo ""
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "Cluster Information:"
kubectl cluster-info
echo ""
echo "Enabled Addons:"
minikube addons list | grep enabled
echo ""
echo "Next Steps:"
echo "1. Configure MetalLB (see above)"
echo "2. Proceed to Phase 2: Database Design & Deployment"
echo ""
