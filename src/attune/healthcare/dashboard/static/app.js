/**
 * Clinical Decision Support Monitor - Frontend Application
 *
 * Vanilla JavaScript application for real-time patient monitoring,
 * CDS assessment submission, and audit trail review.
 *
 * No external dependencies required.
 *
 * Copyright 2026 Smart-AI-Memory
 * Licensed under Apache 2.0
 */

"use strict";

const App = {
    // ---------------------------------------------------------------
    // State
    // ---------------------------------------------------------------
    ws: null,
    patients: {},           // patient_id -> { lastAssessment, sensorData, ... }
    selectedPatient: null,
    alerts: [],             // active alert objects
    reconnectAttempts: 0,
    reconnectTimer: null,
    pingTimer: null,

    // ---------------------------------------------------------------
    // Constants
    // ---------------------------------------------------------------
    MAX_RECONNECT_DELAY: 30000,
    BASE_RECONNECT_DELAY: 1000,
    PING_INTERVAL: 30000,
    TOAST_DURATION: 5000,

    // ---------------------------------------------------------------
    // Initialization
    // ---------------------------------------------------------------

    /**
     * Bootstrap the application. Called on DOMContentLoaded.
     */
    init: function () {
        this.bindTabNavigation();
        this.bindAddPatient();
        this.bindAssessForm();
        this.bindDetailPanel();
        this.bindAlertBanner();
        this.bindAuditRefresh();
        this.bindThemeToggle();
        this.connectWebSocket();
        this.loadProtocols();
    },

    // ---------------------------------------------------------------
    // Tab Navigation
    // ---------------------------------------------------------------

    bindTabNavigation: function () {
        var tabBtns = document.querySelectorAll(".tab-btn");
        tabBtns.forEach(function (btn) {
            btn.addEventListener("click", function () {
                var tab = btn.getAttribute("data-tab");
                App.switchTab(tab);
            });
        });
    },

    switchTab: function (tabName) {
        document.querySelectorAll(".tab-btn").forEach(function (btn) {
            btn.classList.toggle("active", btn.getAttribute("data-tab") === tabName);
            btn.setAttribute("aria-selected",
                btn.getAttribute("data-tab") === tabName ? "true" : "false");
        });
        document.querySelectorAll(".tab-panel").forEach(function (panel) {
            panel.classList.toggle("active",
                panel.id === "panel" + tabName.charAt(0).toUpperCase() + tabName.slice(1));
        });

        if (tabName === "audit") {
            this.renderAuditLog();
        }
    },

    // ---------------------------------------------------------------
    // WebSocket
    // ---------------------------------------------------------------

    /**
     * Connect to the WebSocket endpoint with auto-reconnect.
     */
    connectWebSocket: function () {
        var self = this;
        this.setConnectionStatus("connecting");

        var protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
        var wsUrl = protocol + "//" + window.location.host + "/ws/monitor";

        try {
            this.ws = new WebSocket(wsUrl);
        } catch (e) {
            this.setConnectionStatus("disconnected");
            this.scheduleReconnect();
            return;
        }

        this.ws.onopen = function () {
            self.reconnectAttempts = 0;
            self.setConnectionStatus("connected");
            self.showNotification("Connected to monitor", "success");

            // Subscribe to all current patients
            var patientIds = Object.keys(self.patients);
            if (patientIds.length > 0) {
                self.ws.send(JSON.stringify({
                    action: "subscribe",
                    patient_ids: patientIds,
                }));
            }

            // Start ping timer
            self.startPingTimer();
        };

        this.ws.onmessage = function (event) {
            try {
                var message = JSON.parse(event.data);
                self.handleWebSocketMessage(message);
            } catch (e) {
                // Ignore non-JSON messages
            }
        };

        this.ws.onclose = function () {
            self.setConnectionStatus("disconnected");
            self.stopPingTimer();
            self.scheduleReconnect();
        };

        this.ws.onerror = function () {
            // onclose will fire after this, which handles reconnect
        };
    },

    handleWebSocketMessage: function (message) {
        var event = message.event;

        if (event === "pong") {
            // Heartbeat response, nothing to do
            return;
        }

        if (event === "subscribed") {
            return;
        }

        if (event === "new_assessment") {
            var patientId = message.patient_id;
            var data = message.data;
            if (patientId && data) {
                this.updatePatientData(patientId, data);
                this.showNotification(
                    "New assessment for " + patientId + ": " + (data.overall_risk || "unknown"),
                    data.overall_risk === "critical" || data.overall_risk === "high"
                        ? "warning" : "info"
                );
            }
            return;
        }

        if (event === "alert") {
            this.handleAlert(message);
            return;
        }
    },

    scheduleReconnect: function () {
        var self = this;
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
        }

        var delay = Math.min(
            this.BASE_RECONNECT_DELAY * Math.pow(2, this.reconnectAttempts),
            this.MAX_RECONNECT_DELAY
        );
        this.reconnectAttempts++;

        this.reconnectTimer = setTimeout(function () {
            self.connectWebSocket();
        }, delay);
    },

    startPingTimer: function () {
        var self = this;
        this.stopPingTimer();
        this.pingTimer = setInterval(function () {
            if (self.ws && self.ws.readyState === WebSocket.OPEN) {
                self.ws.send(JSON.stringify({ action: "ping" }));
            }
        }, this.PING_INTERVAL);
    },

    stopPingTimer: function () {
        if (this.pingTimer) {
            clearInterval(this.pingTimer);
            this.pingTimer = null;
        }
    },

    setConnectionStatus: function (status) {
        var el = document.getElementById("connectionStatus");
        if (!el) return;
        el.className = "connection-status " + status;
        var textEl = el.querySelector(".status-text");
        if (textEl) {
            var labels = {
                connected: "Connected",
                disconnected: "Disconnected",
                connecting: "Connecting...",
            };
            textEl.textContent = labels[status] || status;
        }
    },

    // ---------------------------------------------------------------
    // Patient Management
    // ---------------------------------------------------------------

    bindAddPatient: function () {
        var self = this;
        var btn = document.getElementById("btnAddPatient");
        var input = document.getElementById("inlinePatientId");

        if (btn) {
            btn.addEventListener("click", function () {
                var id = input.value.trim();
                if (id) {
                    self.addPatient(id);
                    input.value = "";
                }
            });
        }

        if (input) {
            input.addEventListener("keydown", function (e) {
                if (e.key === "Enter") {
                    e.preventDefault();
                    var id = input.value.trim();
                    if (id) {
                        self.addPatient(id);
                        input.value = "";
                    }
                }
            });
        }
    },

    /**
     * Add a patient to the monitoring grid and subscribe via WebSocket.
     */
    addPatient: function (patientId) {
        if (this.patients[patientId]) {
            this.showNotification("Patient " + patientId + " already being monitored", "warning");
            return;
        }

        this.patients[patientId] = {
            id: patientId,
            lastAssessment: null,
            sensorData: null,
            addedAt: new Date().toISOString(),
        };

        // Subscribe via WebSocket
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                action: "subscribe",
                patient_ids: [patientId],
            }));
        }

        this.renderPatientGrid();
        this.showNotification("Now monitoring " + patientId, "success");
    },

    /**
     * Remove a patient from monitoring.
     */
    removePatient: function (patientId) {
        delete this.patients[patientId];
        if (this.selectedPatient === patientId) {
            this.selectedPatient = null;
            document.getElementById("detailPanel").classList.add("hidden");
        }
        this.renderPatientGrid();
    },

    /**
     * Update patient data from an assessment response.
     */
    updatePatientData: function (patientId, data) {
        if (!this.patients[patientId]) {
            // Auto-add patient if we get data for an unknown one
            this.patients[patientId] = {
                id: patientId,
                lastAssessment: null,
                sensorData: null,
                addedAt: new Date().toISOString(),
            };
        }

        this.patients[patientId].lastAssessment = data;
        this.patients[patientId].lastUpdated = new Date().toISOString();

        this.renderPatientGrid();

        // Flash the card
        var card = document.querySelector("[data-patient-id='" + patientId + "']");
        if (card) {
            card.classList.add("new-data");
            setTimeout(function () {
                card.classList.remove("new-data");
            }, 600);
        }

        // Update detail panel if this patient is selected
        if (this.selectedPatient === patientId) {
            this.renderPatientDetail(patientId);
        }
    },

    // ---------------------------------------------------------------
    // Patient Grid Rendering
    // ---------------------------------------------------------------

    renderPatientGrid: function () {
        var grid = document.getElementById("patientGrid");
        if (!grid) return;

        var patientIds = Object.keys(this.patients);

        if (patientIds.length === 0) {
            grid.innerHTML =
                '<div class="empty-state">' +
                "<p>No patients being monitored.</p>" +
                "<p>Enter a Patient ID above to begin.</p>" +
                "</div>";
            return;
        }

        var html = "";
        for (var i = 0; i < patientIds.length; i++) {
            var pid = patientIds[i];
            var patient = this.patients[pid];
            var assessment = patient.lastAssessment;
            var risk = assessment ? assessment.overall_risk : "unknown";
            var riskClass = "risk-" + risk;
            var selectedClass = this.selectedPatient === pid ? " selected" : "";

            html += '<div class="patient-card ' + riskClass + selectedClass + '" ' +
                'data-patient-id="' + this.escapeHtml(pid) + '">';
            html += '<button class="card-remove" data-remove-id="' +
                this.escapeHtml(pid) + '" title="Remove patient">&times;</button>';
            html += '<div class="card-header">';
            html += '<span class="card-patient-id">' + this.escapeHtml(pid) + '</span>';
            html += '<span class="card-risk-badge ' + riskClass + '">' +
                this.escapeHtml(risk) + '</span>';
            html += '</div>';
            html += '<div class="card-body">';

            if (assessment) {
                html += "<p>Confidence: " +
                    (assessment.confidence * 100).toFixed(0) + "%</p>";
                html += "<p>Last: " + this.formatTimestamp(assessment.timestamp) + "</p>";

                // Show alerts if any
                if (assessment.alerts && assessment.alerts.length > 0) {
                    html += '<div class="card-alerts">';
                    var alertLimit = Math.min(assessment.alerts.length, 2);
                    for (var a = 0; a < alertLimit; a++) {
                        html += '<div class="card-alert-item">' +
                            this.escapeHtml(assessment.alerts[a]) + '</div>';
                    }
                    if (assessment.alerts.length > 2) {
                        html += '<div class="card-alert-item">+' +
                            (assessment.alerts.length - 2) + ' more</div>';
                    }
                    html += '</div>';
                }
            } else {
                html += "<p>No assessment data yet</p>";
                html += "<p>Added: " + this.formatTimestamp(patient.addedAt) + "</p>";
            }

            html += '</div>';
            html += '</div>';
        }

        grid.innerHTML = html;

        // Bind card click events
        var self = this;
        grid.querySelectorAll(".patient-card").forEach(function (card) {
            card.addEventListener("click", function (e) {
                // Ignore clicks on the remove button
                if (e.target.classList.contains("card-remove")) return;
                var pid = card.getAttribute("data-patient-id");
                self.selectPatient(pid);
            });
        });

        // Bind remove buttons
        grid.querySelectorAll(".card-remove").forEach(function (btn) {
            btn.addEventListener("click", function (e) {
                e.stopPropagation();
                var pid = btn.getAttribute("data-remove-id");
                self.removePatient(pid);
            });
        });
    },

    selectPatient: function (patientId) {
        this.selectedPatient = patientId;
        this.renderPatientGrid();
        this.renderPatientDetail(patientId);

        var panel = document.getElementById("detailPanel");
        if (panel) {
            panel.classList.remove("hidden");
        }
    },

    // ---------------------------------------------------------------
    // Patient Detail Panel
    // ---------------------------------------------------------------

    bindDetailPanel: function () {
        var self = this;
        var btnClose = document.getElementById("btnCloseDetail");
        if (btnClose) {
            btnClose.addEventListener("click", function () {
                self.selectedPatient = null;
                document.getElementById("detailPanel").classList.add("hidden");
                self.renderPatientGrid();
            });
        }

        var btnRun = document.getElementById("btnRunAssessment");
        if (btnRun) {
            btnRun.addEventListener("click", function () {
                if (self.selectedPatient) {
                    // Switch to assess tab with patient ID pre-filled
                    self.switchTab("assess");
                    var input = document.getElementById("assessPatientId");
                    if (input) {
                        input.value = self.selectedPatient;
                    }
                }
            });
        }

        var btnHistory = document.getElementById("btnViewHistory");
        if (btnHistory) {
            btnHistory.addEventListener("click", function () {
                if (self.selectedPatient) {
                    self.fetchPatientHistory(self.selectedPatient);
                }
            });
        }
    },

    renderPatientDetail: function (patientId) {
        var patient = this.patients[patientId];
        if (!patient) return;

        var assessment = patient.lastAssessment;

        // Patient ID header
        var idEl = document.getElementById("detailPatientId");
        if (idEl) idEl.textContent = "Patient: " + patientId;

        // Risk badge
        var riskBadge = document.getElementById("detailRiskBadge");
        if (riskBadge) {
            var risk = assessment ? assessment.overall_risk : "unknown";
            riskBadge.textContent = risk;
            riskBadge.className = "risk-badge-large risk-" + risk;
        }

        // Risk meta
        var confEl = document.getElementById("detailConfidence");
        if (confEl) {
            confEl.textContent = assessment
                ? (assessment.confidence * 100).toFixed(0) + "%"
                : "--";
        }
        var protoEl = document.getElementById("detailProtocol");
        if (protoEl) {
            protoEl.textContent = assessment && assessment.protocol_name
                ? assessment.protocol_name
                : "--";
        }
        var costEl = document.getElementById("detailCost");
        if (costEl) {
            costEl.textContent = assessment
                ? "$" + (assessment.cost || 0).toFixed(4)
                : "--";
        }

        // Vitals
        this.renderDetailVitals(patient);

        // ECG
        this.renderDetailECG(assessment);

        // Quality gates
        this.renderDetailQualityGates(assessment);

        // Clinical reasoning
        this.renderDetailReasoning(assessment);

        // Recommendations
        this.renderDetailList(
            "detailRecommendations",
            assessment ? assessment.recommendations : [],
            "No recommendations available"
        );

        // Alerts
        this.renderDetailList(
            "detailAlerts",
            assessment ? assessment.alerts : [],
            "No active alerts"
        );
    },

    renderDetailVitals: function (patient) {
        var container = document.getElementById("detailVitals");
        if (!container) return;

        var sensorData = null;
        if (patient.sensorData) {
            sensorData = patient.sensorData;
        } else if (patient.lastAssessment && patient.lastAssessment.sensor_data) {
            sensorData = patient.lastAssessment.sensor_data;
        }

        if (!sensorData) {
            container.innerHTML = '<span class="no-data">No vitals data available</span>';
            return;
        }

        var vitalDefs = [
            { key: "hr", label: "HR", unit: "bpm", low: 60, high: 100 },
            { key: "systolic_bp", label: "SBP", unit: "mmHg", low: 90, high: 140 },
            { key: "diastolic_bp", label: "DBP", unit: "mmHg", low: 60, high: 90 },
            { key: "respiratory_rate", label: "RR", unit: "/min", low: 12, high: 20 },
            { key: "o2_sat", label: "SpO2", unit: "%", low: 95, high: 100 },
            { key: "temp_f", label: "Temp", unit: "F", low: 97.0, high: 99.5 },
            { key: "pain_score", label: "Pain", unit: "/10", low: 0, high: 3 },
        ];

        var html = "";
        for (var i = 0; i < vitalDefs.length; i++) {
            var v = vitalDefs[i];
            var value = sensorData[v.key];
            if (value === undefined || value === null) continue;

            var abnormal = (typeof value === "number") &&
                (value < v.low || value > v.high);

            html += '<div class="vital-item">';
            html += '<span class="vital-label">' + v.label + '</span>';
            html += '<span class="vital-value' +
                (abnormal ? " abnormal" : "") + '">' +
                value + ' <small>' + v.unit + '</small></span>';
            html += '</div>';
        }

        container.innerHTML = html || '<span class="no-data">No vitals data available</span>';
    },

    renderDetailECG: function (assessment) {
        var noDataEl = document.getElementById("ecgNoData");
        var canvas = document.getElementById("ecgCanvas");

        if (!assessment || !assessment.ecg_analysis) {
            if (noDataEl) noDataEl.style.display = "flex";
            if (canvas) {
                var ctx = canvas.getContext("2d");
                ctx.clearRect(0, 0, canvas.width, canvas.height);
            }
            return;
        }

        if (noDataEl) noDataEl.style.display = "none";

        var ecg = assessment.ecg_analysis;
        if (ecg.waveform_data && ecg.waveform_data.length > 0) {
            this.drawECGWaveform("ecgCanvas", ecg.waveform_data);
        } else {
            // Draw a simulated waveform based on heart rate
            var simulatedData = this.generateSimulatedECG(ecg.heart_rate || 72);
            this.drawECGWaveform("ecgCanvas", simulatedData);
        }
    },

    renderDetailQualityGates: function (assessment) {
        var container = document.getElementById("detailQualityGates");
        if (!container) return;

        if (!assessment || !assessment.quality_gates ||
            assessment.quality_gates.length === 0) {
            container.innerHTML = '<span class="no-data">No quality gate data</span>';
            return;
        }

        var html = "";
        for (var i = 0; i < assessment.quality_gates.length; i++) {
            var gate = assessment.quality_gates[i];
            var passed = gate.passed;
            html += '<div class="quality-gate">';
            html += '<span class="gate-name">' + this.escapeHtml(gate.name) + '</span>';
            html += '<span class="gate-status ' + (passed ? "passed" : "failed") + '">';
            html += passed ? "PASS" : "FAIL";
            if (gate.actual !== undefined && gate.threshold !== undefined) {
                html += " (" + gate.actual + " / " + gate.threshold + ")";
            }
            html += '</span>';
            html += '</div>';
        }

        container.innerHTML = html;
    },

    renderDetailReasoning: function (assessment) {
        var container = document.getElementById("detailReasoning");
        if (!container) return;

        if (!assessment || !assessment.clinical_reasoning) {
            container.innerHTML =
                '<span class="no-data">No clinical reasoning available</span>';
            return;
        }

        var reasoning = assessment.clinical_reasoning;
        var html = "";

        // Narrative summary
        if (reasoning.narrative_summary) {
            html += '<div class="reasoning-narrative">' +
                this.escapeHtml(reasoning.narrative_summary) + '</div>';
        }

        // Differentials
        if (reasoning.differentials && reasoning.differentials.length > 0) {
            html += '<div class="reasoning-section-title">Differentials</div>';
            html += '<ul class="recommendations-list">';
            for (var i = 0; i < reasoning.differentials.length; i++) {
                html += '<li>' + this.escapeHtml(reasoning.differentials[i]) + '</li>';
            }
            html += '</ul>';
        }

        // Recommended workup
        if (reasoning.recommended_workup && reasoning.recommended_workup.length > 0) {
            html += '<div class="reasoning-section-title">Recommended Workup</div>';
            html += '<ul class="recommendations-list">';
            for (var j = 0; j < reasoning.recommended_workup.length; j++) {
                html += '<li>' +
                    this.escapeHtml(reasoning.recommended_workup[j]) + '</li>';
            }
            html += '</ul>';
        }

        // Confidence and risk
        if (reasoning.confidence !== undefined) {
            html += '<p style="margin-top:0.5rem;font-size:0.82rem;color:var(--color-text-secondary)">Reasoning confidence: ' +
                (reasoning.confidence * 100).toFixed(0) + '%</p>';
        }

        container.innerHTML = html ||
            '<span class="no-data">No clinical reasoning available</span>';
    },

    renderDetailList: function (elementId, items, emptyText) {
        var el = document.getElementById(elementId);
        if (!el) return;

        if (!items || items.length === 0) {
            el.innerHTML = '<li class="no-data">' + this.escapeHtml(emptyText) + '</li>';
            return;
        }

        var html = "";
        for (var i = 0; i < items.length; i++) {
            html += '<li>' + this.escapeHtml(items[i]) + '</li>';
        }
        el.innerHTML = html;
    },

    // ---------------------------------------------------------------
    // ECG Waveform Drawing
    // ---------------------------------------------------------------

    /**
     * Draw an ECG waveform on an HTML5 Canvas.
     *
     * @param {string} canvasId - The ID of the canvas element.
     * @param {number[]} waveformData - Array of amplitude values.
     */
    drawECGWaveform: function (canvasId, waveformData) {
        var canvas = document.getElementById(canvasId);
        if (!canvas || !waveformData || waveformData.length === 0) return;

        var ctx = canvas.getContext("2d");
        var w = canvas.width;
        var h = canvas.height;

        // Clear with dark background
        ctx.fillStyle = getComputedStyle(document.documentElement)
            .getPropertyValue("--ecg-bg").trim() || "#1a1a2e";
        ctx.fillRect(0, 0, w, h);

        // Draw grid lines
        ctx.strokeStyle = getComputedStyle(document.documentElement)
            .getPropertyValue("--ecg-grid").trim() || "#2a2a4a";
        ctx.lineWidth = 0.5;

        // Horizontal grid
        var gridSpacing = 25;
        for (var gy = gridSpacing; gy < h; gy += gridSpacing) {
            ctx.beginPath();
            ctx.moveTo(0, gy);
            ctx.lineTo(w, gy);
            ctx.stroke();
        }

        // Vertical grid
        for (var gx = gridSpacing; gx < w; gx += gridSpacing) {
            ctx.beginPath();
            ctx.moveTo(gx, 0);
            ctx.lineTo(gx, h);
            ctx.stroke();
        }

        // Find data range for scaling
        var minVal = waveformData[0];
        var maxVal = waveformData[0];
        for (var d = 1; d < waveformData.length; d++) {
            if (waveformData[d] < minVal) minVal = waveformData[d];
            if (waveformData[d] > maxVal) maxVal = waveformData[d];
        }

        var dataRange = maxVal - minVal;
        if (dataRange === 0) dataRange = 1;

        // Add padding to the range
        var padding = dataRange * 0.1;
        minVal -= padding;
        maxVal += padding;
        dataRange = maxVal - minVal;

        // Draw waveform
        ctx.strokeStyle = getComputedStyle(document.documentElement)
            .getPropertyValue("--ecg-line").trim() || "#27ae60";
        ctx.lineWidth = 2;
        ctx.lineJoin = "round";
        ctx.lineCap = "round";
        ctx.beginPath();

        var step = w / (waveformData.length - 1);
        for (var i = 0; i < waveformData.length; i++) {
            var x = i * step;
            var y = h - ((waveformData[i] - minVal) / dataRange) * h;

            if (i === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        }
        ctx.stroke();

        // Glow effect
        ctx.shadowColor = "#27ae60";
        ctx.shadowBlur = 4;
        ctx.stroke();
        ctx.shadowBlur = 0;
    },

    /**
     * Generate a simulated ECG waveform for display when real data is
     * unavailable but an ECG analysis result exists.
     *
     * @param {number} heartRate - Beats per minute.
     * @returns {number[]} Array of amplitude values.
     */
    generateSimulatedECG: function (heartRate) {
        var sampleRate = 250;
        var duration = 3; // seconds
        var totalSamples = sampleRate * duration;
        var data = [];

        var beatInterval = sampleRate * (60 / heartRate);

        for (var i = 0; i < totalSamples; i++) {
            var posInBeat = (i % beatInterval) / beatInterval;
            var value = 0;

            // P wave (0.0 - 0.15)
            if (posInBeat >= 0.0 && posInBeat < 0.15) {
                var pPhase = (posInBeat - 0.0) / 0.15;
                value = 0.15 * Math.sin(pPhase * Math.PI);
            }
            // QRS complex (0.16 - 0.24)
            else if (posInBeat >= 0.16 && posInBeat < 0.18) {
                value = -0.1;
            } else if (posInBeat >= 0.18 && posInBeat < 0.20) {
                value = 1.0; // R peak
            } else if (posInBeat >= 0.20 && posInBeat < 0.22) {
                value = -0.3; // S wave
            } else if (posInBeat >= 0.22 && posInBeat < 0.24) {
                value = 0;
            }
            // T wave (0.30 - 0.48)
            else if (posInBeat >= 0.30 && posInBeat < 0.48) {
                var tPhase = (posInBeat - 0.30) / 0.18;
                value = 0.25 * Math.sin(tPhase * Math.PI);
            }

            // Add small noise for realism
            value += (Math.random() - 0.5) * 0.02;

            data.push(value);
        }

        return data;
    },

    // ---------------------------------------------------------------
    // Assessment Form
    // ---------------------------------------------------------------

    bindAssessForm: function () {
        var self = this;
        var form = document.getElementById("assessForm");
        if (!form) return;

        form.addEventListener("submit", function (e) {
            e.preventDefault();
            self.submitAssessment();
        });
    },

    /**
     * Gather form values and POST to /api/patients/{id}/assess.
     */
    submitAssessment: async function () {
        var patientId = document.getElementById("assessPatientId").value.trim();
        var protocol = document.getElementById("assessProtocol").value;

        if (!patientId) {
            this.showNotification("Patient ID is required", "error");
            return;
        }
        if (!protocol) {
            this.showNotification("Please select a protocol", "error");
            return;
        }

        // Build sensor_data
        var sensorData = {};
        var fields = [
            { id: "vitalHR", key: "hr" },
            { id: "vitalSBP", key: "systolic_bp" },
            { id: "vitalDBP", key: "diastolic_bp" },
            { id: "vitalRR", key: "respiratory_rate" },
            { id: "vitalSpO2", key: "o2_sat" },
            { id: "vitalTemp", key: "temp_f" },
            { id: "vitalPain", key: "pain_score" },
        ];

        for (var i = 0; i < fields.length; i++) {
            var el = document.getElementById(fields[i].id);
            if (el && el.value !== "") {
                sensorData[fields[i].key] = parseFloat(el.value);
            }
        }

        // Build ecg_metrics (optional)
        var ecgMetrics = null;
        var ecgHR = document.getElementById("ecgHR");
        var ecgHRV = document.getElementById("ecgHRV");
        var ecgRhythm = document.getElementById("ecgRhythm");

        if ((ecgHR && ecgHR.value) || (ecgHRV && ecgHRV.value) ||
            (ecgRhythm && ecgRhythm.value)) {
            ecgMetrics = {};
            if (ecgHR && ecgHR.value) ecgMetrics.heart_rate = parseFloat(ecgHR.value);
            if (ecgHRV && ecgHRV.value) ecgMetrics.hrv_sdnn = parseFloat(ecgHRV.value);
            if (ecgRhythm && ecgRhythm.value) {
                ecgMetrics.rhythm_classification = ecgRhythm.value;
            }
        }

        // Build request body
        var body = {
            sensor_data: sensorData,
            protocol_name: protocol,
        };
        if (ecgMetrics) body.ecg_metrics = ecgMetrics;

        // Submit
        var resultDiv = document.getElementById("assessResult");
        var resultContent = document.getElementById("assessResultContent");

        try {
            this.showNotification("Running assessment...", "info");

            var response = await fetch(
                "/api/patients/" + encodeURIComponent(patientId) + "/assess",
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(body),
                }
            );

            if (!response.ok) {
                var errorData = await response.json().catch(function () {
                    return { detail: "Unknown error" };
                });
                throw new Error(errorData.detail || "Assessment failed: " + response.status);
            }

            var data = await response.json();

            // Store sensor data on the patient
            if (!this.patients[patientId]) {
                this.addPatient(patientId);
            }
            this.patients[patientId].sensorData = sensorData;
            this.updatePatientData(patientId, data);

            // Display result
            if (resultDiv && resultContent) {
                resultDiv.classList.remove("hidden");
                resultContent.innerHTML = this.renderAssessmentResult(data);
            }

            this.showNotification(
                "Assessment complete: " + data.overall_risk,
                data.overall_risk === "critical" || data.overall_risk === "high"
                    ? "warning" : "success"
            );
        } catch (err) {
            this.showNotification("Assessment error: " + err.message, "error");
            if (resultDiv && resultContent) {
                resultDiv.classList.remove("hidden");
                resultContent.innerHTML =
                    '<div class="result-risk-banner" style="background:var(--risk-critical)">' +
                    'Error: ' + this.escapeHtml(err.message) + '</div>';
            }
        }
    },

    renderAssessmentResult: function (data) {
        var risk = data.overall_risk || "unknown";
        var html = "";

        html += '<div class="result-risk-banner" style="background:' +
            this.getRiskColor(risk) + '">' +
            this.escapeHtml(risk) + ' RISK - Confidence: ' +
            (data.confidence * 100).toFixed(0) + '%</div>';

        // Alerts
        if (data.alerts && data.alerts.length > 0) {
            html += '<h4 style="margin-top:0.75rem">Alerts</h4>';
            html += '<ul class="alerts-list">';
            for (var i = 0; i < data.alerts.length; i++) {
                html += '<li>' + this.escapeHtml(data.alerts[i]) + '</li>';
            }
            html += '</ul>';
        }

        // Recommendations
        if (data.recommendations && data.recommendations.length > 0) {
            html += '<h4 style="margin-top:0.75rem">Recommendations</h4>';
            html += '<ul class="recommendations-list">';
            for (var j = 0; j < data.recommendations.length; j++) {
                html += '<li>' + this.escapeHtml(data.recommendations[j]) + '</li>';
            }
            html += '</ul>';
        }

        // Clinical reasoning
        if (data.clinical_reasoning && data.clinical_reasoning.narrative_summary) {
            html += '<h4 style="margin-top:0.75rem">Clinical Reasoning</h4>';
            html += '<div class="reasoning-narrative">' +
                this.escapeHtml(data.clinical_reasoning.narrative_summary) + '</div>';
        }

        // Quality gates
        if (data.quality_gates && data.quality_gates.length > 0) {
            html += '<h4 style="margin-top:0.75rem">Quality Gates</h4>';
            html += '<div class="quality-gates">';
            for (var k = 0; k < data.quality_gates.length; k++) {
                var gate = data.quality_gates[k];
                html += '<div class="quality-gate">';
                html += '<span class="gate-name">' + this.escapeHtml(gate.name) + '</span>';
                html += '<span class="gate-status ' +
                    (gate.passed ? "passed" : "failed") + '">' +
                    (gate.passed ? "PASS" : "FAIL") + '</span>';
                html += '</div>';
            }
            html += '</div>';
        }

        // Cost
        html += '<p style="margin-top:0.75rem;font-size:0.82rem;color:var(--color-text-secondary)">' +
            'Cost: $' + (data.cost || 0).toFixed(4) +
            ' | Timestamp: ' + this.formatTimestamp(data.timestamp) + '</p>';

        return html;
    },

    // ---------------------------------------------------------------
    // Alert Handling
    // ---------------------------------------------------------------

    bindAlertBanner: function () {
        var self = this;
        var btn = document.getElementById("btnDismissAlerts");
        if (btn) {
            btn.addEventListener("click", function () {
                self.dismissAlerts();
            });
        }
    },

    handleAlert: function (alertData) {
        this.alerts.push({
            patient_id: alertData.patient_id,
            risk: alertData.risk,
            alerts: alertData.alerts || [],
            timestamp: new Date().toISOString(),
        });
        this.renderAlerts();

        // Try browser notification
        this.sendBrowserNotification(
            "CDS Alert: " + alertData.patient_id,
            (alertData.risk || "unknown").toUpperCase() + " risk - " +
            (alertData.alerts && alertData.alerts.length > 0
                ? alertData.alerts[0]
                : "Check patient immediately")
        );
    },

    renderAlerts: function () {
        var banner = document.getElementById("alertBanner");
        var messagesEl = document.getElementById("alertMessages");
        if (!banner || !messagesEl) return;

        if (this.alerts.length === 0) {
            banner.classList.add("hidden");
            return;
        }

        banner.classList.remove("hidden");
        banner.classList.add("alert-pulsing");

        var html = "";
        // Show most recent alerts (up to 5)
        var recentAlerts = this.alerts.slice(-5);
        for (var i = recentAlerts.length - 1; i >= 0; i--) {
            var alert = recentAlerts[i];
            html += '<div class="alert-message-item">';
            html += '<strong>' + this.escapeHtml(alert.patient_id) + '</strong>';
            html += ' (' + this.escapeHtml(alert.risk) + ')';
            if (alert.alerts && alert.alerts.length > 0) {
                html += ': ' + this.escapeHtml(alert.alerts[0]);
            }
            html += '</div>';
        }

        if (this.alerts.length > 5) {
            html += '<div class="alert-message-item">+' +
                (this.alerts.length - 5) + ' more alerts</div>';
        }

        messagesEl.innerHTML = html;
    },

    dismissAlerts: function () {
        this.alerts = [];
        var banner = document.getElementById("alertBanner");
        if (banner) {
            banner.classList.add("hidden");
            banner.classList.remove("alert-pulsing");
        }
    },

    sendBrowserNotification: function (title, body) {
        if (!("Notification" in window)) return;

        if (Notification.permission === "granted") {
            new Notification(title, { body: body, icon: "" });
        } else if (Notification.permission !== "denied") {
            Notification.requestPermission().then(function (permission) {
                if (permission === "granted") {
                    new Notification(title, { body: body, icon: "" });
                }
            });
        }
    },

    // ---------------------------------------------------------------
    // Audit Log
    // ---------------------------------------------------------------

    bindAuditRefresh: function () {
        var self = this;
        var btn = document.getElementById("btnRefreshAudit");
        if (btn) {
            btn.addEventListener("click", function () {
                self.renderAuditLog();
            });
        }
    },

    renderAuditLog: async function () {
        var tbody = document.getElementById("auditTableBody");
        if (!tbody) return;

        tbody.innerHTML = '<tr><td colspan="7" class="no-data">Loading...</td></tr>';

        try {
            var response = await fetch("/api/audit?limit=50&offset=0");
            if (!response.ok) {
                throw new Error("Failed to fetch audit log: " + response.status);
            }
            var entries = await response.json();

            if (!entries || entries.length === 0) {
                tbody.innerHTML =
                    '<tr><td colspan="7" class="no-data">No audit entries yet.</td></tr>';
                return;
            }

            var html = "";
            for (var i = 0; i < entries.length; i++) {
                var entry = entries[i];
                var risk = entry.overall_risk || entry.risk || "unknown";
                html += '<tr>';
                html += '<td>' + this.formatTimestamp(entry.timestamp) + '</td>';
                html += '<td><code>' +
                    this.escapeHtml((entry.decision_id || "").substring(0, 8)) +
                    '...</code></td>';
                html += '<td><code>' +
                    this.escapeHtml((entry.patient_id_hash || entry.patient_id || "").substring(0, 12)) +
                    '...</code></td>';
                html += '<td class="audit-risk-cell" style="color:' +
                    this.getRiskColor(risk) + '">' +
                    this.escapeHtml(risk) + '</td>';
                html += '<td>' +
                    (entry.confidence !== undefined
                        ? (entry.confidence * 100).toFixed(0) + '%' : '--') + '</td>';
                html += '<td>$' + (entry.cost || 0).toFixed(4) + '</td>';
                html += '<td>';
                if (entry.decision_id) {
                    html += '<button class="btn btn-sm" onclick="App.viewDecision(\'' +
                        this.escapeHtml(entry.decision_id) + '\')">View</button>';
                    html += ' <button class="btn btn-sm" onclick="App.viewFHIR(\'' +
                        this.escapeHtml(entry.decision_id) + '\')">FHIR</button>';
                }
                html += '</td>';
                html += '</tr>';
            }
            tbody.innerHTML = html;
        } catch (err) {
            tbody.innerHTML = '<tr><td colspan="7" class="no-data">Error: ' +
                this.escapeHtml(err.message) + '</td></tr>';
        }
    },

    /**
     * Fetch and display a single decision in a toast notification.
     */
    viewDecision: async function (decisionId) {
        try {
            var response = await fetch("/api/decisions/" + encodeURIComponent(decisionId));
            if (!response.ok) throw new Error("Not found");
            var data = await response.json();
            this.showNotification(
                "Decision " + decisionId.substring(0, 8) + ": " +
                JSON.stringify(data).substring(0, 200) + "...",
                "info"
            );
        } catch (err) {
            this.showNotification("Failed to load decision: " + err.message, "error");
        }
    },

    /**
     * Fetch and display a FHIR Bundle in a toast notification.
     */
    viewFHIR: async function (decisionId) {
        try {
            var response = await fetch(
                "/api/decisions/" + encodeURIComponent(decisionId) + "/fhir"
            );
            if (!response.ok) throw new Error("Not found");
            var bundle = await response.json();
            this.showNotification(
                "FHIR Bundle (" + bundle.type + "): " +
                (bundle.entry ? bundle.entry.length : 0) + " entries",
                "info"
            );
        } catch (err) {
            this.showNotification("Failed to load FHIR bundle: " + err.message, "error");
        }
    },

    /**
     * Fetch patient assessment history.
     */
    fetchPatientHistory: async function (patientId) {
        try {
            var response = await fetch(
                "/api/patients/" + encodeURIComponent(patientId) + "/history?limit=10"
            );
            if (!response.ok) throw new Error("Failed to fetch history");
            var history = await response.json();

            if (history.length === 0) {
                this.showNotification("No history found for " + patientId, "info");
                return;
            }

            this.showNotification(
                patientId + " has " + history.length + " past assessments. " +
                "Most recent risk: " + (history[0].overall_risk || "unknown"),
                "info"
            );
        } catch (err) {
            this.showNotification(
                "Failed to fetch history: " + err.message, "error"
            );
        }
    },

    // ---------------------------------------------------------------
    // Protocols
    // ---------------------------------------------------------------

    loadProtocols: async function () {
        try {
            var response = await fetch("/api/protocols");
            if (!response.ok) return;
            var protocols = await response.json();

            var select = document.getElementById("assessProtocol");
            if (!select) return;

            // Keep the placeholder option
            select.innerHTML = '<option value="">Select a protocol...</option>';
            for (var i = 0; i < protocols.length; i++) {
                var p = protocols[i];
                var option = document.createElement("option");
                option.value = p.name;
                option.textContent = p.display_name;
                option.title = p.description;
                select.appendChild(option);
            }
        } catch (e) {
            // Protocols will use the hardcoded options in HTML
        }
    },

    // ---------------------------------------------------------------
    // Theme Toggle
    // ---------------------------------------------------------------

    bindThemeToggle: function () {
        var btn = document.getElementById("btnToggleTheme");
        if (!btn) return;

        // Check for saved preference
        var saved = localStorage.getItem("cds-theme");
        if (saved === "dark") {
            document.body.classList.add("dark-mode");
        }

        btn.addEventListener("click", function () {
            document.body.classList.toggle("dark-mode");
            var isDark = document.body.classList.contains("dark-mode");
            localStorage.setItem("cds-theme", isDark ? "dark" : "light");
        });
    },

    // ---------------------------------------------------------------
    // Utility Functions
    // ---------------------------------------------------------------

    /**
     * Get the CSS color for a risk level.
     *
     * @param {string} risk - Risk level (low, moderate, high, critical).
     * @returns {string} CSS color value.
     */
    getRiskColor: function (risk) {
        var colors = {
            low: "var(--risk-low)",
            moderate: "var(--risk-moderate)",
            high: "var(--risk-high)",
            critical: "var(--risk-critical)",
        };
        return colors[risk] || "var(--risk-unknown)";
    },

    /**
     * Format an ISO timestamp for display.
     *
     * @param {string} iso - ISO 8601 timestamp string.
     * @returns {string} Formatted time string.
     */
    formatTimestamp: function (iso) {
        if (!iso) return "--";
        try {
            var date = new Date(iso);
            if (isNaN(date.getTime())) return iso;

            var now = new Date();
            var diffMs = now - date;
            var diffSec = Math.floor(diffMs / 1000);

            if (diffSec < 60) return diffSec + "s ago";
            if (diffSec < 3600) return Math.floor(diffSec / 60) + "m ago";
            if (diffSec < 86400) return Math.floor(diffSec / 3600) + "h ago";

            // Older than a day: show date + time
            return date.toLocaleDateString() + " " +
                date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
        } catch (e) {
            return iso;
        }
    },

    /**
     * Show a toast notification.
     *
     * @param {string} message - Notification message text.
     * @param {string} type - Toast type: success, warning, error, info.
     */
    showNotification: function (message, type) {
        var container = document.getElementById("toastContainer");
        if (!container) return;

        type = type || "info";

        var toast = document.createElement("div");
        toast.className = "toast toast-" + type;
        toast.innerHTML =
            '<div class="toast-body">' + this.escapeHtml(message) + '</div>';

        container.appendChild(toast);

        // Auto-remove after duration
        var self = this;
        setTimeout(function () {
            if (toast.parentNode) {
                toast.style.opacity = "0";
                toast.style.transition = "opacity 0.3s";
                setTimeout(function () {
                    if (toast.parentNode) {
                        container.removeChild(toast);
                    }
                }, 300);
            }
        }, self.TOAST_DURATION);
    },

    /**
     * Escape HTML special characters to prevent XSS.
     *
     * @param {string} text - Raw text to escape.
     * @returns {string} HTML-safe string.
     */
    escapeHtml: function (text) {
        if (text === null || text === undefined) return "";
        var str = String(text);
        var map = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#039;",
        };
        return str.replace(/[&<>"']/g, function (c) {
            return map[c];
        });
    },
};

// ===================================================================
// Bootstrap
// ===================================================================
document.addEventListener("DOMContentLoaded", function () {
    App.init();
});
