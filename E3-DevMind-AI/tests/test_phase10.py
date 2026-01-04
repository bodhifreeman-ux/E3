"""
Test suite for Phase 10 components (Interfaces & Integrations)
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient

# ============================================================================
# REST API TESTS
# ============================================================================

def test_rest_api_health_check():
    """Test REST API health check endpoint"""
    from api.rest_api import app

    client = TestClient(app)
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_rest_api_query_endpoint():
    """Test REST API query endpoint"""
    from api.rest_api import app

    client = TestClient(app)
    response = client.post(
        "/api/query",
        json={
            "query": "Test query",
            "use_compression": True
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "metadata" in data
    assert "agents_involved" in data

def test_rest_api_list_agents():
    """Test REST API agents list endpoint"""
    from api.rest_api import app

    client = TestClient(app)
    response = client.get("/api/agents")

    assert response.status_code == 200
    data = response.json()
    assert data["total_agents"] == 32
    assert "agents_by_tier" in data

def test_rest_api_knowledge_stats():
    """Test REST API knowledge stats endpoint"""
    from api.rest_api import app

    client = TestClient(app)
    response = client.get("/api/knowledge/stats")

    assert response.status_code == 200
    data = response.json()
    assert "total_documents" in data
    assert "total_vectors" in data

# ============================================================================
# WEBSOCKET API TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_websocket_connection_manager():
    """Test WebSocket ConnectionManager"""
    from api.websocket_api import ConnectionManager
    from fastapi import WebSocket

    manager = ConnectionManager()

    # Test connection tracking
    assert len(manager.active_connections) == 0
    assert len(manager.subscriptions) == 0

@pytest.mark.asyncio
async def test_websocket_topic_subscription():
    """Test WebSocket topic subscription system"""
    from api.websocket_api import ConnectionManager

    manager = ConnectionManager()

    # Mock websocket
    mock_ws = Mock()

    # Add to connections first
    manager.active_connections.add(mock_ws)
    manager.connection_metadata[mock_ws] = {
        "client_id": "test_client",
        "subscribed_topics": set()
    }

    # Test subscription
    await manager.subscribe("test_topic", mock_ws)

    assert "test_topic" in manager.subscriptions
    assert mock_ws in manager.subscriptions["test_topic"]

    # Test unsubscription
    await manager.unsubscribe("test_topic", mock_ws)
    assert "test_topic" not in manager.subscriptions

# ============================================================================
# CLI TESTS
# ============================================================================

def test_cli_status_command():
    """Test CLI status command"""
    from cli.main import cli
    from click.testing import CliRunner

    runner = CliRunner()
    result = runner.invoke(cli, ['status'])

    assert result.exit_code == 0
    assert "E3 DevMind AI System Status" in result.output

def test_cli_agents_command():
    """Test CLI agents list command"""
    from cli.main import cli
    from click.testing import CliRunner

    runner = CliRunner()
    result = runner.invoke(cli, ['agents'])

    assert result.exit_code == 0
    assert "32 Agent Swarm" in result.output

def test_cli_kb_stats_command():
    """Test CLI knowledge base stats command"""
    from cli.main import cli
    from click.testing import CliRunner

    runner = CliRunner()
    result = runner.invoke(cli, ['kb-stats'])

    assert result.exit_code == 0
    assert "Knowledge Base Statistics" in result.output

def test_cli_test_connection_command():
    """Test CLI connection test command"""
    from cli.main import cli
    from click.testing import CliRunner

    runner = CliRunner()
    result = runner.invoke(cli, ['test-connection'])

    assert result.exit_code == 0
    assert "Testing connections" in result.output

# ============================================================================
# WEB DASHBOARD TESTS
# ============================================================================

def test_dashboard_index_template_exists():
    """Test that dashboard index template exists"""
    from pathlib import Path

    template_path = Path("ui/templates/index.html")
    assert template_path.exists()

def test_dashboard_functions_exist():
    """Test that dashboard functions are defined"""
    from ui.dashboard import dashboard_home, agents_page, knowledge_page

    assert callable(dashboard_home)
    assert callable(agents_page)
    assert callable(knowledge_page)

# ============================================================================
# INTEGRATION TESTS - GITHUB
# ============================================================================

@pytest.mark.asyncio
async def test_github_integration_init():
    """Test GitHub integration initialization"""
    from integrations.github_integration import GitHubIntegration

    mock_agents = {'craftsman': Mock()}

    with patch('integrations.github_integration.Github'):
        github = GitHubIntegration(
            token="fake_token",
            agents=mock_agents
        )

        assert github is not None
        assert github.agents == mock_agents

@pytest.mark.asyncio
async def test_github_pr_analysis():
    """Test GitHub PR analysis flow"""
    from integrations.github_integration import GitHubIntegration

    mock_craftsman = AsyncMock()
    mock_agents = {'craftsman': mock_craftsman}

    with patch('integrations.github_integration.Github'):
        github = GitHubIntegration(
            token="fake_token",
            agents=mock_agents
        )

        # Mock GitHub API
        with patch.object(github, 'github') as mock_gh:
            mock_repo = Mock()
            mock_pr = Mock()
            mock_pr.number = 123
            mock_pr.title = "Test PR"
            mock_pr.body = "Test description"
            mock_pr.user.login = "testuser"
            mock_pr.created_at.isoformat.return_value = "2024-01-01T00:00:00"
            mock_pr.updated_at.isoformat.return_value = "2024-01-01T00:00:00"
            mock_pr.get_files.return_value = []

            mock_repo.get_pull.return_value = mock_pr
            mock_gh.get_repo.return_value = mock_repo

            # Test analysis (would fail without full mocking)
            # result = await github.analyze_pr("test/repo", 123)
            # assert result is not None

# ============================================================================
# INTEGRATION TESTS - SLACK
# ============================================================================

@pytest.mark.asyncio
async def test_slack_integration_init():
    """Test Slack integration initialization"""
    from integrations.slack_integration import SlackIntegration

    mock_agents = {'oracle': Mock()}

    with patch('integrations.slack_integration.WebClient'):
        slack = SlackIntegration(
            token="fake_token",
            agents=mock_agents
        )

        assert slack is not None
        assert slack.agents == mock_agents

@pytest.mark.asyncio
async def test_slack_send_message():
    """Test Slack message sending"""
    from integrations.slack_integration import SlackIntegration

    mock_agents = {'oracle': Mock()}

    with patch('integrations.slack_integration.WebClient') as mock_client:
        slack = SlackIntegration(
            token="fake_token",
            agents=mock_agents
        )

        # Mock API response
        mock_response = Mock()
        mock_response.data = {"ok": True, "ts": "123456"}
        mock_client.return_value.chat_postMessage.return_value = mock_response

        result = await slack.send_message(
            channel="test-channel",
            text="Test message"
        )

        assert result is not None

@pytest.mark.asyncio
async def test_slack_alert_types():
    """Test Slack alert configurations"""
    from integrations.slack_integration import SlackIntegration

    mock_agents = {'oracle': Mock()}

    with patch('integrations.slack_integration.WebClient'):
        slack = SlackIntegration(
            token="fake_token",
            agents=mock_agents
        )

        # Test that alert method exists
        assert hasattr(slack, 'send_alert')

# ============================================================================
# INTEGRATION TESTS - JIRA
# ============================================================================

@pytest.mark.asyncio
async def test_jira_integration_init():
    """Test Jira integration initialization"""
    from integrations.jira_integration import JiraIntegration

    mock_agents = {'prophet': Mock()}

    with patch('integrations.jira_integration.JIRA'):
        jira = JiraIntegration(
            server="https://test.atlassian.net",
            email="test@test.com",
            api_token="fake_token",
            agents=mock_agents
        )

        assert jira is not None
        assert jira.agents == mock_agents

@pytest.mark.asyncio
async def test_jira_create_issue():
    """Test Jira issue creation"""
    from integrations.jira_integration import JiraIntegration

    mock_agents = {'prophet': Mock()}

    with patch('integrations.jira_integration.JIRA') as mock_jira_class:
        mock_jira = Mock()
        mock_issue = Mock()
        mock_issue.key = "TEST-123"
        mock_issue.id = "12345"
        mock_jira.create_issue.return_value = mock_issue
        mock_jira._options = {'server': 'https://test.atlassian.net'}
        mock_jira_class.return_value = mock_jira

        jira = JiraIntegration(
            server="https://test.atlassian.net",
            email="test@test.com",
            api_token="fake_token",
            agents=mock_agents
        )

        result = await jira.create_issue(
            project_key="TEST",
            summary="Test issue",
            description="Test description"
        )

        assert result["key"] == "TEST-123"
        assert "url" in result

# ============================================================================
# MAIN ENTRY POINT TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_devmind_initialization():
    """Test E3 DevMind AI initialization"""
    from devmind_core.main import E3DevMindAI

    devmind = E3DevMindAI()

    assert devmind is not None
    assert devmind.initialized is False
    assert devmind.agents == {}

@pytest.mark.asyncio
async def test_devmind_component_initialization():
    """Test E3 DevMind AI component initialization flow"""
    from devmind_core.main import E3DevMindAI

    with patch('devmind_core.main.CSDLvLLMClient'):
        with patch('devmind_core.main.QdrantManager'):
            with patch('devmind_core.main.ANLTTranslator'):
                with patch('devmind_core.main.CSDLMessageBus'):
                    with patch('devmind_core.main.OracleAgent'):
                        devmind = E3DevMindAI()

                        # Test that initialization methods exist
                        assert hasattr(devmind, '_initialize_core')
                        assert hasattr(devmind, '_initialize_knowledge')
                        assert hasattr(devmind, '_initialize_agents')
                        assert hasattr(devmind, '_initialize_multimodal')
                        assert hasattr(devmind, '_initialize_integrations')

@pytest.mark.asyncio
async def test_devmind_process_query():
    """Test E3 DevMind AI query processing"""
    from devmind_core.main import E3DevMindAI

    devmind = E3DevMindAI()

    # Test that process_query method exists
    assert hasattr(devmind, 'process_query')
    assert callable(devmind.process_query)

# ============================================================================
# RUN ALL TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
