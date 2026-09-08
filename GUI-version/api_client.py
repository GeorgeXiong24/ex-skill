"""Lightweight API client for DeepSeek and Kimi (Moonshot).

Implements the smallest possible compatible layer using only stdlib `urllib` so
that the GUI does not depend on provider-specific SDKs.
"""

from __future__ import annotations

import json
import os
import ssl
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Iterable


@dataclass
class Message:
    role: str
    content: str


class ApiError(Exception):
    pass


class ApiClient:
    """Generic OpenAI-compatible chat client.

    DeepSeek and Kimi both expose an OpenAI-compatible `/chat/completions`
    endpoint. The differences are only the base URL and the model name.
    """

    _ENDPOINTS = {
        "deepseek": ("https://api.deepseek.com/v1/chat/completions", "deepseek-chat"),
        "kimi": ("https://api.moonshot.cn/v1/chat/completions", "moonshot-v1-8k"),
    }

    def __init__(self, provider: str, api_key: str):
        provider = provider.lower().strip()
        if provider not in self._ENDPOINTS:
            raise ApiError(f"Unsupported provider: {provider}")
        self.provider = provider
        self.api_key = api_key
        self.url, self.model = self._ENDPOINTS[provider]

    def chat(self, messages: Iterable[Message], temperature: float = 0.7) -> str:
        payload = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
        }
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        request = urllib.request.Request(self.url, data=data, headers=headers, method="POST")

        try:
            context = ssl.create_default_context()
            with urllib.request.urlopen(request, timeout=120, context=context) as response:
                result = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="ignore")
            raise ApiError(f"API request failed ({exc.code}): {body}") from exc
        except Exception as exc:
            raise ApiError(f"API request failed: {exc}") from exc

        try:
            return result["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise ApiError(f"Unexpected API response format: {result}") from exc

    def validate_key(self) -> None:
        """Lightweight validation: send a minimal request and check it succeeds."""
        self.chat([Message(role="user", content="Hi")], temperature=0.1)


def format_key_error(provider: str, error: ApiError) -> str:
    """Convert an API error into a friendly message."""
    text = str(error).lower()
    if "401" in text or "unauthorized" in text or "invalid" in text:
        return "The API key appears to be invalid or unauthorized. Please check it and try again."
    if "429" in text:
        return "Rate limit exceeded. Please wait a moment and try again."
    if "deepseek" in provider.lower():
        return "Could not connect to DeepSeek. Please check your key and network connection."
    return "Could not connect to Kimi. Please check your key and network connection."
