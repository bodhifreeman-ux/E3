"""
Agent #4: STRATEGIST (Solution Designer)

Generates multiple strategic approaches and recommends optimal paths.
"""

from agents.base_agent import BaseAgent
from csdl.protocol import CSDLMessage
from typing import Dict, Any, Optional, List
import structlog

logger = structlog.get_logger()


class StrategistAgent(BaseAgent):
    """
    STRATEGIST - Solution Designer Agent

    Capabilities:
    - Multi-option solution generation
    - Trade-off analysis
    - Strategic planning
    - Approach comparison
    - Optimal path selection
    - Contingency planning
    """

    def __init__(self, vllm_client, knowledge_base, config=None):
        super().__init__(
            agent_id="strategist",
            agent_name="Strategist",
            vllm_client=vllm_client,
            knowledge_base=knowledge_base,
            config=config
        )

    def _build_system_context(self) -> Dict[str, Any]:
        return {
            "role": "solution_designer",
            "agent_id": "strategist",
            "agent_name": "Strategist",
            "tier": 2,
            "capabilities": [
                "multi_option_generation",
                "trade_off_analysis",
                "strategic_planning",
                "approach_comparison",
                "optimal_path_selection",
                "contingency_planning"
            ],
            "specialization": "strategic_thinking",
            "outputs": "multiple_strategic_options_with_analysis"
        }

    async def process_csdl(
        self,
        message: CSDLMessage,
        context: Optional[Dict[str, Any]] = None
    ) -> CSDLMessage:
        """
        Process strategy design request

        Generates multiple approaches and recommends the best path.
        """

        problem = message.content.get("problem", message.content)

        logger.info(
            "strategist_processing",
            message_id=message.message_id
        )

        # Generate multiple strategic options
        options = await self._generate_options(problem)

        # Analyze trade-offs
        analysis = await self._analyze_tradeoffs(options, problem)

        # Recommend optimal approach
        recommendation = await self._recommend_optimal(options, analysis)

        result = {
            "semantic_type": "strategic_analysis",
            "options": options,
            "trade_off_analysis": analysis,
            "recommendation": recommendation,
            "contingency_plans": await self._generate_contingencies(recommendation)
        }

        from csdl.protocol import CSDLProtocol

        return CSDLProtocol.create_response(
            content_csdl=result,
            sender_id=self.agent_id,
            in_response_to=message.message_id,
            recipient_id=message.sender_id
        )

    async def _generate_options(
        self,
        problem: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate 3-5 strategic options

        Each option is a complete approach with:
        - Description
        - Key steps
        - Resources required
        - Timeline
        - Risks
        - Benefits
        """

        generation_query = {
            "semantic_type": "option_generation",
            "task": "strategic_option_generation",
            "problem": problem,
            "constraints": problem.get("constraints", []),
            "requirements": [
                "generate_3_to_5_distinct_approaches",
                "ensure_diversity_of_strategies",
                "include_conventional_and_innovative",
                "consider_resource_constraints",
                "account_for_timeline"
            ]
        }

        response = await self._call_vllm(generation_query, temperature=0.7)

        options = response.get("options", [])

        # Ensure each option is complete
        for i, option in enumerate(options):
            option["option_id"] = f"option_{i+1}"
            option.setdefault("description", "")
            option.setdefault("steps", [])
            option.setdefault("resources", {})
            option.setdefault("timeline", "")
            option.setdefault("risks", [])
            option.setdefault("benefits", [])

        return options

    async def _analyze_tradeoffs(
        self,
        options: List[Dict[str, Any]],
        problem: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze trade-offs between options

        Compares:
        - Speed vs Quality
        - Cost vs Benefit
        - Risk vs Reward
        - Complexity vs Maintainability
        - Short-term vs Long-term
        """

        analysis_query = {
            "semantic_type": "tradeoff_analysis",
            "task": "trade_off_analysis",
            "options": options,
            "problem_context": problem,
            "compare_on": [
                "implementation_speed",
                "resource_cost",
                "technical_complexity",
                "maintainability",
                "scalability",
                "risk_level",
                "expected_outcome_quality",
                "team_impact"
            ]
        }

        analysis = await self._call_vllm(analysis_query, temperature=0.3)

        return {
            "comparison_matrix": analysis.get("matrix", {}),
            "key_tradeoffs": analysis.get("tradeoffs", []),
            "strengths_per_option": analysis.get("strengths", {}),
            "weaknesses_per_option": analysis.get("weaknesses", {}),
            "risk_assessment": analysis.get("risks", {})
        }

    async def _recommend_optimal(
        self,
        options: List[Dict[str, Any]],
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Recommend the optimal approach

        Based on:
        - Trade-off analysis
        - Problem priorities
        - Risk tolerance
        - Resource availability
        """

        recommendation_query = {
            "semantic_type": "recommendation",
            "task": "optimal_approach_recommendation",
            "options": options,
            "analysis": analysis,
            "selection_criteria": [
                "best_outcome_probability",
                "acceptable_risk_level",
                "resource_feasibility",
                "timeline_alignment",
                "strategic_fit"
            ]
        }

        recommendation = await self._call_vllm(recommendation_query, temperature=0.2)

        return {
            "recommended_option": recommendation.get("option_id"),
            "rationale": recommendation.get("rationale", ""),
            "confidence": recommendation.get("confidence", 0.0),
            "key_success_factors": recommendation.get("success_factors", []),
            "watch_points": recommendation.get("watch_points", []),
            "fallback_option": recommendation.get("fallback", "")
        }

    async def _generate_contingencies(
        self,
        recommendation: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate contingency plans

        Plans for:
        - If timeline slips
        - If resources unavailable
        - If technical challenges arise
        - If requirements change
        """

        contingency_query = {
            "semantic_type": "contingency_planning",
            "task": "contingency_planning",
            "primary_plan": recommendation,
            "scenarios": [
                "timeline_delay",
                "resource_shortage",
                "technical_blocker",
                "requirement_change",
                "external_dependency_failure"
            ]
        }

        contingencies = await self._call_vllm(contingency_query, temperature=0.4)

        return contingencies.get("contingency_plans", [])
