# Markdown Formatting Rules

**Created:** 2026-01-29
**Source:** Session evaluation - recurring linting warnings
**Purpose:** Prevent predictable markdown linting errors

---

## Critical Rules (Always Apply)

### 1. Blank Lines Around Fenced Code Blocks (MD031)

**ALWAYS add blank lines before and after code blocks:**

```markdown
❌ WRONG:
Some text here
```bash
command here
```
More text

✅ CORRECT:
Some text here

```bash
command here
```

More text
```

### 2. Language Specifiers on Code Blocks (MD040)

**ALWAYS specify language after opening fence:**

```markdown
❌ WRONG:
```
{
  "key": "value"
}
```

✅ CORRECT:
```json
{
  "key": "value"
}
```

**Common languages:**
- `bash` - Shell commands
- `python` - Python code
- `json` - JSON data
- `yaml` - YAML config
- `typescript` - TypeScript
- `javascript` - JavaScript
- `markdown` - Markdown examples
- `text` - Plain text output
- `sql` - SQL queries

### 3. Blank Lines Around Lists (MD032)

**ALWAYS add blank lines before and after lists:**

```markdown
❌ WRONG:
Some text here
- Item 1
- Item 2
More text

✅ CORRECT:
Some text here

- Item 1
- Item 2

More text
```

### 4. Ordered List Numbering (MD029)

**ALWAYS use sequential numbering (1, 2, 3) not (1, 1, 1):**

```markdown
❌ WRONG:
1. First item
1. Second item
1. Third item

✅ CORRECT:
1. First item
2. Second item
3. Third item
```

**Exception:** When intentionally using "1." for all items for easier reordering, add comment:
```markdown
<!-- markdownlint-disable MD029 -->
1. First item
1. Second item
1. Third item
<!-- markdownlint-enable MD029 -->
```

### 5. Table Column Spacing (MD060)

**ALWAYS add spaces around pipe separators:**

```markdown
❌ WRONG:
| Tool| Description|
|-----|------------|
| foo |description |

✅ CORRECT:
| Tool | Description |
|------|-------------|
| foo  | description |
```

### 6. Duplicate Headings (MD024)

**Avoid duplicate headings WITHIN the same section:**

```markdown
❌ WRONG (duplicate in same section):
## Configuration

### Database Setup
...

### Database Setup
...

✅ CORRECT (use different names):
## Configuration

### Database Setup
...

### Database Connection
...
```

**ACCEPTABLE: Duplicate headings in different sections (like CHANGELOG.md):**

```markdown
✅ ACCEPTABLE (different sections):
## [1.0.0]

### Added
- New feature

### Fixed
- Bug fix

## [0.9.0]

### Added
- Another feature

### Fixed
- Another fix
```

**Configuration:** The `.markdownlint.json` file is configured with `"siblings_only": true` which allows duplicate headings in different sections (standard for changelogs) while still catching problematic duplicates within the same section.

---

## Common Patterns to Remember

### Pattern 1: Code Examples in Documentation

```markdown
**Usage:**

```bash
command --flag value
```

**Output:**

```text
Expected output here
```
```

**Key points:**
- Blank line before opening fence
- Language specified
- Blank line after closing fence

### Pattern 2: Numbered Steps with Code

```markdown
1. **Install the package**

```bash
pip install package-name
```

2. **Configure the settings**

```json
{
  "setting": "value"
}
```

3. **Run the command**

```bash
package-name --start
```
```

**Key points:**
- Blank line after step description
- Blank line after code block
- Sequential numbering (1, 2, 3)

### Pattern 3: Lists with Descriptions

```markdown
The framework provides:

- **Feature 1** - Description here
- **Feature 2** - Description here
- **Feature 3** - Description here

These features enable...
```

**Key points:**
- Blank line before list
- Blank line after list

### Pattern 4: Tables with Multiple Columns

```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Value A  | Value B  | Value C  |
| Value D  | Value E  | Value F  |
```

**Key points:**
- Space after opening pipe
- Space before closing pipe
- Space around middle pipes
- Alignment optional but nice

---

## Quick Checklist

Before saving any markdown file, verify:

- [ ] All code blocks have language specifiers (MD040)
- [ ] Blank lines before/after all code blocks (MD031)
- [ ] Blank lines before/after all lists (MD032)
- [ ] Ordered lists use sequential numbers (1, 2, 3...) (MD029)
- [ ] Tables have proper spacing around pipes (MD060)
- [ ] No duplicate headings within same section (MD024)
- [ ] No trailing whitespace on lines
- [ ] File ends with single newline

---

## Auto-Fix Commands

If linting warnings appear:

```bash
# Check for issues
markdownlint filename.md

# Auto-fix common issues (if markdownlint-cli2 available)
markdownlint --fix filename.md
```

---

## Common Violations and Fixes

### Violation: "Fenced code blocks should be surrounded by blank lines"

**Before:**
```markdown
Install the package:
```bash
pip install package
```
Then run:
```

**After:**
```markdown
Install the package:

```bash
pip install package
```

Then run:
```

### Violation: "Fenced code blocks should have a language specified"

**Before:**
```markdown
```
{
  "key": "value"
}
```
```

**After:**
```markdown
```json
{
  "key": "value"
}
```
```

### Violation: "Lists should be surrounded by blank lines"

**Before:**
```markdown
Features include:
- Feature 1
- Feature 2
You can use these...
```

**After:**
```markdown
Features include:

- Feature 1
- Feature 2

You can use these...
```

### Violation: "Ordered list item prefix [Expected: 2; Actual: 1]"

**Before:**
```markdown
1. Step one
1. Step two
1. Step three
```

**After:**
```markdown
1. Step one
2. Step two
3. Step three
```

---

## Project Configuration

### .markdownlint.json (Project Root)

The project uses `.markdownlint.json` for consistent linting across all tools:

```json
{
  "default": true,
  "MD013": false,
  "MD024": {
    "siblings_only": true
  },
  "MD033": false,
  "MD041": false
}
```

**Configuration explained:**

- **`MD013: false`** - Disables line length check (we use Black with 100 chars for code)
- **`MD024: siblings_only`** - Allows duplicate headings in different sections (enables standard CHANGELOG.md format)
- **`MD033: false`** - Allows inline HTML (needed for some documentation features)
- **`MD041: false`** - Allows files to not start with top-level heading (flexible document structure)

### VSCode Extension Integration

If using VSCode with markdownlint extension, settings are automatically loaded from `.markdownlint.json`. You can also override in `.vscode/settings.json`:

```json
{
  "markdownlint.config": {
    "MD013": false,
    "MD033": false,
    "MD041": false
  }
}
```

---

## Summary

**Most Common Issues (Fix These First):**

1. ✅ Add blank lines around code blocks (MD031)
2. ✅ Add language to all code blocks (MD040)
3. ✅ Add blank lines around lists (MD032)
4. ✅ Use sequential list numbering (MD029)
5. ✅ Add spaces around table pipes (MD060)
6. ✅ Avoid duplicate headings within same section (MD024)

**Remember:** Getting it right the first time saves tokens and time!

**Note:** Duplicate headings in CHANGELOG.md are acceptable - they follow the standard Keep a Changelog format.
