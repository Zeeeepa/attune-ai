/**
 * Research Synthesis Panel for VSCode Extension
 *
 * Provides a UI for multi-document research synthesis using the
 * ResearchSynthesisWorkflow. Requires at least 2 source documents.
 *
 * Copyright 2025 Smart-AI-Memory
 * Licensed under Fair Source License 0.9
 */

import * as vscode from 'vscode';
import * as cp from 'child_process';
import * as path from 'path';
import {
    getFilePickerService,
    createFilePickerMessageHandler,
    FilePickerService,
    FilePickerResponse,
    FILE_FILTERS
} from '../services/FilePickerService';

// =============================================================================
// Types
// =============================================================================

interface SourceDocument {
    id: string;
    name: string;
    path: string;
    content?: string;
}

interface SynthesisResult {
    answer: string;
    key_insights: string[];
    confidence: number;
    model_tier_used: string;
    complexity_score: number;
    source_count: number;
    cost: number;
    savings_percent: number;
}

interface ResearchSession {
    sources: SourceDocument[];
    question: string;
    result: SynthesisResult | null;
    status: 'idle' | 'analyzing' | 'complete' | 'error';
    error: string | null;
}

interface BackendHealth {
    status: 'ok' | 'degraded' | 'unknown';
    lastSuccessTime: number | null;
    consecutiveFailures: number;
    lastError: string | null;
}

// =============================================================================
// Constants
// =============================================================================

const MIN_SOURCES = 2;

// =============================================================================
// Panel Implementation
// =============================================================================

export class ResearchSynthesisPanel implements vscode.WebviewViewProvider {
    public static readonly viewType = 'research-synthesis';

    private _view?: vscode.WebviewView;
    private _extensionUri: vscode.Uri;
    private _session: ResearchSession = {
        sources: [],
        question: '',
        result: null,
        status: 'idle',
        error: null,
    };
    private _disposables: vscode.Disposable[] = [];
    private _activeProcess: cp.ChildProcess | null = null;
    private _filePickerService: FilePickerService;
    private _backendHealth: BackendHealth = {
        status: 'unknown',
        lastSuccessTime: null,
        consecutiveFailures: 0,
        lastError: null,
    };

    constructor(extensionUri: vscode.Uri, _context: vscode.ExtensionContext) {
        this._extensionUri = extensionUri;
        this._filePickerService = getFilePickerService();
    }

    public dispose() {
        while (this._disposables.length) {
            const disposable = this._disposables.pop();
            if (disposable) {
                disposable.dispose();
            }
        }
    }

