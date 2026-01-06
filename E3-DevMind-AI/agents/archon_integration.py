"""
Archon MCP Integration for E3 DevMind Agent Swarm

This module bridges Archon's MCP server capabilities with the E3 DevMind
32-agent swarm, enabling:
- RAG-based knowledge queries across agent ecosystem
- Project and task management for agent workflows
- Document versioning for agent-generated artifacts
- Code example search for agent learning

Integration Pattern:
- Archon MCP Server (HTTP) -> ArchonBridge -> Agent Message Bus -> Agents
- Agents can request Archon capabilities via the collaboration framework

Architecture:
    ┌─────────────────────────────────────────────────────────────────┐
    │                     E3 DevMind Agent Swarm                      │
    │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │
    │  │ Oracle  │ │Architect│ │Craftsman│ │ Sage    │ │Sentinel │   │
    │  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘   │
    │       │           │           │           │           │         │
    │       └───────────┴───────────┴───────────┴───────────┘         │
    │                              │                                   │
    │                    ┌─────────▼─────────┐                        │
    │                    │   ArchonBridge    │                        │
    │                    │  (This Module)    │                        │
    │                    └─────────┬─────────┘                        │
    └──────────────────────────────┼──────────────────────────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │    Archon MCP Server        │
                    │  ┌──────────────────────┐   │
                    │  │ RAG Knowledge Base   │   │
                    │  │ Project Management   │   │
                    │  │ Task Management      │   │
                    │  │ Document Versioning  │   │
                    │  └──────────────────────┘   │
                    └─────────────────────────────┘
"""

import asyncio
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import httpx
import structlog

logger = structlog.get_logger()

# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class ArchonConfig:
    """Configuration for Archon MCP integration"""
    host: str = "localhost"
    server_port: int = 8181       # Main API server
    mcp_port: int = 8051          # MCP server
    agents_port: int = 8052       # Agents server
    timeout_seconds: float = 30.0
    max_retries: int = 3
    retry_delay_seconds: float = 1.0

    @classmethod
    def from_env(cls) -> "ArchonConfig":
        """Load configuration from environment variables"""
        return cls(
            host=os.getenv("ARCHON_HOST", "localhost"),
            server_port=int(os.getenv("ARCHON_SERVER_PORT", "8181")),
            mcp_port=int(os.getenv("ARCHON_MCP_PORT", "8051")),
            agents_port=int(os.getenv("ARCHON_AGENTS_PORT", "8052")),
            timeout_seconds=float(os.getenv("ARCHON_TIMEOUT", "30.0")),
        )

    @property
    def server_url(self) -> str:
        return f"http://{self.host}:{self.server_port}"

    @property
    def mcp_url(self) -> str:
        return f"http://{self.host}:{self.mcp_port}"


# =============================================================================
# MCP TOOL DEFINITIONS (Matches Archon's tools)
# =============================================================================

class ArchonTool(Enum):
    """Available Archon MCP tools"""
    # RAG Tools
    RAG_SEARCH_KNOWLEDGE = "rag_search_knowledge_base"
    RAG_SEARCH_CODE = "rag_search_code_examples"
    RAG_GET_SOURCES = "rag_get_available_sources"
    RAG_LIST_PAGES = "rag_list_pages_for_source"
    RAG_READ_PAGE = "rag_read_full_page"

    # Project Tools
    FIND_PROJECTS = "find_projects"
    MANAGE_PROJECT = "manage_project"

    # Task Tools
    FIND_TASKS = "find_tasks"
    MANAGE_TASK = "manage_task"

    # Document Tools
    FIND_DOCUMENTS = "find_documents"
    MANAGE_DOCUMENT = "manage_document"

    # Version Tools
    FIND_VERSIONS = "find_versions"
    MANAGE_VERSION = "manage_version"

    # System Tools
    HEALTH_CHECK = "health_check"
    SESSION_INFO = "session_info"


