"""
E3 DevMind AG-UI Server - Full 32-Agent Swarm
==============================================
Exposes E3 DevMind 32-agent cognitive swarm via AG-UI protocol for CopilotKit integration.
Uses CSDL-14B as the underlying LLM with full swarm coordination.

Architecture:
    Human Input → Oracle → [32-Agent Swarm via CSDL Bus] → Oracle (synthesis) → Human Output
"""

import os
import sys
import json
import asyncio
from typing import Literal, Dict, Any, List, Optional
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', '.env'))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.types import Command
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from copilotkit import CopilotKitState, LangGraphAGUIAgent
from ag_ui_langgraph import add_langgraph_fastapi_endpoint
from langchain_openai import ChatOpenAI

# Import swarm manager
from agents.swarm_manager import swarm, initialize_swarm, query_swarm, SwarmEvent, set_event_callback
from devmind_core.config import AgentRegistryConfig, get_agent_config

# Storage for recent swarm events (for visibility)
recent_swarm_events: List[Dict[str, Any]] = []
MAX_EVENTS = 100


def capture_swarm_event(event: SwarmEvent):
    """Callback to capture swarm events for UI visibility."""
    event_dict = {
        "event_type": event.event_type,
        "agent_id": event.agent_id,
        "agent_name": event.agent_name,
        "message": event.message,
        "data": event.data,
        "timestamp": event.timestamp
    }
    recent_swarm_events.append(event_dict)
    # Keep only recent events
    if len(recent_swarm_events) > MAX_EVENTS:
        recent_swarm_events.pop(0)
    # Log for terminal visibility
    print(f"[SWARM] {event.event_type.upper()}: {event.agent_name or 'Oracle'} - {event.message}")

# Import ANLT translator
try:
    from anlt.translator import ANLTTranslator, CSDL
    ANLT_AVAILABLE = True
    anlt = ANLTTranslator()
except ImportError:
    ANLT_AVAILABLE = False
    anlt = None
    print("Warning: ANLT translator not available")


class E3DevMindState(CopilotKitState):
    """
    E3 DevMind Agent State
    Extends CopilotKitState with E3-specific fields for swarm coordination
    """
    project_context: str = ""
    active_agents: list[str] = []
    task_queue: list[dict] = []
    csdl_context: dict = {}
    agents_involved: list[str] = []
    routing_decision: dict = {}


# =============================================================================
# CSDL-Aware Tools - Route through actual swarm agents
# =============================================================================

@tool
async def search_codebase(query: str, file_pattern: str = "*") -> str:
    """
    Search the E3 codebase for relevant code snippets.
    Routes through Librarian (#22) and Oracle KB (#26) agents.

    Args:
        query: Search query for code content
        file_pattern: Optional glob pattern to filter files
    """
    result = await query_swarm(f"Search codebase for: {query} (pattern: {file_pattern})")
    return json.dumps({
        "status": "success",
        "query": query,
        "pattern": file_pattern,
        "agents_involved": result.get("agents_involved", []),
        "response": result.get("response", "")
    })


@tool
async def analyze_code(file_path: str) -> str:
    """
    Analyze a specific code file for structure, dependencies, and issues.
    Routes through Investigator (#6), Craftsman (#14), and Critic (#7) agents.

    Args:
        file_path: Path to the file to analyze
    """
    result = await query_swarm(f"Analyze code file: {file_path}")
    return json.dumps({
        "status": "success",
        "file": file_path,
        "agents_involved": result.get("agents_involved", []),
        "analysis": result.get("response", "")
    })


@tool
async def generate_code(description: str, language: str = "python") -> str:
    """
    Generate code based on a description.
    Routes through Architect (#12) and Forge (#13) agents.

    Args:
        description: Description of what the code should do
        language: Programming language
    """
    result = await query_swarm(f"Generate {language} code for: {description}")
    return json.dumps({
        "status": "success",
        "language": language,
        "description": description,
        "agents_involved": result.get("agents_involved", []),
        "code": result.get("response", "")
    })


@tool
async def run_tests(test_path: str = "") -> str:
    """
    Run tests for the E3 project.
    Routes through Scientist (#15) agent.

    Args:
        test_path: Optional specific test file or directory
    """
    result = await query_swarm(f"Run tests: {test_path or 'all tests'}")
    return json.dumps({
        "status": "success",
        "path": test_path or "all tests",
        "agents_involved": result.get("agents_involved", []),
        "results": result.get("response", "")
    })


