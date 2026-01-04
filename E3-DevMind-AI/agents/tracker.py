"""
Agent #29: TRACKER (Progress Monitor)

Tracks progress across all E3 work with real-time monitoring and analytics.
"""

from agents.base_agent import BaseAgent
from csdl.protocol import CSDLMessage
from typing import Dict, Any, Optional, List
import structlog

logger = structlog.get_logger()


class TrackerAgent(BaseAgent):
    """TRACKER - Progress Monitor Agent"""

    def __init__(self, vllm_client, knowledge_base, config=None):
        super().__init__(
            agent_id="tracker",
            agent_name="Tracker",
            vllm_client=vllm_client,
            knowledge_base=knowledge_base,
            config=config
        )
        self.progress_snapshots: List[Dict[str, Any]] = []
        self.blockers: Dict[str, List[Dict[str, Any]]] = {}
        self.velocity_metrics: Dict[str, Any] = {
            "historical_velocity": [],
            "current_velocity": 0.0,
            "velocity_trend": "stable"
        }
        self.milestone_tracking: Dict[str, Dict[str, Any]] = {}
        self.health_indicators: Dict[str, Any] = {}

    def _build_system_context(self) -> Dict[str, Any]:
        return {
            "role": "progress_monitoring",
            "agent_id": "tracker",
            "agent_name": "Tracker",
            "tier": 6,
            "capabilities": [
                "real_time_progress_tracking",
                "blocker_identification",
                "velocity_tracking",
                "milestone_monitoring",
                "health_assessment",
                "trend_analysis",
                "early_warning_system"
            ],
            "specialization": "progress_analytics"
        }

    async def process_csdl(self, message: CSDLMessage, context: Optional[Dict[str, Any]] = None) -> CSDLMessage:
        """Process progress tracking request"""
        query_type = message.content.get("query_type", "track_progress")

        if query_type == "track_progress":
            result = await self._track_progress(message.content)
        elif query_type == "identify_blockers":
            result = await self._identify_blockers(message.content)
        elif query_type == "calculate_velocity":
            result = await self._calculate_velocity(message.content)
        elif query_type == "monitor_milestones":
            result = await self._monitor_milestones(message.content)
        elif query_type == "assess_health":
            result = await self._assess_project_health(message.content)
        else:
            result = await self._generate_status_report(message.content)

        from csdl.protocol import CSDLProtocol
        return CSDLProtocol.create_response(
            content_csdl=result, sender_id=self.agent_id,
            in_response_to=message.message_id, recipient_id=message.sender_id
        )

    async def _track_progress(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Track progress across projects and tasks"""
        project_id = query_csdl.get("project_id")
        tasks = query_csdl.get("tasks", [])
        time_period = query_csdl.get("time_period", "current_sprint")

        tracking_query = {
            "semantic_type": "progress_tracking",
            "task": "progress_analysis",
            "project_id": project_id,
            "tasks": tasks,
            "time_period": time_period,
            "historical_data": self.progress_snapshots[-10:],  # Last 10 snapshots
            "tracking_metrics": [
                "completion_percentage",
                "task_throughput",
                "work_in_progress",
                "cycle_time",
                "lead_time"
            ],
            "analysis_dimensions": [
                "overall_progress",
                "individual_task_status",
                "timeline_adherence",
                "scope_changes",
                "quality_metrics"
            ]
        }

        progress = await self._call_vllm(tracking_query, temperature=0.2)

        # Record snapshot
        snapshot = {
            "project_id": project_id,
            "progress": progress,
            "timestamp": "now",
            "task_count": len(tasks)
        }
        self.progress_snapshots.append(snapshot)

        # Keep only last 100 snapshots
        if len(self.progress_snapshots) > 100:
            self.progress_snapshots = self.progress_snapshots[-100:]

        return {
            "semantic_type": "progress_result",
            "project_id": project_id,
            "progress": progress,
            "completion_rate": progress.get("completion_percentage", 0.0),
            "on_track": progress.get("on_track", True),
            "variance": progress.get("variance", "0%")
        }

    async def _identify_blockers(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Identify and analyze blockers"""
        project_id = query_csdl.get("project_id")
        tasks = query_csdl.get("tasks", [])

        blocker_query = {
            "semantic_type": "blocker_identification",
            "task": "blocker_analysis",
            "project_id": project_id,
            "tasks": tasks,
            "historical_blockers": self.blockers.get(project_id, []),
            "identification_criteria": [
                "stalled_tasks",
                "dependency_issues",
                "resource_constraints",
                "technical_impediments",
                "external_dependencies"
            ],
            "blocker_attributes": [
                "blocker_type",
                "severity",
                "impact_scope",
                "affected_tasks",
                "resolution_path",
                "estimated_resolution_time"
            ]
        }

        blockers = await self._call_vllm(blocker_query, temperature=0.2)

        # Record blockers
        if project_id not in self.blockers:
            self.blockers[project_id] = []

        for blocker in blockers.get("blockers", []):
            self.blockers[project_id].append(blocker)

        return {
            "semantic_type": "blocker_result",
            "project_id": project_id,
            "blockers": blockers,
            "blocker_count": len(blockers.get("blockers", [])),
            "critical_blockers": blockers.get("critical_count", 0),
            "resolution_recommendations": blockers.get("resolutions", [])
        }

    async def _calculate_velocity(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate and analyze team velocity"""
        project_id = query_csdl.get("project_id")
        completed_work = query_csdl.get("completed_work", [])
        time_period = query_csdl.get("time_period", "sprint")

        velocity_query = {
            "semantic_type": "velocity_calculation",
            "task": "velocity_analysis",
            "project_id": project_id,
            "completed_work": completed_work,
            "time_period": time_period,
            "historical_velocity": self.velocity_metrics["historical_velocity"],
            "velocity_metrics": [
                "story_points_completed",
                "tasks_completed",
                "throughput_rate",
                "velocity_trend",
                "predictability_score"
            ],
            "analysis_outputs": [
                "current_velocity",
                "velocity_change",
                "forecast_accuracy",
                "capacity_recommendations"
            ]
        }

        velocity = await self._call_vllm(velocity_query, temperature=0.2)

        # Update velocity metrics
        current_velocity = velocity.get("current_velocity", 0.0)
        self.velocity_metrics["historical_velocity"].append(current_velocity)
        self.velocity_metrics["current_velocity"] = current_velocity
        self.velocity_metrics["velocity_trend"] = velocity.get("trend", "stable")

        # Keep only last 20 velocity measurements
        if len(self.velocity_metrics["historical_velocity"]) > 20:
            self.velocity_metrics["historical_velocity"] = \
                self.velocity_metrics["historical_velocity"][-20:]

        return {
            "semantic_type": "velocity_result",
            "project_id": project_id,
            "velocity": velocity,
            "current_velocity": current_velocity,
            "velocity_trend": self.velocity_metrics["velocity_trend"],
            "forecast": velocity.get("forecast", {})
        }

    async def _monitor_milestones(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor milestone progress and health"""
        project_id = query_csdl.get("project_id")
        milestones = query_csdl.get("milestones", [])

        milestone_query = {
            "semantic_type": "milestone_monitoring",
            "task": "milestone_analysis",
            "project_id": project_id,
            "milestones": milestones,
            "milestone_tracking": self.milestone_tracking.get(project_id, {}),
            "monitoring_aspects": [
                "milestone_progress",
                "completion_confidence",
                "risk_factors",
                "dependencies_status",
                "timeline_variance"
            ],
            "early_warning_indicators": [
                "slipping_dates",
                "scope_creep",
                "resource_shortfalls",
                "quality_concerns"
            ]
        }

        milestone_status = await self._call_vllm(milestone_query, temperature=0.2)

        # Update milestone tracking
        self.milestone_tracking[project_id] = milestone_status.get("tracking_data", {})

        return {
            "semantic_type": "milestone_result",
            "project_id": project_id,
            "milestone_status": milestone_status,
            "milestones_on_track": milestone_status.get("on_track_count", 0),
            "milestones_at_risk": milestone_status.get("at_risk_count", 0),
            "next_milestone": milestone_status.get("next_milestone", {})
        }

    async def _assess_project_health(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall project health"""
        project_id = query_csdl.get("project_id")

        health_query = {
            "semantic_type": "health_assessment",
            "task": "project_health_analysis",
            "project_id": project_id,
            "progress_data": self.progress_snapshots[-10:],
            "blockers": self.blockers.get(project_id, []),
            "velocity_metrics": self.velocity_metrics,
            "milestone_status": self.milestone_tracking.get(project_id, {}),
            "health_indicators": [
                "schedule_health",
                "scope_health",
                "quality_health",
                "resource_health",
                "risk_health"
            ],
            "assessment_outputs": [
                "overall_health_score",
                "health_by_dimension",
                "warning_signals",
                "improvement_recommendations"
            ]
        }

        health = await self._call_vllm(health_query, temperature=0.2)

        # Update health indicators
        self.health_indicators[project_id] = health

        return {
            "semantic_type": "health_result",
            "project_id": project_id,
            "health": health,
            "overall_score": health.get("overall_health_score", 0.0),
            "status": health.get("status", "unknown"),
            "recommendations": health.get("improvement_recommendations", [])
        }

    async def _generate_status_report(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive status report"""
        project_id = query_csdl.get("project_id")
        report_type = query_csdl.get("report_type", "comprehensive")

        report_query = {
            "semantic_type": "status_report_generation",
            "task": "comprehensive_status_report",
            "project_id": project_id,
            "report_type": report_type,
            "data_sources": {
                "progress": self.progress_snapshots[-5:],
                "blockers": self.blockers.get(project_id, []),
                "velocity": self.velocity_metrics,
                "milestones": self.milestone_tracking.get(project_id, {}),
                "health": self.health_indicators.get(project_id, {})
            },
            "report_sections": [
                "executive_summary",
                "progress_overview",
                "key_achievements",
                "current_blockers",
                "velocity_analysis",
                "milestone_status",
                "health_assessment",
                "risks_and_issues",
                "next_steps",
                "recommendations"
            ]
        }

        report = await self._call_vllm(report_query, temperature=0.3)

        return {
            "semantic_type": "status_report_result",
            "project_id": project_id,
            "report": report,
            "report_type": report_type,
            "generated_at": "now"
        }
