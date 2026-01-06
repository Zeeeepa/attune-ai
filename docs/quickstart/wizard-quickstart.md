# Wizard Factory Quick Start Guide

**How to access and use the Wizard Factory Enhancement**

---

## 🚀 Main Entry Points

The Wizard Factory is now **fully integrated** with the Empathy CLI!

### Method 1: Via Empathy CLI ⭐ **RECOMMENDED**

```bash
# Create a healthcare wizard (10 minutes)
empathy wizard create patient_intake --domain healthcare

# Create a coach wizard for code analysis
empathy wizard create code_reviewer --domain software --type coach

# List available patterns
empathy wizard list-patterns

# Interactive pattern selection
empathy wizard create my_wizard --interactive --domain finance
```

### Method 2: Direct Module Access (Alternative)

```bash
# Also works - more explicit
python -m scaffolding create patient_intake --domain healthcare
python -m scaffolding list-patterns
```

### 2. **Generate Tests** → `python -m test_generator`

**Use this to generate risk-based tests for existing wizards**

```bash
# Generate tests for a wizard
python -m test_generator generate soap_note --patterns linear_flow,approval

# Analyze risk and get coverage recommendations
python -m test_generator analyze debugging --patterns code_analysis_input,risk_assessment
```

### 3. **Run Test Suite** → `python test_wizard_factory.py`

**Use this to verify all Wizard Factory features are working**

```bash
# Run all 21 integration tests
python test_wizard_factory.py

# Test specific phase
python test_wizard_factory.py --phase 4

# Run pattern unit tests (63 tests)
pytest tests/unit/patterns/ -v
```

---

## 📋 Complete Command Reference

### Scaffolding Commands

```bash
# ============================================================
# CREATE WIZARDS
# ============================================================

# Basic usage (recommended patterns auto-selected)
python -m scaffolding create <wizard_name> --domain <domain>

# Specify wizard type
python -m scaffolding create <name> --domain <domain> --type [domain|coach|ai]

# Choose methodology
python -m scaffolding create <name> --methodology [pattern|tdd]

# Interactive pattern selection
python -m scaffolding create <name> --interactive --domain <domain>

# Manual pattern selection
python -m scaffolding create <name> --patterns linear_flow,approval,structured_fields

# ============================================================
# LIST PATTERNS
# ============================================================

# View all available patterns
python -m scaffolding list-patterns
```

### Test Generator Commands

```bash
# ============================================================
# GENERATE TESTS
# ============================================================

# Generate tests for a wizard
python -m test_generator generate <wizard_id> --patterns <pattern_ids>

# Custom output directory
python -m test_generator generate <wizard_id> --patterns <patterns> --output tests/custom/

# ============================================================
# ANALYZE RISK
# ============================================================

# Analyze wizard risk (get coverage recommendation)
python -m test_generator analyze <wizard_id> --patterns <pattern_ids>

# JSON output for CI/CD
python -m test_generator analyze <wizard_id> --patterns <patterns> --json
```

### Testing Commands

```bash
# ============================================================
# RUN TESTS
# ============================================================

# Run all Wizard Factory tests
python test_wizard_factory.py

# Test specific phase
python test_wizard_factory.py --phase [1|2|3|4]

# Verbose output
python test_wizard_factory.py --verbose

# Keep test files (don't cleanup)
python test_wizard_factory.py --no-cleanup

# Run pattern unit tests
pytest tests/unit/patterns/ -v

# Run generated wizard tests
pytest tests/unit/wizards/test_<wizard_name>_wizard.py -v
```

---

## 🎯 Common Use Cases

### Use Case 1: Create a Healthcare Wizard (Most Common)

```bash
# Step 1: Create wizard
python -m scaffolding create patient_intake --domain healthcare

# Step 2: Review generated files
ls -la empathy_llm_toolkit/wizards/patient_intake_wizard.py
ls -la tests/unit/wizards/test_patient_intake_wizard.py

# Step 3: Run generated tests
pytest tests/unit/wizards/test_patient_intake_wizard.py -v

# Step 4: Register in API (manual)
# Edit backend/api/wizard_api.py
# Add: from empathy_llm_toolkit.wizards.patient_intake_wizard import router
#      app.include_router(router, prefix="/api/wizard")

# Step 5: Test via API
curl -X POST http://localhost:8000/api/wizard/patient_intake/start
```

### Use Case 2: Create a Coach Wizard for Code Analysis

```bash
# Step 1: Create coach wizard
python -m scaffolding create code_reviewer --domain software --type coach

# Automatically includes:
# - code_analysis_input pattern
# - risk_assessment pattern
# - prediction pattern
# - fix_application pattern (if applicable)

# Step 2: Review generated coach wizard
cat coach_wizards/code_reviewer_wizard.py

# Step 3: Test
pytest tests/unit/wizards/test_code_reviewer_wizard.py -v
```

### Use Case 3: Interactive Pattern Selection

```bash
# Start interactive mode
python -m scaffolding create my_wizard --interactive --domain finance

# You'll see:
# Recommended Patterns (10):
#   1. Linear Flow - Step-by-step wizard flow
#   2. Structured Fields - Field validation
#   3. Approval - Preview before finalize
#   ...
#
# Select patterns (comma-separated numbers, or 'all' for all):
# > 1,2,3,4

# Wizard created with your selected patterns
```

