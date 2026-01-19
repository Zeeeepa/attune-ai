/**
 * Meta-Workflow Commands
 *
 * Provides VS Code command palette integration for meta-workflow CLI commands.
 * Executes Empathy Framework meta-workflow system commands.
 *
 * Copyright 2026 Smart AI Memory, LLC
 * Licensed under Fair Source 0.9
 */

import * as vscode from 'vscode';
import * as cp from 'child_process';

/**
 * Execute CLI command and show output
 */
async function executeCliCommand(command: string, args: string[]): Promise<void> {
    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (!workspaceFolders || workspaceFolders.length === 0) {
        vscode.window.showErrorMessage('Please open a workspace folder first.');
        return;
    }

    const cwd = workspaceFolders[0].uri.fsPath;

    return new Promise((resolve, reject) => {
        const fullCommand = `empathy ${command} ${args.join(' ')}`;

        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: `Running: ${fullCommand}`,
            cancellable: false
        }, async () => {
            return new Promise<void>((progressResolve) => {
                cp.exec(fullCommand, { cwd }, (error, stdout, stderr) => {
                    if (error) {
                        vscode.window.showErrorMessage(`Error: ${error.message}`);
                        reject(error);
                    } else {
                        // Show output in new document
                        const output = stdout + (stderr ? `\n\nErrors:\n${stderr}` : '');
                        vscode.workspace.openTextDocument({
                            content: output,
                            language: 'markdown'
                        }).then(doc => {
                            vscode.window.showTextDocument(doc);
                            progressResolve();
                            resolve();
                        });
                    }
                });
            });
        });
    });
}

/**
 * List meta-workflow templates
 */
export async function listTemplates(): Promise<void> {
    vscode.window.showInformationMessage('Loading meta-workflow templates...');
    await executeCliCommand('meta-workflow', ['list-templates']);
}

/**
 * Inspect a meta-workflow template
 */
export async function inspectTemplate(): Promise<void> {
    // Show quick pick with known templates (v4.3.0 built-in templates)
    const templates = [
        { label: '🚀 Release Preparation', value: 'release-prep' },
        { label: '🧪 Test Coverage Boost', value: 'test-coverage-boost' },
        { label: '🔧 Test Maintenance', value: 'test-maintenance' },
        { label: '📚 Documentation Management', value: 'manage-docs' },
        { label: '⌨️  Custom Template (Enter ID)', value: '__custom__' }
    ];

    const selected = await vscode.window.showQuickPick(templates, {
        placeHolder: 'Select template to inspect',
        ignoreFocusOut: true
    });

    if (!selected) {
        return;
    }

    let templateId = selected.value;

    if (templateId === '__custom__') {
        const customId = await vscode.window.showInputBox({
            prompt: 'Enter template ID to inspect',
            placeHolder: 'e.g., my_custom_workflow',
            ignoreFocusOut: true
        });

        if (!customId) {
            return;
        }

        templateId = customId;
    }

    vscode.window.showInformationMessage(`Inspecting template: ${templateId}`);
    await executeCliCommand('meta-workflow', ['inspect', templateId]);
}

/**
 * Run a meta-workflow
 */
