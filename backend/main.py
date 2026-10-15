"""FastAPI control plane for the Campus Customs agent desk."""

import json
import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

try:
    from .team import handle_ticket
except ImportError:  # supports: uvicorn main:app from backend/
    from team import handle_ticket


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SEED_DB = DATA / "campus_customs.db"
WORKING_DB = DATA / "campus_customs_new.db"
AUDIT = ROOT / "output" / "audit_trail.json"

app = FastAPI(title="Campus Customs Agent Desk")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ApprovalRequest(BaseModel):
    ticket_id: int = Field(ge=1)
    amount: float = Field(gt=0)
    approved_by: str = Field(min_length=1)
    kind: str = Field(min_length=1, description="pay or purchase")


def connect() -> sqlite3.Connection:
    connection = sqlite3.connect(WORKING_DB)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def read_events() -> list[dict[str, Any]]:
    if not AUDIT.exists():
        return []
    try:
        value = json.loads(AUDIT.read_text())
    except json.JSONDecodeError:
        return []
    return value if isinstance(value, list) else []


@app.get("/tickets")
def list_tickets(status: str | None = None) -> list[dict[str, Any]]:
    """List tickets, optionally filtered to open or resolved status."""
    if status not in (None, "open", "resolved"):
        raise HTTPException(400, "status must be open or resolved")
    query = "SELECT * FROM tickets"
    params: tuple[Any, ...] = ()
    if status:
        query += " WHERE status = ?"
        params = (status,)
    query += " ORDER BY id"
    with connect() as db:
        return [dict(row) for row in db.execute(query, params).fetchall()]


@app.post("/tickets/{ticket_id}/run")
async def run_ticket(ticket_id: int) -> dict[str, Any]:
    """Run the agent team; agents prepare recommendations but do not change cash."""
    with connect() as db:
        if db.execute("SELECT 1 FROM tickets WHERE id = ?", (ticket_id,)).fetchone() is None:
            raise HTTPException(404, "ticket not found")
    result = await handle_ticket(ticket_id, f"Review ticket {ticket_id} and prepare a safe, evidence-based recommendation.")
    with connect() as db:
        db.execute("UPDATE tickets SET status = 'resolved' WHERE id = ?", (ticket_id,))
    return result.model_dump(mode="json")


@app.get("/agent-events")
def recent_agent_events(limit: int = 50) -> list[dict[str, Any]]:
    """Return recent persistent agent messages, delegation events, and MCP tool events."""
    if limit < 1 or limit > 500:
        raise HTTPException(400, "limit must be between 1 and 500")
    return read_events()[-limit:]


@app.post("/approvals")
def approve_payment(request: ApprovalRequest) -> dict[str, Any]:
    """Human approval boundary: the only route allowed to change cash."""
    if request.kind not in {"pay", "purchase"}:
        raise HTTPException(400, "kind must be pay or purchase")
    with connect() as db:
        ticket = db.execute("SELECT * FROM tickets WHERE id = ?", (request.ticket_id,)).fetchone()
        if ticket is None:
            raise HTTPException(404, "ticket not found")
        account = db.execute("SELECT * FROM cash_accounts WHERE name = 'checking'").fetchone()
        if account is None or account["balance"] < request.amount:
            raise HTTPException(409, "insufficient checking balance")
        paid_at = datetime.now(timezone.utc).isoformat()
        cursor = db.execute(
            "INSERT INTO payments(kind, ref_id, amount, account, paid_at, approved_by) VALUES (?, ?, ?, 'checking', ?, ?)",
            (request.kind, request.ticket_id, request.amount, paid_at, request.approved_by),
        )
        db.execute("UPDATE cash_accounts SET balance = balance - ?, date = ? WHERE name = 'checking'", (request.amount, paid_at[:10]))
        db.execute("UPDATE tickets SET status = 'resolved' WHERE id = ?", (request.ticket_id,))
        result = {"payment_id": cursor.lastrowid, "ticket_id": request.ticket_id, "amount": request.amount, "approved_by": request.approved_by, "status": "approved"}
    return result


@app.get("/cash/checking")
def checking_balance() -> dict[str, Any]:
    with connect() as db:
        row = db.execute("SELECT name, balance, date FROM cash_accounts WHERE name = 'checking'").fetchone()
    if row is None:
        raise HTTPException(404, "checking account not found")
    return dict(row)


@app.post("/reset")
def reset_database() -> dict[str, str]:
    """Restore the working DB from the untouched seed; does not erase the audit trail."""
    shutil.copy2(SEED_DB, WORKING_DB)
    return {"status": "reset", "database": str(WORKING_DB), "audit_trail": "preserved"}
