"""
CSDL Message Bus

Event-driven message bus for inter-agent communication in pure CSDL.

Features:
- Sub-millisecond agent-to-agent latency
- Zero translation overhead
- Async message routing
- Pub/sub pattern support
- Request-response tracking
"""

import asyncio
from typing import Dict, Any, Optional, List, Callable, Awaitable
from collections import defaultdict
import structlog
from csdl.protocol import CSDLMessage, MessageType, MessagePriority

logger = structlog.get_logger()


MessageHandler = Callable[[CSDLMessage], Awaitable[Optional[CSDLMessage]]]


class CSDLMessageBus:
    """
    CSDL-native message bus for all 32 agents

    All inter-agent communication flows through this bus.
    Messages are pure CSDL - no translation happens here.

    Key features:
    - Async message routing
    - Priority-based delivery
    - Request-response correlation
    - Broadcast support
    - Message history tracking
    """

    def __init__(self):
        """Initialize the CSDL message bus"""
        # Agent handlers: agent_id -> handler function
        self._handlers: Dict[str, MessageHandler] = {}

        # Message queues per agent (priority-based)
        self._queues: Dict[str, asyncio.PriorityQueue] = defaultdict(
            lambda: asyncio.PriorityQueue()
        )

        # Pending requests (for request-response pattern)
        self._pending_requests: Dict[str, asyncio.Future] = {}

        # Message history (for debugging and lineage)
        self._message_history: List[CSDLMessage] = []
        self._max_history_size = 10000

        # Active agent processors
        self._processors: Dict[str, asyncio.Task] = {}

        # Bus running state
        self._running = False

        logger.info("csdl_message_bus_initialized")

    async def start(self):
        """Start the message bus"""
        self._running = True
        logger.info("csdl_message_bus_started")

    async def stop(self):
        """Stop the message bus"""
        self._running = False

        # Cancel all processors
        for processor in self._processors.values():
            processor.cancel()

        self._processors.clear()
        logger.info("csdl_message_bus_stopped")

    def register_agent(
        self,
        agent_id: str,
        handler: MessageHandler
    ):
        """
        Register an agent with the message bus

        Args:
            agent_id: Unique agent identifier
            handler: Async function to handle messages
        """
        self._handlers[agent_id] = handler

        # Start message processor for this agent
        if agent_id not in self._processors and self._running:
            processor = asyncio.create_task(self._process_agent_messages(agent_id))
            self._processors[agent_id] = processor

        logger.info("agent_registered", agent_id=agent_id)

    def unregister_agent(self, agent_id: str):
        """
        Unregister an agent from the message bus

        Args:
            agent_id: Agent identifier to remove
        """
        if agent_id in self._handlers:
            del self._handlers[agent_id]

        if agent_id in self._processors:
            self._processors[agent_id].cancel()
            del self._processors[agent_id]

        logger.info("agent_unregistered", agent_id=agent_id)

    async def send_message(
        self,
        message: CSDLMessage
    ) -> Optional[str]:
        """
        Send a message through the bus

        Args:
            message: CSDL message to send

        Returns:
            Message ID if successful
        """
        if not self._running:
            logger.error("message_bus_not_running")
            return None

        # Add to history
        self._add_to_history(message)

        # Route message
        if message.recipient_id:
            # Direct message to specific agent
            await self._route_to_agent(message.recipient_id, message)
        else:
            # Broadcast to all agents (except sender)
            await self._broadcast(message)

        logger.debug(
            "message_sent",
            message_id=message.message_id,
            sender=message.sender_id,
            recipient=message.recipient_id or "broadcast",
            type=message.message_type
        )

        return message.message_id

    async def send_and_wait(
        self,
        message: CSDLMessage,
        timeout: float = 30.0
    ) -> Optional[CSDLMessage]:
        """
        Send a message and wait for response (request-response pattern)

        Args:
            message: CSDL message to send
            timeout: Timeout in seconds

        Returns:
            Response message or None if timeout
        """
        if message.message_type not in [MessageType.REQUEST, MessageType.QUERY]:
            logger.error(
                "send_and_wait_wrong_type",
                message_type=message.message_type
            )
            return None

        # Create future for response
        response_future: asyncio.Future = asyncio.Future()
        self._pending_requests[message.message_id] = response_future

        # Send message
        await self.send_message(message)

        try:
            # Wait for response with timeout
            response = await asyncio.wait_for(response_future, timeout=timeout)
            return response
        except asyncio.TimeoutError:
            logger.error(
                "request_timeout",
                message_id=message.message_id,
                sender=message.sender_id,
                recipient=message.recipient_id
            )
            return None
        finally:
            # Clean up
            if message.message_id in self._pending_requests:
                del self._pending_requests[message.message_id]

    async def _route_to_agent(
        self,
        agent_id: str,
        message: CSDLMessage
    ):
        """
        Route message to specific agent

        Args:
            agent_id: Target agent ID
            message: Message to route
        """
        if agent_id not in self._handlers:
            logger.error("agent_not_found", agent_id=agent_id)
            return

        # Priority mapping
        priority_map = {
            MessagePriority.URGENT: 0,
            MessagePriority.HIGH: 1,
            MessagePriority.NORMAL: 2,
            MessagePriority.LOW: 3
        }

        priority = priority_map.get(message.priority, 2)

        # Add to agent's queue
        await self._queues[agent_id].put((priority, message))

    async def _broadcast(self, message: CSDLMessage):
        """
        Broadcast message to all agents (except sender)

        Args:
            message: Message to broadcast
        """
        for agent_id in self._handlers.keys():
            if agent_id != message.sender_id:
                await self._route_to_agent(agent_id, message)

    async def _process_agent_messages(self, agent_id: str):
        """
        Process messages for a specific agent

        Args:
            agent_id: Agent to process messages for
        """
        logger.info("agent_processor_started", agent_id=agent_id)

        while self._running:
            try:
                # Get next message (blocks until available)
                priority, message = await asyncio.wait_for(
                    self._queues[agent_id].get(),
                    timeout=1.0
                )

                # Get handler
                handler = self._handlers.get(agent_id)
                if not handler:
                    logger.error("handler_not_found", agent_id=agent_id)
                    continue

                # Process message
                try:
                    response = await handler(message)

                    # If this is a response to a pending request, resolve it
                    if message.in_response_to and message.in_response_to in self._pending_requests:
                        future = self._pending_requests[message.in_response_to]
                        if not future.done():
                            future.set_result(message)

                    # If handler generated a response, send it
                    if response:
                        await self.send_message(response)

                except Exception as e:
                    logger.error(
                        "message_handler_error",
                        agent_id=agent_id,
                        message_id=message.message_id,
                        error=str(e)
                    )

            except asyncio.TimeoutError:
                # No messages in queue, continue
                continue
            except asyncio.CancelledError:
                logger.info("agent_processor_cancelled", agent_id=agent_id)
                break
            except Exception as e:
                logger.error(
                    "agent_processor_error",
                    agent_id=agent_id,
                    error=str(e)
                )

        logger.info("agent_processor_stopped", agent_id=agent_id)

    def _add_to_history(self, message: CSDLMessage):
        """
        Add message to history

        Args:
            message: Message to record
        """
        self._message_history.append(message)

        # Trim history if too large
        if len(self._message_history) > self._max_history_size:
            self._message_history = self._message_history[-self._max_history_size:]

    def get_message_history(
        self,
        agent_id: Optional[str] = None,
        message_type: Optional[MessageType] = None,
        limit: int = 100
    ) -> List[CSDLMessage]:
        """
        Get message history

        Args:
            agent_id: Filter by agent ID (sender or recipient)
            message_type: Filter by message type
            limit: Maximum messages to return

        Returns:
            List of messages
        """
        messages = self._message_history

        # Apply filters
        if agent_id:
            messages = [
                m for m in messages
                if m.sender_id == agent_id or m.recipient_id == agent_id
            ]

        if message_type:
            messages = [m for m in messages if m.message_type == message_type]

        # Return most recent
        return messages[-limit:]

    def get_stats(self) -> Dict[str, Any]:
        """
        Get message bus statistics

        Returns:
            Stats dictionary
        """
        return {
            "running": self._running,
            "registered_agents": len(self._handlers),
            "active_processors": len(self._processors),
            "pending_requests": len(self._pending_requests),
            "message_history_size": len(self._message_history),
            "agents": list(self._handlers.keys())
        }


