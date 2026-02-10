"""SMART on FHIR JWT Authentication.

Backend service authentication for CDS Hooks endpoints.
Verifies JWT tokens signed with RS256 or ES256, fetched from
the EHR's JWKS (JSON Web Key Set) endpoint.

For development: set SMART_AUTH_DISABLED=true to bypass auth.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

from __future__ import annotations

import json
import logging
import os
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)

# Auth disabled flag for development
SMART_AUTH_DISABLED = os.getenv("SMART_AUTH_DISABLED", "false").lower() == "true"


@dataclass
class SMARTAuthConfig:
    """Configuration for SMART on FHIR authentication.

    Attributes:
        issuer_url: Expected token issuer (iss claim)
        audience: Expected audience (aud claim) - our service URL
        public_key_url: JWKS endpoint URL for fetching signing keys
        allowed_scopes: Required scopes in the token
        cache_ttl_seconds: How long to cache JWKS keys (default 1hr)
    """

    issuer_url: str
    audience: str
    public_key_url: str
    allowed_scopes: list[str] = field(default_factory=lambda: ["system/*.read"])
    cache_ttl_seconds: int = 3600


# JWKS cache
_jwks_cache: dict[str, Any] = {}
_jwks_cache_time: float = 0.0


def fetch_jwks(url: str, cache_ttl: int = 3600) -> dict[str, Any]:
    """Fetch JSON Web Key Set from JWKS endpoint.

    Uses a simple TTL cache to avoid hitting the endpoint on every request.

    Args:
        url: JWKS endpoint URL
        cache_ttl: Cache TTL in seconds (default 1 hour)

    Returns:
        JWKS dict with 'keys' list

    Raises:
        ValueError: If JWKS endpoint is unreachable or returns invalid JSON
    """
    global _jwks_cache, _jwks_cache_time  # noqa: PLW0603

    if _jwks_cache and (time.time() - _jwks_cache_time) < cache_ttl:
        return _jwks_cache

    try:
        req = Request(url, headers={"Accept": "application/json"})
        with urlopen(req, timeout=10) as response:  # noqa: S310
            data = json.loads(response.read().decode())
            _jwks_cache = data
            _jwks_cache_time = time.time()
            return data
    except URLError as e:
        logger.error(f"Failed to fetch JWKS from {url}: {e}")
        raise ValueError(f"JWKS endpoint unreachable: {url}") from e
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON from JWKS endpoint: {e}")
        raise ValueError(f"Invalid JWKS response from {url}") from e


def _get_signing_key(jwks: dict[str, Any], kid: str) -> Any:
    """Find signing key by kid in JWKS.

    Args:
        jwks: JWKS dict with 'keys' list
        kid: Key ID from JWT header

    Returns:
        PyJWT-compatible key object

    Raises:
        ValueError: If key ID not found in JWKS or unsupported key type
        ImportError: If PyJWT[crypto] not installed
    """
    try:
        from jwt.algorithms import ECAlgorithm, RSAAlgorithm
    except ImportError as e:
        raise ImportError(
            "PyJWT[crypto] required for SMART auth. "
            "Install with: pip install 'PyJWT[crypto]>=2.8.0'"
        ) from e

    for key_data in jwks.get("keys", []):
        if key_data.get("kid") == kid:
            kty = key_data.get("kty", "")
            if kty == "RSA":
                return RSAAlgorithm.from_jwk(json.dumps(key_data))
            elif kty == "EC":
                return ECAlgorithm.from_jwk(json.dumps(key_data))
            else:
                raise ValueError(f"Unsupported key type: {kty}")

    raise ValueError(f"Key ID '{kid}' not found in JWKS")


def verify_smart_token(token: str, config: SMARTAuthConfig) -> dict[str, Any]:
    """Verify a SMART on FHIR JWT token.

    Steps:
        1. Decode JWT header to get kid (key ID) and algorithm
        2. Fetch public key from JWKS endpoint (cached)
        3. Verify signature (RS256 or ES256)
        4. Validate claims: iss, aud, exp
        5. Check required scopes

    Args:
        token: JWT bearer token string
        config: SMART authentication configuration

    Returns:
        Decoded JWT payload dict

    Raises:
        ValueError: If token is invalid, expired, or fails verification
        ImportError: If PyJWT not installed
    """
    try:
        import jwt
    except ImportError as e:
        raise ImportError(
            "PyJWT required for SMART auth. "
            "Install with: pip install 'PyJWT[crypto]>=2.8.0'"
        ) from e

    # Decode header without verification to get kid
    try:
        unverified_header = jwt.get_unverified_header(token)
    except jwt.exceptions.DecodeError as e:
        raise ValueError(f"Invalid JWT format: {e}") from e

    kid = unverified_header.get("kid")
    algorithm = unverified_header.get("alg", "RS256")

    if algorithm not in ("RS256", "ES256", "RS384", "ES384"):
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    if not kid:
        raise ValueError("JWT missing 'kid' header")

    # Fetch JWKS and find signing key
    jwks = fetch_jwks(config.public_key_url, config.cache_ttl_seconds)
    signing_key = _get_signing_key(jwks, kid)

    # Verify token
    try:
        payload = jwt.decode(
            token,
            key=signing_key,
            algorithms=[algorithm],
            issuer=config.issuer_url,
            audience=config.audience,
            options={"require": ["exp", "iss", "aud"]},
        )
    except jwt.ExpiredSignatureError as e:
        raise ValueError("Token has expired") from e
    except jwt.InvalidIssuerError as e:
        raise ValueError(f"Invalid issuer: expected {config.issuer_url}") from e
    except jwt.InvalidAudienceError as e:
        raise ValueError(f"Invalid audience: expected {config.audience}") from e
    except jwt.InvalidTokenError as e:
        raise ValueError(f"Token verification failed: {e}") from e

    # Verify scopes
    token_scope = payload.get("scope", "")
    token_scopes = set(token_scope.split()) if isinstance(token_scope, str) else set()
    required_scopes = set(config.allowed_scopes)
    if required_scopes and not required_scopes.intersection(token_scopes):
        raise ValueError(
            f"Insufficient scopes. Required one of: {config.allowed_scopes}, "
            f"got: {list(token_scopes)}"
        )

    return payload


def smart_auth_dependency(config: SMARTAuthConfig) -> Callable:
    """Create a FastAPI dependency for SMART token verification.

    Returns a callable that can be used with FastAPI's Depends():

        auth = smart_auth_dependency(config)

        @app.get("/protected", dependencies=[Depends(auth)])
        async def protected(): ...

    Args:
        config: SMART authentication configuration

    Returns:
        FastAPI dependency callable
    """
    from fastapi import Depends, HTTPException
    from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

    security = HTTPBearer(auto_error=not SMART_AUTH_DISABLED)

    async def verify(
        credentials: HTTPAuthorizationCredentials | None = Depends(security),
    ) -> dict[str, Any] | None:
        """Verify SMART on FHIR JWT from Authorization header.

        Args:
            credentials: HTTP Bearer credentials from the Authorization header.

        Returns:
            Decoded JWT payload dict, or None if auth is disabled.

        Raises:
            HTTPException: 401 if token is missing or invalid.
            HTTPException: 500 if auth module is not properly installed.
        """
        if SMART_AUTH_DISABLED:
            return None

        if credentials is None:
            raise HTTPException(status_code=401, detail="Missing authorization token")

        try:
            payload = verify_smart_token(credentials.credentials, config)
            return payload
        except ValueError as e:
            raise HTTPException(status_code=401, detail=str(e))
        except ImportError as e:
            logger.error(f"Auth dependency import error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Authentication module not properly installed",
            )

    return verify


def generate_test_token(
    config: SMARTAuthConfig,
    private_key_pem: str,
    additional_claims: dict[str, Any] | None = None,
    expires_in: int = 3600,
) -> str:
    """Generate a valid JWT token for testing.

    Creates a properly signed JWT for integration testing.
    NOT for production use.

    Args:
        config: SMART auth config (provides iss, aud)
        private_key_pem: RSA or EC private key in PEM format
        additional_claims: Extra claims to include
        expires_in: Token lifetime in seconds (default 1 hour)

    Returns:
        Signed JWT string

    Raises:
        ImportError: If PyJWT not installed
    """
    try:
        import jwt
    except ImportError as e:
        raise ImportError(
            "PyJWT required. Install with: pip install 'PyJWT[crypto]>=2.8.0'"
        ) from e

    now = int(time.time())
    payload: dict[str, Any] = {
        "iss": config.issuer_url,
        "aud": config.audience,
        "iat": now,
        "exp": now + expires_in,
        "scope": " ".join(config.allowed_scopes),
    }
    if additional_claims:
        payload.update(additional_claims)

    return jwt.encode(
        payload,
        private_key_pem,
        algorithm="RS256",
        headers={"kid": "test-key-1"},
    )
