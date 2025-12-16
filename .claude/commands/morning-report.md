Generate a morning status report for Empathy Framework. Include:

1. **Project Status**
   - Current version from pyproject.toml
   - Latest PyPI version: `pip index versions empathy-framework 2>/dev/null | head -1`
   - GitHub stars: `gh api repos/Smart-AI-Memory/empathy-framework --jq .stargazers_count`

2. **Marketing Tasks**
   - Read docs/marketing/GUERRILLA_MARKETING_PLAN.md
   - List today's priority tasks

3. **Ready-to-Post Content**
   - List files in docs/marketing/drafts/
   - Show a brief summary of each draft

4. **Quick Actions**
   Remind me I can:
   - Copy drafts to post on Dev.to, Reddit, Twitter
   - Run /publish to release a new version
   - Run /test to check test status

Keep the report concise and actionable.
