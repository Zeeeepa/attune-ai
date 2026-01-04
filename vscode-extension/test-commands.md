# Testing New Workflow Bridge Commands

## Status Check

Based on console output:
- ✅ Extension activated
- ✅ Keyboard layout detected: dvorak
- ❓ **WorkflowBridge initialization status unknown** - no initialization logs visible

Expected console messages (missing):
```
[WorkflowBridge] Initializing...
[WorkflowBridge] Discovered X workflows
[WorkflowBridge] Registered workflow commands
[WorkflowBridge] Registered keyboard shortcuts
[WorkflowBridge] Registered category commands
[WorkflowBridge] Registered utility commands
[WorkflowBridge] ✓ Initialization complete
```

## How to Test Commands

### Method 1: VSCode Command Palette (for registered commands)

1. Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
2. Type `>Empathy: Test Workflow Bridge`
3. Press Enter

This should show:
- Console logs with test results
- Info message: "✓ Workflow Bridge test passed!"

### Method 2: Developer Execute Command (for hidden commands)

1. Press `Cmd+Shift+P`
2. Type `>Developer: Execute Command`
3. Enter one of these command IDs:

**Test Commands:**
- `empathy.simpleTest` - Should show "✓ Simple test works!"
- `empathy.testWorkflowBridge` - Runs full integration test

**Category Quick Pick Commands (NEW):**
- `empathy.quickPick.all` - Show all workflows
- `empathy.quickPick.quick` - Show Quick category (morning, ship, etc.)
- `empathy.quickPick.workflow` - Show Workflow category (bug-predict, code-review, etc.)
- `empathy.quickPick.view` - Show View category (dashboard, costs, status)
- `empathy.quickPick.tool` - Show Tool category (fix-lint, fix-format, sync-claude)

**Utility Commands (NEW):**
- `empathy.refreshWorkflows` - Force refresh workflow cache from Python CLI
- `empathy.keyboardShortcutsCheatsheet` - Open keyboard shortcuts cheatsheet

### Method 3: Create Keybindings (Recommended)

Add to your `keybindings.json`:

```json
[
  {
    "key": "cmd+shift+e q",
    "command": "empathy.quickPick.quick",
    "when": "!inDebugMode"
  },
  {
    "key": "cmd+shift+e w",
    "command": "empathy.quickPick.workflow",
    "when": "!inDebugMode"
  },
  {
    "key": "cmd+shift+e v",
    "command": "empathy.quickPick.view",
    "when": "!inDebugMode"
  },
  {
    "key": "cmd+shift+e t",
    "command": "empathy.quickPick.tool",
    "when": "!inDebugMode"
  },
  {
    "key": "cmd+shift+e a",
    "command": "empathy.quickPick.all",
    "when": "!inDebugMode"
  },
  {
    "key": "cmd+shift+e k",
    "command": "empathy.keyboardShortcutsCheatsheet",
    "when": "!inDebugMode"
  },
  {
    "key": "cmd+shift+e r",
    "command": "empathy.refreshWorkflows",
    "when": "!inDebugMode"
  }
]
```

## Expected Results

### empathy.testWorkflowBridge

**Console Output:**
```
=== Workflow Bridge Integration Test ===
✓ Initialization passed
✓ Stats: {
  "totalWorkflows": 15,
  "byCategory": {
    "quick": 4,
    "workflow": 8,
    "view": 3,
    "tool": 0
  },
  "cacheAge": null
}
✓ Discovered 15 workflows
✓ Generated shortcuts for 4 categories

=== Test Summary ===
Total Workflows: 15
Quick: 4
Workflow: 8
View: 3
Tool: 0
```

**Info Message:**
"✓ Workflow Bridge test passed!"

### empathy.quickPick.all

**Should show Quick Pick menu with:**
- All discovered workflows
- Icons next to each workflow name
- Description of each workflow
- Workflow stages in detail

### empathy.keyboardShortcutsCheatsheet

**Should open:**
- New markdown document in split view
- Keyboard shortcuts organized by category
- Mnemonics for each shortcut
- Home row indicators (��)
- Markdown preview automatically shown

## Troubleshooting

### WorkflowBridge didn't initialize

If you don't see `[WorkflowBridge]` messages in the console:

1. **Check Extension Host console** (not browser console):
   - View > Output
   - Select "Extension Host" from dropdown

2. **Check for Python CLI**:
   ```bash
   cd /Users/patrickroebuck/empathy_11_6_2025/Empathy-framework
   python -m empathy_os.cli workflow list --json
   ```

3. **Reload window**:
   - Cmd+Shift+P > "Developer: Reload Window"

### Commands not found

If "command not found" error:
- Commands ARE registered (in extension.ts)
- Commands are NOT in package.json (intentionally hidden)
- Use "Developer: Execute Command" method

### No workflows shown

If Quick Pick shows "No workflows available":
- Python CLI might not be accessible
- WorkflowDiscoveryService falls back to built-in list
- Check `empathy.pythonPath` setting

## Next Steps

To make these commands visible in Command Palette, add to `package.json`:

```json
{
  "command": "empathy.quickPick.all",
  "title": "Empathy: Show All Workflows",
  "category": "Empathy"
},
{
  "command": "empathy.refreshWorkflows",
  "title": "Empathy: Refresh Workflows",
  "category": "Empathy"
},
{
  "command": "empathy.keyboardShortcutsCheatsheet",
  "title": "Empathy: Keyboard Shortcuts Cheatsheet",
  "category": "Empathy"
}
```
