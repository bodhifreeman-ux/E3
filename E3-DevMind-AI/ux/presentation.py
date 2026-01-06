"""
Presentation Engine

Formats responses for different output channels (CLI, API, UI, etc.)
"""

from typing import Dict, Any, List, Optional
from enum import Enum
import json
import structlog

logger = structlog.get_logger()


class OutputFormat(str, Enum):
    """Supported output formats"""
    CLI = "cli"  # Command-line interface
    API = "api"  # REST API JSON
    MARKDOWN = "markdown"  # Markdown documentation
    HTML = "html"  # HTML for web UI
    PLAIN_TEXT = "plain_text"  # Plain text
    STRUCTURED = "structured"  # Structured data (dict)


class PresentationEngine:
    """
    Formats responses for optimal presentation across different channels

    Handles:
    1. Format-specific rendering
    2. Syntax highlighting
    3. Proper spacing and layout
    4. Visual hierarchy
    5. Interactive elements (where applicable)
    """

    def __init__(self):
        self.formatters = {
            OutputFormat.CLI: self._format_for_cli,
            OutputFormat.API: self._format_for_api,
            OutputFormat.MARKDOWN: self._format_as_markdown,
            OutputFormat.HTML: self._format_as_html,
            OutputFormat.PLAIN_TEXT: self._format_as_plain_text,
            OutputFormat.STRUCTURED: self._format_as_structured
        }

    def present(
        self,
        response_data: Dict[str, Any],
        output_format: OutputFormat = OutputFormat.CLI,
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Present response in specified format

        Args:
            response_data: Response data to present
            output_format: Desired output format
            options: Format-specific options

        Returns:
            Formatted output string
        """
        options = options or {}
        formatter = self.formatters.get(output_format, self._format_as_structured)

        try:
            return formatter(response_data, options)
        except Exception as e:
            logger.error("presentation_error", format=output_format.value, error=str(e))
            # Fallback to plain text
            return self._format_as_plain_text(response_data, options)

    def _format_for_cli(self, data: Dict[str, Any], options: Dict[str, Any]) -> str:
        """Format for CLI display with colors and structure"""
        lines = []

        # Header
        if "summary" in data:
            lines.append(self._cli_header("Summary"))
            lines.append(self._wrap_text(data["summary"], indent=2))
            lines.append("")

        # Key findings
        if "key_findings" in data:
            lines.append(self._cli_header("Key Findings"))
            for i, finding in enumerate(data["key_findings"], 1):
                lines.append(f"  {i}. {finding}")
            lines.append("")

        # Predictions
        if "predictions" in data:
            lines.append(self._cli_header("Predictions"))
            for pred in data["predictions"]:
                if isinstance(pred, dict):
                    lines.append(f"  • {pred.get('prediction', str(pred))}")
                    if "probability" in pred:
                        lines.append(f"    Probability: {pred['probability']}")
                    if "timeframe" in pred:
                        lines.append(f"    Timeframe: {pred['timeframe']}")
                    lines.append("")
            lines.append("")

        # Recommendations
        if "recommendations" in data:
            lines.append(self._cli_header("Recommendations"))
            for i, rec in enumerate(data["recommendations"], 1):
                if isinstance(rec, dict):
                    lines.append(f"  {i}. {rec.get('recommendation', str(rec))}")
                    if "priority" in rec:
                        lines.append(f"     Priority: {rec['priority']}")
                else:
                    lines.append(f"  {i}. {rec}")
            lines.append("")

        # Design overview
        if "design_overview" in data:
            lines.append(self._cli_header("Design Overview"))
            lines.append(self._format_dict_for_cli(data["design_overview"], indent=2))
            lines.append("")

        # User guidance
        if "user_guidance" in data:
            guidance = data["user_guidance"]
            lines.append(self._cli_section("How to Use These Results"))

            if "interpretation" in guidance:
                lines.append(f"  ℹ️  {guidance['interpretation']}")
                lines.append("")

            if "next_actions" in guidance and guidance["next_actions"]:
                lines.append("  Next Actions:")
                for action in guidance["next_actions"]:
                    lines.append(f"    • {action}")
                lines.append("")

        # Metadata (if verbose)
        if options.get("verbose") and "metadata" in data:
            lines.append(self._cli_section("Details"))
            metadata = data["metadata"]

            if "confidence" in metadata:
                lines.append(f"  Confidence: {metadata['confidence']}")

            if "processing_time" in metadata:
                time_info = metadata["processing_time"]
                if isinstance(time_info, dict):
                    lines.append(f"  Processing Time: {time_info.get('human_readable', 'N/A')}")

            if "agents_involved" in metadata and metadata["agents_involved"]:
                agents = metadata["agents_involved"]
                if isinstance(agents, list):
                    agent_names = [a.get("name", a) if isinstance(a, dict) else a for a in agents]
                    lines.append(f"  Agents Involved: {', '.join(agent_names)}")

            lines.append("")

        return "\n".join(lines)

    def _format_for_api(self, data: Dict[str, Any], options: Dict[str, Any]) -> str:
        """Format for API response (JSON)"""
        # Clean up for API - remove internal fields
        api_data = {
            "status": "success",
            "data": self._clean_for_api(data),
            "metadata": data.get("metadata", {})
        }

        # Pretty print if requested
        if options.get("pretty", True):
            return json.dumps(api_data, indent=2, default=str)
        else:
            return json.dumps(api_data, default=str)

    def _format_as_markdown(self, data: Dict[str, Any], options: Dict[str, Any]) -> str:
        """Format as Markdown document"""
        lines = []

        # Title
        title = options.get("title", "E3 DevMind AI Response")
        lines.append(f"# {title}\n")

        # Summary
        if "summary" in data:
            lines.append("## Summary\n")
            lines.append(f"{data['summary']}\n")

        # Key Findings
        if "key_findings" in data:
            lines.append("## Key Findings\n")
            for i, finding in enumerate(data["key_findings"], 1):
                lines.append(f"{i}. {finding}")
            lines.append("")

        # Detailed Analysis
        if "detailed_analysis" in data:
            lines.append("## Detailed Analysis\n")
            lines.append(self._format_value_as_markdown(data["detailed_analysis"]))
            lines.append("")

        # Predictions
        if "predictions" in data:
            lines.append("## Predictions\n")
            for pred in data["predictions"]:
                if isinstance(pred, dict):
                    lines.append(f"### {pred.get('prediction', 'Prediction')}\n")
                    if "probability" in pred:
                        lines.append(f"**Probability:** {pred['probability']}\n")
                    if "timeframe" in pred:
                        lines.append(f"**Timeframe:** {pred['timeframe']}\n")
                    if "mitigation" in pred and pred["mitigation"]:
                        lines.append("**Mitigation:**")
                        for mit in pred["mitigation"]:
                            lines.append(f"- {mit}")
                    lines.append("")

        # Recommendations
        if "recommendations" in data:
            lines.append("## Recommendations\n")
            for i, rec in enumerate(data["recommendations"], 1):
                if isinstance(rec, dict):
                    lines.append(f"{i}. **{rec.get('recommendation', 'Recommendation')}**")
                    if "priority" in rec:
                        lines.append(f"   - Priority: {rec['priority']}")
                    if "rationale" in rec:
                        lines.append(f"   - Rationale: {rec['rationale']}")
                else:
                    lines.append(f"{i}. {rec}")
            lines.append("")

        # Design
        if "design_overview" in data:
            lines.append("## Design Overview\n")
            lines.append("```")
            lines.append(json.dumps(data["design_overview"], indent=2))
            lines.append("```\n")

        # Metadata
        if "metadata" in data and options.get("include_metadata", True):
            lines.append("## Metadata\n")
            metadata = data["metadata"]

            if "confidence" in metadata:
                lines.append(f"- **Confidence:** {metadata['confidence']}")

            if "processing" in metadata:
                proc = metadata["processing"]
                if isinstance(proc, dict) and "processing_time" in proc:
                    time_info = proc["processing_time"]
                    if isinstance(time_info, dict):
                        lines.append(f"- **Processing Time:** {time_info.get('human_readable', 'N/A')}")

            lines.append("")

        return "\n".join(lines)

    def _format_as_html(self, data: Dict[str, Any], options: Dict[str, Any]) -> str:
        """Format as HTML for web display"""
        html_parts = []

        # Container
        html_parts.append('<div class="e3-response">')

        # Summary
        if "summary" in data:
            html_parts.append('<div class="summary">')
            html_parts.append(f'<h2>Summary</h2>')
            html_parts.append(f'<p>{self._html_escape(data["summary"])}</p>')
            html_parts.append('</div>')

        # Key Findings
        if "key_findings" in data:
            html_parts.append('<div class="findings">')
            html_parts.append('<h2>Key Findings</h2>')
            html_parts.append('<ul>')
            for finding in data["key_findings"]:
                html_parts.append(f'<li>{self._html_escape(str(finding))}</li>')
            html_parts.append('</ul>')
            html_parts.append('</div>')

        # Predictions
        if "predictions" in data:
            html_parts.append('<div class="predictions">')
            html_parts.append('<h2>Predictions</h2>')
            for pred in data["predictions"]:
                if isinstance(pred, dict):
                    html_parts.append('<div class="prediction-item">')
                    html_parts.append(f'<h3>{self._html_escape(pred.get("prediction", "Prediction"))}</h3>')

                    if "probability" in pred:
                        html_parts.append(f'<p><strong>Probability:</strong> {pred["probability"]}</p>')

                    if "confidence" in pred:
                        confidence_class = self._get_confidence_class(pred["confidence"])
                        html_parts.append(
                            f'<p><strong>Confidence:</strong> '
                            f'<span class="{confidence_class}">{pred["confidence"]}</span></p>'
                        )

                    html_parts.append('</div>')
            html_parts.append('</div>')

        # Recommendations
        if "recommendations" in data:
            html_parts.append('<div class="recommendations">')
            html_parts.append('<h2>Recommendations</h2>')
            html_parts.append('<ol>')
            for rec in data["recommendations"]:
                if isinstance(rec, dict):
                    priority = rec.get("priority", "medium")
                    html_parts.append(f'<li class="priority-{priority}">')
                    html_parts.append(self._html_escape(rec.get("recommendation", str(rec))))
                    html_parts.append('</li>')
                else:
                    html_parts.append(f'<li>{self._html_escape(str(rec))}</li>')
            html_parts.append('</ol>')
            html_parts.append('</div>')

        # Close container
        html_parts.append('</div>')

        return "\n".join(html_parts)

    def _format_as_plain_text(self, data: Dict[str, Any], options: Dict[str, Any]) -> str:
        """Format as plain text"""
        lines = []

        # Summary
        if "summary" in data:
            lines.append("SUMMARY")
            lines.append("=" * 60)
            lines.append(data["summary"])
            lines.append("")

        # Key findings
        if "key_findings" in data:
            lines.append("KEY FINDINGS")
            lines.append("=" * 60)
            for i, finding in enumerate(data["key_findings"], 1):
                lines.append(f"{i}. {finding}")
            lines.append("")

        # Predictions
        if "predictions" in data:
            lines.append("PREDICTIONS")
            lines.append("=" * 60)
            for pred in data["predictions"]:
                if isinstance(pred, dict):
                    lines.append(f"- {pred.get('prediction', str(pred))}")
                    if "probability" in pred:
                        lines.append(f"  Probability: {pred['probability']}")
                else:
                    lines.append(f"- {pred}")
            lines.append("")

        # Recommendations
        if "recommendations" in data:
            lines.append("RECOMMENDATIONS")
            lines.append("=" * 60)
            for i, rec in enumerate(data["recommendations"], 1):
                if isinstance(rec, dict):
                    lines.append(f"{i}. {rec.get('recommendation', str(rec))}")
                else:
                    lines.append(f"{i}. {rec}")
            lines.append("")

        return "\n".join(lines)

    def _format_as_structured(self, data: Dict[str, Any], options: Dict[str, Any]) -> str:
        """Return as structured JSON"""
        return json.dumps(data, indent=2, default=str)

    # Helper methods

    def _cli_header(self, text: str) -> str:
        """Create CLI header"""
        return f"\n{'='*60}\n{text}\n{'='*60}"

    def _cli_section(self, text: str) -> str:
        """Create CLI section header"""
        return f"\n{text}\n{'-'*len(text)}"

    def _wrap_text(self, text: str, width: int = 76, indent: int = 0) -> str:
        """Wrap text to specified width"""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        indent_str = " " * indent

        for word in words:
            word_len = len(word) + 1
            if current_length + word_len <= width - indent:
                current_line.append(word)
                current_length += word_len
            else:
                if current_line:
                    lines.append(indent_str + " ".join(current_line))
                current_line = [word]
                current_length = word_len

        if current_line:
            lines.append(indent_str + " ".join(current_line))

        return "\n".join(lines)

    def _format_dict_for_cli(self, d: Dict[str, Any], indent: int = 0) -> str:
        """Format dictionary for CLI display"""
        lines = []
        indent_str = " " * indent

        for key, value in d.items():
            key_display = key.replace("_", " ").title()

            if isinstance(value, dict):
                lines.append(f"{indent_str}{key_display}:")
                lines.append(self._format_dict_for_cli(value, indent + 2))
            elif isinstance(value, list):
                lines.append(f"{indent_str}{key_display}:")
                for item in value:
                    if isinstance(item, dict):
                        lines.append(self._format_dict_for_cli(item, indent + 2))
                    else:
                        lines.append(f"{indent_str}  - {item}")
            else:
                lines.append(f"{indent_str}{key_display}: {value}")

        return "\n".join(lines)

    def _clean_for_api(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean data for API response"""
        # Remove internal/debug fields
        internal_fields = {"_internal", "__debug", "raw_"}
        cleaned = {}

        for key, value in data.items():
            # Skip internal fields
            if any(key.startswith(prefix) for prefix in internal_fields):
                continue

            # Recursively clean nested dicts
            if isinstance(value, dict):
                cleaned[key] = self._clean_for_api(value)
            elif isinstance(value, list):
                cleaned[key] = [
                    self._clean_for_api(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                cleaned[key] = value

        return cleaned

    def _format_value_as_markdown(self, value: Any) -> str:
        """Format a value as markdown"""
        if isinstance(value, dict):
            return "```json\n" + json.dumps(value, indent=2) + "\n```"
        elif isinstance(value, list):
            return "\n".join(f"- {item}" for item in value)
        else:
            return str(value)

    def _html_escape(self, text: str) -> str:
        """Escape HTML special characters"""
        return (text
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&#x27;"))

    def _get_confidence_class(self, confidence: str) -> str:
        """Get CSS class for confidence level"""
        if "high" in confidence.lower():
            return "confidence-high"
        elif "medium" in confidence.lower():
            return "confidence-medium"
        elif "low" in confidence.lower():
            return "confidence-low"
        return "confidence-unknown"

    def create_summary_view(self, response_data: Dict[str, Any]) -> str:
        """Create a concise summary view"""
        lines = []

        # Title
        lines.append("RESPONSE SUMMARY")
        lines.append("=" * 60)

        # Key info
        if "summary" in response_data:
            lines.append(response_data["summary"][:200])

        # Stats
        stats = []
        if "key_findings" in response_data:
            stats.append(f"{len(response_data['key_findings'])} findings")
        if "predictions" in response_data:
            stats.append(f"{len(response_data['predictions'])} predictions")
        if "recommendations" in response_data:
            stats.append(f"{len(response_data['recommendations'])} recommendations")

        if stats:
            lines.append("\nIncludes: " + ", ".join(stats))

        # Confidence
        if "metadata" in response_data and "confidence" in response_data["metadata"]:
            lines.append(f"Confidence: {response_data['metadata']['confidence']}")

        return "\n".join(lines)
