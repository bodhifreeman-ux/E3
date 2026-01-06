"""
UX Integration Example

Demonstrates how to integrate UX enhancements into the E3-DevMind-AI system.
"""

from typing import Dict, Any, List, Optional
import asyncio
from datetime import datetime

# Import UX components
from ux.response_formatter import ResponseFormatter, ResponseType
from ux.confidence_scorer import ConfidenceScorer
from ux.metadata_enhancer import MetadataEnhancer
from ux.error_handler import UserFriendlyErrorHandler
from ux.presentation import PresentationEngine, OutputFormat


class UXEnhancedResponse:
    """
    Wrapper that applies UX enhancements to any response

    This can be integrated into the Oracle agent or used as a
    post-processing step for all agent responses.
    """

    def __init__(self):
        self.formatter = ResponseFormatter()
        self.scorer = ConfidenceScorer()
        self.enhancer = MetadataEnhancer()
        self.presenter = PresentationEngine()
        self.error_handler = UserFriendlyErrorHandler()

    async def enhance_response(
        self,
        raw_response: Dict[str, Any],
        agents_involved: List[str],
        processing_time_ms: float,
        response_type: Optional[ResponseType] = None,
        agent_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Apply comprehensive UX enhancements to a response

        Args:
            raw_response: Raw response from agents
            agents_involved: List of agent IDs that contributed
            processing_time_ms: Processing time in milliseconds
            response_type: Type of response (auto-detected if None)
            agent_context: Additional agent context

        Returns:
            Fully enhanced response with all UX improvements
        """
        # Auto-detect response type if not provided
        if response_type is None:
            response_type = self._detect_response_type(raw_response)

        # 1. Format the response for clarity
        formatted_response = self.formatter.format_response(
            response_data=raw_response,
            response_type=response_type,
            include_metadata=True
        )

        # 2. Calculate confidence with detailed explanation
        confidence_assessment = self.scorer.calculate_confidence(
            response_data=raw_response,
            agent_context=agent_context
        )

        # 3. Enhance with rich metadata
        enhanced_metadata = self.enhancer.enhance_metadata(
            response_data=raw_response,
            agents_involved=agents_involved,
            processing_time_ms=processing_time_ms,
            additional_context=agent_context
        )

        # 4. Combine everything into complete response
        complete_response = {
            **formatted_response,
            "confidence_assessment": confidence_assessment,
            "metadata": enhanced_metadata,
            "response_type": response_type.value,
            "enhanced_at": datetime.utcnow().isoformat() + "Z"
        }

        return complete_response

    def present(
        self,
        enhanced_response: Dict[str, Any],
        output_format: OutputFormat = OutputFormat.CLI,
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Present enhanced response in specified format

        Args:
            enhanced_response: Response with UX enhancements
            output_format: Desired output format
            options: Format-specific options

        Returns:
            Formatted output string
        """
        return self.presenter.present(
            response_data=enhanced_response,
            output_format=output_format,
            options=options or {}
        )

    def handle_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        output_format: OutputFormat = OutputFormat.CLI
    ) -> str:
        """
        Handle an error with user-friendly messaging

        Args:
            error: The exception that occurred
            context: Additional context
            output_format: Desired output format

        Returns:
            User-friendly error message
        """
        error_response = self.error_handler.handle_error(error, context)

        if output_format == OutputFormat.CLI:
            return self.error_handler.format_error_for_cli(error_response)
        elif output_format == OutputFormat.API:
            return self.error_handler.format_error_for_api(error_response)
        else:
            return str(error_response)

    def _detect_response_type(self, response: Dict[str, Any]) -> ResponseType:
        """Auto-detect response type from content"""
        if "predictions" in response or "risks" in response:
            return ResponseType.PREDICTION
        elif "design" in response or "architecture" in response:
            return ResponseType.DESIGN
        elif "code" in response or "implementation" in response:
            return ResponseType.IMPLEMENTATION
        elif "error" in response or "error_type" in response:
            return ResponseType.ERROR
        elif "recommendations" in response:
            return ResponseType.RECOMMENDATION
        elif "results" in response or "search_results" in response:
            return ResponseType.QUERY_RESULT
        elif "synthesis" in response:
            return ResponseType.SYNTHESIS
        elif "findings" in response or "analysis" in response:
            return ResponseType.ANALYSIS
        else:
            return ResponseType.GENERAL


