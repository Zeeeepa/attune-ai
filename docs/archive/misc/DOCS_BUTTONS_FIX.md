# VSCode Extension - Docs Buttons Fix

## Issue
The "Generate Docs" and "Sync Docs" buttons in the VSCode dashboard open an input form card instead of running the workflow directly and showing results.

## Root Cause
Lines 2430-2434 in `vscode-extension/src/panels/EmpathyDashboardPanel.ts`:

The `reportWorkflows` array didn't include 'doc-gen' and 'manage-docs', so these workflows fell through to the "Show input panel for other workflows" code path (line 2442+), which displays the form card.

## Fix Applied

**File**: `vscode-extension/src/panels/EmpathyDashboardPanel.ts`
**Lines**: 2430-2434

```typescript
// BEFORE:
const reportWorkflows = [
    'code-review', 'bug-predict', 'security-audit', 'perf-audit',
    'refactor-plan', 'health-check', 'pr-review', 'pro-review'
];

// AFTER:
const reportWorkflows = [
    'code-review', 'bug-predict', 'security-audit', 'perf-audit',
    'refactor-plan', 'health-check', 'pr-review', 'pro-review',
    'doc-gen', 'manage-docs'  // Added: doc workflows should run immediately
];
```

## How It Works Now

When clicking "Generate Docs" or "Sync Docs":
1. ✅ Workflow runs immediately with project root as input (`input: '.'`)
2. ✅ Results open directly in editor (like other report workflows)
3. ❌ No input form card appears

## Testing the Fix

**In VSCode**:
1. Reload the VSCode window (`Cmd+Shift+P` → "Developer: Reload Window")
2. Open the Empathy Dashboard
3. Click "Generate Docs" or "Sync Docs" button
4. ✅ Should run workflow directly without showing input form
5. ✅ Results should appear in editor

**Note**: The extension has been compiled. The fix is in `vscode-extension/out/panels/EmpathyDashboardPanel.js`

## Alternative: Remove the "Manage Docs" Button

If "Manage Docs" (doc-orchestrator) should always open the Documentation Analysis panel, that's working correctly (lines 2416-2418).

The three buttons are:
1. **Manage Docs** (`doc-orchestrator`) - Opens Documentation Analysis panel ✅ Working as designed
2. **Generate Docs** (`doc-gen`) - NOW runs workflow directly ✅ Fixed
3. **Sync Docs** (`manage-docs`) - NOW runs workflow directly ✅ Fixed

## Installation

To use the fixed extension:

```bash
cd vscode-extension
npm run compile  # ✅ Already done
npm run package  # Create .vsix file
code --install-extension empathy-framework-*.vsix
```

Or reload VSCode if developing locally.