export async function runMetaWorkflow(): Promise<void> {
    console.log('[Empathy] runMetaWorkflow called');
    vscode.window.showInformationMessage('Meta-workflow command triggered!');

    try {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        console.log('[Empathy] Workspace folders:', workspaceFolders?.length);

        if (!workspaceFolders || workspaceFolders.length === 0) {
            vscode.window.showErrorMessage('Empathy: Please open a workspace folder first.');
            return;
        }

        console.log('[Empathy] Preparing quick-pick menu...');

        // Show quick pick with known templates (v4.3.0 built-in templates)
        const templates = [
            {
                label: '🚀 Release Preparation',
                description: 'release-prep',
                detail: 'Security, testing, code quality, and docs (~$0.10-$0.75)'
            },
            {
                label: '🧪 Test Coverage Boost',
                description: 'test-coverage-boost',
                detail: 'Analyze gaps and generate tests (~$0.15-$1.00)'
            },
            {
                label: '🔧 Test Maintenance',
                description: 'test-maintenance',
                detail: 'Fix stale tests, lifecycle management (~$0.10-$0.80)'
            },
            {
                label: '📚 Documentation Management',
                description: 'manage-docs',
                detail: 'Sync docs with code, find gaps (~$0.08-$0.50)'
            },
            {
                label: '⌨️  Custom Template (Enter ID)',
                description: '__custom__',
                detail: 'Enter a custom template ID'
            }
        ];

        console.log('[Empathy] Showing quick-pick with', templates.length, 'templates');

        const selected = await vscode.window.showQuickPick(templates, {
            placeHolder: 'Select a meta-workflow template to run',
            ignoreFocusOut: true
        });

        console.log('[Empathy] User selected:', selected ? selected.label : 'nothing');

        if (!selected) {
            console.log('[Empathy] User canceled template selection');
            return;
        }

        let templateId = selected.description;

        // Handle custom template input
        if (templateId === '__custom__') {
            const customId = await vscode.window.showInputBox({
                prompt: 'Enter template ID',
                placeHolder: 'e.g., my_custom_workflow',
                ignoreFocusOut: true
            });

            if (!customId) {
                console.log('[Empathy] User canceled custom template input');
                return;
            }

            templateId = customId;
        }

        console.log(`[Empathy] Creating terminal for template: ${templateId}`);

        // Execute in terminal for interactivity
        const terminal = vscode.window.createTerminal({
            name: 'Empathy Meta-Workflow',
            cwd: workspaceFolders[0].uri.fsPath
        });

        terminal.show();

        // Small delay to ensure terminal is ready
        await new Promise(resolve => setTimeout(resolve, 100));

        const command = `empathy meta-workflow run ${templateId}`;
        console.log(`[Empathy] Sending command to terminal: ${command}`);
        terminal.sendText(command);

        vscode.window.showInformationMessage(`✅ Started meta-workflow: ${templateId}`, 'View Terminal').then(selection => {
            if (selection === 'View Terminal') {
                terminal.show();
            }
        });
    } catch (error) {
        console.error('[Empathy] Error in runMetaWorkflow:', error);
        vscode.window.showErrorMessage(`Failed to run meta-workflow: ${error}`);
    }
}

/**
 * Show meta-workflow analytics
 */
export async function showAnalytics(): Promise<void> {
    vscode.window.showInformationMessage('Loading meta-workflow analytics...');
    await executeCliCommand('meta-workflow', ['analytics']);
}

/**
 * List meta-workflow execution history
 */
export async function listRuns(): Promise<void> {
    vscode.window.showInformationMessage('Loading execution history...');
    await executeCliCommand('meta-workflow', ['list-runs']);
}

/**
 * Show meta-workflow session statistics
 */
export async function showSessionStats(): Promise<void> {
    vscode.window.showInformationMessage('Loading session statistics...');
    await executeCliCommand('meta-workflow', ['session-stats']);
}

/**
 * Register all meta-workflow commands
 */
export function registerMetaWorkflowCommands(context: vscode.ExtensionContext): void {
    context.subscriptions.push(
        vscode.commands.registerCommand('empathy.metaWorkflow.listTemplates', listTemplates),
        vscode.commands.registerCommand('empathy.metaWorkflow.inspect', inspectTemplate),
        vscode.commands.registerCommand('empathy.metaWorkflow.run', runMetaWorkflow),
        vscode.commands.registerCommand('empathy.metaWorkflow.analytics', showAnalytics),
        vscode.commands.registerCommand('empathy.metaWorkflow.listRuns', listRuns),
        vscode.commands.registerCommand('empathy.metaWorkflow.sessionStats', showSessionStats)
    );
}
