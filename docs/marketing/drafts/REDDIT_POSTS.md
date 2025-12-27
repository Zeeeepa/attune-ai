# Reddit Posts - Ready to Copy/Paste (v3.3.0)

---

## r/ClaudeAI

**Title:** v3.3.0: Enterprise-ready workflows with formatted reports + persistent memory

**Body:**

Just shipped [Empathy Framework v3.3.0](https://github.com/Smart-AI-Memory/empathy-framework) with features I've wanted for production Claude apps:

**Formatted reports for all workflows:**

```python
from empathy_os.workflows import SecurityAuditWorkflow

workflow = SecurityAuditWorkflow()
result = await workflow.execute(code=your_code)

print(result.final_output["formatted_report"])
```

Output is clean, consistent, and shareable:

```
============================================================
SECURITY AUDIT REPORT
============================================================
Status: NEEDS_ATTENTION
Risk Score: 7.2/10
Vulnerabilities Found: 3
------------------------------------------------------------
CRITICAL FINDINGS
- SQL injection in user_query() at line 42
- Hardcoded credentials in config.py
============================================================
```

**Enterprise doc-gen with cost guardrails:**

```python
workflow = DocumentGenerationWorkflow(
    export_path="docs/generated",  # Auto-save to disk
    max_cost=5.0,                  # Stop at $5 (no surprises)
    chunked_generation=True,       # Handle large codebases
)
```

**Still saving 80% on costs** with smart routing (Haiku for simple, Sonnet for code review, Opus for architecture).

**Persistent memory** across sessions - Claude remembers your preferences.

```bash
pip install empathy-framework==3.3.0
```

Happy to answer questions about the implementation.

---

## r/Python

**Title:** empathy-framework v3.3.0: Enterprise-ready AI workflows with formatted reports

**Body:**

Just released v3.3.0 of [empathy-framework](https://pypi.org/project/empathy-framework/) - major update focused on production readiness.

**What's new:**

1. **Formatted reports for all 10 workflows** - Consistent, readable output you can share with stakeholders

2. **Enterprise doc-gen** - Auto-scaling tokens, chunked generation, cost guardrails, file export

3. **Output chunking** - Large reports split automatically (no more terminal truncation)

**Example - Security Audit:**

```python
from empathy_os.workflows import SecurityAuditWorkflow

workflow = SecurityAuditWorkflow()
result = await workflow.execute(code=your_code)

# Clean, formatted output
print(result.final_output["formatted_report"])
```

**Example - Doc-Gen with guardrails:**

```python
from empathy_os.workflows import DocumentGenerationWorkflow

workflow = DocumentGenerationWorkflow(
    export_path="docs/generated",  # Auto-save
    max_cost=5.0,                  # Cost limit
    chunked_generation=True,       # Handle large projects
    graceful_degradation=True,     # Partial results on errors
)
```

**Cost optimization (80% savings):**

```python
from empathy_llm_toolkit import EmpathyLLM

llm = EmpathyLLM(provider="hybrid", enable_model_routing=True)

# Routes to appropriate tier automatically
await llm.interact(user_id="dev", task_type="summarize")     # → Haiku
await llm.interact(user_id="dev", task_type="architecture")  # → Opus
```

**Quick start:**

```bash
pip install empathy-framework==3.3.0
python -m empathy_os.models.cli provider --set anthropic
```

GitHub: https://github.com/Smart-AI-Memory/empathy-framework

What workflows would be most useful for your projects?

---

## r/LocalLLaMA

**Title:** Enterprise doc-gen for local LLMs - auto-scaling, cost guardrails (v3.3.0)

**Body:**

Built [Empathy Framework](https://github.com/Smart-AI-Memory/empathy-framework) for LLM workflows with persistent memory. v3.3.0 adds enterprise features that work great with local models.

**New in v3.3.0:**

1. **Formatted reports** - All 10 workflows return clean, consistent output
2. **Enterprise doc-gen** - Chunked generation, auto-scaling, file export
3. **Cost tracking** - Even for local models (helps estimate cloud migration)

**Ollama setup:**

```bash
# Install Ollama (if not already)
# macOS: brew install ollama
# Linux: curl -fsSL https://ollama.com/install.sh | sh

# Pull the models for each tier
ollama pull llama3.2:3b    # cheap tier - fast
ollama pull llama3.1:8b    # capable tier - balanced
ollama pull llama3.1:70b   # premium tier - best quality (requires ~40GB RAM)

# Start Ollama
ollama serve
```

**Ollama integration:**

```python
from empathy_llm_toolkit import EmpathyLLM

llm = EmpathyLLM(provider="ollama", memory_enabled=True)

# Memory persists across sessions
await llm.interact(user_id="dev", user_input="Generate docs for this module")
```

**Hybrid mode:**

```bash
empathy provider set hybrid
```

- Local (Ollama) for sensitive code and quick tasks
- Claude for complex architecture decisions
- Automatic fallback if local model unavailable

**Smart tier routing for local:**

- Cheap: `llama3.2:3b` (3B params, ~2GB)
- Capable: `llama3.1:8b` (8B params, ~5GB)
- Premium: `llama3.1:70b` (70B params, ~40GB)

**Enterprise doc-gen works great locally:**

```python
workflow = DocumentGenerationWorkflow(
    export_path="docs/generated",
    chunked_generation=True,  # Handles context limits
)
```

Chunks large docs into sections your local model can handle.

```bash
pip install empathy-framework==3.3.0
```

Feedback welcome from the local LLM community.

---

## r/MachineLearning (if appropriate)

**Title:** [P] Empathy Framework v3.3.0 - Enterprise-ready LLM workflows with formatted reports

**Body:**

Open source Python framework for production LLM applications. v3.3.0 adds enterprise features.

**Problem:** LLM workflows return raw JSON. Hard to audit, share, or display large outputs.

**Solution:** Formatted reports with consistent structure across all workflows, plus enterprise doc-gen with cost guardrails.

**Key features in v3.3.0:**

1. **Formatted reports** - Every workflow returns `formatted_report` with consistent structure
2. **Enterprise doc-gen** - Auto-scaling tokens, chunked generation, $5 cost guardrail, file export
3. **Output chunking** - Large reports split for display (no more 50k char truncation)
4. **Smart routing** - 80% cost savings (Haiku/Sonnet/Opus based on task)
5. **Persistent memory** - Cross-session context that survives restarts

**Architecture:**

- 10 cost-optimized workflows (security-audit, code-review, doc-gen, etc.)
- Provider-agnostic (Anthropic, OpenAI, Ollama, hybrid)
- Redis-based memory with pattern detection

GitHub: https://github.com/Smart-AI-Memory/empathy-framework
PyPI: `pip install empathy-framework==3.3.0`

Looking for feedback on the workflow architecture.
