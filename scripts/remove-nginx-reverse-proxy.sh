#!/bin/bash
set -e

echo "Removing nginx reverse proxy..."
echo ""

# Stop nginx
if systemctl is-active --quiet nginx; then
    echo "Stopping nginx..."
    sudo systemctl stop nginx
    sudo systemctl disable nginx
fi

# Remove configuration file
if [ -f /etc/nginx/conf.d/finance-dashboard.conf ]; then
    echo "Removing nginx configuration..."
    sudo rm /etc/nginx/conf.d/finance-dashboard.conf
fi

echo ""
echo "✅ Nginx reverse proxy removed!"
