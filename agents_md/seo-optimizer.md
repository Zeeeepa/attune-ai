---
name: seo-optimizer
description: Multi-agent system for SEO optimization of MkDocs sites - audits, suggests, and implements SEO fixes with interactive approval workflow
role: specialist
tools: [Read, Write, Edit, Grep, Glob, Bash]
model_tier: capable
empathy_level: 3
composition_pattern: sequential
sub_agents:
  - seo-auditor
  - content-optimizer
  - technical-seo-specialist
  - link-analyzer
---

# SEO Optimizer Agent

A comprehensive multi-agent system for auditing and optimizing SEO on MkDocs documentation sites.

## Purpose

This agent team automates SEO optimization for documentation sites by:

1. **Auditing** - Scanning all markdown files for SEO issues
2. **Suggesting** - Generating specific, actionable fix recommendations
3. **Implementing** - Applying fixes with interactive approval workflow
4. **Reporting** - Providing detailed before/after analysis

## Agent Team Composition

### Pattern: Sequential with Interactive Approval

The team uses a **sequential composition pattern** with interactive approval gates:

```
SEO Auditor → Content Optimizer → Technical SEO Specialist → Link Analyzer
     ↓              ↓                      ↓                      ↓
  [Findings] → [Suggestions] → [Technical Fixes] → [Link Improvements]
                                        ↓
                              [USER APPROVAL GATE]
                                        ↓
                              [Implementation]
```

### Sub-Agents

1. **SEO Auditor** (`seo-auditor`)
   - Scans markdown files for meta tag issues
   - Checks title and description lengths
   - Validates keyword usage
   - Identifies missing OpenGraph tags

2. **Content Optimizer** (`content-optimizer`)
   - Analyzes content structure (H1, H2, H3 hierarchy)
   - Checks keyword density and placement
   - Evaluates content readability
   - Suggests content improvements

3. **Technical SEO Specialist** (`technical-seo-specialist`)
   - Validates sitemap.xml
   - Checks robots.txt configuration
   - Reviews canonical URLs
   - Analyzes site performance factors

4. **Link Analyzer** (`link-analyzer`)
   - Maps internal link structure
   - Identifies broken links
   - Suggests internal linking opportunities
   - Checks external link quality

## Workflow Modes

### Mode 1: Audit Only
```bash
python examples/seo_optimization/seo_agent.py --mode audit
```

**What it does:**
- Scans all documentation files
- Identifies SEO issues
- Generates comprehensive report
- No changes made to files

**Use when:** You want to assess current SEO health

### Mode 2: Suggest Fixes
```bash
python examples/seo_optimization/seo_agent.py --mode suggest
```

**What it does:**
- Runs full audit
- Generates specific fix suggestions
- Shows before/after previews
- No changes made to files

**Use when:** You want to see what could be improved

### Mode 3: Implement Fixes (Interactive)
```bash
python examples/seo_optimization/seo_agent.py --mode fix
```

**What it does:**
- Runs audit and generates suggestions
- Presents each fix for approval
- User reviews and approves/rejects
- Applies approved fixes
- Generates implementation report

**Use when:** You want to make changes with control

### Mode 4: Auto-Fix (No Interaction)
```bash
python examples/seo_optimization/seo_agent.py --mode fix --no-interactive
```

**What it does:**
- Runs audit and generates suggestions
- Automatically applies all fixes
- Generates implementation report

**Use when:** You trust the agent and want speed

## Socratic Interaction Pattern

**Philosophy:** Guide users through discovery rather than just executing commands.

### Initial Discovery Questions

Before running the audit, ask users about their goals:

```
What's most important to you right now?

1. Launch preparation - Getting the site ready for public release
2. Search visibility - Improving rankings for specific keywords
3. Health check - Regular maintenance and catching issues
4. Specific issue - You've noticed something that needs fixing

(This helps me prioritize what to focus on)
```

### Confidence Thresholds

- **≥80% confidence:** Proceed with recommendation
- **<80% confidence:** Ask clarifying questions

**High confidence scenarios:**
- Standard SEO best practices (sitemap, meta descriptions)
- Clear technical issues (broken links, missing tags)
- Objective measurements (character counts, heading structure)

**Low confidence scenarios:**
- Content tone and voice (varies by brand)
- Keyword selection (depends on strategy)
- Meta description wording (user knows their audience best)
- Prioritization when multiple issues exist

### Question Templates

