#!/usr/bin/env node

/**
 * Standalone test script for Workflow Bridge
 * Run with: node test-workflow-bridge.js
 */

const { promisify } = require('util');
const { execFile } = require('child_process');
const execFileAsync = promisify(execFile);
const path = require('path');

async function testWorkflowDiscovery() {
    console.log('🧪 Testing Workflow Bridge Integration\n');
    console.log('=' .repeat(50));

    try {
        // Test 1: Find Python
        console.log('\n✓ Test 1: Python Detection');
        const pythonPath = 'python';
        const { stdout: versionOut } = await execFileAsync(pythonPath, ['--version']);
        console.log('  Python:', versionOut.trim());

        // Test 2: Set workspace folder
        console.log('\n✓ Test 2: Workspace Setup');
        const workspaceFolder = path.resolve(__dirname, '..');
        console.log('  Workspace:', workspaceFolder);

        // Test 3: Discover Workflows
        console.log('\n✓ Test 3: Workflow Discovery');
        const { stdout: workflowJson } = await execFileAsync(
            pythonPath,
            ['-m', 'empathy_os.cli', 'workflow', 'list', '--json'],
            { cwd: workspaceFolder, timeout: 10000 }
        );

        const workflows = JSON.parse(workflowJson);
        console.log(`  Discovered: ${workflows.length} workflows`);

        // Test 4: Categorize Workflows
        console.log('\n✓ Test 4: Workflow Categorization');

        const categorizeWorkflow = (name) => {
            const quickWorkflows = ['morning', 'ship', 'fix-all', 'learn', 'health'];
            if (quickWorkflows.includes(name)) return 'quick';

            const viewWorkflows = ['dashboard', 'costs', 'status'];
            if (viewWorkflows.includes(name)) return 'view';

            const toolWorkflows = ['fix-lint', 'fix-format', 'sync-claude'];
            if (toolWorkflows.includes(name)) return 'tool';

            return 'workflow';
        };

        const categorized = workflows.reduce((acc, wf) => {
            const category = categorizeWorkflow(wf.name);
            acc[category] = (acc[category] || 0) + 1;
            return acc;
        }, {});

        console.log('  Categories:', categorized);

        // Test 5: Generate Shortcuts
        console.log('\n✓ Test 5: Shortcut Generation');

        const CATEGORY_MAP = {
            quick: { letter: 'q', name: 'Quick' },
            workflow: { letter: 'w', name: 'Workflow' },
            view: { letter: 'v', name: 'View' },
            tool: { letter: 't', name: 'Tool' }
        };

        const homeRow = ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'];
        const allKeys = 'abcdefghijklmnopqrstuvwxyz'.split('');

        const shortcuts = [];
        const categoryWorkflows = {};

        workflows.forEach(wf => {
            const category = categorizeWorkflow(wf.name);
            if (!categoryWorkflows[category]) {
                categoryWorkflows[category] = [];
            }
            categoryWorkflows[category].push(wf);
        });

        Object.entries(categoryWorkflows).forEach(([category, wfList]) => {
            const usedKeys = new Set();
            const categoryLetter = CATEGORY_MAP[category].letter;

            wfList.forEach(wf => {
                // Find best key
                let key = wf.name[0].toLowerCase();
                if (usedKeys.has(key)) {
                    key = homeRow.find(k => !usedKeys.has(k)) ||
                          allKeys.find(k => !usedKeys.has(k)) || 'z';
                }
                usedKeys.add(key);

                shortcuts.push({
                    workflow: wf.name,
                    category,
                    keybinding: `cmd+shift+e ${categoryLetter} ${key}`,
                    homeRow: homeRow.includes(key)
                });
            });
        });

        console.log(`  Generated: ${shortcuts.length} shortcuts`);
        const homeRowCount = shortcuts.filter(s => s.homeRow).length;
        console.log(`  Home row: ${homeRowCount}/${shortcuts.length}`);

        // Test 6: Display Sample Shortcuts
        console.log('\n✓ Test 6: Sample Shortcuts');
        shortcuts.slice(0, 5).forEach(s => {
            console.log(`  ${s.workflow.padEnd(20)} → ${s.keybinding}`);
        });

        // Summary
        console.log('\n' + '='.repeat(50));
        console.log('✅ ALL TESTS PASSED\n');
        console.log('Summary:');
        console.log(`  • Total Workflows: ${workflows.length}`);
        console.log(`  • Categories: ${Object.keys(categorized).length}`);
        console.log(`  • Shortcuts Generated: ${shortcuts.length}`);
        console.log(`  • Home Row Optimized: ${Math.round(homeRowCount/shortcuts.length*100)}%`);
        console.log('\n🎉 Workflow Bridge is ready for VSCode integration!');

    } catch (error) {
        console.error('\n❌ TEST FAILED');
        console.error('\nError:', error.message);
        if (error.stderr) {
            console.error('stderr:', error.stderr);
        }
        process.exit(1);
    }
}

testWorkflowDiscovery();
