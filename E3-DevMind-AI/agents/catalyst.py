"""
Agent #32: CATALYST (Growth Strategy)

E3 Consortium global expansion and growth acceleration expert.
"""

from agents.base_agent import BaseAgent
from csdl.protocol import CSDLMessage
from typing import Dict, Any, Optional, List
import structlog

logger = structlog.get_logger()


class CatalystAgent(BaseAgent):
    """CATALYST - Growth Strategy Agent"""

    def __init__(self, vllm_client, knowledge_base, config=None):
        super().__init__(
            agent_id="catalyst",
            agent_name="Catalyst",
            vllm_client=vllm_client,
            knowledge_base=knowledge_base,
            config=config
        )
        self.growth_strategies: List[Dict[str, Any]] = []
        self.expansion_plans: Dict[str, Dict[str, Any]] = {}
        self.scaling_roadmaps: List[Dict[str, Any]] = []
        self.partnership_opportunities: List[Dict[str, Any]] = []
        self.growth_metrics: Dict[str, Any] = {
            "historical_growth_rates": [],
            "current_growth_rate": 0.0,
            "growth_targets": {}
        }
        self.market_entry_assessments: Dict[str, Dict[str, Any]] = {}

    def _build_system_context(self) -> Dict[str, Any]:
        return {
            "role": "growth_strategy",
            "agent_id": "catalyst",
            "agent_name": "Catalyst",
            "tier": 7,
            "capabilities": [
                "expansion_strategy",
                "scaling_planning",
                "growth_modeling",
                "market_entry_strategy",
                "partnership_strategy",
                "business_model_innovation",
                "growth_acceleration"
            ],
            "specialization": "strategic_growth"
        }

    async def process_csdl(self, message: CSDLMessage, context: Optional[Dict[str, Any]] = None) -> CSDLMessage:
        """Process growth strategy request"""
        query_type = message.content.get("query_type", "develop_strategy")

        if query_type == "develop_strategy":
            result = await self._develop_growth_strategy(message.content)
        elif query_type == "plan_expansion":
            result = await self._plan_expansion(message.content)
        elif query_type == "design_scaling":
            result = await self._design_scaling_strategy(message.content)
        elif query_type == "assess_market_entry":
            result = await self._assess_market_entry(message.content)
        elif query_type == "identify_partnerships":
            result = await self._identify_partnerships(message.content)
        else:
            result = await self._model_growth(message.content)

        from csdl.protocol import CSDLProtocol
        return CSDLProtocol.create_response(
            content_csdl=result, sender_id=self.agent_id,
            in_response_to=message.message_id, recipient_id=message.sender_id
        )

    async def _develop_growth_strategy(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Develop comprehensive growth strategy"""
        current_state = query_csdl.get("current_state", {})
        growth_objectives = query_csdl.get("growth_objectives", {})
        time_horizon = query_csdl.get("time_horizon", "3-5 years")

        strategy_query = {
            "semantic_type": "growth_strategy_development",
            "task": "comprehensive_growth_strategy",
            "current_state": current_state,
            "growth_objectives": growth_objectives,
            "time_horizon": time_horizon,
            "historical_strategies": self.growth_strategies[-5:],
            "strategic_frameworks": [
                "ansoff_matrix",  # Market penetration, development, product development, diversification
                "bcg_growth_share_matrix",  # Stars, cash cows, question marks, dogs
                "ge_mckinsey_matrix",  # Industry attractiveness vs competitive strength
                "growth_share_analysis",
                "product_lifecycle_strategy"
            ],
            "growth_levers": [
                "market_penetration",
                "market_development",
                "product_development",
                "diversification",
                "acquisitions_and_mergers",
                "strategic_partnerships",
                "geographic_expansion",
                "customer_base_expansion"
            ],
            "strategy_components": [
                "growth_vision",
                "strategic_objectives",
                "growth_initiatives",
                "resource_requirements",
                "timeline_and_milestones",
                "success_metrics",
                "risk_mitigation"
            ],
            "implementation_roadmap": [
                "phase_1_foundation",
                "phase_2_acceleration",
                "phase_3_scale",
                "phase_4_optimization"
            ]
        }

        growth_strategy = await self._call_vllm(strategy_query, temperature=0.4)

        # Record strategy
        strategy_record = {
            "growth_objectives": growth_objectives,
            "strategy": growth_strategy,
            "timestamp": "now",
            "time_horizon": time_horizon
        }
        self.growth_strategies.append(strategy_record)

        return {
            "semantic_type": "growth_strategy_result",
            "growth_strategy": growth_strategy,
            "strategic_priorities": growth_strategy.get("priorities", []),
            "growth_initiatives": growth_strategy.get("initiatives", []),
            "expected_outcomes": growth_strategy.get("expected_outcomes", {}),
            "investment_required": growth_strategy.get("investment_required", "TBD")
        }

    async def _plan_expansion(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Plan geographic or market expansion"""
        expansion_type = query_csdl.get("expansion_type", "geographic")
        target_markets = query_csdl.get("target_markets", [])

        expansion_query = {
            "semantic_type": "expansion_planning",
            "task": "market_expansion_strategy",
            "expansion_type": expansion_type,
            "target_markets": target_markets,
            "existing_expansion_plans": self.expansion_plans,
            "expansion_analysis": [
                "market_attractiveness_assessment",
                "competitive_landscape_analysis",
                "entry_barriers_evaluation",
                "regulatory_requirements",
                "cultural_considerations",
                "operational_requirements"
            ],
            "entry_strategies": [
                "greenfield_investment",
                "acquisition",
                "joint_venture",
                "strategic_alliance",
                "licensing",
                "franchising",
                "exporting"
            ],
            "expansion_planning": [
                "market_entry_sequence",
                "resource_allocation",
                "organizational_structure",
                "go_to_market_strategy",
                "localization_requirements",
                "risk_management"
            ],
            "success_factors": [
                "local_partnerships",
                "talent_acquisition",
                "brand_adaptation",
                "supply_chain_setup",
                "customer_acquisition_strategy"
            ]
        }

        expansion_plan = await self._call_vllm(expansion_query, temperature=0.4)

        # Record expansion plan
        for market in target_markets:
            market_id = market.get("id") or market.get("name")
            if market_id:
                self.expansion_plans[market_id] = {
                    "market": market,
                    "plan": expansion_plan,
                    "status": "planned",
                    "created_at": "now"
                }

        return {
            "semantic_type": "expansion_plan_result",
            "expansion_plan": expansion_plan,
            "target_market_count": len(target_markets),
            "entry_strategy": expansion_plan.get("recommended_entry_strategy", "TBD"),
            "timeline": expansion_plan.get("timeline", {}),
            "investment_required": expansion_plan.get("investment_required", "TBD")
        }

    async def _design_scaling_strategy(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Design comprehensive scaling strategy"""
        current_scale = query_csdl.get("current_scale", {})
        target_scale = query_csdl.get("target_scale", {})
        scaling_dimensions = query_csdl.get("dimensions", [
            "operations", "technology", "team", "revenue", "customers"
        ])

        scaling_query = {
            "semantic_type": "scaling_strategy",
            "task": "comprehensive_scaling_plan",
            "current_scale": current_scale,
            "target_scale": target_scale,
            "scaling_dimensions": scaling_dimensions,
            "historical_roadmaps": self.scaling_roadmaps[-3:],
            "scaling_challenges": [
                "operational_scalability",
                "technical_scalability",
                "organizational_scalability",
                "financial_scalability",
                "market_scalability"
            ],
            "scaling_strategies": {
                "operations": [
                    "process_automation",
                    "operational_efficiency",
                    "quality_at_scale",
                    "supply_chain_optimization"
                ],
                "technology": [
                    "infrastructure_scaling",
                    "architecture_modernization",
                    "performance_optimization",
                    "security_at_scale"
                ],
                "team": [
                    "talent_acquisition",
                    "organizational_design",
                    "leadership_development",
                    "culture_preservation"
                ],
                "revenue": [
                    "revenue_stream_diversification",
                    "pricing_optimization",
                    "sales_force_expansion",
                    "customer_success_scaling"
                ],
                "customers": [
                    "customer_acquisition_scaling",
                    "customer_retention_programs",
                    "support_infrastructure",
                    "community_building"
                ]
            },
            "scaling_principles": [
                "maintain_quality",
                "preserve_culture",
                "ensure_sustainability",
                "manage_complexity",
                "build_for_future_scale"
            ]
        }

        scaling_strategy = await self._call_vllm(scaling_query, temperature=0.4)

        # Record scaling roadmap
        roadmap_record = {
            "current_scale": current_scale,
            "target_scale": target_scale,
            "strategy": scaling_strategy,
            "timestamp": "now"
        }
        self.scaling_roadmaps.append(roadmap_record)

        return {
            "semantic_type": "scaling_strategy_result",
            "scaling_strategy": scaling_strategy,
            "scaling_phases": scaling_strategy.get("phases", []),
            "critical_milestones": scaling_strategy.get("milestones", []),
            "resource_requirements": scaling_strategy.get("resources", {}),
            "risk_factors": scaling_strategy.get("risks", [])
        }

    async def _assess_market_entry(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Assess market entry opportunities"""
        target_market = query_csdl.get("target_market", {})
        entry_objectives = query_csdl.get("entry_objectives", {})

        market_entry_query = {
            "semantic_type": "market_entry_assessment",
            "task": "comprehensive_market_entry_analysis",
            "target_market": target_market,
            "entry_objectives": entry_objectives,
            "assessment_dimensions": [
                "market_opportunity_assessment",
                "competitive_landscape",
                "regulatory_environment",
                "economic_factors",
                "cultural_factors",
                "infrastructure_readiness"
            ],
            "entry_analysis": [
                "market_size_and_growth",
                "customer_needs_and_preferences",
                "competitive_intensity",
                "entry_barriers",
                "success_factors",
                "risk_assessment"
            ],
            "entry_mode_evaluation": [
                "wholly_owned_subsidiary",
                "joint_venture",
                "strategic_alliance",
                "licensing_agreement",
                "franchising",
                "exporting"
            ],
            "entry_strategy": [
                "positioning_strategy",
                "go_to_market_approach",
                "pricing_strategy",
                "distribution_strategy",
                "marketing_strategy",
                "partnership_strategy"
            ],
            "implementation_plan": [
                "entry_timeline",
                "resource_requirements",
                "key_milestones",
                "success_metrics",
                "contingency_plans"
            ]
        }

        market_entry_assessment = await self._call_vllm(market_entry_query, temperature=0.3)

        # Record assessment
        market_id = target_market.get("id") or target_market.get("name")
        if market_id:
            self.market_entry_assessments[market_id] = {
                "market": target_market,
                "assessment": market_entry_assessment,
                "assessed_at": "now"
            }

        return {
            "semantic_type": "market_entry_result",
            "assessment": market_entry_assessment,
            "entry_recommendation": market_entry_assessment.get("recommendation", "TBD"),
            "attractiveness_score": market_entry_assessment.get("attractiveness_score", 0.0),
            "feasibility_score": market_entry_assessment.get("feasibility_score", 0.0),
            "recommended_entry_mode": market_entry_assessment.get("entry_mode", "TBD")
        }

    async def _identify_partnerships(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Identify strategic partnership opportunities"""
        partnership_objectives = query_csdl.get("objectives", [])
        partnership_types = query_csdl.get("types", [
            "technology", "distribution", "market_access", "co_development"
        ])

        partnership_query = {
            "semantic_type": "partnership_identification",
            "task": "strategic_partnership_discovery",
            "partnership_objectives": partnership_objectives,
            "partnership_types": partnership_types,
            "identification_criteria": [
                "strategic_alignment",
                "complementary_capabilities",
                "market_access",
                "technology_synergies",
                "resource_sharing_potential",
                "risk_mitigation"
            ],
            "partnership_models": [
                "joint_venture",
                "strategic_alliance",
                "co_marketing_agreement",
                "technology_partnership",
                "distribution_partnership",
                "reseller_agreement",
                "system_integration_partnership"
            ],
            "partnership_evaluation": [
                "value_creation_potential",
                "implementation_complexity",
                "cultural_fit",
                "financial_implications",
                "risk_assessment",
                "exit_strategy"
            ],
            "partnership_structure": [
                "governance_model",
                "revenue_sharing",
                "ip_ownership",
                "decision_rights",
                "performance_metrics"
            ]
        }

        partnerships = await self._call_vllm(partnership_query, temperature=0.4)

        # Add to partnership opportunities
        for partnership in partnerships.get("partnerships", []):
            partnership["identified_at"] = "now"
            partnership["status"] = "identified"
            self.partnership_opportunities.append(partnership)

        # Keep only top 50 opportunities
        if len(self.partnership_opportunities) > 50:
            sorted_partnerships = sorted(
                self.partnership_opportunities,
                key=lambda x: x.get("score", 0),
                reverse=True
            )
            self.partnership_opportunities = sorted_partnerships[:50]

        return {
            "semantic_type": "partnership_result",
            "partnerships": partnerships,
            "opportunity_count": len(partnerships.get("partnerships", [])),
            "high_priority_count": partnerships.get("high_priority_count", 0),
            "recommended_partnerships": partnerships.get("top_recommendations", [])
        }

    async def _model_growth(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Model and forecast growth scenarios"""
        current_metrics = query_csdl.get("current_metrics", {})
        growth_drivers = query_csdl.get("growth_drivers", [])
        scenario_parameters = query_csdl.get("scenario_parameters", {})

        growth_modeling_query = {
            "semantic_type": "growth_modeling",
            "task": "growth_scenario_analysis",
            "current_metrics": current_metrics,
            "growth_drivers": growth_drivers,
            "scenario_parameters": scenario_parameters,
            "historical_metrics": self.growth_metrics,
            "modeling_approaches": [
                "baseline_scenario",
                "conservative_scenario",
                "aggressive_scenario",
                "monte_carlo_simulation",
                "sensitivity_analysis"
            ],
            "growth_drivers_analysis": [
                "customer_acquisition_rate",
                "customer_retention_rate",
                "average_revenue_per_user",
                "market_share_growth",
                "product_adoption_rate",
                "pricing_optimization",
                "operational_efficiency"
            ],
            "modeling_outputs": [
                "revenue_projections",
                "user_growth_projections",
                "market_share_projections",
                "profitability_projections",
                "cash_flow_projections"
            ],
            "scenario_analysis": [
                "best_case_scenario",
                "expected_case_scenario",
                "worst_case_scenario",
                "break_even_analysis",
                "sensitivity_to_assumptions"
            ]
        }

        growth_model = await self._call_vllm(growth_modeling_query, temperature=0.3)

        # Update growth metrics
        projected_growth = growth_model.get("expected_growth_rate", 0.0)
        self.growth_metrics["historical_growth_rates"].append(projected_growth)
        self.growth_metrics["current_growth_rate"] = projected_growth

        return {
            "semantic_type": "growth_model_result",
            "growth_model": growth_model,
            "scenarios": growth_model.get("scenarios", {}),
            "expected_growth_rate": projected_growth,
            "key_assumptions": growth_model.get("assumptions", []),
            "risk_factors": growth_model.get("risk_factors", []),
            "recommendations": growth_model.get("recommendations", [])
        }
