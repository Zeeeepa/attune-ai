/**
 * Test Tracking Panel - Native webview for test status
 *
 * Displays test tracking data by reading directly from .empathy/file_tests.jsonl
 * No server required - pure file-based data access.
 *
 * Copyright 2026 Smart AI Memory, LLC
 * Licensed under Fair Source 0.9
 */

import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

interface FileTestRecord {
    file_path: string;
    test_count: number;
    passed: number;
    failed: number;
    skipped: number;
    duration_seconds: number;
    last_test_result: 'passed' | 'failed' | 'no_tests' | 'error';
    timestamp: string;
    coverage_percentage?: number;
}

interface TestSummary {
    totalFiles: number;
    passingFiles: number;
    failingFiles: number;
    noTestFiles: number;
    totalTests: number;
    totalPassed: number;
    totalFailed: number;
    avgCoverage: number;
    lastUpdated: string | null;
    files: FileTestRecord[];
}

export class TestTrackingPanel {
    public static currentPanel: TestTrackingPanel | undefined;
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
                        await this._update();
                        vscode.window.showInformationMessage('Test tracking data refreshed');
                        break;
                    case 'openFile':
                        if (message.filePath) {
                            const doc = await vscode.workspace.openTextDocument(message.filePath);
                            await vscode.window.showTextDocument(doc);
                        }
                        break;
                    case 'runTests':
                        vscode.commands.executeCommand('empathy.runTests');
                        break;
                }
            },
            null,
            this._disposables
        );

        // Auto-refresh data every 60 seconds
        const refreshInterval = setInterval(() => this._update(), 60000);
        this._disposables.push({ dispose: () => clearInterval(refreshInterval) });
    }

    public static createOrShow(extensionUri: vscode.Uri) {
        const column = vscode.ViewColumn.One;

        // If we already have a panel, show it
        if (TestTrackingPanel.currentPanel) {
            TestTrackingPanel.currentPanel._panel.reveal(column);
            TestTrackingPanel.currentPanel._update();
            return;
        }

        // Otherwise, create a new panel
        const panel = vscode.window.createWebviewPanel(
            'empathyTestTracking',
            'Test Tracking',
            column,
            {
                enableScripts: true,
                retainContextWhenHidden: true,
            }
        );

        TestTrackingPanel.currentPanel = new TestTrackingPanel(panel, extensionUri);
    }

    public dispose() {
        TestTrackingPanel.currentPanel = undefined;
        this._panel.dispose();

        while (this._disposables.length) {
            const x = this._disposables.pop();
            if (x) {
                x.dispose();
            }
        }
    }

    private async _update() {
        const summary = await this._getTestSummary();
        this._panel.webview.html = this._getHtml(summary);
    }

    private async _getTestSummary(): Promise<TestSummary> {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;

        const defaultSummary: TestSummary = {
            totalFiles: 0,
            passingFiles: 0,
            failingFiles: 0,
            noTestFiles: 0,
            totalTests: 0,
            totalPassed: 0,
            totalFailed: 0,
            avgCoverage: 0,
            lastUpdated: null,
            files: []
        };

        if (!workspaceFolder) {
            return defaultSummary;
        }

        const config = vscode.workspace.getConfiguration('empathy');
        const empathyDir = path.join(workspaceFolder, config.get<string>('empathyDir', '.empathy'));
        const fileTestsPath = path.join(empathyDir, 'file_tests.jsonl');

        if (!fs.existsSync(fileTestsPath)) {
            return defaultSummary;
        }

        try {
            const content = fs.readFileSync(fileTestsPath, 'utf8');
            const lines = content.trim().split('\n').filter(line => line.trim());

            // Get latest record per file (last line wins)
            const latestByFile = new Map<string, FileTestRecord>();
            let lastTimestamp: string | null = null;

            for (const line of lines) {
                try {
                    const record: FileTestRecord = JSON.parse(line);
                    latestByFile.set(record.file_path, record);
                    lastTimestamp = record.timestamp;
                } catch {
                    // Skip invalid lines
                }
            }

            const files = Array.from(latestByFile.values());

            let passingFiles = 0;
            let failingFiles = 0;
            let noTestFiles = 0;
            let totalTests = 0;
            let totalPassed = 0;
            let totalFailed = 0;
            let coverageSum = 0;
            let coverageCount = 0;

            for (const file of files) {
                if (file.last_test_result === 'passed') {
                    passingFiles++;
                } else if (file.last_test_result === 'failed') {
                    failingFiles++;
                } else if (file.last_test_result === 'no_tests') {
                    noTestFiles++;
                }

                totalTests += file.test_count || 0;
                totalPassed += file.passed || 0;
                totalFailed += file.failed || 0;

                if (file.coverage_percentage !== undefined) {
                    coverageSum += file.coverage_percentage;
                    coverageCount++;
                }
            }

            // Sort files: failed first, then by name
            files.sort((a, b) => {
                if (a.last_test_result === 'failed' && b.last_test_result !== 'failed') return -1;
                if (a.last_test_result !== 'failed' && b.last_test_result === 'failed') return 1;
                return a.file_path.localeCompare(b.file_path);
            });

            return {
                totalFiles: files.length,
                passingFiles,
                failingFiles,
                noTestFiles,
                totalTests,
                totalPassed,
                totalFailed,
                avgCoverage: coverageCount > 0 ? Math.round(coverageSum / coverageCount) : 0,
                lastUpdated: lastTimestamp ? new Date(lastTimestamp).toLocaleString() : null,
                files: files.slice(0, 100) // Limit to 100 files for performance
            };
        } catch (error) {
            console.error('Failed to read test tracking data:', error);
            return defaultSummary;
        }
    }

    private _getHtml(summary: TestSummary): string {
        const passRate = summary.totalFiles > 0
            ? Math.round((summary.passingFiles / summary.totalFiles) * 100)
            : 0;

        const statusColor = summary.failingFiles === 0
            ? 'var(--vscode-testing-iconPassed)'
            : 'var(--vscode-testing-iconFailed)';

        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Tracking</title>
    <style>
        body {
            font-family: var(--vscode-font-family);
            background: var(--vscode-editor-background);
            color: var(--vscode-editor-foreground);
            margin: 0;
            padding: 20px;
            line-height: 1.5;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--vscode-input-border);
        }
        h1 {
            margin: 0;
            font-size: 24px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .actions {
            display: flex;
            gap: 8px;
        }
        .btn {
            background: var(--vscode-button-secondaryBackground);
            color: var(--vscode-button-secondaryForeground);
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
        }
        .btn:hover {
            background: var(--vscode-button-secondaryHoverBackground);
        }
        .btn-primary {
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
        }
        .btn-primary:hover {
            background: var(--vscode-button-hoverBackground);
        }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }
        .summary-card {
            background: var(--vscode-input-background);
            border: 1px solid var(--vscode-input-border);
            border-radius: 8px;
            padding: 16px;
            text-align: center;
        }
        .summary-value {
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 4px;
        }
        .summary-label {
            font-size: 12px;
            color: var(--vscode-descriptionForeground);
            text-transform: uppercase;
        }
        .pass-rate {
            color: ${statusColor};
        }
        .passing { color: var(--vscode-testing-iconPassed); }
        .failing { color: var(--vscode-testing-iconFailed); }
        .no-tests { color: var(--vscode-descriptionForeground); }

        .file-list {
            margin-top: 24px;
        }
        .file-list h2 {
            font-size: 16px;
            margin-bottom: 12px;
        }
        .file-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }
        .file-table th {
            text-align: left;
            padding: 8px 12px;
            background: var(--vscode-input-background);
            border-bottom: 1px solid var(--vscode-input-border);
            font-weight: 600;
        }
        .file-table td {
            padding: 8px 12px;
            border-bottom: 1px solid var(--vscode-input-border);
        }
        .file-table tr:hover {
            background: var(--vscode-list-hoverBackground);
        }
        .file-link {
            color: var(--vscode-textLink-foreground);
            cursor: pointer;
            text-decoration: none;
        }
        .file-link:hover {
            text-decoration: underline;
        }
        .status-badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 500;
        }
        .status-passed {
            background: rgba(115, 201, 145, 0.2);
            color: var(--vscode-testing-iconPassed);
        }
        .status-failed {
            background: rgba(241, 76, 76, 0.2);
            color: var(--vscode-testing-iconFailed);
        }
        .status-no-tests {
            background: rgba(128, 128, 128, 0.2);
            color: var(--vscode-descriptionForeground);
        }
        .last-updated {
            font-size: 12px;
            color: var(--vscode-descriptionForeground);
            margin-top: 16px;
        }
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: var(--vscode-descriptionForeground);
        }
        .empty-state h2 {
            margin-bottom: 8px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>
            <span style="font-size: 28px;">🧪</span>
            Test Tracking
        </h1>
        <div class="actions">
            <button class="btn" onclick="refresh()">🔄 Refresh</button>
            <button class="btn btn-primary" onclick="runTests()">▶ Run Tests</button>
        </div>
    </div>

    ${summary.totalFiles === 0 ? `
    <div class="empty-state">
        <h2>No Test Data Found</h2>
        <p>Run tests to start tracking. Data is stored in .empathy/file_tests.jsonl</p>
        <button class="btn btn-primary" onclick="runTests()" style="margin-top: 16px;">Run Tests Now</button>
    </div>
    ` : `
    <div class="summary-grid">
        <div class="summary-card">
            <div class="summary-value pass-rate">${passRate}%</div>
            <div class="summary-label">Pass Rate</div>
        </div>
        <div class="summary-card">
            <div class="summary-value passing">${summary.passingFiles}</div>
            <div class="summary-label">Passing Files</div>
        </div>
        <div class="summary-card">
            <div class="summary-value failing">${summary.failingFiles}</div>
            <div class="summary-label">Failing Files</div>
        </div>
        <div class="summary-card">
            <div class="summary-value">${summary.totalTests}</div>
            <div class="summary-label">Total Tests</div>
        </div>
        <div class="summary-card">
            <div class="summary-value">${summary.avgCoverage}%</div>
            <div class="summary-label">Avg Coverage</div>
        </div>
    </div>

    <div class="file-list">
        <h2>File Status (${summary.files.length} files)</h2>
        <table class="file-table">
            <thead>
                <tr>
                    <th>File</th>
                    <th>Status</th>
                    <th>Tests</th>
                    <th>Passed</th>
                    <th>Failed</th>
                </tr>
            </thead>
            <tbody>
                ${summary.files.map(file => `
                <tr>
                    <td>
                        <span class="file-link" onclick="openFile('${this._escapeJs(file.file_path)}')">
                            ${this._shortenPath(file.file_path)}
                        </span>
                    </td>
                    <td>
                        <span class="status-badge status-${file.last_test_result === 'passed' ? 'passed' : file.last_test_result === 'failed' ? 'failed' : 'no-tests'}">
                            ${file.last_test_result === 'passed' ? '✓ Passed' : file.last_test_result === 'failed' ? '✗ Failed' : '○ No Tests'}
                        </span>
                    </td>
                    <td>${file.test_count || 0}</td>
                    <td class="passing">${file.passed || 0}</td>
                    <td class="failing">${file.failed || 0}</td>
                </tr>
                `).join('')}
            </tbody>
        </table>
    </div>

    ${summary.lastUpdated ? `<div class="last-updated">Last updated: ${summary.lastUpdated}</div>` : ''}
    `}

    <script>
        const vscode = acquireVsCodeApi();

        function refresh() {
            vscode.postMessage({ type: 'refresh' });
        }

        function runTests() {
            vscode.postMessage({ type: 'runTests' });
        }

        function openFile(filePath) {
            vscode.postMessage({ type: 'openFile', filePath: filePath });
        }
    </script>
</body>
</html>`;
    }

    private _shortenPath(filePath: string): string {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (workspaceFolder && filePath.startsWith(workspaceFolder)) {
            return filePath.substring(workspaceFolder.length + 1);
        }
        // Show last 3 parts of path
        const parts = filePath.split(path.sep);
        if (parts.length > 3) {
            return '...' + path.sep + parts.slice(-3).join(path.sep);
        }
        return filePath;
    }

    private _escapeJs(str: string): string {
        return str.replace(/\\/g, '\\\\').replace(/'/g, "\\'");
    }
}
