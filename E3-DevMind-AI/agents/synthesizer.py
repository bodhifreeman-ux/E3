"""
Agent #25: SYNTHESIZER (Insight Generator)

Combines insights from multiple agents and sources to generate novel insights.
"""

from agents.base_agent import BaseAgent
from csdl.protocol import CSDLMessage
from typing import Dict, Any, Optional, List
import structlog

logger = structlog.get_logger()


class SynthesizerAgent(BaseAgent):
    """SYNTHESIZER - Insight Generator Agent"""

    def __init__(self, vllm_client, knowledge_base, config=None):
        super().__init__(
            agent_id="synthesizer",
            agent_name="Synthesizer",
            vllm_client=vllm_client,
            knowledge_base=knowledge_base,
            config=config
        )
        self.synthesis_history: List[Dict[str, Any]] = []

    def _build_system_context(self) -> Dict[str, Any]:
        return {
            "role": "insight_generation",
            "agent_id": "synthesizer",
            "agent_name": "Synthesizer",
            "tier": 5,
            "capabilities": [
                "multi_source_synthesis",
                "insight_generation",
                "cross_domain_connection",
                "pattern_synthesis",
                "knowledge_fusion"
            ],
            "specialization": "insight_synthesis"
        }

    async def process_csdl(self, message: CSDLMessage, context: Optional[Dict[str, Any]] = None) -> CSDLMessage:
        """Process synthesis request"""
        query_type = message.content.get("query_type", "synthesize")

        if query_type == "synthesize":
            result = await self._synthesize_insights(message.content)
        elif query_type == "connect":
            result = await self._connect_insights(message.content)
        elif query_type == "fuse":
            result = await self._fuse_knowledge(message.content)
        else:
            result = await self._generate_insights(message.content)

        from csdl.protocol import CSDLProtocol
        return CSDLProtocol.create_response(
            content_csdl=result, sender_id=self.agent_id,
            in_response_to=message.message_id, recipient_id=message.sender_id
        )

    async def _synthesize_insights(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize insights from multiple sources"""
        sources = query_csdl.get("sources", [])
        context_data = query_csdl.get("context", {})

        synthesis_query = {
            "semantic_type": "multi_source_synthesis",
            "task": "insight_synthesis",
            "sources": sources,
            "context": context_data,
            "synthesis_approach": [
                "identify_common_themes",
                "resolve_contradictions",
                "identify_gaps",
                "generate_higher_order_insights",
                "create_unified_perspective"
            ],
            "output_requirements": [
                "coherent_narrative",
                "supporting_evidence",
                "confidence_levels",
                "alternative_interpretations"
            ]
        }

        synthesis = await self._call_vllm(synthesis_query, temperature=0.4)

        # Record synthesis
        synthesis_record = {
            "sources": len(sources),
            "synthesis": synthesis,
            "timestamp": "now"
        }
        self.synthesis_history.append(synthesis_record)

        return {
            "semantic_type": "synthesis_result",
            "synthesis": synthesis,
            "source_count": len(sources),
            "confidence": synthesis.get("confidence", 0.0)
        }

    async def _connect_insights(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Connect insights across domains"""
        insights = query_csdl.get("insights", [])

        connection_query = {
            "semantic_type": "cross_domain_connection",
            "task": "insight_connection",
            "insights": insights,
            "connection_types": [
                "causal_relationships",
                "analogical_reasoning",
                "complementary_patterns",
                "synergistic_opportunities"
            ]
        }

        connections = await self._call_vllm(connection_query, temperature=0.5)

        return {
            "semantic_type": "connection_result",
            "connections": connections,
            "insight_count": len(insights)
        }

    async def _fuse_knowledge(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Fuse knowledge from different domains"""
        knowledge_areas = query_csdl.get("knowledge_areas", [])

        fusion_query = {
            "semantic_type": "knowledge_fusion",
            "task": "cross_domain_fusion",
            "knowledge_areas": knowledge_areas,
            "fusion_strategy": [
                "identify_transferable_concepts",
                "bridge_terminology_differences",
                "synthesize_methodologies",
                "create_integrated_framework"
            ]
        }

        fusion = await self._call_vllm(fusion_query, temperature=0.5)

        return {
            "semantic_type": "fusion_result",
            "fusion": fusion,
            "domains_fused": len(knowledge_areas)
        }

    async def _generate_insights(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Generate novel insights from data"""
        data = query_csdl.get("data", {})
        focus = query_csdl.get("focus", "general")

        insight_query = {
            "semantic_type": "insight_generation",
            "task": "novel_insight_generation",
            "data": data,
            "focus": focus,
            "insight_types": [
                "non_obvious_patterns",
                "emergent_properties",
                "strategic_implications",
                "actionable_recommendations"
            ]
        }

        insights = await self._call_vllm(insight_query, temperature=0.6)

        return {
            "semantic_type": "insight_result",
            "insights": insights,
            "focus": focus,
            "novelty_score": insights.get("novelty_score", 0.0)
        }
