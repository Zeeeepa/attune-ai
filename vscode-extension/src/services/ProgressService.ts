/**
 * Progress Service
 *
 * WebSocket client for receiving real-time workflow progress updates.
 * Connects to the Python progress server and emits events for UI updates.
 *
 * Copyright 2025 Smart AI Memory, LLC
 * Licensed under Fair Source 0.9
 */

import * as vscode from 'vscode';

/**
 * Progress status enum matching Python side
 */
export type ProgressStatus =
    | 'pending'
    | 'running'
    | 'completed'
    | 'failed'
    | 'skipped'
    | 'fallback'
    | 'retrying';

/**
 * Stage progress information
 */
export interface StageProgress {
    name: string;
    status: ProgressStatus;
    tier: string;
    model: string;
    started_at: string | null;
    completed_at: string | null;
    duration_ms: number;
    cost: number;
    tokens_in: number;
    tokens_out: number;
    error: string | null;
    fallback_info: string | null;
    retry_count: number;
}

/**
 * Progress update from server
 */
export interface ProgressUpdate {
    workflow: string;
    workflow_id: string;
    current_stage: string;
    stage_index: number;
    total_stages: number;
    status: ProgressStatus;
    message: string;
    cost_so_far: number;
    tokens_so_far: number;
    percent_complete: number;
    estimated_remaining_ms: number | null;
    stages: StageProgress[];
    fallback_info: string | null;
    error: string | null;
    timestamp: string;
}

/**
 * Event types emitted by ProgressService
 */
export type ProgressEvent =
    | { type: 'connected' }
    | { type: 'disconnected' }
    | { type: 'progress'; update: ProgressUpdate }
    | { type: 'error'; message: string };

/**
 * Configuration for progress service
 */
export interface ProgressServiceConfig {
    host: string;
    port: number;
    reconnectInterval: number;
    maxReconnectAttempts: number;
}

const DEFAULT_CONFIG: ProgressServiceConfig = {
    host: 'localhost',
    port: 8766,
    reconnectInterval: 3000,
    maxReconnectAttempts: 5,
};

/**
 * Service for receiving real-time workflow progress via WebSocket
 */
export class ProgressService {
    private _socket: WebSocket | null = null;
    private _config: ProgressServiceConfig;
    private _reconnectAttempts = 0;
    private _reconnectTimer: NodeJS.Timeout | null = null;
    private _listeners: ((event: ProgressEvent) => void)[] = [];
    private _subscriptions: Set<string> = new Set();
    private _isConnecting = false;

    constructor(config?: Partial<ProgressServiceConfig>) {
        this._config = { ...DEFAULT_CONFIG, ...config };
    }

    /**
     * Connect to the progress server
     */
    public async connect(): Promise<void> {
        if (this._socket || this._isConnecting) {
            return;
        }

        this._isConnecting = true;

        try {
            const url = `ws://${this._config.host}:${this._config.port}`;

            // Note: WebSocket is available in VS Code's webview context
            // For the extension host, we need to use a Node.js WebSocket library
            // This implementation assumes it's called from a webview
            this._socket = new WebSocket(url);

            this._socket.onopen = () => {
                this._isConnecting = false;
                this._reconnectAttempts = 0;
                this._emit({ type: 'connected' });

                // Re-subscribe to any workflows
                for (const workflowId of this._subscriptions) {
                    this._send({ type: 'subscribe', workflow_id: workflowId });
                }
            };

            this._socket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this._handleMessage(data);
                } catch (error) {
                    console.error('Failed to parse progress message:', error);
                }
            };

            this._socket.onclose = () => {
                this._socket = null;
                this._isConnecting = false;
                this._emit({ type: 'disconnected' });
                this._scheduleReconnect();
            };