@tool
async def project_management(action: str, details: str = "") -> str:
    """
    Project management operations.
    Routes through Conductor (#28), Tracker (#29), and Prioritizer (#30) agents.

    Args:
        action: Action type (plan_sprint, track_progress, prioritize_tasks)
        details: Additional details
    """
    result = await query_swarm(f"Project management action '{action}': {details}")
    return json.dumps({
        "status": "success",
        "action": action,
        "details": details,
        "agents_involved": result.get("agents_involved", []),
        "result": result.get("response", "")
    })


@tool
async def security_analysis(target: str, analysis_type: str = "general") -> str:
    """
    Security analysis and threat detection.
    Routes through Sentinel (#16) and Guardian (#21) agents.

    Args:
        target: Target to analyze
        analysis_type: Type of analysis
    """
    result = await query_swarm(f"Security analysis of {target}: {analysis_type}")
    return json.dumps({
        "status": "success",
        "target": target,
        "type": analysis_type,
        "agents_involved": result.get("agents_involved", []),
        "analysis": result.get("response", "")
    })


@tool
async def predictive_analysis(topic: str, timeframe: str = "near-term") -> str:
    """
    Predictive analytics and risk forecasting.
    Routes through Prophet (#2) and Strategist (#4) agents.

    Args:
        topic: Topic to analyze
        timeframe: Prediction timeframe
    """
    result = await query_swarm(f"Predict {topic} for {timeframe}")
    return json.dumps({
        "status": "success",
        "topic": topic,
        "timeframe": timeframe,
        "agents_involved": result.get("agents_involved", []),
        "prediction": result.get("response", "")
    })


@tool
async def knowledge_query(query: str) -> str:
    """
    Query the E3 knowledge base.
    Routes through Oracle KB (#26), Librarian (#22), and Scholar (#24) agents.

    Args:
        query: Question or topic to search
    """
    result = await query_swarm(f"Knowledge query: {query}")
    return json.dumps({
        "status": "success",
        "query": query,
        "agents_involved": result.get("agents_involved", []),
        "answer": result.get("response", "")
    })


tools = [
    search_codebase,
    analyze_code,
    generate_code,
    run_tests,
    project_management,
    security_analysis,
    predictive_analysis,
    knowledge_query,
]


def build_oracle_context(state: E3DevMindState) -> str:
    """Build Oracle's system context for swarm coordination."""
    return """You are **Oracle**, the primary coordinator of E3 DevMind's 32-agent cognitive swarm.

**Your 32-Agent Swarm (by Tier):**

TIER 1 - COMMAND:
  - Oracle (you): Primary coordinator, routes queries, synthesizes responses

TIER 2 - STRATEGIC INTELLIGENCE:
  - Prophet (#2): Predictive analytics, risk prediction
  - Sage (#3): Meta-reasoning, process analysis
  - Strategist (#4): Solution design, strategic planning
  - Economist (#5): Resource optimization, ROI analysis

TIER 3 - DEEP ANALYSIS:
  - Investigator (#6): Technical analysis, problem decomposition
  - Critic (#7): Devil's advocate, quality assurance
  - Visionary (#8): Innovation, creative solutions
  - Detective (#9): Pattern recognition, correlation analysis
  - Historian (#10): Institutional memory, context
  - Cartographer (#11): Knowledge mapping, structure optimization

TIER 4 - EXECUTION SPECIALISTS:
  - Architect (#12): System design, architecture
  - Forge (#13): Code generation, implementation
  - Craftsman (#14): Code quality, review
  - Scientist (#15): Testing strategy, validation
  - Sentinel (#16): Security guardian, threat detection
  - Ops (#17): DevOps, infrastructure
  - Optimizer (#18): Performance engineering
  - Documenter (#19): Documentation, knowledge capture
  - Integrator (#20): Systems integration, API design
  - Guardian (#21): Reliability engineering, resilience

TIER 5 - KNOWLEDGE MASTERY:
  - Librarian (#22): Document processing, ingestion
  - Curator (#23): Knowledge organization
  - Scholar (#24): Deep research, external intelligence
  - Synthesizer (#25): Insight generation, multi-source synthesis
  - Oracle KB (#26): Knowledge base queries, instant answers
  - Learner (#27): Continuous improvement

TIER 6 - PROJECT MANAGEMENT:
  - Conductor (#28): Project orchestration
  - Tracker (#29): Progress monitoring
  - Prioritizer (#30): Task optimization

TIER 7 - MARKET & GROWTH:
  - Navigator (#31): Market intelligence, competitive analysis
  - Catalyst (#32): Growth strategy, expansion

**Your Role:**
1. Analyze incoming queries and route to appropriate agents
2. Coordinate multi-agent responses (parallel or sequential)
3. Synthesize agent outputs into unified, actionable responses
4. Always state which agents contributed to the response

**Response Format:**
- Begin with which agents you've consulted
- Synthesize their collective expertise
- Provide specific, actionable guidance
- Highlight risks or considerations

**CSDL Protocol:**
- All inter-agent communication uses CSDL for 70-90% token reduction
- You translate between human language and CSDL at the system edges"""


