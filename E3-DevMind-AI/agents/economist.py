"""
Agent #5: ECONOMIST (Resource Optimizer)

Optimizes budget, resources, and ROI across E3 operations.
"""

from agents.base_agent import BaseAgent
from csdl.protocol import CSDLMessage
from typing import Dict, Any, Optional, List
import structlog

logger = structlog.get_logger()


class EconomistAgent(BaseAgent):
    """
    ECONOMIST - Resource Optimizer Agent

    Capabilities:
    - Budget optimization
    - ROI analysis
    - Resource allocation
    - Cost-benefit analysis
    - Efficiency optimization
    - Investment prioritization
    """

    def __init__(self, vllm_client, knowledge_base, config=None):
        super().__init__(
            agent_id="economist",
            agent_name="Economist",
            vllm_client=vllm_client,
            knowledge_base=knowledge_base,
            config=config
        )

    def _build_system_context(self) -> Dict[str, Any]:
        return {
            "role": "resource_optimization",
            "agent_id": "economist",
            "agent_name": "Economist",
            "tier": 2,
            "capabilities": [
                "budget_optimization",
                "roi_analysis",
                "resource_allocation",
                "cost_benefit_analysis",
                "efficiency_optimization",
                "investment_prioritization"
            ],
            "specialization": "economic_efficiency",
            "outputs": "resource_allocation_recommendations"
        }

    async def process_csdl(
        self,
        message: CSDLMessage,
        context: Optional[Dict[str, Any]] = None
    ) -> CSDLMessage:
        """
        Process resource optimization request
        """

        query_type = message.content.get("query_type", "general_optimization")

        logger.info(
            "economist_processing",
            query_type=query_type,
            message_id=message.message_id
        )

        if query_type == "budget_optimization":
            result = await self._optimize_budget(message.content)
        elif query_type == "roi_analysis":
            result = await self._analyze_roi(message.content)
        elif query_type == "resource_allocation":
            result = await self._allocate_resources(message.content)
        elif query_type == "cost_benefit":
            result = await self._cost_benefit_analysis(message.content)
        else:
            result = await self._general_optimization(message.content)

        from csdl.protocol import CSDLProtocol

        return CSDLProtocol.create_response(
            content_csdl=result,
            sender_id=self.agent_id,
            in_response_to=message.message_id,
            recipient_id=message.sender_id
        )

    async def _optimize_budget(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Optimize budget allocation across projects/areas
        """

        current_budget = query_csdl.get("current_budget", {})
        priorities = query_csdl.get("priorities", [])

        optimization_query = {
            "semantic_type": "budget_optimization",
            "task": "budget_optimization",
            "current_allocation": current_budget,
            "priorities": priorities,
            "constraints": query_csdl.get("constraints", []),
            "optimize_for": [
                "maximum_value_delivery",
                "risk_mitigation",
                "strategic_alignment",
                "flexibility"
            ]
        }

        optimization = await self._call_vllm(optimization_query, temperature=0.3)

        return {
            "semantic_type": "budget_optimization_result",
            "optimized_allocation": optimization.get("allocation", {}),
            "changes_from_current": optimization.get("changes", []),
            "expected_improvements": optimization.get("improvements", {}),
            "rationale": optimization.get("rationale", ""),
            "implementation_plan": optimization.get("plan", [])
        }

    async def _analyze_roi(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze ROI for investments/projects
        """

        investment = query_csdl.get("investment", {})

        roi_query = {
            "semantic_type": "roi_analysis",
            "task": "roi_analysis",
            "investment": investment,
            "costs": query_csdl.get("costs", {}),
            "expected_benefits": query_csdl.get("benefits", []),
            "timeframe": query_csdl.get("timeframe", "12_months"),
            "calculate": [
                "direct_roi",
                "indirect_benefits",
                "opportunity_cost",
                "risk_adjusted_return",
                "payback_period"
            ]
        }

        analysis = await self._call_vllm(roi_query, temperature=0.2)

        return {
            "semantic_type": "roi_analysis_result",
            "roi_percentage": analysis.get("roi", 0.0),
            "payback_period": analysis.get("payback", ""),
            "npv": analysis.get("npv", 0.0),
            "risk_adjusted_roi": analysis.get("risk_adjusted", 0.0),
            "qualitative_benefits": analysis.get("qualitative", []),
            "recommendation": analysis.get("recommendation", "")
        }

    async def _allocate_resources(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Allocate resources optimally across needs
        """

        available = query_csdl.get("available_resources", {})
        demands = query_csdl.get("resource_demands", [])

        allocation_query = {
            "semantic_type": "resource_allocation",
            "task": "resource_allocation",
            "available": available,
            "demands": demands,
            "constraints": query_csdl.get("constraints", []),
            "optimize_for": "maximum_value_delivery"
        }

        allocation = await self._call_vllm(allocation_query, temperature=0.3)

        return {
            "semantic_type": "resource_allocation_result",
            "allocation_plan": allocation.get("plan", {}),
            "unmet_demands": allocation.get("unmet", []),
            "efficiency_score": allocation.get("efficiency", 0.0),
            "recommendations": allocation.get("recommendations", [])
        }

    async def _cost_benefit_analysis(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Comprehensive cost-benefit analysis
        """

        proposal = query_csdl.get("proposal", {})

        cba_query = {
            "semantic_type": "cost_benefit_analysis",
            "task": "cost_benefit_analysis",
            "proposal": proposal,
            "costs": query_csdl.get("costs", []),
            "benefits": query_csdl.get("benefits", []),
            "timeframe": query_csdl.get("timeframe", ""),
            "analyze": [
                "tangible_costs",
                "intangible_costs",
                "tangible_benefits",
                "intangible_benefits",
                "opportunity_cost",
                "risk_factors"
            ]
        }

        analysis = await self._call_vllm(cba_query, temperature=0.2)

        return {
            "semantic_type": "cost_benefit_result",
            "total_costs": analysis.get("costs", {}),
            "total_benefits": analysis.get("benefits", {}),
            "net_benefit": analysis.get("net", 0.0),
            "benefit_cost_ratio": analysis.get("ratio", 0.0),
            "recommendation": analysis.get("recommendation", ""),
            "key_assumptions": analysis.get("assumptions", [])
        }

    async def _general_optimization(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """General resource optimization"""

        optimization_query = {
            "semantic_type": "general_optimization",
            "task": "general_resource_optimization",
            "context": query_csdl
        }

        optimization = await self._call_vllm(optimization_query, temperature=0.3)

        return optimization
