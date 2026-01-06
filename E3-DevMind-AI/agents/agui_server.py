"""
E3 DevMind AG-UI Server
Exposes E3 DevMind agents via AG-UI protocol for CopilotKit integration.
Uses CSDL-14B as the underlying LLM.
"""

import os
import sys
from typing import Literal
from dotenv import load_dotenv

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

# Import CSDL integration
from langchain_openai import ChatOpenAI


class E3DevMindState(CopilotKitState):
    """
    E3 DevMind Agent State
    Extends CopilotKitState with E3-specific fields
    """
    project_context: str = ""
    active_agents: list[str] = []
    task_queue: list[dict] = []


# E3 DevMind Tools
@tool
def search_codebase(query: str, file_pattern: str = "*"):
    """
    Search the E3 codebase for relevant code snippets.
    Args:
        query: Search query for code content
        file_pattern: Optional glob pattern to filter files (e.g., "*.py", "*.ts")
    """
    # This will be enhanced to actually search the codebase
    return f"Searching codebase for '{query}' in files matching '{file_pattern}'..."


@tool
def analyze_code(file_path: str):
    """
    Analyze a specific code file for structure, dependencies, and potential issues.
    Args:
        file_path: Path to the file to analyze
    """
    return f"Analyzing code file: {file_path}"


@tool
def generate_code(description: str, language: str = "python"):
    """
    Generate code based on a description.
    Args:
        description: Description of what the code should do
        language: Programming language (python, typescript, etc.)
    """
    return f"Generating {language} code for: {description}"


@tool
def run_tests(test_path: str = ""):
    """
    Run tests for the E3 project.
    Args:
        test_path: Optional specific test file or directory to run
    """
    return f"Running tests: {test_path or 'all tests'}"


@tool
def query_archon_knowledge(query: str):
    """
    Query the Archon knowledge base for relevant documentation and context.
    Args:
        query: Question or topic to search for in the knowledge base
    """
    # This will integrate with Archon's RAG system
    return f"Querying Archon knowledge base for: {query}"


tools = [
    search_codebase,
    analyze_code,
    generate_code,
    run_tests,
    query_archon_knowledge,
]


async def e3_chat_node(state: E3DevMindState, config: RunnableConfig) -> Command[Literal["tool_node", "__end__"]]:
    """
    E3 DevMind main chat node using CSDL-14B via OpenAI-compatible API.
    """

    # Use CSDL-14B server (Ollama-compatible endpoint)
    csdl_url = os.getenv("CSDL_SERVER_URL", "http://localhost:5000")

    # Create ChatOpenAI instance pointing to CSDL server
    model = ChatOpenAI(
        model="csdl-14b",
        openai_api_base=f"{csdl_url}/v1",
        openai_api_key="not-needed",  # CSDL doesn't require API key
        temperature=0.7,
    )

    # Bind tools to model
    model_with_tools = model.bind_tools(
        [
            *state["copilotkit"]["actions"],
            *tools,
        ],
        parallel_tool_calls=False,
    )

    # E3 DevMind system prompt
    system_message = SystemMessage(
        content="""You are E3 DevMind, an advanced AI development assistant powered by CSDL-14B.

Your capabilities include:
- Analyzing and understanding complex codebases
- Generating high-quality code in multiple languages
- Debugging and troubleshooting issues
- Querying the Archon knowledge base for project documentation
- Coordinating with specialized agents for complex tasks

You are part of the E3 (Emergent Engineering Environment) platform, designed to augment human developers with AI-powered insights and automation.

When responding:
1. Be concise but thorough
2. Provide code examples when relevant
3. Explain your reasoning
4. Suggest improvements proactively
5. Use the available tools to gather information before answering complex questions

Current project context: {project_context}
""".format(project_context=state.get("project_context", "E3 DevMind AI Development Platform"))
    )

    # Get response from model
    response = await model_with_tools.ainvoke([
        system_message,
        *state["messages"],
    ], config)

    # Handle tool calls
    if isinstance(response, AIMessage) and response.tool_calls:
        actions = state["copilotkit"]["actions"]

        # Check for non-CopilotKit actions
        if not any(
            action.get("name") == response.tool_calls[0].get("name")
            for action in actions
        ):
            return Command(goto="tool_node", update={"messages": response})

    return Command(
        goto=END,
        update={"messages": response}
    )


# Build the workflow graph
workflow = StateGraph(E3DevMindState)
workflow.add_node("chat_node", e3_chat_node)
workflow.add_node("tool_node", ToolNode(tools=tools))
workflow.add_edge("tool_node", "chat_node")
workflow.set_entry_point("chat_node")

# Compile with memory checkpointer
memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)


# Create FastAPI app
app = FastAPI(
    title="E3 DevMind AG-UI Server",
    description="AG-UI protocol server for E3 DevMind agents",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add AG-UI endpoint
add_langgraph_fastapi_endpoint(
    app=app,
    agent=LangGraphAGUIAgent(
        name="e3_devmind",
        description="E3 DevMind - AI-powered development assistant using CSDL-14B",
        graph=graph,
    ),
    path="/",
)


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "agent": "e3_devmind", "model": "csdl-14b"}


def main():
    """Run the E3 DevMind AG-UI server"""
    port = int(os.getenv("E3_AGUI_PORT", "8100"))
    print(f"Starting E3 DevMind AG-UI Server on port {port}")
    print(f"CSDL Server URL: {os.getenv('CSDL_SERVER_URL', 'http://localhost:5000')}")
    uvicorn.run(
        "agents.agui_server:app",
        host="0.0.0.0",
        port=port,
        reload=True,
    )


if __name__ == "__main__":
    main()
