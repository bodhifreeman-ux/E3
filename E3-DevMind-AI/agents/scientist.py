"""
Agent #15: SCIENTIST (Testing & Validation)

Test strategy and quality validation expert.
"""

from agents.base_agent import BaseAgent
from csdl.protocol import CSDLMessage
from typing import Dict, Any, Optional
import structlog

logger = structlog.get_logger()


class ScientistAgent(BaseAgent):
    """SCIENTIST - Testing & Validation Agent"""
    
    def __init__(self, vllm_client, knowledge_base, config=None):
        super().__init__(
            agent_id="scientist",
            agent_name="Scientist",
            vllm_client=vllm_client,
            knowledge_base=knowledge_base,
            config=config
        )
    
    def _build_system_context(self) -> Dict[str, Any]:
        return {
            "role": "testing_validation",
            "agent_id": "scientist",
            "agent_name": "Scientist",
            "tier": 4,
            "capabilities": [
                "test_strategy",
                "test_generation",
                "coverage_analysis",
                "quality_validation"
            ]
        }
    
    async def process_csdl(self, message: CSDLMessage, context: Optional[Dict[str, Any]] = None) -> CSDLMessage:
        query_type = message.content.get("query_type", "test_generation")
        
        if query_type == "test_generation":
            result = await self._generate_tests(message.content)
        elif query_type == "test_strategy":
            result = await self._design_test_strategy(message.content)
        else:
            result = await self._validate_quality(message.content)
        
        from csdl.protocol import CSDLProtocol
        return CSDLProtocol.create_response(
            content_csdl=result, sender_id=self.agent_id,
            in_response_to=message.message_id, recipient_id=message.sender_id
        )
    
    async def _generate_tests(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        code = query_csdl.get("code", "")
        test_query = {
            "semantic_type": "test_generation",
            "task": "test_generation",
            "code": code,
            "generate": ["unit_tests", "integration_tests", "edge_cases"]
        }
        tests = await self._call_vllm(test_query, temperature=0.2)
        return {"semantic_type": "test_result", "tests": tests.get("tests", [])}
    
    async def _design_test_strategy(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        project = query_csdl.get("project", {})
        strategy_query = {
            "semantic_type": "test_strategy",
            "task": "test_strategy_design",
            "project": project
        }
        strategy = await self._call_vllm(strategy_query, temperature=0.3)
        return {"semantic_type": "strategy_result", "strategy": strategy}
    
    async def _validate_quality(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        return await self._call_vllm({
            "semantic_type": "quality_validation",
            "task": "quality_validation",
            "subject": query_csdl
        }, temperature=0.2)
