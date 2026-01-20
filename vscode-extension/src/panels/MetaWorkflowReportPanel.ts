/**
 * Meta-Workflow Report Panel - Rich HTML webview for meta-workflow execution results
 *
 * Displays dynamic reports for meta-workflow executions including:
 * - Execution summary (status, cost, duration, agents)
 * - Form responses used during execution
 * - Individual agent execution results with success/failure status
 * - Cost breakdown by tier
 * - Raw JSON output
 *
 * Features:
 * - Collapsible sections for organized viewing
 * - Agent cards with tier badges and status indicators
 * - Copy, Export, Refresh functionality
 * - VSCode theme integration
 *
 * Copyright 2025 Smart AI Memory, LLC
 * Licensed under Fair Source 0.9
 */

import * as vscode from 'vscode';
import * as cp from 'child_process';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

interface AgentExecutionResult {
    agent_id: string;
    role: string;
    success: boolean;
    cost: number;
    duration: number;
    tier_used: string;
    output: any;
    error?: string;
}

interface MetaWorkflowReport {
    run_id: string;
    template_id: string;
    timestamp: string;
    success: boolean;
    error?: string;
    total_cost: number;
    total_duration: number;
    form_responses?: {
        template_id: string;
        responses: Record<string, any>;
        timestamp: string;
        response_id: string;
    };
    agents_created: number;
    agent_results: AgentExecutionResult[];
    status?: 'running' | 'success' | 'failed';
}

