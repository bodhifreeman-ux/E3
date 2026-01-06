"""
User-Friendly Error Handler

Transforms technical errors into helpful, actionable user messages.
"""

from typing import Dict, Any, Optional, List
from enum import Enum
import structlog

logger = structlog.get_logger()


class ErrorSeverity(str, Enum):
    """Error severity levels"""
    CRITICAL = "critical"  # System-breaking, requires immediate attention
    HIGH = "high"  # Significant impact, requires attention
    MEDIUM = "medium"  # Moderate impact, should be addressed
    LOW = "low"  # Minor impact, informational
    INFO = "info"  # Not an error, just information


class ErrorCategory(str, Enum):
    """Categories of errors"""
    VALIDATION = "validation"  # Input validation errors
    PERMISSION = "permission"  # Authorization errors
    NOT_FOUND = "not_found"  # Resource not found
    TIMEOUT = "timeout"  # Operation timeout
    RATE_LIMIT = "rate_limit"  # Rate limiting
    PROCESSING = "processing"  # Processing errors
    INTEGRATION = "integration"  # External integration errors
    CONFIGURATION = "configuration"  # Configuration errors
    NETWORK = "network"  # Network errors
    UNKNOWN = "unknown"  # Unknown errors


class UserFriendlyErrorHandler:
    """
    Converts technical errors into user-friendly messages

    Principles:
    1. Clear and concise language
    2. Actionable guidance
    3. Appropriate level of technical detail
    4. Helpful next steps
    5. Support resources
    """

    def __init__(self):
        self.error_templates = self._load_error_templates()
        self.resolution_guides = self._load_resolution_guides()

    def handle_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle an error and create user-friendly response

        Args:
            error: The exception that occurred
            context: Additional context about the error

        Returns:
            User-friendly error response
        """
        error_type = type(error).__name__
        error_message = str(error)

        # Categorize the error
        category = self._categorize_error(error_type, error_message)
        severity = self._determine_severity(category, error, context)

        # Create user-friendly message
        user_message = self._create_user_message(
            error_type,
            error_message,
            category,
            severity
        )

        # Generate resolution steps
        resolution_steps = self._generate_resolution_steps(category, error, context)

        # Gather support resources
        support_resources = self._gather_support_resources(category, severity)

        # Create structured error response
        error_response = {
            "error": {
                "category": category.value,
                "severity": severity.value,
                "title": self._get_error_title(category),
                "message": user_message,
                "user_impact": self._describe_user_impact(category, severity),
                "what_happened": self._explain_what_happened(error, category),
            },
            "resolution": {
                "immediate_steps": resolution_steps.get("immediate", []),
                "detailed_steps": resolution_steps.get("detailed", []),
                "alternative_approaches": resolution_steps.get("alternatives", []),
                "expected_resolution_time": self._estimate_resolution_time(category, severity)
            },
            "support": support_resources,
            "technical_details": {
                "error_type": error_type,
                "error_message": error_message,
                "context": context or {},
                "stack_trace_available": hasattr(error, "__traceback__")
            }
        }

        # Log the error with appropriate level
        self._log_error(error, error_response, severity)

        return error_response

    def format_error_for_api(
        self,
        error_response: Dict[str, Any],
        include_technical: bool = False
    ) -> Dict[str, Any]:
        """
        Format error response for API consumption

        Args:
            error_response: Full error response
            include_technical: Whether to include technical details

        Returns:
            API-formatted error
        """
        api_response = {
            "status": "error",
            "error": {
                "code": error_response["error"]["category"],
                "message": error_response["error"]["message"],
                "severity": error_response["error"]["severity"],
                "title": error_response["error"]["title"]
            },
            "resolution": {
                "steps": error_response["resolution"]["immediate_steps"],
                "help_url": error_response["support"].get("documentation_url", "")
            }
        }

        if include_technical:
            api_response["technical_details"] = error_response["technical_details"]

        return api_response

    def format_error_for_cli(self, error_response: Dict[str, Any]) -> str:
        """
        Format error for CLI display

        Args:
            error_response: Full error response

        Returns:
            CLI-formatted error message
        """
        lines = []

        # Title with emoji indicator
        severity_emoji = {
            ErrorSeverity.CRITICAL: "🔴",
            ErrorSeverity.HIGH: "🟠",
            ErrorSeverity.MEDIUM: "🟡",
            ErrorSeverity.LOW: "🔵",
            ErrorSeverity.INFO: "ℹ️"
        }
        emoji = severity_emoji.get(
            ErrorSeverity(error_response["error"]["severity"]),
            "❌"
        )

        lines.append(f"\n{emoji} {error_response['error']['title']}")
        lines.append("=" * 60)

        # Message
        lines.append(f"\n{error_response['error']['message']}\n")

        # What happened
        if error_response["error"]["what_happened"]:
            lines.append("What happened:")
            lines.append(f"  {error_response['error']['what_happened']}\n")

        # Immediate steps
        if error_response["resolution"]["immediate_steps"]:
            lines.append("What to do:")
            for i, step in enumerate(error_response["resolution"]["immediate_steps"], 1):
                lines.append(f"  {i}. {step}")
            lines.append("")

        # Support
        if error_response["support"].get("documentation_url"):
            lines.append(f"📚 Documentation: {error_response['support']['documentation_url']}")

        if error_response["support"].get("need_help"):
            lines.append(f"💬 Get help: {error_response['support']['need_help']}")

        lines.append("")

        return "\n".join(lines)

    def _load_error_templates(self) -> Dict[ErrorCategory, str]:
        """Load user-friendly error message templates"""
        return {
            ErrorCategory.VALIDATION: "The input provided doesn't meet the required format or constraints.",
            ErrorCategory.PERMISSION: "You don't have permission to perform this operation.",
            ErrorCategory.NOT_FOUND: "The requested resource could not be found.",
            ErrorCategory.TIMEOUT: "The operation took too long to complete and was stopped.",
            ErrorCategory.RATE_LIMIT: "Too many requests have been made. Please wait before trying again.",
            ErrorCategory.PROCESSING: "An error occurred while processing your request.",
            ErrorCategory.INTEGRATION: "An error occurred while communicating with an external service.",
            ErrorCategory.CONFIGURATION: "There's a configuration issue preventing this operation.",
            ErrorCategory.NETWORK: "A network error prevented the operation from completing.",
            ErrorCategory.UNKNOWN: "An unexpected error occurred."
        }

    def _load_resolution_guides(self) -> Dict[ErrorCategory, Dict[str, List[str]]]:
        """Load resolution guides for each error category"""
        return {
            ErrorCategory.VALIDATION: {
                "immediate": [
                    "Check your input for typos or incorrect formatting",
                    "Review the required format and try again"
                ],
                "detailed": [
                    "Verify all required fields are provided",
                    "Check data types match expectations (e.g., numbers not text)",
                    "Ensure values are within acceptable ranges",
                    "Review the API documentation for format requirements"
                ],
                "alternatives": [
                    "Use a different input format if supported",
                    "Try with minimal required fields first"
                ]
            },
            ErrorCategory.PERMISSION: {
                "immediate": [
                    "Verify you are logged in with the correct account",
                    "Contact your administrator if you need access"
                ],
                "detailed": [
                    "Check if your account has the required permissions",
                    "Verify your access token or API key is valid",
                    "Ensure your subscription includes this feature",
                    "Request access from your team administrator"
                ],
                "alternatives": [
                    "Try with a different account that has access",
                    "Use a read-only operation if available"
                ]
            },
            ErrorCategory.NOT_FOUND: {
                "immediate": [
                    "Check the resource ID or name is correct",
                    "Verify the resource exists"
                ],
                "detailed": [
                    "Double-check for typos in the resource identifier",
                    "Verify the resource hasn't been deleted",
                    "Check if you're looking in the correct project or workspace",
                    "Try searching for the resource to confirm it exists"
                ],
                "alternatives": [
                    "List all available resources to find the correct ID",
                    "Create the resource if it doesn't exist"
                ]
            },
            ErrorCategory.TIMEOUT: {
                "immediate": [
                    "Try the operation again",
                    "Break the request into smaller parts if possible"
                ],
                "detailed": [
                    "Wait a moment before retrying to allow system recovery",
                    "Reduce the scope of your request if possible",
                    "Check if the system is experiencing high load",
                    "Try during off-peak hours if the operation isn't urgent"
                ],
                "alternatives": [
                    "Use a background job or async operation",
                    "Process data in smaller batches"
                ]
            },
            ErrorCategory.RATE_LIMIT: {
                "immediate": [
                    "Wait a few minutes before trying again",
                    "Reduce the frequency of your requests"
                ],
                "detailed": [
                    "Check your rate limit quotas and usage",
                    "Implement exponential backoff in your code",
                    "Cache responses to reduce duplicate requests",
                    "Consider upgrading your plan for higher limits"
                ],
                "alternatives": [
                    "Batch multiple operations into single requests",
                    "Use webhooks instead of polling"
                ]
            },
            ErrorCategory.PROCESSING: {
                "immediate": [
                    "Try your request again",
                    "If the problem persists, contact support"
                ],
                "detailed": [
                    "Wait a moment and retry the operation",
                    "Check if the issue is with your input data",
                    "Review the error details for specific issues",
                    "Report the issue with error details if it continues"
                ],
                "alternatives": [
                    "Try a simpler version of your request",
                    "Use alternative agents or approaches if available"
                ]
            },
            ErrorCategory.INTEGRATION: {
                "immediate": [
                    "Check if the external service is available",
                    "Try again in a few minutes"
                ],
                "detailed": [
                    "Verify the external service is operational",
                    "Check your credentials for the external service",
                    "Review integration configuration settings",
                    "Check network connectivity to the service"
                ],
                "alternatives": [
                    "Use cached data if available",
                    "Try an alternative integration if configured"
                ]
            },
            ErrorCategory.CONFIGURATION: {
                "immediate": [
                    "Contact your system administrator",
                    "Review configuration documentation"
                ],
                "detailed": [
                    "Verify all required configuration values are set",
                    "Check configuration file syntax and format",
                    "Ensure environment variables are properly set",
                    "Review configuration against documentation"
                ],
                "alternatives": [
                    "Use default configuration if appropriate",
                    "Temporarily disable the misconfigured feature"
                ]
            },
            ErrorCategory.NETWORK: {
                "immediate": [
                    "Check your internet connection",
                    "Try again in a moment"
                ],
                "detailed": [
                    "Verify network connectivity",
                    "Check if firewall is blocking the connection",
                    "Try from a different network if possible",
                    "Check if the service is experiencing downtime"
                ],
                "alternatives": [
                    "Use offline mode if available",
                    "Try again later"
                ]
            },
            ErrorCategory.UNKNOWN: {
                "immediate": [
                    "Try your operation again",
                    "Contact support if the problem persists"
                ],
                "detailed": [
                    "Note what you were doing when the error occurred",
                    "Check system status page for known issues",
                    "Try a simpler operation to test if system is working",
                    "Report the issue with full error details"
                ],
                "alternatives": [
                    "Try an alternative approach to achieve your goal",
                    "Wait and retry later"
                ]
            }
        }

    def _categorize_error(self, error_type: str, error_message: str) -> ErrorCategory:
        """Categorize error based on type and message"""
        error_type_lower = error_type.lower()
        error_message_lower = error_message.lower()

        # Check error type
        if "validation" in error_type_lower or "invalid" in error_message_lower:
            return ErrorCategory.VALIDATION
        elif "permission" in error_type_lower or "forbidden" in error_message_lower or "unauthorized" in error_message_lower:
            return ErrorCategory.PERMISSION
        elif "notfound" in error_type_lower or "not found" in error_message_lower or "404" in error_message:
            return ErrorCategory.NOT_FOUND
        elif "timeout" in error_type_lower or "timeout" in error_message_lower:
            return ErrorCategory.TIMEOUT
        elif "ratelimit" in error_type_lower or "rate limit" in error_message_lower or "429" in error_message:
            return ErrorCategory.RATE_LIMIT
        elif "network" in error_type_lower or "connection" in error_message_lower:
            return ErrorCategory.NETWORK
        elif "config" in error_type_lower or "configuration" in error_message_lower:
            return ErrorCategory.CONFIGURATION
        elif "integration" in error_type_lower or "external" in error_message_lower:
            return ErrorCategory.INTEGRATION
        elif "processing" in error_type_lower:
            return ErrorCategory.PROCESSING

        return ErrorCategory.UNKNOWN

    def _determine_severity(
        self,
        category: ErrorCategory,
        error: Exception,
        context: Optional[Dict[str, Any]]
    ) -> ErrorSeverity:
        """Determine error severity"""
        # Critical errors
        if category in [ErrorCategory.CONFIGURATION]:
            return ErrorSeverity.CRITICAL

        # High severity
        if category in [ErrorCategory.PERMISSION, ErrorCategory.INTEGRATION]:
            return ErrorSeverity.HIGH

        # Medium severity
        if category in [ErrorCategory.PROCESSING, ErrorCategory.TIMEOUT, ErrorCategory.NETWORK]:
            return ErrorSeverity.MEDIUM

        # Low severity
        if category in [ErrorCategory.VALIDATION, ErrorCategory.NOT_FOUND, ErrorCategory.RATE_LIMIT]:
            return ErrorSeverity.LOW

        # Default to medium
        return ErrorSeverity.MEDIUM

    def _create_user_message(
        self,
        error_type: str,
        error_message: str,
        category: ErrorCategory,
        severity: ErrorSeverity
    ) -> str:
        """Create user-friendly error message"""
        base_message = self.error_templates.get(category, self.error_templates[ErrorCategory.UNKNOWN])

        # Add context from the original error if helpful
        if category == ErrorCategory.VALIDATION:
            # Include specific validation details
            return f"{base_message} {self._extract_validation_details(error_message)}"
        elif category == ErrorCategory.NOT_FOUND:
            # Include what wasn't found
            return f"{base_message} {self._extract_resource_details(error_message)}"
        elif category == ErrorCategory.TIMEOUT:
            # Include operation details
            return f"{base_message} {self._extract_operation_details(error_message)}"

        return base_message

    def _extract_validation_details(self, error_message: str) -> str:
        """Extract useful validation details from error message"""
        # Simplify technical validation messages
        if "required" in error_message.lower():
            return "Please ensure all required fields are provided."
        elif "format" in error_message.lower():
            return "Please check the format of your input."
        elif "type" in error_message.lower():
            return "Please check that values are of the correct type."
        return ""

    def _extract_resource_details(self, error_message: str) -> str:
        """Extract resource details from error message"""
        # Try to extract resource name/id from message
        # Simplified implementation
        return "Please verify the resource identifier."

    def _extract_operation_details(self, error_message: str) -> str:
        """Extract operation details from error message"""
        return "This may be due to system load or data volume."

    def _get_error_title(self, category: ErrorCategory) -> str:
        """Get user-friendly error title"""
        titles = {
            ErrorCategory.VALIDATION: "Input Validation Error",
            ErrorCategory.PERMISSION: "Permission Denied",
            ErrorCategory.NOT_FOUND: "Resource Not Found",
            ErrorCategory.TIMEOUT: "Operation Timeout",
            ErrorCategory.RATE_LIMIT: "Rate Limit Exceeded",
            ErrorCategory.PROCESSING: "Processing Error",
            ErrorCategory.INTEGRATION: "Integration Error",
            ErrorCategory.CONFIGURATION: "Configuration Error",
            ErrorCategory.NETWORK: "Network Error",
            ErrorCategory.UNKNOWN: "Unexpected Error"
        }
        return titles.get(category, "Error")

    def _describe_user_impact(self, category: ErrorCategory, severity: ErrorSeverity) -> str:
        """Describe the impact on user"""
        if severity == ErrorSeverity.CRITICAL:
            return "This error prevents the system from functioning. Immediate action required."
        elif severity == ErrorSeverity.HIGH:
            return "This error prevents your operation from completing. Resolution needed."
        elif severity == ErrorSeverity.MEDIUM:
            return "This error prevented your operation. You can retry or try alternatives."
        else:
            return "This error is informational. Your workflow can continue with adjustments."

    def _explain_what_happened(self, error: Exception, category: ErrorCategory) -> str:
        """Explain what happened in user-friendly terms"""
        explanations = {
            ErrorCategory.VALIDATION: "The system checked your input and found it doesn't match the expected format.",
            ErrorCategory.PERMISSION: "The system checked your permissions and found you don't have access to this resource.",
            ErrorCategory.NOT_FOUND: "The system searched for the requested resource but couldn't find it.",
            ErrorCategory.TIMEOUT: "The operation started but didn't complete within the time limit.",
            ErrorCategory.RATE_LIMIT: "The system detected too many requests from your account in a short time.",
            ErrorCategory.PROCESSING: "The system encountered an error while processing your request.",
            ErrorCategory.INTEGRATION: "The system tried to communicate with an external service but failed.",
            ErrorCategory.CONFIGURATION: "The system found a configuration issue that prevents operation.",
            ErrorCategory.NETWORK: "The system experienced a network connectivity issue.",
            ErrorCategory.UNKNOWN: "The system encountered an unexpected situation."
        }
        return explanations.get(category, "An error occurred during processing.")

    def _generate_resolution_steps(
        self,
        category: ErrorCategory,
        error: Exception,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """Generate resolution steps for the error"""
        return self.resolution_guides.get(
            category,
            self.resolution_guides[ErrorCategory.UNKNOWN]
        )

    def _gather_support_resources(
        self,
        category: ErrorCategory,
        severity: ErrorSeverity
    ) -> Dict[str, str]:
        """Gather relevant support resources"""
        base_docs = "/docs/troubleshooting/"

        resources = {
            "documentation_url": f"{base_docs}{category.value}",
            "api_reference": "/docs/api",
            "status_page": "/status",
        }

        if severity in [ErrorSeverity.CRITICAL, ErrorSeverity.HIGH]:
            resources["need_help"] = "/support/urgent"
        else:
            resources["need_help"] = "/support"

        resources["community"] = "/community"

        return resources

    def _estimate_resolution_time(
        self,
        category: ErrorCategory,
        severity: ErrorSeverity
    ) -> str:
        """Estimate time to resolution"""
        if category == ErrorCategory.RATE_LIMIT:
            return "A few minutes"
        elif category == ErrorCategory.VALIDATION:
            return "Immediate (once input is corrected)"
        elif category == ErrorCategory.TIMEOUT:
            return "Immediate to a few minutes (retry)"
        elif category in [ErrorCategory.NETWORK, ErrorCategory.INTEGRATION]:
            return "A few minutes to an hour (depends on external service)"
        elif category in [ErrorCategory.CONFIGURATION, ErrorCategory.PERMISSION]:
            return "Hours to days (requires administrator action)"
        else:
            return "Varies (depends on issue complexity)"

    def _log_error(
        self,
        error: Exception,
        error_response: Dict[str, Any],
        severity: ErrorSeverity
    ):
        """Log error with appropriate level"""
        log_data = {
            "error_type": type(error).__name__,
            "category": error_response["error"]["category"],
            "severity": severity.value,
            "message": error_response["error"]["message"]
        }

        if severity == ErrorSeverity.CRITICAL:
            logger.critical("critical_error", **log_data, exc_info=error)
        elif severity == ErrorSeverity.HIGH:
            logger.error("high_severity_error", **log_data, exc_info=error)
        elif severity == ErrorSeverity.MEDIUM:
            logger.warning("medium_severity_error", **log_data)
        else:
            logger.info("low_severity_error", **log_data)