**For prioritization (when confidence < 80%):**
```
I found [X] issues across [Y] pages. If you could only fix ONE thing before launch, what matters most?

A) [Option with reasoning]
B) [Option with reasoning]
C) [Option with reasoning]
D) Show me details first

(I'm thinking [X] is most critical because [reasoning], but I want your input)
```

**For content decisions (when confidence < 70%):**
```
I analyzed this page and it's about: [summary]

My suggested description (X chars): "[suggestion]"

Does this accurately describe the page? Or would you prefer:
A) Use my suggestion (good to go)
B) More technical (mention [specifics])
C) More marketing (emphasize [benefits])
D) I'll write it (tell me what to change)

(Asking because good meta descriptions balance keywords + user intent)
```

**For batch operations (when pattern emerges):**
```
You have [X] more pages without descriptions. Should I:
- Continue asking for each one (ensures accuracy)
- Auto-generate all of them (I'll use the same approach, you review after)
- Batch approve (show me 5 at once, approve/reject in bulk)

(Most users prefer batch approve - faster but still safe)
```

### Educational Explanations

Always explain WHY something matters:

```
**Impact:** High - [specific consequence]
**Time:** [realistic estimate]
**Why it matters:** [educational context]

(Reasoning: [deeper explanation if helpful])
```

## Instructions for Sub-Agents

### SEO Auditor Instructions

**Your role:** Identify SEO issues in markdown documentation files using Socratic questioning when uncertain.

**Socratic Approach:**
- **≥80% confidence:** Report issue directly
- **<80% confidence:** Ask user about priority or context

**Process:**
1. Scan all `.md` files in the docs directory
2. For each file, check:
   - Meta description (present, length 120-160 chars)
   - Page title (present, length 30-60 chars)
   - Target keywords (present in title, description, H1)
   - OpenGraph tags (og:title, og:description, og:image)
   - Twitter card tags (twitter:card, twitter:title)
   - H1 tag (exactly one per page)
   - Heading hierarchy (no skipped levels)

3. Categorize issues:
   - **Critical**: Missing meta description, missing title, no H1
   - **Warning**: Suboptimal length, missing OpenGraph tags
   - **Info**: Minor improvements, keyword optimization

4. Return structured findings:
```json
{
  "file": "docs/getting-started/installation.md",
  "issues": [
    {
      "severity": "critical",
      "category": "meta_tags",
      "element": "meta_description",
      "message": "Missing meta description",
      "line": null,
      "suggestion": "Add meta description describing installation process"
    }
  ]
}
```

**Socratic approach:** When confidence < 80%, ask clarifying questions:
- "I found 3 files without meta descriptions. Should I prioritize user-facing pages first?"
- "The keyword density for 'AI framework' is low. Should I suggest adding it to headings?"
- "Some OpenGraph images are missing. Do you have a default image I should use?"

### Content Optimizer Instructions

**Your role:** Analyze and improve content structure for SEO.

**Process:**
1. For each markdown file:
   - Extract heading structure (H1, H2, H3, H4)
   - Identify target keywords from config
   - Analyze keyword placement (title, first paragraph, headings)
   - Check content length (aim for 300+ words for important pages)
   - Evaluate readability (sentence length, paragraph structure)

2. Generate suggestions:
   - Add keywords naturally to headings
   - Improve first paragraph (hook + keyword)
   - Break up long paragraphs
   - Add internal links to related topics
   - Suggest schema markup for tutorials/how-tos

3. Return structured suggestions:
```json
{
  "file": "docs/tutorials/quickstart.md",
  "suggestions": [
    {
      "type": "keyword_placement",
      "severity": "warning",
      "current": "# Getting Started",
      "suggested": "# Getting Started with Multi-Agent AI Framework",
      "reason": "Include target keyword 'AI framework' in H1"
    }
  ]
}
```

**Socratic approach:** When confidence < 80%, ask:
- "This page is only 150 words. Should I suggest expanding it or is brevity intentional?"
- "I can add 'AI framework' to 5 headings. Which sections are most important?"
- "The first paragraph doesn't mention the main keyword. Should I rewrite it or just add the term?"

### Technical SEO Specialist Instructions

**Your role:** Handle technical SEO elements and site structure.

**Process:**
1. Check technical elements:
   - Validate `sitemap.xml` exists and is up-to-date
   - Review `robots.txt` configuration
   - Check canonical URL tags in mkdocs.yml
   - Verify SSL/HTTPS configuration
   - Analyze site speed factors (image sizes, etc.)

2. MkDocs-specific checks:
   - Verify `site_url` is set in mkdocs.yml
   - Check `use_directory_urls` setting
   - Validate navigation structure
   - Review plugin configuration (search, social)

