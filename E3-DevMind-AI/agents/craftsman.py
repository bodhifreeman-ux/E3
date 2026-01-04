"""
Agent #14: CRAFTSMAN (Code Quality)

Code review and quality assurance expert.
"""

from agents.base_agent import BaseAgent
from csdl.protocol import CSDLMessage
from typing import Dict, Any, Optional
import structlog

logger = structlog.get_logger()


class CraftsmanAgent(BaseAgent):
    """
    CRAFTSMAN - Code Quality Agent
    
    Capabilities:
    - Code review
    - Quality standards enforcement
    - Best practices validation
    - Technical debt identification
    - Refactoring suggestions
    - Style consistency
    """
    
    def __init__(self, vllm_client, knowledge_base, config=None):
        super().__init__(
            agent_id="craftsman",
            agent_name="Craftsman",
            vllm_client=vllm_client,
            knowledge_base=knowledge_base,
            config=config
        )
    
    def _build_system_context(self) -> Dict[str, Any]:
        return {
            "role": "code_quality",
            "agent_id": "craftsman",
            "agent_name": "Craftsman",
            "tier": 4,
            "capabilities": [
                "code_review",
                "quality_validation",
                "best_practices",
                "technical_debt",
                "refactoring_suggestions"
            ],
            "specialization": "code_quality_assurance"
        }
    
    async def process_csdl(
        self,
        message: CSDLMessage,
        context: Optional[Dict[str, Any]] = None
    ) -> CSDLMessage:
        """Review code for quality"""
        
        query_type = message.content.get("query_type", "code_review")
        
        if query_type == "code_review":
            result = await self._review_code(message.content)
        elif query_type == "technical_debt":
            result = await self._identify_technical_debt(message.content)
        else:
            result = await self._quality_analysis(message.content)
        
        from csdl.protocol import CSDLProtocol
        
        return CSDLProtocol.create_response(
            content_csdl=result,
            sender_id=self.agent_id,
            in_response_to=message.message_id,
            recipient_id=message.sender_id
        )
    
    async def _review_code(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive code review"""
        
        code = query_csdl.get("code", "")
        
        review_query = {
            "semantic_type": "code_review",
            "task": "code_review",
            "code": code,
            "review_for": [
                "correctness",
                "efficiency",
                "readability",
                "maintainability",
                "security",
                "scalability"
            ]
        }
        
        review = await self._call_vllm(review_query, temperature=0.2)
        
        return {
            "semantic_type": "code_review_result",
            "quality_score": review.get("score", 0.0),
            "issues": review.get("issues", []),
            "suggestions": review.get("suggestions", []),
            "best_practices": review.get("best_practices", [])
        }
    
    async def _identify_technical_debt(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Identify technical debt"""
        
        codebase = query_csdl.get("codebase", {})
        
        debt_query = {
            "semantic_type": "technical_debt",
            "task": "technical_debt_identification",
            "codebase": codebase,
            "identify": [
                "code_smells",
                "outdated_patterns",
                "missing_tests",
                "poor_documentation",
                "coupling_issues"
            ]
        }
        
        debt = await self._call_vllm(debt_query, temperature=0.3)
        
        return {
            "semantic_type": "technical_debt_result",
            "debt_items": debt.get("items", []),
            "priority": debt.get("priority", []),
            "estimated_effort": debt.get("effort", {})
        }
    
    async def _quality_analysis(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """General quality analysis"""
        
        quality_query = {
            "semantic_type": "quality_analysis",
            "task": "code_quality_analysis",
            "subject": query_csdl
        }
        
        result = await self._call_vllm(quality_query, temperature=0.2)
        
        return result
