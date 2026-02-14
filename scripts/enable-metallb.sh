#!/bin/bash
# Enable MetalLB LoadBalancer access with rootless Podman
# Run this script with: sudo ./scripts/enable-metallb.sh

set -e

echo "======================================"
echo "Enabling MetalLB LoadBalancer Access"
echo "======================================"
echo ""

# Get LoadBalancer IP
FRONTEND_IP=$(sudo -u $SUDO_USER kubectl get svc frontend -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "192.168.49.100")

echo "Frontend LoadBalancer IP: $FRONTEND_IP"
echo ""

# Create dummy interface
echo "Step 1: Creating dummy network interface..."
ip link add metallb0 type dummy 2>/dev/null || echo "  Interface already exists"
ip addr add ${FRONTEND_IP}/32 dev metallb0 2>/dev/null || echo "  IP already assigned"
ip link set metallb0 up
echo "✓ Dummy interface created: metallb0 with IP $FRONTEND_IP"
echo ""

# Get minikube SSH port
echo "Step 2: Setting up SSH tunnel..."
SSH_PORT=$(sudo -u $SUDO_USER podman port minikube | grep '22/tcp' | cut -d: -f2)
SSH_KEY=/home/$SUDO_USER/.minikube/machines/minikube/id_rsa

# Kill any existing tunnel
pkill -f "ssh.*${FRONTEND_IP}:80" 2>/dev/null || true
sleep 1

# Create SSH tunnel as the user (not root)
sudo -u $SUDO_USER ssh -i $SSH_KEY \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    -L localhost:8888:${FRONTEND_IP}:80 \
    -p $SSH_PORT docker@localhost -N -f 2>&1 | grep -v "Warning: Permanently added" || true

sleep 2

echo "✓ SSH tunnel created: localhost:8888 -> ${FRONTEND_IP}:80"
echo ""

# Add iptables rule to forward traffic from the dummy interface to the tunnel
echo "Step 3: Adding iptables DNAT rule..."
iptables -t nat -C OUTPUT -d ${FRONTEND_IP} -p tcp --dport 80 -j DNAT --to-destination 127.0.0.1:8888 2>/dev/null || \
    iptables -t nat -A OUTPUT -d ${FRONTEND_IP} -p tcp --dport 80 -j DNAT --to-destination 127.0.0.1:8888

echo "✓ iptables rule added"
echo ""

# Test access
echo "Testing access..."
if curl -s -o /dev/null -w '%{http_code}' --connect-timeout 5 http://${FRONTEND_IP}/ | grep -q 200; then
    echo "✓ SUCCESS! Frontend is accessible at http://${FRONTEND_IP}/"
else
    echo "⚠ Frontend may not be ready yet. Wait a moment and try: curl -I http://${FRONTEND_IP}/"
fi

echo ""
echo "======================================"
echo "Step 4: Setting up Nginx Reverse Proxy for Home Network Access"
echo "======================================"
echo ""

# Check if nginx is installed
if ! command -v nginx &> /dev/null; then
    echo "Installing nginx..."
    dnf install -y nginx
fi

# Configuration
HOST_PORT="8080"
BACKEND="localhost:8888"

# Create nginx configuration for reverse proxy
echo "Creating nginx configuration..."
tee /etc/nginx/conf.d/finance-dashboard.conf > /dev/null <<EOF
server {
    listen $HOST_PORT;
    server_name _;

    access_log /var/log/nginx/dashboard-access.log;
    error_log /var/log/nginx/dashboard-error.log;

    location / {
        proxy_pass http://$BACKEND;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF

# Configure SELinux to allow nginx to connect to network
echo "Configuring SELinux for nginx..."
setsebool -P httpd_can_network_connect 1 2>/dev/null || true

# Test nginx configuration
echo "Testing nginx configuration..."
nginx -t

# Enable and start nginx
echo "Enabling and starting nginx..."
systemctl enable nginx
systemctl restart nginx

sleep 2
echo "✓ Nginx reverse proxy configured on port $HOST_PORT"

echo ""
echo "======================================"
echo "✓ Setup Complete!"
echo "======================================"
echo ""
echo "Access your dashboard:"
echo "  - Local: http://${FRONTEND_IP}/"
echo "  - Home network: http://11.11.2.65:$HOST_PORT"
echo ""
echo "To disable and clean up later, run:"
echo "  sudo ./scripts/disable-metallb.sh"
echo ""
