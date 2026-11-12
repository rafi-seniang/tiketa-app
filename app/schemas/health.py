"""What the service says about itself."""

from pydantic import BaseModel


class ServiceMeta(BaseModel):
    id: str
    name: str
    summary: str
    version: str
    docs_path: str
    mcp_path: str | None  # None when the MCP server is turned off
