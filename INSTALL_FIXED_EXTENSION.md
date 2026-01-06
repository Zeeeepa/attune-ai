# Install Fixed VSCode Extension

## The Fix
"Generate Docs" and "Sync Docs" buttons now run workflows directly instead of showing input form.

## Installation Steps

### Option 1: Install via Command Line (Recommended)

```bash
# 1. Uninstall old version (if installed)
code --uninstall-extension smartaimemory.empathy-framework

# 2. Install new version with fix
code --install-extension /Users/patrickroebuck/empathy_11_6_2025/Empathy-framework/vscode-extension/empathy-framework-1.3.1.vsix

# 3. Reload VSCode window
# Press Cmd+Shift+P → type "Developer: Reload Window" → Enter
```

### Option 2: Install via VSCode UI

1. Open VSCode
2. Press `Cmd+Shift+P` (or `Ctrl+Shift+P` on Windows/Linux)
3. Type "Extensions: Install from VSIX"
4. Select: `/Users/patrickroebuck/empathy_11_6_2025/Empathy-framework/vscode-extension/empathy-framework-1.3.1.vsix`
5. Click "Reload Window" when prompted

## Verify the Fix

1. Open the Empathy Dashboard (click Empathy icon in sidebar)
2. Scroll to "Documentation & Code Quality" section
3. Click "Generate Docs" button
4. ✅ Should run `doc-gen` workflow directly
5. ✅ Should open results in editor (not show input form)

Same for "Sync Docs" button.

## What Changed

**File**: `vscode-extension/src/panels/EmpathyDashboardPanel.ts` (Line 2433)

**Before**:
```typescript
const reportWorkflows = [
    'code-review', 'bug-predict', 'security-audit', 'perf-audit',
    'refactor-plan', 'health-check', 'pr-review', 'pro-review'
];
```

**After**:
```typescript
const reportWorkflows = [
    'code-review', 'bug-predict', 'security-audit', 'perf-audit',
    'refactor-plan', 'health-check', 'pr-review', 'pro-review',
    'doc-gen', 'manage-docs'  // Now run immediately
];
```

## Troubleshooting

If buttons still show form after installing:
1. Check extension version in Extensions panel (should be 1.3.1)
2. Try "Developer: Reload Window" again
3. Close and reopen VSCode completely
4. Check VSCode Developer Tools console for errors (Help → Toggle Developer Tools)
