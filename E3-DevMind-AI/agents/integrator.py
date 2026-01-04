"""
Agent #20: INTEGRATOR (Systems Integration)

Third-party integration and API design expert.
"""

from agents.base_agent import BaseAgent
from csdl.protocol import CSDLMessage
from typing import Dict, Any, Optional
import structlog

logger = structlog.get_logger()


class IntegratorAgent(BaseAgent):
    """INTEGRATOR - Systems Integration Agent"""
    
    def __init__(self, vllm_client, knowledge_base, config=None):
        super().__init__(
            agent_id="integrator",
            agent_name="Integrator",
            vllm_client=vllm_client,
            knowledge_base=knowledge_base,
            config=config
        )
    
    def _build_system_context(self) -> Dict[str, Any]:
        return {
            "role": "systems_integration",
            "agent_id": "integrator",
            "agent_name": "Integrator",
            "tier": 4,
            "capabilities": [
                "api_design",
                "integration_architecture",
                "third_party_integration",
                "data_synchronization"
            ]
        }
    
    async def process_csdl(self, message: CSDLMessage, context: Optional[Dict[str, Any]] = None) -> CSDLMessage:
        query_type = message.content.get("query_type", "api_design")
        
        if query_type == "api_design":
            result = await self._design_api(message.content)
        elif query_type == "integration":
            result = await self._design_integration(message.content)
        else:
            result = await self._general_integration(message.content)
        
        from csdl.protocol import CSDLProtocol
        return CSDLProtocol.create_response(
            content_csdl=result, sender_id=self.agent_id,
            in_response_to=message.message_id, recipient_id=message.sender_id
        )
    
    async def _design_api(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        requirements = query_csdl.get("requirements", {})
        api_query = {
            "semantic_type": "api_design",
            "task": "api_design",
            "requirements": requirements
        }
        design = await self._call_vllm(api_query, temperature=0.3)
        return {"semantic_type": "api_design_result", "design": design}
    
    async def _design_integration(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        systems = query_csdl.get("systems", [])
        integration_query = {
            "semantic_type": "integration_design",
            "task": "integration_design",
            "systems": systems
        }
        design = await self._call_vllm(integration_query, temperature=0.3)
        return {"semantic_type": "integration_result", "design": design}
    
    async def _general_integration(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        return await self._call_vllm({
            "semantic_type": "general_integration",
            "task": "integration_planning",
            "context": query_csdl
        }, temperature=0.3)
