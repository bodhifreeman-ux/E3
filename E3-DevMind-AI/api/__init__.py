"""
E3 DevMind AI - API Interfaces

REST and WebSocket APIs for E3 DevMind AI.
"""

from api.rest_api import app as rest_app
from api.websocket_api import (
    ConnectionManager,
    manager,
    websocket_endpoint,
    handle_query,
    handle_stream,
    send_system_notifications
)

__all__ = [
    "rest_app",
    "ConnectionManager",
    "manager",
    "websocket_endpoint",
    "handle_query",
    "handle_stream",
    "send_system_notifications",
]
