import json
from pathlib import Path
from typing import Any

try:
    from .models import AgentName, AuditEvent
except ImportError:  # supports: uvicorn main:app from backend/
    from models import AgentName, AuditEvent


def append_audit(
    path: str | Path,
    run_id: str,
    step: int,
    agent: AgentName,
    event: str,
    ticket_id: int | None = None,
    detail: str = "",
    output: dict[str, Any] | None = None,
) -> None:
    """Append one event; never truncate the audit trail between runs."""
    audit_path = Path(path)
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        events = json.loads(audit_path.read_text()) if audit_path.exists() else []
    except json.JSONDecodeError:
        events = []
    if not isinstance(events, list):
        events = []
    events.append(AuditEvent(
        run_id=run_id, step=step, agent=agent, event=event,
        ticket_id=ticket_id, detail=detail, output=output or {},
    ).model_dump(mode="json"))
    audit_path.write_text(json.dumps(events, indent=2) + "\n")
