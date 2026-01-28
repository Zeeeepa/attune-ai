// Agent Coordination Dashboard - Frontend Logic

class Dashboard {
    constructor() {
        this.refreshInterval = 5000; // 5 seconds
        this.intervals = [];
        this.init();
    }

    init() {
        console.log('🚀 Dashboard initializing...');

        // Initial load
        this.loadAll();

        // Set up auto-refresh
        this.intervals.push(setInterval(() => this.loadAll(), this.refreshInterval));

        // Check health
        this.checkHealth();
        this.intervals.push(setInterval(() => this.checkHealth(), 10000));
    }

    async loadAll() {
        try {
            await Promise.all([
                this.loadAgents(),
                this.loadApprovals(),
                this.loadSignals(),
                this.loadEvents(),
                this.loadQualityMetrics(),
                this.loadUnderperforming()
            ]);
            this.updateLastUpdate();
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
        }
    }

    async checkHealth() {
        try {
            const response = await fetch('/api/health');
            const health = await response.json();

            const indicator = document.getElementById('health-indicator');
            const text = document.getElementById('health-text');

            if (health.status === 'healthy') {
                indicator.textContent = '🟢';
                text.textContent = 'System Healthy';
            } else if (health.status === 'degraded') {
                indicator.textContent = '🟡';
                text.textContent = 'System Degraded (No Redis)';
            } else {
                indicator.textContent = '🔴';
                text.textContent = 'System Unhealthy';
            }

            // Update stats
            document.getElementById('active-agents').textContent = health.active_agents || 0;
            document.getElementById('pending-approvals').textContent = health.pending_approvals || 0;

        } catch (error) {
            document.getElementById('health-indicator').textContent = '🔴';
            document.getElementById('health-text').textContent = 'Connection Failed';
        }
    }

    async loadAgents() {
        try {
            const response = await fetch('/api/agents');
            const agents = await response.json();

            const container = document.getElementById('agents-list');

            if (agents.length === 0) {
                container.innerHTML = '<div class="empty-state">No active agents</div>';
                return;
            }

            container.innerHTML = agents.map(agent => `
                <div class="agent-item ${agent.status}">
                    <div class="agent-header">
                        <span class="agent-id">${this.truncate(agent.agent_id, 40)}</span>
                        <span class="agent-status">${agent.status}</span>
                    </div>
                    <div class="agent-task">${agent.current_task || 'Idle'}</div>
                    <div class="agent-progress">
                        <div class="agent-progress-bar" style="width: ${agent.progress * 100}%"></div>
                    </div>
                </div>
            `).join('');

        } catch (error) {
            console.error('Failed to load agents:', error);
        }
    }

    async loadApprovals() {
        try {
            const response = await fetch('/api/approvals');
            const approvals = await response.json();

            const container = document.getElementById('approvals-list');

            if (approvals.length === 0) {
                container.innerHTML = '<div class="empty-state">No pending approvals</div>';
                return;
            }

            container.innerHTML = approvals.map(approval => `
                <div class="approval-item">
                    <div class="approval-header">
                        <span class="approval-type">${approval.approval_type}</span>
                    </div>
                    <div class="approval-context">
                        Agent: ${this.truncate(approval.agent_id, 30)}<br>
                        Context: ${JSON.stringify(approval.context)}
                    </div>
                    <div class="approval-actions">
                        <button class="btn btn-approve" onclick="dashboard.approveRequest('${approval.request_id}')">
                            ✓ Approve
                        </button>
                        <button class="btn btn-reject" onclick="dashboard.rejectRequest('${approval.request_id}')">
                            ✗ Reject
                        </button>
                    </div>
                </div>
            `).join('');

        } catch (error) {
            console.error('Failed to load approvals:', error);
        }
    }

