"""
Agent #21: GUARDIAN (Reliability Engineer)

System reliability and resilience expert.
"""

from agents.base_agent import BaseAgent
from csdl.protocol import CSDLMessage
from typing import Dict, Any, Optional
import structlog

logger = structlog.get_logger()


class GuardianAgent(BaseAgent):
    """GUARDIAN - Reliability Engineer Agent"""
    
    def __init__(self, vllm_client, knowledge_base, config=None):
        super().__init__(
            agent_id="guardian",
            agent_name="Guardian",
            vllm_client=vllm_client,
            knowledge_base=knowledge_base,
            config=config
        )
    
    def _build_system_context(self) -> Dict[str, Any]:
        return {
            "role": "reliability_engineering",
            "agent_id": "guardian",
            "agent_name": "Guardian",
            "tier": 4,
            "capabilities": [
                "reliability_analysis",
                "failure_mode_analysis",
                "disaster_recovery",
                "resilience_design"
            ]
        }
    
    async def process_csdl(self, message: CSDLMessage, context: Optional[Dict[str, Any]] = None) -> CSDLMessage:
        query_type = message.content.get("query_type", "reliability_analysis")
        
        if query_type == "reliability_analysis":
            result = await self._analyze_reliability(message.content)
        elif query_type == "failure_mode":
            result = await self._analyze_failure_modes(message.content)
        else:
            result = await self._design_resilience(message.content)
        
        from csdl.protocol import CSDLProtocol
        return CSDLProtocol.create_response(
            content_csdl=result, sender_id=self.agent_id,
            in_response_to=message.message_id, recipient_id=message.sender_id
        )
    
    async def _analyze_reliability(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        system = query_csdl.get("system", {})
        reliability_query = {
            "semantic_type": "reliability_analysis",
            "task": "reliability_analysis",
            "system": system
        }
        analysis = await self._call_vllm(reliability_query, temperature=0.2)
        return {"semantic_type": "reliability_result", "analysis": analysis}
    
    async def _analyze_failure_modes(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        component = query_csdl.get("component", {})
        fmea_query = {
            "semantic_type": "failure_mode_analysis",
            "task": "failure_mode_analysis",
            "component": component
        }
        fmea = await self._call_vllm(fmea_query, temperature=0.2)
        return {"semantic_type": "fmea_result", "analysis": fmea}
    
    async def _design_resilience(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        return await self._call_vllm({
            "semantic_type": "resilience_design",
            "task": "resilience_design",
            "system": query_csdl.get("system", {})
        }, temperature=0.3)
