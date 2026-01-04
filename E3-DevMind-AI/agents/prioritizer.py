"""
Agent #30: PRIORITIZER (Task Optimizer)

Determines optimal task priorities using sophisticated analysis frameworks.
"""

from agents.base_agent import BaseAgent
from csdl.protocol import CSDLMessage
from typing import Dict, Any, Optional, List
import structlog

logger = structlog.get_logger()


class PrioritizerAgent(BaseAgent):
    """PRIORITIZER - Task Optimizer Agent"""

    def __init__(self, vllm_client, knowledge_base, config=None):
        super().__init__(
            agent_id="prioritizer",
            agent_name="Prioritizer",
            vllm_client=vllm_client,
            knowledge_base=knowledge_base,
            config=config
        )
        self.priority_scores: Dict[str, float] = {}
        self.prioritization_history: List[Dict[str, Any]] = []
        self.value_metrics: Dict[str, Any] = {}
        self.effort_estimates: Dict[str, Any] = {}

    def _build_system_context(self) -> Dict[str, Any]:
        return {
            "role": "task_prioritization",
            "agent_id": "prioritizer",
            "agent_name": "Prioritizer",
            "tier": 6,
            "capabilities": [
                "impact_vs_effort_analysis",
                "priority_scoring",
                "value_assessment",
                "risk_adjusted_prioritization",
                "strategic_alignment",
                "multi_criteria_optimization",
                "dynamic_reprioritization"
            ],
            "specialization": "priority_optimization"
        }

    async def process_csdl(self, message: CSDLMessage, context: Optional[Dict[str, Any]] = None) -> CSDLMessage:
        """Process prioritization request"""
        query_type = message.content.get("query_type", "prioritize")

        if query_type == "prioritize":
            result = await self._prioritize_tasks(message.content)
        elif query_type == "impact_analysis":
            result = await self._analyze_impact(message.content)
        elif query_type == "effort_analysis":
            result = await self._analyze_effort(message.content)
        elif query_type == "value_assessment":
            result = await self._assess_value(message.content)
        elif query_type == "strategic_alignment":
            result = await self._assess_strategic_alignment(message.content)
        else:
            result = await self._reprioritize(message.content)

        from csdl.protocol import CSDLProtocol
        return CSDLProtocol.create_response(
            content_csdl=result, sender_id=self.agent_id,
            in_response_to=message.message_id, recipient_id=message.sender_id
        )

    async def _prioritize_tasks(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Prioritize tasks using multi-criteria analysis"""
        tasks = query_csdl.get("tasks", [])
        context_data = query_csdl.get("context", {})
        prioritization_framework = query_csdl.get("framework", "comprehensive")

        prioritization_query = {
            "semantic_type": "task_prioritization",
            "task": "multi_criteria_prioritization",
            "tasks": tasks,
            "context": context_data,
            "framework": prioritization_framework,
            "prioritization_criteria": [
                "business_value",
                "strategic_importance",
                "customer_impact",
                "technical_risk",
                "implementation_effort",
                "dependencies",
                "time_sensitivity",
                "resource_availability"
            ],
            "scoring_methods": [
                "weighted_score_calculation",
                "rice_scoring",  # Reach, Impact, Confidence, Effort
                "moscow_categorization",  # Must, Should, Could, Won't
                "kano_analysis",  # Customer satisfaction
                "cost_of_delay"
            ],
            "optimization_objectives": [
                "maximize_value_delivery",
                "minimize_risk",
                "optimize_resource_utilization",
                "maintain_strategic_alignment"
            ]
        }

        prioritization = await self._call_vllm(prioritization_query, temperature=0.2)

        # Record priorities
        for task in prioritization.get("prioritized_tasks", []):
            task_id = task.get("task_id")
            if task_id:
                self.priority_scores[task_id] = task.get("priority_score", 0.0)

        # Record prioritization event
        prioritization_record = {
            "framework": prioritization_framework,
            "task_count": len(tasks),
            "prioritization": prioritization,
            "timestamp": "now"
        }
        self.prioritization_history.append(prioritization_record)

        return {
            "semantic_type": "prioritization_result",
            "prioritized_tasks": prioritization.get("prioritized_tasks", []),
            "task_count": len(tasks),
            "framework": prioritization_framework,
            "priority_distribution": prioritization.get("priority_distribution", {}),
            "recommendations": prioritization.get("recommendations", [])
        }

    async def _analyze_impact(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze potential impact of tasks"""
        tasks = query_csdl.get("tasks", [])
        impact_dimensions = query_csdl.get("dimensions", [
            "customer", "revenue", "efficiency", "strategic", "technical"
        ])

        impact_query = {
            "semantic_type": "impact_analysis",
            "task": "multi_dimensional_impact_assessment",
            "tasks": tasks,
            "impact_dimensions": impact_dimensions,
            "analysis_framework": [
                "direct_impact",
                "indirect_impact",
                "long_term_impact",
                "ripple_effects",
                "opportunity_cost"
            ],
            "assessment_criteria": {
                "customer": ["satisfaction", "retention", "acquisition"],
                "revenue": ["direct_revenue", "revenue_enablement", "cost_savings"],
                "efficiency": ["time_savings", "resource_optimization", "automation"],
                "strategic": ["competitive_advantage", "market_positioning", "innovation"],
                "technical": ["technical_debt_reduction", "scalability", "maintainability"]
            }
        }

        impact_analysis = await self._call_vllm(impact_query, temperature=0.2)

        return {
            "semantic_type": "impact_result",
            "impact_analysis": impact_analysis,
            "task_count": len(tasks),
            "high_impact_tasks": impact_analysis.get("high_impact_count", 0),
            "impact_summary": impact_analysis.get("summary", {})
        }

    async def _analyze_effort(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze effort required for tasks"""
        tasks = query_csdl.get("tasks", [])

        effort_query = {
            "semantic_type": "effort_analysis",
            "task": "comprehensive_effort_estimation",
            "tasks": tasks,
            "effort_components": [
                "development_time",
                "testing_time",
                "deployment_time",
                "documentation_time",
                "coordination_overhead"
            ],
            "estimation_factors": [
                "technical_complexity",
                "unknowns_and_risks",
                "team_experience",
                "dependencies",
                "infrastructure_requirements"
            ],
            "estimation_methods": [
                "story_points",
                "time_based_estimation",
                "three_point_estimation",  # Best, Most Likely, Worst
                "historical_comparison"
            ]
        }

        effort_analysis = await self._call_vllm(effort_query, temperature=0.2)

        # Update effort estimates
        for task_estimate in effort_analysis.get("task_estimates", []):
            task_id = task_estimate.get("task_id")
            if task_id:
                self.effort_estimates[task_id] = task_estimate

        return {
            "semantic_type": "effort_result",
            "effort_analysis": effort_analysis,
            "task_count": len(tasks),
            "total_effort": effort_analysis.get("total_effort", 0),
            "effort_distribution": effort_analysis.get("distribution", {})
        }

    async def _assess_value(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Assess business value of tasks"""
        tasks = query_csdl.get("tasks", [])
        value_framework = query_csdl.get("framework", "comprehensive")

        value_query = {
            "semantic_type": "value_assessment",
            "task": "business_value_analysis",
            "tasks": tasks,
            "value_framework": value_framework,
            "value_dimensions": [
                "financial_value",
                "strategic_value",
                "customer_value",
                "operational_value",
                "innovation_value"
            ],
            "assessment_methods": [
                "roi_calculation",
                "npv_analysis",
                "payback_period",
                "strategic_value_scoring",
                "customer_lifetime_value_impact"
            ],
            "value_metrics": [
                "quantitative_value",
                "qualitative_value",
                "risk_adjusted_value",
                "time_value_of_money"
            ]
        }

        value_assessment = await self._call_vllm(value_query, temperature=0.2)

        # Update value metrics
        for task_value in value_assessment.get("task_values", []):
            task_id = task_value.get("task_id")
            if task_id:
                self.value_metrics[task_id] = task_value

        return {
            "semantic_type": "value_result",
            "value_assessment": value_assessment,
            "task_count": len(tasks),
            "high_value_tasks": value_assessment.get("high_value_count", 0),
            "total_value": value_assessment.get("total_value", 0)
        }

    async def _assess_strategic_alignment(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Assess strategic alignment of tasks"""
        tasks = query_csdl.get("tasks", [])
        strategic_goals = query_csdl.get("strategic_goals", [])

        alignment_query = {
            "semantic_type": "strategic_alignment_assessment",
            "task": "strategic_alignment_analysis",
            "tasks": tasks,
            "strategic_goals": strategic_goals,
            "alignment_criteria": [
                "goal_contribution",
                "strategic_fit",
                "mission_alignment",
                "vision_support",
                "competitive_positioning"
            ],
            "analysis_outputs": [
                "alignment_scores",
                "strategic_gaps",
                "alignment_recommendations",
                "portfolio_balance"
            ]
        }

        alignment = await self._call_vllm(alignment_query, temperature=0.2)

        return {
            "semantic_type": "alignment_result",
            "alignment": alignment,
            "task_count": len(tasks),
            "aligned_tasks": alignment.get("aligned_count", 0),
            "misaligned_tasks": alignment.get("misaligned_count", 0),
            "strategic_gaps": alignment.get("gaps", [])
        }

    async def _reprioritize(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Dynamic reprioritization based on changed conditions"""
        current_priorities = query_csdl.get("current_priorities", [])
        changed_conditions = query_csdl.get("changed_conditions", {})

        reprioritization_query = {
            "semantic_type": "dynamic_reprioritization",
            "task": "priority_adjustment",
            "current_priorities": current_priorities,
            "changed_conditions": changed_conditions,
            "historical_priorities": self.prioritization_history[-5:],
            "reprioritization_triggers": [
                "market_changes",
                "resource_changes",
                "deadline_changes",
                "strategic_shifts",
                "risk_changes",
                "dependency_updates"
            ],
            "adjustment_strategy": [
                "impact_assessment",
                "priority_recalculation",
                "cascade_analysis",
                "stakeholder_impact"
            ]
        }

        reprioritization = await self._call_vllm(reprioritization_query, temperature=0.3)

        # Update priorities
        for task in reprioritization.get("reprioritized_tasks", []):
            task_id = task.get("task_id")
            if task_id:
                self.priority_scores[task_id] = task.get("new_priority_score", 0.0)

        # Record reprioritization
        reprioritization_record = {
            "changed_conditions": changed_conditions,
            "task_count": len(current_priorities),
            "reprioritization": reprioritization,
            "timestamp": "now"
        }
        self.prioritization_history.append(reprioritization_record)

        return {
            "semantic_type": "reprioritization_result",
            "reprioritized_tasks": reprioritization.get("reprioritized_tasks", []),
            "changed_count": reprioritization.get("changed_count", 0),
            "priority_shifts": reprioritization.get("priority_shifts", []),
            "impact_summary": reprioritization.get("impact_summary", {})
        }
