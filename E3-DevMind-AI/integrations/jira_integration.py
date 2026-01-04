"""
Jira Integration

Project management and issue tracking integration.
"""

from jira import JIRA
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class JiraIntegration:
    """
    Jira integration for E3 DevMind AI

    Capabilities:
    - Create issues automatically
    - Update issue status
    - Add comments with analysis
    - Track sprint progress
    - Generate reports
    """

    def __init__(self, server: str, email: str, api_token: str, agents: Dict[str, Any]):
        """
        Initialize Jira integration

        Args:
            server: Jira server URL
            email: User email
            api_token: Jira API token
            agents: Dictionary of E3 DevMind AI agents
        """
        self.jira = JIRA(
            server=server,
            basic_auth=(email, api_token)
        )
        self.agents = agents
        logger.info("Jira integration initialized")

    async def create_issue(
        self,
        project_key: str,
        summary: str,
        description: str,
        issue_type: str = "Task",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create Jira issue

        Args:
            project_key: Project key (e.g., "E3")
            summary: Issue summary
            description: Issue description
            issue_type: Issue type (Task, Bug, Story, etc.)
            **kwargs: Additional fields

        Returns:
            Created issue data
        """
        try:
            issue_dict = {
                'project': {'key': project_key},
                'summary': summary,
                'description': description,
                'issuetype': {'name': issue_type},
            }

            # Add additional fields
            issue_dict.update(kwargs)

            issue = self.jira.create_issue(fields=issue_dict)

            logger.info(f"Created Jira issue: {issue.key}")

            return {
                "key": issue.key,
                "id": issue.id,
                "url": f"{self.jira._options['server']}/browse/{issue.key}"
            }

        except Exception as e:
            logger.error(f"Failed to create Jira issue: {e}")
            raise

    async def add_comment(
        self,
        issue_key: str,
        comment: str
    ) -> bool:
        """
        Add comment to Jira issue
        """
        try:
            self.jira.add_comment(issue_key, comment)
            logger.info(f"Added comment to {issue_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to add comment: {e}")
            return False

    async def get_sprint_issues(
        self,
        board_id: int,
        sprint_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get issues in sprint

        If sprint_id is None, gets active sprint
        """
        try:
            if sprint_id is None:
                # Get active sprint
                sprints = self.jira.sprints(board_id, state='active')
                if not sprints:
                    return []
                sprint_id = sprints[0].id

            issues = self.jira.sprint(sprint_id)

            return [
                {
                    "key": issue.key,
                    "summary": issue.fields.summary,
                    "status": issue.fields.status.name,
                    "assignee": issue.fields.assignee.displayName if issue.fields.assignee else None
                }
                for issue in issues
            ]

        except Exception as e:
            logger.error(f"Failed to get sprint issues: {e}")
            return []

    async def analyze_sprint(
        self,
        board_id: int,
        sprint_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Analyze sprint with E3 DevMind AI

        Uses Prophet and Tracker agents to assess sprint health
        """
        try:
            issues = await self.get_sprint_issues(board_id, sprint_id)

            # Use Prophet to analyze sprint health
            prophet = self.agents.get('prophet')
            if prophet:
                from csdl.protocol import CSDLMessage

                message = CSDLMessage(
                    message_type="request",
                    sender_id="jira_integration",
                    content={
                        "query_type": "sprint_analysis",
                        "sprint_data": {
                            "board_id": board_id,
                            "sprint_id": sprint_id,
                            "issues": issues
                        }
                    }
                )

                analysis = await prophet.process_csdl(message)

                return {
                    "sprint_id": sprint_id,
                    "total_issues": len(issues),
                    "analysis": analysis.content
                }

            return {
                "sprint_id": sprint_id,
                "total_issues": len(issues),
                "error": "Prophet agent not available"
            }

        except Exception as e:
            logger.error(f"Failed to analyze sprint: {e}")
            return {"error": str(e)}