    public resolveWebviewView(
        webviewView: vscode.WebviewView,
        _context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken
    ) {
        this._view = webviewView;

        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri],
        };

        webviewView.webview.html = this._getHtmlContent();

        webviewView.webview.onDidReceiveMessage(async (message) => {
            // Route filePicker messages through the service
            if (message.type?.startsWith('filePicker:')) {
                await this._handleFilePickerMessage(message);
                return;
            }

            switch (message.type) {
                case 'removeSource':
                    this._removeSource(message.id);
                    break;
                case 'setQuestion':
                    this._session.question = message.question;
                    this._sendSessionState();
                    break;
                case 'runSynthesis':
                    await this._runSynthesis();
                    break;
                case 'cancelSynthesis':
                    this._cancelSynthesis();
                    break;
                case 'getSessionState':
                    this._sendSessionState();
                    this._sendHealthStatus();
                    break;
                case 'resetSession':
                    this._resetSession();
                    break;
                case 'exportMarkdown':
                    await this._exportToMarkdown();
                    break;
                case 'askClaude':
                    await this._askClaude(message.content);
                    break;
            }
        });
    }

    // =========================================================================
    // Source Management
    // =========================================================================

    private async _handleFilePickerMessage(message: any): Promise<void> {
        switch (message.type) {
            case 'filePicker:selectFiles': {
                const results = await this._filePickerService.showFilePicker({
                    allowMultiple: true,
                    filters: FILE_FILTERS.DOCUMENTS,
                    title: 'Select source documents'
                });
                if (results) {
                    for (const result of results) {
                        await this._addSource(result.absolutePath);
                    }
                }
                break;
            }
            case 'filePicker:selectFolder': {
                const result = await this._filePickerService.showFolderPicker({
                    title: 'Select folder to scan'
                });
                if (result) {
                    const pattern = new vscode.RelativePattern(result.absolutePath, '**/*.{md,txt,py,ts,js}');
                    const files = await vscode.workspace.findFiles(pattern, '**/node_modules/**', 20);
                    for (const file of files) {
                        await this._addSource(file.fsPath);
                    }
                }
                break;
            }
            case 'filePicker:useActiveFile': {
                const result = this._filePickerService.getActiveFile();
                if (result) {
                    await this._addSource(result.absolutePath);
                } else {
                    vscode.window.showWarningMessage('No active file to add');
                }
                break;
            }
            case 'filePicker:useProjectRoot': {
                const result = this._filePickerService.getProjectRoot();
                if (result) {
                    const pattern = new vscode.RelativePattern(result.absolutePath, '**/*.{md,txt,py,ts,js}');
                    const files = await vscode.workspace.findFiles(pattern, '**/node_modules/**', 20);
                    for (const file of files) {
                        await this._addSource(file.fsPath);
                    }
                } else {
                    vscode.window.showWarningMessage('No workspace folder open');
                }
                break;
            }
        }
    }

    private async _addSource(filePath: string) {
        // Check if already added
        if (this._session.sources.some(s => s.path === filePath)) {
            return;
        }

        try {
            const content = await vscode.workspace.fs.readFile(vscode.Uri.file(filePath));
            const source: SourceDocument = {
                id: `src_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`,
                name: path.basename(filePath),
                path: filePath,
                content: new TextDecoder().decode(content),
            };

            this._session.sources.push(source);
            this._sendSessionState();
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to read file: ${filePath}`);
        }
    }

    private _removeSource(id: string) {
        this._session.sources = this._session.sources.filter(s => s.id !== id);
        this._sendSessionState();
    }

    private _resetSession() {
        this._session = {
            sources: [],
            question: '',
            result: null,
            status: 'idle',
            error: null,
        };
        this._sendSessionState();
    }

    // =========================================================================
    // Synthesis Execution
    // =========================================================================

    private async _runSynthesis() {
        if (this._session.sources.length < MIN_SOURCES) {
            vscode.window.showWarningMessage(
                `Research synthesis requires at least ${MIN_SOURCES} source documents.`
            );
            return;
        }

        if (!this._session.question.trim()) {
            vscode.window.showWarningMessage('Please enter a research question.');
            return;
        }

        this._session.status = 'analyzing';
        this._session.error = null;
        this._sendSessionState();

        const config = vscode.workspace.getConfiguration('empathy');
        const pythonPath = config.get<string>('pythonPath', 'python');
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || '.';

        // Prepare input data
        const inputData = {
            sources: this._session.sources.map(s => s.content),
            question: this._session.question,
        };

        // Get path to runner script (bundled with extension)
        const runnerScript = path.join(
            this._extensionUri.fsPath,
            'scripts',
            'research_synthesis_runner.py'
        );

        const args = [
            runnerScript,
            JSON.stringify(inputData),
        ];

        this._activeProcess = cp.execFile(pythonPath, args, {
            cwd: workspaceFolder,
            maxBuffer: 10 * 1024 * 1024,
            timeout: 300000, // 5 minutes for multi-doc synthesis
        }, (error, stdout, stderr) => {
            this._activeProcess = null;

            if (error) {
                if ((error as any).killed) {
                    return; // Cancelled
                }
                console.error('Synthesis error:', stderr || error.message);
                this._recordBackendFailure(error.message);
                this._session.status = 'error';
                this._session.error = error.message;
                this._sendSessionState();
                return;
            }

            try {
                const result = JSON.parse(stdout.trim());
                this._session.result = result;
                this._session.status = 'complete';
                this._recordBackendSuccess();
                this._sendSessionState();
            } catch (parseErr) {
                console.error('Parse error:', stdout, parseErr);
                this._recordBackendFailure('Failed to parse synthesis results');
                this._session.status = 'error';
                this._session.error = 'Failed to parse synthesis results';
                this._sendSessionState();
            }
        });
    }

    private _cancelSynthesis() {
        if (this._activeProcess) {
            this._activeProcess.kill();
            this._activeProcess = null;
            this._session.status = 'idle';
            this._sendSessionState();
            vscode.window.showInformationMessage('Synthesis cancelled');
        }
    }

    // =========================================================================
    // Export
    // =========================================================================

    private async _exportToMarkdown() {
        if (!this._session.result) {
            return;
        }

        const content = `# Research Synthesis

## Question
${this._session.question}

## Sources Analyzed
${this._session.sources.map(s => `- ${s.name}`).join('\n')}

## Key Insights
${this._session.result.key_insights.map((i, idx) => `${idx + 1}. ${i}`).join('\n')}

## Full Synthesis
${this._session.result.answer}

---
*Generated by Empathy Framework Research Synthesis*
*Sources: ${this._session.result.source_count} | Cost: $${this._session.result.cost?.toFixed(4) || '0.00'} | Saved: ${this._session.result.savings_percent?.toFixed(1) || '0'}%*
`;

        const doc = await vscode.workspace.openTextDocument({
            content,
            language: 'markdown',
        });
        await vscode.window.showTextDocument(doc);
    }

    private async _askClaude(content: string) {
        // Copy report with prompt to clipboard
        await vscode.env.clipboard.writeText(content);
        vscode.window.showInformationMessage('Report copied! Paste into Claude Code input.');
    }

    // =========================================================================
    // Health Tracking
    // =========================================================================

    private _recordBackendSuccess() {
        this._backendHealth.status = 'ok';
        this._backendHealth.lastSuccessTime = Date.now();
        this._backendHealth.consecutiveFailures = 0;
        this._backendHealth.lastError = null;
        this._sendHealthStatus();
    }

    private _recordBackendFailure(error: string) {
        this._backendHealth.consecutiveFailures++;
        this._backendHealth.lastError = error;
        if (this._backendHealth.consecutiveFailures >= 2) {
            this._backendHealth.status = 'degraded';
        }
        this._sendHealthStatus();
    }

    private _sendHealthStatus() {
        this._view?.webview.postMessage({
            type: 'healthStatus',
            health: this._backendHealth,
        });
    }

    private _sendSessionState() {
        this._view?.webview.postMessage({
            type: 'sessionState',
            session: {
                sources: this._session.sources.map(s => ({
                    id: s.id,
                    name: s.name,
                    path: s.path,
                })),
                question: this._session.question,
                result: this._session.result,
                status: this._session.status,
                error: this._session.error,
                canRun: this._session.sources.length >= MIN_SOURCES && this._session.question.trim().length > 0,
            },
        });
    }

    // =========================================================================
    // HTML Content
    // =========================================================================

    private _getHtmlContent(): string {
        return `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        :root {
            --bg: var(--vscode-editor-background);
            --fg: var(--vscode-editor-foreground);
            --border: var(--vscode-panel-border);
            --button-bg: var(--vscode-button-background);
            --button-fg: var(--vscode-button-foreground);
            --input-bg: var(--vscode-input-background);
            --input-fg: var(--vscode-input-foreground);
            --input-border: var(--vscode-input-border);
            --success: #4caf50;
            --warning: #ff9800;
            --error: #f44336;
        }

        body {
            font-family: var(--vscode-font-family);
            font-size: var(--vscode-font-size);
            color: var(--fg);
            background: var(--bg);
            padding: 12px;
            margin: 0;
        }

        h2 {
            font-size: 14px;
            font-weight: 600;
            margin: 0 0 12px 0;
        }

        .section {
            margin-bottom: 16px;
        }

        .card {
            background: var(--vscode-editor-inactiveSelectionBackground);
            border-radius: 6px;
            padding: 12px;
            margin-bottom: 12px;
        }

        .btn {
            background: var(--button-bg);
            color: var(--button-fg);
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            margin-right: 6px;
        }

        .btn:hover {
            opacity: 0.9;
        }

        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .btn-secondary {
            background: transparent;
            border: 1px solid var(--border);
            color: var(--fg);
        }

        .btn-row {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin-top: 8px;
        }

        .input {
            width: 100%;
            padding: 8px;
            border: 1px solid var(--input-border);
            border-radius: 4px;
            background: var(--input-bg);
            color: var(--input-fg);
            font-size: 12px;
            box-sizing: border-box;
        }

        textarea.input {
            min-height: 60px;
            resize: vertical;
        }

        .source-list {
            max-height: 150px;
            overflow-y: auto;
            margin: 8px 0;
        }

        .source-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 6px 8px;
            background: var(--input-bg);
            border-radius: 4px;
            margin-bottom: 4px;
            font-size: 11px;
        }

        .source-item .name {
            flex: 1;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .source-item .remove {
            cursor: pointer;
            opacity: 0.6;
            margin-left: 8px;
        }

        .source-item .remove:hover {
            opacity: 1;
            color: var(--error);
        }

        .source-count {
            font-size: 11px;
            opacity: 0.7;
            margin-bottom: 8px;
        }

        .min-warning {
            color: var(--warning);
            font-size: 11px;
            margin-top: 8px;
        }

        .result-section {
            margin-top: 16px;
        }

        .insights-list {
            margin: 8px 0;
            padding-left: 20px;
        }

        .insights-list li {
            margin-bottom: 4px;
            font-size: 12px;
        }

        .synthesis-text {
            background: var(--input-bg);
            padding: 12px;
            border-radius: 4px;
            font-size: 12px;
            line-height: 1.5;
            max-height: 300px;
            overflow-y: auto;
            white-space: pre-wrap;
        }

        .stats-row {
            display: flex;
            gap: 16px;
            margin-top: 12px;
            font-size: 11px;
            opacity: 0.8;
        }

        .status-analyzing {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 12px;
            background: var(--input-bg);
            border-radius: 4px;
        }

        .spinner {
            width: 16px;
            height: 16px;
            border: 2px solid var(--border);
            border-top-color: var(--button-bg);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .error-banner {
            background: rgba(244, 67, 54, 0.15);
            color: var(--error);
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 12px;
            margin-bottom: 12px;
        }

        .health-indicator {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 10px;
            padding: 4px 8px;
            border-radius: 4px;
            margin-bottom: 8px;
        }

        .health-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
        }

        .health-ok { background: rgba(0, 128, 0, 0.15); }
        .health-ok .health-dot { background: var(--success); }
        .health-degraded { background: rgba(255, 165, 0, 0.15); }
        .health-degraded .health-dot { background: var(--warning); }
        .health-unknown { background: rgba(128, 128, 128, 0.15); }
        .health-unknown .health-dot { background: #888; }

        .hidden { display: none !important; }
    </style>
</head>
<body>
    <!-- Health Indicator -->
    <div id="health-indicator" class="health-indicator health-unknown">
        <span class="health-dot"></span>
        <span id="health-text">Backend: Checking...</span>
    </div>

    <!-- Error Banner -->
    <div id="error-banner" class="error-banner hidden"></div>

    <!-- Main Content -->
    <div id="input-section">
        <h2>Research Synthesis</h2>
        <p style="font-size: 11px; opacity: 0.8; margin-bottom: 12px;">
            Compare and synthesize insights from multiple documents.
        </p>

        <!-- Sources -->
        <div class="section">
            <div class="source-count">
                <span id="source-count">0</span> source(s) added
                <span id="min-warning" class="min-warning hidden">(minimum ${MIN_SOURCES} required)</span>
            </div>
            <div id="source-list" class="source-list"></div>
            <div class="btn-row">
                <button class="btn btn-secondary" onclick="addFiles()">Files</button>
                <button class="btn btn-secondary" onclick="addFolder()">Folder</button>
                <button class="btn btn-secondary" onclick="addActive()">Active</button>
                <button class="btn btn-secondary" onclick="addProject()">Project</button>
            </div>
        </div>

        <!-- Question -->
        <div class="section">
            <label style="font-size: 11px; display: block; margin-bottom: 4px;">Research Question</label>
            <textarea
                id="question-input"
                class="input"
                placeholder="What patterns emerge across these documents?"
                oninput="updateQuestion(this.value)"
            ></textarea>
        </div>

        <!-- Run Button -->
        <button id="run-btn" class="btn" onclick="runSynthesis()" disabled>
            Synthesize Research
        </button>
    </div>

    <!-- Analyzing State -->
    <div id="analyzing-section" class="hidden">
        <div class="status-analyzing">
            <div class="spinner"></div>
            <span>Analyzing <span id="analyzing-count">0</span> sources...</span>
        </div>
        <button class="btn btn-secondary" style="margin-top: 12px;" onclick="cancelSynthesis()">
            Cancel
        </button>
    </div>

    <!-- Results -->
    <div id="results-section" class="result-section hidden">
        <h2>Synthesis Complete</h2>

        <div class="card">
            <strong>Key Insights</strong>
            <ol id="insights-list" class="insights-list"></ol>
        </div>

        <div class="card">
            <strong>Full Synthesis</strong>
            <div id="synthesis-text" class="synthesis-text"></div>
        </div>

        <div class="stats-row">
            <span>Sources: <span id="stat-sources">0</span></span>
            <span>Cost: $<span id="stat-cost">0.00</span></span>
            <span>Saved: <span id="stat-savings">0</span>%</span>
        </div>

        <div style="margin-top: 12px;">
            <button class="btn" onclick="exportMarkdown()">Export to Markdown</button>
            <button class="btn btn-secondary" onclick="newResearch()">New Research</button>
        </div>

        <!-- Ask Claude Action -->
        <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--border);">
            <button id="ask-claude-btn" class="btn" style="width: 100%; font-size: 11px; padding: 8px 12px;" onclick="askClaude()" title="Copy report with prompt to clipboard for Claude review">
                &#x1F4AC; Ask Claude
            </button>
        </div>
    </div>

    <script>
        const vscode = acquireVsCodeApi();

        let session = {
            sources: [],
            question: '',
            result: null,
            status: 'idle',
            canRun: false,
        };

        // Message handlers
        window.addEventListener('message', event => {
            const message = event.data;
            switch (message.type) {
                case 'sessionState':
                    session = message.session;
                    renderState();
                    break;
                case 'healthStatus':
                    updateHealthIndicator(message.health);
                    break;
            }
        });

        function renderState() {
            // Update source list
            const sourceList = document.getElementById('source-list');
            sourceList.innerHTML = session.sources.map(s => \`
                <div class="source-item">
                    <span class="name" title="\${s.path}">\${s.name}</span>
                    <span class="remove" onclick="removeSource('\${s.id}')">&times;</span>
                </div>
            \`).join('');

            // Update source count
            document.getElementById('source-count').textContent = session.sources.length;
            const minWarning = document.getElementById('min-warning');
            if (session.sources.length < ${MIN_SOURCES}) {
                minWarning.classList.remove('hidden');
            } else {
                minWarning.classList.add('hidden');
            }

            // Update question
            const questionInput = document.getElementById('question-input');
            if (questionInput.value !== session.question) {
                questionInput.value = session.question;
            }

            // Update run button
            document.getElementById('run-btn').disabled = !session.canRun;

            // Show/hide sections based on status
            const inputSection = document.getElementById('input-section');
            const analyzingSection = document.getElementById('analyzing-section');
            const resultsSection = document.getElementById('results-section');
            const errorBanner = document.getElementById('error-banner');

            inputSection.classList.toggle('hidden', session.status === 'analyzing');
            analyzingSection.classList.toggle('hidden', session.status !== 'analyzing');
            resultsSection.classList.toggle('hidden', session.status !== 'complete');

            if (session.status === 'analyzing') {
                document.getElementById('analyzing-count').textContent = session.sources.length;
            }

            if (session.error) {
                errorBanner.textContent = session.error;
                errorBanner.classList.remove('hidden');
            } else {
                errorBanner.classList.add('hidden');
            }

            // Render results
            if (session.result) {
                const insightsList = document.getElementById('insights-list');
                insightsList.innerHTML = (session.result.key_insights || [])
                    .map(i => \`<li>\${i}</li>\`)
                    .join('');

                document.getElementById('synthesis-text').textContent = session.result.answer || '';
                document.getElementById('stat-sources').textContent = session.result.source_count || 0;
                document.getElementById('stat-cost').textContent = (session.result.cost || 0).toFixed(4);
                document.getElementById('stat-savings').textContent = (session.result.savings_percent || 0).toFixed(1);
            }
        }

        function updateHealthIndicator(health) {
            const indicator = document.getElementById('health-indicator');
            const text = document.getElementById('health-text');

            indicator.classList.remove('health-ok', 'health-degraded', 'health-unknown');

            if (health.status === 'ok') {
                indicator.classList.add('health-ok');
                text.textContent = 'Backend: OK';
            } else if (health.status === 'degraded') {
                indicator.classList.add('health-degraded');
                text.textContent = 'Backend: Degraded';
            } else {
                indicator.classList.add('health-unknown');
                text.textContent = 'Backend: Unknown';
            }
        }

        // Actions - using standardized filePicker:* message types
        function addFiles() {
            vscode.postMessage({ type: 'filePicker:selectFiles' });
        }

        function addFolder() {
            vscode.postMessage({ type: 'filePicker:selectFolder' });
        }

        function addActive() {
            vscode.postMessage({ type: 'filePicker:useActiveFile' });
        }

        function addProject() {
            vscode.postMessage({ type: 'filePicker:useProjectRoot' });
        }

        function removeSource(id) {
            vscode.postMessage({ type: 'removeSource', id });
        }

        function updateQuestion(value) {
            vscode.postMessage({ type: 'setQuestion', question: value });
        }

        function runSynthesis() {
            vscode.postMessage({ type: 'runSynthesis' });
        }

        function cancelSynthesis() {
            vscode.postMessage({ type: 'cancelSynthesis' });
        }

        function exportMarkdown() {
            vscode.postMessage({ type: 'exportMarkdown' });
        }

        function newResearch() {
            vscode.postMessage({ type: 'resetSession' });
        }

        function askClaude() {
            if (!session.result) return;

            const btn = document.getElementById('ask-claude-btn');
            const newline = String.fromCharCode(10);

            // Build metadata header
            const metadata = [
                '--- Research Synthesis Report ---',
                'Question: ' + session.question,
                'Sources: ' + session.sources.length + ' documents',
                'Timestamp: ' + new Date().toISOString(),
                'Cost: $' + (session.result.cost || 0).toFixed(4),
                'Savings: ' + (session.result.savings_percent || 0).toFixed(1) + '%',
                'Model Tier: ' + (session.result.model_tier_used || 'unknown'),
                '---',
                ''
            ].join(newline);

            // Build key insights section
            const insights = (session.result.key_insights || []).length > 0
                ? 'Key Insights:' + newline + session.result.key_insights.map((i, idx) => (idx + 1) + '. ' + i).join(newline) + newline + newline
                : '';

            // Build the prompt
            const prompt = 'Please review this research synthesis report and provide:' + newline +
                '1. Your assessment of the findings' + newline +
                '2. Any gaps or areas that need deeper investigation' + newline +
                '3. Suggested next steps or actions' + newline +
                '4. Questions I should consider asking' + newline + newline +
                metadata + insights +
                'Full Synthesis:' + newline + session.result.answer;

            // Send to backend
            vscode.postMessage({ type: 'askClaude', content: prompt });

            // Visual feedback
            const originalText = btn.innerHTML;
            btn.innerHTML = '&#x2714; Copied!';
            btn.style.background = 'rgba(16, 185, 129, 0.3)';
            setTimeout(() => {
                btn.innerHTML = originalText;
                btn.style.background = '';
            }, 2000);
        }

        // Initialize
        vscode.postMessage({ type: 'getSessionState' });
    </script>
</body>
</html>`;
    }
}
