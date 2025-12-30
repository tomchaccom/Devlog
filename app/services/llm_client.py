from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Protocol

import httpx


class LLMClient(Protocol):
    def complete(self, prompt: str) -> str:
        """Return raw JSON string content from the model."""


@dataclass
class OpenAICompatibleClient:
    """
    Thin client around OpenAI-compatible /v1/chat/completions.
    We keep it minimal and synchronous for deterministic behavior
    and to avoid hidden retries that complicate debugging.
    """

    base_url: str
    api_key: str
    model: str
    timeout_s: float = 20.0

    def complete(self, prompt: str) -> str:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "model": self.model,
            "temperature": 0.0,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a senior backend engineer mentoring a junior developer. "
                        "Be precise, critical, and constructive."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        }

        with httpx.Client(timeout=self.timeout_s) as client:
            response = client.post(
                f"{self.base_url}/v1/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        # Expect OpenAI-compatible schema.
        return data["choices"][0]["message"]["content"]


@dataclass
class StubLLMClient:
    """
    Deterministic stub for local tests. Ensures the service can boot
    without calling a real model and avoids hardcoded credentials.
    """

    response_json: str

    def complete(self, prompt: str) -> str:
        return self.response_json
