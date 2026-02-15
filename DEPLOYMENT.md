# MCP Server Deployment Guide

This guide covers deploying the Node.js MCP server to minikube with MetalLB LoadBalancer.

## Prerequisites

- minikube running with MetalLB installed
- podman or docker for building images
- kubectl configured to access your minikube cluster

## Quick Start

### 1. Build the MCP Server Image

```bash
./scripts/build-mcp-server.sh
```

This builds the Node.js MCP server container image.

### 2. Deploy to Kubernetes

```bash
./scripts/deploy-mcp-server.sh
```

This will:
- Apply MetalLB configuration
- Deploy the MCP server
- Wait for the deployment to be ready

### 3. Start Minikube Tunnel

In a separate terminal, start the minikube tunnel (requires sudo):

```bash
sudo ./scripts/start-minikube-tunnel.sh
```

Keep this running in the background. The tunnel is required for LoadBalancer services to be accessible from your host machine.

### 4. Get the MCP Server URL

```bash
./scripts/get-mcp-server-url.sh
```

This will display the LoadBalancer IP and the full URL for your MCP server.

### 5. Update .mcp.json

Edit `.mcp.json` and replace `<LOADBALANCER_IP>` with the actual IP address from step 4:

```json
{
  "mcpServers": {
    "personal-finance": {
      "url": "http://192.168.49.100:8081/sse",
      "type": "sse",
      "env": {}
    }
  }
}
```

### 6. Test the Connection

```bash
# Check health endpoint
curl http://<LOADBALANCER_IP>:8081/health

# Check server info
curl http://<LOADBALANCER_IP>:8081/
```

## Architecture Changes

### What Was Removed

- **Python MCP server**: Completely replaced with Node.js implementation
- **nginx-ingress**: No longer needed, using MetalLB LoadBalancer instead
- **Ingress resources**: Removed in favor of direct LoadBalancer access
- **nginx-related scripts**: Removed port-forwarding and reverse proxy scripts

### What Was Added

- **Node.js MCP server**: Clean implementation using @modelcontextprotocol/sdk
- **MetalLB LoadBalancer**: Direct external IP access to services
- **Minikube tunnel**: Exposes LoadBalancer IPs to the host machine
- **Helper scripts**: Build, deploy, and get URL scripts

## Troubleshooting

### LoadBalancer IP Stuck in Pending

Make sure:
1. MetalLB is installed in your cluster
2. MetalLB configuration is applied: `kubectl apply -f k8s/base/metallb-config.yaml`
3. The IP range in `metallb-config.yaml` matches your minikube network

### Cannot Access MCP Server

Make sure:
1. Minikube tunnel is running: `sudo ./scripts/start-minikube-tunnel.sh`
2. The LoadBalancer has an external IP: `kubectl get svc mcp-server`
3. The pod is running: `kubectl get pods -l app=mcp-server`

### Check Logs

```bash
# MCP server logs
kubectl logs -l app=mcp-server -f

# Check pod status
kubectl describe pod -l app=mcp-server
```

## MetalLB Configuration

The MetalLB configuration is in `k8s/base/metallb-config.yaml` and uses the IP range `192.168.49.100-192.168.49.110`. This range should work with the default minikube network. If you need to adjust it:

1. Check your minikube IP: `minikube ip`
2. Update the IP range in `metallb-config.yaml` to match your network
3. Reapply: `kubectl apply -f k8s/base/metallb-config.yaml`

## Development

To develop locally without Kubernetes:

```bash
cd backend/mcp-server

# Install dependencies
npm install

# Set environment variables
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=finance
export DB_USER=finance_user
export DB_PASSWORD=finance_password

# Run in development mode
npm run dev
```

The server will be available at `http://localhost:8081/sse`.
