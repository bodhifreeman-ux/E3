"""
Agent #6: INVESTIGATOR (Technical Analyzer)

Deep technical analysis and root cause investigation.
"""

from agents.base_agent import BaseAgent
from csdl.protocol import CSDLMessage
from typing import Dict, Any, Optional, List
import structlog

logger = structlog.get_logger()


class InvestigatorAgent(BaseAgent):
    """
    INVESTIGATOR - Technical Analyzer Agent

    Capabilities:
    - Root cause analysis
    - Complex problem decomposition
    - Technical feasibility studies
    - Deep architecture analysis
    - System behavior analysis
    - Performance profiling
    """

    def __init__(self, vllm_client, knowledge_base, config=None):
        super().__init__(
            agent_id="investigator",
            agent_name="Investigator",
            vllm_client=vllm_client,
            knowledge_base=knowledge_base,
            config=config
        )

    def _build_system_context(self) -> Dict[str, Any]:
        return {
            "role": "technical_analysis",
            "agent_id": "investigator",
            "agent_name": "Investigator",
            "tier": 3,
            "capabilities": [
                "root_cause_analysis",
                "problem_decomposition",
                "feasibility_studies",
                "architecture_analysis",
                "system_behavior_analysis",
                "performance_profiling"
            ],
            "specialization": "deep_technical_investigation",
            "outputs": "detailed_technical_findings"
        }

    async def process_csdl(
        self,
        message: CSDLMessage,
        context: Optional[Dict[str, Any]] = None
    ) -> CSDLMessage:
        """Deep technical investigation"""

        query_type = message.content.get("query_type", "root_cause")

        logger.info(
            "investigator_processing",
            query_type=query_type,
            message_id=message.message_id
        )

        if query_type == "root_cause":
            result = await self._root_cause_analysis(message.content)
        elif query_type == "decomposition":
            result = await self._decompose_problem(message.content)
        elif query_type == "feasibility":
            result = await self._feasibility_study(message.content)
        elif query_type == "architecture_analysis":
            result = await self._analyze_architecture(message.content)
        elif query_type == "system_behavior":
            result = await self._analyze_system_behavior(message.content)
        else:
            result = await self._general_investigation(message.content)

        from csdl.protocol import CSDLProtocol

        return CSDLProtocol.create_response(
            content_csdl=result,
            sender_id=self.agent_id,
            in_response_to=message.message_id,
            recipient_id=message.sender_id
        )

    async def _root_cause_analysis(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Deep root cause analysis

        Uses:
        - 5 Whys technique
        - Fishbone diagram logic
        - System analysis
        - Historical pattern matching
        """

        issue = query_csdl.get("issue", {})

        # Gather context from knowledge base
        context = await self.retrieve_knowledge(
            {"related_to": issue.get("description", ""), "type": "technical"},
            limit=15
        )

        rca_query = {
            "semantic_type": "root_cause_analysis",
            "task": "root_cause_analysis",
            "issue": issue,
            "context": context,
            "symptoms": query_csdl.get("symptoms", []),
            "timeline": query_csdl.get("timeline", {}),
            "methodology": "5_whys_and_fishbone",
            "investigate": [
                "immediate_cause",
                "contributing_factors",
                "underlying_root_cause",
                "system_vulnerabilities",
                "prevention_measures"
            ]
        }

        analysis = await self._call_vllm(rca_query, temperature=0.2)

        return {
            "semantic_type": "root_cause_result",
            "root_cause": analysis.get("root_cause", ""),
            "causal_chain": analysis.get("causal_chain", []),
            "contributing_factors": analysis.get("factors", []),
            "evidence": analysis.get("evidence", []),
            "prevention_recommendations": analysis.get("prevention", []),
            "confidence": analysis.get("confidence", 0.0),
            "methodology_used": "5_whys_and_fishbone"
        }

    async def _decompose_problem(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Break down complex problem into manageable parts
        """

        problem = query_csdl.get("problem", {})

        decomposition_query = {
            "semantic_type": "problem_decomposition",
            "task": "problem_decomposition",
            "problem": problem,
            "decompose_into": [
                "core_components",
                "dependencies",
                "interfaces",
                "constraints",
                "sub_problems"
            ],
            "create_hierarchy": True
        }

        decomposition = await self._call_vllm(decomposition_query, temperature=0.3)

        return {
            "semantic_type": "decomposition_result",
            "components": decomposition.get("components", []),
            "hierarchy": decomposition.get("hierarchy", {}),
            "dependencies": decomposition.get("dependencies", []),
            "complexity_assessment": decomposition.get("complexity", {}),
            "recommended_approach": decomposition.get("approach", ""),
            "sub_problems": decomposition.get("sub_problems", [])
        }

    async def _feasibility_study(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Technical feasibility analysis
        """

        proposal = query_csdl.get("proposal", {})

        feasibility_query = {
            "semantic_type": "feasibility_study",
            "task": "technical_feasibility_study",
            "proposal": proposal,
            "assess": [
                "technical_viability",
                "implementation_complexity",
                "resource_requirements",
                "risk_factors",
                "timeline_realism",
                "alternatives"
            ]
        }

        study = await self._call_vllm(feasibility_query, temperature=0.3)

        return {
            "semantic_type": "feasibility_result",
            "feasibility_score": study.get("score", 0.0),
            "technical_challenges": study.get("challenges", []),
            "required_capabilities": study.get("capabilities", []),
            "estimated_effort": study.get("effort", {}),
            "risk_assessment": study.get("risks", []),
            "recommendation": study.get("recommendation", ""),
            "alternatives": study.get("alternatives", [])
        }

    async def _analyze_architecture(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Deep architecture analysis
        """

        architecture = query_csdl.get("architecture", {})

        analysis_query = {
            "semantic_type": "architecture_analysis",
            "task": "architecture_analysis",
            "architecture": architecture,
            "analyze": [
                "component_design",
                "coupling_and_cohesion",
                "scalability",
                "performance_characteristics",
                "security_posture",
                "maintainability"
            ]
        }

        analysis = await self._call_vllm(analysis_query, temperature=0.3)

        return {
            "semantic_type": "architecture_analysis_result",
            "strengths": analysis.get("strengths", []),
            "weaknesses": analysis.get("weaknesses", []),
            "bottlenecks": analysis.get("bottlenecks", []),
            "security_concerns": analysis.get("security", []),
            "scalability_assessment": analysis.get("scalability", {}),
            "recommendations": analysis.get("recommendations", [])
        }

    async def _analyze_system_behavior(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze system behavior and performance
        """

        system_data = query_csdl.get("system_data", {})

        behavior_query = {
            "semantic_type": "behavior_analysis",
            "task": "system_behavior_analysis",
            "data": system_data,
            "analyze": [
                "performance_patterns",
                "resource_utilization",
                "bottlenecks",
                "anomalies",
                "optimization_opportunities"
            ]
        }

        analysis = await self._call_vllm(behavior_query, temperature=0.3)

        return {
            "semantic_type": "behavior_analysis_result",
            "performance_patterns": analysis.get("patterns", []),
            "bottlenecks_identified": analysis.get("bottlenecks", []),
            "anomalies": analysis.get("anomalies", []),
            "optimization_opportunities": analysis.get("optimizations", []),
            "recommendations": analysis.get("recommendations", [])
        }

    async def _general_investigation(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """General technical investigation"""

        investigation_query = {
            "semantic_type": "general_investigation",
            "task": "technical_investigation",
            "subject": query_csdl,
            "approach": "systematic_analysis"
        }

        result = await self._call_vllm(investigation_query, temperature=0.3)

        return result
