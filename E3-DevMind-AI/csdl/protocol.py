"""
CSDL Protocol Implementation

Defines the CSDL (Compressed Semantic Data Language) communication protocol
used by all 32 agents in the E3 DevMind AI system.

CRITICAL: All inter-agent communication uses pure CSDL.
No natural language translation happens between agents.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import uuid


class MessageType(str, Enum):
    """CSDL message types"""
    QUERY = "query"
    RESPONSE = "response"
    REQUEST = "request"
    NOTIFICATION = "notification"
    ERROR = "error"
    COORDINATION = "coordination"
    SYNTHESIS = "synthesis"


class MessagePriority(str, Enum):
    """Message priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class CSDLMessage(BaseModel):
    """
    CSDL Protocol Message Format

    All inter-agent communication uses this format.
    Content is always in CSDL (compressed semantic format).

    IMPORTANT: This is the core communication primitive for all 32 agents.
    """
    model_config = ConfigDict(use_enum_values=True)

    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    message_type: MessageType = MessageType.QUERY
    sender_id: Optional[str] = None
    recipient_id: Optional[str] = None
    content: Dict[str, Any]  # CSDL-formatted content
    priority: MessagePriority = MessagePriority.NORMAL
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    correlation_id: Optional[str] = None  # For tracking related messages
    in_response_to: Optional[str] = None  # Original message ID

    def __str__(self) -> str:
        return (
            f"CSDLMessage({self.message_type}, "
            f"{self.sender_id or 'unknown'} -> {self.recipient_id or 'broadcast'})"
        )