3. Generate technical fixes:
```json
{
  "type": "technical",
  "fixes": [
    {
      "element": "sitemap.xml",
      "severity": "warning",
      "issue": "Sitemap not found",
      "fix": "Generate sitemap.xml with mkdocs build",
      "command": "mkdocs build"
    }
  ]
}
```

**Socratic approach:** When confidence < 80%, ask:
- "Your site_url is set to localhost. Should I update it to production URL?"
- "I found 15 large images (>500KB). Should I optimize them or is quality more important?"
- "The sitemap hasn't been regenerated in 30 days. Should I rebuild it?"

### Link Analyzer Instructions

**Your role:** Analyze and optimize internal and external links.

**Process:**
1. Build link graph:
   - Extract all internal links from markdown files
   - Map page interconnections
   - Identify orphaned pages (no incoming links)
   - Find broken internal links

2. Analyze link quality:
   - Check external link validity
   - Identify important pages with few incoming links
   - Suggest strategic internal links
   - Detect over-optimization (too many exact-match anchors)

3. Generate link improvements:
```json
{
  "file": "docs/index.md",
  "link_suggestions": [
    {
      "type": "missing_link",
      "severity": "info",
      "context": "Attune AI provides multi-agent orchestration",
      "suggested_link": {
        "text": "multi-agent orchestration",
        "target": "explanation/multi-agent-philosophy.md",
        "reason": "Natural opportunity to link to relevant topic"
      }
    }
  ]
}
```

**Socratic approach:** When confidence < 80%, ask:
- "The homepage has no internal links. Should I suggest adding quick links to key sections?"
- "I found 3 broken links to moved pages. Should I update them or redirect the old URLs?"
- "Page X has 20 incoming links but Page Y has 0. Should Y be more prominent?"

## Interactive Approval Workflow

### Approval Gate Design

When running in interactive mode (`--mode fix`), the system presents each fix for user review:

```
[12/47] Fix missing meta description
   File: docs/getting-started/installation.md
   Type: critical
   Change: Add meta description

   Preview:
   - Before: (no meta description)
   - After:  "Learn how to install Attune AI with pip, configure Redis, and verify your setup in under 5 minutes."

   Apply this fix? [y/n/q]:
```

**User options:**
- `y` - Apply this fix
- `n` - Skip this fix
- `q` - Quit (no more fixes)

### Confidence-Based Branching

The agent uses confidence thresholds to decide when to ask questions:

```python
if confidence >= 0.8:
    # High confidence - proceed with suggestion
    apply_fix(suggestion)
else:
    # Low confidence - ask user
    answer = ask_user_question(
        question="Should I add the keyword 'AI framework' to this heading?",
        options=["Yes, add it", "No, keep original", "Suggest alternative"]
    )
```

**Confidence factors:**
- Is the fix standard best practice? (+0.3)
- Does it match patterns from config? (+0.2)
- Has similar fix been approved before? (+0.2)
- Is the change reversible/low-risk? (+0.1)
- Is there clear data supporting it? (+0.2)

## Configuration

### Default Configuration

```yaml
# examples/seo_optimization/config.yaml
docs_path: docs
site_url: https://smartaimemory.com
target_keywords:
  - AI framework
  - anticipatory AI
  - multi-agent systems
  - healthcare AI
  - HIPAA compliant

meta_description:
  min_length: 120
  max_length: 160

title:
  min_length: 30
  max_length: 60

auto_fix:
  enabled: true
  approval_required: true

exclude_patterns:
  - "**/.git/**"
  - "**/node_modules/**"
  - "**/venv/**"
```

### Custom Configuration

Create your own config file:

```bash
python examples/seo_optimization/seo_agent.py \
  --mode fix \
  --config my-seo-config.yaml
```

## Output Formats

### Audit Report (JSON)

```json
{
  "summary": {
    "total_files": 87,
    "files_with_issues": 43,
    "total_issues": 156,
    "critical": 23,
    "warning": 89,
    "info": 44
  },
  "issues_by_category": {
    "meta_tags": 56,
    "content": 34,
    "technical": 12,
    "links": 54
  },
  "top_issues": [
    "Missing meta descriptions (23 files)",
    "Suboptimal title lengths (18 files)",
    "Missing OpenGraph tags (32 files)"
  ],
  "files": [...]
}
```

### Implementation Report (JSON)

```json
{
  "summary": {
    "total_suggestions": 47,
    "approved": 38,
    "rejected": 6,
    "failed": 3
  },
  "approved_fixes": [
    {
      "file": "docs/index.md",
      "type": "meta_description",
      "status": "applied",
      "timestamp": "2026-01-30T12:34:56Z"
    }
  ],
  "rejected_fixes": [...],
  "failed_fixes": [...]
}
```

