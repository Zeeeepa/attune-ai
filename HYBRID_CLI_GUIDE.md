# Hybrid CLI Guide - Slash Commands + Natural Language

**Version:** 1.0
**Created:** January 27, 2026

---

## 🎯 Overview

Empathy Framework supports **four levels of interaction**, from structured slash commands to natural language. Choose what feels natural - they all work together!

| Level | Style | Example | Best For |
|-------|-------|---------|----------|
| **1. Discovery** | `/help` | Explore available commands | New users |
| **2. Structured** | `/dev commit` | Direct execution | Power users |
| **3. Inference** | `commit` | Quick shortcuts | Speed |
| **4. Natural** | `"commit my stuff"` | Conversational | Exploration |

---

## 📚 Level 1: Discovery (Slash Commands)

### **Purpose:** Learn what's available

```bash
# Show all hubs
$ empathy /help

📚 Available Hubs:
  /dev      - Development tools (commits, reviews, refactoring)
  /testing  - Test generation and coverage analysis
  /learning - Session evaluation and pattern learning
  /workflows - AI-powered workflows (security, bugs, performance)
  /context  - Memory and state management
  /docs     - Documentation generation
  /plan     - Development planning
  /release  - Release preparation
  /utilities - Profiling, dependencies

# Explore a specific hub
$ empathy /dev

🛠️ Development Tools:
  commit      - Create AI-generated git commit
  review-pr   - Review pull request
  refactor    - Refactoring assistant
  perf-audit  - Performance analysis

# Get help on specific command
$ empathy /dev commit --help
```

---

## 🎯 Level 2: Structured Usage (Direct Commands)

### **Purpose:** Fast, predictable execution

```bash
# Development
$ empathy /dev commit
$ empathy /dev review-pr 123
$ empathy /dev refactor auth.py

# Testing
$ empathy /testing run
$ empathy /testing coverage
$ empathy /testing gen

# Workflows
$ empathy /workflows security-audit
$ empathy /workflows bug-predict
$ empathy /workflows perf-audit

# Learning
$ empathy /learning evaluate
$ empathy /learning patterns
```

**Benefit:** Predictable, structured, IDE-friendly

---

## ⚡ Level 3: Command Inference (Keywords)

### **Purpose:** Quick shortcuts without full slash command

```bash
# Single word - framework infers the slash command
$ empathy commit
🤖 Running /dev commit
   (equivalent slash command shown)

$ empathy test
🤖 Running /testing run

$ empathy security
🤖 Running /workflows security-audit

$ empathy review
🤖 Running /dev review-pr
```

### Built-in Keyword Mappings:

| Keyword | Infers | Description |
|---------|--------|-------------|
| `commit` | `/dev commit` | Create commit |
| `test` | `/testing run` | Run tests |
| `tests` | `/testing run` | Run tests |
| `coverage` | `/testing coverage` | Test coverage |
| `security` | `/workflows security-audit` | Security scan |
| `bugs` | `/workflows bug-predict` | Bug prediction |
| `review` | `/dev review-pr` | PR review |
| `refactor` | `/dev refactor` | Refactoring |
| `perf` | `/dev perf-audit` | Performance |
| `evaluate` | `/learning evaluate` | Session eval |
| `status` | `/context status` | Check status |
| `explain` | `/docs explain` | Explain code |

**Benefit:** Fast typing, muscle memory

---

## 💬 Level 4: Natural Language (AI Routing)

### **Purpose:** Conversational, exploratory

```bash
# Natural language - framework understands intent
$ empathy "I want to commit my changes"
🤖 I think you mean: /dev commit
✓ Running in 3s (Ctrl+C to cancel)
⏳ Creating commit...

$ empathy "run security check on auth.py"
🤖 Running: /workflows security-audit
   Context: auth.py
   Confidence: 95%

$ empathy "something's slow in the API"
🤖 I think you mean: /dev perf-audit
   Reasoning: User mentioned performance issue
✓ Proceed? [Y/n]: _

$ empathy "generate tests for my new feature"
🤖 Running: /testing gen
   Secondary: /dev review (suggested)
```

### Natural Language Patterns:

| What You Say | Framework Understands | Routes To |
|--------------|----------------------|-----------|
| "commit this" | Commit workflow | `/dev commit` |
| "run tests" | Test execution | `/testing run` |
| "security check" | Security audit | `/workflows security-audit` |
| "find bugs" | Bug prediction | `/workflows bug-predict` |
| "review my code" | Code review | `/dev review-pr` |
| "slow performance" | Performance audit | `/dev perf-audit` |
| "generate docs" | Documentation | `/docs generate` |
| "what should I do?" | Status check | `/context status` |

**Benefit:** No learning curve, intuitive

---

## 🎓 Learning System

The framework learns your preferences over time:

### Example: Teaching Custom Shortcuts

```bash
# First time: Use natural language
$ empathy "deploy to production"
🤖 I think you mean: /release prep
✓ Proceed? [Y/n]: y
⏳ Running release prep...
✅ Complete

📚 Learn this shortcut?
   "deploy" → /release prep
   [Y/n]: y
✅ Learned!

# Next time: Use the shortcut
$ empathy deploy
🤖 Running /release prep (learned preference)
   Confidence: 80%
   Usage count: 1

# After 5 uses: Higher confidence
$ empathy deploy
✅ Running /release prep (94% confidence)
```

