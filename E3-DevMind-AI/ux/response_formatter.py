"""
Response Formatter

Ensures all responses are clear, well-structured, and user-friendly.
"""

from typing import Dict, Any, List, Optional
from enum import Enum
import structlog

logger = structlog.get_logger()


class ResponseType(str, Enum):
    """Types of responses that can be formatted"""
    ANALYSIS = "analysis"
    PREDICTION = "prediction"
    DESIGN = "design"
    IMPLEMENTATION = "implementation"
    ERROR = "error"
    RECOMMENDATION = "recommendation"
    QUERY_RESULT = "query_result"
    SYNTHESIS = "synthesis"
    GENERAL = "general"


class ResponseFormatter:
    """
    Formats agent responses for optimal user experience

    Key Principles:
    1. Clarity: Use plain language, avoid jargon unless necessary
    2. Structure: Organize information hierarchically
    3. Scannability: Use headings, bullets, and emphasis
    4. Completeness: Include context, confidence, and next steps
    5. Actionability: Provide clear recommendations
    """

    def __init__(self):
        self.formatters = {
            ResponseType.ANALYSIS: self._format_analysis,
            ResponseType.PREDICTION: self._format_prediction,
            ResponseType.DESIGN: self._format_design,
            ResponseType.IMPLEMENTATION: self._format_implementation,
            ResponseType.ERROR: self._format_error,
            ResponseType.RECOMMENDATION: self._format_recommendation,
            ResponseType.QUERY_RESULT: self._format_query_result,
            ResponseType.SYNTHESIS: self._format_synthesis,
            ResponseType.GENERAL: self._format_general
        }

    def format_response(
        self,
        response_data: Dict[str, Any],
        response_type: ResponseType = ResponseType.GENERAL,
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """
        Format a response for user consumption

        Args:
            response_data: Raw response data from agent
            response_type: Type of response
            include_metadata: Whether to include metadata section

        Returns:
            Formatted response with user-friendly structure
        """
        formatter = self.formatters.get(response_type, self._format_general)

        formatted = formatter(response_data)

        # Add metadata section if requested
        if include_metadata:
            formatted["metadata"] = self._format_metadata(response_data)

        # Add user guidance
        formatted["user_guidance"] = self._generate_user_guidance(
            response_data,
            response_type
        )

        return formatted

    def _format_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format analysis-type responses"""
        return {
            "summary": self._extract_summary(data),
            "key_findings": self._extract_findings(data),
            "detailed_analysis": self._extract_details(data),
            "implications": self._extract_implications(data),
            "recommendations": self._extract_recommendations(data),
            "confidence": self._extract_confidence(data),
            "supporting_evidence": self._extract_evidence(data)
        }

    def _format_prediction(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format prediction-type responses"""
        predictions = data.get("predictions", data.get("risks", []))

        formatted_predictions = []
        for pred in predictions if isinstance(predictions, list) else [predictions]:
            if isinstance(pred, dict):
                formatted_predictions.append({
                    "prediction": pred.get("description", str(pred)),
                    "probability": self._format_probability(pred.get("probability", pred.get("confidence", 0.5))),
                    "timeframe": pred.get("timeframe", pred.get("predicted_date", "Not specified")),
                    "impact": pred.get("impact", "Unknown"),
                    "confidence": self._format_confidence_level(pred.get("confidence", 0.5)),
                    "indicators": pred.get("indicators", pred.get("early_indicators", [])),
                    "mitigation": pred.get("prevention_actions", pred.get("mitigation_suggestions", []))
                })

        return {
            "summary": self._generate_prediction_summary(formatted_predictions),
            "predictions": formatted_predictions,
            "overall_confidence": self._extract_confidence(data),
            "data_quality": self._assess_data_quality(data),
            "recommendations": self._extract_recommendations(data),
            "monitoring_suggestions": self._generate_monitoring_suggestions(formatted_predictions)
        }

    def _format_design(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format design-type responses"""
        return {
            "summary": self._extract_summary(data),
            "design_overview": data.get("architecture_design", data.get("design", {})),
            "components": self._format_components(data.get("components", [])),
            "technical_decisions": self._extract_technical_decisions(data),
            "trade_offs": data.get("trade_offs", []),
            "implementation_guidance": self._generate_implementation_guidance(data),
            "considerations": {
                "scalability": data.get("scalability_strategy", {}),
                "security": data.get("security_considerations", []),
                "performance": data.get("performance_requirements", {})
            }
        }

    def _format_implementation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format implementation-type responses"""
        return {
            "summary": self._extract_summary(data),
            "implementation_steps": self._extract_steps(data),
            "code_snippets": data.get("code", data.get("implementation", {})),
            "dependencies": data.get("dependencies", []),
            "testing_strategy": data.get("testing", {}),
            "deployment_notes": data.get("deployment", {}),
            "quality_checks": self._generate_quality_checks(data)
        }

    def _format_error(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format error responses with helpful guidance"""
        error_type = data.get("error_type", "unknown_error")
        description = data.get("description", "An error occurred")

        return {
            "error_type": self._humanize_error_type(error_type),
            "message": self._make_error_user_friendly(description),
            "what_happened": self._explain_error(data),
            "what_to_do": self._suggest_error_resolution(data),
            "technical_details": data.get("details", {}),
            "need_help": self._generate_help_resources(error_type)
        }

    def _format_recommendation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format recommendation-type responses"""
        recommendations = data.get("recommendations", [])

        formatted_recs = []
        for i, rec in enumerate(recommendations if isinstance(recommendations, list) else [recommendations], 1):
            if isinstance(rec, dict):
                formatted_recs.append({
                    "priority": rec.get("priority", "medium"),
                    "recommendation": rec.get("recommendation", str(rec)),
                    "rationale": rec.get("rationale", ""),
                    "expected_impact": rec.get("impact", ""),
                    "effort_estimate": rec.get("effort", "Not specified"),
                    "implementation_notes": rec.get("notes", "")
                })
            else:
                formatted_recs.append({
                    "priority": "medium",
                    "recommendation": str(rec),
                    "rationale": "",
                    "expected_impact": "",
                    "effort_estimate": "Not specified",
                    "implementation_notes": ""
                })

        return {
            "summary": f"Generated {len(formatted_recs)} recommendations",
            "recommendations": formatted_recs,
            "prioritization_guide": self._generate_prioritization_guide(formatted_recs),
            "quick_wins": self._identify_quick_wins(formatted_recs),
            "next_steps": self._generate_next_steps(formatted_recs)
        }

    def _format_query_result(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format knowledge query results"""
        results = data.get("results", [])

        return {
            "summary": f"Found {len(results)} relevant results",
            "top_results": self._format_search_results(results[:5]),
            "result_count": len(results),
            "relevance_threshold": data.get("min_score", 0.0),
            "search_quality": self._assess_search_quality(data),
            "related_queries": self._generate_related_queries(data)
        }

    def _format_synthesis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format synthesis of multiple agent responses"""
        return {
            "summary": self._extract_summary(data),
            "synthesized_insights": data.get("synthesis", {}),
            "source_count": data.get("source_count", data.get("agents_involved", 0)),
            "consensus_points": self._extract_consensus(data),
            "divergent_views": self._extract_divergences(data),
            "integrated_recommendations": self._extract_recommendations(data),
            "confidence": self._extract_confidence(data)
        }

    def _format_general(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format general responses"""
        return {
            "summary": self._extract_summary(data),
            "main_content": self._extract_main_content(data),
            "additional_details": self._extract_additional_details(data),
            "recommendations": self._extract_recommendations(data)
        }

    # Helper methods for formatting

    def _extract_summary(self, data: Dict[str, Any]) -> str:
        """Extract or generate a summary"""
        if "summary" in data:
            return data["summary"]
        if "description" in data:
            return data["description"]

        # Try to generate a summary from available data
        if "findings" in data:
            findings = data["findings"]
            if isinstance(findings, list) and findings:
                return f"Analysis revealed {len(findings)} key findings."

        return "Response generated successfully."

    def _extract_findings(self, data: Dict[str, Any]) -> List[str]:
        """Extract key findings"""
        findings = data.get("findings", data.get("key_findings", []))
        if not isinstance(findings, list):
            findings = [findings] if findings else []
        return findings

    def _extract_details(self, data: Dict[str, Any]) -> Any:
        """Extract detailed analysis"""
        return data.get("details", data.get("analysis", data.get("data", {})))

    def _extract_implications(self, data: Dict[str, Any]) -> List[str]:
        """Extract implications"""
        return data.get("implications", data.get("impact", []))

    def _extract_recommendations(self, data: Dict[str, Any]) -> List[str]:
        """Extract recommendations"""
        recs = data.get("recommendations", data.get("recommendation", []))
        if not isinstance(recs, list):
            recs = [recs] if recs else []
        return recs

    def _extract_confidence(self, data: Dict[str, Any]) -> str:
        """Extract and format confidence level"""
        confidence = data.get("confidence", 0.5)
        if isinstance(confidence, (int, float)):
            return self._format_confidence_level(confidence)
        return str(confidence)

    def _extract_evidence(self, data: Dict[str, Any]) -> List[str]:
        """Extract supporting evidence"""
        return data.get("evidence", data.get("supporting_data", []))

    def _format_probability(self, probability: float) -> str:
        """Format probability as user-friendly text"""
        if probability >= 0.8:
            return f"Very Likely ({probability:.0%})"
        elif probability >= 0.6:
            return f"Likely ({probability:.0%})"
        elif probability >= 0.4:
            return f"Moderate ({probability:.0%})"
        elif probability >= 0.2:
            return f"Unlikely ({probability:.0%})"
        else:
            return f"Very Unlikely ({probability:.0%})"

    def _format_confidence_level(self, confidence: float) -> str:
        """Format confidence as user-friendly text"""
        if confidence >= 0.9:
            return f"Very High ({confidence:.0%})"
        elif confidence >= 0.7:
            return f"High ({confidence:.0%})"
        elif confidence >= 0.5:
            return f"Medium ({confidence:.0%})"
        elif confidence >= 0.3:
            return f"Low ({confidence:.0%})"
        else:
            return f"Very Low ({confidence:.0%})"

    def _generate_prediction_summary(self, predictions: List[Dict]) -> str:
        """Generate a summary for predictions"""
        if not predictions:
            return "No significant predictions at this time."

        high_impact = sum(1 for p in predictions if p.get("impact", "").lower() in ["high", "critical"])

        if high_impact > 0:
            return f"Identified {len(predictions)} predictions, including {high_impact} high-impact items requiring attention."
        else:
            return f"Identified {len(predictions)} predictions for monitoring."

    def _assess_data_quality(self, data: Dict[str, Any]) -> str:
        """Assess and describe data quality"""
        quality = data.get("data_quality", 0)

        if isinstance(quality, int):
            if quality >= 20:
                return "High - Based on extensive historical data"
            elif quality >= 10:
                return "Medium - Based on moderate historical data"
            else:
                return "Low - Limited historical data available"

        return "Quality assessment not available"

    def _generate_monitoring_suggestions(self, predictions: List[Dict]) -> List[str]:
        """Generate monitoring suggestions"""
        suggestions = ["Review predictions regularly for accuracy"]

        if any(p.get("indicators") for p in predictions):
            suggestions.append("Monitor the listed indicators for early warning signs")

        if any(p.get("mitigation") for p in predictions):
            suggestions.append("Implement suggested mitigation actions proactively")

        return suggestions

    def _format_components(self, components: List) -> List[Dict]:
        """Format component information"""
        formatted = []
        for comp in components:
            if isinstance(comp, dict):
                formatted.append({
                    "name": comp.get("name", "Unnamed component"),
                    "description": comp.get("description", ""),
                    "responsibilities": comp.get("responsibilities", []),
                    "interfaces": comp.get("interfaces", comp.get("interface", {}))
                })
        return formatted

    def _extract_technical_decisions(self, data: Dict[str, Any]) -> List[Dict]:
        """Extract technical decisions"""
        decisions = []

        if "technology_recommendations" in data:
            decisions.append({
                "decision": "Technology Stack",
                "choice": data["technology_recommendations"],
                "rationale": data.get("rationale", "")
            })

        if "deployment_model" in data:
            decisions.append({
                "decision": "Deployment Model",
                "choice": data["deployment_model"],
                "rationale": ""
            })

        return decisions

    def _generate_implementation_guidance(self, data: Dict[str, Any]) -> str:
        """Generate implementation guidance"""
        if "implementation_notes" in data:
            return data["implementation_notes"]
        return "Follow standard implementation practices for this design."

    def _extract_steps(self, data: Dict[str, Any]) -> List[str]:
        """Extract implementation steps"""
        steps = data.get("steps", data.get("implementation_steps", []))
        if not isinstance(steps, list):
            steps = [steps] if steps else []
        return steps

    def _generate_quality_checks(self, data: Dict[str, Any]) -> List[str]:
        """Generate quality check recommendations"""
        checks = [
            "Verify code follows style guidelines",
            "Ensure all tests pass",
            "Review for security vulnerabilities",
            "Check performance against requirements"
        ]

        if data.get("testing"):
            checks.insert(1, "Run comprehensive test suite")

        return checks

    def _humanize_error_type(self, error_type: str) -> str:
        """Make error type human-readable"""
        return error_type.replace("_", " ").title()

    def _make_error_user_friendly(self, description: str) -> str:
        """Make error description user-friendly"""
        # Remove technical jargon if possible
        if "failed" in description.lower():
            return "The operation couldn't be completed. " + description
        return description

    def _explain_error(self, data: Dict[str, Any]) -> str:
        """Explain what caused the error"""
        error_type = data.get("error_type", "")

        explanations = {
            "timeout": "The operation took too long to complete.",
            "not_found": "The requested resource could not be found.",
            "validation": "The input didn't meet the required format or constraints.",
            "permission": "You don't have permission to perform this operation.",
            "processing": "An error occurred while processing your request."
        }

        for key, explanation in explanations.items():
            if key in error_type.lower():
                return explanation

        return "An unexpected error occurred during processing."

    def _suggest_error_resolution(self, data: Dict[str, Any]) -> str:
        """Suggest how to resolve the error"""
        error_type = data.get("error_type", "")

        suggestions = {
            "timeout": "Try breaking your request into smaller parts or try again later.",
            "not_found": "Check that the resource name or ID is correct.",
            "validation": "Review your input and ensure it meets the required format.",
            "permission": "Contact your administrator for access.",
            "processing": "Try your request again. If the problem persists, contact support."
        }

        for key, suggestion in suggestions.items():
            if key in error_type.lower():
                return suggestion

        return "Try your request again. If the problem persists, contact support with the error details."

    def _generate_help_resources(self, error_type: str) -> Dict[str, str]:
        """Generate help resources for error"""
        return {
            "documentation": "/docs/errors/" + error_type.lower(),
            "support": "/support",
            "community": "/community/errors"
        }

    def _generate_prioritization_guide(self, recommendations: List[Dict]) -> str:
        """Generate guidance for prioritizing recommendations"""
        high_priority = sum(1 for r in recommendations if r.get("priority") == "high")

        if high_priority > 0:
            return f"Start with the {high_priority} high-priority recommendation(s) first."
        return "Prioritize based on your current project needs and constraints."

    def _identify_quick_wins(self, recommendations: List[Dict]) -> List[str]:
        """Identify quick win recommendations"""
        quick_wins = []
        for rec in recommendations:
            effort = rec.get("effort_estimate", "").lower()
            if "low" in effort or "quick" in effort or "easy" in effort:
                quick_wins.append(rec.get("recommendation", ""))
        return quick_wins

    def _generate_next_steps(self, recommendations: List[Dict]) -> List[str]:
        """Generate next steps from recommendations"""
        if not recommendations:
            return ["No immediate actions required"]

        return [
            "Review all recommendations thoroughly",
            "Prioritize based on your team's capacity",
            "Create action items for high-priority recommendations",
            "Track implementation progress"
        ]

    def _format_search_results(self, results: List) -> List[Dict]:
        """Format search results"""
        formatted = []
        for result in results:
            if isinstance(result, dict):
                formatted.append({
                    "title": result.get("title", "Untitled"),
                    "relevance": self._format_confidence_level(result.get("score", 0.5)),
                    "excerpt": result.get("excerpt", result.get("content", ""))[:200],
                    "category": result.get("category", "General"),
                    "id": result.get("id", "")
                })
        return formatted

    def _assess_search_quality(self, data: Dict[str, Any]) -> str:
        """Assess search result quality"""
        results = data.get("results", [])
        if not results:
            return "No results found - try refining your query"

        avg_score = sum(r.get("score", 0) for r in results if isinstance(r, dict)) / len(results)

        if avg_score >= 0.8:
            return "Excellent match - highly relevant results"
        elif avg_score >= 0.6:
            return "Good match - relevant results found"
        elif avg_score >= 0.4:
            return "Moderate match - some relevant results"
        else:
            return "Weak match - consider refining your query"

    def _generate_related_queries(self, data: Dict[str, Any]) -> List[str]:
        """Generate related query suggestions"""
        # In production, this would use actual query analysis
        return [
            "Try more specific terms",
            "Use different keywords",
            "Broaden your search criteria"
        ]

    def _extract_consensus(self, data: Dict[str, Any]) -> List[str]:
        """Extract consensus points from synthesis"""
        return data.get("consensus", data.get("common_themes", []))

    def _extract_divergences(self, data: Dict[str, Any]) -> List[str]:
        """Extract divergent viewpoints"""
        return data.get("divergences", data.get("conflicts", []))

    def _extract_main_content(self, data: Dict[str, Any]) -> Any:
        """Extract main content from response"""
        if "content" in data:
            return data["content"]
        if "data" in data:
            return data["data"]
        if "result" in data:
            return data["result"]
        return data

    def _extract_additional_details(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract additional details"""
        excluded_keys = {"summary", "content", "data", "result", "metadata"}
        return {k: v for k, v in data.items() if k not in excluded_keys}

    def _format_metadata(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format metadata section"""
        return {
            "timestamp": data.get("timestamp", "Now"),
            "confidence": self._extract_confidence(data),
            "data_sources": data.get("data_quality", "Multiple sources"),
            "agents_involved": data.get("agents_involved", data.get("agent_ids", [])),
            "processing_time": data.get("processing_time_ms", data.get("execution_time_ms", "N/A"))
        }

    def _generate_user_guidance(
        self,
        data: Dict[str, Any],
        response_type: ResponseType
    ) -> Dict[str, Any]:
        """Generate helpful user guidance"""
        guidance = {
            "interpretation": self._generate_interpretation_guide(response_type),
            "next_actions": self._suggest_next_actions(data, response_type),
            "limitations": self._describe_limitations(data),
            "feedback": "Was this response helpful? Please provide feedback to improve."
        }

        return guidance

    def _generate_interpretation_guide(self, response_type: ResponseType) -> str:
        """Generate interpretation guidance"""
        guides = {
            ResponseType.PREDICTION: "Predictions are probabilities, not certainties. Use them to inform proactive decisions.",
            ResponseType.ANALYSIS: "Analysis provides insights based on available data. Consider it alongside other information.",
            ResponseType.RECOMMENDATION: "Recommendations are suggestions based on best practices and your context.",
            ResponseType.DESIGN: "Design proposals should be reviewed and adapted to your specific needs.",
            ResponseType.ERROR: "Errors provide information to help resolve issues. Follow the suggested steps."
        }

        return guides.get(response_type, "Review the information and apply it to your context.")

    def _suggest_next_actions(self, data: Dict[str, Any], response_type: ResponseType) -> List[str]:
        """Suggest next actions"""
        if response_type == ResponseType.ERROR:
            return ["Follow the resolution steps provided", "Contact support if needed"]

        if response_type == ResponseType.PREDICTION:
            return ["Monitor the indicators listed", "Implement prevention actions", "Review predictions regularly"]

        if response_type == ResponseType.RECOMMENDATION:
            return ["Prioritize recommendations", "Create action items", "Track implementation"]

        return ["Review the information", "Apply insights to your work", "Follow up if needed"]

    def _describe_limitations(self, data: Dict[str, Any]) -> str:
        """Describe any limitations"""
        confidence = data.get("confidence", 1.0)

        if isinstance(confidence, float) and confidence < 0.6:
            return "This response has moderate confidence due to limited data. Consider gathering more information."

        data_quality = data.get("data_quality", 100)
        if isinstance(data_quality, int) and data_quality < 10:
            return "Limited historical data available. Results may be less accurate."

        return "No significant limitations identified."