# Example integration with Oracle agent
class OracleWithUXEnhancements:
    """
    Example of how to integrate UX enhancements into Oracle agent

    This shows the modification needed to Oracle's query_from_human method
    """

    def __init__(self, oracle_agent, anlt_interface):
        self.oracle = oracle_agent
        self.anlt = anlt_interface
        self.ux = UXEnhancedResponse()

    async def query_from_human(
        self,
        human_query: str,
        output_format: OutputFormat = OutputFormat.CLI,
        include_ux_enhancements: bool = True
    ) -> str:
        """
        Process human query with UX enhancements

        Args:
            human_query: Natural language query from user
            output_format: Desired output format
            include_ux_enhancements: Whether to apply UX enhancements

        Returns:
            Formatted response string
        """
        start_time = datetime.utcnow()

        try:
            # 1. Translate to CSDL
            csdl_query = await self.anlt.human_to_csdl(human_query)

            # 2. Process through Oracle
            csdl_response = await self.oracle.query_from_human(csdl_query)

            # Calculate processing time
            processing_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

            # 3. Translate back to human language
            human_response_text = await self.anlt.csdl_to_human(csdl_response)

            # Convert to structured format
            response_data = {
                "summary": human_response_text,
                **csdl_response  # Include all CSDL data
            }

            # 4. Apply UX enhancements if requested
            if include_ux_enhancements:
                agents_involved = csdl_response.get(
                    "agent_ids",
                    csdl_response.get("agents_involved", ["oracle"])
                )

                # Enhance the response
                enhanced_response = await self.ux.enhance_response(
                    raw_response=response_data,
                    agents_involved=agents_involved,
                    processing_time_ms=processing_time_ms,
                    agent_context={
                        "query": human_query,
                        "historical_accuracy": 0.85  # Track this in production
                    }
                )

                # Present in desired format
                return self.ux.present(
                    enhanced_response=enhanced_response,
                    output_format=output_format,
                    options={"verbose": True}
                )
            else:
                # Return basic response
                return human_response_text

        except Exception as e:
            # Handle error with user-friendly messaging
            return self.ux.handle_error(
                error=e,
                context={
                    "query": human_query,
                    "timestamp": start_time.isoformat()
                },
                output_format=output_format
            )


# Example usage
async def example_usage():
    """
    Example of using UX enhancements
    """
    # Initialize UX wrapper
    ux = UXEnhancedResponse()

    # Example 1: Enhance a prediction response
    prediction_response = {
        "risks": [
            {
                "description": "Timeline delay risk for Sprint 24",
                "probability": 0.75,
                "impact": "high",
                "timeframe": "next_2_weeks",
                "indicators": ["Velocity drop", "Increased blockers"],
                "prevention_actions": [
                    "Add additional resources",
                    "Remove non-critical tasks"
                ]
            }
        ],
        "confidence": 0.85,
        "data_quality": 15,
        "agents_involved": ["oracle", "prophet", "strategist"]
    }

    enhanced = await ux.enhance_response(
        raw_response=prediction_response,
        agents_involved=["oracle", "prophet", "strategist"],
        processing_time_ms=1250.5,
        response_type=ResponseType.PREDICTION
    )

    # Present for CLI
    cli_output = ux.present(enhanced, OutputFormat.CLI, {"verbose": True})
    print(cli_output)

    print("\n" + "="*80 + "\n")

    # Present for API
    api_output = ux.present(enhanced, OutputFormat.API, {"pretty": True})
    print(api_output)

    print("\n" + "="*80 + "\n")

    # Present as Markdown
    markdown_output = ux.present(
        enhanced,
        OutputFormat.MARKDOWN,
        {"title": "Risk Analysis Report", "include_metadata": True}
    )
    print(markdown_output)


# Example 2: Error handling
async def example_error_handling():
    """
    Example of error handling with UX enhancements
    """
    ux = UXEnhancedResponse()

    try:
        # Simulate an error
        raise ValueError("Invalid input format: expected JSON, got string")
    except Exception as e:
        # Handle with user-friendly messaging
        error_output = ux.handle_error(
            error=e,
            context={"operation": "data_validation", "input_type": "string"},
            output_format=OutputFormat.CLI
        )
        print(error_output)


# Example 3: Complete workflow
async def example_complete_workflow():
    """
    Example of complete query workflow with UX enhancements
    """
    # This simulates the full flow from human query to enhanced response

    # Simulated components (in production, these would be real)
    class MockOracle:
        async def query_from_human(self, csdl):
            return {
                "agent_ids": ["oracle", "prophet", "strategist"],
                "synthesis": {
                    "findings": [
                        "Current sprint velocity is 15% below target",
                        "Three high-priority tasks are blocked",
                        "Team capacity reduced due to leave"
                    ],
                    "recommendations": [
                        "Defer non-critical features to next sprint",
                        "Resolve blockers with stakeholder meeting",
                        "Consider extending sprint by 2 days"
                    ]
                },
                "confidence": 0.88
            }

    class MockANLT:
        async def human_to_csdl(self, text):
            return {"query": text, "intent": "risk_analysis"}

        async def csdl_to_human(self, csdl):
            return "Analysis of current sprint shows several risks requiring attention."

    # Initialize
    oracle = MockOracle()
    anlt = MockANLT()
    oracle_with_ux = OracleWithUXEnhancements(oracle, anlt)

    # Process query
    result = await oracle_with_ux.query_from_human(
        "What are the risks in our current sprint?",
        output_format=OutputFormat.CLI,
        include_ux_enhancements=True
    )

    print(result)


if __name__ == "__main__":
    # Run examples
    print("="*80)
    print("EXAMPLE 1: Enhanced Prediction Response")
    print("="*80)
    asyncio.run(example_usage())

    print("\n\n")
    print("="*80)
    print("EXAMPLE 2: Error Handling")
    print("="*80)
    asyncio.run(example_error_handling())

    print("\n\n")
    print("="*80)
    print("EXAMPLE 3: Complete Workflow")
    print("="*80)
    asyncio.run(example_complete_workflow())
