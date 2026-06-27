"""ZERO 2.0 — Konfiguration.

Alle Werte können als Umgebungsvariablen oder direkt hier gesetzt werden.
"""

from dataclasses import dataclass, field
import os


@dataclass
class ZeroConfig:
    # LLM
    anthropic_api_key: str = field(
        default_factory=lambda: os.environ.get("ANTHROPIC_API_KEY", "")
    )
    anthropic_model: str = "claude-opus-4-8"

    # TTS / STT
    elevenlabs_api_key: str = field(
        default_factory=lambda: os.environ.get("ELEVENLABS_API_KEY", "")
    )
    elevenlabs_voice_id: str = "MMwckqU477oQxnAk1SgA"  # Deine persönliche Stimme

    # Gmail
    gmail_access_token: str = field(
        default_factory=lambda: os.environ.get("GMAIL_ACCESS_TOKEN", "")
    )

    # Wix S-LOGIC 3D Shop
    wix_api_key: str = field(default_factory=lambda: os.environ.get("WIX_API_KEY", ""))
    wix_account_id: str = field(
        default_factory=lambda: os.environ.get("WIX_ACCOUNT_ID", "")
    )
    wix_site_id: str = field(default_factory=lambda: os.environ.get("WIX_SITE_ID", ""))

    # Obsidian Vault (leer = kein Logging)
    obsidian_vault_path: str = field(
        default_factory=lambda: os.environ.get("OBSIDIAN_VAULT_PATH", "")
    )

    # Server
    host: str = "0.0.0.0"
    port: int = 8765

    # Agent
    max_steps: int = 25
    use_vision: bool = False
    experimental_tools: bool = True

    def secrets(self) -> dict:
        """Erstellt das secrets-Dict für den Agent."""
        return {
            "gmail_token": self.gmail_access_token,
            "wix_api_key": self.wix_api_key,
            "wix_account_id": self.wix_account_id,
            "wix_site_id": self.wix_site_id,
        }

    @classmethod
    def from_env(cls) -> "ZeroConfig":
        return cls()
