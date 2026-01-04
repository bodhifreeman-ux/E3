"""
Agent #31: NAVIGATOR (Market Intelligence)

Comprehensive market analysis and competitive intelligence for E3 Consortium.
"""

from agents.base_agent import BaseAgent
from csdl.protocol import CSDLMessage
from typing import Dict, Any, Optional, List
import structlog

logger = structlog.get_logger()


class NavigatorAgent(BaseAgent):
    """NAVIGATOR - Market Intelligence Agent"""

    def __init__(self, vllm_client, knowledge_base, config=None):
        super().__init__(
            agent_id="navigator",
            agent_name="Navigator",
            vllm_client=vllm_client,
            knowledge_base=knowledge_base,
            config=config
        )
        self.market_snapshots: List[Dict[str, Any]] = []
        self.competitor_profiles: Dict[str, Dict[str, Any]] = {}
        self.market_trends: Dict[str, List[Dict[str, Any]]] = {}
        self.opportunity_pipeline: List[Dict[str, Any]] = []
        self.threat_registry: List[Dict[str, Any]] = []
        self.market_intelligence_cache: Dict[str, Any] = {}

    def _build_system_context(self) -> Dict[str, Any]:
        return {
            "role": "market_intelligence",
            "agent_id": "navigator",
            "agent_name": "Navigator",
            "tier": 7,
            "capabilities": [
                "market_trend_analysis",
                "competitive_intelligence",
                "opportunity_identification",
                "threat_assessment",
                "market_segmentation",
                "positioning_analysis",
                "customer_insight_generation"
            ],
            "specialization": "market_analytics"
        }

    async def process_csdl(self, message: CSDLMessage, context: Optional[Dict[str, Any]] = None) -> CSDLMessage:
        """Process market intelligence request"""
        query_type = message.content.get("query_type", "analyze_market")

        if query_type == "analyze_market":
            result = await self._analyze_market(message.content)
        elif query_type == "monitor_competitors":
            result = await self._monitor_competitors(message.content)
        elif query_type == "identify_opportunities":
            result = await self._identify_opportunities(message.content)
        elif query_type == "assess_threats":
            result = await self._assess_threats(message.content)
        elif query_type == "segment_market":
            result = await self._segment_market(message.content)
        else:
            result = await self._analyze_positioning(message.content)

        from csdl.protocol import CSDLProtocol
        return CSDLProtocol.create_response(
            content_csdl=result, sender_id=self.agent_id,
            in_response_to=message.message_id, recipient_id=message.sender_id
        )

    async def _analyze_market(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive market analysis"""
        market_segment = query_csdl.get("market_segment", "global")
        analysis_depth = query_csdl.get("depth", "comprehensive")
        time_horizon = query_csdl.get("time_horizon", "1-3 years")

        market_analysis_query = {
            "semantic_type": "market_analysis",
            "task": "comprehensive_market_assessment",
            "market_segment": market_segment,
            "analysis_depth": analysis_depth,
            "time_horizon": time_horizon,
            "historical_data": self.market_snapshots[-10:],
            "analysis_dimensions": [
                "market_size_and_growth",
                "market_dynamics",
                "customer_segments",
                "buying_behavior",
                "price_sensitivity",
                "distribution_channels",
                "regulatory_environment",
                "technology_adoption"
            ],
            "analytical_frameworks": [
                "porter_five_forces",  # Competition, suppliers, buyers, substitutes, entry barriers
                "pestel_analysis",  # Political, Economic, Social, Tech, Environmental, Legal
                "market_maturity_assessment",
                "value_chain_analysis",
                "ecosystem_mapping"
            ],
            "intelligence_sources": [
                "market_research_reports",
                "industry_publications",
                "financial_data",
                "customer_feedback",
                "social_listening"
            ]
        }

        market_analysis = await self._call_vllm(market_analysis_query, temperature=0.3)

        # Record market snapshot
        snapshot = {
            "market_segment": market_segment,
            "analysis": market_analysis,
            "timestamp": "now",
            "time_horizon": time_horizon
        }
        self.market_snapshots.append(snapshot)

        # Keep only last 50 snapshots
        if len(self.market_snapshots) > 50:
            self.market_snapshots = self.market_snapshots[-50:]

        return {
            "semantic_type": "market_analysis_result",
            "market_segment": market_segment,
            "analysis": market_analysis,
            "market_size": market_analysis.get("market_size", {}),
            "growth_rate": market_analysis.get("growth_rate", "N/A"),
            "key_trends": market_analysis.get("key_trends", []),
            "opportunities": market_analysis.get("opportunities", []),
            "risks": market_analysis.get("risks", [])
        }

    async def _monitor_competitors(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor and analyze competitors"""
        competitors = query_csdl.get("competitors", [])
        monitoring_focus = query_csdl.get("focus", "comprehensive")

        competitor_query = {
            "semantic_type": "competitive_intelligence",
            "task": "competitor_monitoring",
            "competitors": competitors,
            "monitoring_focus": monitoring_focus,
            "historical_profiles": self.competitor_profiles,
            "intelligence_areas": [
                "product_portfolio",
                "technology_stack",
                "pricing_strategy",
                "go_to_market_strategy",
                "customer_base",
                "financial_performance",
                "strategic_moves",
                "partnerships_and_alliances"
            ],
            "competitive_analysis": [
                "strengths_weaknesses",
                "market_positioning",
                "differentiation_strategy",
                "innovation_capacity",
                "resource_capabilities",
                "strategic_intent"
            ],
            "comparison_framework": [
                "feature_comparison",
                "performance_benchmarking",
                "price_comparison",
                "market_share_analysis",
                "brand_perception"
            ]
        }

        competitor_intelligence = await self._call_vllm(competitor_query, temperature=0.3)

        # Update competitor profiles
        for competitor in competitors:
            competitor_id = competitor.get("id") or competitor.get("name")
            if competitor_id:
                self.competitor_profiles[competitor_id] = {
                    "competitor": competitor,
                    "intelligence": competitor_intelligence,
                    "last_updated": "now"
                }

        return {
            "semantic_type": "competitor_intelligence_result",
            "competitor_intelligence": competitor_intelligence,
            "competitor_count": len(competitors),
            "competitive_advantages": competitor_intelligence.get("our_advantages", []),
            "competitive_gaps": competitor_intelligence.get("our_gaps", []),
            "strategic_recommendations": competitor_intelligence.get("recommendations", [])
        }

    async def _identify_opportunities(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Identify market opportunities"""
        market_context = query_csdl.get("market_context", {})
        opportunity_types = query_csdl.get("opportunity_types", [
            "market", "product", "technology", "partnership", "geographic"
        ])

        opportunity_query = {
            "semantic_type": "opportunity_identification",
            "task": "opportunity_discovery",
            "market_context": market_context,
            "opportunity_types": opportunity_types,
            "market_intelligence": {
                "market_snapshots": self.market_snapshots[-5:],
                "competitor_profiles": self.competitor_profiles,
                "market_trends": self.market_trends
            },
            "identification_methods": [
                "gap_analysis",
                "unmet_needs_identification",
                "emerging_trend_analysis",
                "whitespace_mapping",
                "customer_pain_point_analysis"
            ],
            "opportunity_assessment": [
                "market_potential",
                "competitive_intensity",
                "entry_barriers",
                "resource_requirements",
                "strategic_fit",
                "risk_level",
                "time_to_market"
            ],
            "prioritization_criteria": [
                "attractiveness",
                "feasibility",
                "strategic_importance",
                "urgency"
            ]
        }

        opportunities = await self._call_vllm(opportunities_query=opportunity_query, temperature=0.4)

        # Add to opportunity pipeline
        for opp in opportunities.get("opportunities", []):
            opp["identified_at"] = "now"
            self.opportunity_pipeline.append(opp)

        # Keep only top 100 opportunities
        if len(self.opportunity_pipeline) > 100:
            # Sort by score and keep top 100
            sorted_opps = sorted(
                self.opportunity_pipeline,
                key=lambda x: x.get("score", 0),
                reverse=True
            )
            self.opportunity_pipeline = sorted_opps[:100]

        return {
            "semantic_type": "opportunity_result",
            "opportunities": opportunities,
            "opportunity_count": len(opportunities.get("opportunities", [])),
            "high_priority_count": opportunities.get("high_priority_count", 0),
            "total_pipeline_size": len(self.opportunity_pipeline)
        }

    async def _assess_threats(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Assess market threats and risks"""
        assessment_scope = query_csdl.get("scope", "comprehensive")

        threat_query = {
            "semantic_type": "threat_assessment",
            "task": "threat_identification_and_analysis",
            "assessment_scope": assessment_scope,
            "market_context": {
                "market_snapshots": self.market_snapshots[-5:],
                "competitor_profiles": self.competitor_profiles,
                "historical_threats": self.threat_registry[-20:]
            },
            "threat_categories": [
                "competitive_threats",
                "market_disruption",
                "technology_obsolescence",
                "regulatory_changes",
                "economic_shifts",
                "customer_behavior_changes",
                "supply_chain_vulnerabilities",
                "cybersecurity_risks"
            ],
            "threat_analysis": [
                "threat_probability",
                "potential_impact",
                "velocity_of_threat",
                "early_warning_indicators",
                "mitigation_strategies",
                "contingency_plans"
            ],
            "risk_scoring": [
                "severity_assessment",
                "likelihood_assessment",
                "risk_score_calculation",
                "risk_prioritization"
            ]
        }

        threat_assessment = await self._call_vllm(threat_query, temperature=0.3)

        # Update threat registry
        for threat in threat_assessment.get("threats", []):
            threat["assessed_at"] = "now"
            self.threat_registry.append(threat)

        # Keep only last 50 threats
        if len(self.threat_registry) > 50:
            self.threat_registry = self.threat_registry[-50:]

        return {
            "semantic_type": "threat_assessment_result",
            "threat_assessment": threat_assessment,
            "threat_count": len(threat_assessment.get("threats", [])),
            "critical_threats": threat_assessment.get("critical_count", 0),
            "mitigation_recommendations": threat_assessment.get("mitigations", [])
        }

    async def _segment_market(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Segment market for targeted strategies"""
        market = query_csdl.get("market", {})
        segmentation_approach = query_csdl.get("approach", "multi_dimensional")

        segmentation_query = {
            "semantic_type": "market_segmentation",
            "task": "customer_segmentation_analysis",
            "market": market,
            "segmentation_approach": segmentation_approach,
            "segmentation_variables": {
                "demographic": ["age", "income", "education", "occupation"],
                "geographic": ["region", "country", "urban_rural", "climate"],
                "psychographic": ["lifestyle", "values", "personality", "interests"],
                "behavioral": ["usage_rate", "loyalty", "benefits_sought", "user_status"],
                "firmographic": ["company_size", "industry", "revenue", "growth_stage"]
            },
            "segmentation_methods": [
                "cluster_analysis",
                "decision_tree_segmentation",
                "factor_analysis",
                "latent_class_analysis"
            ],
            "segment_evaluation": [
                "segment_size",
                "segment_growth",
                "segment_profitability",
                "segment_accessibility",
                "segment_differentiation"
            ],
            "targeting_strategy": [
                "segment_attractiveness_scoring",
                "competitive_position_assessment",
                "strategic_fit_evaluation",
                "targeting_recommendations"
            ]
        }

        segmentation = await self._call_vllm(segmentation_query, temperature=0.3)

        return {
            "semantic_type": "segmentation_result",
            "segmentation": segmentation,
            "segment_count": len(segmentation.get("segments", [])),
            "target_segments": segmentation.get("target_segments", []),
            "segment_profiles": segmentation.get("segment_profiles", [])
        }

    async def _analyze_positioning(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market positioning"""
        product_or_brand = query_csdl.get("product_or_brand", {})

        positioning_query = {
            "semantic_type": "positioning_analysis",
            "task": "competitive_positioning_assessment",
            "product_or_brand": product_or_brand,
            "competitive_context": self.competitor_profiles,
            "positioning_dimensions": [
                "price_quality_positioning",
                "feature_benefit_positioning",
                "usage_occasion_positioning",
                "user_positioning",
                "competitive_positioning"
            ],
            "positioning_analysis": [
                "perceptual_mapping",
                "positioning_statement_evaluation",
                "differentiation_analysis",
                "positioning_gaps",
                "positioning_opportunities"
            ],
            "strategic_positioning": [
                "unique_value_proposition",
                "points_of_parity",
                "points_of_difference",
                "brand_essence",
                "positioning_strategy"
            ]
        }

        positioning = await self._call_vllm(positioning_query, temperature=0.3)

        return {
            "semantic_type": "positioning_result",
            "positioning": positioning,
            "current_position": positioning.get("current_position", {}),
            "desired_position": positioning.get("desired_position", {}),
            "positioning_gap": positioning.get("gap_analysis", {}),
            "recommendations": positioning.get("recommendations", [])
        }
