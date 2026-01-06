# Wizard Factory Cheat Sheet

**Quick reference for creating wizards 12x faster**

> **Note:** Wizards are interactive, step-by-step processes. This is different from workflows (automated processes) and agents (AI-powered systems).

---

## 🚀 Access Methods

### VSCode Command Palette (Recommended)

Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux):

- **Empathy: Create Wizard (12x faster)** - Interactive wizard creation
- **Empathy: List Wizard Patterns** - Browse available patterns
- **Empathy: Generate Wizard Tests** - Generate tests for a wizard
- **Empathy: Analyze Wizard Risk** - Analyze risk and coverage

Keyboard shortcut: `Cmd+Shift+E Z` (Mac) / `Ctrl+Shift+E Z` (Windows/Linux)

### CLI Commands

```bash
# Create a wizard
empathy wizard create <name> --domain <domain>

# List available patterns
empathy wizard list-patterns

# Generate tests
empathy wizard generate-tests <wizard_id> --patterns <patterns>

# Analyze risk
empathy wizard analyze <wizard_id> --patterns <patterns>
```

### Direct Python Module Access

```bash
# Alternative access (if empathy CLI not installed)
python -m scaffolding create <name> --domain <domain>
python -m scaffolding list-patterns
python -m test_generator generate <name> --patterns <patterns>
python -m test_generator analyze <name> --patterns <patterns>
```

---

## 📋 Common Examples

### Healthcare Wizard

```bash
python -m scaffolding create patient_intake --domain healthcare
```

**Generated files:**
- `empathy_llm_toolkit/wizards/patient_intake_wizard.py`
- `tests/unit/wizards/test_patient_intake_wizard.py`
- `tests/unit/wizards/fixtures_patient_intake.py`
- `empathy_llm_toolkit/wizards/patient_intake_README.md`

### Coach Wizard (Code Analysis)

```bash
python -m scaffolding create code_reviewer --domain software --type coach
```

**Generated files:**
- `coach_wizards/code_reviewer_wizard.py`
- `tests/unit/wizards/test_code_reviewer_wizard.py`
- (+ fixtures and README)

### Interactive Mode

```bash
python -m scaffolding create my_wizard --interactive --domain finance
```

Prompts you to select patterns interactively.

---

## 🎯 Pattern Categories

| Category | Common Patterns |
|----------|----------------|
| **Structural** | linear_flow, phased_processing, session_based |
| **Input** | structured_fields, code_analysis_input, context_based_input |
| **Validation** | config_validation, step_validation, approval |
| **Behavior** | risk_assessment, ai_enhancement, prediction, fix_application |
| **Empathy** | empathy_level, educational_banner, user_guidance |

---

## 🔧 Options Reference

### Create Command

```bash
python -m scaffolding create <name> [OPTIONS]
```

| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `--domain` | `-d` | Domain (healthcare, finance, software) | `-d healthcare` |
| `--type` | `-t` | Wizard type (domain, coach, ai) | `-t coach` |
| `--methodology` | `-m` | Methodology (pattern, tdd) | `-m tdd` |
| `--patterns` | `-p` | Manual pattern selection | `-p linear_flow,approval` |
| `--interactive` | `-i` | Interactive pattern selection | `-i` |

### Test Generator

```bash
python -m test_generator generate <name> [OPTIONS]
python -m test_generator analyze <name> [OPTIONS]
```

| Option | Short | Description |
|--------|-------|-------------|
| `--patterns` | `-p` | Comma-separated pattern IDs (REQUIRED) |
| `--output` | `-o` | Output directory for tests |
| `--json` |  | JSON output format (analyze only) |

---

## 📁 Output Locations

| Wizard Type | Location |
|-------------|----------|
| Domain (`--type domain`) | `empathy_llm_toolkit/wizards/` |
| Coach (`--type coach`) | `coach_wizards/` |
| AI (`--type ai`) | `wizards/` |
| **Tests (all types)** | `tests/unit/wizards/` |

---

## 💡 Quick Workflow

```bash
# 1. Create wizard
python -m scaffolding create my_wizard --domain healthcare

# 2. Review generated files
ls -la empathy_llm_toolkit/wizards/my_wizard*

# 3. Run generated tests
pytest tests/unit/wizards/test_my_wizard_wizard.py -v

# 4. Analyze risk
python -m test_generator analyze my_wizard \
  --patterns linear_flow,approval,structured_fields
```

---

## 🆘 Help Commands

```bash
# Main help
python -m scaffolding --help
python -m test_generator --help

# Command-specific help
python -m scaffolding create --help
python -m test_generator generate --help
python -m test_generator analyze --help
```

---

## 📊 Success Metrics

- **Creation time:** ~10 minutes (vs 2 hours manual)
- **Test generation:** ~10 seconds (vs 1 hour manual)
- **Test coverage:** 70-95% (risk-based, not arbitrary)
- **Patterns available:** 16 patterns across 5 categories

---

## 📚 Full Documentation

- **Quick Start:** [WIZARD_FACTORY_QUICKSTART.md](WIZARD_FACTORY_QUICKSTART.md)
- **Testing Guide:** [WIZARD_FACTORY_TESTING.md](WIZARD_FACTORY_TESTING.md)
- **Detailed Guide:** [scaffolding/README.md](scaffolding/README.md)
- **Completion Report:** [docs/architecture/WIZARD_FACTORY_COMPLETION.md](docs/architecture/WIZARD_FACTORY_COMPLETION.md)

---

## ✅ Verification

Test that everything works:

```bash
# Run test suite (21 tests)
python test_wizard_factory.py

# Run pattern unit tests (63 tests)
pytest tests/unit/patterns/ -v
```

**Expected:** All tests passing ✅

---

**Version:** 1.0 | **Last Updated:** 2025-01-05
