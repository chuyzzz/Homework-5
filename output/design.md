# Frontend design

The frontend is a compact operations dashboard rather than a generic admin table. A two-column layout keeps the ticket queue visible beside the selected ticket’s activity and controls, so an operator can move from context to action without losing the thread.

The navy balance card gives the financial state a strong visual anchor, while the warm approval panel separates the human money gate from agent activity. Blue is reserved for active controls and navigation; green indicates resolved or successfully completed work; amber signals pending attention. This makes safety state legible at a glance.

The activity stream is intentionally chronological and lightweight. It polls `/agent-events` while a ticket is selected so delegation and MCP events can appear without a page reload. The summary card separates the final agent recommendation from raw activity, and the approval form makes the human name and amount explicit.

The layout uses responsive CSS: the queue and workspace become a single column on smaller screens, while ticket controls remain usable with large touch targets. The frontend points directly to `http://localhost:8000` and expects the Vite dev server at `http://localhost:5173`.
