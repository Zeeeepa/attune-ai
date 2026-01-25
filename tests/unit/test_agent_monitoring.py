"""Tests for empathy_os.agent_monitoring"""

from datetime import datetime

from empathy_os.agent_monitoring import AgentMetrics, AgentMonitor, TeamMetrics
from empathy_os.pattern_library import Pattern, PatternLibrary


class TestAgentMetrics:
    """Tests for AgentMetrics class."""

    def test_initialization(self):
        """Test AgentMetrics initialization with defaults."""
        metrics = AgentMetrics(agent_id="test_agent")

        assert metrics.agent_id == "test_agent"
        assert metrics.total_interactions == 0
        assert metrics.total_response_time_ms == 0.0
        assert metrics.patterns_discovered == 0
        assert metrics.patterns_used == 0
        assert metrics.successful_pattern_uses == 0
        assert metrics.failed_pattern_uses == 0
        assert isinstance(metrics.first_seen, datetime)
        assert isinstance(metrics.last_active, datetime)

    def test_avg_response_time_ms_with_data(self):
        """Test average response time calculation."""
        metrics = AgentMetrics(agent_id="test_agent")
        metrics.total_interactions = 4
        metrics.total_response_time_ms = 800.0  # 4 interactions * 200ms avg

        assert metrics.avg_response_time_ms == 200.0

    def test_avg_response_time_ms_no_interactions(self):
        """Test average response time with zero interactions."""
        metrics = AgentMetrics(agent_id="test_agent")

        assert metrics.avg_response_time_ms == 0.0

    def test_success_rate_with_data(self):
        """Test success rate calculation."""
        metrics = AgentMetrics(agent_id="test_agent")
        metrics.successful_pattern_uses = 8
        metrics.failed_pattern_uses = 2

        # 8 successes / 10 total = 0.8
        assert metrics.success_rate == 0.8

    def test_success_rate_no_pattern_uses(self):
        """Test success rate with no pattern uses."""
        metrics = AgentMetrics(agent_id="test_agent")

        assert metrics.success_rate == 0.0

    def test_success_rate_all_failures(self):
        """Test success rate with all failures."""
        metrics = AgentMetrics(agent_id="test_agent")
        metrics.successful_pattern_uses = 0
        metrics.failed_pattern_uses = 5

        assert metrics.success_rate == 0.0

    def test_pattern_contribution_rate(self):
        """Test pattern contribution rate calculation."""
        metrics = AgentMetrics(agent_id="test_agent")
        metrics.total_interactions = 100
        metrics.patterns_discovered = 10

        # 10 patterns / 100 interactions = 0.1
        assert metrics.pattern_contribution_rate == 0.1

    def test_pattern_contribution_rate_no_interactions(self):
        """Test pattern contribution rate with zero interactions."""
        metrics = AgentMetrics(agent_id="test_agent")
        metrics.patterns_discovered = 5

        assert metrics.pattern_contribution_rate == 0.0


class TestTeamMetrics:
    """Tests for TeamMetrics class."""

    def test_initialization(self):
        """Test TeamMetrics initialization with defaults."""
        metrics = TeamMetrics()

        assert metrics.active_agents == 0
        assert metrics.total_agents == 0
        assert metrics.shared_patterns == 0
        assert metrics.total_interactions == 0
        assert metrics.pattern_reuse_count == 0
        assert metrics.cross_agent_reuses == 0

    def test_pattern_reuse_rate_with_data(self):
        """Test pattern reuse rate calculation."""
        metrics = TeamMetrics()
        metrics.shared_patterns = 10
        metrics.pattern_reuse_count = 30

        # 30 reuses / 10 patterns = 3.0 (each pattern used 3 times on avg)
        assert metrics.pattern_reuse_rate == 3.0

    def test_pattern_reuse_rate_no_patterns(self):
        """Test pattern reuse rate with no shared patterns."""
        metrics = TeamMetrics()
        metrics.pattern_reuse_count = 10

        assert metrics.pattern_reuse_rate == 0.0

    def test_collaboration_efficiency_with_data(self):
        """Test collaboration efficiency calculation."""
        metrics = TeamMetrics()
        metrics.pattern_reuse_count = 20
        metrics.cross_agent_reuses = 15

        # 15 cross-agent / 20 total = 0.75 (75% collaboration)
        assert metrics.collaboration_efficiency == 0.75

    def test_collaboration_efficiency_no_reuses(self):
        """Test collaboration efficiency with no pattern reuses."""
        metrics = TeamMetrics()

        assert metrics.collaboration_efficiency == 0.0

    def test_collaboration_efficiency_no_cross_agent(self):
        """Test collaboration efficiency with no cross-agent reuses."""
        metrics = TeamMetrics()
        metrics.pattern_reuse_count = 10
        metrics.cross_agent_reuses = 0

        assert metrics.collaboration_efficiency == 0.0


