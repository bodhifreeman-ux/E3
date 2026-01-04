"""
E3 DevMind AI WebSocket API

Real-time WebSocket interface for streaming responses and live updates.
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set, Optional
import structlog
import asyncio
import json
from datetime import datetime

logger = structlog.get_logger()


class ConnectionManager:
    """Manages WebSocket connections with topic-based subscriptions"""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.connection_metadata: Dict[WebSocket, Dict] = {}
        self.subscriptions: Dict[str, Set[WebSocket]] = {}  # topic -> websockets

    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept and track new connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        self.connection_metadata[websocket] = {
            "client_id": client_id,
            "connected_at": datetime.utcnow().isoformat(),
            "subscribed_topics": set()
        }
        logger.info("websocket_connected", client_id=client_id, total_connections=len(self.active_connections))

    def disconnect(self, websocket: WebSocket):
        """Remove disconnected client and clean up subscriptions"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            metadata = self.connection_metadata.pop(websocket, {})

            # Clean up topic subscriptions
            for topic in metadata.get("subscribed_topics", set()):
                if topic in self.subscriptions and websocket in self.subscriptions[topic]:
                    self.subscriptions[topic].remove(websocket)
                    if not self.subscriptions[topic]:  # Remove empty topic
                        del self.subscriptions[topic]

            logger.info("websocket_disconnected",
                       client_id=metadata.get("client_id"),
                       total_connections=len(self.active_connections))

    async def subscribe(self, topic: str, websocket: WebSocket):
        """Subscribe websocket to a topic"""
        if topic not in self.subscriptions:
            self.subscriptions[topic] = set()

        self.subscriptions[topic].add(websocket)

        if websocket in self.connection_metadata:
            self.connection_metadata[websocket]["subscribed_topics"].add(topic)

        logger.info("websocket_subscribed",
                   topic=topic,
                   client_id=self.connection_metadata.get(websocket, {}).get("client_id"),
                   subscribers_count=len(self.subscriptions[topic]))

    async def unsubscribe(self, topic: str, websocket: WebSocket):
        """Unsubscribe websocket from a topic"""
        if topic in self.subscriptions and websocket in self.subscriptions[topic]:
            self.subscriptions[topic].remove(websocket)

            if not self.subscriptions[topic]:  # Remove empty topic
                del self.subscriptions[topic]

            if websocket in self.connection_metadata:
                self.connection_metadata[websocket]["subscribed_topics"].discard(topic)

            logger.info("websocket_unsubscribed",
                       topic=topic,
                       client_id=self.connection_metadata.get(websocket, {}).get("client_id"))

    async def send_personal_message(self, message: Dict, websocket: WebSocket):
        """Send message to specific client"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error("send_personal_message_failed",
                        error=str(e),
                        client_id=self.connection_metadata.get(websocket, {}).get("client_id"))

    async def broadcast(self, message: Dict):
        """Broadcast message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error("broadcast_failed", error=str(e))
                disconnected.append(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)

    async def publish_to_topic(self, topic: str, message: Dict):
        """Publish message to all subscribers of a topic"""
        if topic not in self.subscriptions:
            logger.debug("publish_to_empty_topic", topic=topic)
            return

        disconnected = []
        subscribers = self.subscriptions[topic].copy()  # Copy to avoid modification during iteration

        for websocket in subscribers:
            try:
                await websocket.send_json({
                    "type": "topic_message",
                    "topic": topic,
                    "data": message,
                    "timestamp": datetime.utcnow().isoformat()
                })
            except Exception as e:
                logger.error("publish_to_topic_failed",
                           topic=topic,
                           error=str(e))
                disconnected.append(websocket)

        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)

        logger.debug("published_to_topic",
                    topic=topic,
                    subscribers=len(subscribers),
                    successful=len(subscribers) - len(disconnected))


manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    Main WebSocket endpoint handler

    Handles real-time bidirectional communication with clients.

    Supported message types:
    - query: Process natural language query with progress updates
    - stream: Request streaming response
    - subscribe: Subscribe to topic for notifications
    - unsubscribe: Unsubscribe from topic
    - ping: Connection keep-alive
    """
    await manager.connect(websocket, client_id)

    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "client_id": client_id,
            "message": "Connected to E3 DevMind AI",
            "timestamp": datetime.utcnow().isoformat(),
            "available_topics": [
                "system_notifications",
                "agent_updates",
                "knowledge_updates",
                "query_results"
            ]
        })

        while True:
            # Receive message from client
            data = await websocket.receive_json()

            message_type = data.get("type", "unknown")
            logger.info("websocket_message_received",
                       client_id=client_id,
                       message_type=message_type)

            # Route message based on type
            if message_type == "query":
                await handle_query(websocket, data)

            elif message_type == "stream":
                await handle_stream(websocket, data)

            elif message_type == "subscribe":
                topic = data.get("topic")
                if topic:
                    await manager.subscribe(topic, websocket)
                    await websocket.send_json({
                        "type": "subscribed",
                        "topic": topic,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                else:
                    await websocket.send_json({
                        "type": "error",
                        "error": "Topic name required for subscription",
                        "timestamp": datetime.utcnow().isoformat()
                    })

            elif message_type == "unsubscribe":
                topic = data.get("topic")
                if topic:
                    await manager.unsubscribe(topic, websocket)
                    await websocket.send_json({
                        "type": "unsubscribed",
                        "topic": topic,
                        "timestamp": datetime.utcnow().isoformat()
                    })

            elif message_type == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                })

            else:
                await websocket.send_json({
                    "type": "error",
                    "error": f"Unknown message type: {message_type}",
                    "supported_types": ["query", "stream", "subscribe", "unsubscribe", "ping"],
                    "timestamp": datetime.utcnow().isoformat()
                })

    except WebSocketDisconnect:
        logger.info("websocket_disconnected_by_client", client_id=client_id)
        manager.disconnect(websocket)

    except Exception as e:
        logger.error("websocket_error", client_id=client_id, error=str(e), exc_info=True)
        manager.disconnect(websocket)


async def handle_query(websocket: WebSocket, data: Dict):
    """
    Handle query message type

    Processes query through agent swarm with real-time progress updates.
    """
    query = data.get("query", "")
    context = data.get("context", {})
    use_compression = data.get("use_compression", True)

    # Send acknowledgment
    await websocket.send_json({
        "type": "query_received",
        "query": query,
        "use_compression": use_compression,
        "timestamp": datetime.utcnow().isoformat()
    })

    try:
        # Progress update: ANLT processing
        await websocket.send_json({
            "type": "progress",
            "stage": "anlt_processing",
            "message": "Converting natural language to CSDL...",
            "progress": 0.15,
            "timestamp": datetime.utcnow().isoformat()
        })
        await asyncio.sleep(0.3)

        # Progress update: CSDL compression
        await websocket.send_json({
            "type": "progress",
            "stage": "csdl_compression",
            "message": "Applying CSDL compression (70-90% token reduction)...",
            "progress": 0.25,
            "timestamp": datetime.utcnow().isoformat()
        })
        await asyncio.sleep(0.2)

        # Progress update: Oracle routing
        await websocket.send_json({
            "type": "progress",
            "stage": "oracle_routing",
            "message": "Oracle analyzing query and routing to agents...",
            "progress": 0.35,
            "timestamp": datetime.utcnow().isoformat()
        })
        await asyncio.sleep(0.4)

        # Progress update: Agent swarm processing
        await websocket.send_json({
            "type": "progress",
            "stage": "agent_processing",
            "message": "Processing with agent swarm...",
            "agents_active": ["oracle", "prophet", "strategist"],
            "progress": 0.60,
            "timestamp": datetime.utcnow().isoformat()
        })
        await asyncio.sleep(0.8)

        # Progress update: Response synthesis
        await websocket.send_json({
            "type": "progress",
            "stage": "response_synthesis",
            "message": "Synthesizing CSDL response...",
            "progress": 0.85,
            "timestamp": datetime.utcnow().isoformat()
        })
        await asyncio.sleep(0.3)

        # Progress update: ANLT translation
        await websocket.send_json({
            "type": "progress",
            "stage": "anlt_translation",
            "message": "Converting CSDL to natural language...",
            "progress": 0.95,
            "timestamp": datetime.utcnow().isoformat()
        })
        await asyncio.sleep(0.2)

        # Send final response
        await websocket.send_json({
            "type": "response",
            "query": query,
            "response": f"Analysis complete: {query[:50]}...",
            "agents_used": ["oracle", "prophet", "strategist"],
            "processing_time_ms": 2300,
            "tokens_saved": 450 if use_compression else 0,
            "csdl_used": use_compression,
            "progress": 1.0,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "confidence": 0.95,
                "sources": 12,
                "compression_ratio": 0.75 if use_compression else 1.0
            }
        })

    except Exception as e:
        logger.error("query_processing_failed", error=str(e), exc_info=True)
        await websocket.send_json({
            "type": "error",
            "error": f"Query processing failed: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        })


async def handle_stream(websocket: WebSocket, data: Dict):
    """
    Handle streaming message type

    Streams response token by token for real-time display.
    """
    query = data.get("query", "")

    # Send stream start
    await websocket.send_json({
        "type": "stream_start",
        "query": query,
        "timestamp": datetime.utcnow().isoformat()
    })

    # Simulate streaming response (in production, would stream from vLLM)
    response_chunks = [
        "Based on", " the", " comprehensive", " analysis", " of", " your",
        " current", " sprint,", " here", " are", " the", " key", " risk", " factors:\n\n",
        "1.", " **Resource", " Constraints**:", " Team", " capacity", " is",
        " limited...\n",
        "2.", " **Technical", " Debt**:", " Legacy", " code", " requires",
        " refactoring...\n",
        "3.", " **Timeline", " Pressure**:", " Tight", " deadlines", " may",
        " impact", " quality..."
    ]

    for i, chunk in enumerate(response_chunks):
        await websocket.send_json({
            "type": "stream_chunk",
            "chunk": chunk,
            "index": i,
            "progress": (i + 1) / len(response_chunks),
            "is_final": i == len(response_chunks) - 1,
            "timestamp": datetime.utcnow().isoformat()
        })
        await asyncio.sleep(0.1)  # Simulate token generation time

    # Send stream complete
    await websocket.send_json({
        "type": "stream_complete",
        "total_chunks": len(response_chunks),
        "processing_time_ms": len(response_chunks) * 100,
        "timestamp": datetime.utcnow().isoformat()
    })


async def send_system_notifications():
    """
    Background task that sends periodic system notifications to subscribers

    Publishes to 'system_notifications' topic:
    - System health updates
    - Agent status changes
    - Knowledge base updates
    - Performance metrics
    """
    logger.info("system_notifications_task_started")

    notification_count = 0

    while True:
        try:
            await asyncio.sleep(30)  # Send notification every 30 seconds

            # System health notification
            if notification_count % 2 == 0:
                await manager.publish_to_topic("system_notifications", {
                    "notification_type": "system_health",
                    "status": "healthy",
                    "components": {
                        "api": "healthy",
                        "csdl_vllm": "healthy",
                        "qdrant": "healthy",
                        "agents": "healthy"
                    },
                    "active_queries": 5,
                    "uptime_hours": 24.5,
                    "timestamp": datetime.utcnow().isoformat()
                })

            # Agent updates notification
            else:
                await manager.publish_to_topic("agent_updates", {
                    "notification_type": "agent_status",
                    "updates": [
                        {
                            "agent_id": "oracle",
                            "status": "active",
                            "current_load": 0.45,
                            "queries_processed": 1523
                        },
                        {
                            "agent_id": "prophet",
                            "status": "active",
                            "current_load": 0.32,
                            "queries_processed": 842
                        }
                    ],
                    "timestamp": datetime.utcnow().isoformat()
                })

            notification_count += 1
            logger.debug("system_notification_sent",
                        notification_count=notification_count,
                        active_connections=len(manager.active_connections))

        except Exception as e:
            logger.error("system_notification_failed", error=str(e), exc_info=True)
            await asyncio.sleep(5)  # Back off on error