### Use Case 4: TDD Methodology (Tests First)

```bash
# Generate tests FIRST, then implement
python -m scaffolding create invoice_processor --methodology tdd --domain finance

# Tests generated first in:
# tests/unit/wizards/test_invoice_processor_wizard.py

# Minimal skeleton in:
# wizards/invoice_processor_wizard.py

# Implement to make tests pass
vim wizards/invoice_processor_wizard.py

# Run tests iteratively
pytest tests/unit/wizards/test_invoice_processor_wizard.py -v
```

### Use Case 5: Generate Tests for Existing Wizard

```bash
# If you have an existing wizard, generate tests for it
python -m test_generator generate existing_wizard \
  --patterns linear_flow,approval,structured_fields

# Analyze risk first (recommended)
python -m test_generator analyze existing_wizard \
  --patterns linear_flow,approval,structured_fields

# Output shows:
# - Critical paths: 2
# - Recommended coverage: 89%
# - Test priorities (Priority 1-5)
```

---

## 🔍 Pattern Selection Guide

### View All Patterns

```bash
python -m scaffolding list-patterns
```

**Output:**
```
STRUCTURAL (3 patterns):
  - linear_flow          | Linear Flow          | Reusability: 0.90
  - phased_processing    | Phased Processing    | Reusability: 0.85
  - session_based        | Session-Based        | Reusability: 0.95

INPUT (3 patterns):
  - structured_fields    | Structured Fields    | Reusability: 0.90
  - code_analysis_input  | Code Analysis Input  | Reusability: 0.90
  - context_based_input  | Context-Based Input  | Reusability: 0.80

VALIDATION (3 patterns):
  - config_validation    | Config Validation    | Reusability: 0.90
  - step_validation      | Step Validation      | Reusability: 0.90
  - approval             | User Approval        | Reusability: 0.95

BEHAVIOR (4 patterns):
  - risk_assessment      | Risk Assessment      | Reusability: 0.80
  - ai_enhancement       | AI Enhancement       | Reusability: 0.70
  - prediction           | Prediction           | Reusability: 0.80
  - fix_application      | Fix Application      | Reusability: 0.75

EMPATHY (3 patterns):
  - empathy_level        | Empathy Level        | Reusability: 1.00
  - educational_banner   | Educational Banner   | Reusability: 1.00
  - user_guidance        | User Guidance        | Reusability: 1.00
```

### Recommended Patterns by Domain

| Domain | Recommended Patterns |
|--------|---------------------|
| **Healthcare** | linear_flow, structured_fields, approval, educational_banner, empathy_level |
| **Finance** | approval, risk_assessment, step_validation, structured_fields |
| **Software (Coach)** | code_analysis_input, risk_assessment, prediction, fix_application |
| **Legal** | approval, structured_fields, step_validation, educational_banner |
| **AI/ML** | phased_processing, context_based_input, ai_enhancement |

---

## 💻 Python API Access

You can also use the Wizard Factory programmatically:

### Pattern Library

```python
from patterns import get_pattern_registry

# Get registry
registry = get_pattern_registry()

# List all patterns
patterns = registry.list_all()
print(f"Loaded {len(patterns)} patterns")

# Get recommendations
healthcare_patterns = registry.recommend_for_wizard("domain", "healthcare")
print(f"Healthcare: {[p.id for p in healthcare_patterns]}")

# Search patterns
results = registry.search("linear")
print(f"Found {len(results)} patterns matching 'linear'")

# Get specific pattern
linear_pattern = registry.get("linear_flow")
print(f"Pattern: {linear_pattern.name}, Score: {linear_pattern.reusability_score}")
```

### Scaffolding (Create Wizards)

```python
from scaffolding import PatternCompose
from pathlib import Path

# Initialize methodology
method = PatternCompose()

# Create wizard
result = method.create_wizard(
    name="patient_intake",
    domain="healthcare",
    wizard_type="domain",
    selected_patterns=["linear_flow", "approval", "structured_fields"],
    output_dir=Path("empathy_llm_toolkit/wizards"),
)

print(f"Generated files: {result['files']}")
print(f"Patterns used: {result['patterns']}")
print(f"Next steps: {result['next_steps']}")
```

### Test Generator

```python
from test_generator import TestGenerator, RiskAnalyzer

# Analyze risk
analyzer = RiskAnalyzer()
analysis = analyzer.analyze(
    wizard_id="soap_note",
    pattern_ids=["linear_flow", "approval", "step_validation"],
)

print(f"Critical paths: {len(analysis.critical_paths)}")
print(f"Recommended coverage: {analysis.recommended_coverage}%")
print(f"Test priorities: {analysis.test_priorities}")

# Generate tests
generator = TestGenerator()
tests = generator.generate_tests(
    wizard_id="soap_note",
    pattern_ids=["linear_flow", "approval"],
)

print(f"Unit tests: {len(tests['unit'])} chars")
print(f"Fixtures: {len(tests['fixtures'])} chars")
```

