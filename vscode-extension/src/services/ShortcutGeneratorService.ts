/**
 * Shortcut Generator Service
 *
 * Generates three-level keyboard shortcuts for workflows with conflict resolution.
 * Pattern: cmd+shift+e <category> <letter>
 * Categories: Q=Quick, W=Workflows, V=Views, T=Tools
 */

import * as vscode from 'vscode';
import {
    Workflow,
    ShortcutMapping,
    ShortcutConfiguration,
    KeyboardLayout,
    KeyboardLayoutConfig,
} from '../types/workflow';

export class ShortcutGeneratorService {
    private static readonly CATEGORY_MAP = {
        quick: { letter: 'q', name: 'Quick' },
        workflow: { letter: 'w', name: 'Workflow' },
        view: { letter: 'v', name: 'View' },
        tool: { letter: 't', name: 'Tool' },
    };

    private static readonly LAYOUTS: Record<KeyboardLayout, KeyboardLayoutConfig> = {
        qwerty: {
            layout: 'qwerty',
            homeRow: ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
            topRow: ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
            bottomRow: ['z', 'x', 'c', 'v', 'b', 'n', 'm'],
            mnemonicBase: 'QWERTY',
        },
        dvorak: {
            layout: 'dvorak',
            homeRow: ['a', 'o', 'e', 'u', 'i', 'd', 'h', 't', 'n', 's'],
            topRow: ["'", ',', '.', 'p', 'y', 'f', 'g', 'c', 'r', 'l'],
            bottomRow: [';', 'q', 'j', 'k', 'x', 'b', 'm', 'w', 'v', 'z'],
            mnemonicBase: 'Dvorak',
        },
        colemak: {
            layout: 'colemak',
            homeRow: ['a', 'r', 's', 't', 'd', 'h', 'n', 'e', 'i', 'o'],
            topRow: ['q', 'w', 'f', 'p', 'g', 'j', 'l', 'u', 'y', ';'],
            bottomRow: ['z', 'x', 'c', 'v', 'b', 'k', 'm', ',', '.'],
            mnemonicBase: 'Colemak',
        },
    };

    private context: vscode.ExtensionContext;

    constructor(context: vscode.ExtensionContext) {
        this.context = context;
    }

    /**
     * Generate shortcuts for all workflows
     */
    generateShortcuts(workflows: Workflow[], layout: KeyboardLayout = 'qwerty'): ShortcutConfiguration {
        const layoutConfig = ShortcutGeneratorService.LAYOUTS[layout];
        const shortcuts = this.assignShortcuts(workflows, layoutConfig);

        // Group by category
        const categories: ShortcutConfiguration['categories'] = {};
        for (const [category, info] of Object.entries(ShortcutGeneratorService.CATEGORY_MAP)) {
            const categoryShortcuts = shortcuts.filter(s => s.category === info.letter);
            const basePrefix = this.getBasePrefix();
            categories[category] = {
                prefix: `${basePrefix} ${info.letter}`,
                shortcuts: categoryShortcuts,
            };
        }

        return {
            categories,
            layouts: {
                [layout]: layoutConfig,
            },
            generatedAt: new Date().toISOString(),
            version: '1.0.0',
        };
    }

    /**
     * Assign shortcuts to workflows with conflict resolution
     */
    private assignShortcuts(workflows: Workflow[], layout: KeyboardLayoutConfig): ShortcutMapping[] {
        const mappings: ShortcutMapping[] = [];

        // Group workflows by category
        const categorized = this.groupByCategory(workflows);

        // Assign shortcuts for each category
        for (const [category, categoryWorkflows] of Object.entries(categorized)) {
            const categoryLetter = ShortcutGeneratorService.CATEGORY_MAP[category as keyof typeof ShortcutGeneratorService.CATEGORY_MAP].letter;
            const categoryName = ShortcutGeneratorService.CATEGORY_MAP[category as keyof typeof ShortcutGeneratorService.CATEGORY_MAP].name;

            // Track used keys in this category
            const usedKeys = new Set<string>();

            // Sort workflows alphabetically for consistency
            const sorted = [...categoryWorkflows].sort((a, b) => a.name.localeCompare(b.name));

            for (const workflow of sorted) {
                const key = this.findBestKey(workflow.name, layout, usedKeys);
                usedKeys.add(key);

                const basePrefix = this.getBasePrefix();
                const keybinding = `${basePrefix} ${categoryLetter} ${key}`;
                const mnemonic = `${categoryName[0]} ${key.toUpperCase()} = ${categoryName} ${this.capitalize(workflow.name)}`;
                const homeRow = layout.homeRow.includes(key);

                mappings.push({
                    workflowName: workflow.name,
                    category: categoryLetter,
                    key,
                    keybinding,
                    mnemonic,
                    homeRow,
                    layout: layout.layout,
                });
            }
        }

        return mappings;
    }

