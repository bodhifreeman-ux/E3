"""
Agent #8: VISIONARY (Innovation Engine)

Generates innovative approaches and identifies emerging technologies.
"""

from agents.base_agent import BaseAgent
from csdl.protocol import CSDLMessage
from typing import Dict, Any, Optional, List
import structlog

logger = structlog.get_logger()


class VisionaryAgent(BaseAgent):
    """
    VISIONARY - Innovation Engine Agent

    Capabilities:
    - Novel approach generation
    - Emerging technology identification
    - Creative problem solving
    - Blue-sky thinking
    - Paradigm shift suggestions
    - Unconventional strategies
    """

    def __init__(self, vllm_client, knowledge_base, config=None):
        super().__init__(
            agent_id="visionary",
            agent_name="Visionary",
            vllm_client=vllm_client,
            knowledge_base=knowledge_base,
            config=config
        )

    def _build_system_context(self) -> Dict[str, Any]:
        return {
            "role": "innovation_and_creativity",
            "agent_id": "visionary",
            "agent_name": "Visionary",
            "tier": 3,
            "capabilities": [
                "novel_approach_generation",
                "emerging_tech_identification",
                "creative_problem_solving",
                "paradigm_shift_suggestions",
                "unconventional_thinking",
                "innovation_catalysis"
            ],
            "thinking_style": "blue_sky_and_practical",
            "perspective": "future_oriented"
        }

    async def process_csdl(
        self,
        message: CSDLMessage,
        context: Optional[Dict[str, Any]] = None
    ) -> CSDLMessage:
        """Generate innovative solutions"""

        query_type = message.content.get("query_type", "innovation")

        logger.info(
            "visionary_processing",
            query_type=query_type,
            message_id=message.message_id
        )

        if query_type == "innovative_solutions":
            result = await self._generate_innovations(message.content)
        elif query_type == "emerging_tech":
            result = await self._identify_emerging_tech(message.content)
        elif query_type == "paradigm_shift":
            result = await self._suggest_paradigm_shift(message.content)
        elif query_type == "creative_problem_solving":
            result = await self._creative_problem_solving(message.content)
        else:
            result = await self._general_innovation(message.content)

        from csdl.protocol import CSDLProtocol

        return CSDLProtocol.create_response(
            content_csdl=result,
            sender_id=self.agent_id,
            in_response_to=message.message_id,
            recipient_id=message.sender_id
        )

    async def _generate_innovations(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate innovative approaches

        Thinks:
        - What if we tried something completely different?
        - What's the cutting-edge approach?
        - How would this look in 5 years?
        """

        problem = query_csdl.get("problem", {})

        innovation_query = {
            "semantic_type": "innovation_generation",
            "task": "innovative_solution_generation",
            "problem": problem,
            "explore": [
                "unconventional_approaches",
                "emerging_technologies",
                "paradigm_shifts",
                "creative_combinations",
                "future_oriented_solutions"
            ],
            "balance": "innovative_yet_practical",
            "thinking_mode": "lateral"
        }

        innovations = await self._call_vllm(innovation_query, temperature=0.8)

        return {
            "semantic_type": "innovation_result",
            "innovative_approaches": innovations.get("approaches", []),
            "emerging_tech_opportunities": innovations.get("technologies", []),
            "paradigm_shifts": innovations.get("shifts", []),
            "creative_combinations": innovations.get("combinations", []),
            "feasibility_notes": innovations.get("feasibility", []),
            "implementation_pathways": innovations.get("pathways", [])
        }

    async def _identify_emerging_tech(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Identify emerging technologies relevant to the problem
        """

        domain = query_csdl.get("domain", "")

        tech_query = {
            "semantic_type": "emerging_tech_identification",
            "task": "emerging_technology_identification",
            "domain": domain,
            "timeframe": "next_2_5_years",
            "identify": [
                "cutting_edge_technologies",
                "maturity_assessment",
                "applicability",
                "adoption_timeline",
                "potential_impact"
            ]
        }

        technologies = await self._call_vllm(tech_query, temperature=0.6)

        return {
            "semantic_type": "emerging_tech_result",
            "technologies": technologies.get("technologies", []),
            "maturity_levels": technologies.get("maturity", {}),
            "applicability_assessment": technologies.get("applicability", []),
            "recommended_exploration": technologies.get("recommendations", []),
            "potential_impact": technologies.get("impact", {})
        }

    async def _suggest_paradigm_shift(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Suggest paradigm shifts and radical rethinking
        """

        current_approach = query_csdl.get("current_approach", {})

        paradigm_query = {
            "semantic_type": "paradigm_shift",
            "task": "paradigm_shift_exploration",
            "current_paradigm": current_approach,
            "question": [
                "fundamental_assumptions",
                "alternative_frameworks",
                "radical_rethinking",
                "opposite_approach",
                "future_state"
            ]
        }

        shifts = await self._call_vllm(paradigm_query, temperature=0.7)

        return {
            "semantic_type": "paradigm_shift_result",
            "paradigm_shifts": shifts.get("shifts", []),
            "challenged_assumptions": shifts.get("assumptions", []),
            "alternative_frameworks": shifts.get("frameworks", []),
            "radical_approaches": shifts.get("radical", []),
            "transformation_pathway": shifts.get("pathway", {})
        }

    async def _creative_problem_solving(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Creative problem solving with unconventional methods
        """

        problem = query_csdl.get("problem", {})

        creative_query = {
            "semantic_type": "creative_problem_solving",
            "task": "creative_problem_solving",
            "problem": problem,
            "techniques": [
                "lateral_thinking",
                "analogical_reasoning",
                "constraint_removal",
                "perspective_shifting",
                "combination_innovation"
            ]
        }

        solutions = await self._call_vllm(creative_query, temperature=0.7)

        return {
            "semantic_type": "creative_solution_result",
            "creative_solutions": solutions.get("solutions", []),
            "analogies_used": solutions.get("analogies", []),
            "constraints_removed": solutions.get("constraints_removed", []),
            "new_perspectives": solutions.get("perspectives", []),
            "feasibility_assessment": solutions.get("feasibility", {})
        }

    async def _general_innovation(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """General innovation exploration"""

        innovation_query = {
            "semantic_type": "general_innovation",
            "task": "innovation_exploration",
            "context": query_csdl,
            "mode": "creative_and_practical"
        }

        result = await self._call_vllm(innovation_query, temperature=0.7)

        return result
