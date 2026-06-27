import json
from datetime import datetime
from pathlib import Path

from windows_use.agent.events.subscriber import BaseEventSubscriber
from windows_use.agent.events.views import AgentEvent, EventType


class ObsidianEventSubscriber(BaseEventSubscriber):
    """Schreibt jeden Agenten-Schritt als Markdown in einen Obsidian-Vault-Ordner.

    Ordnerstruktur: {vault_path}/ZERO-2.0/YYYY-MM-DD/HH-MM-SS_session.md
    """

    def __init__(self, vault_path: str, task_hint: str = "session") -> None:
        self._vault = Path(vault_path)
        self._task_hint = task_hint[:30].replace("/", "-").replace(" ", "_")
        now = datetime.now()
        day_folder = self._vault / "ZERO-2.0" / now.strftime("%Y-%m-%d")
        day_folder.mkdir(parents=True, exist_ok=True)
        ts = now.strftime("%H-%M-%S")
        self._log_path = day_folder / f"{ts}_{self._task_hint}.md"
        self._write_header(now)
        self._step = 0

    def _write_header(self, now: datetime) -> None:
        header = (
            f"# ZERO 2.0 — Session {now.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"**Aufgabe:** {self._task_hint}\n\n---\n\n"
        )
        self._log_path.write_text(header, encoding="utf-8")

    def _append(self, text: str) -> None:
        with self._log_path.open("a", encoding="utf-8") as f:
            f.write(text)

    def invoke(self, event: AgentEvent) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        data = event.data

        match event.type:
            case EventType.THOUGHT:
                self._step = data.get("step", self._step)
                thought = data.get("thought", "")
                self._append(
                    f"## Schritt {self._step} | GEDANKE | {ts}\n\n"
                    f"> {thought}\n\n"
                )
            case EventType.TOOL_CALL:
                tool = data.get("tool_name", "?")
                params = dict(data.get("tool_params", {}))
                params.pop("thought", None)
                self._append(
                    f"### Tool-Aufruf: `{tool}`\n\n"
                    f"```json\n{json.dumps(params, ensure_ascii=False, indent=2)}\n```\n\n"
                )
            case EventType.TOOL_RESULT:
                tool = data.get("tool_name", "?")
                ok = data.get("is_success", False)
                content = data.get("content") or data.get("error", "")
                icon = "✅" if ok else "❌"
                self._append(
                    f"**Ergebnis** {icon} `{tool}`\n\n"
                    f"```\n{content}\n```\n\n"
                )
            case EventType.DONE:
                content = data.get("content", "")
                self._append(
                    f"---\n\n## ✅ Abgeschlossen | {ts}\n\n{content}\n\n"
                )
            case EventType.ERROR:
                error = data.get("error", "")
                self._append(
                    f"---\n\n## ❌ Fehler | {ts}\n\n```\n{error}\n```\n\n"
                )
