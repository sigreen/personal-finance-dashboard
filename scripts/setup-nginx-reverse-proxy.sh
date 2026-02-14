#!/bin/bash
set -e

# Configuration
BACKEND="localhost:8888"  # SSH tunnel endpoint
HOST_PORT="8080"
HOST_IP="11.11.2.65"

echo "Setting up nginx reverse proxy for dashboard..."
echo ""

# Check if nginx is installed
if ! command -v nginx &> /dev/null; then
    echo "Installing nginx..."
    sudo dnf install -y nginx
fi

# Create nginx configuration for reverse proxy
echo "Creating nginx configuration..."
sudo tee /etc/nginx/conf.d/finance-dashboard.conf > /dev/null <<EOF
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

# Test nginx configuration
echo "Testing nginx configuration..."
sudo nginx -t

# Configure SELinux to allow nginx to connect to network
echo "Configuring SELinux for nginx..."
sudo setsebool -P httpd_can_network_connect 1 2>/dev/null || true

# Enable and start nginx
echo "Enabling and starting nginx..."
sudo systemctl enable nginx
sudo systemctl restart nginx

# Wait for nginx to start
sleep 2

echo ""
echo "✅ Nginx reverse proxy configured!"
echo ""
echo "Dashboard accessible at:"
echo "  - Local: http://$HOST_IP:$HOST_PORT"
echo "  - Home network: http://$HOST_IP:$HOST_PORT"
echo ""
echo "Note: Requires SSH tunnel to be running (enable-metallb.sh)"
