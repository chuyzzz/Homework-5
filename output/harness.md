# HW 5 Harness Notes

## Working database

The working copy is `data/campus_customs_new.db`, copied from `data/campus_customs.db` before later problems modify it.

## Tables and fields

### `desk`

Fields: `date_today` (TEXT, required), `notes` (TEXT).

Why it matters: Gives agents the current operating date and shared operational notes for time-sensitive decisions.

### `inventory`

Fields: `sku` (TEXT, required; composite primary key with `size`), `name` (TEXT, required), `size` (TEXT, required), `qty` (INTEGER, required), `location` (TEXT, required).

Why it matters: Lets agents check product availability, requested size, quantity, and picking location.

### `pricing`

Fields: `sku` (TEXT, primary key), `unit_cost` (REAL, required), `list_price` (REAL, required).

Why it matters: Supports margin checks and pricing or discount decisions.

### `vendors`

Fields: `id` (INTEGER, primary key), `name` (TEXT, required), `specialty` (TEXT, required), `lead_days` (INTEGER, required).

Why it matters: Helps agents select vendors and estimate replenishment timing.

### `leases`

Fields: `id` (INTEGER, primary key), `space_name` (TEXT, required), `landlord` (TEXT, required), `monthly_rent` (REAL, required), `next_due` (TEXT, required), `notes` (TEXT).

Why it matters: Provides the rent obligation and due date needed for lease and payment workflows.

### `cash_accounts`

Fields: `name` (TEXT, primary key), `balance` (REAL, required), `date` (TEXT, required).

Why it matters: Shows available cash and its as-of date before agents approve payments.

### `payments`

Fields: `id` (INTEGER, primary key), `kind` (TEXT, required), `ref_id` (INTEGER), `amount` (REAL, required), `account` (TEXT, required), `paid_at` (TEXT, required), `approved_by` (TEXT, required).

Why it matters: Records payment actions and their approval trail for auditability.

### `invoices`

Fields: `id` (INTEGER, primary key), `vendor_id` (INTEGER, required; foreign key to `vendors.id`), `amount` (REAL, required), `due_date` (TEXT, required), `status` (TEXT, required), `description` (TEXT).

Why it matters: Tracks vendor bills, deadlines, and payment status for finance agents.

### `tickets`

Fields: `id` (INTEGER, primary key), `type` (TEXT, required), `requester` (TEXT, required), `subject` (TEXT, required), `sku` (TEXT), `size` (TEXT), `qty` (INTEGER), `lease_id` (INTEGER; foreign key to `leases.id`), `invoice_id` (INTEGER; foreign key to `invoices.id`), `status` (TEXT, required), `notes` (TEXT), `created_at` (TEXT, required).

Why it matters: Serves as the agent work queue and connects customer, rent, and pricing requests to operational records.

## Three open tickets and relationships

- Ticket `101` (`customer_order`): requests one `CC-TEE-WHITE` in size `S`. Its `invoice_id = 501` links to invoice `501`, whose `vendor_id = 1` links to vendor `Bulldog Print Co`. The requested inventory row currently has quantity `0`; the invoice description is a rush reprint for that SKU and size.
- Ticket `102` (`rent_notice`): concerns shop rent and has `lease_id = 1`, linking to the Chapel Street shop lease with Elm City Properties, monthly rent `$2,400`, due `2026-09-02`.
- Ticket `103` (`price_override`): requests a bulk discount for `20` `CC-HOOD-NAVY` hoodies in size `M`. It has no direct lease or invoice link; agents must join the SKU to `inventory` (8 currently available) and `pricing` (unit cost `$22`, list price `$58`) to evaluate the request.

## MCP tools

- `get_customer_order_context(ticket_id)`: reads `tickets`, `inventory`, `invoices`, and `vendors`. It unlocks ticket `101` by showing whether the requested Bulldog tee is in stock and connecting the out-of-stock request to the rush reprint invoice and its vendor lead time.
- `get_rent_notice_context(ticket_id)`: reads `tickets`, `leases`, and `cash_accounts`. It unlocks ticket `102` by combining the rent notice’s linked lease due date and amount with the checking balance needed to assess the payment.
- `get_bulk_discount_context(ticket_id)`: reads `tickets`, `inventory`, and `pricing`. It unlocks ticket `103` by comparing the requested 20 hoodies with the available size-M quantity and the SKU’s cost and list price before a discount decision.

## Agent team

- **Boss** coordinates the queue, delegates to all specialists, reconciles their evidence, and escalates decisions requiring approval.
- **Inventory** handles SKU, size, quantity, location, and replenishment evidence.
- **Accounting** handles invoices, rent amounts, costs, prices, balances, due dates, and payment-risk review.
- **Facilities** handles leases, landlord requests, shop space, and rent timing.
- **Customer Service** turns verified evidence into safe customer-facing recommendations for orders and bulk requests.

Every shop-data lookup is routed through the MCP client to the three named MCP tools above. The agents do not open SQLite or use a parallel database-tools layer.

## Safety and token guardrails

Agents may recommend actions but may not promise stock or delivery, approve discounts, issue refunds, authorize payments, change balances, alter leases, contact real customers or vendors, or mark a ticket resolved without human approval. Customer-facing drafts must use only verified ticket facts and must avoid unnecessary private information. Conflicting, missing, or stale data is escalated rather than guessed.

Each agent run is bounded by the PydanticAI model’s configured request/tool loop limits, and prompts require concise outputs. The implementation records every agent start, MCP lookup, and agent result in `output/audit_trail.json`; the append-only logger preserves prior runs instead of wiping the file.

## FastAPI routes

- `GET /tickets?status=open|resolved`: lists tickets, optionally filtered by status.
- `POST /tickets/{ticket_id}/run`: runs the agent team for a ticket; agents prepare a recommendation only.
- `GET /agent-events?limit=50`: returns recent persistent agent messages, delegation events, and MCP tool events.
- `POST /approvals`: human approval route that records a payment, decreases checking cash, and resolves the ticket; agents cannot call this route.
- `GET /cash/checking`: returns the current checking balance and as-of date.
- `POST /reset`: restores `campus_customs_new.db` from the seed database while preserving `audit_trail.json`.

Start from `backend/` with `uvicorn main:app --reload --port 8000`.