    /**
     * Find the best key for a workflow name
     */
    private findBestKey(name: string, layout: KeyboardLayoutConfig, usedKeys: Set<string>): string {
        // Try first letter
        const firstLetter = name[0].toLowerCase();
        if (!usedKeys.has(firstLetter)) {
            return firstLetter;
        }

        // Try first letter if it's on home row (prioritize ergonomics)
        if (layout.homeRow.includes(firstLetter) && !usedKeys.has(firstLetter)) {
            return firstLetter;
        }

        // Try second letter
        if (name.length > 1) {
            const secondLetter = name[1].toLowerCase();
            if (!usedKeys.has(secondLetter)) {
                return secondLetter;
            }
        }

        // Try all letters in the name
        for (const char of name.toLowerCase()) {
            if (/[a-z]/.test(char) && !usedKeys.has(char)) {
                return char;
            }
        }

        // Try home row keys (most ergonomic)
        for (const key of layout.homeRow) {
            if (!usedKeys.has(key)) {
                return key;
            }
        }

        // Try top row keys
        for (const key of layout.topRow) {
            if (!usedKeys.has(key)) {
                return key;
            }
        }

        // Try bottom row keys
        for (const key of layout.bottomRow) {
            if (!usedKeys.has(key)) {
                return key;
            }
        }

        // Fallback: use 'x' as a last resort
        return 'x';
    }

    /**
     * Group workflows by category
     */
    private groupByCategory(workflows: Workflow[]): Record<string, Workflow[]> {
        const grouped: Record<string, Workflow[]> = {
            quick: [],
            workflow: [],
            view: [],
            tool: [],
        };

        for (const workflow of workflows) {
            grouped[workflow.category].push(workflow);
        }

        return grouped;
    }

    /**
     * Get base keyboard prefix (platform-aware)
     */
    private getBasePrefix(): string {
        const isMac = process.platform === 'darwin';
        return isMac ? 'cmd+shift+e' : 'ctrl+shift+e';
    }

    /**
     * Capitalize first letter of string
     */
    private capitalize(str: string): string {
        return str.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join('-');
    }

    /**
     * Get shortcut for a specific workflow
     */
    getShortcutForWorkflow(workflows: Workflow[], workflowName: string, layout: KeyboardLayout = 'qwerty'): ShortcutMapping | undefined {
        const config = this.generateShortcuts(workflows, layout);
        for (const category of Object.values(config.categories)) {
            const shortcut = category.shortcuts.find(s => s.workflowName === workflowName);
            if (shortcut) {
                return shortcut;
            }
        }
        return undefined;
    }

    /**
     * Generate cheatsheet markdown
     */
    generateCheatsheet(workflows: Workflow[], layout: KeyboardLayout = 'qwerty'): string {
        const config = this.generateShortcuts(workflows, layout);
        let md = '# Empathy Framework Keyboard Shortcuts\n\n';
        md += `> Generated for ${layout.toUpperCase()} layout\n\n`;
        md += `**Base prefix:** ${this.getBasePrefix()}\n\n`;

        for (const [categoryName, categoryInfo] of Object.entries(config.categories)) {
            if (categoryInfo.shortcuts.length === 0) continue;

            md += `## ${this.capitalize(categoryName)} (${categoryInfo.prefix.split(' ').pop()?.toUpperCase()})\n\n`;
            md += '| Shortcut | Workflow | Mnemonic |\n';
            md += '|----------|----------|----------|\n';

            for (const shortcut of categoryInfo.shortcuts) {
                const key = shortcut.key.toUpperCase();
                const homeRowIndicator = shortcut.homeRow ? ' 🏠' : '';
                md += `| ${shortcut.keybinding} | ${shortcut.workflowName}${homeRowIndicator} | ${shortcut.mnemonic} |\n`;
            }

            md += '\n';
        }

        md += '---\n\n';
        md += '*🏠 = Home row key (most ergonomic)*\n\n';
        md += `*Generated by Empathy Framework at ${new Date().toLocaleString()}*\n`;

        return md;
    }
}
