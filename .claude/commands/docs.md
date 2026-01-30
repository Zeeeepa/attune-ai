---
name: docs
description: Documentation hub - explain code, generate docs, feature overviews
category: hub
aliases: [documentation]
tags: [documentation, explanation, hub]
version: "3.0"
question:
  header: "Documentation"
  question: "What documentation task do you need?"
  multiSelect: false
  options:
    - label: "💡 Explain code"
      description: "Understand how code works with teaching-focused explanations"
    - label: "📝 Generate docs"
      description: "Create documentation from code with examples"
    - label: "📋 Feature overview"
      description: "Get high-level overview of a feature or module"
    - label: "🔍 API reference"
      description: "Generate API documentation with usage examples"
    - label: "🔍 SEO optimization"
      description: "Audit and optimize SEO for documentation sites"
---

# Documentation

**Aliases:** `/documentation`

Documentation operations powered by Socratic agents that help you understand and explain code.

## Quick Examples

```bash
/docs                         # Interactive menu
/docs explain                 # Get code explanation with context
/docs generate                # Generate documentation
/docs overview                # Feature or module overview
/docs seo                     # SEO audit for documentation site
```

## Discovery

```yaml
Question:
  header: "Task"
  question: "What documentation task do you need?"
  options:
    - label: "Explain code"
      description: "Understand how code works with guided exploration"
    - label: "Generate docs"
      description: "Create documentation for code or features"
    - label: "Feature overview"
      description: "High-level overview for stakeholders"
    - label: "Optimize SEO"
      description: "Audit and optimize documentation site SEO"
```

---

## Explain Code

**Agent:** `architect` | **Workflow:** (code exploration)

Understand code through guided exploration, not just reading.

**Invoke:**

```bash
/docs explain                         # Interactive selection
/docs explain src/auth/oauth.py       # Explain specific file
/docs explain "how does caching work" # Explain by concept
```

**The architect agent will:**

1. Ask what you're trying to understand
2. Explore the code structure together
3. Guide you through the logic step by step
4. Ask: "What do you think this function does based on its name?"
5. Connect patterns to broader concepts
6. Answer follow-up questions

**Philosophy:** Instead of "This function authenticates users", you'll hear "Looking at the function name and parameters, what do you think it does? Let's trace through what happens when a user logs in."

**Good for:**

- Onboarding to unfamiliar code
- Understanding complex algorithms
- Learning patterns used in codebase
- Preparing to make changes

---

## Generate Documentation

**Agent:** `architect` | **Workflow:** `document_gen`

Generate documentation that matches the code.

**Invoke:**

```bash
/docs generate                        # Interactive selection
/docs generate src/api/               # Document specific module
/docs generate --type api             # Generate API reference
/docs generate --type readme          # Update README
```

**The architect agent will:**

1. Analyze the code structure
2. Ask about target audience (users, developers, stakeholders)
3. Generate appropriate documentation
4. Ensure accuracy with the actual implementation
5. Format for the intended use (Markdown, docstrings, etc.)

**Documentation types:**

| Type | Description |
|------|-------------|
| `readme` | Project overview and quickstart |
| `api` | Function/class reference docs |
| `guide` | How-to tutorials |
| `architecture` | System design overview |
| `changelog` | Version history |

**Philosophy:** Instead of generic templates, you'll hear "Who will read this documentation? Developers integrating your API, or users learning the product?"

---

## Feature Overview

**Agent:** `architect` | **Workflow:** (exploration + generation)

Generate high-level overviews for features or modules.

**Invoke:**

```bash
/docs overview                        # Interactive selection
/docs overview "authentication"       # Overview of auth system
/docs overview src/workflows/         # Overview of module
```

**The architect agent will:**

1. Explore the relevant code
2. Identify key components and their relationships
3. Ask about target audience and depth
4. Generate a structured overview
5. Include diagrams or flow descriptions where helpful

**Output includes:**

- Purpose and scope
- Key components
- How they interact
- Usage examples
- Limitations and caveats

**Philosophy:** Instead of just listing files, you'll hear "This module has 6 main components. Which aspect are you most interested in understanding?"

---

## SEO Optimization

**Multi-Agent System** | **Workflow:** `seo-optimization`

Audit and optimize SEO for documentation sites (MkDocs, static site generators).

**Invoke:**

```bash
/docs seo                             # Quick audit
/docs seo-audit                       # Full audit mode
/docs seo-optimize                    # Interactive fixes
```

Or via workflows:

```bash
/workflows run seo-optimization --mode audit      # Audit only
/workflows run seo-optimization --mode suggest    # Audit + suggestions
/workflows run seo-optimization --mode fix        # Interactive fixes
```

**The SEO optimization team includes:**

1. **SEO Auditor** - Scans meta tags, titles, descriptions
2. **Content Optimizer** - Analyzes heading structure, keywords
3. **Technical SEO Specialist** - Validates sitemap, robots.txt
4. **Link Analyzer** - Checks internal/external links

**What it checks:**

- Meta descriptions (120-160 characters)
- Page titles (30-60 characters)
- OpenGraph tags (og:title, og:description, og:image)
- Twitter Card tags
- H1 tags (exactly one per page)
- Heading hierarchy (no skipped levels)
- Sitemap.xml
- robots.txt
- Broken links
- Internal linking opportunities

**Interactive workflow:**

1. Scans all markdown files
2. Identifies SEO issues (critical, warning, info)
3. Generates specific fix suggestions
4. Shows before/after previews
5. Asks for approval before applying changes
6. Implements approved fixes
7. Generates implementation report

**Modes:**

| Mode | Description | Cost Tier |
| ------ | ------------- | ----------- |
| `audit` | Scan and report issues only | CHEAP → CAPABLE |
| `suggest` | Audit + generate fix recommendations | CHEAP → CAPABLE → PREMIUM |
| `fix` | Audit + suggest + implement with approval | CHEAP → CAPABLE → PREMIUM → CAPABLE |

**Output:**

- SEO score (0-100)
- Issues by severity (critical, warning, info)
- Detailed findings with file locations
- Implementation report (if fixes applied)

**Reference Example:** See [examples/seo_optimization/](../../examples/seo_optimization/) for complete multi-agent system implementation.

**Good for:**

- Pre-launch documentation site checks
- Regular SEO health monitoring
- Improving documentation discoverability
- Fixing broken links and missing metadata

---

## Agent-Skill-Workflow Mapping

| Skill | Agent | Workflow | When to Use |
|-------|-------|----------|-------------|
| `/docs explain` | architect | (exploration) | Understanding existing code |
| `/docs generate` | architect | document_gen | Creating new documentation |
| `/docs overview` | architect | (exploration) | High-level feature summaries |
| `/docs seo` | multi-agent | seo-optimization | Optimizing documentation site SEO |

---

## When to Use Each Skill

```text
Need to understand unfamiliar code  → /docs explain
Need to write new documentation     → /docs generate
Need summary for stakeholders       → /docs overview
Need to optimize documentation SEO  → /docs seo
```

---

## When NOT to Use This Hub

| If you need...     | Use instead |
|--------------------|-------------|
| Fix code issues    | `/dev debug` |
| Review code        | `/dev review` |
| Run tests          | `/testing` |
| Deploy changes     | `/release` |

## Related Hubs

- `/dev` - Code changes, commits, PRs
- `/workflows` - Run automated workflows (doc-gen, doc-orchestrator, seo-optimization)
- `/plan` - Feature planning
- `/learning` - Pattern documentation
- `/agent` - Direct agent invocation
