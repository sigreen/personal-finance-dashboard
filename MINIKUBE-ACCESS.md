# Accessing MCP Server from Minikube

## The Problem

With minikube using the **podman driver**, the standard `minikube tunnel` doesn't work properly because:
- LoadBalancer IPs (192.168.49.x) aren't routable from the host
- The podman network is isolated
- Tunnel requires complex routing setup

## The Solution

Use **kubectl port-forward** to expose the service on localhost.

### Start Port Forward

In a separate terminal, run:

```bash
./scripts/start-mcp-port-forward.sh
```

Or manually:

```bash
kubectl port-forward svc/mcp-server 8081:8081
```

Keep this terminal open. The MCP server will be accessible at `http://localhost:8081/sse`.

### Alternative: minikube service

You can also use:

```bash
minikube service mcp-server
```

This automatically opens a browser and creates a proxy, but the port changes each time.

## Why Not minikube tunnel?

`minikube tunnel` is designed for:
- Docker driver (not podman)
- KVM/VirtualBox drivers
- Environments where the minikube network is routable

With podman on Linux, the network isolation prevents the tunnel from working correctly.

## Summary

**Recommended approach**: Use `./scripts/start-mcp-port-forward.sh`
- Simple
- Reliable
- Consistent port (8081)
- No special privileges required
