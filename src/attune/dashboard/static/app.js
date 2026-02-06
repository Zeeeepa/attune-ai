// Agent Coordination Dashboard - Frontend Logic

class Dashboard {
    constructor() {
        this.refreshInterval = 5000; // 5 seconds
        this.intervals = [];
        this.agentDisplayNames = {}; // Map of agent_id -> display_name
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
                text.textContent = 'Redis Requires Enabling';
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

    // DOM element builder: el('div', {className: 'foo'}, [children...])
    el(tag, attrs, children) {
        const elem = document.createElement(tag);
        if (attrs) {
            for (const [key, value] of Object.entries(attrs)) {
                if (key === 'className') elem.className = value;
                else if (key === 'textContent') elem.textContent = value;
                else if (key === 'style') elem.setAttribute('style', value);
                else if (key.startsWith('on')) elem.addEventListener(key.slice(2), value);
                else elem.setAttribute(key, value);
            }
        }
        if (children) {
            for (const child of children) {
                if (typeof child === 'string') {
                    elem.appendChild(document.createTextNode(child));
                } else if (child) {
                    elem.appendChild(child);
                }
            }
        }
        return elem;
    }

    renderList(container, items, renderFn) {
        container.textContent = '';
        for (const item of items) {
            container.appendChild(renderFn(item));
        }
    }

    async loadAgents() {
        try {
            const response = await fetch('/api/agents');
            const agents = await response.json();

            console.log('DEBUG: Loaded agents:', agents);

            const container = document.getElementById('agents-list');

            if (agents.length === 0) {
                this.setEmptyState(container, 'No active agents');
                return;
            }

            // Build display name lookup map
            this.agentDisplayNames = {};
            agents.forEach(agent => {
                this.agentDisplayNames[agent.agent_id] = agent.display_name || agent.agent_id;
            });

            this.renderList(container, agents, (agent) => {
                const displayValue = agent.display_name || agent.agent_id;
                console.log(`DEBUG: Agent ${agent.agent_id} - display_name: "${agent.display_name}", showing: "${displayValue}"`);

                return this.el('div', {className: `agent-item ${agent.status}`}, [
                    this.el('div', {className: 'agent-header'}, [
                        this.el('span', {className: 'agent-id', textContent: this.truncate(displayValue, 40)}),
                        this.el('span', {className: 'agent-status', textContent: agent.status})
                    ]),
                    this.el('div', {className: 'agent-task', textContent: agent.current_task || 'Idle'}),
                    this.el('div', {className: 'agent-progress'}, [
                        this.el('div', {className: 'agent-progress-bar', style: `width: ${agent.progress * 100}%`})
                    ])
                ]);
            });

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
                this.setEmptyState(container, 'No pending approvals');
                return;
            }

            this.renderList(container, approvals, (approval) => {
                const approveBtn = this.el('button', {
                    className: 'btn btn-approve',
                    textContent: '\u2713 Approve',
                    onclick: () => this.approveRequest(approval.request_id)
                });
                const rejectBtn = this.el('button', {
                    className: 'btn btn-reject',
                    textContent: '\u2717 Reject',
                    onclick: () => this.rejectRequest(approval.request_id)
                });

                const contextDiv = this.el('div', {className: 'approval-context'});
                contextDiv.appendChild(document.createTextNode('Agent: ' + this.truncate(approval.agent_id, 30)));
                contextDiv.appendChild(this.el('br'));
                contextDiv.appendChild(document.createTextNode('Context: ' + JSON.stringify(approval.context)));

                return this.el('div', {className: 'approval-item'}, [
                    this.el('div', {className: 'approval-header'}, [
                        this.el('span', {className: 'approval-type', textContent: approval.approval_type})
                    ]),
                    contextDiv,
                    this.el('div', {className: 'approval-actions'}, [approveBtn, rejectBtn])
                ]);
            });

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
                this.setEmptyState(container, 'No recent signals');
                document.getElementById('recent-signals').textContent = '0';
                return;
            }

            document.getElementById('recent-signals').textContent = signals.length;

            this.renderList(container, signals, (signal) => {
                const sourceDisplay = this.agentDisplayNames[signal.source_agent] || signal.source_agent;
                const targetDisplay = this.agentDisplayNames[signal.target_agent] || signal.target_agent;

                return this.el('div', {className: 'signal-item'}, [
                    this.el('div', {className: 'signal-header'}, [
                        this.el('span', {className: 'signal-type', textContent: signal.signal_type}),
                        this.el('span', {className: 'signal-time', textContent: this.formatTime(signal.timestamp)})
                    ]),
                    this.el('div', {className: 'signal-route', textContent: `${this.truncate(sourceDisplay, 20)} \u2192 ${this.truncate(targetDisplay, 20)}`})
                ]);
            });

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
                this.setEmptyState(container, 'No recent events');
                document.getElementById('event-streams').textContent = '0';
                return;
            }

            document.getElementById('event-streams').textContent = events.length;