### Preference File

Stored in `~/.empathy/routing_preferences.yaml`:

```yaml
preferences:
  deploy:
    slash_command: /release prep
    usage_count: 5
    confidence: 0.94

  ship:
    slash_command: /release publish
    usage_count: 3
    confidence: 0.85

  fix:
    slash_command: /workflows bug-predict
    usage_count: 10
    confidence: 0.98
```

---

## 🔀 Comparison: All Four Levels

### Scenario: Commit Changes

**Level 1 (Discovery):**
```bash
$ empathy /help
$ empathy /dev
$ empathy /dev commit
```
👍 Great for learning

**Level 2 (Structured):**
```bash
$ empathy /dev commit
```
👍 Fast and predictable

**Level 3 (Inference):**
```bash
$ empathy commit
```
👍 Fastest typing

**Level 4 (Natural):**
```bash
$ empathy "commit my changes"
```
👍 Most intuitive

---

## 🎯 Which Level Should I Use?

### Use Slash Commands When:
- ✅ Learning the framework (discovery)
- ✅ Need predictable behavior
- ✅ Using IDE integrations
- ✅ Writing scripts/automation
- ✅ Sharing commands with team

### Use Keywords When:
- ✅ You know what you want (muscle memory)
- ✅ Speed is priority
- ✅ Command is unambiguous

### Use Natural Language When:
- ✅ Exploring new features
- ✅ Not sure exact command
- ✅ Context-dependent actions
- ✅ Voice commands
- ✅ Conversational flow

---

## 💡 Pro Tips

### 1. Mix and Match

```bash
# Morning routine: Discovery
$ empathy /context status

# During work: Quick keywords
$ empathy test
$ empathy commit

# Exploration: Natural language
$ empathy "what's causing this error?"

# End of day: Structured
$ empathy /learning evaluate
```

### 2. Autocomplete

```bash
# Start typing, framework suggests
$ empathy com<TAB>
  commit → /dev commit
  coverage → /testing coverage

$ empathy sec<TAB>
  security → /workflows security-audit
```

### 3. Show Slash Equivalent

All routing shows the slash command equivalent:

```bash
$ empathy "run security scan"
🤖 Running: /workflows security-audit
   (You can also type: empathy /workflows security-audit)
```

### 4. Confidence Threshold

Framework asks for confirmation if uncertain:

```bash
$ empathy "optimize"
🤖 I think you mean: /dev perf-audit (confidence: 68%)
   Proceed? [Y/n]: _

# High confidence = auto-run
$ empathy "commit"
✅ Running /dev commit (confidence: 95%)
```

---

## 🛠️ Configuration

### Set Confidence Threshold

Edit `~/.empathy/routing_preferences.yaml`:

```yaml
settings:
  # Auto-run if confidence > threshold
  confidence_threshold: 0.8  # Default: 0.8 (80%)

  # Show slash equivalent always
  show_slash_equivalent: true

  # Learn new shortcuts automatically
  auto_learn: true

  # Confirmation timeout
  confirmation_timeout: 5  # seconds
```

### Disable Natural Language

```yaml
settings:
  enable_natural_language: false  # Only slash commands & keywords
```

### Add Custom Keywords

```yaml
preferences:
  my-custom-shortcut:
    slash_command: /workflows custom-workflow
    confidence: 1.0
```

---

## 📊 Examples by Use Case

### New User Learning Framework

```bash
# Day 1: Discovery
empathy /help          # What's available?
empathy /dev           # Development tools?
empathy /dev commit    # How to commit?

# Day 2: Starting to use shortcuts
empathy commit         # Faster!

# Day 3: Natural language
empathy "run tests"    # Even easier!
```

### Power User with Muscle Memory

```bash
# Morning
commit
test
review

# Afternoon
security
perf

# Evening
evaluate
```

### Team Lead Writing Scripts

```bash
#!/bin/bash
# pre-commit.sh

empathy /testing run || exit 1
empathy /workflows security-audit || exit 1
empathy /dev commit
```

### Voice Commands

```bash
# Voice assistant integration
"Empathy, commit my changes"
"Empathy, run security check"
"Empathy, what should I work on next?"
```

---

## 🎉 Summary

### **Slash Commands** = Structure + Discovery
- Predictable, documented, IDE-friendly
- Best for: Learning, automation, sharing

### **Keywords** = Speed + Muscle Memory
- Fast, unambiguous, efficient
- Best for: Daily workflow, repeated actions

### **Natural Language** = Flexibility + Exploration
- Intuitive, conversational, zero learning curve
- Best for: Discovery, context-dependent, voice

### **Together** = Best of All Worlds
- Choose what feels natural
- Framework adapts to you
- Seamless integration

---

## 📚 Next Steps

1. **Try the demo:**
   ```bash
   python examples/hybrid_cli_demo.py
   ```

2. **Start with discovery:**
   ```bash
   empathy /help
   ```

3. **Use what feels natural:**
   - Structured? `empathy /dev commit`
   - Quick? `empathy commit`
   - Natural? `empathy "commit my stuff"`

4. **Let the framework learn:**
   - It adapts to your style
   - Preferences saved automatically
   - Gets smarter with use

---

**The framework supports your style, not the other way around!** 🎯
