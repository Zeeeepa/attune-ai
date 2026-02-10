"""Unit tests for SMART on FHIR JWT authentication.

Tests cover SMARTAuthConfig creation, token verification (expired, wrong issuer,
wrong audience, valid RS256), generate_test_token, SMART_AUTH_DISABLED bypass,
and JWKS fetch/caching behavior.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

from __future__ import annotations

import json
import time
from unittest.mock import MagicMock, patch

import pytest

jwt_mod = pytest.importorskip("jwt", reason="PyJWT required for SMART auth tests")
pytest.importorskip("cryptography", reason="cryptography required for SMART auth tests")

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)
from jwt.algorithms import RSAAlgorithm

from attune.healthcare.fhir.smart_auth import (
    SMARTAuthConfig,
    _get_signing_key,
    fetch_jwks,
    generate_test_token,
    verify_smart_token,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def rsa_key_pair():
    """Generate a fresh RSA key pair for testing."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=Encoding.PEM,
        format=PrivateFormat.PKCS8,
        encryption_algorithm=NoEncryption(),
    ).decode()

    public_pem = public_key.public_bytes(
        encoding=Encoding.PEM,
        format=PublicFormat.SubjectPublicKeyInfo,
    ).decode()

    return private_key, public_key, private_pem, public_pem


@pytest.fixture()
def jwks_from_public_key(rsa_key_pair):
    """Build a JWKS dict from the test RSA public key."""
    _, public_key, _, _ = rsa_key_pair
    jwk_dict = json.loads(RSAAlgorithm.to_jwk(public_key))
    jwk_dict["kid"] = "test-key-1"
    jwk_dict["use"] = "sig"
    jwk_dict["alg"] = "RS256"
    return {"keys": [jwk_dict]}


@pytest.fixture()
def smart_config():
    """Standard SMARTAuthConfig for test use."""
    return SMARTAuthConfig(
        issuer_url="https://ehr.example.com",
        audience="https://cds.example.com/cds-services",
        public_key_url="https://ehr.example.com/.well-known/jwks.json",
        allowed_scopes=["system/*.read"],
    )


@pytest.fixture(autouse=True)
def _clear_jwks_cache():
    """Clear the module-level JWKS cache before each test."""
    import attune.healthcare.fhir.smart_auth as mod

    mod._jwks_cache = {}
    mod._jwks_cache_time = 0.0
    yield
    mod._jwks_cache = {}
    mod._jwks_cache_time = 0.0