export class MetaWorkflowReportPanel {
    public static currentPanel: MetaWorkflowReportPanel | undefined;
    private readonly _panel: vscode.WebviewPanel;
    private readonly _extensionUri: vscode.Uri;
    private _disposables: vscode.Disposable[] = [];
    private _currentRunId: string = '';
    private _currentReport: MetaWorkflowReport | null = null;
    private _currentTemplateId: string = '';

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
                        await this._rerunWorkflow();
                        break;
                    case 'copyReport':
                        await this._copyReport();
                        break;
                    case 'exportJson':
                        await this._exportJson();
                        break;
                    case 'viewRawOutput':
                        await this._viewRawOutput();
                        break;
                    case 'openDashboard':
                        vscode.commands.executeCommand('empathy.dashboard');
                        break;
                    case 'toggleSection':
                        // Handled in webview JavaScript
                        break;
                }
            },
            null,
            this._disposables
        );
    }

    /**
     * Create or show the panel
     */
    public static createOrShow(extensionUri: vscode.Uri, runId?: string) {
        const column = vscode.ViewColumn.One;

        // If we already have a panel, show it
        if (MetaWorkflowReportPanel.currentPanel) {
            MetaWorkflowReportPanel.currentPanel._panel.reveal(column);
            if (runId) {
                MetaWorkflowReportPanel.currentPanel._loadResults(runId);
            }
            return;
        }

        // Otherwise, create a new panel
        const panel = vscode.window.createWebviewPanel(
            'empathyMetaWorkflowReport',
            'Meta-Workflow Report',
            column,
            {
                enableScripts: true,
                retainContextWhenHidden: true,
                localResourceRoots: [
                    vscode.Uri.joinPath(extensionUri, 'webview'),
                ],
            }
        );

        MetaWorkflowReportPanel.currentPanel = new MetaWorkflowReportPanel(panel, extensionUri);

        // If runId provided, load that run's results
        if (runId) {
            MetaWorkflowReportPanel.currentPanel._loadResults(runId);
        }
    }

    /**
     * Show the panel after a workflow execution completes
     */
    public static showAfterExecution(
        extensionUri: vscode.Uri,
        result: MetaWorkflowReport,
        templateId: string
    ) {
        MetaWorkflowReportPanel.createOrShow(extensionUri);

        if (MetaWorkflowReportPanel.currentPanel) {
            MetaWorkflowReportPanel.currentPanel._currentTemplateId = templateId;
            MetaWorkflowReportPanel.currentPanel._currentRunId = result.run_id;
            MetaWorkflowReportPanel.currentPanel._updateReport({
                ...result,
                status: result.success ? 'success' : 'failed'
            });
        }
    }

    /**
     * Show running state while workflow executes
     */
    public static showRunning(extensionUri: vscode.Uri, templateId: string) {
        MetaWorkflowReportPanel.createOrShow(extensionUri);

        if (MetaWorkflowReportPanel.currentPanel) {
            MetaWorkflowReportPanel.currentPanel._currentTemplateId = templateId;
            MetaWorkflowReportPanel.currentPanel._panel.title = `Meta-Workflow: ${templateId}`;
            MetaWorkflowReportPanel.currentPanel._updateReport({
                run_id: '',
                template_id: templateId,
                timestamp: new Date().toISOString(),
                success: false,
                total_cost: 0,
                total_duration: 0,
                agents_created: 0,
                agent_results: [],
                status: 'running'
            });
        }
    }

    public dispose() {
        MetaWorkflowReportPanel.currentPanel = undefined;

        // Clean up resources
        this._panel.dispose();

        while (this._disposables.length) {
            const x = this._disposables.pop();
            if (x) {
                x.dispose();
            }
        }
    }

    /**
     * Load results from the file system
     */
    private async _loadResults(runId: string) {
        this._currentRunId = runId;

        const empathyDir = path.join(os.homedir(), '.empathy', 'meta_workflows', 'executions', runId);
        const resultFile = path.join(empathyDir, 'result.json');

        if (fs.existsSync(resultFile)) {
            try {
                const content = fs.readFileSync(resultFile, 'utf-8');
                const result = JSON.parse(content);
                this._currentTemplateId = result.template_id || runId.split('-')[0];
                this._updateReport({
                    ...result,
                    status: result.success ? 'success' : 'failed'
                });
            } catch (e) {
                vscode.window.showErrorMessage(`Failed to load results: ${e}`);
            }
        } else {
            vscode.window.showErrorMessage(`Results not found for run: ${runId}`);
        }
    }

    /**
     * Re-run the current workflow
     */
    private async _rerunWorkflow() {
        if (!this._currentTemplateId) {
            vscode.window.showWarningMessage('No workflow to re-run');
            return;
        }

        // Trigger the run command
        vscode.commands.executeCommand('empathy.metaWorkflow.runWithReport', this._currentTemplateId);
    }

    private _updateReport(report: MetaWorkflowReport) {
        this._currentReport = report;
        this._panel.title = `Meta-Workflow: ${report.template_id || 'Report'}`;
        this._panel.webview.postMessage({
            type: 'reportUpdate',
            data: report
        });
    }

    private async _copyReport() {
        if (!this._currentReport) {
            return;
        }

        const text = JSON.stringify(this._currentReport, null, 2);
        await vscode.env.clipboard.writeText(text);
        vscode.window.showInformationMessage('Report copied to clipboard');
    }

    private async _exportJson() {
        if (!this._currentReport) {
            return;
        }

        const uri = await vscode.window.showSaveDialog({
            filters: { 'JSON': ['json'] },
            defaultUri: vscode.Uri.file(`meta-workflow-${this._currentReport.run_id || 'report'}.json`)
        });

        if (uri) {
            fs.writeFileSync(uri.fsPath, JSON.stringify(this._currentReport, null, 2));
            vscode.window.showInformationMessage(`Report exported to ${uri.fsPath}`);
        }
    }

    private async _viewRawOutput() {
        if (!this._currentReport) {
            return;
        }

        const doc = await vscode.workspace.openTextDocument({
            content: JSON.stringify(this._currentReport, null, 2),
            language: 'json'
        });
        await vscode.window.showTextDocument(doc);
    }

    private _update() {
        this._panel.webview.html = this._getHtmlForWebview();
    }

    private _getHtmlForWebview(): string {
        const nonce = getNonce();

        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'nonce-${nonce}';">
    <title>Meta-Workflow Report</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: var(--vscode-font-family);
            color: var(--vscode-foreground);
            background: var(--vscode-editor-background);
            padding: 20px;
            line-height: 1.6;
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--vscode-panel-border);
        }

        .header-left {
            display: flex;
            flex-direction: column;
            gap: 4px;
        }

        .title {
            font-size: 24px;
            font-weight: 600;
        }

        .run-id {
            font-size: 12px;
            color: var(--vscode-descriptionForeground);
            font-family: monospace;
        }

        .actions {
            display: flex;
            gap: 8px;
        }

        button {
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
            transition: background 0.2s;
        }

        button:hover {
            background: var(--vscode-button-hoverBackground);
        }

        button.secondary {
            background: var(--vscode-button-secondaryBackground);
            color: var(--vscode-button-secondaryForeground);
        }

        .status-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            margin-left: 12px;
        }

        .status-running { background: #ffa500; color: white; }
        .status-success { background: #28a745; color: white; }
        .status-failed { background: #dc3545; color: white; }

        .loading {
            text-align: center;
            padding: 60px;
            color: var(--vscode-descriptionForeground);
        }

        .spinner {
            display: inline-block;
            width: 48px;
            height: 48px;
            border: 4px solid var(--vscode-panel-border);
            border-top-color: var(--vscode-button-background);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }

        .metric-card {
            background: var(--vscode-editor-background);
            border: 1px solid var(--vscode-panel-border);
            border-radius: 8px;
            padding: 16px;
            text-align: center;
        }

        .metric-value {
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 4px;
        }

        .metric-label {
            font-size: 12px;
            color: var(--vscode-descriptionForeground);
            text-transform: uppercase;
        }

        .metric-value.success { color: #28a745; }
        .metric-value.warning { color: #ffa500; }
        .metric-value.error { color: #dc3545; }
        .metric-value.info { color: var(--vscode-textLink-foreground); }

        .section {
            margin-bottom: 20px;
            background: var(--vscode-editor-background);
            border: 1px solid var(--vscode-panel-border);
            border-radius: 8px;
            overflow: hidden;
        }

        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 16px;
            background: var(--vscode-sideBar-background);
            cursor: pointer;
            user-select: none;
        }

        .section-header:hover {
            background: var(--vscode-list-hoverBackground);
        }

        .section-title {
            font-size: 14px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .section-arrow {
            transition: transform 0.2s;
        }

        .section-arrow.collapsed {
            transform: rotate(-90deg);
        }

        .section-content {
            padding: 16px;
            border-top: 1px solid var(--vscode-panel-border);
        }

        .section-content.collapsed {
            display: none;
        }

        .agent-card {
            background: var(--vscode-editor-background);
            border: 1px solid var(--vscode-panel-border);
            border-radius: 6px;
            margin-bottom: 12px;
            overflow: hidden;
        }

        .agent-card:last-child {
            margin-bottom: 0;
        }

        .agent-header {
            display: flex;
            align-items: center;
            padding: 12px 16px;
            gap: 12px;
        }

        .agent-status {
            font-size: 18px;
        }

        .agent-role {
            font-weight: 600;
            flex: 1;
        }

        .tier-badge {
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
        }

        .tier-cheap { background: #28a745; color: white; }
        .tier-capable { background: #007bff; color: white; }
        .tier-premium { background: #6f42c1; color: white; }

        .agent-metrics {
            display: flex;
            gap: 16px;
            font-size: 12px;
            color: var(--vscode-descriptionForeground);
        }

        .agent-details {
            padding: 12px 16px;
            border-top: 1px solid var(--vscode-panel-border);
            background: var(--vscode-textCodeBlock-background);
        }

        .agent-details.collapsed {
            display: none;
        }

        .response-item {
            display: flex;
            padding: 8px 0;
            border-bottom: 1px solid var(--vscode-panel-border);
        }

        .response-item:last-child {
            border-bottom: none;
        }

        .response-key {
            font-weight: 600;
            min-width: 200px;
            color: var(--vscode-descriptionForeground);
        }

        .response-value {
            flex: 1;
        }

        pre {
            background: var(--vscode-textCodeBlock-background);
            padding: 12px;
            border-radius: 4px;
            overflow-x: auto;
            font-size: 12px;
            font-family: var(--vscode-editor-font-family);
        }

        .error-message {
            background: rgba(220, 53, 69, 0.1);
            border: 1px solid #dc3545;
            border-radius: 6px;
            padding: 16px;
            color: #dc3545;
        }

        .empty-state {
            text-align: center;
            padding: 40px;
            color: var(--vscode-descriptionForeground);
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-left">
            <div>
                <span class="title" id="title">Meta-Workflow Report</span>
                <span class="status-badge status-running" id="status">Initializing...</span>
            </div>
            <div class="run-id" id="runId"></div>
        </div>
        <div class="actions">
            <button onclick="refresh()">Re-run</button>
            <button class="secondary" onclick="copyReport()">Copy</button>
            <button class="secondary" onclick="exportJson()">Export</button>
            <button class="secondary" onclick="openDashboard()">Dashboard</button>
        </div>
    </div>

    <div id="content">
        <div class="loading">
            <div class="spinner"></div>
            <p style="margin-top: 16px;">Initializing report...</p>
        </div>
    </div>

    <script nonce="${nonce}">
        const vscode = acquireVsCodeApi();
        let currentReport = null;

        // Listen for messages from extension
        window.addEventListener('message', event => {
            const message = event.data;

            if (message.type === 'reportUpdate') {
                currentReport = message.data;
                updateUI(message.data);
            }
        });

        function updateUI(report) {
            const statusEl = document.getElementById('status');
            const titleEl = document.getElementById('title');
            const runIdEl = document.getElementById('runId');
            const contentEl = document.getElementById('content');

            // Update title
            titleEl.textContent = formatTemplateName(report.template_id || 'Meta-Workflow');

            // Update run ID
            runIdEl.textContent = report.run_id ? 'Run ID: ' + report.run_id : '';

            // Update status badge
            const status = report.status || (report.success ? 'success' : 'failed');
            statusEl.className = 'status-badge status-' + status;
            statusEl.textContent = status === 'running' ? 'Running...' :
                                  status === 'success' ? 'Success' : 'Failed';

            // Update content based on status
            if (status === 'running') {
                contentEl.innerHTML = renderLoading();
            } else if (status === 'failed' && report.error) {
                contentEl.innerHTML = renderError(report);
            } else {
                contentEl.innerHTML = renderReport(report);
            }
        }

        function formatTemplateName(templateId) {
            if (!templateId) return 'Meta-Workflow Report';
            return templateId.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
        }

        function renderLoading() {
            return \`
                <div class="loading">
                    <div class="spinner"></div>
                    <p style="margin-top: 16px;">Running meta-workflow...</p>
                    <p style="margin-top: 8px; font-size: 12px; color: var(--vscode-descriptionForeground);">
                        This may take a few minutes depending on the workflow complexity.
                    </p>
                </div>
            \`;
        }

        function renderError(report) {
            return \`
                <div class="error-message">
                    <h3 style="margin-bottom: 8px;">Workflow Failed</h3>
                    <p>\${escapeHtml(report.error || 'Unknown error occurred')}</p>
                </div>
                \${report.agent_results && report.agent_results.length > 0 ? renderAgentResults(report) : ''}
            \`;
        }

        function renderReport(report) {
            const successCount = (report.agent_results || []).filter(a => a.success).length;
            const totalAgents = report.agents_created || (report.agent_results || []).length;
            const successRate = totalAgents > 0 ? Math.round((successCount / totalAgents) * 100) : 0;

            return \`
                \${renderMetrics(report, successCount, totalAgents, successRate)}
                \${renderFormResponses(report)}
                \${renderAgentResults(report)}
                \${renderRawOutput(report)}
            \`;
        }

        function renderMetrics(report, successCount, totalAgents, successRate) {
            const costClass = report.total_cost > 1 ? 'warning' : 'info';
            const rateClass = successRate === 100 ? 'success' : successRate >= 50 ? 'warning' : 'error';

            return \`
                <div class="metric-grid">
                    <div class="metric-card">
                        <div class="metric-value \${costClass}">$\${(report.total_cost || 0).toFixed(4)}</div>
                        <div class="metric-label">Total Cost</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value info">\${((report.total_duration || 0)).toFixed(1)}s</div>
                        <div class="metric-label">Duration</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">\${successCount}/\${totalAgents}</div>
                        <div class="metric-label">Agents</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value \${rateClass}">\${successRate}%</div>
                        <div class="metric-label">Success Rate</div>
                    </div>
                </div>
            \`;
        }

        function renderFormResponses(report) {
            const responses = report.form_responses?.responses || {};
            const keys = Object.keys(responses);

            if (keys.length === 0) {
                return '';
            }

            const items = keys.map(key => \`
                <div class="response-item">
                    <div class="response-key">\${escapeHtml(key)}</div>
                    <div class="response-value">\${escapeHtml(String(responses[key]))}</div>
                </div>
            \`).join('');

            return \`
                <div class="section">
                    <div class="section-header" onclick="toggleSection('responses')">
                        <div class="section-title">
                            <span class="section-arrow" id="responses-arrow">▼</span>
                            Form Responses
                        </div>
                        <span style="color: var(--vscode-descriptionForeground); font-size: 12px;">
                            \${keys.length} responses
                        </span>
                    </div>
                    <div class="section-content" id="responses-content">
                        \${items}
                    </div>
                </div>
            \`;
        }

        function renderAgentResults(report) {
            const agents = report.agent_results || [];

            if (agents.length === 0) {
                return \`
                    <div class="section">
                        <div class="section-header">
                            <div class="section-title">Agent Results</div>
                        </div>
                        <div class="section-content">
                            <div class="empty-state">No agent results available</div>
                        </div>
                    </div>
                \`;
            }

            const successCount = agents.filter(a => a.success).length;

            const agentCards = agents.map((agent, idx) => \`
                <div class="agent-card">
                    <div class="agent-header" onclick="toggleAgent(\${idx})" style="cursor: pointer;">
                        <span class="agent-status">\${agent.success ? '✅' : '❌'}</span>
                        <span class="agent-role">\${escapeHtml(agent.role)}</span>
                        <span class="tier-badge tier-\${(agent.tier_used || 'capable').toLowerCase()}">\${agent.tier_used || 'capable'}</span>
                        <div class="agent-metrics">
                            <span>$\${(agent.cost || 0).toFixed(4)}</span>
                            <span>\${(agent.duration || 0).toFixed(1)}s</span>
                        </div>
                    </div>
                    <div class="agent-details collapsed" id="agent-\${idx}">
                        \${agent.error ? \`<div class="error-message" style="margin-bottom: 12px;">\${escapeHtml(agent.error)}</div>\` : ''}
                        <pre>\${escapeHtml(JSON.stringify(agent.output || {}, null, 2))}</pre>
                    </div>
                </div>
            \`).join('');

            return \`
                <div class="section">
                    <div class="section-header" onclick="toggleSection('agents')">
                        <div class="section-title">
                            <span class="section-arrow" id="agents-arrow">▼</span>
                            Agent Results
                        </div>
                        <span style="color: var(--vscode-descriptionForeground); font-size: 12px;">
                            \${successCount}/\${agents.length} successful
                        </span>
                    </div>
                    <div class="section-content" id="agents-content">
                        \${agentCards}
                    </div>
                </div>
            \`;
        }

        function renderRawOutput(report) {
            return \`
                <div class="section">
                    <div class="section-header" onclick="toggleSection('raw')">
                        <div class="section-title">
                            <span class="section-arrow collapsed" id="raw-arrow">▼</span>
                            Raw Output
                        </div>
                        <button onclick="event.stopPropagation(); viewRawOutput()" class="secondary" style="padding: 4px 8px; font-size: 11px;">
                            Open in Editor
                        </button>
                    </div>
                    <div class="section-content collapsed" id="raw-content">
                        <pre>\${escapeHtml(JSON.stringify(report, null, 2))}</pre>
                    </div>
                </div>
            \`;
        }

        function escapeHtml(text) {
            if (typeof text !== 'string') text = String(text);
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        function toggleSection(sectionId) {
            const content = document.getElementById(sectionId + '-content');
            const arrow = document.getElementById(sectionId + '-arrow');

            if (content && arrow) {
                content.classList.toggle('collapsed');
                arrow.classList.toggle('collapsed');
            }
        }

        function toggleAgent(idx) {
            const details = document.getElementById('agent-' + idx);
            if (details) {
                details.classList.toggle('collapsed');
            }
        }

        function refresh() {
            vscode.postMessage({ type: 'refresh' });
        }

        function copyReport() {
            vscode.postMessage({ type: 'copyReport' });
        }

        function exportJson() {
            vscode.postMessage({ type: 'exportJson' });
        }

        function viewRawOutput() {
            vscode.postMessage({ type: 'viewRawOutput' });
        }

        function openDashboard() {
            vscode.postMessage({ type: 'openDashboard' });
        }
    </script>
</body>
</html>`;
    }
}

function getNonce() {
    let text = '';
    const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    for (let i = 0; i < 32; i++) {
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
}
