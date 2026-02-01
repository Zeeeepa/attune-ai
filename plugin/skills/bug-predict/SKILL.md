---
name: bug-predict
description: "Predictive bug analysis. Triggers: 'predict bugs', 'find bugs', 'potential bugs', 'risky code', 'bug prone', 'where will bugs occur', 'code risk', 'technical debt', 'hotspots', 'regression risk', 'problematic code'."
---

# Bug Prediction

AI-powered bug prediction and risk analysis.

## Quick Start

```bash
# CLI (primary)
attune workflow run bug-predict --path ./src

# Legacy alias
empathy workflow run bug-predict --path ./src

# Natural language:
"find potential bugs in src/"
"where are bugs likely to occur?"
"identify risky code areas"
```

## Usage

### Via MCP Tool

The `bug_predict` tool is available via MCP:

```python
# Invoked automatically when you describe:
"Find potential bugs"
"Identify risky code areas"
"Where are bugs likely to occur?"
```

### Via Python

```python
from attune.workflows import BugPredictWorkflow

workflow = BugPredictWorkflow()
result = await workflow.execute(target_path="./src")
print(result.risk_areas)
```

## Analysis Factors

- **Complexity Metrics**: Cyclomatic complexity, cognitive load
- **Change Frequency**: Files with frequent modifications
- **Code Churn**: Recent high-velocity changes
- **Pattern Matching**: Known bug-prone patterns
- **Dependency Analysis**: Tightly coupled modules

## Output

Returns:
- Risk-ranked file list
- Specific concern areas with line numbers
- Confidence scores
- Recommended actions
