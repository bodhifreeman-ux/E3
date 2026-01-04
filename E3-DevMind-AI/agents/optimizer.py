"""
Agent #18: OPTIMIZER (Performance Engineer)

Performance analysis and optimization expert.
"""

from agents.base_agent import BaseAgent
from csdl.protocol import CSDLMessage
from typing import Dict, Any, Optional
import structlog

logger = structlog.get_logger()


class OptimizerAgent(BaseAgent):
    """OPTIMIZER - Performance Engineer Agent"""
    
    def __init__(self, vllm_client, knowledge_base, config=none):
        super().__init__(
            agent_id="optimizer",
            agent_name="Optimizer",
            vllm_client=vllm_client,
            knowledge_base=knowledge_base,
            config=config
        )
    
    def _build_system_context(self) -> Dict[str, Any]:
        return {
            "role": "performance_optimization",
            "agent_id": "optimizer",
            "agent_name": "Optimizer",
            "tier": 4,
            "capabilities": [
                "performance_profiling",
                "bottleneck_identification",
                "query_optimization",
                "caching_strategy"
            ]
        }
    
    async def process_csdl(self, message: CSDLMessage, context: Optional[Dict[str, Any]] = None) -> CSDLMessage:
        query_type = message.content.get("query_type", "performance_analysis")
        
        if query_type == "performance_analysis":
            result = await self._analyze_performance(message.content)
        elif query_type == "optimization":
            result = await self._optimize_code(message.content)
        else:
            result = await self._identify_bottlenecks(message.content)
        
        from csdl.protocol import CSDLProtocol
        return CSDLProtocol.create_response(
            content_csdl=result, sender_id=self.agent_id,
            in_response_to=message.message_id, recipient_id=message.sender_id
        )
    
    async def _analyze_performance(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        system = query_csdl.get("system", {})
        perf_query = {
            "semantic_type": "performance_analysis",
            "task": "performance_profiling",
            "system": system
        }
        analysis = await self._call_vllm(perf_query, temperature=0.2)
        return {"semantic_type": "performance_result", "analysis": analysis}
    
    async def _optimize_code(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        code = query_csdl.get("code", "")
        opt_query = {
            "semantic_type": "code_optimization",
            "task": "code_optimization",
            "code": code
        }
        optimized = await self._call_vllm(opt_query, temperature=0.2)
        return {"semantic_type": "optimization_result", "optimized": optimized}
    
    async def _identify_bottlenecks(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        return await self._call_vllm({
            "semantic_type": "bottleneck_identification",
            "task": "bottleneck_identification",
            "metrics": query_csdl.get("metrics", {})
        }, temperature=0.2)
