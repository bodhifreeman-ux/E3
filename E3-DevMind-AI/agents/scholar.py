"""
Agent #24: SCHOLAR (Deep Researcher)

Research and external intelligence gathering expert.
"""

from agents.base_agent import BaseAgent
from csdl.protocol import CSDLMessage
from typing import Dict, Any, Optional, List
import structlog

logger = structlog.get_logger()


class ScholarAgent(BaseAgent):
    """SCHOLAR - Deep Researcher Agent"""

    def __init__(self, vllm_client, knowledge_base, config=None):
        super().__init__(
            agent_id="scholar",
            agent_name="Scholar",
            vllm_client=vllm_client,
            knowledge_base=knowledge_base,
            config=config
        )
        self.research_cache: Dict[str, Any] = {}

    def _build_system_context(self) -> Dict[str, Any]:
        return {
            "role": "research_intelligence",
            "agent_id": "scholar",
            "agent_name": "Scholar",
            "tier": 5,
            "capabilities": [
                "technology_research",
                "competitive_analysis",
                "academic_research",
                "trend_analysis",
                "external_intelligence"
            ],
            "specialization": "deep_research"
        }

    async def process_csdl(self, message: CSDLMessage, context: Optional[Dict[str, Any]] = None) -> CSDLMessage:
        """Process research request"""
        query_type = message.content.get("query_type", "research")

        if query_type == "research":
            result = await self._conduct_research(message.content)
        elif query_type == "competitive_analysis":
            result = await self._analyze_competition(message.content)
        elif query_type == "trend_analysis":
            result = await self._analyze_trends(message.content)
        else:
            result = await self._gather_intelligence(message.content)

        from csdl.protocol import CSDLProtocol
        return CSDLProtocol.create_response(
            content_csdl=result, sender_id=self.agent_id,
            in_response_to=message.message_id, recipient_id=message.sender_id
        )

    async def _conduct_research(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct deep research on a topic"""
        topic = query_csdl.get("topic", "")
        depth = query_csdl.get("depth", "comprehensive")

        # Check cache first
        cache_key = f"{topic}_{depth}"
        if cache_key in self.research_cache:
            logger.info("research_cache_hit", topic=topic)
            return self.research_cache[cache_key]

        research_query = {
            "semantic_type": "deep_research",
            "task": "comprehensive_research",
            "topic": topic,
            "depth": depth,
            "research_areas": [
                "current_state_of_art",
                "recent_developments",
                "key_players",
                "future_directions",
                "challenges_and_limitations"
            ],
            "sources": [
                "academic_papers",
                "industry_reports",
                "technical_documentation",
                "expert_opinions"
            ]
        }

        research = await self._call_vllm(research_query, temperature=0.3)

        # Cache result
        self.research_cache[cache_key] = {
            "semantic_type": "research_result",
            "topic": topic,
            "research": research,
            "depth": depth
        }

        return self.research_cache[cache_key]

    async def _analyze_competition(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze competitive landscape"""
        domain = query_csdl.get("domain", "")
        competitors = query_csdl.get("competitors", [])

        competitive_query = {
            "semantic_type": "competitive_analysis",
            "task": "competitive_intelligence",
            "domain": domain,
            "competitors": competitors,
            "analysis_dimensions": [
                "product_offerings",
                "technology_stack",
                "market_positioning",
                "strengths_weaknesses",
                "differentiation_opportunities"
            ]
        }

        analysis = await self._call_vllm(competitive_query, temperature=0.3)

        return {
            "semantic_type": "competitive_analysis_result",
            "domain": domain,
            "analysis": analysis,
            "competitor_count": len(competitors)
        }

    async def _analyze_trends(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze technology and market trends"""
        domain = query_csdl.get("domain", "")
        timeframe = query_csdl.get("timeframe", "2-5 years")

        trend_query = {
            "semantic_type": "trend_analysis",
            "task": "trend_identification",
            "domain": domain,
            "timeframe": timeframe,
            "trend_categories": [
                "emerging_technologies",
                "market_shifts",
                "adoption_patterns",
                "regulatory_changes",
                "paradigm_shifts"
            ]
        }

        trends = await self._call_vllm(trend_query, temperature=0.4)

        return {
            "semantic_type": "trend_analysis_result",
            "domain": domain,
            "timeframe": timeframe,
            "trends": trends
        }

    async def _gather_intelligence(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Gather external intelligence"""
        focus = query_csdl.get("focus", "general")

        intelligence_query = {
            "semantic_type": "intelligence_gathering",
            "task": "external_intelligence",
            "focus": focus,
            "intelligence_types": [
                "technological_developments",
                "industry_news",
                "best_practices",
                "case_studies",
                "lessons_learned"
            ]
        }

        intelligence = await self._call_vllm(intelligence_query, temperature=0.3)

        return {
            "semantic_type": "intelligence_result",
            "focus": focus,
            "intelligence": intelligence
        }
