"""Authentication and authorization using Keycloak OAuth2/OIDC."""

from typing import Optional
import logging
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import requests
from functools import lru_cache

from .config import settings

logger = logging.getLogger(__name__)

# Security scheme for Bearer token
security = HTTPBearer(auto_error=False)


class KeycloakAuth:
    """Keycloak authentication handler."""

    def __init__(self):
        self.server_url = settings.keycloak_server_url
        self.realm = settings.keycloak_realm
        self.client_id = settings.keycloak_client_id
        self._public_key = None

    @property
    def realm_url(self) -> str:
        """Get the realm URL."""
        return f"{self.server_url}/realms/{self.realm}"

    @lru_cache(maxsize=1)
    def get_public_key(self) -> str:
        """
        Fetch Keycloak realm public key for JWT verification.

        Cached to avoid repeated requests to Keycloak.
        """
        try:
            # Get realm configuration
            response = requests.get(f"{self.realm_url}", timeout=5)
            response.raise_for_status()
            realm_info = response.json()

            # Extract public key
            public_key = realm_info.get("public_key")
            if not public_key:
                raise ValueError("Public key not found in realm configuration")

            # Format as PEM
            return f"-----BEGIN PUBLIC KEY-----\n{public_key}\n-----END PUBLIC KEY-----"

        except Exception as e:
            logger.error(f"Failed to fetch Keycloak public key: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service unavailable"
            )

    def verify_token(self, token: str) -> dict:
        """
        Verify and decode JWT token from Keycloak.

        Args:
            token: JWT access token

        Returns:
            Decoded token payload

        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            public_key = self.get_public_key()

            # Decode and verify token
            payload = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                audience=self.client_id,
                options={
                    "verify_signature": True,
                    "verify_aud": True,
                    "verify_exp": True,
                }
            )

            return payload

        except JWTError as e:
            logger.warning(f"JWT validation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )


# Global auth instance
keycloak_auth = KeycloakAuth()


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> dict:
    """
    Dependency to get current authenticated user.

    Validates JWT token from Authorization header and returns user info.

    Args:
        request: FastAPI request object
        credentials: HTTP Authorization credentials

    Returns:
        User information from validated token

    Raises:
        HTTPException: If authentication fails
    """
    # Skip authentication for public endpoints
    if not settings.auth_enabled:
        logger.warning("Authentication is disabled - allowing all requests")
        return {"sub": "anonymous", "preferred_username": "anonymous"}

    # Check if endpoint is public
    path = request.url.path
    if path in settings.public_endpoints:
        return {"sub": "anonymous", "preferred_username": "anonymous"}

    # Require authentication for protected endpoints
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify token
    token = credentials.credentials
    user_info = keycloak_auth.verify_token(token)

    logger.info(f"Authenticated user: {user_info.get('preferred_username', 'unknown')}")

    return user_info


async def get_current_active_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Dependency to get current active user.

    Can be extended to check user status, roles, etc.

    Args:
        current_user: User info from token

    Returns:
        Active user information
    """
    # Could add additional checks here:
    # - Check if user is active
    # - Check if user has required roles
    # - Check if user is verified

    return current_user


def require_role(required_role: str):
    """
    Dependency factory for role-based access control.

    Usage:
        @router.get("/admin")
        async def admin_endpoint(user: dict = Depends(require_role("admin"))):
            ...

    Args:
        required_role: Role name required to access endpoint

    Returns:
        Dependency function
    """
    async def check_role(current_user: dict = Depends(get_current_user)) -> dict:
        """Check if user has required role."""
        # Get user roles from token
        realm_access = current_user.get("realm_access", {})
        roles = realm_access.get("roles", [])

        if required_role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role '{required_role}' not found"
            )

        return current_user

    return check_role
