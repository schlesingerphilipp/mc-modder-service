from langchain_mcp_adapters.client import MultiServerMCPClient
import os

def getClient() -> MultiServerMCPClient:
    """Gets the MCP client to connect to the MCP server.
        Use tools = await client.get_tools() to get the tools from the server.

    Returns:
        MultiServerMCPClient: The client to connect to the MCP server.
    """
    server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8080/mcp")
    return MultiServerMCPClient(
    {
        "weather": {
            "transport": "streamable_http",  # HTTP-based remote server
            # Ensure you start your weather server on port 8000
            "url": server_url,
        }
    }
)