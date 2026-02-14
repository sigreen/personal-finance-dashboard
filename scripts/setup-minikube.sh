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

# Configure rootless Podman
echo "Configuring minikube for rootless Podman..."
minikube config set rootless true

# Start minikube
echo "Starting minikube cluster with Podman driver and CRI-O runtime..."
minikube start --cpus=4 --memory=8192 --driver=podman --container-runtime=cri-o

echo ""
echo "✓ Minikube cluster started"
echo ""

# Enable storage provisioner
echo "Enabling storage provisioner..."
minikube addons enable storage-provisioner || true

echo ""
echo "✓ Storage provisioner enabled"
echo ""

# Install metrics-server manually (addon doesn't work with rootless Podman)
echo "Installing metrics-server (manual installation)..."
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml >/dev/null

echo "Patching metrics-server for minikube..."
kubectl patch deployment metrics-server -n kube-system --type='json' -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]' >/dev/null

echo ""
echo "✓ Metrics-server installed"
echo ""

# Install MetalLB manually (addon doesn't work with rootless Podman)
echo "Installing MetalLB (manual installation)..."
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.14.9/config/manifests/metallb-native.yaml

echo ""
echo "Waiting for MetalLB deployment to be created..."
until kubectl get deployment -n metallb-system controller >/dev/null 2>&1; do sleep 1; done

echo "Waiting for MetalLB to be ready..."
kubectl rollout status deployment/controller -n metallb-system --timeout=90s
kubectl rollout status daemonset/speaker -n metallb-system --timeout=90s

echo ""
echo "✓ MetalLB installed"
echo ""

# Get minikube IP and configure MetalLB
MINIKUBE_IP=$(minikube ip)
IP_PREFIX=$(echo $MINIKUBE_IP | cut -d'.' -f1-3)
IP_START="${IP_PREFIX}.100"
IP_END="${IP_PREFIX}.110"

echo "Configuring MetalLB IP pool..."

cat <<EOF | kubectl apply -f -
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: default-pool
  namespace: metallb-system
spec:
  addresses:
  - ${IP_START}-${IP_END}
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

echo ""
echo "✓ MetalLB configured with IP range: ${IP_START}-${IP_END}"
echo ""

echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "Cluster Information:"
kubectl cluster-info
echo ""
echo "Minikube IP: $MINIKUBE_IP"
echo "MetalLB IP pool: ${IP_START}-${IP_END}"
echo ""
echo "Enabled Addons:"
minikube addons list | grep enabled
echo ""
echo "MetalLB Status:"
kubectl get pods -n metallb-system
echo ""
echo "Next Steps:"
echo "1. Proceed to Phase 2: Database Design & Deployment"
echo ""
