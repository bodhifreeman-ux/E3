"""
Agent #7: CRITIC (Devil's Advocate)

Finds flaws, challenges proposals, ensures quality through constructive criticism.
"""

from agents.base_agent import BaseAgent
from csdl.protocol import CSDLMessage
from typing import Dict, Any, Optional, List
import structlog

logger = structlog.get_logger()


class CriticAgent(BaseAgent):
    """
    CRITIC - Devil's Advocate Agent

    Capabilities:
    - Identifies weaknesses in proposals
    - Security vulnerability assessment
    - Edge case discovery
    - Quality assurance
    - Assumption challenging
    - Risk identification
    """

    def __init__(self, vllm_client, knowledge_base, config=None):
        super().__init__(
            agent_id="critic",
            agent_name="Critic",
            vllm_client=vllm_client,
            knowledge_base=knowledge_base,
            config=config
        )

    def _build_system_context(self) -> Dict[str, Any]:
        return {
            "role": "quality_assurance_through_criticism",
            "agent_id": "critic",
            "agent_name": "Critic",
            "tier": 3,
            "capabilities": [
                "flaw_identification",
                "risk_assessment",
                "edge_case_discovery",
                "assumption_challenging",
                "security_analysis",
                "quality_validation"
            ],
            "mode": "constructive_criticism",
            "perspective": "skeptical_yet_helpful"
        }

    async def process_csdl(
        self,
        message: CSDLMessage,
        context: Optional[Dict[str, Any]] = None
    ) -> CSDLMessage:
        """Find flaws and risks in proposals"""

        query_type = message.content.get("query_type", "general_critique")

        logger.info(
            "critic_processing",
            query_type=query_type,
            message_id=message.message_id
        )

        if query_type == "proposal_critique":
            result = await self._critique_proposal(message.content)
        elif query_type == "security_assessment":
            result = await self._assess_security(message.content)
        elif query_type == "edge_case_discovery":
            result = await self._discover_edge_cases(message.content)
        elif query_type == "quality_review":
            result = await self._review_quality(message.content)
        else:
            result = await self._general_critique(message.content)

        from csdl.protocol import CSDLProtocol

        return CSDLProtocol.create_response(
            content_csdl=result,
            sender_id=self.agent_id,
            in_response_to=message.message_id,
            recipient_id=message.sender_id
        )

    async def _critique_proposal(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Comprehensive proposal critique

        Asks:
        - What could go wrong?
        - What are we missing?
        - What assumptions are invalid?
        - What edge cases exist?
        """

        proposal = query_csdl.get("proposal", {})

        critique_query = {
            "semantic_type": "proposal_critique",
            "task": "critical_analysis",
            "subject": proposal,
            "find": [
                "flaws",
                "risks",
                "edge_cases",
                "invalid_assumptions",
                "missing_considerations",
                "potential_failures"
            ],
            "mode": "constructive",
            "perspective": "devils_advocate"
        }

        critique = await self._call_vllm(critique_query, temperature=0.4)

        return {
            "semantic_type": "critique_result",
            "flaws_identified": critique.get("flaws", []),
            "risks": critique.get("risks", []),
            "edge_cases": critique.get("edge_cases", []),
            "invalid_assumptions": critique.get("assumptions", []),
            "missing_considerations": critique.get("missing", []),
            "improvement_recommendations": critique.get("improvements", []),
            "severity_assessment": critique.get("severity", {})
        }

    async def _assess_security(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Security vulnerability assessment
        """

        system = query_csdl.get("system", {})

        security_query = {
            "semantic_type": "security_assessment",
            "task": "security_vulnerability_assessment",
            "system": system,
            "check_for": [
                "authentication_issues",
                "authorization_gaps",
                "injection_vulnerabilities",
                "data_exposure_risks",
                "cryptography_weaknesses",
                "dependency_vulnerabilities"
            ],
            "standard": "OWASP_Top_10"
        }

        assessment = await self._call_vllm(security_query, temperature=0.3)

        return {
            "semantic_type": "security_assessment_result",
            "vulnerabilities": assessment.get("vulnerabilities", []),
            "security_score": assessment.get("score", 0.0),
            "critical_issues": assessment.get("critical", []),
            "recommendations": assessment.get("recommendations", []),
            "compliance_status": assessment.get("compliance", {})
        }

    async def _discover_edge_cases(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Discover edge cases and boundary conditions
        """

        feature = query_csdl.get("feature", {})

        edge_case_query = {
            "semantic_type": "edge_case_discovery",
            "task": "edge_case_identification",
            "feature": feature,
            "explore": [
                "boundary_conditions",
                "null_and_empty_inputs",
                "extreme_values",
                "concurrent_operations",
                "error_conditions",
                "unexpected_sequences"
            ]
        }

        edge_cases = await self._call_vllm(edge_case_query, temperature=0.5)

        return {
            "semantic_type": "edge_case_result",
            "edge_cases": edge_cases.get("cases", []),
            "boundary_conditions": edge_cases.get("boundaries", []),
            "failure_scenarios": edge_cases.get("failures", []),
            "test_recommendations": edge_cases.get("tests", [])
        }

    async def _review_quality(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Quality review and validation
        """

        subject = query_csdl.get("subject", {})

        quality_query = {
            "semantic_type": "quality_review",
            "task": "quality_validation",
            "subject": subject,
            "evaluate": [
                "correctness",
                "completeness",
                "maintainability",
                "performance",
                "security",
                "usability"
            ]
        }

        review = await self._call_vllm(quality_query, temperature=0.3)

        return {
            "semantic_type": "quality_review_result",
            "quality_score": review.get("score", 0.0),
            "strengths": review.get("strengths", []),
            "weaknesses": review.get("weaknesses", []),
            "critical_issues": review.get("critical", []),
            "recommendations": review.get("recommendations", [])
        }

    async def _general_critique(
        self,
        query_csdl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """General critical analysis"""

        critique_query = {
            "semantic_type": "general_critique",
            "task": "critical_analysis",
            "subject": query_csdl,
            "mode": "constructive_criticism"
        }

        critique = await self._call_vllm(critique_query, temperature=0.4)

        return critique
