# Campus Customs MCP server

This is the read-only FastMCP data boundary for the Campus Customs agent team. It uses `../data/campus_customs_new.db`, the working copy created from the original database. The five PydanticAI agents access shop data through this server; they do not open SQLite directly or use a parallel tools layer.

## Tools

- `get_customer_order_context(ticket_id)`: joins a customer-order ticket to its requested SKU/size inventory, linked invoice, and vendor lead time. This supports Inventory, Accounting, and Customer Service with ticket 101.
- `get_rent_notice_context(ticket_id)`: joins a rent-notice ticket to its lease and current checking-account balance. This supports Facilities and Accounting with ticket 102.
- `get_bulk_discount_context(ticket_id)`: joins a price-override ticket to its requested inventory row and SKU cost/list pricing. This supports Inventory, Accounting, and Customer Service with ticket 103.

All tools accept a `ticket_id`, enforce the expected ticket type in SQL, and return only fields present in the database. A missing match raises an error rather than inventing data. The server never writes to the database or authorizes money, discounts, customer promises, or ticket resolution.

## Codex configuration

The project-root `.mcp.json` registers this server as `campus-customs` and starts it with the HW 5 virtual-environment Python interpreter. Install dependencies from `backend/requirements.txt` before using the server.

## Running locally

From this directory, run `python server.py` after installing the MCP dependency. The agent client in `backend/mcp_client.py` starts the server over stdio and calls the tools by name. Smoke-test prompts and database-matching outputs are recorded in `../output/mcp_smoke.json`.
