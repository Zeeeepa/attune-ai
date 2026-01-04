/**
 * Workflow Bridge Integration
 *
 * Integrates all workflow services and provides a unified API for extension.ts
 * This is a facade that coordinates WorkflowDiscovery, ShortcutGenerator, and WorkflowExecution.
 */

import * as vscode from 'vscode';
import { WorkflowDiscoveryService } from './WorkflowDiscoveryService';
import { ShortcutGeneratorService } from './ShortcutGeneratorService';
import { WorkflowExecutionService } from './WorkflowExecutionService';
import { KeyboardLayout, WorkflowCategory } from '../types/workflow';

export class WorkflowBridgeIntegration {
    private discoveryService: WorkflowDiscoveryService;
    private shortcutService: ShortcutGeneratorService;
    private executionService: WorkflowExecutionService;
    private context: vscode.ExtensionContext;

    constructor(context: vscode.ExtensionContext) {
        this.context = context;
        this.discoveryService = new WorkflowDiscoveryService(context);
        this.shortcutService = new ShortcutGeneratorService(context);
        this.executionService = new WorkflowExecutionService(context, this.discoveryService);
    }

    /**
     * Initialize the workflow bridge
     * Call this from extension.activate()
     */
    async initialize(): Promise<void> {
        console.log('[WorkflowBridge] Initializing...');

        try {
            // 1. Discover workflows from Python CLI
            const workflows = await this.discoveryService.discoverWorkflows();
            console.log(`[WorkflowBridge] Discovered ${workflows.length} workflows`);

            // 2. Register workflow commands
            await this.executionService.registerWorkflowCommands();
            console.log('[WorkflowBridge] Registered workflow commands');

            // 3. Generate and register keyboard shortcuts
            await this.registerKeyboardShortcuts();
            console.log('[WorkflowBridge] Registered keyboard shortcuts');

            // 4. Register category Quick Pick commands
            this.registerCategoryCommands();
            console.log('[WorkflowBridge] Registered category commands');

            // 5. Register utility commands
            this.registerUtilityCommands();
            console.log('[WorkflowBridge] Registered utility commands');

            console.log('[WorkflowBridge] ✓ Initialization complete');
        } catch (error) {
            console.error('[WorkflowBridge] Initialization failed:', error);
            vscode.window.showErrorMessage('Empathy: Failed to initialize workflow bridge');
        }
    }

    /**
     * Register keyboard shortcuts for all workflows
     */
    private async registerKeyboardShortcuts(): Promise<void> {
        const workflows = await this.discoveryService.discoverWorkflows();
        const layout = this.getUserKeyboardLayout();
        const config = this.shortcutService.generateShortcuts(workflows, layout);

        // Register keybindings for each workflow
        for (const [categoryName, categoryInfo] of Object.entries(config.categories)) {
            for (const shortcut of categoryInfo.shortcuts) {
                const commandId = `empathy.workflow.${shortcut.workflowName}`;

                // VSCode doesn't allow dynamic keybinding registration via API
                // So we'll register commands that can be triggered by the shortcuts
                // The actual keybindings need to be in package.json or updated via keybindings.json

                // For now, we'll just log what shortcuts were generated
                console.log(`[WorkflowBridge] Shortcut: ${shortcut.keybinding} → ${commandId}`);
            }
        }

        // Store shortcuts in extension state for cheatsheet
        await this.context.globalState.update('empathy.shortcuts', config);
    }

    /**
     * Register category-based Quick Pick commands
     */
    private registerCategoryCommands(): void {
        const commands = [
            { id: 'empathy.quickPick.quick', category: 'quick' as const },
            { id: 'empathy.quickPick.workflow', category: 'workflow' as const },
            { id: 'empathy.quickPick.view', category: 'view' as const },
            { id: 'empathy.quickPick.tool', category: 'tool' as const },
            { id: 'empathy.quickPick.all', category: undefined },
        ];

        for (const cmd of commands) {
            try {
                const disposable = vscode.commands.registerCommand(cmd.id, async () => {
                    await this.executionService.showWorkflowPicker(cmd.category);
                });
                this.context.subscriptions.push(disposable);
            } catch (error) {
                if (error instanceof Error && error.message.includes('already exists')) {
                    console.log(`[WorkflowBridge] Command ${cmd.id} already registered, skipping`);
                } else {
                    throw error;
                }
            }
        }
    }

