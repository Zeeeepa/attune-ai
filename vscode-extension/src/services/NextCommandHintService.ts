import * as vscode from 'vscode';

/**
 * NextCommandHintService - Ghost text hints for next command suggestions
 *
 * Shows contextual "Next: Ctrl+Shift+E S → Ship" hints:
 * - After command completion (3-5 seconds)
 * - On cursor idle (2+ seconds)
 *
 * Works in both power and guided modes (shared experience).
 */

interface CommandChain {
    trigger: string;
    suggestions: Array<{
        command: string;
        label: string;
        shortcut: string;
        description?: string;
    }>;
}

// Default command chains (will be merged with config + learned patterns)
const DEFAULT_CHAINS: CommandChain[] = [
    {
        trigger: 'empathy.morning',
        suggestions: [
            { command: 'empathy.ship', label: 'Ship', shortcut: 'Ctrl+Shift+E S', description: 'Pre-ship check' },
            { command: 'empathy.fixAll', label: 'Fix All', shortcut: 'Ctrl+Shift+E F', description: 'Fix all issues' },
        ],
    },
    {
        trigger: 'empathy.ship',
        suggestions: [
            { command: 'empathy.fixAll', label: 'Fix All', shortcut: 'Ctrl+Shift+E F', description: 'Fix remaining issues' },
            { command: 'empathy.dashboard', label: 'Dashboard', shortcut: 'Ctrl+Shift+E D', description: 'View dashboard' },
        ],
    },
    {
        trigger: 'empathy.fixAll',
        suggestions: [
            { command: 'empathy.runTests', label: 'Tests', shortcut: 'Ctrl+Shift+E T', description: 'Run tests' },
            { command: 'empathy.ship', label: 'Ship', shortcut: 'Ctrl+Shift+E S', description: 'Pre-ship check' },
        ],
    },
    {
        trigger: 'empathy.reviewFile',
        suggestions: [
            { command: 'empathy.fixLint', label: 'Fix Lint', shortcut: 'Ctrl+Shift+E L', description: 'Fix lint issues' },
            { command: 'empathy.generateTests', label: 'Gen Tests', shortcut: 'Ctrl+Shift+E G', description: 'Generate tests' },
        ],
    },
    {
        trigger: 'empathy.redetectKeyboardLayout',
        suggestions: [
            { command: 'empathy.applyKeyboardLayout', label: 'Apply Layout', shortcut: '', description: 'Apply optimized shortcuts' },
        ],
    },
    {
        trigger: 'empathy.togglePowerMode',
        suggestions: [
            { command: 'empathy.morning', label: 'Morning', shortcut: 'Ctrl+Shift+E M', description: 'Start your day' },
        ],
    },
];

export class NextCommandHintService {
    private static instance: NextCommandHintService;
    private lastCommand: string | null = null;
    private hintDecoration: vscode.TextEditorDecorationType | null = null;
    private idleTimer: NodeJS.Timeout | null = null;
    private hintTimer: NodeJS.Timeout | null = null;
    private commandHistory: string[] = [];
    private disposables: vscode.Disposable[] = [];

    private constructor() {}

    static getInstance(): NextCommandHintService {
        if (!NextCommandHintService.instance) {
            NextCommandHintService.instance = new NextCommandHintService();
        }
        return NextCommandHintService.instance;
    }

    /**
     * Initialize the service with event listeners
     */
    initialize(context: vscode.ExtensionContext): void {
        // Listen for cursor position changes (for idle detection)
        const cursorListener = vscode.window.onDidChangeTextEditorSelection(() => {
            this.resetIdleTimer();
        });
        this.disposables.push(cursorListener);

        // Listen for active editor changes
        const editorListener = vscode.window.onDidChangeActiveTextEditor(() => {
            this.clearHint();
            this.resetIdleTimer();
        });
        this.disposables.push(editorListener);

        context.subscriptions.push(...this.disposables);
    }

    /**
     * Record that a command was executed and show hint
     */
    recordCommand(commandId: string): void {
        this.lastCommand = commandId;
        this.commandHistory.push(commandId);

        // Keep history manageable
        if (this.commandHistory.length > 50) {
            this.commandHistory.shift();
        }

        // Show hint after command completion
        this.showHintForCommand(commandId);
    }

    /**
     * Show ghost text hint for the given command
     */
    private showHintForCommand(commandId: string): void {
        const chain = DEFAULT_CHAINS.find(c => c.trigger === commandId);
        if (!chain || chain.suggestions.length === 0) {
            return;
        }

        const suggestion = chain.suggestions[0];
        const hintText = this.formatHint(suggestion);

        this.displayHint(hintText, 4000); // Show for 4 seconds
    }

    /**
     * Format the hint text
     */
    private formatHint(suggestion: { label: string; shortcut: string; description?: string }): string {
        if (suggestion.shortcut) {
            return `Next: ${suggestion.shortcut} → ${suggestion.label}`;
        }
        return `Next: ${suggestion.label}`;
    }

    /**
     * Display the hint as ghost text or status bar
     */
    private displayHint(text: string, duration: number): void {
        this.clearHint();

        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            // Fallback to status bar
            vscode.window.setStatusBarMessage(`💡 ${text}`, duration);
            return;
        }

        // Create ghost text decoration
        this.hintDecoration = vscode.window.createTextEditorDecorationType({
            after: {
                contentText: `  💡 ${text}`,
                color: new vscode.ThemeColor('editorGhostText.foreground'),
                fontStyle: 'italic',
            },
            isWholeLine: true,
        });

        const position = editor.selection.active;
        const range = new vscode.Range(position.line, 0, position.line, 0);
        editor.setDecorations(this.hintDecoration, [range]);

        // Auto-dismiss
        this.hintTimer = setTimeout(() => {
            this.clearHint();
        }, duration);
    }

    /**
     * Clear any active hint
     */
    private clearHint(): void {
        if (this.hintDecoration) {
            this.hintDecoration.dispose();
            this.hintDecoration = null;
        }
        if (this.hintTimer) {
            clearTimeout(this.hintTimer);
            this.hintTimer = null;
        }
    }

    /**
     * Reset the idle timer (called on cursor movement)
     */
    private resetIdleTimer(): void {
        if (this.idleTimer) {
            clearTimeout(this.idleTimer);
        }

        // After 2 seconds of idle, show a contextual hint
        this.idleTimer = setTimeout(() => {
            this.showIdleHint();
        }, 2000);
    }

    /**
     * Show a contextual hint when cursor is idle
     */
    private showIdleHint(): void {
        // Don't show if there's already a hint
        if (this.hintDecoration) {
            return;
        }

        // Use the last command to suggest next step
        if (this.lastCommand) {
            const chain = DEFAULT_CHAINS.find(c => c.trigger === this.lastCommand);
            if (chain && chain.suggestions.length > 0) {
                const suggestion = chain.suggestions[0];
                const hintText = this.formatHint(suggestion);
                this.displayHint(hintText, 3000);
            }
        }
    }

    /**
     * Get suggestions for a given command (for UI display)
     */
    getSuggestionsFor(commandId: string): Array<{ command: string; label: string; shortcut: string; description?: string }> {
        const chain = DEFAULT_CHAINS.find(c => c.trigger === commandId);
        return chain?.suggestions || [];
    }

    /**
     * Dispose of all listeners
     */
    dispose(): void {
        this.clearHint();
        if (this.idleTimer) {
            clearTimeout(this.idleTimer);
        }
        this.disposables.forEach(d => d.dispose());
    }
}