@dataclass
class ArchonToolResult:
    """Result from an Archon MCP tool call"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    tool: Optional[ArchonTool] = None
    latency_ms: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# =============================================================================
# ARCHON BRIDGE - Main Integration Class
# =============================================================================

class ArchonBridge:
    """
    Bridge between E3 DevMind agents and Archon MCP server.

    Provides typed methods for all Archon tools with:
    - Automatic retry with exponential backoff
    - Circuit breaker protection
    - Request/response logging
    - CSDL-compatible output format
    """

    def __init__(self, config: Optional[ArchonConfig] = None):
        self.config = config or ArchonConfig.from_env()
        self._client: Optional[httpx.AsyncClient] = None
        self._circuit_open = False
        self._failure_count = 0
        self._last_failure_time: Optional[float] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.config.timeout_seconds),
                limits=httpx.Limits(max_keepalive_connections=5)
            )
        return self._client

    async def close(self):
        """Close HTTP client"""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _call_mcp_tool(
        self,
        tool: ArchonTool,
        params: Dict[str, Any]
    ) -> ArchonToolResult:
        """
        Call an Archon MCP tool with retry logic.

        Args:
            tool: The Archon tool to call
            params: Tool parameters

        Returns:
            ArchonToolResult with success/failure and data
        """
        start_time = datetime.now(timezone.utc)

        # Circuit breaker check
        if self._circuit_open:
            if self._last_failure_time:
                elapsed = (datetime.now(timezone.utc).timestamp() - self._last_failure_time)
                if elapsed < 60:  # 60 second cooldown
                    return ArchonToolResult(
                        success=False,
                        error="Circuit breaker open - Archon service temporarily unavailable",
                        tool=tool
                    )
                else:
                    self._circuit_open = False
                    self._failure_count = 0

        client = await self._get_client()
        last_error = None

        for attempt in range(self.config.max_retries):
            try:
                # Call the Archon API server directly
                # MCP tools are exposed via the server API
                response = await client.post(
                    f"{self.config.server_url}/api/mcp/tools/{tool.value}",
                    json=params,
                    headers={"Content-Type": "application/json"}
                )

                if response.status_code == 200:
                    data = response.json()
                    self._failure_count = 0

                    latency = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000

                    logger.info(
                        "archon_tool_success",
                        tool=tool.value,
                        latency_ms=latency,
                        attempt=attempt + 1
                    )

                    return ArchonToolResult(
                        success=True,
                        data=data,
                        tool=tool,
                        latency_ms=latency
                    )
                else:
                    last_error = f"HTTP {response.status_code}: {response.text}"

            except httpx.TimeoutException as e:
                last_error = f"Timeout: {str(e)}"
            except httpx.ConnectError as e:
                last_error = f"Connection error: {str(e)}"
            except Exception as e:
                last_error = f"Unexpected error: {str(e)}"

            # Exponential backoff
            if attempt < self.config.max_retries - 1:
                delay = self.config.retry_delay_seconds * (2 ** attempt)
                await asyncio.sleep(delay)

        # All retries failed
        self._failure_count += 1
        self._last_failure_time = datetime.now(timezone.utc).timestamp()

        if self._failure_count >= 5:
            self._circuit_open = True
            logger.warning("archon_circuit_breaker_open", failure_count=self._failure_count)

        latency = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000

        logger.error(
            "archon_tool_failed",
            tool=tool.value,
            error=last_error,
            attempts=self.config.max_retries,
            latency_ms=latency
        )

        return ArchonToolResult(
            success=False,
            error=last_error,
            tool=tool,
            latency_ms=latency
        )

    # =========================================================================
    # RAG TOOLS - Knowledge Base Access
    # =========================================================================

    async def search_knowledge(
        self,
        query: str,
        source_id: Optional[str] = None,
        match_count: int = 5
    ) -> ArchonToolResult:
        """
        Search the Archon knowledge base using RAG.

        Args:
            query: Search query (keep short: 2-5 keywords)
            source_id: Optional source filter
            match_count: Number of results to return

        Returns:
            ArchonToolResult with matching documents
        """
        params = {
            "query": query,
            "match_count": match_count
        }
        if source_id:
            params["source_id"] = source_id

        return await self._call_mcp_tool(ArchonTool.RAG_SEARCH_KNOWLEDGE, params)

    async def search_code_examples(
        self,
        query: str,
        source_id: Optional[str] = None,
        match_count: int = 3
    ) -> ArchonToolResult:
        """
        Search for code examples in the knowledge base.

        Args:
            query: Code-related search query
            source_id: Optional source filter
            match_count: Number of results

        Returns:
            ArchonToolResult with code snippets
        """
        params = {
            "query": query,
            "match_count": match_count
        }
        if source_id:
            params["source_id"] = source_id

        return await self._call_mcp_tool(ArchonTool.RAG_SEARCH_CODE, params)

    async def get_available_sources(self) -> ArchonToolResult:
        """
        Get all available knowledge sources.

        Returns:
            ArchonToolResult with list of sources (id, title, url)
        """
        return await self._call_mcp_tool(ArchonTool.RAG_GET_SOURCES, {})

    async def list_pages_for_source(self, source_id: str) -> ArchonToolResult:
        """
        List all pages for a given source.

        Args:
            source_id: The source ID to get pages for

        Returns:
            ArchonToolResult with page list
        """
        return await self._call_mcp_tool(
            ArchonTool.RAG_LIST_PAGES,
            {"source_id": source_id}
        )

    async def read_full_page(
        self,
        page_id: Optional[str] = None,
        url: Optional[str] = None
    ) -> ArchonToolResult:
        """
        Read full content of a specific page.

        Args:
            page_id: Page ID to read
            url: Or page URL

        Returns:
            ArchonToolResult with full page content
        """
        params = {}
        if page_id:
            params["page_id"] = page_id
        if url:
            params["url"] = url

        return await self._call_mcp_tool(ArchonTool.RAG_READ_PAGE, params)

    # =========================================================================
    # PROJECT MANAGEMENT
    # =========================================================================

    async def find_projects(
        self,
        project_id: Optional[str] = None,
        query: Optional[str] = None,
        page: int = 1,
        per_page: int = 10
    ) -> ArchonToolResult:
        """
        Find projects by ID, query, or list all.

        Args:
            project_id: Specific project ID
            query: Search query
            page: Page number
            per_page: Results per page

        Returns:
            ArchonToolResult with project(s)
        """
        params = {"page": page, "per_page": per_page}
        if project_id:
            params["project_id"] = project_id
        if query:
            params["query"] = query

        return await self._call_mcp_tool(ArchonTool.FIND_PROJECTS, params)

    async def create_project(
        self,
        title: str,
        description: Optional[str] = None,
        github_repo: Optional[str] = None
    ) -> ArchonToolResult:
        """Create a new project"""
        params = {
            "action": "create",
            "title": title
        }
        if description:
            params["description"] = description
        if github_repo:
            params["github_repo"] = github_repo

        return await self._call_mcp_tool(ArchonTool.MANAGE_PROJECT, params)

    async def update_project(
        self,
        project_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> ArchonToolResult:
        """Update an existing project"""
        params = {
            "action": "update",
            "project_id": project_id
        }
        if title:
            params["title"] = title
        if description:
            params["description"] = description

        return await self._call_mcp_tool(ArchonTool.MANAGE_PROJECT, params)

    # =========================================================================
    # TASK MANAGEMENT
    # =========================================================================

    async def find_tasks(
        self,
        task_id: Optional[str] = None,
        query: Optional[str] = None,
        filter_by: Optional[str] = None,
        filter_value: Optional[str] = None,
        per_page: int = 10
    ) -> ArchonToolResult:
        """
        Find tasks with various filters.

        Args:
            task_id: Specific task ID
            query: Search query
            filter_by: Filter field (status, project, assignee)
            filter_value: Filter value
            per_page: Results per page

        Returns:
            ArchonToolResult with task(s)
        """
        params = {"per_page": per_page}
        if task_id:
            params["task_id"] = task_id
        if query:
            params["query"] = query
        if filter_by:
            params["filter_by"] = filter_by
        if filter_value:
            params["filter_value"] = filter_value

        return await self._call_mcp_tool(ArchonTool.FIND_TASKS, params)

    async def create_task(
        self,
        project_id: str,
        title: str,
        description: Optional[str] = None,
        status: str = "todo",
        assignee: str = "AI IDE Agent"
    ) -> ArchonToolResult:
        """
        Create a new task.

        Args:
            project_id: Project to add task to
            title: Task title
            description: Task description
            status: Initial status (todo, doing, review, done)
            assignee: Task assignee (User, Archon, AI IDE Agent)
        """
        params = {
            "action": "create",
            "project_id": project_id,
            "title": title,
            "status": status,
            "assignee": assignee
        }
        if description:
            params["description"] = description

        return await self._call_mcp_tool(ArchonTool.MANAGE_TASK, params)

    async def update_task(
        self,
        task_id: str,
        status: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> ArchonToolResult:
        """Update task status or details"""
        params = {
            "action": "update",
            "task_id": task_id
        }
        if status:
            params["status"] = status
        if title:
            params["title"] = title
        if description:
            params["description"] = description

        return await self._call_mcp_tool(ArchonTool.MANAGE_TASK, params)

    # =========================================================================
    # DOCUMENT MANAGEMENT
    # =========================================================================

    async def find_documents(
        self,
        project_id: str,
        document_id: Optional[str] = None,
        query: Optional[str] = None,
        document_type: Optional[str] = None,
        per_page: int = 10
    ) -> ArchonToolResult:
        """Find documents in a project"""
        params = {
            "project_id": project_id,
            "per_page": per_page
        }
        if document_id:
            params["document_id"] = document_id
        if query:
            params["query"] = query
        if document_type:
            params["document_type"] = document_type

        return await self._call_mcp_tool(ArchonTool.FIND_DOCUMENTS, params)

    async def create_document(
        self,
        project_id: str,
        title: str,
        document_type: str,
        content: str
    ) -> ArchonToolResult:
        """Create a new document"""
        params = {
            "action": "create",
            "project_id": project_id,
            "title": title,
            "document_type": document_type,
            "content": content
        }
        return await self._call_mcp_tool(ArchonTool.MANAGE_DOCUMENT, params)

    # =========================================================================
    # HEALTH & STATUS
    # =========================================================================

    async def health_check(self) -> ArchonToolResult:
        """Check Archon service health"""
        return await self._call_mcp_tool(ArchonTool.HEALTH_CHECK, {})

    async def session_info(self) -> ArchonToolResult:
        """Get Archon session information"""
        return await self._call_mcp_tool(ArchonTool.SESSION_INFO, {})


# =============================================================================
# E3 DEVMIND AGENT CAPABILITY REGISTRATION
# =============================================================================

# Capability definitions for agent collaboration framework
ARCHON_CAPABILITIES = {
    "knowledge_search": {
        "name": "archon_knowledge_search",
        "version": "1.0.0",
        "description": "Search Archon knowledge base using RAG",
        "input_schema": {
            "query": "string",
            "source_id": "string (optional)",
            "match_count": "integer"
        },
        "output_schema": {
            "results": "array of documents"
        },
        "success_rate": 0.95,
        "avg_latency_ms": 500
    },
    "code_search": {
        "name": "archon_code_search",
        "version": "1.0.0",
        "description": "Search for code examples in knowledge base",
        "input_schema": {
            "query": "string",
            "source_id": "string (optional)"
        },
        "output_schema": {
            "code_examples": "array"
        },
        "success_rate": 0.93,
        "avg_latency_ms": 600
    },
    "task_management": {
        "name": "archon_task_management",
        "version": "1.0.0",
        "description": "Create and manage tasks in Archon",
        "input_schema": {
            "action": "string (create|update|delete)",
            "task_id": "string (optional)",
            "title": "string",
            "status": "string"
        },
        "output_schema": {
            "task": "object"
        },
        "success_rate": 0.98,
        "avg_latency_ms": 200
    },
    "project_management": {
        "name": "archon_project_management",
        "version": "1.0.0",
        "description": "Manage projects in Archon",
        "input_schema": {
            "action": "string",
            "project_id": "string (optional)",
            "title": "string"
        },
        "output_schema": {
            "project": "object"
        },
        "success_rate": 0.98,
        "avg_latency_ms": 200
    }
}


# =============================================================================
# SINGLETON BRIDGE INSTANCE
# =============================================================================

_archon_bridge: Optional[ArchonBridge] = None


def get_archon_bridge() -> ArchonBridge:
    """Get or create the global Archon bridge instance"""
    global _archon_bridge
    if _archon_bridge is None:
        _archon_bridge = ArchonBridge()
    return _archon_bridge


async def init_archon_integration():
    """
    Initialize Archon integration for E3 DevMind.

    AUTOMATICALLY called at agent swarm startup to:
    1. Verify Archon connectivity
    2. Register Archon capabilities with discovery service
    3. Create E3 DevMind project in Archon if not exists
    4. Set up initial tasks for tracking agent work

    No manual intervention required - fully automated for 2026!
    """
    bridge = get_archon_bridge()

    # Health check
    health = await bridge.health_check()
    if not health.success:
        logger.warning(
            "archon_not_available",
            error=health.error,
            message="Archon integration disabled - service not available"
        )
        return False

    logger.info(
        "archon_integration_ready",
        health=health.data
    )

    # Check for E3 DevMind project
    projects = await bridge.find_projects(query="E3 DevMind")
    project_id = None

    if projects.success and projects.data:
        existing = projects.data.get("projects", [])
        for p in existing:
            if "E3 DevMind" in p.get("title", ""):
                project_id = p.get("id")
                logger.info("archon_project_found", project_id=project_id)
                break

    # Auto-create E3 DevMind project if not exists
    if not project_id:
        result = await bridge.create_project(
            title="E3 DevMind Agent Swarm",
            description="""32-agent AI development swarm with CSDL compression.

