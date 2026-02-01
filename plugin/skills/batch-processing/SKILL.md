---
name: batch-processing
description: "Batch processing for cost savings. Triggers: 'batch', 'bulk processing', 'save money', 'async processing', 'queue jobs', 'batch API', '50% savings', 'non-urgent', 'process many files', 'large scale'."
---

# Batch Processing

50% cost savings via Anthropic's Batch API.

## Quick Start

```bash
# CLI
attune batch submit requests.json
attune batch status <batch_id>
attune batch results <batch_id> output.json

# Legacy alias
empathy batch submit requests.json
```

## Usage

### Via Script

```bash
python scripts/run.py submit --input requests.json
python scripts/run.py status --batch-id msgbatch_abc123
python scripts/run.py results --batch-id msgbatch_abc123
```

### Via Python

```python
from attune.workflows import BatchProcessingWorkflow

workflow = BatchProcessingWorkflow()
batch_id = await workflow.submit(requests)
results = await workflow.get_results(batch_id)
```

## Use Cases

- Bulk code analysis
- Mass test generation
- Large-scale documentation
- Report generation
- Log analysis

## Output

- Batch job ID
- Status tracking
- Results in JSON format
- Cost comparison (batch vs real-time)
