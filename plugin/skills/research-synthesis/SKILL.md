---
name: research-synthesis
description: "Research and synthesis. Triggers: 'research', 'synthesize', 'learn this codebase', 'how does this work', 'explain the architecture', 'competitive analysis', 'best practices for', 'compare approaches', 'technical research'."
---

# Research Synthesis

AI-powered research and knowledge synthesis.

## Quick Start

```bash
# CLI
attune workflow run research-synthesis --topic "authentication patterns"

# Legacy alias
empathy workflow run research-synthesis --topic "auth"
```

## Usage

### Via Script

```bash
python scripts/run.py --topic "microservices patterns" --depth deep
```

### Via Python

```python
from attune.workflows import ResearchSynthesisWorkflow

workflow = ResearchSynthesisWorkflow()
result = await workflow.execute(
    topic="authentication best practices",
    sources=["./src", "docs"]
)
```

## Features

- Multi-source analysis
- Pattern extraction
- Best practice identification
- Comparison matrices
- Recommendation synthesis

## Output

- Executive summary
- Detailed findings
- Source citations
- Actionable recommendations
