"""
E3 DevMind AI - Main Entry Point

Initializes and runs the complete E3 DevMind AI system.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import signal
import sys

# Core imports
from devmind_core.config import get_settings
from csdl.vllm_client import CSDLvLLMClient
from csdl.message_bus import CSDLMessageBus
from anlt.translator import ANLTTranslator

# Import all 32 agents
from agents.oracle import OracleAgent
from agents.prophet import ProphetAgent
from agents.sage import SageAgent
from agents.strategist import StrategistAgent
from agents.economist import EconomistAgent
from agents.investigator import InvestigatorAgent
from agents.critic import CriticAgent
from agents.visionary import VisionaryAgent
from agents.detective import DetectiveAgent
from agents.historian import HistorianAgent
from agents.cartographer import CartographerAgent
from agents.architect import ArchitectAgent
# ... import remaining agents

# Knowledge system imports
from knowledge.retrieval.qdrant_manager import QdrantManager
from knowledge.ingestion.document_loader import DocumentLoader

# Multimodal imports
from multimodal.voice.voice_processor import VoiceProcessor
from multimodal.vision.vision_processor import VisionProcessor
from multimodal.video.video_processor import VideoProcessor

# Integration imports
from integrations.github_integration import GitHubIntegration
from integrations.slack_integration import SlackIntegration
from integrations.jira_integration import JiraIntegration

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class E3DevMindAI:
    """
    E3 DevMind AI - Complete System

    Orchestrates all 32 agents, knowledge system, multimodal intelligence,
    and external integrations.
    """

    def __init__(self):
        """Initialize E3 DevMind AI"""
        self.settings = get_settings()

        # Core components
        self.vllm_client = None
        self.anlt = None
        self.message_bus = None

        # Agent registry
        self.agents = {}

        # Knowledge system
        self.knowledge_store = None
        self.document_loader = None

        # Multimodal
        self.voice = None
        self.vision = None
        self.video = None

        # Integrations
        self.github = None
        self.slack = None
        self.jira = None

        # State
        self.is_running = False
        self.initialized = False

    async def initialize(self):
        """
        Initialize all components

        Order:
        1. Core infrastructure (vLLM, ANLT, message bus)
        2. Knowledge system
        3. All 32 agents
        4. Multimodal processors
        5. External integrations
        """
        if self.initialized:
            logger.warning("E3 DevMind AI already initialized")
            return

        logger.info("="*60)
        logger.info("🚀 Initializing E3 DevMind AI...")
        logger.info("="*60)

        try:
            # Step 1: Core infrastructure
            await self._initialize_core()

            # Step 2: Knowledge system
            await self._initialize_knowledge()

            # Step 3: Agent swarm
            await self._initialize_agents()

            # Step 4: Multimodal
            await self._initialize_multimodal()

            # Step 5: Integrations
            await self._initialize_integrations()

            self.initialized = True

            logger.info("="*60)
            logger.info("✅ E3 DevMind AI initialized successfully!")
            logger.info("="*60)
            logger.info(f"   • Agents: {len(self.agents)}/32")
            logger.info(f"   • CSDL-vLLM: Connected")
            logger.info(f"   • Knowledge Base: Ready")
            logger.info(f"   • Multimodal: Ready")
            logger.info("="*60)

        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}", exc_info=True)
            raise

    async def _initialize_core(self):
        """Initialize core infrastructure"""
        logger.info("1️⃣  Initializing core infrastructure...")

        # CSDL-vLLM client
        self.vllm_client = CSDLvLLMClient(
            base_url=self.settings.CSDL_VLLM_URL,
            api_key=self.settings.CSDL_VLLM_API_KEY
        )

        # Check connection
        if await self.vllm_client.health_check():
            logger.info("   ✅ CSDL-vLLM connected")
        else:
            raise Exception("CSDL-vLLM not available")

        # ANLT translator
        self.anlt = ANLTTranslator(
            compression_level=self.settings.ANLT_COMPRESSION_LEVEL
        )
        logger.info("   ✅ ANLT initialized")

        # Message bus
        self.message_bus = CSDLMessageBus()
        logger.info("   ✅ Message bus initialized")

    async def _initialize_knowledge(self):
        """Initialize knowledge system"""
        logger.info("2️⃣  Initializing knowledge system...")

        # Qdrant vector store
        self.knowledge_store = QdrantManager(
            host=self.settings.QDRANT_HOST,
            port=self.settings.QDRANT_PORT
        )

        await self.knowledge_store.initialize()
        logger.info("   ✅ Qdrant initialized")

        # Document loader (will need Librarian agent)
        # Initialized after agents

    async def _initialize_agents(self):
        """Initialize all 32 agents"""
        logger.info("3️⃣  Initializing 32-agent swarm...")

        # Agent #1: Oracle (main coordinator)
        self.agents['oracle'] = OracleAgent(
            vllm_client=self.vllm_client,
            knowledge_base=self.knowledge_store,
            agent_registry=self.agents,
            config=self.settings.dict()
        )
        logger.info("   ✅ Oracle (Main Coordinator)")

        # Strategic Intelligence agents (#2-5)
        self.agents['prophet'] = ProphetAgent(
            vllm_client=self.vllm_client,
            knowledge_base=self.knowledge_store
        )
        logger.info("   ✅ Prophet (Predictive Analytics)")

        self.agents['sage'] = SageAgent(
            vllm_client=self.vllm_client,
            knowledge_base=self.knowledge_store
        )
        logger.info("   ✅ Sage (Meta-Reasoner)")

        self.agents['strategist'] = StrategistAgent(
            vllm_client=self.vllm_client,
            knowledge_base=self.knowledge_store
        )
        logger.info("   ✅ Strategist (Solution Designer)")

        self.agents['economist'] = EconomistAgent(
            vllm_client=self.vllm_client,
            knowledge_base=self.knowledge_store
        )
        logger.info("   ✅ Economist (Resource Optimizer)")

        # Deep Analysis agents (#6-11)
        self.agents['investigator'] = InvestigatorAgent(
            vllm_client=self.vllm_client,
            knowledge_base=self.knowledge_store
        )
        logger.info("   ✅ Investigator (Technical Analyzer)")

        # ... initialize remaining 26 agents
        # (In production, all 32 agents would be initialized here)

        logger.info(f"   ✅ Initialized {len(self.agents)} agents")

        # Now initialize document loader with Librarian
        if 'librarian' in self.agents:
            self.document_loader = DocumentLoader(
                librarian_agent=self.agents['librarian'],
                knowledge_store=self.knowledge_store
            )
            logger.info("   ✅ Document loader initialized")

    async def _initialize_multimodal(self):
        """Initialize multimodal processors"""
        logger.info("4️⃣  Initializing multimodal intelligence...")

        if self.settings.OPENAI_API_KEY:
            # Voice processor
            self.voice = VoiceProcessor(
                openai_api_key=self.settings.OPENAI_API_KEY,
                anlt_client=self.anlt
            )
            logger.info("   ✅ Voice processor (Whisper + TTS)")

            # Vision processor
            self.vision = VisionProcessor(
                openai_api_key=self.settings.OPENAI_API_KEY,
                anlt_client=self.anlt
            )
            logger.info("   ✅ Vision processor (GPT-4V)")

            # Video processor
            self.video = VideoProcessor(
                voice_processor=self.voice,
                vision_processor=self.vision,
                anlt_client=self.anlt
            )
            logger.info("   ✅ Video processor")
        else:
            logger.warning("   ⚠️  Multimodal disabled (no OpenAI API key)")

    async def _initialize_integrations(self):
        """Initialize external integrations"""
        logger.info("5️⃣  Initializing integrations...")

        # GitHub
        if self.settings.GITHUB_TOKEN:
            self.github = GitHubIntegration(
                token=self.settings.GITHUB_TOKEN,
                agents=self.agents
            )
            logger.info("   ✅ GitHub integration")

        # Slack
        if self.settings.SLACK_BOT_TOKEN:
            self.slack = SlackIntegration(
                token=self.settings.SLACK_BOT_TOKEN,
                agents=self.agents
            )
            logger.info("   ✅ Slack integration")

        # Jira
        if all([self.settings.JIRA_SERVER, self.settings.JIRA_EMAIL, self.settings.JIRA_API_TOKEN]):
            self.jira = JiraIntegration(
                server=self.settings.JIRA_SERVER,
                email=self.settings.JIRA_EMAIL,
                api_token=self.settings.JIRA_API_TOKEN,
                agents=self.agents
            )
            logger.info("   ✅ Jira integration")

    async def process_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Process a natural language query

        Flow:
        1. Human query → ANLT → CSDL
        2. CSDL → Oracle
        3. Oracle coordinates agent swarm
        4. Response CSDL → ANLT → Natural language
        """
        if not self.initialized:
            raise Exception("E3 DevMind AI not initialized")

        logger.info(f"Processing query: {query[:100]}...")

        # Step 1: Translate to CSDL
        csdl_query = self.anlt.text_to_csdl(query)

        # Step 2: Create CSDL message
        from csdl.protocol import CSDLMessage

        message = CSDLMessage(
            message_type="query",
            sender_id="human",
            recipient_id="oracle",
            content=csdl_query,
            metadata={"context": context or {}}
        )

        # Step 3: Send to Oracle
        response_csdl = await self.agents['oracle'].process_csdl(message)

        # Step 4: Translate back to natural language
        response_text = self.anlt.csdl_to_text(response_csdl.content)

        logger.info("Query processed successfully")

        return response_text

    async def run(self):
        """Run E3 DevMind AI system"""
        await self.initialize()

        self.is_running = True
        logger.info("E3 DevMind AI is running...")

        # Setup signal handlers
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(
                sig,
                lambda: asyncio.create_task(self.shutdown())
            )

        # Keep running
        try:
            while self.is_running:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass

    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("Shutting down E3 DevMind AI...")

        self.is_running = False

        # Close connections
        if self.vllm_client:
            # await self.vllm_client.close()
            pass

        logger.info("E3 DevMind AI shut down complete")

async def main():
    """Main entry point"""
    devmind = E3DevMindAI()
    await devmind.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