            this.renderList(container, events, (event) => {
                const sourceDisplay = this.agentDisplayNames[event.source] || event.source;

                return this.el('div', {className: 'event-item'}, [
                    this.el('div', {className: 'event-header'}, [
                        this.el('span', {className: 'event-type', textContent: event.event_type}),
                        this.el('span', {className: 'event-time', textContent: this.formatTime(event.timestamp)})
                    ]),
                    this.el('div', {style: 'font-size: 12px; color: #94a3b8; margin-top: 2px;', textContent: `Source Agent: ${sourceDisplay}`})
                ]);
            });

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
                this.setEmptyState(container, 'No quality data');
                return;
            }

            // Sort by quality (worst first)
            metrics.sort((a, b) => a.avg_quality - b.avg_quality);

            this.renderList(container, metrics.slice(0, 10), (metric) => {
                const qualityClass = metric.avg_quality >= 0.8 ? 'good' :
                                   metric.avg_quality >= 0.6 ? 'warning' : 'poor';

                let trendIcon, trendClass, trendLabel;
                if (metric.trend > 0.01) {
                    trendIcon = '\u25B2';
                    trendClass = 'trend-up';
                    trendLabel = 'Improving';
                } else if (metric.trend < -0.01) {
                    trendIcon = '\u25BC';
                    trendClass = 'trend-down';
                    trendLabel = 'Declining';
                } else {
                    trendIcon = '\u2501';
                    trendClass = 'trend-flat';
                    trendLabel = 'Stable';
                }

                return this.el('div', {className: 'quality-item'}, [
                    this.el('div', {className: 'quality-header'}, [
                        this.el('span', {className: 'quality-name', textContent: `${metric.workflow_name}/${metric.stage_name}`}),
                        this.el('span', {className: `quality-score ${qualityClass}`, textContent: `${(metric.avg_quality * 100).toFixed(0)}%`})
                    ]),
                    this.el('div', {className: 'quality-details'}, [
                        this.el('span', {className: 'detail-tier', textContent: `Tier: ${metric.tier}`}),
                        this.el('span', {className: 'detail-samples', textContent: `Samples: ${metric.sample_count}`}),
                        this.el('span', {className: `trend-indicator ${trendClass}`}, [
                            this.el('span', {className: 'trend-icon', textContent: trendIcon}),
                            this.el('span', {className: 'trend-label', textContent: trendLabel})
                        ])
                    ])
                ]);
            });

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
                this.setEmptyState(container, 'All tiers performing well \u2713');
                return;
            }

            this.renderList(container, stages, (stage) => {
                const [stageName, tier] = stage.stage_name.split('/');

                const headerChildren = [
                    this.el('span', {className: 'workflow-name', textContent: stage.workflow_name}),
                    this.el('span', {className: 'stage-separator', textContent: '/'}),
                    this.el('span', {className: 'stage-name', textContent: stageName})
                ];
                if (tier) {
                    headerChildren.push(
                        this.el('span', {className: `tier-badge tier-${tier}`, textContent: tier.toUpperCase()})
                    );
                }

                return this.el('div', {className: 'underperforming-item'}, [
                    this.el('div', {className: 'underperforming-header'}, headerChildren),
                    this.el('div', {className: 'underperforming-details'}, [
                        this.el('div', {className: 'detail-item'}, [
                            this.el('span', {className: 'detail-label', textContent: 'Avg Quality:'}),
                            this.el('span', {className: 'detail-value quality-poor', textContent: `${(stage.avg_quality * 100).toFixed(0)}%`})
                        ]),
                        this.el('div', {className: 'detail-item'}, [
                            this.el('span', {className: 'detail-label', textContent: 'Samples:'}),
                            this.el('span', {className: 'detail-value', textContent: `${stage.sample_count}`})
                        ]),
                        this.el('div', {className: 'detail-item'}, [
                            this.el('span', {className: 'detail-label', textContent: 'Range:'}),
                            this.el('span', {className: 'detail-value', textContent: `${(stage.min_quality * 100).toFixed(0)}% - ${(stage.max_quality * 100).toFixed(0)}%`})
                        ])
                    ])
                ]);
            });

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

    setEmptyState(container, message) {
        container.textContent = '';
        const div = document.createElement('div');
        div.className = 'empty-state';
        div.textContent = message;
        container.appendChild(div);
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

// Help Panel functionality
document.addEventListener('DOMContentLoaded', () => {
    const helpButton = document.getElementById('help-button');
    const closeHelp = document.getElementById('close-help');
    const helpPanel = document.getElementById('help-panel');
    const helpOverlay = document.getElementById('help-overlay');
    const helpToggles = document.querySelectorAll('.help-toggle');

    // Open help panel
    helpButton.addEventListener('click', () => {
        helpPanel.classList.add('active');
        helpOverlay.classList.add('active');
    });

    // Close help panel
    const closeHelpPanel = () => {
        helpPanel.classList.remove('active');
        helpOverlay.classList.remove('active');
    };

    closeHelp.addEventListener('click', closeHelpPanel);
    helpOverlay.addEventListener('click', closeHelpPanel);

    // Accordion functionality
    helpToggles.forEach(toggle => {
        toggle.addEventListener('click', () => {
            const section = toggle.parentElement;
            const isActive = section.classList.contains('active');

            // Close all sections
            document.querySelectorAll('.help-section').forEach(s => {
                s.classList.remove('active');
            });

            // Toggle current section
            if (!isActive) {
                section.classList.add('active');
            }
        });
    });
});
