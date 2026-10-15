"""Read-only FastMCP tools for the Campus Customs ticket queue."""

from pathlib import Path
import sqlite3
from typing import Any

from mcp.server.fastmcp import FastMCP


DB_PATH = Path(__file__).resolve().parents[1] / "data" / "campus_customs_new.db"
mcp = FastMCP("campus-customs")


def _fetch_one(query: str, params: tuple[Any, ...]) -> dict[str, Any]:
    with sqlite3.connect(DB_PATH) as connection:
        connection.row_factory = sqlite3.Row
        row = connection.execute(query, params).fetchone()
    if row is None:
        raise ValueError("No matching record was found in campus_customs_new.db.")
    return dict(row)


@mcp.tool()
def get_customer_order_context(ticket_id: int) -> dict[str, Any]:
    """Return the ticket, requested stock, linked invoice, and vendor for a customer order."""
    return _fetch_one(
        """
        SELECT t.id AS ticket_id, t.type, t.requester, t.subject, t.sku, t.size,
               t.qty, t.status, t.notes, i.qty AS inventory_qty,
               i.location AS inventory_location, inv.id AS invoice_id,
               inv.amount AS invoice_amount, inv.due_date AS invoice_due_date,
               inv.status AS invoice_status, v.id AS vendor_id,
               v.name AS vendor_name, v.lead_days AS vendor_lead_days
        FROM tickets AS t
        LEFT JOIN inventory AS i ON i.sku = t.sku AND i.size = t.size
        LEFT JOIN invoices AS inv ON inv.id = t.invoice_id
        LEFT JOIN vendors AS v ON v.id = inv.vendor_id
        WHERE t.id = ? AND t.type = 'customer_order'
        """,
        (ticket_id,),
    )


@mcp.tool()
def get_rent_notice_context(ticket_id: int) -> dict[str, Any]:
    """Return the rent ticket, linked lease, current cash balance, and payment date context."""
    return _fetch_one(
        """
        SELECT t.id AS ticket_id, t.type, t.requester, t.subject, t.status, t.notes,
               l.id AS lease_id, l.space_name, l.landlord, l.monthly_rent,
               l.next_due, l.notes AS lease_notes, c.name AS cash_account,
               c.balance AS cash_balance, c.date AS cash_as_of
        FROM tickets AS t
        LEFT JOIN leases AS l ON l.id = t.lease_id
        LEFT JOIN cash_accounts AS c ON c.name = 'checking'
        WHERE t.id = ? AND t.type = 'rent_notice'
        """,
        (ticket_id,),
    )


@mcp.tool()
def get_bulk_discount_context(ticket_id: int) -> dict[str, Any]:
    """Return requested bulk quantity, stock, and cost/list pricing for a price override ticket."""
    return _fetch_one(
        """
        SELECT t.id AS ticket_id, t.type, t.requester, t.subject, t.sku, t.size,
               t.qty AS requested_qty, t.status, t.notes, i.name AS product_name,
               i.qty AS inventory_qty, i.location AS inventory_location,
               p.unit_cost, p.list_price
        FROM tickets AS t
        LEFT JOIN inventory AS i ON i.sku = t.sku AND i.size = t.size
        LEFT JOIN pricing AS p ON p.sku = t.sku
        WHERE t.id = ? AND t.type = 'price_override'
        """,
        (ticket_id,),
    )


if __name__ == "__main__":
    mcp.run()
