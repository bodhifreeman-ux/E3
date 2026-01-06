"""
Confidence Scorer

Provides consistent confidence scoring across all agent responses.
"""

from typing import Dict, Any, List, Optional
from enum import Enum
import structlog

logger = structlog.get_logger()


class ConfidenceLevel(str, Enum):
    """Confidence level categories"""
    VERY_HIGH = "very_high"  # 90-100%
    HIGH = "high"  # 70-89%
    MEDIUM = "medium"  # 50-69%
    LOW = "low"  # 30-49%
    VERY_LOW = "very_low"  # 0-29%


class ConfidenceFactor:
    """Factors that influence confidence scoring"""
    DATA_QUALITY = "data_quality"
    DATA_QUANTITY = "data_quantity"
    MODEL_CERTAINTY = "model_certainty"
    HISTORICAL_ACCURACY = "historical_accuracy"
    CROSS_VALIDATION = "cross_validation"
    CONSENSUS_LEVEL = "consensus_level"
    RECENCY = "recency"
    COMPLETENESS = "completeness"


class ConfidenceScorer:
    """
    Calculates and explains confidence scores for agent responses

    Provides:
    1. Numerical confidence scores (0-1)
    2. Categorical confidence levels
    3. Detailed explanations of scoring factors
    4. Recommendations for improving confidence
    """

    def __init__(self):
        self.factor_weights = {
            ConfidenceFactor.DATA_QUALITY: 0.25,
            ConfidenceFactor.DATA_QUANTITY: 0.20,
            ConfidenceFactor.MODEL_CERTAINTY: 0.20,
            ConfidenceFactor.HISTORICAL_ACCURACY: 0.15,
            ConfidenceFactor.CROSS_VALIDATION: 0.10,
            ConfidenceFactor.CONSENSUS_LEVEL: 0.05,
            ConfidenceFactor.RECENCY: 0.03,
            ConfidenceFactor.COMPLETENESS: 0.02
        }

    def calculate_confidence(
        self,
        response_data: Dict[str, Any],
        agent_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive confidence score

        Args:
            response_data: Response data from agent
            agent_context: Additional agent context

        Returns:
            Confidence assessment with score, level, and explanation
        """
        # Extract or calculate individual factor scores
        factors = self._assess_all_factors(response_data, agent_context)

        # Calculate weighted overall score
        overall_score = self._calculate_weighted_score(factors)

        # Determine confidence level
        confidence_level = self._determine_confidence_level(overall_score)

        # Generate explanation
        explanation = self._generate_confidence_explanation(factors, overall_score)

        # Generate recommendations for improvement
        recommendations = self._generate_improvement_recommendations(factors)

        return {
            "score": round(overall_score, 3),
            "level": confidence_level.value,
            "level_description": self._get_level_description(confidence_level),
            "percentage": f"{overall_score * 100:.1f}%",
            "factors": factors,
            "explanation": explanation,
            "improvement_recommendations": recommendations,
            "reliability": self._assess_reliability(overall_score, factors)
        }

    def _assess_all_factors(
        self,
        response_data: Dict[str, Any],
        agent_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """Assess all confidence factors"""
        return {
            ConfidenceFactor.DATA_QUALITY: self._assess_data_quality(response_data),
            ConfidenceFactor.DATA_QUANTITY: self._assess_data_quantity(response_data),
            ConfidenceFactor.MODEL_CERTAINTY: self._assess_model_certainty(response_data),
            ConfidenceFactor.HISTORICAL_ACCURACY: self._assess_historical_accuracy(
                response_data,
                agent_context
            ),
            ConfidenceFactor.CROSS_VALIDATION: self._assess_cross_validation(response_data),
            ConfidenceFactor.CONSENSUS_LEVEL: self._assess_consensus_level(response_data),
            ConfidenceFactor.RECENCY: self._assess_recency(response_data),
            ConfidenceFactor.COMPLETENESS: self._assess_completeness(response_data)
        }

    def _assess_data_quality(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess quality of underlying data"""
        # Check for data quality indicators
        quality_indicators = data.get("data_quality", data.get("quality", None))

        if quality_indicators is None:
            # Estimate based on available information
            has_sources = bool(data.get("sources", data.get("evidence", [])))
            has_validation = bool(data.get("validated", data.get("verified", False)))

            if has_sources and has_validation:
                score = 0.8
                status = "good"
            elif has_sources or has_validation:
                score = 0.6
                status = "moderate"
            else:
                score = 0.4
                status = "limited"
        else:
            # Use provided quality indicator
            if isinstance(quality_indicators, (int, float)):
                if quality_indicators >= 20:
                    score = 0.9
                    status = "excellent"
                elif quality_indicators >= 10:
                    score = 0.7
                    status = "good"
                elif quality_indicators >= 5:
                    score = 0.5
                    status = "moderate"
                else:
                    score = 0.3
                    status = "limited"
            else:
                score = 0.5
                status = "unknown"

        return {
            "score": score,
            "status": status,
            "description": f"Data quality is {status}"
        }

    def _assess_data_quantity(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess quantity of data used"""
        # Look for data quantity indicators
        quantity = data.get("data_quantity", data.get("sample_size", data.get("data_points", None)))

        if quantity is None:
            # Estimate from available information
            sources = data.get("sources", [])
            evidence = data.get("evidence", [])

            quantity = len(sources) + len(evidence)

        if isinstance(quantity, (int, float)):
            if quantity >= 100:
                score = 1.0
                status = "extensive"
            elif quantity >= 50:
                score = 0.8
                status = "substantial"
            elif quantity >= 20:
                score = 0.6
                status = "adequate"
            elif quantity >= 10:
                score = 0.4
                status = "limited"
            else:
                score = 0.2
                status = "minimal"
        else:
            score = 0.5
            status = "unknown"

        return {
            "score": score,
            "status": status,
            "description": f"Data quantity is {status}",
            "data_points": quantity if isinstance(quantity, (int, float)) else "unknown"
        }

    def _assess_model_certainty(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess model's certainty in its output"""
        # Check for explicit confidence from model
        model_confidence = data.get("confidence", data.get("certainty", None))

        if model_confidence is not None and isinstance(model_confidence, (int, float)):
            if isinstance(model_confidence, int):
                # Assume 0-100 scale
                score = model_confidence / 100.0
            else:
                # Assume 0-1 scale
                score = float(model_confidence)

            if score >= 0.9:
                status = "very_certain"
            elif score >= 0.7:
                status = "certain"
            elif score >= 0.5:
                status = "moderate"
            elif score >= 0.3:
                status = "uncertain"
            else:
                status = "very_uncertain"
        else:
            # Default moderate certainty if not specified
            score = 0.6
            status = "moderate"

        return {
            "score": score,
            "status": status,
            "description": f"Model certainty is {status}"
        }

    def _assess_historical_accuracy(
        self,
        data: Dict[str, Any],
        agent_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Assess historical accuracy of similar predictions/analyses"""
        if agent_context and "historical_accuracy" in agent_context:
            accuracy = agent_context["historical_accuracy"]
            score = float(accuracy)

            if score >= 0.85:
                status = "excellent"
            elif score >= 0.70:
                status = "good"
            elif score >= 0.55:
                status = "fair"
            else:
                status = "developing"
        else:
            # Default to moderate if no history available
            score = 0.7
            status = "unknown"

        return {
            "score": score,
            "status": status,
            "description": f"Historical accuracy is {status}"
        }

    def _assess_cross_validation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess whether results were cross-validated"""
        # Check for cross-validation indicators
        agents_involved = data.get("agents_involved", data.get("source_count", 1))

        if isinstance(agents_involved, (list, tuple)):
            validation_count = len(agents_involved)
        elif isinstance(agents_involved, int):
            validation_count = agents_involved
        else:
            validation_count = 1

        if validation_count >= 5:
            score = 1.0
            status = "extensive"
        elif validation_count >= 3:
            score = 0.8
            status = "multiple"
        elif validation_count >= 2:
            score = 0.5
            status = "limited"
        else:
            score = 0.2
            status = "none"

        return {
            "score": score,
            "status": status,
            "description": f"Cross-validation is {status}",
            "validators": validation_count
        }

    def _assess_consensus_level(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess consensus among multiple sources"""
        # Check for consensus indicators
        consensus = data.get("consensus", data.get("agreement", None))
        divergences = data.get("divergences", data.get("conflicts", []))

        if consensus is not None:
            # Explicit consensus provided
            if isinstance(consensus, (int, float)):
                score = float(consensus) if consensus <= 1 else consensus / 100.0
            else:
                score = 0.7
        else:
            # Infer from divergences
            if isinstance(divergences, list):
                if len(divergences) == 0:
                    score = 0.9
                    status = "high"
                elif len(divergences) <= 2:
                    score = 0.6
                    status = "moderate"
                else:
                    score = 0.3
                    status = "low"
            else:
                score = 0.7
                status = "assumed"

        if score >= 0.85:
            status = "strong"
        elif score >= 0.65:
            status = "moderate"
        else:
            status = "weak"

        return {
            "score": score,
            "status": status,
            "description": f"Consensus level is {status}"
        }

    def _assess_recency(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess recency of data used"""
        # Check for timestamp indicators
        updated_at = data.get("updated_at", data.get("last_updated", None))

        # Simplified assessment - in production would use actual timestamps
        if updated_at:
            score = 0.8
            status = "recent"
        else:
            score = 0.5
            status = "unknown"

        return {
            "score": score,
            "status": status,
            "description": f"Data recency is {status}"
        }

    def _assess_completeness(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess completeness of response"""
        # Check for expected fields
        expected_fields = ["summary", "findings", "recommendations", "analysis"]
        present_fields = sum(1 for field in expected_fields if field in data)

        if present_fields >= 3:
            score = 0.9
            status = "complete"
        elif present_fields >= 2:
            score = 0.7
            status = "mostly_complete"
        elif present_fields >= 1:
            score = 0.5
            status = "partial"
        else:
            score = 0.3
            status = "minimal"

        return {
            "score": score,
            "status": status,
            "description": f"Response completeness is {status}"
        }

    def _calculate_weighted_score(self, factors: Dict[str, Dict[str, Any]]) -> float:
        """Calculate weighted overall confidence score"""
        total_score = 0.0
        total_weight = 0.0

        for factor_name, factor_data in factors.items():
            weight = self.factor_weights.get(factor_name, 0.0)
            score = factor_data.get("score", 0.5)

            total_score += score * weight
            total_weight += weight

        # Normalize if weights don't sum to 1.0
        if total_weight > 0:
            return total_score / total_weight
        else:
            return 0.5

    def _determine_confidence_level(self, score: float) -> ConfidenceLevel:
        """Determine categorical confidence level"""
        if score >= 0.90:
            return ConfidenceLevel.VERY_HIGH
        elif score >= 0.70:
            return ConfidenceLevel.HIGH
        elif score >= 0.50:
            return ConfidenceLevel.MEDIUM
        elif score >= 0.30:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW

    def _get_level_description(self, level: ConfidenceLevel) -> str:
        """Get description for confidence level"""
        descriptions = {
            ConfidenceLevel.VERY_HIGH: "Highly reliable - Results backed by strong evidence and validation",
            ConfidenceLevel.HIGH: "Reliable - Results supported by good evidence and validation",
            ConfidenceLevel.MEDIUM: "Moderately reliable - Results based on adequate data but could be improved",
            ConfidenceLevel.LOW: "Limited reliability - Results based on limited data, use with caution",
            ConfidenceLevel.VERY_LOW: "Low reliability - Results highly uncertain, seek additional validation"
        }
        return descriptions.get(level, "Unknown reliability")

    def _generate_confidence_explanation(
        self,
        factors: Dict[str, Dict[str, Any]],
        overall_score: float
    ) -> str:
        """Generate human-readable explanation of confidence score"""
        # Identify strongest and weakest factors
        sorted_factors = sorted(
            factors.items(),
            key=lambda x: x[1].get("score", 0),
            reverse=True
        )

        strongest = sorted_factors[0] if sorted_factors else None
        weakest = sorted_factors[-1] if sorted_factors else None

        explanation = f"The confidence score of {overall_score:.1%} is based on multiple factors. "

        if strongest:
            strongest_name = strongest[0].replace("_", " ").title()
            explanation += f"The strongest factor is {strongest_name} ({strongest[1].get('status', 'unknown')}). "

        if weakest and weakest[1].get("score", 1.0) < 0.5:
            weakest_name = weakest[0].replace("_", " ").title()
            explanation += f"The weakest factor is {weakest_name} ({weakest[1].get('status', 'unknown')}), which could be improved. "

        return explanation

    def _generate_improvement_recommendations(
        self,
        factors: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations for improving confidence"""
        recommendations = []

        for factor_name, factor_data in factors.items():
            score = factor_data.get("score", 1.0)

            if score < 0.5:
                factor_readable = factor_name.replace("_", " ").title()

                if factor_name == ConfidenceFactor.DATA_QUALITY:
                    recommendations.append(
                        "Improve data quality by validating sources and ensuring accuracy"
                    )
                elif factor_name == ConfidenceFactor.DATA_QUANTITY:
                    recommendations.append(
                        "Gather more data to increase confidence in results"
                    )
                elif factor_name == ConfidenceFactor.MODEL_CERTAINTY:
                    recommendations.append(
                        "Model uncertainty is high - consider alternative approaches or more context"
                    )
                elif factor_name == ConfidenceFactor.CROSS_VALIDATION:
                    recommendations.append(
                        "Validate results with additional sources or agents"
                    )
                elif factor_name == ConfidenceFactor.HISTORICAL_ACCURACY:
                    recommendations.append(
                        "Build historical accuracy by tracking prediction outcomes over time"
                    )
                else:
                    recommendations.append(
                        f"Improve {factor_readable.lower()} to increase confidence"
                    )

        if not recommendations:
            recommendations.append("Confidence is already high - maintain current data quality standards")

        return recommendations

    def _assess_reliability(
        self,
        overall_score: float,
        factors: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Assess overall reliability of results"""
        # Check for critical factors
        data_quality = factors.get(ConfidenceFactor.DATA_QUALITY, {}).get("score", 0.5)
        model_certainty = factors.get(ConfidenceFactor.MODEL_CERTAINTY, {}).get("score", 0.5)

        # Results are only truly reliable if both quality and certainty are good
        if overall_score >= 0.7 and data_quality >= 0.6 and model_certainty >= 0.6:
            reliability = "high"
            use_guidance = "Results are reliable and can be used with confidence for decision-making."
        elif overall_score >= 0.5 and data_quality >= 0.4:
            reliability = "moderate"
            use_guidance = "Results are reasonably reliable but should be combined with other information."
        else:
            reliability = "limited"
            use_guidance = "Results have limited reliability - use as preliminary insight only and validate independently."

        return {
            "level": reliability,
            "guidance": use_guidance,
            "suitable_for": self._determine_suitable_uses(reliability)
        }

    def _determine_suitable_uses(self, reliability: str) -> List[str]:
        """Determine what the results are suitable for"""
        if reliability == "high":
            return [
                "Strategic decision-making",
                "Production deployment",
                "Critical analysis",
                "Stakeholder reporting"
            ]
        elif reliability == "moderate":
            return [
                "Preliminary analysis",
                "Development decisions",
                "Internal discussions",
                "Planning purposes"
            ]
        else:
            return [
                "Exploratory analysis only",
                "Hypothesis generation",
                "Identifying areas for investigation"
            ]

    def create_confidence_badge(self, confidence_score: float) -> str:
        """Create a visual confidence badge/indicator"""
        level = self._determine_confidence_level(confidence_score)

        badges = {
            ConfidenceLevel.VERY_HIGH: "🟢 Very High Confidence",
            ConfidenceLevel.HIGH: "🟢 High Confidence",
            ConfidenceLevel.MEDIUM: "🟡 Medium Confidence",
            ConfidenceLevel.LOW: "🟠 Low Confidence",
            ConfidenceLevel.VERY_LOW: "🔴 Very Low Confidence"
        }

        return badges.get(level, "⚪ Unknown Confidence")
