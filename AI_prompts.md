# AI prompts

The HW 5 prompt log records the requests made while completing each problem.

## Initial inspection — HW 5 materials

**Prompt typed:** “Inspect the HW 5 folder, identify the available files and database structure, and report what is present before beginning the problems.”

**Follow-up prompt:** “Check whether the HW 5 folder contains an assignment sheet or any files that identify the individual problem titles.”

The first attempt identified the database but did not establish the problem titles or requirements because the assignment materials are not present.

## Problem 1 — Vibe coder prompts

**Prompt typed:** “Help me complete Problem 1. Explain the requirements in plain language, then propose a solution using the available HW 5 files.”

**Follow-up prompt:** “Review the Problem 1 solution against every requirement and identify anything missing or unsupported.”

The first attempt was missing the official Problem 1 requirements and title because the assignment sheet was unavailable.

## Problem 2 — Study the Campus Customs database

**Prompt typed:** “Look through every table and field in `data/campus_customs.db`. Copy it to `data/campus_customs_new.db`, which is the working copy later problems change. Study how the three open tickets link to other tables. Start `output/harness.md`. For each table, list its fields and one line on why it matters to the agents.”

**Follow-up prompt:** “Check the Problem 2 result for correctness, edge cases, and compliance with the assignment.”

The first attempt was missing the database copy, the ticket relationship analysis, and the table-by-table harness documentation.

## Problem 3 — Build the MCP server

**Prompt typed:** “In `mcp_server/`, write a FastMCP server over `campus_customs_new.db` with three clearly named tools the tickets will need. Never invent data. In `harness.md`, document each tool’s source tables, ticket number, and specific reason it fits. Add a short `mcp_server/README.md` describing the purpose, database, and tools. Do not run the server yet.”

**Follow-up prompt:** “Test Problem 3 with representative inputs and list any remaining gaps.”

The first attempt was missing the concrete tool-to-ticket mappings, source-table documentation, and server README.

## Problem 4 — Add the MCP server to vibe coder and test each tool

**Prompt typed:** “Add the server to Codex and save the configuration in the project-root `.mcp.json`. Test each MCP tool and save `output/mcp_smoke.json` with the prompt, tool name, and database-matching output for every tool.”

**Follow-up prompt:** “Audit the Problem 4 solution and suggest the smallest changes needed for full compliance.”

The first attempt was missing the Codex MCP configuration and saved smoke-test evidence for all three tools.

## Problem 5 — Build the agent team and grow the MCP tools

**Prompt typed:** “Build five PydanticAI agents—Boss, Inventory, Accounting, Facilities, and Customer Service—with full delegation. Put one detailed prompt per agent in `backend/prompts/`, types in `backend/models.py`, and agent code under `backend/`. Use `PORTKEY_API_KEY` with only `gpt-6-luna`. Route all shop data through MCP, append every agent-loop step to `output/audit_trail.json` without wiping prior runs, and document the agents, tools, safety guardrails, and token limits in `harness.md`.”

**Follow-up prompt:** “Explain how to verify the Problem 5 result and what evidence should be submitted.”

The first attempt was missing the five-agent delegation graph, persistent loop audit events, and explicit real-customer and money guardrails.

## Problem 6 — Plan the three tickets

**Prompt typed:** “Build `output/desk_tickets.html` with tabs for tickets 101, 102, and 103, plus empty Cash and Reflection tabs. For each ticket, fill only Expected with the first Boss call and why, every expected delegation, and the expected MCP tools. Leave room for Actual.”

**Follow-up prompt:** “Compare the Problem 6 result with the assignment requirements and identify unsupported claims.”

The first attempt was missing the ticket-specific delegation sequences, MCP-tool expectations, and blank Actual areas.

## Problem 7 — Backend routes

**Prompt typed:** “In `backend/main.py` using FastAPI, add routes to list open/resolved tickets, run the agent team for a ticket, return recent agent messages and tools, approve a pay or purchase only after a human clicks approve, return the checking balance, and reset the working database. Agents may prepare payments but only the approval route changes cash. Start it from `backend/` with `uvicorn main:app --reload --port 8000`, and list every route in `harness.md`.”

**Follow-up prompt:** “Try both a normal case and a failure case for Problem 7, then report the results.”

The first attempt was missing explicit human approval as the only cash-changing boundary, persistent event retrieval, and a documented route list.

## Problem 8 — Agent dashboard

**Prompt typed:** “Help me finish Problem 8 using the project’s conventions and explain how the implementation meets each requirement.”

**Follow-up prompt:** “Review Problem 8 for missing requirements, incorrect results, and evidence that would not prove completion.”

The first attempt was missing a requirement-by-requirement audit of Problem 8.

## Problem 9 — Resolve the tickets

**Prompt typed:** “Complete Problem 9 and make the final behavior easy to demonstrate from a clean run.”

**Follow-up prompt:** “Describe the clean-run verification procedure and the exact outputs to capture for Problem 9.”

The first attempt was missing a reproducible verification procedure and evidence checklist.

## Problem 10 — Reflection

**Prompt typed:** “Fill the Reflection tab in `output/desk_tickets.html` in detail: evaluate the agents on tickets 101, 102, and 103; compare Actual with Expected; explain what would be simpler as one agent with tools; give three new problems the team could solve and three it could not, including the tools or agents needed. Tie every answer to the three tickets and the Cash tab, and do not invent live-run results.”

**Follow-up prompt:** “Visualize Expected versus Actual in `desk_tickets.html` with row-by-row tables showing what is resolved, what is not, and the Cash impact for tickets 101, 102, and 103.”

**Additional prompt:** “Generate the Cash tab with the current checking balance, each ticket’s cash impact, and a clear explanation that only human approval can change the balance.”

The first attempt was missing ticket-specific evaluation criteria, an honest Actual-versus-Expected comparison, and explicit Cash-tab consequences.