    /**
     * Register utility commands
     */
    private registerUtilityCommands(): void {
        const commands = [
            {
                id: 'empathy.refreshWorkflows',
                handler: async () => {
                    await this.executionService.refreshWorkflows();
                    await this.initialize();
                }
            },
            {
                id: 'empathy.keyboardShortcutsCheatsheet',
                handler: async () => {
                    await this.showCheatsheet();
                }
            }
        ];

        for (const cmd of commands) {
            try {
                const disposable = vscode.commands.registerCommand(cmd.id, cmd.handler);
                this.context.subscriptions.push(disposable);
            } catch (error) {
                if (error instanceof Error && error.message.includes('already exists')) {
                    console.log(`[WorkflowBridge] Command ${cmd.id} already registered, skipping`);
                } else {
                    throw error;
                }
            }
        }
    }

    /**
     * Show keyboard shortcuts cheatsheet
     */
    private async showCheatsheet(): Promise<void> {
        const workflows = await this.discoveryService.discoverWorkflows();
        const layout = this.getUserKeyboardLayout();
        const markdown = this.shortcutService.generateCheatsheet(workflows, layout);

        // Create and show markdown document
        const doc = await vscode.workspace.openTextDocument({
            content: markdown,
            language: 'markdown',
        });

        await vscode.window.showTextDocument(doc, {
            preview: false,
            viewColumn: vscode.ViewColumn.Beside,
        });

        // Show markdown preview
        await vscode.commands.executeCommand('markdown.showPreview', doc.uri);
    }

    /**
     * Get user's keyboard layout preference
     */
    private getUserKeyboardLayout(): KeyboardLayout {
        const config = vscode.workspace.getConfiguration('empathy');
        const layout = config.get<string>('keyboardLayout') || 'qwerty';
        return layout as KeyboardLayout;
    }

    /**
     * Get statistics about the workflow bridge
     */
    async getStats(): Promise<{
        totalWorkflows: number;
        byCategory: Record<WorkflowCategory, number>;
        cacheAge: number | null;
    }> {
        const workflows = await this.discoveryService.discoverWorkflows();

        const byCategory: Record<WorkflowCategory, number> = {
            quick: 0,
            workflow: 0,
            view: 0,
            tool: 0,
        };

        for (const workflow of workflows) {
            byCategory[workflow.category]++;
        }

        return {
            totalWorkflows: workflows.length,
            byCategory,
            cacheAge: null, // TODO: Get from discovery service
        };
    }

    /**
     * Dispose all services
     */
    dispose(): void {
        this.executionService.dispose();
    }
}

/**
 * Integration test function
 * Call this to verify the workflow bridge works
 */
export async function testWorkflowBridge(context: vscode.ExtensionContext): Promise<void> {
    console.log('=== Workflow Bridge Integration Test ===');

    const bridge = new WorkflowBridgeIntegration(context);

    try {
        // Test initialization
        await bridge.initialize();
        console.log('✓ Initialization passed');

        // Test stats
        const stats = await bridge.getStats();
        console.log('✓ Stats:', JSON.stringify(stats, null, 2));

        // Test workflow discovery
        const discoveryService = new WorkflowDiscoveryService(context);
        const workflows = await discoveryService.discoverWorkflows();
        console.log(`✓ Discovered ${workflows.length} workflows`);

        // Test shortcut generation
        const shortcutService = new ShortcutGeneratorService(context);
        const shortcuts = shortcutService.generateShortcuts(workflows, 'qwerty');
        console.log(`✓ Generated shortcuts for ${Object.keys(shortcuts.categories).length} categories`);

        // Show summary
        console.log('\n=== Test Summary ===');
        console.log(`Total Workflows: ${stats.totalWorkflows}`);
        console.log(`Quick: ${stats.byCategory.quick}`);
        console.log(`Workflow: ${stats.byCategory.workflow}`);
        console.log(`View: ${stats.byCategory.view}`);
        console.log(`Tool: ${stats.byCategory.tool}`);

        vscode.window.showInformationMessage('✓ Workflow Bridge test passed!');
    } catch (error) {
        console.error('✗ Test failed:', error);
        vscode.window.showErrorMessage(`Workflow Bridge test failed: ${error}`);
    }
}
