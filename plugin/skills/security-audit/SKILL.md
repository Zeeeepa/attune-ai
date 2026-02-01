---
name: security-audit
description: "Security vulnerability scanning. Triggers: 'security audit', 'find vulnerabilities', 'check for injection', 'XSS', 'SQL injection', 'OWASP', 'security scan', 'CVE', 'security issues', 'penetration test', 'secure my code', 'hardcoded secrets', 'credential leak'."
---

# Security Audit

Automated security vulnerability detection with 82% accuracy.

## Quick Start

```bash
# CLI (primary)
attune workflow run security-audit --path ./src

# Legacy alias (still works)
empathy workflow run security-audit --path ./src

# Natural language - just describe what you need:
"find security vulnerabilities in src/"
"check my code for injection attacks"
"scan for hardcoded secrets"
```

## Usage

### Via MCP Tool

The `security_audit` tool is available via MCP:

```python
# Invoked automatically when you describe:
"Run a security audit on src/"
"Check for security vulnerabilities"
"Find injection attacks in my code"
```

### Via Python

```python
from attune.workflows import SecurityAuditWorkflow

workflow = SecurityAuditWorkflow()
result = await workflow.execute(target_path="./src")
print(result.findings)
```

## Detected Vulnerabilities

- SQL Injection
- Cross-Site Scripting (XSS)
- Path Traversal
- Command Injection
- Insecure Deserialization
- Hardcoded Secrets
- Weak Cryptography
- SSRF vulnerabilities

## Output

Returns structured findings with:
- Severity (critical, high, medium, low)
- File location and line number
- Vulnerability description
- Remediation guidance
