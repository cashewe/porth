from fastapi import FastAPI
from fastmcp import FastMCP


def generate_mcp_tools(app: FastAPI) -> None:
    """Setup the MCP toolset."""
    mcp = FastMCP.from_fastapi(app=app)
    mcp.enable(tags={"mcp"}, only=True)  # dont expose all the health routes etc...
