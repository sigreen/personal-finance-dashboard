#!/bin/bash
# Disable MetalLB LoadBalancer access
# Run this script with: sudo ./scripts/disable-metallb.sh

FRONTEND_IP="192.168.49.100"

echo "======================================"
echo "Disabling MetalLB LoadBalancer Access"
echo "======================================"
echo ""

# Remove iptables rule
echo "Removing iptables rule..."
iptables -t nat -D OUTPUT -d ${FRONTEND_IP} -p tcp --dport 80 -j DNAT --to-destination 127.0.0.1:8888 2>/dev/null || echo "  Rule not found"

# Kill SSH tunnel
echo "Stopping SSH tunnel..."
pkill -f "ssh.*${FRONTEND_IP}:80" 2>/dev/null || echo "  No tunnel found"
pkill -f "ssh.*localhost:8888" 2>/dev/null || echo "  No tunnel found"

# Remove dummy interface
echo "Removing dummy interface..."
ip link del metallb0 2>/dev/null || echo "  Interface not found"

echo ""
echo "✓ Cleanup complete!"
