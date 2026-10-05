"""Persistent user configuration for OpenBI Desktop.

Stored at ~/.config/openbi-desktop/config.toml (XDG-style).
"""

from __future__ import annotations

import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path

import tomli_w


def default_config_dir() -> Path:
    """Return the XDG config directory for the app, creating it if needed."""
    config_dir = Path.home() / ".config" / "openbi-desktop"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def default_config_path() -> Path:
    return default_config_dir() / "config.toml"


@dataclass
class AppConfig:
    """Top-level application configuration."""

    api_url: str = "http://localhost:8000"

    @classmethod
    def load(cls, path: Path | None = None) -> "AppConfig":
        path = path or default_config_path()
        if not path.exists():
            return cls()
        try:
            with path.open("rb") as f:
                data = tomllib.load(f)
        except (OSError, tomllib.TOMLDecodeError):
            # Corrupt or unreadable: fall back to defaults rather than crash.
            return cls()
        return cls(api_url=str(data.get("api_url", cls.api_url)))

    def save(self, path: Path | None = None) -> None:
        path = path or default_config_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("wb") as f:
            tomli_w.dump(asdict(self), f)
