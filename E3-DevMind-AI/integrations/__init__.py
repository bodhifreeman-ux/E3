"""
E3 DevMind AI - External Integrations

Integrations with external services:
- GitHub: Repository monitoring, PR analysis, issue triage
- Slack: Team communication, Q&A, alerts
- Jira: Project management, sprint tracking, issue management
"""

from integrations.github_integration import GitHubIntegration
from integrations.slack_integration import SlackIntegration
from integrations.jira_integration import JiraIntegration

__all__ = [
    "GitHubIntegration",
    "SlackIntegration",
    "JiraIntegration",
]