def _make_token(
    private_pem: str,
    *,
    iss: str = "https://ehr.example.com",
    aud: str = "https://cds.example.com/cds-services",
    scope: str = "system/*.read",
    kid: str = "test-key-1",
    algorithm: str = "RS256",
    exp_offset: int = 3600,
    extra_claims: dict | None = None,
) -> str:
    """Helper to mint a JWT with configurable claims."""
    now = int(time.time())
    payload = {
        "iss": iss,
        "aud": aud,
        "iat": now,
        "exp": now + exp_offset,
        "scope": scope,
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt_mod.encode(
        payload,
        private_pem,
        algorithm=algorithm,
        headers={"kid": kid},
    )


# ---------------------------------------------------------------------------
# 1. SMARTAuthConfig creation with valid fields
# ---------------------------------------------------------------------------

class TestSMARTAuthConfig:
    """Tests for SMARTAuthConfig dataclass."""

    def test_create_with_required_fields(self) -> None:
        """Test creating config with only required fields uses correct defaults."""
        config = SMARTAuthConfig(
            issuer_url="https://ehr.example.com",
            audience="https://cds.example.com/cds-services",
            public_key_url="https://ehr.example.com/.well-known/jwks.json",
        )
        assert config.issuer_url == "https://ehr.example.com"
        assert config.audience == "https://cds.example.com/cds-services"
        assert config.public_key_url == "https://ehr.example.com/.well-known/jwks.json"
        assert config.allowed_scopes == ["system/*.read"]
        assert config.cache_ttl_seconds == 3600

    def test_create_with_all_fields(self) -> None:
        """Test creating config with all fields explicitly set."""
        config = SMARTAuthConfig(
            issuer_url="https://ehr.example.com",
            audience="https://cds.example.com/cds-services",
            public_key_url="https://ehr.example.com/.well-known/jwks.json",
            allowed_scopes=["system/Patient.read", "system/Observation.read"],
            cache_ttl_seconds=7200,
        )
        assert config.allowed_scopes == ["system/Patient.read", "system/Observation.read"]
        assert config.cache_ttl_seconds == 7200

    def test_allowed_scopes_default_not_shared(self) -> None:
        """Test that default allowed_scopes list is independent per instance."""
        config_a = SMARTAuthConfig(
            issuer_url="https://a.example.com",
            audience="https://a.example.com/cds",
            public_key_url="https://a.example.com/jwks",
        )
        config_b = SMARTAuthConfig(
            issuer_url="https://b.example.com",
            audience="https://b.example.com/cds",
            public_key_url="https://b.example.com/jwks",
        )
        config_a.allowed_scopes.append("extra")
        assert "extra" not in config_b.allowed_scopes


# ---------------------------------------------------------------------------
# 2. verify_smart_token rejects expired tokens
# ---------------------------------------------------------------------------

class TestVerifyExpiredToken:
    """Tests for expired token rejection."""

    def test_rejects_expired_token(
        self, rsa_key_pair, jwks_from_public_key, smart_config
    ) -> None:
        """Test that a token with exp in the past is rejected."""
        _, _, private_pem, _ = rsa_key_pair

        token = _make_token(private_pem, exp_offset=-3600)

        with patch(
            "attune.healthcare.fhir.smart_auth.fetch_jwks",
            return_value=jwks_from_public_key,
        ):
            with pytest.raises(ValueError, match="Token has expired"):
                verify_smart_token(token, smart_config)


# ---------------------------------------------------------------------------
# 3. verify_smart_token rejects wrong issuer
# ---------------------------------------------------------------------------

class TestVerifyWrongIssuer:
    """Tests for wrong issuer rejection."""

    def test_rejects_wrong_issuer(
        self, rsa_key_pair, jwks_from_public_key, smart_config
    ) -> None:
        """Test that a token from an unexpected issuer is rejected."""
        _, _, private_pem, _ = rsa_key_pair

        token = _make_token(private_pem, iss="https://evil.example.com")

        with patch(
            "attune.healthcare.fhir.smart_auth.fetch_jwks",
            return_value=jwks_from_public_key,
        ):
            with pytest.raises(ValueError, match="Invalid issuer"):
                verify_smart_token(token, smart_config)


# ---------------------------------------------------------------------------
# 4. verify_smart_token rejects wrong audience
# ---------------------------------------------------------------------------

class TestVerifyWrongAudience:
    """Tests for wrong audience rejection."""

    def test_rejects_wrong_audience(
        self, rsa_key_pair, jwks_from_public_key, smart_config
    ) -> None:
        """Test that a token with the wrong audience is rejected."""
        _, _, private_pem, _ = rsa_key_pair

        token = _make_token(private_pem, aud="https://wrong.example.com/service")

        with patch(
            "attune.healthcare.fhir.smart_auth.fetch_jwks",
            return_value=jwks_from_public_key,
        ):
            with pytest.raises(ValueError, match="Invalid audience"):
                verify_smart_token(token, smart_config)


# ---------------------------------------------------------------------------
# 5. verify_smart_token accepts valid RS256 JWT
# ---------------------------------------------------------------------------

class TestVerifyValidToken:
    """Tests for successful token verification."""

    def test_accepts_valid_rs256_token(
        self, rsa_key_pair, jwks_from_public_key, smart_config
    ) -> None:
        """Test that a properly signed, unexpired token with correct claims passes."""
        _, _, private_pem, _ = rsa_key_pair

        token = _make_token(private_pem)

        with patch(
            "attune.healthcare.fhir.smart_auth.fetch_jwks",
            return_value=jwks_from_public_key,
        ):
            payload = verify_smart_token(token, smart_config)

        assert payload["iss"] == "https://ehr.example.com"
        assert payload["aud"] == "https://cds.example.com/cds-services"
        assert "exp" in payload
        assert payload["scope"] == "system/*.read"

    def test_rejects_insufficient_scopes(
        self, rsa_key_pair, jwks_from_public_key
    ) -> None:
        """Test that a token with wrong scopes is rejected."""
        _, _, private_pem, _ = rsa_key_pair

        config = SMARTAuthConfig(
            issuer_url="https://ehr.example.com",
            audience="https://cds.example.com/cds-services",
            public_key_url="https://ehr.example.com/.well-known/jwks.json",
            allowed_scopes=["system/Patient.write"],
        )

        token = _make_token(private_pem, scope="system/*.read")

        with patch(
            "attune.healthcare.fhir.smart_auth.fetch_jwks",
            return_value=jwks_from_public_key,
        ):
            with pytest.raises(ValueError, match="Insufficient scopes"):
                verify_smart_token(token, config)

    def test_rejects_missing_kid_header(
        self, rsa_key_pair, jwks_from_public_key, smart_config
    ) -> None:
        """Test that a token without a kid header is rejected."""
        _, _, private_pem, _ = rsa_key_pair

        now = int(time.time())
        payload = {
            "iss": "https://ehr.example.com",
            "aud": "https://cds.example.com/cds-services",
            "iat": now,
            "exp": now + 3600,
            "scope": "system/*.read",
        }
        # Encode without kid in headers
        token = jwt_mod.encode(payload, private_pem, algorithm="RS256")

        with pytest.raises(ValueError, match="missing 'kid' header"):
            verify_smart_token(token, smart_config)

    def test_rejects_unsupported_algorithm(
        self, rsa_key_pair, smart_config
    ) -> None:
        """Test that an unsupported algorithm (HS256) is rejected."""
        token = jwt_mod.encode(
            {"iss": "x", "aud": "y", "exp": int(time.time()) + 3600},
            "secret",
            algorithm="HS256",
            headers={"kid": "test-key-1"},
        )

        with pytest.raises(ValueError, match="Unsupported algorithm"):
            verify_smart_token(token, smart_config)

    def test_rejects_invalid_jwt_format(self, smart_config) -> None:
        """Test that a completely malformed token raises ValueError."""
        with pytest.raises(ValueError, match="Invalid JWT format"):
            verify_smart_token("not.a.valid.jwt", smart_config)


# ---------------------------------------------------------------------------
# 6. generate_test_token produces valid token that passes verification
# ---------------------------------------------------------------------------

class TestGenerateTestToken:
    """Tests for generate_test_token helper."""

    def test_generated_token_passes_verification(
        self, rsa_key_pair, jwks_from_public_key, smart_config
    ) -> None:
        """Test that generate_test_token produces a token that verify_smart_token accepts."""
        _, _, private_pem, _ = rsa_key_pair

        token = generate_test_token(smart_config, private_pem)

        with patch(
            "attune.healthcare.fhir.smart_auth.fetch_jwks",
            return_value=jwks_from_public_key,
        ):
            payload = verify_smart_token(token, smart_config)

        assert payload["iss"] == smart_config.issuer_url
        assert payload["aud"] == smart_config.audience
        assert "system/*.read" in payload["scope"]

    def test_generated_token_includes_additional_claims(
        self, rsa_key_pair, jwks_from_public_key, smart_config
    ) -> None:
        """Test that additional_claims are included in the token."""
        _, _, private_pem, _ = rsa_key_pair

        extra = {"sub": "service-account-1", "jti": "unique-id-123"}
        token = generate_test_token(
            smart_config, private_pem, additional_claims=extra
        )

        with patch(
            "attune.healthcare.fhir.smart_auth.fetch_jwks",
            return_value=jwks_from_public_key,
        ):
            payload = verify_smart_token(token, smart_config)

        assert payload["sub"] == "service-account-1"
        assert payload["jti"] == "unique-id-123"

    def test_generated_token_uses_kid_test_key_1(
        self, rsa_key_pair, smart_config
    ) -> None:
        """Test that generate_test_token sets kid header to 'test-key-1'."""
        _, _, private_pem, _ = rsa_key_pair

        token = generate_test_token(smart_config, private_pem)
        header = jwt_mod.get_unverified_header(token)

        assert header["kid"] == "test-key-1"
        assert header["alg"] == "RS256"

    def test_generated_token_custom_expiry(
        self, rsa_key_pair, smart_config
    ) -> None:
        """Test that expires_in parameter controls token lifetime."""
        _, _, private_pem, _ = rsa_key_pair

        token = generate_test_token(smart_config, private_pem, expires_in=60)
        payload = jwt_mod.decode(token, options={"verify_signature": False})

        assert payload["exp"] - payload["iat"] == 60


# ---------------------------------------------------------------------------
# 7. SMART_AUTH_DISABLED=true bypasses auth
# ---------------------------------------------------------------------------

class TestSmartAuthDisabled:
    """Tests for the SMART_AUTH_DISABLED environment variable."""

    def test_disabled_flag_reads_from_env(self) -> None:
        """Test that the module flag reads SMART_AUTH_DISABLED env var."""
        with patch.dict("os.environ", {"SMART_AUTH_DISABLED": "true"}):
            # Re-evaluate the module-level variable
            import importlib

            import attune.healthcare.fhir.smart_auth as mod

            importlib.reload(mod)
            assert mod.SMART_AUTH_DISABLED is True

        # Restore default
        with patch.dict("os.environ", {"SMART_AUTH_DISABLED": "false"}):
            importlib.reload(mod)
            assert mod.SMART_AUTH_DISABLED is False

    def test_disabled_flag_default_is_false(self) -> None:
        """Test that SMART_AUTH_DISABLED defaults to False when env not set."""
        with patch.dict("os.environ", {}, clear=False):
            os_environ = dict(__import__("os").environ)
            os_environ.pop("SMART_AUTH_DISABLED", None)
            with patch.dict("os.environ", os_environ, clear=True):
                import importlib

                import attune.healthcare.fhir.smart_auth as mod

                importlib.reload(mod)
                assert mod.SMART_AUTH_DISABLED is False


# ---------------------------------------------------------------------------
# 8. JWKS fetch and caching
# ---------------------------------------------------------------------------

class TestFetchJWKS:
    """Tests for fetch_jwks with caching behavior."""

    def test_fetch_jwks_returns_parsed_json(self, jwks_from_public_key) -> None:
        """Test that fetch_jwks returns parsed JWKS from the endpoint."""
        jwks_json = json.dumps(jwks_from_public_key).encode()
        mock_response = MagicMock()
        mock_response.read.return_value = jwks_json
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch(
            "attune.healthcare.fhir.smart_auth.urlopen",
            return_value=mock_response,
        ):
            result = fetch_jwks("https://ehr.example.com/.well-known/jwks.json")

        assert "keys" in result
        assert len(result["keys"]) == 1
        assert result["keys"][0]["kid"] == "test-key-1"

    def test_fetch_jwks_caches_result(self, jwks_from_public_key) -> None:
        """Test that fetch_jwks caches the result and does not re-fetch within TTL."""
        jwks_json = json.dumps(jwks_from_public_key).encode()
        mock_response = MagicMock()
        mock_response.read.return_value = jwks_json
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch(
            "attune.healthcare.fhir.smart_auth.urlopen",
            return_value=mock_response,
        ) as mock_urlopen:
            # First call fetches from network
            result1 = fetch_jwks(
                "https://ehr.example.com/.well-known/jwks.json", cache_ttl=300
            )
            # Second call should use cache
            result2 = fetch_jwks(
                "https://ehr.example.com/.well-known/jwks.json", cache_ttl=300
            )

            assert mock_urlopen.call_count == 1
            assert result1 == result2

    def test_fetch_jwks_re_fetches_after_ttl_expires(
        self, jwks_from_public_key
    ) -> None:
        """Test that fetch_jwks re-fetches when cache TTL has expired."""
        jwks_json = json.dumps(jwks_from_public_key).encode()
        mock_response = MagicMock()
        mock_response.read.return_value = jwks_json
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        import attune.healthcare.fhir.smart_auth as mod

        with patch(
            "attune.healthcare.fhir.smart_auth.urlopen",
            return_value=mock_response,
        ) as mock_urlopen:
            # First call
            fetch_jwks("https://ehr.example.com/.well-known/jwks.json", cache_ttl=10)
            assert mock_urlopen.call_count == 1

            # Simulate cache expiration
            mod._jwks_cache_time = time.time() - 20

            # Should re-fetch
            fetch_jwks("https://ehr.example.com/.well-known/jwks.json", cache_ttl=10)
            assert mock_urlopen.call_count == 2

    def test_fetch_jwks_raises_on_unreachable_endpoint(self) -> None:
        """Test that fetch_jwks raises ValueError when endpoint is unreachable."""
        from urllib.error import URLError

        with patch(
            "attune.healthcare.fhir.smart_auth.urlopen",
            side_effect=URLError("Connection refused"),
        ):
            with pytest.raises(ValueError, match="JWKS endpoint unreachable"):
                fetch_jwks("https://bad.example.com/jwks")

    def test_fetch_jwks_raises_on_invalid_json(self) -> None:
        """Test that fetch_jwks raises ValueError on non-JSON response."""
        mock_response = MagicMock()
        mock_response.read.return_value = b"<html>not json</html>"
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch(
            "attune.healthcare.fhir.smart_auth.urlopen",
            return_value=mock_response,
        ):
            with pytest.raises(ValueError, match="Invalid JWKS response"):
                fetch_jwks("https://ehr.example.com/.well-known/jwks.json")


# ---------------------------------------------------------------------------
# Additional edge cases: _get_signing_key
# ---------------------------------------------------------------------------

class TestGetSigningKey:
    """Tests for the _get_signing_key helper."""

    def test_returns_key_for_matching_kid(self, jwks_from_public_key) -> None:
        """Test that _get_signing_key returns the correct key for a known kid."""
        key = _get_signing_key(jwks_from_public_key, "test-key-1")
        assert key is not None

    def test_raises_for_unknown_kid(self, jwks_from_public_key) -> None:
        """Test that _get_signing_key raises ValueError for unknown kid."""
        with pytest.raises(ValueError, match="Key ID 'unknown-kid' not found"):
            _get_signing_key(jwks_from_public_key, "unknown-kid")

    def test_raises_for_unsupported_key_type(self) -> None:
        """Test that _get_signing_key raises ValueError for unsupported kty."""
        jwks = {"keys": [{"kid": "test-key-1", "kty": "OKP"}]}
        with pytest.raises(ValueError, match="Unsupported key type"):
            _get_signing_key(jwks, "test-key-1")

    def test_raises_for_empty_keys_list(self) -> None:
        """Test that _get_signing_key raises ValueError when keys list is empty."""
        jwks = {"keys": []}
        with pytest.raises(ValueError, match="Key ID .* not found"):
            _get_signing_key(jwks, "test-key-1")
