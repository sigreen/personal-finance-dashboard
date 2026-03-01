# Kubernetes Network Policies

This directory contains NetworkPolicy resources that implement defense-in-depth security by restricting pod-to-pod network communication.

## Overview

Network Policies use a whitelist approach - by default, all traffic is denied unless explicitly allowed by a policy.

## Policies

### 1. PostgreSQL Network Policy
**File:** `postgres-network-policy.yaml`

**Purpose:** Restricts database access to only authorized services

**Ingress (Allowed Inbound):**
- ETL Service (app=etl-service) → port 5432
- MCP Server (app=personal-finance-mcp) → port 5432
- Database migration jobs (job-name=db-migrations) → port 5432
- Backup jobs (app=postgres-backup) → port 5432

**Egress (Allowed Outbound):**
- DNS queries (kube-dns) → port 53/UDP
- Database replication (app=postgres) → port 5432

**Security Impact:**
- ✅ Prevents unauthorized pods from accessing database
- ✅ Limits lateral movement in case of compromise
- ✅ Enforces principle of least privilege

### 2. ETL Service Network Policy
**File:** `etl-service-network-policy.yaml`

**Purpose:** Restricts API access to authorized clients only

**Ingress (Allowed Inbound):**
- Frontend (app=frontend) → port 8080
- Istio/service mesh (namespace=istio-system) → port 8080
- Kagenti gateway (namespace=kagenti-system) → port 8080
- Health checks (namespace=kube-system) → port 8080

**Egress (Allowed Outbound):**
- DNS queries → port 53/UDP
- PostgreSQL database → port 5432
- Keycloak authentication → port 8080
- HTTPS external services → port 443

**Security Impact:**
- ✅ Only frontend can call the ETL API
- ✅ Prevents direct external access bypassing auth
- ✅ Allows service mesh observability

### 3. Frontend Network Policy
**File:** `frontend-network-policy.yaml`

**Purpose:** Public-facing component with restricted egress

**Ingress (Allowed Inbound):**
- All traffic (public-facing service)

**Egress (Allowed Outbound):**
- DNS queries → port 53/UDP
- ETL Service API → port 8080
- Keycloak authentication → port 8080

**Security Impact:**
- ✅ Limits what frontend can communicate with
- ✅ Prevents data exfiltration to unauthorized destinations
- ✅ Enforces API-only communication pattern

## Deployment

### Apply All Policies
```bash
kubectl apply -f k8s/network-policies/
```

### Apply Individual Policy
```bash
kubectl apply -f k8s/network-policies/postgres-network-policy.yaml
kubectl apply -f k8s/network-policies/etl-service-network-policy.yaml
kubectl apply -f k8s/network-policies/frontend-network-policy.yaml
```

### Verify Policies
```bash
# List all network policies
kubectl get networkpolicies -n personal-finance

# Describe specific policy
kubectl describe networkpolicy postgres-network-policy -n personal-finance
```

## Testing

### Test Database Access

**Should SUCCEED:**
```bash
# From ETL service pod
kubectl exec -n personal-finance deployment/etl-service -- \
  psql -h postgres -U finance_user -d finance_db -c "SELECT 1;"
```

**Should FAIL:**
```bash
# From unauthorized pod
kubectl run test-pod -n personal-finance --image=postgres:15-alpine --rm -it -- \
  psql -h postgres -U finance_user -d finance_db -c "SELECT 1;"
# Expected: Connection timeout or refused
```

### Test ETL API Access

**Should SUCCEED:**
```bash
# From frontend pod
kubectl exec -n personal-finance deployment/frontend -- \
  curl -s http://etl-service:8080/api/health
```

**Should FAIL:**
```bash
# From unauthorized pod
kubectl run test-pod -n personal-finance --image=curlimages/curl --rm -it -- \
  curl -s http://etl-service:8080/api/health --max-time 5
# Expected: Timeout
```

## Troubleshooting

### Policy Not Working
1. **Check CNI plugin supports NetworkPolicies:**
   ```bash
   kubectl get nodes -o wide
   # Calico, Cilium, Weave Net support NetworkPolicies
   # Flannel (default) does NOT support NetworkPolicies
   ```

2. **Verify policy is applied:**
   ```bash
   kubectl get networkpolicy -n personal-finance
   kubectl describe networkpolicy <policy-name> -n personal-finance
   ```

3. **Check pod labels match selectors:**
   ```bash
   kubectl get pods -n personal-finance --show-labels
   ```

### Allow Additional Access

To allow a new service to access PostgreSQL:
```yaml
# Add to postgres-network-policy.yaml ingress rules:
- from:
  - podSelector:
      matchLabels:
        app: new-service-name
  ports:
  - protocol: TCP
    port: 5432
```

## Security Considerations

### Defense in Depth
Network Policies are ONE layer of security:
- ✅ Network isolation
- ✅ Principle of least privilege
- ⚠️ Does NOT replace authentication/authorization
- ⚠️ Does NOT encrypt traffic (use mTLS for that)
- ⚠️ Does NOT prevent container breakouts

### Best Practices
1. **Default Deny:** Start with deny-all, then whitelist
2. **Least Privilege:** Only allow required connections
3. **Label Discipline:** Use consistent, meaningful labels
4. **Regular Audits:** Review policies as architecture evolves
5. **Testing:** Verify policies work as expected

### CNI Requirements
Network Policies require a CNI plugin with policy support:
- ✅ Calico
- ✅ Cilium
- ✅ Weave Net
- ❌ Flannel (default k3s CNI does NOT support policies)

**Note:** k3s/k3d clusters may need Calico or Cilium installed for NetworkPolicy support.

## Monitoring

View denied connections (if CNI supports logging):
```bash
# Calico example
kubectl logs -n kube-system -l k8s-app=calico-node | grep "calico-packet"

# Check for network policy events
kubectl get events -n personal-finance --field-selector reason=NetworkPolicyViolation
```

## Future Enhancements

- [ ] Add egress policies for MCP server
- [ ] Implement namespace-level isolation
- [ ] Add policies for backup jobs
- [ ] Configure ingress policies for Istio/gateway
- [ ] Add monitoring/alerting for policy violations
