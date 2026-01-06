# Workflow Factory Cheat Sheet

**Quick reference for creating workflows 12x faster**

> **Note:** Workflows are automated processes. This is different from wizards (interactive processes) and agents (AI-powered systems).

---

## 🚀 Essential Commands

```bash
# Create a workflow
empathy workflow create <name> --patterns <patterns>

# List available patterns
empathy workflow list-patterns

# Get recommendations
empathy workflow recommend <type>

# Run a workflow
empathy workflow run <name>
```

---

## 📋 Common Examples

### Code Analysis Workflow

```bash
empathy workflow create bug-scanner \
  --patterns multi-stage,code-scanner,conditional-tier \
  --description "Scan code for bugs"
```

**Generated files:**
- `src/empathy_os/workflows/bug_scanner.py`
- `tests/unit/workflows/test_bug_scanner.py`
- `src/empathy_os/workflows/bug_scanner_README.md`

### Multi-Agent Workflow (CrewAI)

```bash
empathy workflow create security-audit \
  --patterns crew-based,result-dataclass \
  --description "Security audit with multiple agents"
```

### Simple Workflow

```bash
empathy workflow create text-analyzer \
  --patterns single-stage \
  --description "Analyze text input"
```

---

## 🎯 Pattern Quick Reference

| Pattern | Use For | Complexity |
|---------|---------|------------|
| `single-stage` | Simple tasks | SIMPLE |
| `multi-stage` | Complex pipelines | MODERATE |
| `crew-based` | Multi-agent tasks | COMPLEX |
| `conditional-tier` | Cost optimization | MODERATE |
| `config-driven` | Customizable behavior | SIMPLE |
| `code-scanner` | Code analysis | MODERATE |
| `result-dataclass` | Type-safe output | SIMPLE |

---

## 🔧 Pattern Combinations

**Recommended:**
- Code Analysis: `multi-stage,code-scanner,conditional-tier`
- Multi-Agent: `crew-based,result-dataclass`
- Cost-Optimized: `multi-stage,conditional-tier`
- Configurable: `multi-stage,config-driven`

**Rules:**
- `conditional-tier` requires `multi-stage`
- `crew-based` conflicts with `single-stage`

---

## 📁 Output Locations

| File Type | Location |
|-----------|----------|
| Workflow | `src/empathy_os/workflows/<name>.py` |
| Tests | `tests/unit/workflows/test_<name>.py` |
| README | `src/empathy_os/workflows/<name>_README.md` |

---

## 💡 Quick Workflow

```bash
# 1. Create workflow
empathy workflow create my-workflow \
  --patterns multi-stage,conditional-tier

# 2. Review generated files
cat src/empathy_os/workflows/my_workflow.py

# 3. Implement TODOs
# Search for TODO comments and implement logic

# 4. Run tests
pytest tests/unit/workflows/test_my_workflow.py -v

# 5. Run workflow
empathy workflow run my-workflow
```

---

## 🆘 Help Commands

```bash
# Main help
empathy workflow --help

# Create command help
empathy workflow create --help

# List all patterns
empathy workflow list-patterns

# Get recommendations
empathy workflow recommend code-analysis
empathy workflow recommend multi-agent
```

---

## 📊 Success Metrics

- **Creation time:** ~10 minutes (vs 2 hours manual)
- **Files generated:** 3 files with full scaffold
- **Test coverage:** 70%+ auto-generated
- **Patterns available:** 7 patterns from 17 workflows
- **Speedup:** 12x faster than manual

---

## 📚 Full Documentation

- **Quick Start:** [WORKFLOW_FACTORY_QUICKSTART.md](WORKFLOW_FACTORY_QUICKSTART.md)
- **Pattern Analysis:** [WORKFLOW_FACTORY_PATTERN_ANALYSIS.md](WORKFLOW_FACTORY_PATTERN_ANALYSIS.md)
- **Progress:** [WORKFLOW_FACTORY_PROGRESS.md](WORKFLOW_FACTORY_PROGRESS.md)

---

## ✅ Verification

Test that everything works:

```bash
# Create a test workflow
empathy workflow create test-workflow --patterns single-stage

# Verify files created
ls src/empathy_os/workflows/test_workflow*
ls tests/unit/workflows/test_test_workflow.py

# Run tests
pytest tests/unit/workflows/test_test_workflow.py
```

**Expected:** All files created, tests pass ✅

---

**Version:** 1.0 | **Last Updated:** 2025-01-05
