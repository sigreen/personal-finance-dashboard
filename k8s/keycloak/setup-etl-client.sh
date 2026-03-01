#!/bin/bash
# Setup Keycloak client for Finance ETL Service

set -e

echo "========================================="
echo "Keycloak Client Setup for Finance ETL"
echo "========================================="
echo ""

# Login to Keycloak admin CLI
echo "Logging into Keycloak..."
kubectl exec -n keycloak keycloak-0 -- /opt/keycloak/bin/kcadm.sh config credentials \
  --server http://localhost:8080 \
  --realm master \
  --user admin \
  --password admin

echo "✓ Logged in successfully"
echo ""

# Check if client already exists
echo "Checking if finance-etl client exists..."
CLIENT_ID=$(kubectl exec -n keycloak keycloak-0 -- /opt/keycloak/bin/kcadm.sh get clients -r master \
  --fields id,clientId \
  2>/dev/null | grep -B 1 '"clientId" : "finance-etl"' | grep '"id"' | cut -d'"' -f4 || echo "")

if [ -n "$CLIENT_ID" ]; then
  echo "⚠ Client 'finance-etl' already exists with ID: $CLIENT_ID"
  echo "Updating existing client..."

  kubectl exec -n keycloak keycloak-0 -- /opt/keycloak/bin/kcadm.sh update clients/$CLIENT_ID -r master \
    -s enabled=true \
    -s publicClient=true \
    -s 'redirectUris=["http://finance.localtest.me:8081/*","http://localhost:3000/*"]' \
    -s 'webOrigins=["http://finance.localtest.me:8081","http://localhost:3000"]' \
    -s directAccessGrantsEnabled=true \
    -s standardFlowEnabled=true \
    -s implicitFlowEnabled=false \
    -s serviceAccountsEnabled=false

  echo "✓ Client updated successfully"
else
  echo "Creating new client 'finance-etl'..."

  kubectl exec -n keycloak keycloak-0 -- /opt/keycloak/bin/kcadm.sh create clients -r master \
    -s clientId=finance-etl \
    -s enabled=true \
    -s publicClient=true \
    -s 'redirectUris=["http://finance.localtest.me:8081/*","http://localhost:3000/*"]' \
    -s 'webOrigins=["http://finance.localtest.me:8081","http://localhost:3000"]' \
    -s directAccessGrantsEnabled=true \
    -s standardFlowEnabled=true \
    -s implicitFlowEnabled=false \
    -s serviceAccountsEnabled=false \
    -s 'description=Finance ETL Service API authentication'

  echo "✓ Client created successfully"
fi

echo ""
echo "========================================="
echo "Client Configuration Complete"
echo "========================================="
echo ""
echo "Client ID: finance-etl"
echo "Realm: master"
echo "Public Client: true (no secret required)"
echo "Allowed Origins: http://finance.localtest.me:8081, http://localhost:3000"
echo ""
echo "To test authentication:"
echo "1. Get access token:"
echo "   curl -X POST http://keycloak.localtest.me:8081/realms/master/protocol/openid-connect/token \\"
echo "     -d 'client_id=finance-etl' \\"
echo "     -d 'username=admin' \\"
echo "     -d 'password=admin' \\"
echo "     -d 'grant_type=password'"
echo ""
echo "2. Use token to call API:"
echo "   curl -H 'Authorization: Bearer <token>' http://finance.localtest.me:8081/api/accounts"
echo ""
