import * as vscode from 'vscode';

/**
 * FeedbackService - Unified feedback system for Empathy commands
 *
 * Supports two modes:
 * - "guided" (default): Modal dialogs with explanations for new users
 * - "power": Brief inline badge near cursor for experienced users
 *
 * Power mode preserves the "riff-like" keyboard flow without interruptions.
 */
export class FeedbackService {
    private static instance: FeedbackService;
    private activeDecoration: vscode.TextEditorDecorationType | null = null;

    private constructor() {}

    static getInstance(): FeedbackService {
        if (!FeedbackService.instance) {
            FeedbackService.instance = new FeedbackService();
        }
        return FeedbackService.instance;
    }

    /**
     * Get current feedback mode from settings
     */
    private getMode(): 'guided' | 'power' {
        const config = vscode.workspace.getConfiguration('empathy');
        return config.get<'guided' | 'power'>('feedbackMode', 'guided');
    }

    /**
     * Show feedback based on current mode
     */
    async notify(
        message: string,
        type: 'success' | 'info' | 'warning' | 'error' = 'info'
    ): Promise<string | undefined> {
        const mode = this.getMode();
        console.log(`[Empathy FeedbackService] notify called: mode=${mode}, message="${message}", type=${type}`);

        if (mode === 'power') {
            console.log('[Empathy FeedbackService] Showing inline badge');
            this.showInlineBadge(message, type);
            return undefined;
        } else {
            console.log('[Empathy FeedbackService] Showing guided dialog');
            return this.showGuidedDialog(message, type);
        }
    }

    /**
     * Show feedback with action buttons (guided mode only in guided, auto-execute in power)
     */
    async notifyWithActions(
        message: string,
        type: 'success' | 'info' | 'warning' | 'error',
        actions: string[],
        defaultAction?: string
    ): Promise<string | undefined> {
        const mode = this.getMode();

        if (mode === 'power') {
            // In power mode, show brief feedback and return default action
            this.showInlineBadge(message, type);
            return defaultAction;
        } else {
            return this.showGuidedDialogWithActions(message, type, actions);
        }
    }

    /**
     * Power mode: Brief inline badge near cursor
     */
    private showInlineBadge(message: string, type: string): void {
        // Clear any existing decoration
        if (this.activeDecoration) {
            this.activeDecoration.dispose();
            this.activeDecoration = null;
        }

        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            // FALLBACK: Status bar when no editor is open
            vscode.window.setStatusBarMessage(`${this.getIcon(type)} ${message}`, 1500);
            return;
        }

        // Create decoration at cursor position
        this.activeDecoration = vscode.window.createTextEditorDecorationType({
            after: {
                contentText: ` ${this.getIcon(type)} ${message}`,
                color: this.getColor(type),
                fontWeight: 'bold',
                margin: '0 0 0 1em',
            },
            isWholeLine: false,
        });

        const position = editor.selection.active;
        const range = new vscode.Range(position.line, 0, position.line, 0);

        editor.setDecorations(this.activeDecoration, [range]);

        // Auto-dismiss after 1.5 seconds
        const decoration = this.activeDecoration;
        setTimeout(() => {
            decoration.dispose();
            if (this.activeDecoration === decoration) {
                this.activeDecoration = null;
            }
        }, 1500);
    }

    /**
     * Guided mode: Modal dialog with OK button
     */
    private async showGuidedDialog(
        message: string,
        type: string
    ): Promise<string | undefined> {
        const icon = this.getIcon(type);
        const fullMessage = `${icon} ${message}`;

        switch (type) {
            case 'error':
                return vscode.window.showErrorMessage(fullMessage, { modal: true }, 'OK');
            case 'warning':
                return vscode.window.showWarningMessage(fullMessage, { modal: true }, 'OK');
            default:
                return vscode.window.showInformationMessage(fullMessage, { modal: true }, 'OK');
        }
    }

    /**
     * Guided mode: Modal dialog with action buttons
     */
    private async showGuidedDialogWithActions(
        message: string,
        type: string,
        actions: string[]
    ): Promise<string | undefined> {
        const icon = this.getIcon(type);
        const fullMessage = `${icon} ${message}`;

        switch (type) {
            case 'error':
                return vscode.window.showErrorMessage(fullMessage, { modal: true }, ...actions);
            case 'warning':
                return vscode.window.showWarningMessage(fullMessage, { modal: true }, ...actions);
            default:
                return vscode.window.showInformationMessage(fullMessage, { modal: true }, ...actions);
        }
    }

    /**
     * Get icon for feedback type
     */
    private getIcon(type: string): string {
        const icons: Record<string, string> = {
            success: '\u2713', // ✓
            info: '\u2139',    // ℹ
            warning: '\u26A0', // ⚠
            error: '\u2717',   // ✗
        };
        return icons[type] || '';
    }

    /**
     * Get color for feedback type
     */
    private getColor(type: string): string {
        const colors: Record<string, string> = {
            success: '#4EC9B0', // Green
            info: '#9CDCFE',    // Blue
            warning: '#DCDCAA', // Yellow
            error: '#F14C4C',   // Red
        };
        return colors[type] || '#CCCCCC';
    }
}
