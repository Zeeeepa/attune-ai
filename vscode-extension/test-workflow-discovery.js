/**
 * Test workflow discovery from the VSCode extension
 */

const { execSync } = require('child_process');
const path = require('path');

console.log('=== Testing Workflow Discovery ===\n');

try {
    // Test 1: Can we discover workflows from Python CLI?
    console.log('Test 1: Discovering workflows from Python CLI...');
    const result = execSync('python -m empathy_os.cli workflow list --json', {
        cwd: path.join(__dirname, '..'),
        encoding: 'utf-8',
        timeout: 10000
    });

    const workflows = JSON.parse(result);
    console.log(`✓ Discovered ${workflows.length} workflows`);

    // Test 2: Categorize workflows
    console.log('\nTest 2: Categorizing workflows...');
    const categories = {
        quick: [],
        workflow: [],
        view: [],
        tool: []
    };

    const quickWorkflows = ['morning', 'ship', 'fix-all', 'learn', 'health'];
    const viewWorkflows = ['dashboard', 'costs', 'status'];
    const toolWorkflows = ['fix-lint', 'fix-format', 'sync-claude'];

    workflows.forEach(wf => {
        if (quickWorkflows.includes(wf.name)) {
            categories.quick.push(wf.name);
        } else if (viewWorkflows.includes(wf.name)) {
            categories.view.push(wf.name);
        } else if (toolWorkflows.includes(wf.name)) {
            categories.tool.push(wf.name);
        } else {
            categories.workflow.push(wf.name);
        }
    });

    console.log('Quick:', categories.quick.length, '-', categories.quick.join(', '));
    console.log('Workflow:', categories.workflow.length, '-', categories.workflow.join(', '));
    console.log('View:', categories.view.length, '-', categories.view.join(', '));
    console.log('Tool:', categories.tool.length, '-', categories.tool.join(', '));

    // Test 3: Verify workflow structure
    console.log('\nTest 3: Verifying workflow structure...');
    const firstWorkflow = workflows[0];
    console.log('Sample workflow:', JSON.stringify(firstWorkflow, null, 2));

    console.log('\n✅ All tests passed!');

} catch (error) {
    console.error('❌ Test failed:', error.message);
    if (error.stderr) {
        console.error('stderr:', error.stderr.toString());
    }
    process.exit(1);
}
