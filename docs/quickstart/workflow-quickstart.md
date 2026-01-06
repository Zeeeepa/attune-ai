# Workflow Factory Quick Start Guide

**Create workflows 12x faster using extracted patterns from 17 existing workflows**

---

## 🚀 Quick Start

### Method 1: Via Empathy CLI ⭐ **RECOMMENDED**

```bash
# Create a simple workflow (1 stage)
empathy workflow create my-simple-workflow

# Create a multi-stage code analysis workflow
empathy workflow create bug-scanner \
  --patterns multi-stage,code-scanner,conditional-tier \
  --description "Scan code for potential bugs"

# Create a crew-based workflow
empathy workflow create code-review-crew \
  --patterns crew-based,result-dataclass \
  --description "Multi-agent code review"

# List available patterns
empathy workflow list-patterns

# Get pattern recommendations
empathy workflow recommend code-analysis
```

### Method 2: Direct Module Access (Alternative)

```bash
python -m workflow_scaffolding create my-workflow \
  --patterns multi-stage,conditional-tier

python -m workflow_scaffolding list-patterns

python -m workflow_scaffolding recommend code-analysis
```

---

## 📋 Available Patterns

| Pattern ID | Category | Complexity | Description |
|------------|----------|------------|-------------|
| `single-stage` | STRUCTURAL | SIMPLE | Simple one-stage workflow |
| `multi-stage` | STRUCTURAL | MODERATE | Multiple sequential stages |
| `crew-based` | INTEGRATION | COMPLEX | Wraps CrewAI crew |
| `conditional-tier` | BEHAVIOR | MODERATE | Dynamic tier routing |
| `config-driven` | BEHAVIOR | SIMPLE | Loads from empathy.config.yml |
| `code-scanner` | BEHAVIOR | MODERATE | File scanning and analysis |
| `result-dataclass` | OUTPUT | SIMPLE | Structured output format |

---

## 🎯 Common Use Cases

### Code Analysis Workflow

```bash
empathy workflow create code-analyzer \
  --patterns multi-stage,code-scanner,conditional-tier \
  --stages scan,analyze,report \
  --description "Analyze code quality and detect issues"
```

**Generated files:**
- `src/empathy_os/workflows/code_analyzer.py`
- `tests/unit/workflows/test_code_analyzer.py`
- `src/empathy_os/workflows/code_analyzer_README.md`

### Multi-Agent Workflow

```bash
empathy workflow create security-crew \
  --patterns crew-based,result-dataclass,config-driven \
  --description "Security analysis with multiple agents"
```

### Simple Single-Stage Workflow

```bash
empathy workflow create text-processor \
  --patterns single-stage \
  --description "Process text input"
```

---

## 🔧 Pattern Combinations

**Recommended combinations:**

- **Code Analysis**: `multi-stage,code-scanner,conditional-tier`
- **Multi-Agent**: `crew-based,result-dataclass`
- **Cost-Optimized**: `multi-stage,conditional-tier`
- **Configurable**: `multi-stage,config-driven`
- **Simple**: `single-stage`

**Pattern requirements:**
- `conditional-tier` requires `multi-stage`
- `crew-based` conflicts with `single-stage`

---

## 📝 Generated Files

After creating a workflow, you get:

### 1. Main Workflow File
`src/empathy_os/workflows/<name>.py`

Includes:
- Class definition inheriting from `BaseWorkflow`
- Stage definitions and tier mapping
- Helper functions (if applicable)
- Configuration loading (if applicable)
- Full implementation scaffold

### 2. Test File
`tests/unit/workflows/test_<name>.py`

Includes:
- Test suite with pytest
- Basic tests for initialization
- Tests for each pattern used
- TODO comments for custom tests

### 3. README
`src/empathy_os/workflows/<name>_README.md`

Includes:
- Usage examples
- CLI commands
- Configuration options
- Stage descriptions
- Cost optimization details

---

## 🚀 Next Steps

After generating a workflow:

1. **Review Generated Files**
   ```bash
   cat src/empathy_os/workflows/my_workflow.py
   ```

2. **Implement Stage Logic**
   - Search for `TODO` comments
   - Implement each stage's processing logic
   - Add any custom helper functions

3. **Run Tests**
   ```bash
   pytest tests/unit/workflows/test_my_workflow.py -v
   ```

4. **Configure (if using config-driven pattern)**
   ```yaml
   # empathy.config.yml
   my_workflow:
     threshold: 0.7
     enabled: true
   ```

5. **Run the Workflow**
   ```bash
   empathy workflow run my-workflow
   ```

---

## 📊 Speed Comparison

| Method | Time | Files Generated | Test Coverage |
|--------|------|-----------------|---------------|
| **Manual** | 2 hours | 3 files | 0% (manual) |
| **Workflow Factory** | 10 minutes | 3 files | 70%+ (auto-generated) |
| **Speedup** | **12x faster** | Same | Better |

---

## 🔍 Pattern Details

### single-stage
- **Use for**: Quick tasks, single API calls
- **Generates**: 1 processing stage
- **Tier**: Configurable (default: CAPABLE)

### multi-stage
- **Use for**: Complex pipelines, tiered processing
- **Generates**: Multiple sequential stages
- **Tiers**: Auto-assigned (CHEAP → CAPABLE → PREMIUM)

### crew-based
- **Use for**: Multi-agent collaboration
- **Requires**: CrewAI integration
- **Generates**: Crew initialization and execution

### conditional-tier
- **Use for**: Cost optimization
- **Requires**: multi-stage
- **Generates**: Dynamic tier routing logic

### config-driven
- **Use for**: Customizable behavior
- **Generates**: Config loading from empathy.config.yml
- **Defaults**: Included

### code-scanner
- **Use for**: Code analysis
- **Generates**: File scanning utilities
- **Supports**: Pattern matching, exclusions

### result-dataclass
- **Use for**: Type-safe outputs
- **Generates**: Dataclass with standard fields
- **Customizable**: Add custom fields

---

## 🆘 Help

```bash
# Show all workflow commands
empathy workflow --help

# Show create command options
empathy workflow create --help

# Get pattern recommendations
empathy workflow recommend <type>

# List all patterns with details
empathy workflow list-patterns
```

---

## 📚 Related Docs

- [Pattern Analysis](WORKFLOW_FACTORY_PATTERN_ANALYSIS.md) - Detailed pattern extraction
- [Progress Report](WORKFLOW_FACTORY_PROGRESS.md) - Implementation status
- [Cheatsheet](WORKFLOW_FACTORY_CHEATSHEET.md) - Quick reference

---

**Last Updated:** 2025-01-05
**Version:** 1.0
**Patterns:** 7 core patterns from 17 workflows
