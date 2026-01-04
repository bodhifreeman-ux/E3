"""
Agent #17: OPS (DevOps & Infrastructure)

Infrastructure and deployment expert.
"""

from agents.base_agent import BaseAgent
from csdl.protocol import CSDLMessage
from typing import Dict, Any, Optional
import structlog

logger = structlog.get_logger()


class OpsAgent(BaseAgent):
    """OPS - DevOps & Infrastructure Agent"""
    
    def __init__(self, vllm_client, knowledge_base, config=None):
        super().__init__(
            agent_id="ops",
            agent_name="Ops",
            vllm_client=vllm_client,
            knowledge_base=knowledge_base,
            config=config
        )
    
    def _build_system_context(self) -> Dict[str, Any]:
        return {
            "role": "devops_infrastructure",
            "agent_id": "ops",
            "agent_name": "Ops",
            "tier": 4,
            "capabilities": [
                "cicd_management",
                "infrastructure_optimization",
                "deployment_strategy",
                "monitoring_setup"
            ]
        }
    
    async def process_csdl(self, message: CSDLMessage, context: Optional[Dict[str, Any]] = None) -> CSDLMessage:
        query_type = message.content.get("query_type", "deployment")
        
        if query_type == "deployment":
            result = await self._plan_deployment(message.content)
        elif query_type == "cicd":
            result = await self._setup_cicd(message.content)
        else:
            result = await self._optimize_infrastructure(message.content)
        
        from csdl.protocol import CSDLProtocol
        return CSDLProtocol.create_response(
            content_csdl=result, sender_id=self.agent_id,
            in_response_to=message.message_id, recipient_id=message.sender_id
        )
    
    async def _plan_deployment(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        app = query_csdl.get("application", {})
        deploy_query = {
            "semantic_type": "deployment_planning",
            "task": "deployment_strategy",
            "application": app
        }
        plan = await self._call_vllm(deploy_query, temperature=0.2)
        return {"semantic_type": "deployment_plan", "plan": plan}
    
    async def _setup_cicd(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        return await self._call_vllm({
            "semantic_type": "cicd_setup",
            "task": "cicd_pipeline_setup",
            "project": query_csdl.get("project", {})
        }, temperature=0.2)
    
    async def _optimize_infrastructure(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        return await self._call_vllm({
            "semantic_type": "infrastructure_optimization",
            "task": "infrastructure_optimization",
            "current": query_csdl.get("current", {})
        }, temperature=0.3)
