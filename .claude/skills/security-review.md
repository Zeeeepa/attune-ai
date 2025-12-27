# Security Review Skill

Use this skill when reviewing code for security issues in the Empathy Framework.

## Security Classification

### Data Classification Levels
- **PUBLIC**: General patterns, safe to share
- **INTERNAL**: Proprietary algorithms, company-only
- **SENSITIVE**: Healthcare/HIPAA data, requires encryption

### PII Patterns to Detect
```python
# Healthcare PII (HIPAA)
HEALTHCARE_PII = {
    "mrn": r'\bMRN:?\s*\d{6,10}\b',       # Medical Record Number
    "patient_id": r'\bPT\d{6,10}\b',       # Patient ID
    "insurance_id": r'\bINS\d{8,12}\b',    # Insurance ID
    "dob": r'\b\d{1,2}/\d{1,2}/\d{4}\b',   # Date of birth
}

# Software PII
SOFTWARE_PII = {
    "internal_id": r'\b[A-Z]{2,4}-\d{4,6}\b',  # JIRA tickets
    "database_conn": r'(postgresql|mysql|mongodb)://[^"\s]+',
}
```

## Security Checklist

### API Keys & Secrets
- [ ] No hardcoded API keys
- [ ] Secrets loaded from environment variables
- [ ] `.env` files in `.gitignore`
- [ ] No secrets in logs or error messages

### Input Validation
- [ ] User input sanitized before use
- [ ] SQL injection prevention (parameterized queries)
- [ ] Command injection prevention (no `shell=True` with user input)
- [ ] Path traversal prevention (validate file paths)

### Healthcare Wizards (HIPAA)
- [ ] All data classified as SENSITIVE
- [ ] Encryption enabled for storage
- [ ] 90-day retention policy enforced
- [ ] Audit logging for all accesses

### Dependencies
- [ ] Run `pip-audit` for vulnerability scan
- [ ] Check for outdated packages with known CVEs
- [ ] Review new dependencies before adding

## Security Tests

```bash
# Run security test suite
pytest tests/test_security_controls.py -v
pytest tests/test_pii_scrubbing.py -v
pytest tests/test_secrets_detection.py -v
pytest tests/test_pattern_classification.py -v

# Scan for secrets in git history
git log -p | grep -E "(api_key|password|secret|token)" --color

# Check for hardcoded credentials
grep -r "api_key\s*=" --include="*.py" | grep -v "os.getenv"
```

## Compliance Requirements

| Standard | Requirement | Implementation |
|----------|-------------|----------------|
| GDPR | Data minimization | Scrub PII before storage |
| HIPAA | PHI protection | SENSITIVE classification + encryption |
| SOC2 | Audit trails | All LLM interactions logged |

## Reporting Security Issues

1. Do NOT commit the vulnerability
2. Contact: admin@smartaimemory.com
3. Use secure communication channel
4. Provide reproduction steps
