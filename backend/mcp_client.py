from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncIterator

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


SERVER = Path(__file__).resolve().parents[1] / "mcp_server" / "server.py"
PYTHON = Path(__file__).resolve().parents[1] / ".venv" / "bin" / "python"


class CampusMCP:
    """The only data boundary used by the agents: every shop lookup is an MCP call."""

    def __init__(self) -> None:
        self.parameters = StdioServerParameters(command=str(PYTHON), args=[str(SERVER)])
        self._stdio = None
        self._session = None

    async def __aenter__(self) -> "CampusMCP":
        self._stdio = stdio_client(self.parameters)
        read_write = await self._stdio.__aenter__()
        self._session = ClientSession(*read_write)
        await self._session.__aenter__()
        await self._session.initialize()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._session is not None:
            await self._session.__aexit__(exc_type, exc, tb)
        if self._stdio is not None:
            await self._stdio.__aexit__(exc_type, exc, tb)

    async def call(self, tool_name: str, ticket_id: int) -> dict[str, Any]:
        if self._session is None:
            raise RuntimeError("CampusMCP must be used as an async context manager.")
        result = await self._session.call_tool(tool_name, {"ticket_id": ticket_id})
        if result.isError:
            raise RuntimeError(str(result.content))
        return result.structuredContent or {}
