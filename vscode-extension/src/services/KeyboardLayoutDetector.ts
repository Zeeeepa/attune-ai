/**
 * Keyboard Layout Detector Service
 *
 * Detects the OS keyboard layout (QWERTY, Dvorak, Colemak) using
 * platform-specific shell commands. Falls back to user preference.
 *
 * Supports:
 * - macOS: HIToolbox input sources, system preferences
 * - Windows: PowerShell language list, registry, layout IDs
 * - Linux: setxkbmap, gsettings (GNOME), kreadconfig5 (KDE), localectl
 *
 * Part of the Keyboard Conductor automation system.
 */

import * as vscode from 'vscode';
import * as cp from 'child_process';

export type KeyboardLayout = 'qwerty' | 'dvorak' | 'colemak';

/**
 * Known keyboard layout identifiers by platform
 */
const LAYOUT_PATTERNS = {
    dvorak: {
        keywords: ['dvorak', 'dvp', 'programmer dvorak'],
        // Windows keyboard layout IDs for Dvorak variants
        windowsIds: ['00010409', '00020409', '00030409', 'd0010409'],
        // macOS layout names
        macNames: ['dvorak', 'dvorak - qwerty', 'dvorak-qwerty ⌘', 'programmer dvorak'],
    },
    colemak: {
        keywords: ['colemak', 'colemak-dh', 'colemak_dh'],
        windowsIds: [],  // Colemak typically installed as custom
        macNames: ['colemak'],
    },
};

export class KeyboardLayoutDetector {
    private static instance: KeyboardLayoutDetector | null = null;
    private context: vscode.ExtensionContext | null = null;
    private cachedLayout: KeyboardLayout | null = null;

    private constructor() {}

    static getInstance(): KeyboardLayoutDetector {
        if (!KeyboardLayoutDetector.instance) {
            KeyboardLayoutDetector.instance = new KeyboardLayoutDetector();
        }
        return KeyboardLayoutDetector.instance;
    }

    initialize(context: vscode.ExtensionContext): void {
        this.context = context;
    }

    /**
     * Detect the current keyboard layout from the OS
     */
    async detect(): Promise<KeyboardLayout> {
        // Use cached value if available
        if (this.cachedLayout) {
            return this.cachedLayout;
        }

        try {
            const platform = process.platform;
            let layout: KeyboardLayout = 'qwerty';

            if (platform === 'darwin') {
                layout = await this.detectMacOS();
            } else if (platform === 'win32') {
                layout = await this.detectWindows();
            } else if (platform === 'linux') {
                layout = await this.detectLinux();
            }

            this.cachedLayout = layout;
            return layout;
        } catch (error) {
            console.warn('Keyboard layout detection failed, using preference:', error);
            return this.getUserPreference();
        }
    }

    /**
     * Detect keyboard layout on macOS
     *
     * Tries multiple methods:
     * 1. HIToolbox input sources (primary)
     * 2. System Preferences plist (fallback)
     */
    private async detectMacOS(): Promise<KeyboardLayout> {
        // Try primary method first
        const primary = await this.execCommand(
            'defaults read com.apple.HIToolbox AppleSelectedInputSources 2>/dev/null'
        );

        if (primary) {
            const layout = this.parseLayoutFromOutput(primary);
            if (layout !== 'qwerty') {
                return layout;
            }
        }

        // Fallback: check keyboard layout ID directly
        const fallback = await this.execCommand(
            'defaults read com.apple.HIToolbox AppleCurrentKeyboardLayoutInputSourceID 2>/dev/null'
        );

        if (fallback) {
            const layout = this.parseLayoutFromOutput(fallback);
            if (layout !== 'qwerty') {
                return layout;
            }
        }

        return primary ? this.parseLayoutFromOutput(primary) : this.getUserPreference();
    }

    /**
     * Detect keyboard layout on Windows
     *
     * Tries multiple methods:
     * 1. PowerShell Get-WinUserLanguageList (modern)
     * 2. Registry query (fallback for older systems)
     * 3. PowerShell keyboard layout name
     */
    private async detectWindows(): Promise<KeyboardLayout> {
        // Try PowerShell language list first
        const langList = await this.execCommand(
            'powershell -NoProfile -Command "Get-WinUserLanguageList | Select-Object -ExpandProperty InputMethodTips"',
            3000
        );

        if (langList) {
            const layout = this.parseLayoutFromOutput(langList);
            if (layout !== 'qwerty') {
                return layout;
            }
        }

        // Fallback: Get current keyboard layout name
        const layoutName = await this.execCommand(
            'powershell -NoProfile -Command "(Get-Culture).KeyboardLayoutId; (Get-WinUserLanguageList).LocalizedName"',
            3000
        );

        if (layoutName) {
            const layout = this.parseLayoutFromOutput(layoutName);
            if (layout !== 'qwerty') {
                return layout;
            }
        }

        // Final fallback: Registry query
        const registry = await this.execCommand(
            'reg query "HKCU\\Keyboard Layout\\Preload" 2>nul',
            2000
        );

        if (registry) {
            const layout = this.parseLayoutFromOutput(registry);
            if (layout !== 'qwerty') {
                return layout;
            }
        }

        return langList ? this.parseLayoutFromOutput(langList) : this.getUserPreference();
    }