    async approveRequest(requestId) {
        try {
            const response = await fetch(`/api/approvals/${requestId}/approve`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({reason: 'Approved via dashboard'})
            });

            if (response.ok) {
                console.log(`Approved ${requestId}`);
                this.loadApprovals(); // Refresh
            }
        } catch (error) {
            console.error('Failed to approve:', error);
        }
    }

    async rejectRequest(requestId) {
        try {
            const response = await fetch(`/api/approvals/${requestId}/reject`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({reason: 'Rejected via dashboard'})
            });

            if (response.ok) {
                console.log(`Rejected ${requestId}`);
                this.loadApprovals(); // Refresh
            }
        } catch (error) {
            console.error('Failed to reject:', error);
        }
    }

    async loadSignals() {
        try {
            const response = await fetch('/api/signals?limit=20');
            const signals = await response.json();

            const container = document.getElementById('signals-list');

            if (signals.length === 0) {
                container.innerHTML = '<div class="empty-state">No recent signals</div>';
                document.getElementById('recent-signals').textContent = '0';
                return;
            }

            document.getElementById('recent-signals').textContent = signals.length;

            container.innerHTML = signals.map(signal => `
                <div class="signal-item">
                    <div class="signal-header">
                        <span class="signal-type">${signal.signal_type}</span>
                        <span class="signal-time">${this.formatTime(signal.timestamp)}</span>
                    </div>
                    <div class="signal-route">
                        ${this.truncate(signal.source_agent, 20)} → ${this.truncate(signal.target_agent, 20)}
                    </div>
                </div>
            `).join('');

        } catch (error) {
            console.error('Failed to load signals:', error);
        }
    }

    async loadEvents() {
        try {
            const response = await fetch('/api/events?limit=30');
            const events = await response.json();

            const container = document.getElementById('events-list');

            if (events.length === 0) {
                container.innerHTML = '<div class="empty-state">No recent events</div>';
                document.getElementById('event-streams').textContent = '0';
                return;
            }

            document.getElementById('event-streams').textContent = events.length;

            container.innerHTML = events.map(event => `
                <div class="event-item">
                    <div class="event-header">
                        <span class="event-type">${event.event_type}</span>
                        <span class="event-time">${this.formatTime(event.timestamp)}</span>
                    </div>
                    <div style="font-size: 12px; color: #94a3b8; margin-top: 2px;">
                        Source: ${event.source}
                    </div>
                </div>
            `).join('');

        } catch (error) {
            console.error('Failed to load events:', error);
        }
    }

    async loadQualityMetrics() {
        try {
            const response = await fetch('/api/feedback/workflows');
            const metrics = await response.json();

            const container = document.getElementById('quality-metrics');

            if (metrics.length === 0) {
                container.innerHTML = '<div class="empty-state">No quality data</div>';
                return;
            }

            // Sort by quality (worst first)
            metrics.sort((a, b) => a.avg_quality - b.avg_quality);

            container.innerHTML = metrics.slice(0, 10).map(metric => {
                const qualityClass = metric.avg_quality >= 0.8 ? 'good' :
                                   metric.avg_quality >= 0.6 ? 'warning' : 'poor';
                const trendIcon = metric.trend > 0 ? '📈' : metric.trend < 0 ? '📉' : '➡️';

                return `
                    <div class="quality-item">
                        <div class="quality-header">
                            <span class="quality-name">
                                ${metric.workflow_name}/${metric.stage_name}
                            </span>
                            <span class="quality-score ${qualityClass}">
                                ${(metric.avg_quality * 100).toFixed(0)}%
                            </span>
                        </div>
                        <div class="quality-details">
                            Tier: ${metric.tier} | Samples: ${metric.sample_count} | ${trendIcon}
                        </div>
                    </div>
                `;
            }).join('');

        } catch (error) {
            console.error('Failed to load quality metrics:', error);
        }
    }

    async loadUnderperforming() {
        try {
            const response = await fetch('/api/feedback/underperforming?threshold=0.7');
            const stages = await response.json();

            const container = document.getElementById('underperforming-list');

            if (stages.length === 0) {
                container.innerHTML = '<div class="empty-state">All stages performing well ✓</div>';
                return;
            }

            container.innerHTML = stages.map(stage => `
                <div class="underperforming-item">
                    <div class="underperforming-header">
                        ${stage.workflow_name}/${stage.stage_name}
                    </div>
                    <div class="underperforming-details">
                        <div class="detail-item">
                            <span class="detail-label">Avg Quality:</span>
                            <span class="detail-value">${(stage.avg_quality * 100).toFixed(0)}%</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Samples:</span>
                            <span class="detail-value">${stage.sample_count}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Range:</span>
                            <span class="detail-value">
                                ${(stage.min_quality * 100).toFixed(0)}% - ${(stage.max_quality * 100).toFixed(0)}%
                            </span>
                        </div>
                    </div>
                </div>
            `).join('');

        } catch (error) {
            console.error('Failed to load underperforming stages:', error);
        }
    }

    formatTime(isoString) {
        try {
            const date = new Date(isoString);
            const now = new Date();
            const diff = (now - date) / 1000; // seconds

            if (diff < 60) return `${Math.floor(diff)}s ago`;
            if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
            if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
            return date.toLocaleDateString();
        } catch {
            return isoString;
        }
    }

    truncate(str, maxLen) {
        if (!str) return '';
        if (str.length <= maxLen) return str;
        return str.substring(0, maxLen - 3) + '...';
    }

    updateLastUpdate() {
        document.getElementById('last-update').textContent =
            `Last update: ${new Date().toLocaleTimeString()}`;
    }

    cleanup() {
        this.intervals.forEach(interval => clearInterval(interval));
    }
}

// Initialize dashboard when page loads
let dashboard;
document.addEventListener('DOMContentLoaded', () => {
    dashboard = new Dashboard();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (dashboard) dashboard.cleanup();
});
