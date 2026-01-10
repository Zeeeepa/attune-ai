/**
 * Coverage Panel - Dedicated webview for test coverage boost results
 *
 * Displays comprehensive coverage metrics including:
 * - Current vs. target coverage
 * - Coverage progress visualization
 * - Tests generated details
 * - Coverage improvement over time
 * - Quick action buttons
 *
 * Copyright 2025 Smart AI Memory, LLC
 * Licensed under Fair Source 0.9
 */

import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

interface CoverageData {
    current_coverage: number;
    target_coverage: number;
    coverage_improvement: number;
    tests_generated: number;
    gaps_identified: number;
    files_analyzed: number;
    timestamp: string;
    status: 'success' | 'in_progress' | 'failed';
    message?: string;
}

export class CoveragePanel {
    public static currentPanel: CoveragePanel | undefined;
    private readonly _panel: vscode.WebviewPanel;
    private readonly _extensionUri: vscode.Uri;
    private _disposables: vscode.Disposable[] = [];

    private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
        this._panel = panel;
        this._extensionUri = extensionUri;

        // Set the webview's initial html content
        this._update();

        // Listen for when the panel is disposed
        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);

        // Handle messages from the webview
        this._panel.webview.onDidReceiveMessage(
            async (message) => {
                switch (message.type) {
                    case 'refresh':
                        await this._updateData();
                        break;
                    case 'runBoost':
                        await this._runCoverageBoost(message.target);
                        break;
                    case 'openDashboard':
                        vscode.commands.executeCommand('empathy.dashboard');
                        break;
                }
            },
            null,
            this._disposables
        );

        // Auto-refresh data every 30 seconds
        const refreshInterval = setInterval(() => this._updateData(), 30000);
        this._disposables.push({ dispose: () => clearInterval(refreshInterval) });
    }

    public static createOrShow(extensionUri: vscode.Uri) {
        const column = vscode.ViewColumn.One;

        // If we already have a panel, show it
        if (CoveragePanel.currentPanel) {
            CoveragePanel.currentPanel._panel.reveal(column);
            return;
        }

        // Otherwise, create a new panel
        const panel = vscode.window.createWebviewPanel(
            'empathyCoveragePanel',
            'Test Coverage Boost',
            column,
            {
                enableScripts: true,
                retainContextWhenHidden: true,
                localResourceRoots: [
                    vscode.Uri.joinPath(extensionUri, 'webview'),
                ],
            }
        );

        CoveragePanel.currentPanel = new CoveragePanel(panel, extensionUri);
    }

    public dispose() {
        CoveragePanel.currentPanel = undefined;

        // Clean up resources
        this._panel.dispose();

        while (this._disposables.length) {
            const x = this._disposables.pop();
            if (x) {
                x.dispose();
            }
        }
    }

    private async _runCoverageBoost(target: number) {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspaceFolder) {
            vscode.window.showErrorMessage('No workspace folder open');
            return;
        }

        // Show in-progress state
        this._panel.webview.postMessage({
            type: 'coverageData',
            data: {
                status: 'in_progress',
                target_coverage: target,
                message: 'Running test coverage boost...'
            }
        });

        // Get configured python path
        const config = vscode.workspace.getConfiguration('empathy');
        const pythonPath = config.get<string>('pythonPath', 'python');

        // Run orchestrated test coverage command
        const cp = require('child_process');
        const args = ['-m', 'empathy_os.cli', 'orchestrate', 'test-coverage', '--target', target.toString()];

        cp.execFile(pythonPath, args, { cwd: workspaceFolder, maxBuffer: 1024 * 1024 * 5 }, async (error: any, stdout: string, stderr: string) => {
            if (error) {
                this._panel.webview.postMessage({
                    type: 'coverageData',
                    data: {
                        status: 'failed',
                        message: `Coverage boost failed: ${error.message}`
                    }
                });
                return;
            }

            // Refresh data to show results
            await this._updateData();
        });
    }

    private async _updateData() {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspaceFolder) {
            return;
        }

        // Load coverage data from .empathy/coverage.json
        const coverageFile = path.join(workspaceFolder, '.empathy', 'coverage.json');

        try {
            if (fs.existsSync(coverageFile)) {
                const data = JSON.parse(fs.readFileSync(coverageFile, 'utf-8'));

                // Send to webview
                this._panel.webview.postMessage({
                    type: 'coverageData',
                    data: data
                });
            } else {
                // No data yet - show initial state
                this._panel.webview.postMessage({
                    type: 'coverageData',
                    data: {
                        status: 'success',
                        current_coverage: 0,
                        target_coverage: 80,
                        coverage_improvement: 0,
                        tests_generated: 0,
                        gaps_identified: 0,
                        files_analyzed: 0,
                        timestamp: new Date().toISOString()
                    }
                });
            }
        } catch (error) {
            console.error('Error loading coverage data:', error);
        }
    }

    private _update() {
        const webview = this._panel.webview;
        this._panel.title = 'Test Coverage Boost';
        this._panel.webview.html = this._getHtmlForWebview(webview);
        this._updateData();
    }

    private _getHtmlForWebview(webview: vscode.Webview): string {
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Coverage Boost</title>
    <style>
        body {
            font-family: var(--vscode-font-family);
            color: var(--vscode-foreground);
            background-color: var(--vscode-editor-background);
            padding: 20px;
            margin: 0;
        }

        .header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 2px solid var(--vscode-panel-border);
        }

        .header h1 {
            margin: 0;
            font-size: 24px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .badge {
            background: linear-gradient(90deg, #8b5cf6, #ec4899);
            color: white;
            font-size: 10px;
            padding: 3px 8px;
            border-radius: 8px;
            font-weight: 700;
        }

        .coverage-circle {
            width: 200px;
            height: 200px;
            margin: 0 auto 30px;
            position: relative;
        }

        .coverage-number {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
        }

        .coverage-percent {
            font-size: 48px;
            font-weight: bold;
        }

        .coverage-label {
            font-size: 14px;
            opacity: 0.7;
        }

        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }

        .metric-card {
            background: var(--vscode-editor-background);
            border: 1px solid var(--vscode-panel-border);
            border-radius: 8px;
            padding: 15px;
        }

        .metric-value {
            font-size: 32px;
            font-weight: bold;
            color: var(--vscode-textLink-foreground);
        }

        .metric-label {
            font-size: 12px;
            opacity: 0.7;
            margin-top: 5px;
        }

        .progress-bar {
            width: 100%;
            height: 30px;
            background: var(--vscode-editor-background);
            border: 1px solid var(--vscode-panel-border);
            border-radius: 15px;
            overflow: hidden;
            margin: 20px 0;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #10b981, #3b82f6);
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 10px;
            color: white;
            font-weight: bold;
        }

        .actions {
            display: flex;
            gap: 10px;
            margin-top: 30px;
        }

        button {
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }

        button:hover {
            background: var(--vscode-button-hoverBackground);
        }

        .secondary-btn {
            background: var(--vscode-button-secondaryBackground);
            color: var(--vscode-button-secondaryForeground);
        }

        .secondary-btn:hover {
            background: var(--vscode-button-secondaryHoverBackground);
        }

        .status-message {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: none;
        }

        .status-success {
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid #10b981;
            color: #10b981;
        }

        .status-progress {
            background: rgba(59, 130, 246, 0.1);
            border: 1px solid #3b82f6;
            color: #3b82f6;
        }

        .status-error {
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid #ef4444;
            color: #ef4444;
        }

        .timestamp {
            text-align: center;
            font-size: 12px;
            opacity: 0.5;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>
            🎯 Test Coverage Boost
            <span class="badge">v4.0</span>
        </h1>
        <button onclick="refresh()" class="secondary-btn">↻ Refresh</button>
    </div>

    <div id="status-message" class="status-message"></div>

    <div class="coverage-circle">
        <svg width="200" height="200" viewBox="0 0 200 200">
            <circle cx="100" cy="100" r="90" fill="none" stroke="var(--vscode-panel-border)" stroke-width="15"/>
            <circle id="coverage-progress" cx="100" cy="100" r="90" fill="none"
                    stroke="url(#gradient)" stroke-width="15"
                    stroke-linecap="round"
                    stroke-dasharray="565.48"
                    stroke-dashoffset="565.48"
                    transform="rotate(-90 100 100)"/>
            <defs>
                <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" style="stop-color:#10b981;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#3b82f6;stop-opacity:1" />
                </linearGradient>
            </defs>
        </svg>
        <div class="coverage-number">
            <div class="coverage-percent" id="coverage-percent">0%</div>
            <div class="coverage-label">Current Coverage</div>
        </div>
    </div>

    <div class="progress-bar">
        <div class="progress-fill" id="progress-fill" style="width: 0%;">
            <span id="progress-text"></span>
        </div>
    </div>

    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-value" id="tests-generated">0</div>
            <div class="metric-label">Tests Generated</div>
        </div>
        <div class="metric-card">
            <div class="metric-value" id="gaps-identified">0</div>
            <div class="metric-label">Gaps Identified</div>
        </div>
        <div class="metric-card">
            <div class="metric-value" id="improvement">+0%</div>
            <div class="metric-label">Coverage Improvement</div>
        </div>
        <div class="metric-card">
            <div class="metric-value" id="files-analyzed">0</div>
            <div class="metric-label">Files Analyzed</div>
        </div>
    </div>

    <div class="actions">
        <button onclick="runBoost()">🚀 Run Coverage Boost</button>
        <button onclick="openDashboard()" class="secondary-btn">← Back to Dashboard</button>
    </div>

    <div class="timestamp" id="timestamp"></div>

    <script>
        const vscode = acquireVsCodeApi();

        function refresh() {
            vscode.postMessage({ type: 'refresh' });
        }

        function runBoost() {
            // Prompt for target coverage
            const target = prompt('Target coverage percentage:', '80');
            if (target) {
                vscode.postMessage({ type: 'runBoost', target: parseInt(target) });
            }
        }

        function openDashboard() {
            vscode.postMessage({ type: 'openDashboard' });
        }

        function updateUI(data) {
            const statusMessage = document.getElementById('status-message');

            // Update status message
            if (data.status === 'in_progress') {
                statusMessage.className = 'status-message status-progress';
                statusMessage.textContent = data.message || 'Running coverage boost...';
                statusMessage.style.display = 'block';
            } else if (data.status === 'failed') {
                statusMessage.className = 'status-message status-error';
                statusMessage.textContent = data.message || 'Coverage boost failed';
                statusMessage.style.display = 'block';
            } else if (data.status === 'success' && data.coverage_improvement > 0) {
                statusMessage.className = 'status-message status-success';
                statusMessage.textContent = \`✅ Coverage boosted by \${data.coverage_improvement.toFixed(1)}%!\`;
                statusMessage.style.display = 'block';
            } else {
                statusMessage.style.display = 'none';
            }

            // Update coverage circle
            const coverage = data.current_coverage || 0;
            const coveragePercent = document.getElementById('coverage-percent');
            coveragePercent.textContent = \`\${coverage.toFixed(1)}%\`;

            // Animate coverage circle
            const circle = document.getElementById('coverage-progress');
            const circumference = 565.48;
            const offset = circumference - (coverage / 100) * circumference;
            circle.style.strokeDashoffset = offset.toString();

            // Update progress bar
            const progressFill = document.getElementById('progress-fill');
            const progressText = document.getElementById('progress-text');
            const target = data.target_coverage || 80;
            const progress = Math.min((coverage / target) * 100, 100);
            progressFill.style.width = \`\${progress}%\`;
            progressText.textContent = \`\${coverage.toFixed(1)}% / \${target}%\`;

            // Update metrics
            document.getElementById('tests-generated').textContent = data.tests_generated || 0;
            document.getElementById('gaps-identified').textContent = data.gaps_identified || 0;
            document.getElementById('improvement').textContent = \`+\${(data.coverage_improvement || 0).toFixed(1)}%\`;
            document.getElementById('files-analyzed').textContent = data.files_analyzed || 0;

            // Update timestamp
            if (data.timestamp) {
                const date = new Date(data.timestamp);
                document.getElementById('timestamp').textContent =
                    \`Last updated: \${date.toLocaleString()}\`;
            }
        }

        // Listen for messages from extension
        window.addEventListener('message', event => {
            const message = event.data;
            switch (message.type) {
                case 'coverageData':
                    updateUI(message.data);
                    break;
            }
        });
    </script>
</body>
</html>`;
    }
}