Features:
- CSDL-ANLT compression (85-98% token reduction)
- Circuit breaker and retry patterns
- Capability discovery and intelligent routing
- State-of-the-art agent system contexts

Tiers:
- Tier 7: Conductor (orchestration)
- Tier 6: Oracle (intelligence routing)
- Tier 5: Strategist, Synthesizer, Sage (leadership)
- Tier 4: 27 specialized agents""",
            github_repo="https://github.com/bodhifreeman/E3"
        )
        if result.success:
            project_id = result.data.get("project", {}).get("id")
            logger.info("archon_project_auto_created", project_id=project_id)

            # Auto-create initial tracking task
            await bridge.create_task(
                project_id=project_id,
                title="Agent Swarm Initialized",
                description="E3 DevMind 32-agent swarm started successfully",
                status="done",
                assignee="E3 DevMind Agent"
            )

    return True


# =============================================================================
# AGENT HELPER FUNCTIONS
# =============================================================================

async def agent_search_knowledge(query: str, source_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Helper for agents to search Archon knowledge base.

    Returns CSDL-compatible format for inter-agent communication.
    """
    bridge = get_archon_bridge()
    result = await bridge.search_knowledge(query, source_id)

    return {
        "op": "knowledge_search_result",
        "success": result.success,
        "query": query,
        "results": result.data if result.success else None,
        "error": result.error,
        "latency_ms": result.latency_ms,
        "ts": datetime.now(timezone.utc).isoformat()
    }


