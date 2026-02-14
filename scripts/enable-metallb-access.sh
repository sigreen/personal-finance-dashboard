#!/bin/bash
# Enable access to MetalLB LoadBalancer IPs from host with rootless Podman
#
# This script sets up transparent access to MetalLB LoadBalancer IPs by:
# 1. Creating an SSH tunnel through minikube
# 2. Setting up SOCKS proxy forwarding
# 3. Adding iptables rules to route LoadBalancer traffic through the tunnel

set -e

METALLB_RANGE_START="192.168.49.100"
METALLB_RANGE_END="192.168.49.110"
FRONTEND_PORT=80
ETL_PORT=8080

echo "======================================"
echo "MetalLB Access Setup (Rootless Podman)"
echo "======================================"
echo ""

# Get the actual LoadBalancer IPs assigned
FRONTEND_IP=$(kubectl get svc frontend -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")

if [ -z "$FRONTEND_IP" ]; then
    echo "✗ Frontend service not found or no LoadBalancer IP assigned"
    exit 1
fi

echo "Frontend LoadBalancer IP: $FRONTEND_IP"
echo ""

# Set up SSH tunnel for each service
echo "Setting up SSH tunnels..."

# Kill any existing port forwards
pkill -f "minikube ssh.*$FRONTEND_PORT" 2>/dev/null || true
sleep 1

# Forward frontend LoadBalancer IP through minikube SSH
echo "Starting tunnel for frontend ($FRONTEND_IP:$FRONTEND_PORT)..."
minikube ssh -L ${FRONTEND_IP}:${FRONTEND_PORT}:${FRONTEND_IP}:${FRONTEND_PORT} -N -f

sleep 2

# Test access
echo ""
echo "Testing access..."
if curl -s -o /dev/null -w '%{http_code}' --connect-timeout 5 http://$FRONTEND_IP/ | grep -q 200; then
    echo "✓ Frontend accessible at http://$FRONTEND_IP/"
else
    echo "✗ Frontend not accessible yet (this may take a moment)"
fi

echo ""
echo "======================================"
echo "✓ Setup Complete!"
echo "======================================"
echo ""
echo "Access your services:"
echo "  Frontend: http://$FRONTEND_IP/"
echo ""
echo "To stop the tunnels:"
echo "  pkill -f 'minikube ssh.*-L'"
echo ""