async def e3_chat_node(state: E3DevMindState, config: RunnableConfig) -> Command[Literal["tool_node", "__end__"]]:
    """
    E3 DevMind main chat node - Oracle orchestrates the full 32-agent swarm.
    """
    # Get the latest user message
    user_messages = [m for m in state["messages"] if isinstance(m, HumanMessage)]
    latest_query = user_messages[-1].content if user_messages else ""

    # Query the full swarm via Oracle
    try:
        swarm_result = await query_swarm(latest_query)
        agents_involved = swarm_result.get("agents_involved", [])
        routing = swarm_result.get("routing", {})
        swarm_response = swarm_result.get("response", "")
    except Exception as e:
        print(f"Swarm query error: {e}")
        agents_involved = []
        routing = {}
        swarm_response = None

    # Use CSDL-14B server for final response
    csdl_url = os.getenv("CSDL_SERVER_URL", "http://localhost:5000")

    # Enable streaming for real-time response delivery
    model = ChatOpenAI(
        model="csdl-14b",
        openai_api_base=f"{csdl_url}/v1",
        openai_api_key="not-needed",
        temperature=0.7,
        streaming=True,  # Enable streaming
        max_tokens=2048,
    )

    # Bind tools
    model_with_tools = model.bind_tools(
        [*state["copilotkit"]["actions"], *tools],
        parallel_tool_calls=False,
    )

    # Build context with swarm response
    system_context = build_oracle_context(state)

    if swarm_response:
        # Include swarm response in context
        agent_names = [get_agent_config(aid).get("agent_name", aid) if get_agent_config(aid) else aid
                      for aid in agents_involved]
        system_context += f"""

**Swarm Analysis Complete:**
Agents consulted: {', '.join(agent_names)}
Routing: {routing.get('reasoning', 'Standard routing')}

**Agent Synthesis:**
{swarm_response}

Use this swarm synthesis to inform your response. Reference which agents contributed."""

    system_message = SystemMessage(content=system_context)

    # Get response
    response = await model_with_tools.ainvoke([
        system_message,
        *state["messages"],
    ], config)

    # Handle tool calls
    if isinstance(response, AIMessage) and response.tool_calls:
        actions = state["copilotkit"]["actions"]
        if not any(action.get("name") == response.tool_calls[0].get("name") for action in actions):
            return Command(
                goto="tool_node",
                update={
                    "messages": response,
                    "active_agents": [get_agent_config(aid).get("agent_name", aid) if get_agent_config(aid) else aid
                                     for aid in agents_involved],
                    "agents_involved": agents_involved,
                    "routing_decision": routing,
                }
            )

    return Command(
        goto=END,
        update={
            "messages": response,
            "active_agents": [get_agent_config(aid).get("agent_name", aid) if get_agent_config(aid) else aid
                             for aid in agents_involved],
            "agents_involved": agents_involved,
            "routing_decision": routing,
        }
    )


# Build the workflow graph
workflow = StateGraph(E3DevMindState)
workflow.add_node("chat_node", e3_chat_node)
workflow.add_node("tool_node", ToolNode(tools=tools))
workflow.add_edge("tool_node", "chat_node")
workflow.set_entry_point("chat_node")

memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)


