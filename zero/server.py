"""ZERO 2.0 — FastAPI WebSocket-Server.

Start: uvicorn zero.server:app --host 0.0.0.0 --port 8765 --reload
oder:  python -m zero.server
"""

from __future__ import annotations

import asyncio
import json
import uuid
from pathlib import Path
from typing import Any

try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect
    from fastapi.responses import FileResponse, HTMLResponse
    from fastapi.staticfiles import StaticFiles
except ImportError:
    raise ImportError("Bitte installieren: pip install fastapi uvicorn")

from windows_use.agent.events.obsidian import ObsidianEventSubscriber
from windows_use.agent.events.views import AgentEvent, EventType
from windows_use.agent.security.service import SecurityRegistry
from windows_use.agent.tools import BUILTIN_TOOLS, EXPERIMENTAL_TOOLS
from windows_use.agent.tools.mcp_tools import MCP_TOOLS
from windows_use.providers.anthropic import ChatAnthropic
from zero.config import ZeroConfig

DOWNLOADS_DIR = Path("zero_downloads")
DOWNLOADS_DIR.mkdir(exist_ok=True)
FRONTEND_PATH = Path("frontend/zero_ui.html")

app = FastAPI(title="ZERO 2.0", version="2.0.0")

# Statische Downloads bereitstellen
app.mount("/download", StaticFiles(directory=str(DOWNLOADS_DIR)), name="downloads")

cfg = ZeroConfig.from_env()


# ─── Bestätigungs-Manager (für ROT-Tier Tools) ───────────────────────────────


class ConfirmationManager:
    def __init__(self) -> None:
        self._pending: dict[str, asyncio.Future] = {}

    async def request(
        self, ws: WebSocket, req_id: str, tool_name: str, params: dict
    ) -> bool:
        loop = asyncio.get_running_loop()
        future: asyncio.Future = loop.create_future()
        self._pending[req_id] = future
        await ws.send_json(
            {
                "type": "confirmation_request",
                "data": {
                    "id": req_id,
                    "tool_name": tool_name,
                    "params": params,
                    "message": (
                        f"⚠️ ROT-TIER Aktion: '{tool_name}' wird ausgeführt. "
                        "Bestätigen?"
                    ),
                },
            }
        )
        try:
            return await asyncio.wait_for(future, timeout=60)
        except asyncio.TimeoutError:
            self._pending.pop(req_id, None)
            return False

    def resolve(self, req_id: str, confirmed: bool) -> None:
        future = self._pending.pop(req_id, None)
        if future and not future.done():
            future.set_result(confirmed)


# ─── WebSocket-Endpoint ───────────────────────────────────────────────────────


@app.get("/")
async def root():
    if FRONTEND_PATH.exists():
        return HTMLResponse(FRONTEND_PATH.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>ZERO 2.0 Server läuft</h1><p>Frontend nicht gefunden.</p>")


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    confirm_mgr = ConfirmationManager()
    agent_task: asyncio.Task | None = None
    security_registry: SecurityRegistry | None = None

    # Initialmeldung an Client
    await ws.send_json(
        {
            "type": "system",
            "data": {
                "status": "online",
                "message": "ZERO 2.0 bereit.",
                "model": cfg.anthropic_model,
            },
        }
    )

    async def emit_to_ws(event: AgentEvent) -> None:
        """Event-Subscriber: leitet alle Agent-Events zum WebSocket."""
        data: dict[str, Any] = dict(event.data)
        # Download-Link erkennen
        content = data.get("content", "") or ""
        if "/download/" in content:
            for part in content.split():
                if part.startswith("/download/"):
                    fname = part.split("/")[-1]
                    await ws.send_json(
                        {
                            "type": "file",
                            "data": {
                                "url": part,
                                "name": fname,
                                "message": f"Datei bereit: {fname}",
                            },
                        }
                    )
        await ws.send_json({"type": event.type.value, "data": data})

    async def run_agent(task: str) -> None:
        nonlocal security_registry
        from windows_use.agent.service import Agent

        # Bestätigungs-Callback für ROT-Tier
        async def ws_confirm(req_id: str, tool_name: str, params: dict) -> bool:
            return await confirm_mgr.request(ws, req_id, tool_name, params)

        all_tools = BUILTIN_TOOLS + EXPERIMENTAL_TOOLS + MCP_TOOLS
        security_registry = SecurityRegistry(
            tools=all_tools,
            confirmation_callback=ws_confirm,
        )

        llm = ChatAnthropic(
            model=cfg.anthropic_model,
            api_key=cfg.anthropic_api_key,
        )

        # Obsidian-Subscriber wenn Vault konfiguriert
        obsidian_sub = None
        if cfg.obsidian_vault_path:
            obsidian_sub = ObsidianEventSubscriber(
                vault_path=cfg.obsidian_vault_path,
                task_hint=task[:40],
            )

        agent = Agent(
            llm=llm,
            max_steps=cfg.max_steps,
            use_vision=cfg.use_vision,
            experimental=cfg.experimental_tools,
            secrets=cfg.secrets(),
            event_subscriber=emit_to_ws,
            log_to_console=True,
        )
        # SecurityRegistry injizieren
        agent.registry = security_registry

        # Obsidian-Subscriber hinzufügen
        if obsidian_sub:
            agent.event.add_subscriber(obsidian_sub)

        await agent.ainvoke(task)

    try:
        while True:
            raw = await ws.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue

            msg_type = msg.get("type", "")
            data = msg.get("data", {})

            if msg_type == "task":
                content = data.get("content", "").strip()
                if not content:
                    continue

                # Kryptonit-Erkennung
                if "kryptonit" in content.lower():
                    if security_registry:
                        security_registry.kryptonit()
                    if agent_task and not agent_task.done():
                        agent_task.cancel()
                    await ws.send_json(
                        {
                            "type": "kryptonit",
                            "data": {
                                "message": "🛑 KRYPTONIT aktiviert — alle Aktionen gestoppt."
                            },
                        }
                    )
                    continue

                # Laufenden Task abbrechen falls vorhanden
                if agent_task and not agent_task.done():
                    agent_task.cancel()
                if security_registry:
                    security_registry.reset()

                agent_task = asyncio.create_task(run_agent(content))

            elif msg_type == "kryptonit":
                if security_registry:
                    security_registry.kryptonit()
                if agent_task and not agent_task.done():
                    agent_task.cancel()
                await ws.send_json(
                    {
                        "type": "kryptonit",
                        "data": {"message": "🛑 KRYPTONIT aktiviert — alle Aktionen gestoppt."},
                    }
                )

            elif msg_type == "confirmation_response":
                req_id = data.get("id", "")
                confirmed = bool(data.get("confirmed", False))
                confirm_mgr.resolve(req_id, confirmed)

            elif msg_type == "ping":
                await ws.send_json({"type": "pong", "data": {}})

    except WebSocketDisconnect:
        if agent_task and not agent_task.done():
            agent_task.cancel()
    except Exception as e:
        try:
            await ws.send_json({"type": "error", "data": {"error": str(e)}})
        except Exception:
            pass


# ─── Standalone-Start ─────────────────────────────────────────────────────────


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "zero.server:app",
        host=cfg.host,
        port=cfg.port,
        reload=False,
        log_level="info",
    )