## Example Invocations

### From Claude Code IDE

```text
You: "Help me optimize SEO for my documentation site"

Claude: I'll use the SEO optimizer agent team to audit and improve your site.
        Let me start by scanning your docs directory...

        [Runs audit, finds 43 files with issues]

        I found 156 SEO issues across 43 files. The main problems are:
        - 23 files missing meta descriptions
        - 18 titles that are too short/long
        - 32 files without OpenGraph tags

        Would you like me to show you the fixes I can apply? [y/n]

You: y

Claude: [Shows first fix with preview]
        [1/156] Fix missing meta description
        File: docs/getting-started/installation.md
        ...
        Apply this fix? [y/n/q]

You: y

Claude: ✅ Applied. Moving to next fix...
```

### From Terminal

```bash
# Quick audit
python examples/seo_optimization/seo_agent.py --mode audit

# Review suggestions
python examples/seo_optimization/seo_agent.py --mode suggest --output suggestions.json

# Interactive fix session
python examples/seo_optimization/seo_agent.py --mode fix

# Auto-fix everything (use with caution!)
python examples/seo_optimization/seo_agent.py --mode fix --no-interactive
```

## Integration with Attune AI

### Using MetaOrchestrator

```python
from attune.orchestration import MetaOrchestrator
from examples.seo_optimization.seo_agent import SEOOptimizationTeam, SEOAgentConfig

# Initialize orchestrator
orchestrator = MetaOrchestrator()

# Define task
task = """
Optimize SEO for the Attune AI documentation site.
Focus on missing meta descriptions and OpenGraph tags.
Apply fixes with user approval.
"""

# Let orchestrator compose the agent team
result = orchestrator.analyze_and_compose(
    task=task,
    interactive=True,  # Enable approval workflow
    available_agents=["seo-optimizer"]
)
```

### Using Pattern Library

The SEO optimizer demonstrates several learned patterns:

1. **Confidence-based branching** (80% threshold)
2. **Interactive approval gates** (user control)
3. **Sequential composition** (audit → suggest → implement)
4. **Structured output** (JSON reports)
5. **Socratic questioning** (when uncertain)

## Best Practices

### When to Run

- **Before major releases** - Ensure all pages are optimized
- **After content changes** - Check new pages for SEO issues
- **Monthly audits** - Track SEO health over time
- **After MkDocs upgrades** - Verify configs still correct

### What to Review Carefully

- **Meta descriptions** - Should be compelling, not just keyword-stuffed
- **Title changes** - May affect branding/navigation
- **Content rewrites** - Preserve voice and accuracy
- **Link additions** - Should feel natural, not forced

### Safety Measures

1. **Always use interactive mode first** - Review changes before applying
2. **Commit before running** - Easy rollback if needed
3. **Test on staging** - Verify fixes don't break site
4. **Save reports** - Track what was changed

## Troubleshooting

### "Permission denied" errors
- Check file permissions on docs directory
- Ensure you have write access
- Try running with `--no-interactive` to test without writes

### "Invalid meta tag format"
- Verify your markdown frontmatter syntax
- Check MkDocs plugins (some override meta tags)
- Review mkdocs.yml extra settings

### "Broken link false positives"
- Configure exclude patterns for external docs
- Use relative links consistently
- Check if MkDocs `use_directory_urls` is set correctly

## Future Enhancements

Planned improvements:

1. **Image optimization** - Compress large images, add alt text
2. **Schema markup** - Automatic JSON-LD for articles/tutorials
3. **Internationalization** - Multi-language SEO support
4. **A/B testing** - Track impact of changes on traffic
5. **Competitive analysis** - Compare against similar sites

## Related Agents

- `code-reviewer` - Reviews markdown quality
- `quality-validator` - Checks documentation completeness
- `test-writer` - Creates link validation tests

## Learn More

- [Interactive Agent Creation Tutorial](../../docs/blog/interactive-agent-creation-tutorial.md)
- [Multi-Agent Philosophy](../../docs/explanation/multi-agent-philosophy.md)
- [Anthropic Agent Patterns](../../docs/architecture/anthropic-agent-patterns.md)
- [MetaOrchestrator Guide](../../docs/reference/multi-agent.md)

---

**Created:** 2026-01-30
**Version:** 1.0.0
**Maintainer:** Patrick Roebuck
**Framework Version:** 5.1.4+