# Lifespan for swarm initialization
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize swarm on startup, cleanup on shutdown."""
    print("=" * 60)
    print("Initializing E3 DevMind 32-Agent Swarm...")
    print("=" * 60)

    # Register event callback for visibility
    set_event_callback(capture_swarm_event)
    print("Swarm event callback registered for UI visibility")

    await initialize_swarm()
    stats = swarm.get_stats()
    print(f"Swarm initialized: {stats['total_agents']} agents ready")
    print(f"Agents by tier: {stats['agents_by_tier']}")
    print("=" * 60)
    yield
    print("Shutting down swarm...")
    set_event_callback(None)
    await swarm.shutdown()


# Create FastAPI app with lifespan
app = FastAPI(
    title="E3 DevMind AG-UI Server",
    description="AG-UI protocol server for E3 DevMind 32-agent cognitive swarm",
    version="3.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AG-UI endpoint
add_langgraph_fastapi_endpoint(
    app=app,
    agent=LangGraphAGUIAgent(
        name="e3_devmind",
        description="E3 DevMind - Full 32-agent cognitive swarm powered by CSDL-14B",
        graph=graph,
    ),
    path="/",
)


@app.get("/health")
async def health():
    """Health check with swarm status."""
    stats = swarm.get_stats()
    return {
        "status": "ok",
        "agent": "e3_devmind",
        "model": "csdl-14b",
        "swarm_size": stats["total_agents"],
        "swarm_initialized": stats["initialized"],
        "anlt_available": ANLT_AVAILABLE,
        "message_bus": stats["message_bus_stats"],
    }


@app.post("/info")
@app.get("/info")
async def info():
    """CopilotKit info endpoint with full agent registry."""
    agents_by_tier = {}
    for agent in AgentRegistryConfig.AGENTS:
        tier = agent["tier"]
        if tier not in agents_by_tier:
            agents_by_tier[tier] = []
        agents_by_tier[tier].append({
            "id": agent["agent_id"],
            "name": agent["agent_name"],
            "role": agent["role"],
            "description": agent["description"],
            "capabilities": agent["capabilities"]
        })

    return {
        "sdkVersion": "0.1.74",
        "swarmSize": 32,
        "protocol": "CSDL",
        "agentsByTier": agents_by_tier,
        "tierDescriptions": {
            1: "Command & Coordination",
            2: "Strategic Intelligence",
            3: "Deep Analysis",
            4: "Execution Specialists",
            5: "Knowledge Mastery",
            6: "Project Management",
            7: "Market & Growth"
        },
        "agents": [{"name": "e3_devmind", "description": "E3 DevMind - 32-agent cognitive swarm"}]
    }


@app.get("/agents")
async def list_agents():
    """List all 32 agents with their status."""
    stats = swarm.get_stats()
    return {
        "total": 32,
        "initialized": stats["initialized"],
        "agents": AgentRegistryConfig.AGENTS,
        "by_tier": stats["agents_by_tier"]
    }


@app.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get details for a specific agent."""
    agent = get_agent_config(agent_id)
    if agent:
        swarm_agent = swarm.get_agent(agent_id)
        return {
            **agent,
            "active": swarm_agent is not None
        }
    return {"error": f"Agent '{agent_id}' not found"}


@app.get("/swarm/stats")
async def swarm_stats():
    """Get detailed swarm statistics."""
    return swarm.get_stats()


@app.post("/swarm/query")
async def direct_swarm_query(query: str):
    """Direct query to the swarm (bypasses AG-UI)."""
    result = await query_swarm(query)
    return result


@app.get("/swarm/events")
async def get_swarm_events(limit: int = 50):
    """Get recent swarm events for visibility into agent activity."""
    return {
        "events": recent_swarm_events[-limit:],
        "total": len(recent_swarm_events)
    }


@app.get("/swarm/events/stream")
async def stream_swarm_events():
    """SSE endpoint for real-time swarm event streaming."""
    from fastapi.responses import StreamingResponse
    import time

    async def event_generator():
        """Generate SSE events for swarm activity."""
        last_event_count = len(recent_swarm_events)

        # Send initial connection event
        yield f"data: {json.dumps({'type': 'connected', 'message': 'Connected to E3 DevMind swarm event stream'})}\n\n"

        while True:
            current_count = len(recent_swarm_events)
            if current_count > last_event_count:
                # New events available
                new_events = recent_swarm_events[last_event_count:]
                for event in new_events:
                    yield f"data: {json.dumps(event)}\n\n"
                last_event_count = current_count

            # Send heartbeat every 5 seconds
            yield f": heartbeat {int(time.time())}\n\n"
            await asyncio.sleep(0.5)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.delete("/swarm/events")
async def clear_swarm_events():
    """Clear the swarm events log."""
    global recent_swarm_events
    recent_swarm_events = []
    return {"status": "cleared"}


def main():
    """Run the E3 DevMind AG-UI server with full 32-agent swarm."""
    port = int(os.getenv("E3_AGUI_PORT", "8100"))
    print(f"=" * 60)
    print(f"E3 DevMind AG-UI Server v3.0 - Full 32-Agent Swarm")
    print(f"=" * 60)
    print(f"Port: {port}")
    print(f"CSDL Server: {os.getenv('CSDL_SERVER_URL', 'http://localhost:5000')}")
    print(f"ANLT Available: {ANLT_AVAILABLE}")
    print(f"=" * 60)
    uvicorn.run(
        "agents.agui_server:app",
        host="0.0.0.0",
        port=port,
        reload=True,
    )


if __name__ == "__main__":
    main()
