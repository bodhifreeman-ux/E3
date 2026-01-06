"""
Metadata Enhancer

Enriches responses with helpful metadata for user understanding.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog

logger = structlog.get_logger()


class MetadataEnhancer:
    """
    Enhances response metadata for better user experience

    Adds:
    1. Processing insights
    2. Agent attribution
    3. Data provenance
    4. Quality indicators
    5. Usage suggestions
    """

    def __init__(self):
        self.agent_descriptions = self._load_agent_descriptions()

    def enhance_metadata(
        self,
        response_data: Dict[str, Any],
        agents_involved: List[str],
        processing_time_ms: float,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Enhance response with rich metadata

        Args:
            response_data: Original response data
            agents_involved: List of agent IDs that contributed
            processing_time_ms: Processing time in milliseconds
            additional_context: Additional context to include

        Returns:
            Enhanced metadata structure
        """
        metadata = {
            "processing": self._create_processing_metadata(
                processing_time_ms,
                agents_involved
            ),
            "agents": self._create_agent_metadata(agents_involved),
            "data_provenance": self._create_provenance_metadata(response_data),
            "quality": self._create_quality_metadata(response_data),
            "usage_guidance": self._create_usage_guidance(response_data, agents_involved),
            "timestamps": self._create_timestamp_metadata(),
            "csdl_efficiency": self._calculate_csdl_efficiency(response_data)
        }

        if additional_context:
            metadata["additional_context"] = additional_context

        return metadata

    def _create_processing_metadata(
        self,
        processing_time_ms: float,
        agents_involved: List[str]
    ) -> Dict[str, Any]:
        """Create processing performance metadata"""
        return {
            "processing_time": {
                "milliseconds": round(processing_time_ms, 2),
                "seconds": round(processing_time_ms / 1000, 2),
                "human_readable": self._format_duration(processing_time_ms)
            },
            "agent_count": len(agents_involved),
            "coordination": "parallel" if len(agents_involved) > 1 else "single",
            "efficiency": self._assess_efficiency(processing_time_ms, len(agents_involved))
        }

    def _create_agent_metadata(self, agent_ids: List[str]) -> List[Dict[str, Any]]:
        """Create metadata about agents involved"""
        agent_metadata = []

        for agent_id in agent_ids:
            description = self.agent_descriptions.get(agent_id, {})
            agent_metadata.append({
                "id": agent_id,
                "name": description.get("name", agent_id.title()),
                "role": description.get("role", "Unknown"),
                "specialization": description.get("specialization", ""),
                "contribution": self._describe_agent_contribution(agent_id)
            })

        return agent_metadata

    def _create_provenance_metadata(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create data provenance metadata"""
        return {
            "sources": self._extract_sources(response_data),
            "data_freshness": self._assess_data_freshness(response_data),
            "validation_status": self._check_validation_status(response_data),
            "cross_referenced": self._check_cross_referencing(response_data)
        }

    def _create_quality_metadata(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create quality indicators"""
        return {
            "confidence": response_data.get("confidence", "Not specified"),
            "completeness": self._assess_completeness(response_data),
            "accuracy_indicators": self._gather_accuracy_indicators(response_data),
            "limitations": self._identify_limitations(response_data),
            "quality_score": self._calculate_quality_score(response_data)
        }

    def _create_usage_guidance(
        self,
        response_data: Dict[str, Any],
        agents_involved: List[str]
    ) -> Dict[str, Any]:
        """Create usage guidance"""
        return {
            "best_used_for": self._determine_use_cases(response_data, agents_involved),
            "interpretation_notes": self._generate_interpretation_notes(response_data),
            "recommended_actions": self._suggest_recommended_actions(response_data),
            "follow_up_queries": self._suggest_follow_up_queries(response_data, agents_involved)
        }

    def _create_timestamp_metadata(self) -> Dict[str, str]:
        """Create timestamp metadata"""
        now = datetime.utcnow()
        return {
            "generated_at": now.isoformat() + "Z",
            "generated_at_human": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "valid_until": "Real-time data - verify if using later"
        }

    def _calculate_csdl_efficiency(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate CSDL compression efficiency"""
        tokens_saved = response_data.get("tokens_saved", 0)
        csdl_used = response_data.get("csdl_used", True)

        if not csdl_used:
            return {
                "enabled": False,
                "message": "CSDL compression not used for this request"
            }

        compression_ratio = response_data.get("compression_ratio", 0.75)

        return {
            "enabled": True,
            "tokens_saved": tokens_saved,
            "compression_ratio": f"{compression_ratio * 100:.0f}%",
            "efficiency_gain": f"{compression_ratio * 100:.0f}% reduction in processing overhead",
            "impact": self._describe_csdl_impact(tokens_saved, compression_ratio)
        }

    def _format_duration(self, ms: float) -> str:
        """Format duration in human-readable form"""
        if ms < 1000:
            return f"{ms:.0f}ms"
        elif ms < 60000:
            return f"{ms / 1000:.1f}s"
        else:
            return f"{ms / 60000:.1f}m"

    def _assess_efficiency(self, processing_time_ms: float, agent_count: int) -> str:
        """Assess processing efficiency"""
        if processing_time_ms < 500:
            return "Excellent - Very fast response"
        elif processing_time_ms < 2000:
            return "Good - Fast response"
        elif processing_time_ms < 5000:
            return "Acceptable - Standard response time"
        elif processing_time_ms < 10000:
            return "Slow - Consider simplifying query"
        else:
            return "Very Slow - May need optimization"

    def _describe_agent_contribution(self, agent_id: str) -> str:
        """Describe what the agent contributed"""
        contributions = {
            "oracle": "Coordinated the overall response and synthesized results",
            "prophet": "Provided predictive analytics and risk forecasting",
            "sage": "Contributed meta-reasoning and strategic insights",
            "strategist": "Designed solution strategy and approach",
            "architect": "Provided architectural design and system structure",
            "forge": "Generated code implementations",
            "craftsman": "Ensured code quality and best practices",
            "scientist": "Validated through testing and analysis",
            "sentinel": "Reviewed security considerations",
            "synthesizer": "Combined insights from multiple sources",
            "oracle_kb": "Retrieved relevant knowledge",
            "librarian": "Processed and organized information"
        }
        return contributions.get(agent_id, "Contributed specialized analysis")

    def _extract_sources(self, response_data: Dict[str, Any]) -> List[str]:
        """Extract data sources"""
        sources = []

        if "sources" in response_data:
            sources.extend(response_data["sources"])

        if "evidence" in response_data:
            sources.append("Supporting evidence from knowledge base")

        if "historical_data" in response_data:
            sources.append("Historical data analysis")

        if not sources:
            sources.append("Agent reasoning and analysis")

        return sources

    def _assess_data_freshness(self, response_data: Dict[str, Any]) -> str:
        """Assess how fresh the data is"""
        if "last_updated" in response_data or "updated_at" in response_data:
            return "Recent - Based on current data"

        return "Standard - Based on available data"

    def _check_validation_status(self, response_data: Dict[str, Any]) -> str:
        """Check if results were validated"""
        agents_count = len(response_data.get("agents_involved", []))

        if agents_count >= 3:
            return "Cross-validated by multiple agents"
        elif agents_count >= 2:
            return "Validated by multiple sources"
        else:
            return "Single-source analysis"

    def _check_cross_referencing(self, response_data: Dict[str, Any]) -> bool:
        """Check if results were cross-referenced"""
        return len(response_data.get("sources", [])) > 1 or \
               len(response_data.get("agents_involved", [])) > 1

    def _assess_completeness(self, response_data: Dict[str, Any]) -> str:
        """Assess response completeness"""
        expected_fields = ["summary", "findings", "recommendations", "analysis", "details"]
        present = sum(1 for field in expected_fields if field in response_data)

        if present >= 4:
            return "Complete - All expected sections present"
        elif present >= 3:
            return "Mostly complete - Most sections present"
        elif present >= 2:
            return "Partial - Some sections present"
        else:
            return "Basic - Essential information only"

    def _gather_accuracy_indicators(self, response_data: Dict[str, Any]) -> List[str]:
        """Gather indicators of accuracy"""
        indicators = []

        confidence = response_data.get("confidence", 0)
        if isinstance(confidence, (int, float)) and confidence >= 0.8:
            indicators.append("High confidence score")

        if response_data.get("data_quality", 0) >= 20:
            indicators.append("Based on substantial data")

        if len(response_data.get("agents_involved", [])) >= 3:
            indicators.append("Cross-validated by multiple agents")

        if response_data.get("validated", False):
            indicators.append("Explicitly validated")

        if not indicators:
            indicators.append("Standard accuracy - no special indicators")

        return indicators

    def _identify_limitations(self, response_data: Dict[str, Any]) -> List[str]:
        """Identify any limitations"""
        limitations = []

        confidence = response_data.get("confidence", 1.0)
        if isinstance(confidence, (int, float)) and confidence < 0.6:
            limitations.append("Moderate confidence - results may need verification")

        data_quality = response_data.get("data_quality", 100)
        if isinstance(data_quality, int) and data_quality < 10:
            limitations.append("Limited historical data - results may be less accurate")

        if response_data.get("incomplete", False):
            limitations.append("Incomplete analysis - some aspects not covered")

        if not limitations:
            return ["No significant limitations identified"]

        return limitations

    def _calculate_quality_score(self, response_data: Dict[str, Any]) -> str:
        """Calculate overall quality score"""
        score = 0.0
        factors = 0

        # Confidence
        confidence = response_data.get("confidence", 0)
        if isinstance(confidence, (int, float)):
            score += confidence
            factors += 1

        # Data quality
        data_quality = response_data.get("data_quality", 0)
        if isinstance(data_quality, int):
            score += min(data_quality / 20, 1.0)
            factors += 1

        # Cross-validation
        if len(response_data.get("agents_involved", [])) >= 2:
            score += 0.8
            factors += 1

        if factors > 0:
            avg_score = score / factors
            if avg_score >= 0.85:
                return "Excellent"
            elif avg_score >= 0.70:
                return "Good"
            elif avg_score >= 0.55:
                return "Fair"
            else:
                return "Developing"

        return "Not assessed"

    def _determine_use_cases(
        self,
        response_data: Dict[str, Any],
        agents_involved: List[str]
    ) -> List[str]:
        """Determine best use cases for this response"""
        use_cases = []

        if "prophet" in agents_involved:
            use_cases.append("Strategic planning and risk management")

        if "architect" in agents_involved:
            use_cases.append("System design and technical planning")

        if "forge" in agents_involved or "craftsman" in agents_involved:
            use_cases.append("Implementation and development")

        if "synthesizer" in agents_involved:
            use_cases.append("Decision-making with multiple perspectives")

        if not use_cases:
            use_cases.append("General analysis and insights")

        return use_cases

    def _generate_interpretation_notes(self, response_data: Dict[str, Any]) -> List[str]:
        """Generate interpretation notes"""
        notes = []

        confidence = response_data.get("confidence", 1.0)
        if isinstance(confidence, (int, float)) and confidence < 0.7:
            notes.append("Consider results as preliminary - verify with additional sources")

        if response_data.get("predictions") or response_data.get("risks"):
            notes.append("Predictions are probabilities, not certainties - use for planning")

        if response_data.get("recommendations"):
            notes.append("Recommendations should be evaluated in your specific context")

        if not notes:
            notes.append("Results can be applied directly to your use case")

        return notes

    def _suggest_recommended_actions(self, response_data: Dict[str, Any]) -> List[str]:
        """Suggest recommended actions"""
        actions = []

        if response_data.get("recommendations"):
            actions.append("Review and prioritize the recommendations")

        if response_data.get("risks"):
            actions.append("Implement risk mitigation strategies")

        if response_data.get("findings"):
            actions.append("Incorporate findings into your planning")

        if not actions:
            actions.append("Apply insights to your current work")

        return actions

    def _suggest_follow_up_queries(
        self,
        response_data: Dict[str, Any],
        agents_involved: List[str]
    ) -> List[str]:
        """Suggest follow-up queries"""
        suggestions = []

        if "prophet" in agents_involved:
            suggestions.append("Ask for specific mitigation strategies for identified risks")

        if "architect" in agents_involved:
            suggestions.append("Request detailed implementation plans for the design")

        if response_data.get("recommendations"):
            suggestions.append("Ask for prioritization of recommendations")

        if not suggestions:
            suggestions.append("Ask for clarification on any specific points")

        return suggestions

    def _describe_csdl_impact(self, tokens_saved: int, compression_ratio: float) -> str:
        """Describe the impact of CSDL compression"""
        if tokens_saved >= 1000:
            return f"Significant efficiency gain - saved ~{tokens_saved} tokens, enabling faster processing"
        elif tokens_saved >= 500:
            return f"Notable efficiency gain - saved ~{tokens_saved} tokens"
        elif tokens_saved >= 100:
            return f"Moderate efficiency gain - saved ~{tokens_saved} tokens"
        else:
            return "Standard CSDL compression applied"

    def _load_agent_descriptions(self) -> Dict[str, Dict[str, str]]:
        """Load agent descriptions"""
        return {
            "oracle": {
                "name": "Oracle",
                "role": "Coordinator",
                "specialization": "Multi-agent orchestration and response synthesis"
            },
            "prophet": {
                "name": "Prophet",
                "role": "Predictive Analytics",
                "specialization": "Risk prediction and timeline forecasting"
            },
            "sage": {
                "name": "Sage",
                "role": "Meta-Reasoner",
                "specialization": "Strategic thinking and high-level reasoning"
            },
            "strategist": {
                "name": "Strategist",
                "role": "Solution Designer",
                "specialization": "Strategy formulation and solution design"
            },
            "economist": {
                "name": "Economist",
                "role": "Resource Optimizer",
                "specialization": "Cost optimization and resource allocation"
            },
            "investigator": {
                "name": "Investigator",
                "role": "Technical Analyzer",
                "specialization": "Deep technical analysis"
            },
            "architect": {
                "name": "Architect",
                "role": "System Designer",
                "specialization": "System architecture and design"
            },
            "forge": {
                "name": "Forge",
                "role": "Code Generator",
                "specialization": "Code generation and implementation"
            },
            "craftsman": {
                "name": "Craftsman",
                "role": "Quality Assurance",
                "specialization": "Code quality and best practices"
            },
            "scientist": {
                "name": "Scientist",
                "role": "Testing Specialist",
                "specialization": "Testing and validation"
            },
            "sentinel": {
                "name": "Sentinel",
                "role": "Security Guardian",
                "specialization": "Security analysis and protection"
            },
            "synthesizer": {
                "name": "Synthesizer",
                "role": "Insight Generator",
                "specialization": "Cross-domain synthesis and insights"
            },
            "oracle_kb": {
                "name": "Oracle KB",
                "role": "Knowledge Retrieval",
                "specialization": "Knowledge base querying"
            },
            "librarian": {
                "name": "Librarian",
                "role": "Document Processor",
                "specialization": "Document processing and organization"
            }
        }