class CSDLProtocol:
    """
    CSDL communication protocol

    Defines how agents communicate in pure CSDL.
    No natural language translation in agent-to-agent communication.

    Key principles:
    1. All content is CSDL-formatted (compressed semantic structures)
    2. Messages are strongly typed
    3. Supports request-response patterns
    4. Enables async coordination
    5. Maintains message lineage
    """

    @staticmethod
    def create_query(
        content_csdl: Dict[str, Any],
        sender_id: str,
        recipient_id: Optional[str] = None,
        priority: MessagePriority = MessagePriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None
    ) -> CSDLMessage:
        """
        Create CSDL query message

        Args:
            content_csdl: CSDL-formatted query content
            sender_id: Agent ID sending the query
            recipient_id: Target agent ID (None for broadcast)
            priority: Message priority
            metadata: Additional metadata

        Returns:
            CSDLMessage query
        """
        return CSDLMessage(
            message_type=MessageType.QUERY,
            sender_id=sender_id,
            recipient_id=recipient_id,
            content=content_csdl,
            priority=priority,
            metadata=metadata or {}
        )

    @staticmethod
    def create_response(
        content_csdl: Dict[str, Any],
        sender_id: str,
        in_response_to: str,
        recipient_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> CSDLMessage:
        """
        Create CSDL response message

        Args:
            content_csdl: CSDL-formatted response content
            sender_id: Agent ID sending the response
            in_response_to: Original message ID
            recipient_id: Target agent ID
            metadata: Additional metadata

        Returns:
            CSDLMessage response
        """
        return CSDLMessage(
            message_type=MessageType.RESPONSE,
            sender_id=sender_id,
            recipient_id=recipient_id,
            content=content_csdl,
            in_response_to=in_response_to,
            metadata=metadata or {}
        )

    @staticmethod
    def create_request(
        content_csdl: Dict[str, Any],
        sender_id: str,
        recipient_id: str,
        priority: MessagePriority = MessagePriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None
    ) -> CSDLMessage:
        """
        Create CSDL request message (requires response)

        Args:
            content_csdl: CSDL-formatted request content
            sender_id: Agent ID sending the request
            recipient_id: Target agent ID
            priority: Message priority
            metadata: Additional metadata

        Returns:
            CSDLMessage request
        """
        return CSDLMessage(
            message_type=MessageType.REQUEST,
            sender_id=sender_id,
            recipient_id=recipient_id,
            content=content_csdl,
            priority=priority,
            metadata=metadata or {}
        )

    @staticmethod
    def create_notification(
        content_csdl: Dict[str, Any],
        sender_id: str,
        recipient_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> CSDLMessage:
        """
        Create CSDL notification message (no response expected)

        Args:
            content_csdl: CSDL-formatted notification content
            sender_id: Agent ID sending the notification
            recipient_id: Target agent ID (None for broadcast)
            metadata: Additional metadata

        Returns:
            CSDLMessage notification
        """
        return CSDLMessage(
            message_type=MessageType.NOTIFICATION,
            sender_id=sender_id,
            recipient_id=recipient_id,
            content=content_csdl,
            metadata=metadata or {}
        )

    @staticmethod
    def create_error(
        error_csdl: Dict[str, Any],
        sender_id: str,
        in_response_to: Optional[str] = None,
        recipient_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> CSDLMessage:
        """
        Create CSDL error message

        Args:
            error_csdl: CSDL-formatted error details
            sender_id: Agent ID reporting the error
            in_response_to: Original message ID that caused error
            recipient_id: Target agent ID
            metadata: Additional metadata

        Returns:
            CSDLMessage error
        """
        return CSDLMessage(
            message_type=MessageType.ERROR,
            sender_id=sender_id,
            recipient_id=recipient_id,
            content=error_csdl,
            in_response_to=in_response_to,
            priority=MessagePriority.HIGH,
            metadata=metadata or {}
        )

    @staticmethod
    def create_coordination(
        content_csdl: Dict[str, Any],
        sender_id: str,
        recipient_ids: List[str],
        correlation_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[CSDLMessage]:
        """
        Create coordination messages for multi-agent orchestration

        Args:
            content_csdl: CSDL-formatted coordination content
            sender_id: Agent ID coordinating
            recipient_ids: List of target agent IDs
            correlation_id: ID to correlate all related messages
            metadata: Additional metadata

        Returns:
            List of CSDLMessage coordination messages
        """
        messages = []
        for recipient_id in recipient_ids:
            msg = CSDLMessage(
                message_type=MessageType.COORDINATION,
                sender_id=sender_id,
                recipient_id=recipient_id,
                content=content_csdl,
                correlation_id=correlation_id,
                metadata=metadata or {}
            )
            messages.append(msg)
        return messages

    @staticmethod
    def validate_csdl_format(content: Dict[str, Any]) -> bool:
        """
        Validate that content is in proper CSDL format

        CSDL format requirements:
        - Dictionary structure
        - Semantic compression applied
        - No redundant natural language
        - Contains semantic primitives

        Args:
            content: Content to validate

        Returns:
            True if valid CSDL format
        """
        # Basic validation
        if not isinstance(content, dict):
            return False

        # CSDL should have semantic structure
        # This is a simplified validation - real CSDL validation
        # would check for proper semantic compression markers

        # Check for common CSDL keys (from ANLT)
        # In production, this would validate against CSDL schema
        return True  # Simplified for now

    @staticmethod
    def extract_intent(message: CSDLMessage) -> str:
        """
        Extract semantic intent from CSDL message

        Args:
            message: CSDL message

        Returns:
            Intent string
        """
        content = message.content

        # Extract intent from CSDL structure
        # Common intent patterns in CSDL
        if "intent" in content:
            return content["intent"]
        elif "task" in content:
            return content["task"]
        elif "action" in content:
            return content["action"]
        elif "query" in content:
            return "query"
        else:
            return "unknown"

    @staticmethod
    def get_message_chain(
        messages: List[CSDLMessage],
        initial_message_id: str
    ) -> List[CSDLMessage]:
        """
        Get chain of related messages (request-response pairs)

        Args:
            messages: List of all messages
            initial_message_id: Starting message ID

        Returns:
            Ordered list of related messages
        """
        chain = []
        message_map = {msg.message_id: msg for msg in messages}

        # Find initial message
        if initial_message_id not in message_map:
            return chain

        current = message_map[initial_message_id]
        chain.append(current)

        # Follow the chain
        while True:
            # Find responses to current message
            responses = [
                msg for msg in messages
                if msg.in_response_to == current.message_id
            ]

            if not responses:
                break

            # Add first response and continue
            current = responses[0]
            chain.append(current)

        return chain


class CSDLSemanticStructure:
    """
    Helper class for constructing CSDL semantic structures

    Provides utilities for building well-formed CSDL content
    """

    @staticmethod
    def create_task(
        task_type: str,
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create CSDL task structure"""
        return {
            "semantic_type": "task",
            "task_type": task_type,
            "parameters": parameters,
            "context": context or {}
        }

    @staticmethod
    def create_query(
        query_type: str,
        target: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create CSDL query structure"""
        return {
            "semantic_type": "query",
            "query_type": query_type,
            "target": target,
            "filters": filters or {},
            "limit": limit
        }

    @staticmethod
    def create_analysis_request(
        analysis_type: str,
        subject: Dict[str, Any],
        aspects: List[str],
        depth: str = "standard"
    ) -> Dict[str, Any]:
        """Create CSDL analysis request structure"""
        return {
            "semantic_type": "analysis_request",
            "analysis_type": analysis_type,
            "subject": subject,
            "aspects": aspects,
            "depth": depth
        }

    @staticmethod
    def create_result(
        result_type: str,
        data: Dict[str, Any],
        confidence: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create CSDL result structure"""
        return {
            "semantic_type": "result",
            "result_type": result_type,
            "data": data,
            "confidence": confidence,
            "metadata": metadata or {}
        }

    @staticmethod
    def create_error_structure(
        error_type: str,
        description: str,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create CSDL error structure"""
        return {
            "semantic_type": "error",
            "error_type": error_type,
            "description": description,
            "details": details or {}
        }
