#!/bin/bash

set -e

echo "======================================"
echo "MetalLB Configuration"
echo "======================================"
echo ""

# Get minikube IP
MINIKUBE_IP=$(minikube ip 2>/dev/null)
if [ -z "$MINIKUBE_IP" ]; then
    echo "ERROR: Minikube is not running. Please start minikube first."
    exit 1
fi

echo "Minikube IP: $MINIKUBE_IP"
echo ""

# Calculate IP range
IP_PREFIX=$(echo $MINIKUBE_IP | cut -d'.' -f1-3)
IP_START="${IP_PREFIX}.100"
IP_END="${IP_PREFIX}.110"

echo "Configuring MetalLB with IP range: $IP_START - $IP_END"
echo ""

# Create MetalLB ConfigMap
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  namespace: metallb-system
  name: config
data:
  config: |
    address-pools:
    - name: default
      protocol: layer2
      addresses:
      - $IP_START-$IP_END
EOF

echo ""
echo "✓ MetalLB configured successfully!"
echo ""
echo "Available IP range: $IP_START - $IP_END"
echo ""
echo "Services with type=LoadBalancer will receive IPs from this pool."
echo ""
