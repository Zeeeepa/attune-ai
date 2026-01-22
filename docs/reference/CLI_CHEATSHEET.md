# Empathy Framework CLI Cheatsheet

Quick reference for Empathy Framework commands. Full docs at [smartaimemory.com/framework-docs](https://www.smartaimemory.com/framework-docs/).

---

## Installation

```bash
pip install empathy-framework
```

---

## Workflows

### Code Analysis (8 commands)

```bash
empathy code-review .          # Multi-tier code analysis
empathy security-audit .       # OWASP vulnerability scanning
empathy test-gen .             # Generate tests for coverage gaps
empathy bug-predict .          # Predict bugs from patterns
empathy doc-gen .              # Generate documentation
empathy perf-audit .           # Performance analysis
empathy refactor-plan .        # Tech debt prioritization
empathy dependency-check .     # Dependency audit
```

### Release (3 commands)

```bash
empathy release-prep .         # Release readiness check
empathy health-check .         # Project health check
empathy test-coverage-boost .  # Boost test coverage
```

### Review (3 commands)

```bash
empathy pr-review .            # Pull request review
empathy pro-review .           # Professional code review
empathy secure-release .       # Security-focused release
```

### Workflow Options

All workflows support:

```bash
empathy <workflow> .           # Analyze current directory
empathy <workflow> ./src       # Analyze specific path
empathy <workflow> . --json    # JSON output for automation
```

---

## Reports

```bash
empathy report                 # List available reports
empathy report costs           # API cost tracking
empathy report health          # Project health summary
empathy report coverage        # Test coverage
empathy report patterns        # Learned patterns
empathy report metrics         # Project metrics
empathy report telemetry       # LLM usage telemetry
empathy report dashboard       # Open web dashboard
```

### Dashboard Options

```bash
empathy report dashboard                # Default port 8765
empathy report dashboard --port 9000    # Custom port
empathy report dashboard --no-browser   # Don't open browser
```

---

## Code Inspection

```bash
empathy scan .                 # Quick scan for issues
empathy scan . --fix           # Auto-fix issues
empathy scan . --staged        # Staged files only

empathy inspect .              # Deep inspection
empathy inspect . --format sarif   # SARIF for CI/CD

empathy fix                    # Auto-fix lint/format
```

---

## Memory & Patterns

```bash
empathy memory                 # Show status (default)
empathy memory status          # Check Redis & patterns
empathy memory start           # Start Redis server
empathy memory stop            # Stop Redis
empathy memory patterns        # List stored patterns
```

---

## Pattern Learning

```bash
empathy learn                  # Learn from last 20 commits
empathy learn --analyze 50     # Learn from last 50 commits
empathy sync-claude            # Sync to Claude Code memory
```

---

## Tier Optimization

```bash
empathy tier setup --show              # Show current config
empathy tier setup --default CAPABLE   # Set default tier
empathy tier setup --max-cost 0.50     # Set cost limit
empathy tier setup --auto-escalate     # Enable auto-escalation

empathy tier recommend "fix login bug"     # Get tier recommendation
empathy tier recommend "refactor auth" --files auth.py,login.py
```

---

## Project Setup

```bash
empathy init                   # Initialize new project
empathy new --list             # List project templates
empathy new minimal my-proj    # Create from template
empathy onboard                # Interactive tutorial
empathy explain <command>      # Explain a command
empathy --version              # Show version
empathy cheatsheet             # Show this reference
```

---

## CI/CD Integration

### GitHub Actions (SARIF)

```yaml
- name: Run Empathy Inspect
  run: empathy inspect . --format sarif -o results.sarif

- name: Upload SARIF
  uses: github/codeql-action/upload-sarif@v2
  with:
    sarif_file: results.sarif
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: empathy-security
        name: Security audit
        entry: empathy security-audit . --json
        language: system
        pass_filenames: false
```

---

## Environment Variables

```bash
ANTHROPIC_API_KEY=sk-...          # Claude API key (required)
OPENAI_API_KEY=sk-...             # OpenAI key (optional)
EMPATHY_CONFIG=./config.yaml      # Custom config path
REDIS_URL=redis://localhost:6379  # Redis connection
```

---

## Getting Help

```bash
empathy --help                 # Main help
empathy <command> --help       # Command-specific help
empathy cheatsheet             # Quick reference
```

---

*Empathy Framework v4.6.6 | [GitHub](https://github.com/Smart-AI-Memory/empathy-framework) | [Docs](https://www.smartaimemory.com/framework-docs/)*
