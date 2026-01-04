/**
 * Type definitions for workflow discovery and keyboard shortcuts
 */

export type WorkflowCategory = 'quick' | 'workflow' | 'view' | 'tool';
export type KeyboardLayout = 'qwerty' | 'dvorak' | 'colemak';

/**
 * A workflow discovered from the Python CLI
 */
export interface Workflow {
    /** Unique identifier (e.g., "bug-predict", "morning") */
    name: string;

    /** Human-readable description */
    description: string;

    /** Category for shortcut routing (Q/W/V/T) */
    category: WorkflowCategory;

    /** Workflow stages (e.g., ["scan", "correlate", "predict"]) */
    stages?: string[];

    /** VSCode icon identifier (e.g., "$(bug)") */
    icon?: string;

    /** Whether this is a built-in quick command */
    isBuiltIn?: boolean;
}

/**
 * A keyboard shortcut assignment for a workflow
 */
export interface ShortcutMapping {
    /** Workflow name */
    workflowName: string;

    /** Category letter (Q/W/V/T) */
    category: string;

    /** Assigned letter key */
    key: string;

    /** Full keybinding (e.g., "cmd+shift+e q m") */
    keybinding: string;

    /** Mnemonic phrase (e.g., "Q M = Quick Morning") */
    mnemonic: string;

    /** Whether key is on home row */
    homeRow: boolean;

    /** Keyboard layout */
    layout: KeyboardLayout;
}

/**
 * Complete shortcut configuration for all workflows
 */
export interface ShortcutConfiguration {
    /** Shortcuts grouped by category */
    categories: {
        [category: string]: {
            prefix: string; // e.g., "cmd+shift+e q"
            shortcuts: ShortcutMapping[];
        };
    };

    /** Layouts supported */
    layouts: {
        [layout: string]: KeyboardLayoutConfig;
    };

    /** Generation timestamp */
    generatedAt: string;

    /** Version of generator */
    version: string;
}

/**
 * Keyboard layout configuration
 */
export interface KeyboardLayoutConfig {
    layout: KeyboardLayout;
    homeRow: string[];
    topRow: string[];
    bottomRow: string[];
    mnemonicBase: string;
}

/**
 * Workflow data from Python CLI (empathy workflow list --json)
 */
export interface PythonWorkflowData {
    name: string;
    class: string;
    description: string;
    stages: string[];
    tier_map: Record<string, string>;
}

/**
 * Category configuration
 */
export interface CategoryConfig {
    name: string;
    letter: string; // Q, W, V, T
    description: string;
    icon: string;
    workflows: string[]; // Workflow names in this category
}
