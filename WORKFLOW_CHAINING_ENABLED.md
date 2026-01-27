# Workflow Chaining - ENABLED ✅

**Status:** Automatic workflow chaining is now configured and ready to use!

---

## 🎯 What Just Happened

Created **`.empathy/workflow_chains.yaml`** with:

✅ **5 workflow chain configurations** - Smart triggers for all major workflows
✅ **6 pre-defined templates** - Ready-to-use workflow sequences
✅ **Safety controls** - Approval requirements, rate limits, cost optimization
✅ **Custom triggers** - Advanced conditions for complex scenarios

---

## 🚀 How to Use It

### Option 1: Run a Workflow (Chains Trigger Automatically)

```bash
# Run security audit
empathy workflow run security-audit

# If issues found (high_severity_count > 3):
# 🔗 Chain triggered: bug-predict
#    ✓ Auto-approved (reason: Many security issues found)
#    ⏳ Running bug-predict...

# If critical issues found:
# 🔗 Chain suggested: code-review
#    ⚠️  Approval required (reason: Critical vulnerabilities detected)
#    ❓ Run code-review? [y/N]: _
```

### Option 2: Execute a Pre-defined Template

```bash
# Full security review (4 workflows)
empathy workflow template full-security-review

# Runs in sequence:
# 1. security-audit
# 2. bug-predict
# 3. code-review
# 4. test-gen
```

### Option 3: Test Chaining with Demo

```bash
python examples/workflow_chaining_demo.py
```

---

## 📊 Configured Chains

### 1. **security-audit** → Follow-ups

| Trigger | Next Workflow | Auto? | Reason |
|---------|--------------|-------|---------|
| `high_severity_count > 3` | bug-predict | ✓ Yes | Predict related bugs |
| `critical_issues > 0` | code-review | ⚠️ Approval | Critical vuln found |
| `'sql_injection' in types` | perf-audit | ⚠️ Approval | Check resource issues |

### 2. **code-review** → Quality Assurance

| Trigger | Next Workflow | Auto? | Reason |
|---------|--------------|-------|---------|
| `files_changed > 10` | test-gen | ✓ Yes | Large changes need tests |
| `test_coverage < 0.6` | test-gen | ✓ Yes | Low coverage detected |
| `high_complexity_count > 5` | bug-predict | ✓ Yes | Complex code = bugs |
| `security_concerns > 0` | security-audit | ⚠️ Approval | Security issues found |

### 3. **bug-predict** → Prevention

| Trigger | Next Workflow | Auto? | Reason |
|---------|--------------|-------|---------|
| `high_risk_count > 5` | test-gen | ✓ Yes | Generate defensive tests |
| `'memory_leak' in patterns` | perf-audit | ✓ Yes | Audit performance |
| `dangerous_patterns > 3` | code-review | ⚠️ Approval | Manual review needed |

### 4. **perf-audit** → Optimization

| Trigger | Next Workflow | Auto? | Reason |
|---------|--------------|-------|---------|
| `critical_perf_issues > 0` | code-review | ⚠️ Approval | Critical issues found |
| `memory_issues > 3` | bug-predict | ✓ Yes | Predict related bugs |
| `optimization_score < 50` | test-gen | ✓ Yes | Tests before refactor |

### 5. **test-gen** → Verification

| Trigger | Next Workflow | Auto? | Reason |
|---------|--------------|-------|---------|
| `tests_generated > 10` | security-audit | ✓ Yes | Verify no security gaps |
| `coverage_improvement < 0.2` | bug-predict | ✓ Yes | Low coverage = risk |

---

## 📦 Pre-defined Templates

### **full-security-review**
Complete security assessment pipeline
```
security-audit → bug-predict → code-review → test-gen
```

### **qa-pipeline**
Comprehensive quality assurance
```
code-review → test-gen → bug-predict → perf-audit
```

### **pre-release**
Full validation before release
```
security-audit → perf-audit → bug-predict → test-gen
```

### **refactor-safe**
Safe refactoring with checks
```
test-gen → code-review → bug-predict
```

### **perf-optimize**
Performance optimization pipeline
```
perf-audit → code-review → test-gen
```

### **security-harden**
Security hardening pipeline
```
security-audit → bug-predict → test-gen → code-review
```

---

## ⚙️ Configuration Options

### Enable Full Auto-Approval

Edit `.empathy/workflow_chains.yaml`:

```yaml
global:
  auto_approve: true  # Change from false → true
```

**Warning:** This will run chains automatically without asking. Start with `false` to review chains first.

### Adjust Trigger Conditions

```yaml
chains:
  security-audit:
    triggers:
      - condition: "high_severity_count > 5"  # Increase threshold
        next: "bug-predict"
        approval_required: false
```

### Add Custom Chain

