"""
Agent #3: SAGE (Meta-Reasoner)

Analyzes how the swarm thinks and improves decision-making processes.
"""

from agents.base_agent import BaseAgent
from csdl.protocol import CSDLMessage
from typing import Dict, Any, Optional, List
import structlog
from datetime import datetime

logger = structlog.get_logger()


class SageAgent(BaseAgent):
    """
    SAGE - Meta-Reasoner Agent

    Capabilities:
    - Analyzes swarm decision quality
    - Identifies process inefficiencies
    - Questions assumptions
    - Optimizes agent coordination
    - Self-improvement strategies
    - Cognitive bias detection
    """

    def __init__(self, vllm_client, knowledge_base, config=None):
        self.decision_history: List[Dict[str, Any]] = []
        self.improvement_suggestions: List[Dict[str, Any]] = []

        super().__init__(
            agent_id="sage",
            agent_name="Sage",
            vllm_client=vllm_client,
            knowledge_base=knowledge_base,
            config=config
        )

    def _build_system_context(self) -> Dict[str, Any]:
        return {
            "role": "meta_reasoning",
            "agent_id": "sage",
            "agent_name": "Sage",
            "tier": 2,
            "capabilities": [
                "decision_quality_analysis",
                "process_improvement",
                "assumption_challenging",
                "coordination_optimization",
                "self_improvement",
                "bias_detection"
            ],
            "specialization": "thinking_about_thinking",
            "outputs": "process_improvements_and_insights"
        }

    async def process_csdl(
        self,
        message: CSDLMessage,
        context: Optional[Dict[str, Any]] = None
    ) -> CSDLMessage:
        """
        Process meta-reasoning request

        Analyzes the quality of thinking and decision-making.
        """

        query_type = message.content.get("query_type", "general_meta_analysis")

        logger.info(
            "sage_processing",
            query_type=query_type,
            message_id=message.message_id
        )

        if query_type == "decision_quality":
            result = await self._analyze_decision_quality(message.content)
        elif query_type == "process_efficiency":
            result = await self._analyze_process_efficiency(message.content)
        elif query_type == "challenge_assumptions":
            result = await self._challenge_assumptions(message.content)
        elif query_type == "coordination_analysis":
            result = await self._analyze_coordination(message.content)
        elif query_type == "improvement_recommendations":
            result = await self._generate_improvements(message.content)
        else:
            result = await self._general_meta_analysis(message.content)

        from csdl.protocol import CSDLProtocol

        return CSDLProtocol.create_response(
            content_csdl=result,
            sender_id=self.agent_id,
            in_response_to=message.message_id,
            recipient_id=message.sender_id,
            metadata={
                "analysis_type": query_type,
                "meta_level": "second_order_thinking"
            }
        )

    async def _analyze_decision_quality(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze the quality of a decision or decision process

        Evaluates:
        - Information completeness
        - Reasoning soundness
        - Alternative consideration
        - Bias presence
        - Outcome prediction
        """

        decision_data = query_csdl.get("decision", {})

        analysis_query = {
            "semantic_type": "meta_analysis",
            "task": "decision_quality_analysis",
            "decision": decision_data,
            "context": query_csdl.get("context", {}),
            "evaluate": [
                "information_completeness",
                "logical_soundness",
                "alternatives_considered",
                "cognitive_biases",
                "risk_assessment_quality",
                "stakeholder_consideration"
            ]
        }

        analysis = await self._call_vllm(analysis_query, temperature=0.2)

        # Score the decision
        quality_score = self._calculate_decision_score(analysis)

        return {
            "semantic_type": "decision_analysis_result",
            "quality_score": quality_score,
            "strengths": analysis.get("strengths", []),
            "weaknesses": analysis.get("weaknesses", []),
            "biases_detected": analysis.get("biases", []),
            "missing_considerations": analysis.get("missing", []),
            "improvement_suggestions": analysis.get("improvements", []),
            "confidence": analysis.get("confidence", 0.8)
        }

    async def _analyze_process_efficiency(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze efficiency of agent coordination and processes

        Looks for:
        - Redundant work
        - Communication overhead
        - Bottlenecks in coordination
        - Suboptimal routing
        - Resource waste
        """

        # Get recent agent interactions
        interaction_history = query_csdl.get("interactions", [])

        efficiency_query = {
            "semantic_type": "efficiency_analysis",
            "task": "process_efficiency_analysis",
            "interactions": interaction_history,
            "metrics": query_csdl.get("metrics", {}),
            "identify": [
                "redundant_computations",
                "communication_overhead",
                "coordination_bottlenecks",
                "routing_inefficiencies",
                "resource_waste"
            ]
        }

        analysis = await self._call_vllm(efficiency_query, temperature=0.3)

        return {
            "semantic_type": "efficiency_analysis_result",
            "efficiency_score": analysis.get("efficiency_score", 0.0),
            "inefficiencies": analysis.get("inefficiencies", []),
            "optimization_opportunities": analysis.get("optimizations", []),
            "estimated_improvements": analysis.get("improvements", {}),
            "implementation_priority": analysis.get("priorities", [])
        }

    async def _challenge_assumptions(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Challenge assumptions in a plan, decision, or approach

        Questions:
        - What are we assuming?
        - Are these assumptions valid?
        - What if we're wrong?
        - What are alternative perspectives?
        """

        subject = query_csdl.get("subject", {})

        challenge_query = {
            "semantic_type": "assumption_challenge",
            "task": "assumption_challenging",
            "subject": subject,
            "extract_and_challenge": [
                "explicit_assumptions",
                "implicit_assumptions",
                "hidden_constraints",
                "accepted_norms",
                "conventional_wisdom"
            ],
            "mode": "constructive_skepticism"
        }

        analysis = await self._call_vllm(challenge_query, temperature=0.5)

        return {
            "semantic_type": "assumption_challenge_result",
            "assumptions_identified": analysis.get("assumptions", []),
            "validity_assessment": analysis.get("validity", []),
            "challenged_assumptions": analysis.get("challenges", []),
            "alternative_perspectives": analysis.get("alternatives", []),
            "risk_if_wrong": analysis.get("risks", []),
            "recommendations": analysis.get("recommendations", [])
        }

    async def _analyze_coordination(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze agent coordination patterns

        Evaluates:
        - Communication patterns
        - Task routing efficiency
        - Response time distribution
        - Collaboration quality
        """

        coordination_data = query_csdl.get("coordination", {})

        analysis_query = {
            "semantic_type": "coordination_analysis",
            "task": "coordination_analysis",
            "data": coordination_data,
            "analyze": [
                "communication_patterns",
                "routing_efficiency",
                "response_times",
                "collaboration_quality",
                "information_flow"
            ]
        }

        analysis = await self._call_vllm(analysis_query, temperature=0.3)

        return {
            "semantic_type": "coordination_analysis_result",
            "coordination_score": analysis.get("score", 0.0),
            "pattern_analysis": analysis.get("patterns", {}),
            "bottlenecks": analysis.get("bottlenecks", []),
            "optimization_suggestions": analysis.get("optimizations", []),
            "best_practices": analysis.get("best_practices", [])
        }

    async def _generate_improvements(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate self-improvement recommendations for the swarm
        """

        # Analyze recent performance
        performance_data = await self.retrieve_knowledge(
            {"topic": "agent_performance", "recent": True},
            limit=20
        )

        improvement_query = {
            "semantic_type": "improvement_generation",
            "task": "self_improvement_recommendations",
            "performance_data": performance_data,
            "current_challenges": query_csdl.get("challenges", []),
            "focus_areas": [
                "speed_improvements",
                "accuracy_improvements",
                "coordination_improvements",
                "resource_efficiency",
                "capability_gaps"
            ]
        }

        recommendations = await self._call_vllm(improvement_query, temperature=0.4)

        return {
            "semantic_type": "improvement_recommendations",
            "improvements": recommendations.get("improvements", []),
            "priority_ranking": recommendations.get("priorities", []),
            "expected_impact": recommendations.get("impact", {}),
            "implementation_complexity": recommendations.get("complexity", {}),
            "quick_wins": recommendations.get("quick_wins", [])
        }

    async def _general_meta_analysis(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """General meta-cognitive analysis"""

        analysis_query = {
            "semantic_type": "general_meta_analysis",
            "task": "general_meta_analysis",
            "subject": query_csdl,
            "perspective": "second_order_thinking"
        }

        analysis = await self._call_vllm(analysis_query, temperature=0.4)

        return analysis

    def _calculate_decision_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall decision quality score"""

        strengths = len(analysis.get("strengths", []))
        weaknesses = len(analysis.get("weaknesses", []))
        biases = len(analysis.get("biases", []))

        # Simple scoring formula
        score = max(0.0, min(1.0,
            0.7 + (strengths * 0.05) - (weaknesses * 0.1) - (biases * 0.15)
        ))

        return round(score, 2)
