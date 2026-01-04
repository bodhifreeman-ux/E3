#!/usr/bin/env python3
"""
CSDL-14B Python Client Example

This module provides a simple client for interacting with the CSDL-14B model
via the Ollama API.
"""

import json
import requests
from typing import Optional, Dict, Any, Union


class CSDLClient:
    """Client for interacting with CSDL-14B model via Ollama."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "csdl-14b",
        timeout: int = 120
    ):
        """
        Initialize the CSDL client.

        Args:
            base_url: Ollama API base URL
            model: Model name to use (csdl-14b, csdl-14b-atlas, etc.)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = False
    ) -> Union[Dict[str, Any], str]:
        """
        Generate a response from the model.

        Args:
            prompt: The user prompt
            system: Optional system prompt override
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response

        Returns:
            Parsed JSON response or raw string if parsing fails
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        if system:
            payload["system"] = system

        response = requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()

        result = response.json()
        raw_response = result.get("response", "")

        # Try to parse as JSON (CSDL format)
        try:
            return json.loads(raw_response)
        except json.JSONDecodeError:
            return raw_response

    def chat(
        self,
        messages: list,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> Dict[str, Any]:
        """
        Have a chat conversation with the model.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Response dict with 'message' containing the assistant's reply
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        response = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    def list_models(self) -> list:
        """List available models."""
        response = requests.get(
            f"{self.base_url}/api/tags",
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json().get("models", [])

    def is_available(self) -> bool:
        """Check if the Ollama server is available."""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            return response.status_code == 200
        except requests.RequestException:
            return False


# Specialized agent classes
class AtlasAgent(CSDLClient):
    """Atlas - Reasoning and planning specialist."""

    def __init__(self, base_url: str = "http://localhost:11434"):
        super().__init__(base_url=base_url, model="csdl-14b-atlas")

    def plan_task(self, task: str) -> Dict[str, Any]:
        """Create a plan for a given task."""
        return self.generate(
            f"Create a detailed step-by-step plan for: {task}",
            temperature=0.6
        )

    def reflect(self, context: str, outcome: str) -> Dict[str, Any]:
        """Reflect on an outcome and suggest improvements."""
        return self.generate(
            f"Context: {context}\nOutcome: {outcome}\n\nReflect on this outcome and suggest improvements.",
            temperature=0.6
        )


class NexusAgent(CSDLClient):
    """NEXUS - Code generation specialist."""

    def __init__(self, base_url: str = "http://localhost:11434"):
        super().__init__(base_url=base_url, model="csdl-14b-nexus")

    def generate_function(self, description: str) -> Dict[str, Any]:
        """Generate a CSDL function definition."""
        return self.generate(
            f"Generate a CSDL function definition for: {description}",
            temperature=0.5
        )

    def generate_class(self, description: str) -> Dict[str, Any]:
        """Generate a CSDL class definition."""
        return self.generate(
            f"Generate a CSDL class definition for: {description}",
            temperature=0.5
        )


class MarketingAgent(CSDLClient):
    """Marketing - Content generation specialist."""

    def __init__(self, base_url: str = "http://localhost:11434"):
        super().__init__(base_url=base_url, model="csdl-14b-marketing")

    def generate_content(self, brief: str) -> Dict[str, Any]:
        """Generate content based on a brief."""
        return self.generate(
            f"Generate content for: {brief}",
            temperature=0.8
        )


# Example usage
if __name__ == "__main__":
    # Basic usage
    client = CSDLClient()

    if not client.is_available():
        print("Error: Ollama server is not available")
        print("Start it with: ollama serve")
        exit(1)

    print("Available models:")
    for model in client.list_models():
        print(f"  - {model['name']}")

    print("\n--- Basic Generation ---")
    response = client.generate("Define a CSDL function to validate email addresses")
    print(json.dumps(response, indent=2))

    print("\n--- Atlas Planning ---")
    atlas = AtlasAgent()
    plan = atlas.plan_task("Build a REST API for user management")
    print(json.dumps(plan, indent=2))

    print("\n--- NEXUS Code Generation ---")
    nexus = NexusAgent()
    func = nexus.generate_function("Search documents in a vector database")
    print(json.dumps(func, indent=2))
