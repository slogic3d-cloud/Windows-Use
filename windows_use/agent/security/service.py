import asyncio
import uuid
from typing import Awaitable, Callable

from windows_use.agent.desktop.service import Desktop
from windows_use.agent.registry.service import Registry
from windows_use.agent.registry.views import ToolResult
from windows_use.agent.security.views import TOOL_TIERS, Tier
from windows_use.agent.tools import Tool

ConfirmCallback = Callable[[str, str, dict], Awaitable[bool]]


async def _cli_confirm(req_id: str, tool_name: str, tool_params: dict) -> bool:
    print(f"\n[ZERO SICHERHEIT – ROT] Tool: {tool_name}")
    print(f"Parameter: {tool_params}")
    answer = input("Bestätigen? (ja/nein): ").strip().lower()
    return answer in ("ja", "j", "yes", "y")


class SecurityRegistry(Registry):
    """Drop-in-Ersatz für Registry mit Tier-Prüfung und Kryptonit-Abbruch."""

    def __init__(
        self,
        tools: list[Tool],
        confirmation_callback: ConfirmCallback | None = None,
    ):
        super().__init__(tools)
        self._stop = False
        self._confirmation_callback: ConfirmCallback = confirmation_callback or _cli_confirm

    def kryptonit(self) -> None:
        """Setzt Stop-Flag — nächstes Tool wird sofort abgebrochen."""
        self._stop = True

    def reset(self) -> None:
        """Erlaubt Ausführung wieder (für neue Aufgabe)."""
        self._stop = False

    def get_tier(self, tool_name: str) -> Tier:
        return TOOL_TIERS.get(tool_name, Tier.YELLOW)

    def execute(
        self, tool_name: str, tool_params: dict, desktop: Desktop | None = None
    ) -> ToolResult:
        if self._stop:
            return ToolResult(
                is_success=False,
                error="[KRYPTONIT] Sofort-Abbruch aktiviert. Alle weiteren Aktionen gestoppt.",
            )
        tier = self.get_tier(tool_name)
        if tier == Tier.RED:
            req_id = str(uuid.uuid4())[:8]
            try:
                loop = asyncio.get_running_loop()
                # Wenn wir in einem laufenden Event-Loop sind: BlockingIOError vermeiden
                confirmed = loop.run_until_complete(
                    self._confirmation_callback(req_id, tool_name, tool_params)
                )
            except RuntimeError:
                confirmed = asyncio.run(
                    self._confirmation_callback(req_id, tool_name, tool_params)
                )
            if not confirmed:
                return ToolResult(
                    is_success=False,
                    error=f"[SICHERHEIT] '{tool_name}' wurde nicht bestätigt und abgebrochen.",
                )
        return super().execute(tool_name, tool_params, desktop)

    async def aexecute(
        self, tool_name: str, tool_params: dict, desktop: Desktop | None = None
    ) -> ToolResult:
        if self._stop:
            return ToolResult(
                is_success=False,
                error="[KRYPTONIT] Sofort-Abbruch aktiviert. Alle weiteren Aktionen gestoppt.",
            )
        tier = self.get_tier(tool_name)
        if tier == Tier.RED:
            req_id = str(uuid.uuid4())[:8]
            confirmed = await self._confirmation_callback(req_id, tool_name, tool_params)
            if not confirmed:
                return ToolResult(
                    is_success=False,
                    error=f"[SICHERHEIT] '{tool_name}' wurde nicht bestätigt und abgebrochen.",
                )
        return await super().aexecute(tool_name, tool_params, desktop)
