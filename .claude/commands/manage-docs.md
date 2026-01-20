# /manage-docs - Documentation Management Workflow

Keep documentation in sync with code using AI-powered analysis.

## What This Does

Runs 3 specialized analyses to maintain documentation health:

- **Docstring Analyzer** - Find missing or outdated docstrings
- **README Checker** - Verify README accuracy
- **Doc Sync Validator** - Ensure docs match code

## Usage

```
/manage-docs
```

## Instructions for Claude

When the user invokes /manage-docs, execute these steps using the Task tool.
This runs entirely within Claude Code using the user's Max subscription ($0 cost).

### Step 1: Analyze Docstring Coverage

Use the Task tool with subagent_type="Explore":

```
Analyze docstring coverage in the codebase:

1. Find all public functions/classes in src/ without docstrings
2. Identify docstrings that are incomplete (missing Args, Returns, Raises)
3. Find docstrings that reference parameters that no longer exist
4. Check for type hints that don't match docstring types

Focus on public APIs that users interact with.
Output a list of files and functions needing documentation.
```

### Step 2: Check README Accuracy

Use the Task tool with subagent_type="Explore":

```
Verify README.md is accurate and current:

1. Check that installation instructions work
2. Verify code examples are valid and up-to-date
3. Check that features listed actually exist
4. Verify version numbers are current
5. Check for broken links or outdated references

Compare README claims against actual codebase capabilities.
```

### Step 3: Validate Documentation Sync

Use the Task tool with subagent_type="Explore":

```
Check that documentation matches the code:

1. Compare docs/ content against src/ implementation
2. Find features in code that aren't documented
3. Find documented features that no longer exist
4. Check CHANGELOG.md has recent changes

Identify any drift between documentation and implementation.
```

### Step 4: Generate Documentation Report

Create a documentation health report:

```markdown
## Documentation Report

### Overall Health: [GOOD / NEEDS WORK / OUTDATED]

### Docstring Coverage

| Module | Coverage | Missing |
|--------|----------|---------|
| module1 | 85% | 3 functions |
| module2 | 60% | 8 functions |

### README Status
- Installation: [OK/OUTDATED]
- Examples: [OK/BROKEN]
- Features: [ACCURATE/DRIFT]

### Documentation Gaps

**High Priority (public APIs):**
1. [list undocumented public functions]

**Medium Priority:**
1. [list incomplete docstrings]

**Low Priority:**
1. [list minor improvements]

### Recommended Actions
1. [prioritized list of documentation tasks]
```

## Cost

**$0** - Runs entirely within Claude Code using your Max subscription.

## Alternative: API Mode

To use the API-based execution instead (costs $0.08-$0.50):

```bash
empathy meta-workflow run manage-docs --real --use-defaults
```
