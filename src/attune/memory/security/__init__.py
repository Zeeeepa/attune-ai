"""Security Module for Attune AI Memory

Provides enterprise-grade security controls including:
- PII scrubbing (GDPR, HIPAA, SOC2 compliant)
- Secrets detection (API keys, passwords, private keys)
- Audit logging (tamper-evident, SOC2/HIPAA compliant)

Copyright 2025 Smart AI Memory, LLC
Licensed under the Apache License, Version 2.0
"""

from .audit_logger import AuditEvent, AuditLogger, SecurityViolation
from .pii_scrubber import PIIDetection, PIIPattern, PIIScrubber
from .secrets_detector import SecretDetection, SecretsDetector, SecretType, Severity, detect_secrets

__all__ = [
    "AuditEvent",
    # Audit Logging
    "AuditLogger",
    "PIIDetection",
    "PIIPattern",
    # PII Scrubbing
    "PIIScrubber",
    "SecretDetection",
    "SecretType",
    # Secrets Detection
    "SecretsDetector",
    "SecurityViolation",
    "Severity",
    "detect_secrets",
]