class TestAgentMonitor:
    """Tests for AgentMonitor class."""

    def test_initialization(self):
        """Test AgentMonitor initialization."""
        monitor = AgentMonitor()

        assert len(monitor.agents) == 0
        assert monitor.pattern_library is None
        assert len(monitor.pattern_uses) == 0
        assert len(monitor.alerts) == 0

    def test_initialization_with_library(self):
        """Test AgentMonitor initialization with pattern library."""
        library = PatternLibrary()
        monitor = AgentMonitor(pattern_library=library)

        assert monitor.pattern_library is library

    def test_record_interaction(self):
        """Test recording agent interactions."""
        monitor = AgentMonitor()

        monitor.record_interaction("agent_1", response_time_ms=150.0)
        monitor.record_interaction("agent_1", response_time_ms=250.0)

        agent = monitor.agents["agent_1"]
        assert agent.total_interactions == 2
        assert agent.total_response_time_ms == 400.0
        assert agent.avg_response_time_ms == 200.0

    def test_record_interaction_creates_new_agent(self):
        """Test that recording interaction creates agent if needed."""
        monitor = AgentMonitor()

        monitor.record_interaction("new_agent", response_time_ms=100.0)

        assert "new_agent" in monitor.agents
        assert monitor.agents["new_agent"].total_interactions == 1

    def test_record_interaction_slow_response_alert(self):
        """Test that slow responses trigger alerts."""
        monitor = AgentMonitor()

        # Record slow interaction (over 5000ms)
        monitor.record_interaction("slow_agent", response_time_ms=6000.0)

        assert len(monitor.alerts) == 1
        alert = monitor.alerts[0]
        assert alert["agent_id"] == "slow_agent"
        assert alert["alert_type"] == "slow_response"
        assert "6000ms" in alert["message"]

    def test_record_pattern_discovery(self):
        """Test recording pattern discoveries."""
        monitor = AgentMonitor()

        monitor.record_pattern_discovery("agent_1", pattern_id="pattern_1")
        monitor.record_pattern_discovery("agent_1", pattern_id="pattern_2")

        agent = monitor.agents["agent_1"]
        assert agent.patterns_discovered == 2

    def test_record_pattern_use_success(self):
        """Test recording successful pattern use."""
        monitor = AgentMonitor()

        monitor.record_pattern_use(
            agent_id="agent_1",
            pattern_id="pattern_123",
            pattern_agent="agent_2",
            success=True,
        )

        agent = monitor.agents["agent_1"]
        assert agent.patterns_used == 1
        assert agent.successful_pattern_uses == 1
        assert agent.failed_pattern_uses == 0
        assert agent.success_rate == 1.0

    def test_record_pattern_use_failure(self):
        """Test recording failed pattern use."""
        monitor = AgentMonitor()

        monitor.record_pattern_use(
            agent_id="agent_1",
            pattern_id="pattern_123",
            success=False,
        )

        agent = monitor.agents["agent_1"]
        assert agent.patterns_used == 1
        assert agent.successful_pattern_uses == 0
        assert agent.failed_pattern_uses == 1
        assert agent.success_rate == 0.0

    def test_record_pattern_use_tracks_cross_agent(self):
        """Test that pattern uses track cross-agent collaboration."""
        monitor = AgentMonitor()

        # Same agent using own pattern (not cross-agent)
        monitor.record_pattern_use(
            agent_id="agent_1",
            pattern_id="p1",
            pattern_agent="agent_1",
            success=True,
        )

        # Different agent using pattern (cross-agent)
        monitor.record_pattern_use(
            agent_id="agent_2",
            pattern_id="p1",
            pattern_agent="agent_1",
            success=True,
        )

        assert len(monitor.pattern_uses) == 2
        assert monitor.pattern_uses[0]["cross_agent"] is False
        assert monitor.pattern_uses[1]["cross_agent"] is True

    def test_get_agent_stats_existing_agent(self):
        """Test getting stats for existing agent."""
        monitor = AgentMonitor()

        monitor.record_interaction("agent_1", response_time_ms=100.0)
        monitor.record_pattern_discovery("agent_1")
        monitor.record_pattern_use("agent_1", success=True)

        stats = monitor.get_agent_stats("agent_1")

        assert stats["agent_id"] == "agent_1"
        assert stats["total_interactions"] == 1
        assert stats["avg_response_time_ms"] == 100.0
        assert stats["patterns_discovered"] == 1
        assert stats["patterns_used"] == 1
        assert stats["success_rate"] == 1.0
        assert stats["status"] == "active"

    def test_get_agent_stats_nonexistent_agent(self):
        """Test getting stats for non-existent agent."""
        monitor = AgentMonitor()

        stats = monitor.get_agent_stats("unknown_agent")

        assert stats["agent_id"] == "unknown_agent"
        assert stats["total_interactions"] == 0
        assert stats["avg_response_time_ms"] == 0.0
        assert stats["patterns_discovered"] == 0
        assert stats["status"] == "unknown"

    def test_get_team_stats_no_agents(self):
        """Test getting team stats with no agents."""
        monitor = AgentMonitor()

        stats = monitor.get_team_stats()

        assert stats["active_agents"] == 0
        assert stats["total_agents"] == 0
        assert stats["shared_patterns"] == 0
        assert stats["total_interactions"] == 0
        assert stats["pattern_reuse_rate"] == 0.0
        assert stats["collaboration_efficiency"] == 0.0

    def test_get_team_stats_with_agents(self):
        """Test getting team stats with multiple agents."""
        monitor = AgentMonitor()

        # Record activity for multiple agents
        monitor.record_interaction("agent_1", response_time_ms=100.0)
        monitor.record_interaction("agent_2", response_time_ms=150.0)
        monitor.record_pattern_discovery("agent_1")
        monitor.record_pattern_discovery("agent_2")

        # Record pattern uses (cross-agent collaboration)
        monitor.record_pattern_use("agent_1", pattern_agent="agent_2", success=True)
        monitor.record_pattern_use("agent_2", pattern_agent="agent_1", success=True)

        stats = monitor.get_team_stats()

        assert stats["active_agents"] == 2
        assert stats["total_agents"] == 2
        assert stats["total_interactions"] == 2
        assert stats["total_patterns_discovered"] == 2
        assert stats["pattern_reuse_count"] == 2
        assert stats["cross_agent_reuses"] == 2
        assert stats["collaboration_efficiency"] == 1.0  # All reuses are cross-agent

    def test_get_team_stats_with_pattern_library(self):
        """Test team stats uses pattern library count."""
        library = PatternLibrary()
        pattern = Pattern(
            id="lib_pattern",
            agent_id="agent_1",
            pattern_type="test",
            name="Library Pattern",
            description="Test pattern",
        )
        library.contribute_pattern("agent_1", pattern)

        monitor = AgentMonitor(pattern_library=library)

        stats = monitor.get_team_stats()

        assert stats["shared_patterns"] == 1

    def test_get_top_contributors(self):
        """Test getting top pattern contributors."""
        monitor = AgentMonitor()

        # Create agents with different contribution levels
        monitor.record_pattern_discovery("agent_1")
        monitor.record_pattern_discovery("agent_1")
        monitor.record_pattern_discovery("agent_1")

        monitor.record_pattern_discovery("agent_2")
        monitor.record_pattern_discovery("agent_2")

        monitor.record_pattern_discovery("agent_3")

        # Get top 2 contributors
        top = monitor.get_top_contributors(n=2)

        assert len(top) == 2
        assert top[0]["agent_id"] == "agent_1"
        assert top[0]["patterns_discovered"] == 3
        assert top[1]["agent_id"] == "agent_2"
        assert top[1]["patterns_discovered"] == 2

    def test_get_alerts(self):
        """Test getting recent alerts."""
        monitor = AgentMonitor()

        # Trigger slow response alert
        monitor.record_interaction("slow_agent", response_time_ms=6000.0)

        alerts = monitor.get_alerts()

        assert len(alerts) == 1
        assert alerts[0]["agent_id"] == "slow_agent"
        assert alerts[0]["alert_type"] == "slow_response"

    def test_get_alerts_with_limit(self):
        """Test getting alerts with limit."""
        monitor = AgentMonitor()

        # Create multiple alerts
        for i in range(10):
            monitor.record_interaction(f"agent_{i}", response_time_ms=6000.0)

        # Get limited alerts
        alerts = monitor.get_alerts(limit=5)

        assert len(alerts) == 5

    def test_check_health_healthy(self):
        """Test health check returns healthy status."""
        monitor = AgentMonitor()

        # Record some activity
        monitor.record_interaction("agent_1", response_time_ms=100.0)

        health = monitor.check_health()

        assert health["status"] == "healthy"
        assert len(health["issues"]) == 0
        assert health["active_agents"] == 1

    def test_check_health_no_active_agents(self):
        """Test health check detects no active agents."""
        monitor = AgentMonitor()

        health = monitor.check_health()

        assert health["status"] == "degraded"
        assert "No active agents" in health["issues"]
        assert health["active_agents"] == 0

    def test_check_health_low_collaboration(self):
        """Test health check detects low collaboration efficiency."""
        monitor = AgentMonitor()

        # Create agents with low collaboration
        monitor.record_interaction("agent_1", response_time_ms=100.0)
        monitor.record_pattern_discovery("agent_1")

        # Record many same-agent pattern uses (low collaboration)
        for _ in range(15):
            monitor.record_pattern_use("agent_1", pattern_agent="agent_1", success=True)

        health = monitor.check_health()

        assert health["status"] == "degraded"
        assert "Low collaboration efficiency" in health["issues"]

    def test_reset(self):
        """Test resetting all monitoring data."""
        monitor = AgentMonitor()

        # Add some data
        monitor.record_interaction("agent_1", response_time_ms=100.0)
        monitor.record_pattern_discovery("agent_1")
        monitor.record_pattern_use("agent_1", success=True)
        monitor.record_interaction("slow_agent", response_time_ms=6000.0)  # Alert

        # Verify data exists
        assert len(monitor.agents) > 0
        assert len(monitor.pattern_uses) > 0
        assert len(monitor.alerts) > 0

        # Reset
        monitor.reset()

        # Verify all data cleared
        assert len(monitor.agents) == 0
        assert len(monitor.pattern_uses) == 0
        assert len(monitor.alerts) == 0

    def test_alert_bounding(self):
        """Test that alerts are bounded to prevent memory issues."""
        monitor = AgentMonitor()

        # Create exactly 1001 alerts to trigger bounding
        for i in range(1001):
            monitor._add_alert(
                agent_id=f"agent_{i}",
                alert_type="test",
                message="Test alert",
            )

        # Should be bounded to 500 most recent after exceeding 1000
        assert len(monitor.alerts) == 500

        # Verify it's the most recent 500
        assert monitor.alerts[0]["agent_id"] == "agent_501"
        assert monitor.alerts[-1]["agent_id"] == "agent_1000"
