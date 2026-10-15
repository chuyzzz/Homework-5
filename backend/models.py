from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class AgentName(StrEnum):
    BOSS = "Boss"
    INVENTORY = "Inventory"
    ACCOUNTING = "Accounting"
    FACILITIES = "Facilities"
    CUSTOMER_SERVICE = "Customer Service"


class DelegationRequest(BaseModel):
    ticket_id: int = Field(ge=1)
    objective: str = Field(min_length=1)


class AgentResult(BaseModel):
    agent: AgentName
    ticket_id: int
    summary: str
    facts: dict[str, Any] = Field(default_factory=dict)
    next_action: str = "No action authorized."
    requires_human_approval: bool = True


class AuditEvent(BaseModel):
    run_id: str
    step: int
    agent: AgentName
    event: str
    ticket_id: int | None = None
    detail: str = ""
    output: dict[str, Any] = Field(default_factory=dict)


@dataclass
class TeamContext:
    run_id: str
    audit_path: str
    mcp: Any
    step: int = 0
    seen_agents: list[AgentName] = field(default_factory=list)
