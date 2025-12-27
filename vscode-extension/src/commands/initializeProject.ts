/**
 * Initialize Project Command
 *
 * Entry point for the Empathy Framework onboarding wizard.
 * Checks if project is already initialized and launches the wizard.
 *
 * Copyright 2025 Smart AI Memory, LLC
 * Licensed under Fair Source 0.9
 */

import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import { InitializeWizardPanel } from '../panels/InitializeWizardPanel';

/**
 * Check if the current workspace has been initialized
 */
export function isProjectInitialized(context: vscode.ExtensionContext): boolean {
    // Check global state
    const initialized = context.globalState.get<boolean>('empathy.initialized');
    if (initialized) {
        return true;
    }

    // Check for config file in workspace
    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (workspaceFolders && workspaceFolders.length > 0) {
        const configPath = path.join(workspaceFolders[0].uri.fsPath, 'empathy.config.yml');
        if (fs.existsSync(configPath)) {
            return true;
        }
    }

    return false;
}

/**
 * Initialize Project command handler
 */
export async function initializeProject(context: vscode.ExtensionContext, options?: { force?: boolean }): Promise<void> {
    console.log('[Empathy] initializeProject called', options);

    // Check if already initialized (unless force=true)
    if (!options?.force && isProjectInitialized(context)) {
        console.log('[Empathy] Project is initialized, showing reinitialize prompt');
        const action = await vscode.window.showWarningMessage(
            'Empathy Framework is already initialized for this workspace. Would you like to reinitialize?',
            'Reinitialize',
            'Cancel'
        );

        if (action !== 'Reinitialize') {
            return;
        }

        // Reset initialization state
        await context.globalState.update('empathy.initialized', false);
    }

    // Check for workspace
    if (!vscode.workspace.workspaceFolders || vscode.workspace.workspaceFolders.length === 0) {
        const action = await vscode.window.showErrorMessage(
            'Please open a folder or workspace before initializing Empathy Framework.',
            'Open Folder'
        );

        if (action === 'Open Folder') {
            await vscode.commands.executeCommand('vscode.openFolder');
        }
        return;
    }

    // Launch the wizard
    console.log('[Empathy] Launching wizard panel');
    try {
        InitializeWizardPanel.createOrShow(context);
        console.log('[Empathy] Wizard panel created');
    } catch (err) {
        console.error('[Empathy] Error creating wizard panel:', err);
        vscode.window.showErrorMessage(`Failed to open wizard: ${err}`);
    }
}

/**
 * Show welcome message for first-time users
 */
export async function showWelcomeIfNeeded(context: vscode.ExtensionContext): Promise<void> {
    const hasSeenWelcome = context.globalState.get<boolean>('empathy.hasSeenWelcome');

    if (!hasSeenWelcome && !isProjectInitialized(context)) {
        const action = await vscode.window.showInformationMessage(
            'Welcome to Empathy Framework! Would you like to set up your project now?',
            'Initialize',
            'Later',
            "Don't Show Again"
        );

        if (action === 'Initialize') {
            await initializeProject(context);
        } else if (action === "Don't Show Again") {
            await context.globalState.update('empathy.hasSeenWelcome', true);
        }
    }
}

/**
 * Check for existing API keys in secrets
 */
export async function hasStoredApiKeys(context: vscode.ExtensionContext): Promise<{
    anthropic: boolean;
    openai: boolean;
}> {
    const anthropicKey = await context.secrets.get('empathy.anthropic.apiKey');
    const openaiKey = await context.secrets.get('empathy.openai.apiKey');

    return {
        anthropic: !!anthropicKey,
        openai: !!openaiKey
    };
}

/**
 * Get the stored API key for a provider
 */
export async function getApiKey(
    context: vscode.ExtensionContext,
    provider: 'anthropic' | 'openai'
): Promise<string | undefined> {
    return context.secrets.get(`empathy.${provider}.apiKey`);
}

/**
 * Store an API key for a provider
 */
export async function storeApiKey(
    context: vscode.ExtensionContext,
    provider: 'anthropic' | 'openai',
    key: string
): Promise<void> {
    await context.secrets.store(`empathy.${provider}.apiKey`, key);
}

/**
 * Delete stored API key for a provider
 */
export async function deleteApiKey(
    context: vscode.ExtensionContext,
    provider: 'anthropic' | 'openai'
): Promise<void> {
    await context.secrets.delete(`empathy.${provider}.apiKey`);
}