    /**
     * Detect keyboard layout on Linux
     *
     * Tries multiple methods for different desktop environments:
     * 1. setxkbmap (X11 - most common)
     * 2. gsettings (GNOME/GTK)
     * 3. kreadconfig5 (KDE Plasma)
     * 4. localectl (systemd fallback)
     */
    private async detectLinux(): Promise<KeyboardLayout> {
        // Try setxkbmap first (works on most X11 systems)
        const xkb = await this.execCommand('setxkbmap -query 2>/dev/null');
        if (xkb) {
            const layout = this.parseLayoutFromOutput(xkb);
            if (layout !== 'qwerty') {
                return layout;
            }
        }

        // Try GNOME/GTK settings
        const gnome = await this.execCommand(
            'gsettings get org.gnome.desktop.input-sources sources 2>/dev/null'
        );
        if (gnome) {
            const layout = this.parseLayoutFromOutput(gnome);
            if (layout !== 'qwerty') {
                return layout;
            }
        }

        // Try KDE Plasma settings
        const kde = await this.execCommand(
            'kreadconfig5 --group Layout --key LayoutList 2>/dev/null'
        );
        if (kde) {
            const layout = this.parseLayoutFromOutput(kde);
            if (layout !== 'qwerty') {
                return layout;
            }
        }

        // Try localectl (systemd)
        const localectl = await this.execCommand('localectl status 2>/dev/null');
        if (localectl) {
            const layout = this.parseLayoutFromOutput(localectl);
            if (layout !== 'qwerty') {
                return layout;
            }
        }

        // Return qwerty or user preference
        return xkb ? this.parseLayoutFromOutput(xkb) : this.getUserPreference();
    }

    /**
     * Get user's saved layout preference
     */
    getUserPreference(): KeyboardLayout {
        const config = vscode.workspace.getConfiguration('empathy');
        return config.get<KeyboardLayout>('keyboardLayout', 'qwerty');
    }

    /**
     * Check if first-run detection has already happened
     */
    hasDetectedBefore(): boolean {
        if (!this.context) return false;
        return this.context.globalState.get<boolean>('keyboardLayoutDetected', false);
    }

    /**
     * Mark that first-run detection has happened
     */
    markDetected(): void {
        if (this.context) {
            this.context.globalState.update('keyboardLayoutDetected', true);
        }
    }

    /**
     * Run first-time detection and prompt user
     */
    async promptFirstTimeDetection(): Promise<void> {
        if (this.hasDetectedBefore()) {
            return;
        }

        const detected = await this.detect();
        const current = this.getUserPreference();

        // Only prompt if detected layout differs from current setting
        if (detected !== current && detected !== 'qwerty') {
            const action = await vscode.window.showInformationMessage(
                `Detected ${detected.toUpperCase()} keyboard layout. Apply optimized Empathy shortcuts?`,
                'Apply',
                'Keep Current'
            );

            if (action === 'Apply') {
                const config = vscode.workspace.getConfiguration('empathy');
                await config.update('keyboardLayout', detected, vscode.ConfigurationTarget.Global);

                // Show success and guide to keybindings
                const viewAction = await vscode.window.showInformationMessage(
                    `Applied ${detected.toUpperCase()} layout. View keybindings?`,
                    'View Keybindings',
                    'Later'
                );

                if (viewAction === 'View Keybindings') {
                    await vscode.commands.executeCommand('empathy.applyKeyboardLayout');
                }
            }
        } else if (detected !== 'qwerty') {
            // Layout matches, just log it
            console.log(`Empathy: Detected ${detected} keyboard layout (matches current setting)`);
        }

        this.markDetected();
    }

    /**
     * Get layout-specific home row keys
     */
    static getHomeRowKeys(layout: KeyboardLayout): string[] {
        switch (layout) {
            case 'dvorak':
                return ['a', 'o', 'e', 'u'];
            case 'colemak':
                return ['a', 'r', 's', 't'];
            case 'qwerty':
            default:
                return ['a', 's', 'd', 'f'];
        }
    }

    /**
     * Get layout-specific mnemonic phrase
     */
    static getMnemonicPhrase(layout: KeyboardLayout): string {
        switch (layout) {
            case 'dvorak':
                return 'AOEU - vowels for daily actions';
            case 'colemak':
                return 'ARST - your daily rhythm';
            case 'qwerty':
            default:
                return 'My Ship Floats Daily';
        }
    }

    /**
     * Clear cached layout (useful when user manually changes layout)
     */
    clearCache(): void {
        this.cachedLayout = null;
    }

    // =========================================================================
    // Helper Methods
    // =========================================================================

    /**
     * Execute a shell command and return stdout
     */
    private execCommand(command: string, timeout: number = 2000): Promise<string | null> {
        return new Promise((resolve) => {
            cp.exec(command, { timeout }, (error, stdout) => {
                if (error || !stdout) {
                    resolve(null);
                } else {
                    resolve(stdout);
                }
            });
        });
    }

    /**
     * Parse keyboard layout from command output using pattern matching
     */
    private parseLayoutFromOutput(output: string): KeyboardLayout {
        const lowerOutput = output.toLowerCase();

        // Check Dvorak patterns
        for (const keyword of LAYOUT_PATTERNS.dvorak.keywords) {
            if (lowerOutput.includes(keyword)) {
                return 'dvorak';
            }
        }

        // Check Windows Dvorak layout IDs
        for (const id of LAYOUT_PATTERNS.dvorak.windowsIds) {
            if (lowerOutput.includes(id)) {
                return 'dvorak';
            }
        }

        // Check Colemak patterns
        for (const keyword of LAYOUT_PATTERNS.colemak.keywords) {
            if (lowerOutput.includes(keyword)) {
                return 'colemak';
            }
        }

        return 'qwerty';
    }
}
