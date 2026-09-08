"""Lightweight in-memory session state with optional disk persistence.

Persisted data lives in `GUI-version/config/session.json` and is intentionally
kept minimal (provider + masked key hint). The actual API key is held only in
memory for the duration of the session.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


CONFIG_DIR = Path(__file__).resolve().parent / "config"
SESSION_FILE = CONFIG_DIR / "session.json"


@dataclass
class Session:
    provider: str = ""
    api_key: str = ""
    api_key_hint: str = ""
    settings: dict[str, Any] = field(default_factory=dict)

    def is_configured(self) -> bool:
        return bool(self.provider and self.api_key)

    def mask_key(self) -> str:
        if len(self.api_key) <= 8:
            return ""
        return self.api_key[:4] + "****" + self.api_key[-4:]

    def save(self) -> None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        payload = {
            "provider": self.provider,
            "api_key_hint": self.mask_key(),
            "settings": self.settings,
        }
        SESSION_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @classmethod
    def load(cls) -> "Session":
        if not SESSION_FILE.exists():
            return cls()
        try:
            data = json.loads(SESSION_FILE.read_text(encoding="utf-8"))
            return cls(
                provider=data.get("provider", ""),
                api_key="",
                api_key_hint=data.get("api_key_hint", ""),
                settings=data.get("settings", {}),
            )
        except Exception:
            return cls()

    def reset(self) -> None:
        self.provider = ""
        self.api_key = ""
        self.api_key_hint = ""
        self.settings = {}
        if SESSION_FILE.exists():
            SESSION_FILE.unlink()
