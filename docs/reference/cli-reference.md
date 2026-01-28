# CLI Reference

Complete reference for the `empathy` command-line interface.

---

## Quick Reference

```bash
# Workflows
empathy workflow list                    # List available workflows
empathy workflow info <name>             # Show workflow details
empathy workflow run <name> [options]    # Execute a workflow

# Telemetry
empathy telemetry show                   # Display usage summary
empathy telemetry savings                # Show cost savings
empathy telemetry export -o <file>       # Export to CSV/JSON

# Provider
empathy provider show                    # Show current provider
empathy provider set <name>              # Set provider (anthropic)

# Utilities
empathy validate                         # Validate configuration
empathy version                          # Show version
```

---

## Workflow Commands

### `empathy workflow list`

List all available workflows registered in the framework.

```bash
empathy workflow list
```

**Output:**
```
📋 Available Workflows

------------------------------------------------------------
  security-audit           Audit code for security vulnerabilities
  bug-predict              Predict potential bugs using patterns
  release-prep             Prepare release with changelog
  test-coverage            Generate tests for coverage gaps
------------------------------------------------------------

Total: 4 workflows

Run a workflow: empathy workflow run <name>
```

---

### `empathy workflow info <name>`

Show detailed information about a specific workflow.

```bash
empathy workflow info security-audit
```

**Arguments:**

| Argument | Required | Description |
|----------|----------|-------------|
| `name` | Yes | Workflow name |

---

### `empathy workflow run <name>`

Execute a workflow with optional parameters.

```bash
# Basic usage
empathy workflow run security-audit

# With target path
empathy workflow run security-audit --path ./src

# With JSON input
empathy workflow run bug-predict --input '{"threshold": 0.8}'

# Output as JSON (for CI/CD)
empathy workflow run security-audit --path ./src --json
```

**Arguments:**

| Argument | Required | Description |
|----------|----------|-------------|
| `name` | Yes | Workflow name |

**Options:**

| Option | Short | Description |
|--------|-------|-------------|
| `--path` | `-p` | Target path for analysis |
| `--input` | `-i` | JSON input data |
| `--target` | `-t` | Target value (e.g., coverage percentage) |
| `--json` | `-j` | Output result as JSON |

**Examples:**

```bash
# Security audit on src directory
empathy workflow run security-audit --path ./src

# Bug prediction with custom threshold
empathy workflow run bug-predict --input '{"path":"./src","threshold":0.7}'

# Test coverage targeting 80%
empathy workflow run test-coverage --path ./src --target 80

# CI/CD friendly output
empathy workflow run security-audit --path ./src --json > results.json
```

---

## Telemetry Commands

### `empathy telemetry show`

Display usage summary including API calls, tokens, and costs.

```bash
empathy telemetry show
empathy telemetry show --days 7
```

**Options:**

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--days` | `-d` | 30 | Number of days to summarize |

**Output:**
```
📊 Telemetry Summary

------------------------------------------------------------
  Period:         Last 30 days
  Workflow runs:  45
  Total tokens:   1,234,567
  Total cost:     $12.34
------------------------------------------------------------
```

---

### `empathy telemetry savings`

Show cost savings from intelligent tier routing.

```bash
empathy telemetry savings
empathy telemetry savings --days 90
```

**Options:**

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--days` | `-d` | 30 | Number of days to analyze |

**Output:**
```
💰 Cost Savings Report

------------------------------------------------------------
  Period:              Last 30 days
  Actual cost:         $12.34
  Premium-only cost:   $45.00 (estimated)
  Savings:             $32.66
  Savings percentage:  72.6%

  * Premium baseline assumes Claude Opus pricing (~$45/1M tokens)
------------------------------------------------------------
```

---

### `empathy telemetry export`

Export telemetry data to a file.

```bash
empathy telemetry export -o telemetry.json
empathy telemetry export -o telemetry.csv --format csv
```

**Options:**

| Option | Short | Required | Default | Description |
|--------|-------|----------|---------|-------------|
| `--output` | `-o` | Yes | - | Output file path |
| `--format` | `-f` | No | json | Output format (json/csv) |
| `--days` | `-d` | No | 30 | Number of days |

---

## Provider Commands

### `empathy provider show`

Display current LLM provider configuration.

```bash
empathy provider show
```

**Output:**
```
🔧 Provider Configuration

------------------------------------------------------------
  Mode:            SINGLE
  Primary provider: anthropic
  Cost optimization: ✅ Enabled

  Available providers:
    [✓] anthropic
------------------------------------------------------------
```

---

### `empathy provider set <name>`

Set the active LLM provider.

```bash
empathy provider set anthropic
```

**Arguments:**

| Argument | Required | Choices | Description |
|----------|----------|---------|-------------|
| `name` | Yes | `anthropic` | Provider to use |

> **Note:** As of v5.0.0, Empathy Framework is Anthropic-only. Multi-provider support may return in future versions.

---

## Utility Commands

### `empathy validate`

Validate your configuration and environment.

```bash
empathy validate
```

**Checks:**
- Configuration file (empathy.config.json/yml)
- API keys (ANTHROPIC_API_KEY)
- Workflow registration

**Output:**
```
🔍 Validating configuration...

  ✅ Config file: empathy.config.yml
  ✅ Anthropic (Claude) API key set
  ✅ 12 workflows registered

------------------------------------------------------------

✅ Configuration is valid
```

---

### `empathy version`

Show version information.

```bash
empathy version
empathy version --verbose
```

**Options:**

| Option | Short | Description |
|--------|-------|-------------|
| `--verbose` | `-v` | Show Python version and platform |

---

## Global Options

These options work with any command:

| Option | Short | Description |
|--------|-------|-------------|
| `--verbose` | `-v` | Enable debug logging |
| `--help` | `-h` | Show help for command |

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Anthropic API key (required) |
| `EMPATHY_CONFIG` | Custom config file path |
| `EMPATHY_LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING) |

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error (invalid input, workflow failed, etc.) |

---

## Related Tools

The framework includes additional CLI tools:

| Tool | Description |
|------|-------------|
| `empathy-inspect` | Code inspection pipeline |
| `empathy-memory` | Memory control panel |
| `empathy-sync-claude` | Sync patterns to Claude Code |

See [CLI Guide](CLI_GUIDE.md) for detailed documentation on these tools.

---

## Claude Code Integration

For interactive features, use Claude Code slash commands instead of CLI:

| Command | Purpose |
|---------|---------|
| `/dev` | Developer tools (debug, commit, PR) |
| `/testing` | Run tests, coverage, benchmarks |
| `/docs` | Documentation generation |
| `/release` | Release preparation |
| `/help` | Navigation hub overview |

These provide guided, conversational experiences built on top of the same framework.
