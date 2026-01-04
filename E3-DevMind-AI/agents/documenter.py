"""
Agent #19: DOCUMENTER (Documentation Expert)

Technical documentation generation expert.
"""

from agents.base_agent import BaseAgent
from csdl.protocol import CSDLMessage
from typing import Dict, Any, Optional
import structlog

logger = structlog.get_logger()


class DocumenterAgent(BaseAgent):
    """DOCUMENTER - Documentation Expert Agent"""
    
    def __init__(self, vllm_client, knowledge_base, config=None):
        super().__init__(
            agent_id="documenter",
            agent_name="Documenter",
            vllm_client=vllm_client,
            knowledge_base=knowledge_base,
            config=config
        )
    
    def _build_system_context(self) -> Dict[str, Any]:
        return {
            "role": "documentation",
            "agent_id": "documenter",
            "agent_name": "Documenter",
            "tier": 4,
            "capabilities": [
                "technical_documentation",
                "api_documentation",
                "user_guides",
                "code_comments"
            ]
        }
    
    async def process_csdl(self, message: CSDLMessage, context: Optional[Dict[str, Any]] = None) -> CSDLMessage:
        query_type = message.content.get("query_type", "documentation")
        
        if query_type == "api_docs":
            result = await self._document_api(message.content)
        elif query_type == "user_guide":
            result = await self._create_user_guide(message.content)
        else:
            result = await self._generate_documentation(message.content)
        
        from csdl.protocol import CSDLProtocol
        return CSDLProtocol.create_response(
            content_csdl=result, sender_id=self.agent_id,
            in_response_to=message.message_id, recipient_id=message.sender_id
        )
    
    async def _document_api(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        api = query_csdl.get("api", {})
        doc_query = {
            "semantic_type": "api_documentation",
            "task": "api_documentation_generation",
            "api": api
        }
        docs = await self._call_vllm(doc_query, temperature=0.2)
        return {"semantic_type": "api_docs_result", "documentation": docs}
    
    async def _create_user_guide(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        feature = query_csdl.get("feature", {})
        guide_query = {
            "semantic_type": "user_guide",
            "task": "user_guide_creation",
            "feature": feature
        }
        guide = await self._call_vllm(guide_query, temperature=0.3)
        return {"semantic_type": "user_guide_result", "guide": guide}
    
    async def _generate_documentation(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        return await self._call_vllm({
            "semantic_type": "documentation_generation",
            "task": "documentation_generation",
            "subject": query_csdl
        }, temperature=0.2)
