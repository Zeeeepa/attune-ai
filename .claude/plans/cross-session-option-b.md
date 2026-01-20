# Option B: Cross-Session Awareness for Base Workflow

**Scheduled:** Thursday, January 23, 2026

## Goal
Add optional cross-session awareness to `BaseWorkflow` so long-running workflows can:
- Announce when they start/complete
- Check for conflicts before starting
- Share results with other sessions

## Implementation Plan

### 1. Modify `BaseWorkflow` in `src/empathy_os/workflows/base.py`

```python
class BaseWorkflow:
    def __init__(
        self,
        enable_cross_session: bool = False,  # New parameter
        ...
    ):
        self._cross_session_enabled = enable_cross_session
        self._coordinator = None

    async def execute(self, ...):
        # Check for cross-session coordination
        if self._cross_session_enabled:
            memory = get_redis_memory()
            if memory.cross_session_available():
                self._coordinator = memory.enable_cross_session()

                # Try to acquire workflow lock
                lock_key = f"workflow:{self.__class__.__name__}"
                if not self._coordinator.acquire_lock(lock_key):
                    return {
                        "status": "skipped",
                        "reason": "Workflow already running in another session"
                    }

        try:
            result = await self._execute_impl(...)
        finally:
            if self._coordinator:
                self._coordinator.release_lock(lock_key)
                self._coordinator.close()

        return result
```

### 2. Update specific workflows to opt-in

Priority workflows to enable cross-session:
- [ ] `release_prep_crew.py` - Long-running, modifies many files
- [ ] `test_coverage_boost_crew.py` - Long-running, generates tests
- [ ] `manage_documentation.py` - Modifies docs across codebase
- [ ] `orchestrated_release_prep.py` - Multi-step release process

### 3. Add tests

- Test workflow lock acquisition
- Test conflict detection
- Test graceful handling when another session is running

## Success Criteria

- [ ] `BaseWorkflow` has optional `enable_cross_session` flag
- [ ] At least 2 workflows use cross-session coordination
- [ ] Tests pass
- [ ] Documentation updated

## Dependencies

- Cross-session feature (completed January 20, 2026)
- Redis available for testing
