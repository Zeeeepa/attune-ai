Show current Empathy Framework project status.

Gather and display:

1. **Version Info**
   - Local version (pyproject.toml)
   - PyPI version: `pip index versions empathy-framework 2>/dev/null | head -1`
   - Latest git tag: `git tag -l 'v*' | tail -1`

2. **Repository**
   - Current branch: `git branch --show-current`
   - Uncommitted changes: `git status --short | wc -l` files
   - Last commit: `git log -1 --oneline`

3. **GitHub**
   - Stars: `gh api repos/Smart-AI-Memory/empathy-framework --jq .stargazers_count`
   - Open issues: `gh api repos/Smart-AI-Memory/empathy-framework --jq .open_issues_count`

4. **Installation**
   - Currently installed: `pip show empathy-framework | grep -E "^(Version|Location|Editable)"`

Format as a clean status dashboard.
