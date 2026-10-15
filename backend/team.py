import os
from pathlib import Path
from typing import Any, Awaitable, Callable
from uuid import uuid4

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.providers.openai import OpenAIProvider

try:
    from .audit import append_audit
    from .mcp_client import CampusMCP
    from .models import AgentName, AgentResult, DelegationRequest, TeamContext
except ImportError:  # supports: uvicorn main:app from backend/
    from audit import append_audit
    from mcp_client import CampusMCP
    from models import AgentName, AgentResult, DelegationRequest, TeamContext


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "output" / "audit_trail.json"
PROMPTS = ROOT / "backend" / "prompts"


def _model() -> OpenAIResponsesModel:
    key = os.environ["PORTKEY_API_KEY"]
    return OpenAIResponsesModel(
        "gpt-6-luna",
        provider=OpenAIProvider(base_url="https://api.portkey.ai/v1", api_key=key),
    )


def _instructions(agent: AgentName) -> str:
    return (PROMPTS / f"{agent.value.lower().replace(' ', '_')}.md").read_text()


def _agent(agent: AgentName) -> Agent[TeamContext, AgentResult]:
    return Agent(
        _model(),
        deps_type=TeamContext,
        output_type=AgentResult,
        instructions=_instructions(agent),
        model_settings={"reasoning_effort": "none", "max_tokens": 1200},
    )


AGENTS = {name: _agent(name) for name in AgentName}


async def _mcp_lookup(ctx: RunContext[TeamContext], tool: str, ticket_id: int) -> dict[str, Any]:
    ctx.deps.step += 1
    data = await ctx.deps.mcp.call(tool, ticket_id)
    append_audit(AUDIT_PATH, ctx.deps.run_id, ctx.deps.step, AgentName(ctx.deps.seen_agents[-1]), "mcp_lookup", ticket_id, tool, data)
    return data


def register_tools() -> None:
    @AGENTS[AgentName.INVENTORY].tool
    async def inventory_context(ctx: RunContext[TeamContext], request: DelegationRequest) -> dict[str, Any]:
        tool = {
            101: "get_customer_order_context",
            103: "get_bulk_discount_context",
        }.get(request.ticket_id, "get_customer_order_context")
        return await _mcp_lookup(ctx, tool, request.ticket_id)

    @AGENTS[AgentName.ACCOUNTING].tool
    async def accounting_context(ctx: RunContext[TeamContext], request: DelegationRequest) -> dict[str, Any]:
        tool = {
            101: "get_customer_order_context",
            102: "get_rent_notice_context",
            103: "get_bulk_discount_context",
        }.get(request.ticket_id, "get_customer_order_context")
        return await _mcp_lookup(ctx, tool, request.ticket_id)

    @AGENTS[AgentName.FACILITIES].tool
    async def facilities_context(ctx: RunContext[TeamContext], request: DelegationRequest) -> dict[str, Any]:
        return await _mcp_lookup(ctx, "get_rent_notice_context", request.ticket_id)

    @AGENTS[AgentName.CUSTOMER_SERVICE].tool
    async def customer_service_context(ctx: RunContext[TeamContext], request: DelegationRequest) -> dict[str, Any]:
        tool = {
            101: "get_customer_order_context",
            102: "get_rent_notice_context",
            103: "get_bulk_discount_context",
        }.get(request.ticket_id, "get_customer_order_context")
        return await _mcp_lookup(ctx, tool, request.ticket_id)

    for specialist in (AgentName.INVENTORY, AgentName.ACCOUNTING, AgentName.FACILITIES, AgentName.CUSTOMER_SERVICE):
        @AGENTS[specialist].tool
        async def delegate(ctx: RunContext[TeamContext], request: DelegationRequest) -> AgentResult:
            return await run_agent(AgentName.BOSS, request.ticket_id, request.objective, ctx.deps)

    @AGENTS[AgentName.BOSS].tool
    async def delegate_to_inventory(ctx: RunContext[TeamContext], request: DelegationRequest) -> AgentResult:
        return await run_agent(AgentName.INVENTORY, request.ticket_id, request.objective, ctx.deps)

    @AGENTS[AgentName.BOSS].tool
    async def delegate_to_accounting(ctx: RunContext[TeamContext], request: DelegationRequest) -> AgentResult:
        return await run_agent(AgentName.ACCOUNTING, request.ticket_id, request.objective, ctx.deps)

    @AGENTS[AgentName.BOSS].tool
    async def delegate_to_facilities(ctx: RunContext[TeamContext], request: DelegationRequest) -> AgentResult:
        return await run_agent(AgentName.FACILITIES, request.ticket_id, request.objective, ctx.deps)

    @AGENTS[AgentName.BOSS].tool
    async def delegate_to_customer_service(ctx: RunContext[TeamContext], request: DelegationRequest) -> AgentResult:
        return await run_agent(AgentName.CUSTOMER_SERVICE, request.ticket_id, request.objective, ctx.deps)


async def run_agent(agent: AgentName, ticket_id: int, objective: str, ctx: TeamContext) -> AgentResult:
    ctx.seen_agents.append(agent)
    ctx.step += 1
    append_audit(AUDIT_PATH, ctx.run_id, ctx.step, agent, "agent_start", ticket_id, objective)
    result = await AGENTS[agent].run(objective, deps=ctx)
    output = result.output
    append_audit(AUDIT_PATH, ctx.run_id, ctx.step + 1, agent, "agent_result", ticket_id, output.summary, output.model_dump(mode="json"))
    ctx.step += 1
    return output


register_tools()


async def handle_ticket(ticket_id: int, objective: str) -> AgentResult:
    async with CampusMCP() as mcp:
        context = TeamContext(run_id=str(uuid4()), audit_path=str(AUDIT_PATH), mcp=mcp)
        return await run_agent(AgentName.BOSS, ticket_id, objective, context)