# Global message bus instance
csdl_bus = CSDLMessageBus()


# Convenience functions

async def send_to_agent(
    target_agent_id: str,
    content: Dict[str, Any],
    sender_id: str,
    message_type: MessageType = MessageType.REQUEST,
    priority: MessagePriority = MessagePriority.NORMAL
) -> Optional[str]:
    """
    Convenience function to send a message to an agent

    Args:
        target_agent_id: Target agent ID
        content: CSDL content
        sender_id: Sender agent ID
        message_type: Type of message
        priority: Message priority

    Returns:
        Message ID
    """
    from csdl.protocol import CSDLProtocol

    if message_type == MessageType.REQUEST:
        message = CSDLProtocol.create_request(
            content_csdl=content,
            sender_id=sender_id,
            recipient_id=target_agent_id,
            priority=priority
        )
    elif message_type == MessageType.QUERY:
        message = CSDLProtocol.create_query(
            content_csdl=content,
            sender_id=sender_id,
            recipient_id=target_agent_id,
            priority=priority
        )
    else:
        message = CSDLMessage(
            message_type=message_type,
            sender_id=sender_id,
            recipient_id=target_agent_id,
            content=content,
            priority=priority
        )

    return await csdl_bus.send_message(message)


async def request_and_wait(
    target_agent_id: str,
    content: Dict[str, Any],
    sender_id: str,
    timeout: float = 30.0
) -> Optional[CSDLMessage]:
    """
    Convenience function to send a request and wait for response

    Args:
        target_agent_id: Target agent ID
        content: CSDL content
        sender_id: Sender agent ID
        timeout: Timeout in seconds

    Returns:
        Response message
    """
    from csdl.protocol import CSDLProtocol

    message = CSDLProtocol.create_request(
        content_csdl=content,
        sender_id=sender_id,
        recipient_id=target_agent_id
    )

    return await csdl_bus.send_and_wait(message, timeout=timeout)
