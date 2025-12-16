Guide me through publishing a new version of Empathy Framework to PyPI.

Steps to perform:

1. **Pre-flight checks**
   - Run `pytest tests/ -x -q` to verify tests pass
   - Check current version in pyproject.toml
   - Check latest tag: `git tag -l 'v*' | tail -1`
   - Check for uncommitted changes: `git status --short`

2. **Version bump** (if needed)
   - Ask what type of release: patch, minor, or major
   - Update version in pyproject.toml
   - Update version in .claude/CLAUDE.md

3. **Commit and tag**
   - Commit version bump
   - Create new git tag
   - Push to origin with tag

4. **Verify**
   - Check GitHub Actions status
   - Confirm PyPI publish succeeded

Do NOT proceed without my confirmation at each step.