```yaml
chains:
  my-custom-workflow:
    triggers:
      - condition: "my_metric > threshold"
        next: "next-workflow"
        approval_required: true
        reason: "Custom trigger reason"
```

---

## 🛡️ Safety Features

### 1. **Max Chain Depth**
```yaml
max_chain_depth: 4  # Prevents infinite loops
```

### 2. **Cost Optimization**
```yaml
cost_optimization:
  skip_if_budget_low: true
  budget_threshold: 0.50  # Skip chains if < $0.50 remaining
```

### 3. **Rate Limiting**
```yaml
rate_limits:
  max_chains_per_hour: 20
  chain_cooldown: 5  # seconds between chains
```

### 4. **Approval Rules**
```yaml
approval_rules:
  require_approval_if:
    - "chain_depth > 2"  # Always ask for 3+ chain depth
    - "critical_issues > 0"
```

---

## 📊 Monitoring

### View Chain History

```bash
# JSON logs of all chain executions
cat .empathy/chain_history.jsonl
```

### Enable Verbose Logging

Edit `.empathy/workflow_chains.yaml`:

```yaml
debug:
  verbose: true
  show_trigger_eval: true
```

---

## 💡 Best Practices

### 1. **Start Conservative**
```yaml
global:
  auto_approve: false  # Review chains first
```

### 2. **Test with Small Codebases**
Run workflows on small projects to see which chains trigger.

### 3. **Monitor Costs**
```yaml
cost_optimization:
  max_chain_cost: 1.00  # Limit per chain sequence
```

### 4. **Adjust Triggers**
Fine-tune thresholds based on your workflow patterns:
- Too many chains? Increase thresholds
- Missing chains? Decrease thresholds

---

## 🎓 Real-World Example

### Scenario: Security-Sensitive Code Change

```bash
# 1. Developer runs security audit
$ empathy workflow run security-audit

# 2. Output shows:
✅ Security Audit Complete
   - High severity issues: 6
   - Critical issues: 1 (SQL injection)
   - Vulnerabilities: 3

# 3. Automatic chaining triggers:
🔗 Chain triggered: bug-predict
   ✓ Auto-approved (Many security issues found)
   ⏳ Running bug-predict...

✅ Bug Prediction Complete
   - High risk files: 8
   - Dangerous patterns: 4

# 4. Manual approval required:
🔗 Chain suggested: code-review
   ⚠️  Approval required (Critical vulnerabilities detected)
   ❓ Run code-review? [y/N]: y

⏳ Running code-review...

✅ Code Review Complete
   - Files reviewed: 15
   - Security concerns: 2
   - Recommendations: 8

# 5. Another chain triggers:
🔗 Chain triggered: test-gen
   ✓ Auto-approved (Large code changes detected)
   ⏳ Running test-gen...

✅ Test Generation Complete
   - Tests generated: 12
   - Coverage improvement: 18%

# 6. Summary
📊 Chain Execution Summary:
   - Workflows run: 4 (security-audit, bug-predict, code-review, test-gen)
   - Total time: 45 seconds
   - Total cost: $0.032
   - Issues found: 17
   - Tests generated: 12
   - Value: Comprehensive security review ✨
```

---

## 🔧 Troubleshooting

### Chains Not Triggering?

1. **Check trigger conditions:**
   ```bash
   python examples/workflow_chaining_demo.py
   ```

2. **Enable debug mode:**
   ```yaml
   debug:
     verbose: true
     show_trigger_eval: true
   ```

3. **Verify workflow outputs match conditions:**
   - `high_severity_count`, `critical_issues`, etc.

### Too Many Chains?

1. **Increase thresholds:**
   ```yaml
   condition: "high_severity_count > 10"  # Was: > 3
   ```

2. **Require more approvals:**
   ```yaml
   approval_required: true
   ```

3. **Reduce max_chain_depth:**
   ```yaml
   max_chain_depth: 2  # Was: 4
   ```

---

## 📚 Documentation

- **Configuration File:** `.empathy/workflow_chains.yaml`
- **Demo Script:** `examples/workflow_chaining_demo.py`
- **Chain History:** `.empathy/chain_history.jsonl`

---

## 🎉 Summary

**Automatic workflow chaining is now ENABLED!**

✅ Configured 5 workflow chains with intelligent triggers
✅ Created 6 pre-defined templates for common scenarios
✅ Added safety controls (approvals, limits, cost optimization)
✅ Included comprehensive examples and documentation

**Next Steps:**

1. **Test it:** `empathy workflow run security-audit`
2. **Review:** `.empathy/workflow_chains.yaml`
3. **Customize:** Adjust triggers to fit your workflow
4. **Monitor:** Check `.empathy/chain_history.jsonl`

**The framework will now automatically suggest follow-up workflows based on results!** 🚀
