"""
Slack Integration

E3 team communication integration.
"""

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from typing import Dict, Any, Optional
import logging
import re

logger = logging.getLogger(__name__)

class SlackIntegration:
    """
    Slack integration for E3 DevMind AI

    Capabilities:
    - Answer questions in Slack channels
    - Send proactive notifications and alerts
    - Summarize conversations
    - Participate in threads
    - Alert team on critical issues
    """

    def __init__(self, token: str, agents: Dict[str, Any]):
        """
        Initialize Slack integration

        Args:
            token: Slack bot token
            agents: Dictionary of E3 DevMind AI agents
        """
        self.client = WebClient(token=token)
        self.agents = agents
        logger.info("Slack integration initialized")

    async def send_message(
        self,
        channel: str,
        text: str,
        thread_ts: Optional[str] = None,
        blocks: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Send message to Slack channel

        Args:
            channel: Channel ID or name
            text: Message text
            thread_ts: Thread timestamp (for replies)
            blocks: Block Kit blocks for rich formatting

        Returns:
            Slack API response
        """
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                text=text,
                thread_ts=thread_ts,
                blocks=blocks
            )

            logger.info(f"Sent message to {channel}")
            return response.data

        except SlackApiError as e:
            logger.error(f"Slack API error: {e.response['error']}")
            raise

    async def handle_mention(
        self,
        event: Dict[str, Any]
    ) -> str:
        """
        Handle @devmind mention in Slack

        Flow:
        1. Extract question from message
        2. Process with Oracle
        3. Send response in thread

        Args:
            event: Slack event data

        Returns:
            Response text
        """
        try:
            text = event.get('text', '')
            channel = event.get('channel')
            thread_ts = event.get('thread_ts') or event.get('ts')
            user = event.get('user')

            # Remove bot mention
            question = re.sub(r'<@[A-Z0-9]+>', '', text).strip()

            if not question:
                await self.send_message(
                    channel,
                    "Hi! How can I help you? Ask me anything about E3!",
                    thread_ts=thread_ts
                )
                return ""

            logger.info(f"Processing Slack question from {user}: {question}")

            # Send thinking indicator
            thinking_msg = await self.send_message(
                channel,
                "🤔 Let me think about that...",
                thread_ts=thread_ts
            )

            # Process with Oracle
            oracle = self.agents.get('oracle')
            if oracle:
                from csdl.protocol import CSDLMessage
                from anlt.translator import ANLTTranslator

                anlt = ANLTTranslator()

                # Convert to CSDL
                csdl_query = anlt.text_to_csdl(question)

                message = CSDLMessage(
                    message_type="query",
                    sender_id="slack_integration",
                    content=csdl_query,
                    metadata={"user": user, "channel": channel}
                )

                # Get response
                response_csdl = await oracle.process_csdl(message)
                response_text = anlt.csdl_to_text(response_csdl.content)

                # Delete thinking message
                try:
                    self.client.chat_delete(
                        channel=channel,
                        ts=thinking_msg['ts']
                    )
                except:
                    pass

                # Send actual response
                await self.send_message(
                    channel,
                    response_text,
                    thread_ts=thread_ts
                )

                return response_text

            else:
                await self.send_message(
                    channel,
                    "❌ Oracle agent not available",
                    thread_ts=thread_ts
                )
                return "Error: Oracle not available"

        except Exception as e:
            logger.error(f"Error handling mention: {e}", exc_info=True)
            await self.send_message(
                event['channel'],
                f"❌ Error processing question: {str(e)}",
                thread_ts=event.get('thread_ts') or event.get('ts')
            )
            return f"Error: {str(e)}"

    async def send_alert(
        self,
        channel: str,
        alert_type: str,
        details: Dict[str, Any]
    ):
        """
        Send proactive alert to Slack

        Alert types:
        - risk: Risk detected by Prophet
        - security: Security issue found by Sentinel
        - build_failure: Build failure detected by Ops
        - deployment: Deployment notification
        """
        try:
            # Alert emoji and colors
            alert_config = {
                "risk": {
                    "emoji": "⚠️",
                    "color": "#FFA500",
                    "title": "Risk Alert"
                },
                "security": {
                    "emoji": "🔒",
                    "color": "#FF0000",
                    "title": "Security Alert"
                },
                "build_failure": {
                    "emoji": "❌",
                    "color": "#FF0000",
                    "title": "Build Failure"
                },
                "deployment": {
                    "emoji": "🚀",
                    "color": "#00FF00",
                    "title": "Deployment"
                }
            }

            config = alert_config.get(alert_type, alert_config["risk"])

            # Create rich message with Block Kit
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"{config['emoji']} {config['title']}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": details.get("message", "No details provided")
                    }
                }
            ]

            # Add fields if provided
            if "fields" in details:
                blocks.append({
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*{k}:*\n{v}"
                        }
                        for k, v in details["fields"].items()
                    ]
                })

            # Add actions if provided
            if "actions" in details:
                blocks.append({
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": action
                            },
                            "action_id": f"alert_{alert_type}_{action.lower().replace(' ', '_')}"
                        }
                        for action in details["actions"]
                    ]
                })

            await self.send_message(
                channel=channel,
                text=f"{config['emoji']} {details.get('message', 'Alert')}",
                blocks=blocks
            )

            logger.info(f"Sent {alert_type} alert to {channel}")

        except Exception as e:
            logger.error(f"Failed to send alert: {e}")

    async def summarize_conversation(
        self,
        channel: str,
        thread_ts: str
    ) -> str:
        """
        Summarize a Slack conversation thread

        Uses Synthesizer agent to create summary
        """
        try:
            # Get conversation history
            history = self.client.conversations_replies(
                channel=channel,
                ts=thread_ts
            )

            messages = [
                {
                    "user": msg.get("user", "unknown"),
                    "text": msg.get("text", ""),
                    "timestamp": msg.get("ts")
                }
                for msg in history["messages"]
            ]

            # Use Synthesizer to create summary
            synthesizer = self.agents.get('synthesizer')
            if synthesizer:
                from csdl.protocol import CSDLMessage

                message = CSDLMessage(
                    message_type="request",
                    sender_id="slack_integration",
                    content={
                        "query_type": "conversation_summary",
                        "messages": messages
                    }
                )

                summary_response = await synthesizer.process_csdl(message)
                summary = summary_response.content.get("summary", "Unable to generate summary")

                return summary

            return "Synthesizer agent not available"

        except Exception as e:
            logger.error(f"Failed to summarize conversation: {e}")
            return f"Error: {str(e)}"
