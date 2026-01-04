"""
CSDL-vLLM Client

Client for CSDL-vLLM (custom LLM that processes CSDL natively)

This LLM processes CSDL directly - no translation needed.
Integration with: https://github.com/LUBTFY/CSDL-vLLM

CRITICAL: Both input and output are pure CSDL.
No compression/decompression happens at this layer.
"""

import aiohttp
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import structlog
from devmind_core.config import CSDLvLLMConfig

logger = structlog.get_logger()


class CSDLvLLMClient:
    """
    Client for CSDL-vLLM (your custom LLM)

    This LLM processes CSDL natively - no translation needed.

    Features:
    - Native CSDL processing (3-5x faster)
    - Zero translation overhead
    - Optimized for Grace Blackwell
    - Supports unlimited agents at near-zero cost
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        config: Optional[CSDLvLLMConfig] = None
    ):
        """
        Initialize CSDL-vLLM client

        Args:
            base_url: Base URL of CSDL-vLLM service
            api_key: API key for authentication
            config: Configuration object
        """
        if config:
            self.base_url = config.url
            self.api_key = config.api_key
            self.timeout = config.timeout
            self.max_retries = config.max_retries
        else:
            self.base_url = base_url or "http://localhost:8002"
            self.api_key = api_key
            self.timeout = 120
            self.max_retries = 3

        self.session: Optional[aiohttp.ClientSession] = None
        self._session_created = False

    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session and self._session_created:
            await self.session.close()
            self.session = None
            self._session_created = False

    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
            self._session_created = True

    async def generate(
        self,
        csdl_input: Dict[str, Any],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        agent_context: Optional[Dict[str, Any]] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Generate response from CSDL input

        CRITICAL: Both input and output are pure CSDL.
        No compression/decompression happens here.

        Args:
            csdl_input: CSDL-formatted input
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Max tokens to generate
            agent_context: Agent-specific context (also CSDL)
            stream: Whether to stream the response

        Returns:
            CSDL-formatted output with metadata
        """
        await self._ensure_session()

        payload = {
            "csdl_input": csdl_input,
            "parameters": {
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": stream
            }
        }

        if agent_context:
            payload["agent_context"] = agent_context

        headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        # Retry logic
        for attempt in range(self.max_retries):
            try:
                start_time = datetime.now()

                async with self.session.post(
                    f"{self.base_url}/v1/generate",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        end_time = datetime.now()
                        duration_ms = (end_time - start_time).total_seconds() * 1000

                        logger.info(
                            "csdl_vllm_generate_success",
                            duration_ms=duration_ms,
                            tokens_used=result.get("tokens_used", 0)
                        )

                        return {
                            "csdl_output": result.get("csdl_output", {}),
                            "metadata": result.get("metadata", {}),
                            "tokens_used": result.get("tokens_used", 0),
                            "duration_ms": duration_ms
                        }
                    else:
                        error_text = await response.text()
                        logger.error(
                            "csdl_vllm_generate_error",
                            status=response.status,
                            error=error_text,
                            attempt=attempt + 1
                        )

                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(2 ** attempt)  # Exponential backoff
                        else:
                            raise Exception(
                                f"CSDL-vLLM request failed: {response.status} - {error_text}"
                            )

            except aiohttp.ClientError as e:
                logger.error(
                    "csdl_vllm_network_error",
                    error=str(e),
                    attempt=attempt + 1
                )

                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise Exception(f"CSDL-vLLM network error: {str(e)}")

        raise Exception("CSDL-vLLM request failed after all retries")

    async def generate_batch(
        self,
        csdl_inputs: List[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        agent_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate responses for multiple CSDL inputs in parallel

        Args:
            csdl_inputs: List of CSDL-formatted inputs
            temperature: Sampling temperature
            max_tokens: Max tokens per generation
            agent_context: Shared agent context

        Returns:
            List of CSDL-formatted outputs
        """
        tasks = [
            self.generate(
                csdl_input=csdl_input,
                temperature=temperature,
                max_tokens=max_tokens,
                agent_context=agent_context
            )
            for csdl_input in csdl_inputs
        ]

        return await asyncio.gather(*tasks)

    async def health_check(self) -> Dict[str, Any]:
        """
        Check if CSDL-vLLM is healthy

        Returns:
            Health status dict
        """
        await self._ensure_session()

        try:
            async with self.session.get(
                f"{self.base_url}/health",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "status": "healthy",
                        "details": data
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "error": f"HTTP {response.status}"
                    }
        except Exception as e:
            return {
                "status": "unreachable",
                "error": str(e)
            }

    async def get_model_info(self) -> Dict[str, Any]:
        """
        Get CSDL-vLLM model information

        Returns:
            Model info dict
        """
        await self._ensure_session()

        try:
            async with self.session.get(
                f"{self.base_url}/v1/model/info"
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Failed to get model info: {response.status}")
        except Exception as e:
            logger.error("get_model_info_error", error=str(e))
            raise

    async def close(self):
        """Close the client session"""
        if self.session and self._session_created:
            await self.session.close()
            self.session = None
            self._session_created = False


class CSDLvLLMPool:
    """
    Connection pool for CSDL-vLLM clients

    Manages multiple clients for high-throughput scenarios
    """

    def __init__(
        self,
        pool_size: int = 10,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        config: Optional[CSDLvLLMConfig] = None
    ):
        """
        Initialize CSDL-vLLM connection pool

        Args:
            pool_size: Number of clients in pool
            base_url: Base URL of CSDL-vLLM service
            api_key: API key for authentication
            config: Configuration object
        """
        self.pool_size = pool_size
        self.base_url = base_url
        self.api_key = api_key
        self.config = config
        self.clients: List[CSDLvLLMClient] = []
        self.available: asyncio.Queue = asyncio.Queue()
        self._initialized = False

    async def initialize(self):
        """Initialize the connection pool"""
        if self._initialized:
            return

        for _ in range(self.pool_size):
            client = CSDLvLLMClient(
                base_url=self.base_url,
                api_key=self.api_key,
                config=self.config
            )
            await client._ensure_session()
            self.clients.append(client)
            await self.available.put(client)

        self._initialized = True
        logger.info("csdl_vllm_pool_initialized", pool_size=self.pool_size)

    async def acquire(self) -> CSDLvLLMClient:
        """
        Acquire a client from the pool

        Returns:
            CSDLvLLMClient instance
        """
        if not self._initialized:
            await self.initialize()

        return await self.available.get()

    async def release(self, client: CSDLvLLMClient):
        """
        Release a client back to the pool

        Args:
            client: Client to release
        """
        await self.available.put(client)

    async def close_all(self):
        """Close all clients in the pool"""
        for client in self.clients:
            await client.close()
        self.clients.clear()
        self._initialized = False
        logger.info("csdl_vllm_pool_closed")

    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close_all()
