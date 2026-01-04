"""
GitHub Integration

Monitors repositories, analyzes PRs, tracks issues for E3 projects.
"""

from github import Github, GithubException
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class GitHubIntegration:
    """
    GitHub integration for E3 DevMind AI

    Capabilities:
    - Monitor repositories for changes
    - Automatically analyze pull requests
    - Track and triage issues
    - Comment on PRs with insights
    - Generate PR summaries
    """

    def __init__(self, token: str, agents: Dict[str, Any]):
        """
        Initialize GitHub integration

        Args:
            token: GitHub personal access token
            agents: Dictionary of E3 DevMind AI agents
        """
        self.github = Github(token)
        self.agents = agents
        logger.info("GitHub integration initialized")

    async def monitor_repository(
        self,
        repo_name: str,
        check_prs: bool = True,
        check_issues: bool = True
    ) -> Dict[str, Any]:
        """
        Monitor a repository for activity

        Args:
            repo_name: Repository name (e.g., "E3-Consortium/platform")
            check_prs: Check pull requests
            check_issues: Check issues

        Returns:
            Dictionary with monitoring results
        """
        try:
            logger.info(f"Monitoring repository: {repo_name}")

            repo = self.github.get_repo(repo_name)
            results = {
                "repository": repo_name,
                "timestamp": datetime.now().isoformat()
            }

            if check_prs:
                results["pull_requests"] = await self._check_pull_requests(repo)

            if check_issues:
                results["issues"] = await self._check_issues(repo)

            return results

        except GithubException as e:
            logger.error(f"GitHub API error: {e}")
            raise

    async def _check_pull_requests(self, repo) -> List[Dict[str, Any]]:
        """Check open pull requests"""
        pulls = repo.get_pulls(state='open', sort='updated', direction='desc')

        pr_results = []
        for pr in list(pulls)[:10]:  # Check last 10 PRs
            analysis = await self.analyze_pr(repo.full_name, pr.number)
            pr_results.append(analysis)

        return pr_results

    async def _check_issues(self, repo) -> List[Dict[str, Any]]:
        """Check open issues"""
        issues = repo.get_issues(state='open', sort='updated', direction='desc')

        issue_results = []
        for issue in list(issues)[:20]:  # Check last 20 issues
            if not issue.pull_request:  # Exclude PRs
                triage = await self.triage_issue(repo.full_name, issue.number)
                issue_results.append(triage)

        return issue_results

    async def analyze_pr(
        self,
        repo_name: str,
        pr_number: int
    ) -> Dict[str, Any]:
        """
        Analyze a pull request

        Uses multiple agents:
        - Craftsman: Code quality review
        - Sentinel: Security check
        - Scientist: Test coverage analysis
        """
        try:
            logger.info(f"Analyzing PR #{pr_number} in {repo_name}")

            repo = self.github.get_repo(repo_name)
            pr = repo.get_pull(pr_number)

            # Get PR files
            files = list(pr.get_files())

            # Prepare analysis request
            from csdl.protocol import CSDLMessage

            analysis_request = {
                "query_type": "code_review",
                "pr_info": {
                    "number": pr.number,
                    "title": pr.title,
                    "description": pr.body,
                    "author": pr.user.login,
                    "created_at": pr.created_at.isoformat(),
                    "updated_at": pr.updated_at.isoformat()
                },
                "files": [
                    {
                        "filename": f.filename,
                        "status": f.status,
                        "additions": f.additions,
                        "deletions": f.deletions,
                        "changes": f.changes,
                        "patch": f.patch[:5000] if f.patch else None  # Limit size
                    }
                    for f in files
                ],
                "stats": {
                    "total_files": len(files),
                    "total_additions": sum(f.additions for f in files),
                    "total_deletions": sum(f.deletions for f in files)
                }
            }

            # Analyze with Craftsman agent (code quality)
            craftsman = self.agents.get('craftsman')
            if craftsman:
                message = CSDLMessage(
                    message_type="request",
                    sender_id="github_integration",
                    content=analysis_request
                )

                review = await craftsman.process_csdl(message)

                return {
                    "pr_number": pr.number,
                    "title": pr.title,
                    "analysis": review.content,
                    "analyzed_at": datetime.now().isoformat()
                }

            return {
                "pr_number": pr.number,
                "title": pr.title,
                "error": "Craftsman agent not available"
            }

        except Exception as e:
            logger.error(f"Error analyzing PR #{pr_number}: {e}")
            return {
                "pr_number": pr_number,
                "error": str(e)
            }

    async def comment_on_pr(
        self,
        repo_name: str,
        pr_number: int,
        comment: str
    ) -> bool:
        """
        Post comment on pull request

        Args:
            repo_name: Repository name
            pr_number: PR number
            comment: Comment text

        Returns:
            True if successful
        """
        try:
            repo = self.github.get_repo(repo_name)
            pr = repo.get_pull(pr_number)

            pr.create_issue_comment(comment)

            logger.info(f"Posted comment on PR #{pr_number}")
            return True

        except Exception as e:
            logger.error(f"Failed to comment on PR: {e}")
            return False

    async def triage_issue(
        self,
        repo_name: str,
        issue_number: int
    ) -> Dict[str, Any]:
        """
        Triage an issue

        Uses Strategist agent to:
        - Determine priority
        - Suggest labels
        - Recommend assignment
        """
        try:
            repo = self.github.get_repo(repo_name)
            issue = repo.get_issue(issue_number)

            # Prepare triage request
            triage_request = {
                "query_type": "issue_triage",
                "issue": {
                    "number": issue.number,
                    "title": issue.title,
                    "body": issue.body,
                    "labels": [label.name for label in issue.labels],
                    "created_at": issue.created_at.isoformat()
                }
            }

            # Use Strategist for triage
            strategist = self.agents.get('strategist')
            if strategist:
                from csdl.protocol import CSDLMessage

                message = CSDLMessage(
                    message_type="request",
                    sender_id="github_integration",
                    content=triage_request
                )

                triage = await strategist.process_csdl(message)

                return {
                    "issue_number": issue.number,
                    "triage": triage.content
                }

            return {
                "issue_number": issue.number,
                "error": "Strategist agent not available"
            }

        except Exception as e:
            logger.error(f"Error triaging issue #{issue_number}: {e}")
            return {
                "issue_number": issue_number,
                "error": str(e)
            }

    async def generate_pr_summary(
        self,
        repo_name: str,
        pr_number: int
    ) -> str:
        """
        Generate comprehensive PR summary

        Returns markdown summary suitable for posting
        """
        analysis = await self.analyze_pr(repo_name, pr_number)

        if "error" in analysis:
            return f"⚠️ Unable to analyze PR: {analysis['error']}"

        # Generate markdown summary
        summary = f"""## 🤖 E3 DevMind AI - PR Analysis

**PR #{analysis['pr_number']}:** {analysis['title']}

### Code Quality Review
{analysis.get('analysis', {}).get('quality_review', 'No review available')}

### Security Check
{analysis.get('analysis', {}).get('security_check', 'No security issues detected')}

### Test Coverage
{analysis.get('analysis', {}).get('test_coverage', 'Test coverage analysis unavailable')}

---
*Analysis performed by E3 DevMind AI at {analysis['analyzed_at']}*
"""

        return summary
