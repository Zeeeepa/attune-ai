# Workflow Bridge Integration Test

## Quick Test (Add to extension.ts)

To test the workflow bridge without fully integrating it, add this code to your `extension.ts`:

```typescript
// Add to imports at top of extension.ts
import { testWorkflowBridge, WorkflowBridgeIntegration } from './services/WorkflowBridgeIntegration';

// Add to activate() function
export function activate(context: vscode.ExtensionContext) {
    // ... existing code ...

    // TEST: Workflow Bridge Integration
    const testCmd = vscode.commands.registerCommand('empathy.testWorkflowBridge', async () => {
        await testWorkflowBridge(context);
    });
    context.subscriptions.push(testCmd);

    console.log('Empathy Framework extension activated with workflow bridge test');
}
```

## How to Test

1. **Reload VSCode**
   - Press `Cmd+Shift+P`
   - Type "Developer: Reload Window"

2. **Run the test**
   - Press `Cmd+Shift+P`
   - Type "Empathy: Test Workflow Bridge"
   - Press Enter

3. **Check the output**
   - Open Developer Console: `Cmd+Option+I` → Console tab
   - Look for test output starting with "=== Workflow Bridge Integration Test ==="

## Expected Output

```
=== Workflow Bridge Integration Test ===
[WorkflowBridge] Initializing...
[WorkflowBridge] Discovered 16 workflows
[WorkflowBridge] Registered workflow commands
[WorkflowBridge] Registered keyboard shortcuts
[WorkflowBridge] Registered category commands
[WorkflowBridge] Registered utility commands
[WorkflowBridge] ✓ Initialization complete
✓ Initialization passed
✓ Stats: {
  "totalWorkflows": 16,
  "byCategory": {
    "quick": 4,
    "workflow": 10,
    "view": 3,
    "tool": 0
  },
  "cacheAge": null
}
✓ Discovered 16 workflows
✓ Generated shortcuts for 4 categories

=== Test Summary ===
Total Workflows: 16
Quick: 4
Workflow: 10
View: 3
Tool: 0
```

## What Gets Tested

1. ✅ **Workflow Discovery** - Discovers workflows from Python CLI
2. ✅ **Command Registration** - Registers all workflows as VSCode commands
3. ✅ **Shortcut Generation** - Generates three-level shortcuts (Q/W/V/T)
4. ✅ **Category Commands** - Registers Quick Pick menus for each category
5. ✅ **Stats Calculation** - Counts workflows by category

## Troubleshooting

### If test fails with "No workspace folder found"
- Open a folder in VSCode first
- Make sure the folder contains the Empathy Framework

### If test fails with "Failed to discover from Python CLI"
- Check that Python is installed: `python --version`
- Check that Empathy Framework CLI is accessible: `python -m empathy_os.cli --version`
- Verify workflow list works: `python -m empathy_os.cli workflow list --json`
- Check the Developer Console for detailed error messages

### If test succeeds but shows 0 workflows
- The Python CLI might not be returning JSON correctly
- Run manually: `cd <workspace> && python -m empathy_os.cli workflow list --json`
- Check if it outputs valid JSON

## Next Steps After Successful Test

Once the test passes, we can:

1. **Full Integration** - Integrate into extension.ts activate()
2. **Add Keybindings** - Update package.json with keyboard shortcuts
3. **UI Integration** - Add workflow buttons to Dashboard
4. **Documentation** - Generate keyboard shortcuts cheatsheet

---

**Ready to test?** Add the code snippet above to your extension.ts and run the test command!