async def agent_create_task(
    title: str,
    description: str,
    project_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Helper for agents to create tasks in Archon.

    If no project_id provided, uses E3 DevMind project.
    """
    bridge = get_archon_bridge()

    # Find E3 DevMind project if no project specified
    if not project_id:
        projects = await bridge.find_projects(query="E3 DevMind")
        if projects.success and projects.data:
            project_list = projects.data.get("projects", [])
            if project_list:
                project_id = project_list[0].get("id")

    if not project_id:
        return {
            "op": "task_create_error",
            "error": "No project available",
            "ts": datetime.now(timezone.utc).isoformat()
        }

    result = await bridge.create_task(
        project_id=project_id,
        title=title,
        description=description,
        assignee="E3 DevMind Agent"
    )

    return {
        "op": "task_created",
        "success": result.success,
        "task": result.data if result.success else None,
        "error": result.error,
        "ts": datetime.now(timezone.utc).isoformat()
    }


async def agent_update_task_status(task_id: str, status: str) -> Dict[str, Any]:
    """
    Helper for agents to update task status.

    Status flow: todo -> doing -> review -> done
    """
    bridge = get_archon_bridge()
    result = await bridge.update_task(task_id, status=status)

    return {
        "op": "task_updated",
        "success": result.success,
        "task_id": task_id,
        "new_status": status,
        "error": result.error,
        "ts": datetime.now(timezone.utc).isoformat()
    }
