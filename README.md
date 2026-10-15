# Campus Customs — HW 5

Campus Customs is a five-agent operations desk backed by a read-only FastMCP server, a FastAPI control plane, and a React/Vite dashboard. The agents use `gpt-6-luna` through Portkey and read shop data through MCP.

## Setup

```bash
cp .env.example .env
python -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Set `PORTKEY_API_KEY` in `.env` before running the agent team. Never commit `.env`.

## Database

The seed database is `data/campus_customs.db`; later work uses `data/campus_customs_new.db`. To reset the working database:

```bash
cp data/campus_customs.db data/campus_customs_new.db
```

Both database files are included in this submission.

## Start the MCP server

From the repository root:

```bash
.venv/bin/python mcp_server/server.py
```

Codex can load the same server from `.mcp.json`. The MCP server is read-only and exposes the three ticket-context tools in `mcp_server/README.md`.

## Start the backend

```bash
cd backend
../.venv/bin/uvicorn main:app --reload --port 8000
```

The API lists tickets, runs the agent team, streams audit events, exposes the checking balance, resets the working DB, and provides the human-only approval route that can change cash.

## Start the board

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The board talks to `http://localhost:8000`; the backend allows the Vite origin. The static planning and resolution views are in `output/desk_tickets.html` and `output/resolved_board.html`.

## Evidence

- `output/harness.md` documents the schema, MCP tools, agent team, safety controls, and routes.
- `output/mcp_smoke.json` records the three MCP smoke tests.
- `output/audit_trail.json` preserves agent starts, MCP lookups, and results across runs.
- `output/resolved_tickets.json` records the resolved ticket snapshot used by the resolution board.