### Hot-Reload (Development)

```python
from hot_reload import HotReloadIntegration
from fastapi import FastAPI

app = FastAPI()

# Initialize hot-reload
hot_reload = HotReloadIntegration(app, register_wizard)

@app.on_event("startup")
async def startup():
    hot_reload.start()
    print("Hot-reload enabled")

@app.on_event("shutdown")
async def shutdown():
    hot_reload.stop()
```

---

## 📁 Where Files Are Created

Different wizard types go to different directories:

| Wizard Type | Generated Location |
|-------------|-------------------|
| `--type domain` | `empathy_llm_toolkit/wizards/` |
| `--type coach` | `coach_wizards/` |
| `--type ai` | `wizards/` |
| Tests (all types) | `tests/unit/wizards/` |

**Example:**
```bash
# Domain wizard
python -m scaffolding create patient_intake --domain healthcare --type domain
# → empathy_llm_toolkit/wizards/patient_intake_wizard.py

# Coach wizard
python -m scaffolding create code_reviewer --domain software --type coach
# → coach_wizards/code_reviewer_wizard.py

# AI wizard
python -m scaffolding create ml_analyzer --domain ai --type ai
# → wizards/ml_analyzer_wizard.py
```

---

## 🎓 Tutorial: Your First Wizard (5 Minutes)

### Step-by-Step Tutorial

```bash
# 1. List available patterns
python -m scaffolding list-patterns

# 2. Create a simple healthcare wizard
python -m scaffolding create appointment_scheduler --domain healthcare

# 3. Check what was generated
ls -la empathy_llm_toolkit/wizards/appointment_scheduler*
ls -la tests/unit/wizards/test_appointment_scheduler*

# 4. Preview the wizard code
head -50 empathy_llm_toolkit/wizards/appointment_scheduler_wizard.py

# 5. Run the generated tests
pytest tests/unit/wizards/test_appointment_scheduler_wizard.py -v

# 6. Analyze the risk
python -m test_generator analyze appointment_scheduler \
  --patterns linear_flow,approval,structured_fields

# 7. Success! You created your first wizard
echo "✅ First wizard complete!"
```

---

## 🆘 Help & Documentation

### Get Help

```bash
# Scaffolding help
python -m scaffolding --help
python -m scaffolding create --help
python -m scaffolding list-patterns --help

# Test generator help
python -m test_generator --help
python -m test_generator generate --help
python -m test_generator analyze --help

# Test suite help
python test_wizard_factory.py --help
```

### Documentation Files

- **This guide:** [WIZARD_FACTORY_QUICKSTART.md](WIZARD_FACTORY_QUICKSTART.md)
- **Testing guide:** [WIZARD_FACTORY_TESTING.md](WIZARD_FACTORY_TESTING.md)
- **Scaffolding README:** [scaffolding/README.md](scaffolding/README.md)
- **Hot-Reload README:** [hot_reload/README.md](hot_reload/README.md)
- **Discovery report:** [docs/architecture/WIZARD_FACTORY_DISCOVERY.md](docs/architecture/WIZARD_FACTORY_DISCOVERY.md)
- **Completion report:** [docs/architecture/WIZARD_FACTORY_COMPLETION.md](docs/architecture/WIZARD_FACTORY_COMPLETION.md)

---

## 🚨 Common Issues

### Issue: Command not found

**Problem:** `python -m scaffolding` not working

**Solution:**
```bash
# Ensure you're in the correct directory
cd /path/to/empathy-framework

# Verify modules exist
ls -la scaffolding/
ls -la test_generator/
ls -la patterns/

# Try with python3
python3 -m scaffolding list-patterns
```

### Issue: Import errors

**Problem:** Module import failures

**Solution:**
```bash
# Install in development mode
pip install -e .

# Verify installation
python -c "from patterns import get_pattern_registry; print('✅ Working')"
python -c "from scaffolding import PatternCompose; print('✅ Working')"
```

### Issue: No patterns found

**Problem:** Pattern registry empty

**Solution:**
```bash
# Check pattern files exist
ls -la patterns/

# Test pattern loading
python -c "from patterns import get_pattern_registry; r = get_pattern_registry(); print(f'{len(r.list_all())} patterns loaded')"
```

---

## 📊 Next Steps

After creating your first wizard:

1. **Register with API:** Add to `backend/api/wizard_api.py`
2. **Enable hot-reload:** Set `HOT_RELOAD_ENABLED=true`
3. **Test via API:** `curl -X POST http://localhost:8000/api/wizard/<name>/start`
4. **Customize:** Edit generated wizard for your specific needs
5. **Iterate:** Use hot-reload for instant updates

---

## 🎉 You're Ready!

The Wizard Factory is accessed through simple CLI commands:

```bash
# Create wizards
python -m scaffolding create <name> --domain <domain>

# Generate tests
python -m test_generator generate <name> --patterns <patterns>

# List patterns
python -m scaffolding list-patterns

# Run tests
python test_wizard_factory.py
```

**Happy wizard building!** 🧙‍♂️✨

---

**Last Updated:** 2025-01-05
**Version:** 1.0
