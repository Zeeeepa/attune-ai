---
name: document-gen
description: "Documentation generation. Triggers: 'generate docs', 'write documentation', 'API docs', 'README', 'docstrings', 'document this code', 'update docs', 'architecture diagram', 'usage guide', 'explain this code'."
---

# Document Generation

AI-powered documentation creation and maintenance.

## Quick Start

```bash
# CLI
attune workflow run document-gen --path ./src

# Legacy alias
empathy workflow run document-gen --path ./src
```

## Usage

### Via Script

```bash
python scripts/run.py --path ./src --output ./docs
```

### Via Python

```python
from attune.workflows import DocumentGenWorkflow

workflow = DocumentGenWorkflow()
result = await workflow.execute(
    target_path="./src",
    output_dir="./docs"
)
```

## Document Types

- **API Reference**: Function/class documentation
- **README**: Project overview and quickstart
- **Architecture**: System design docs
- **Tutorials**: Step-by-step guides
- **Changelog**: Version history

## Output

- Markdown files
- Docstring suggestions
- Coverage report (documented vs undocumented)