            this._socket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this._emit({ type: 'error', message: 'WebSocket connection error' });
            };

        } catch (error) {
            this._isConnecting = false;
            this._emit({ type: 'error', message: `Failed to connect: ${error}` });
            this._scheduleReconnect();
        }
    }

    /**
     * Disconnect from the progress server
     */
    public disconnect(): void {
        if (this._reconnectTimer) {
            clearTimeout(this._reconnectTimer);
            this._reconnectTimer = null;
        }

        if (this._socket) {
            this._socket.close();
            this._socket = null;
        }

        this._reconnectAttempts = 0;
    }

    /**
     * Subscribe to updates for a specific workflow
     */
    public subscribe(workflowId: string): void {
        this._subscriptions.add(workflowId);

        if (this._socket && this._socket.readyState === WebSocket.OPEN) {
            this._send({ type: 'subscribe', workflow_id: workflowId });
        }
    }

    /**
     * Unsubscribe from a workflow's updates
     */
    public unsubscribe(workflowId: string): void {
        this._subscriptions.delete(workflowId);
    }

    /**
     * Add an event listener
     */
    public addListener(listener: (event: ProgressEvent) => void): void {
        this._listeners.push(listener);
    }

    /**
     * Remove an event listener
     */
    public removeListener(listener: (event: ProgressEvent) => void): void {
        const index = this._listeners.indexOf(listener);
        if (index !== -1) {
            this._listeners.splice(index, 1);
        }
    }

    /**
     * Check if connected
     */
    public get isConnected(): boolean {
        return this._socket !== null && this._socket.readyState === WebSocket.OPEN;
    }

    /**
     * Handle incoming message from server
     */
    private _handleMessage(data: any): void {
        switch (data.type) {
            case 'progress':
                const update: ProgressUpdate = {
                    workflow: data.workflow,
                    workflow_id: data.workflow_id,
                    current_stage: data.current_stage,
                    stage_index: data.stage_index,
                    total_stages: data.total_stages,
                    status: data.status,
                    message: data.message,
                    cost_so_far: data.cost_so_far,
                    tokens_so_far: data.tokens_so_far,
                    percent_complete: data.percent_complete,
                    estimated_remaining_ms: data.estimated_remaining_ms,
                    stages: data.stages || [],
                    fallback_info: data.fallback_info,
                    error: data.error,
                    timestamp: data.timestamp,
                };
                this._emit({ type: 'progress', update });
                break;

            case 'connected':
                // Server acknowledged connection
                break;

            case 'subscribed':
                // Server acknowledged subscription
                break;

            case 'pong':
                // Response to ping
                break;

            case 'error':
                this._emit({ type: 'error', message: data.message });
                break;
        }
    }

    /**
     * Send message to server
     */
    private _send(data: any): void {
        if (this._socket && this._socket.readyState === WebSocket.OPEN) {
            this._socket.send(JSON.stringify(data));
        }
    }

    /**
     * Emit event to all listeners
     */
    private _emit(event: ProgressEvent): void {
        for (const listener of this._listeners) {
            try {
                listener(event);
            } catch (error) {
                console.error('Progress listener error:', error);
            }
        }
    }

    /**
     * Schedule a reconnection attempt
     */
    private _scheduleReconnect(): void {
        if (this._reconnectAttempts >= this._config.maxReconnectAttempts) {
            console.log('Max reconnect attempts reached');
            return;
        }

        this._reconnectAttempts++;
        const delay = this._config.reconnectInterval * this._reconnectAttempts;

        this._reconnectTimer = setTimeout(() => {
            this.connect();
        }, delay);
    }
}

// Singleton instance for extension-wide use
let _progressService: ProgressService | null = null;

/**
 * Get the global progress service instance
 */
export function getProgressService(config?: Partial<ProgressServiceConfig>): ProgressService {
    if (!_progressService) {
        _progressService = new ProgressService(config);
    }
    return _progressService;
}

/**
 * Create progress event handler for VS Code status bar
 */
export function createStatusBarHandler(
    statusBarItem: vscode.StatusBarItem
): (event: ProgressEvent) => void {
    return (event: ProgressEvent) => {
        if (event.type === 'progress') {
            const update = event.update;
            const percent = Math.round(update.percent_complete);
            const cost = update.cost_so_far.toFixed(4);

            statusBarItem.text = `$(sync~spin) ${update.workflow}: ${percent}% ($${cost})`;
            statusBarItem.tooltip = `${update.message}\nStage: ${update.current_stage} (${update.stage_index + 1}/${update.total_stages})`;

            if (update.status === 'completed') {
                statusBarItem.text = `$(check) ${update.workflow}: Complete ($${cost})`;
                setTimeout(() => {
                    statusBarItem.text = '$(pulse) Empathy';
                }, 5000);
            } else if (update.status === 'failed') {
                statusBarItem.text = `$(error) ${update.workflow}: Failed`;
                statusBarItem.tooltip = update.error || 'Unknown error';
            }
        }
    };
}
