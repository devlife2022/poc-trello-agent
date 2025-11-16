"""
MCP client for executing tools via the FastMCP server.
Supports both STDIO (local) and HTTP (production) modes.
"""
from typing import Any, Dict, List, Optional
import logging
import httpx
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from config import settings

logger = logging.getLogger(__name__)


class MCPClient:
    """Client for interacting with the MCP server."""

    def __init__(self):
        """Initialize the MCP client."""
        self.session: Optional[ClientSession] = None
        self.tools: List[Dict[str, Any]] = []
        self._connected = False
        self._stdio_context = None
        self._http_client: Optional[httpx.AsyncClient] = None
        self._use_http = bool(settings.mcp_server_url)

    async def connect(self) -> None:
        """Connect to the MCP server."""
        if self._connected:
            return

        try:
            if self._use_http:
                # Production: Connect via HTTP
                logger.info(f"Connecting to MCP server via HTTP: {settings.mcp_server_url}")
                self._http_client = httpx.AsyncClient(base_url=settings.mcp_server_url, timeout=30.0)

                # Fetch tools from HTTP endpoint
                response = await self._http_client.get("/mcp/v1/tools")
                response.raise_for_status()
                tools_data = response.json()

                # Convert to Claude format
                self.tools = tools_data.get("tools", [])
                self._connected = True
                logger.info(f"Connected to MCP server via HTTP, loaded {len(self.tools)} tools")
            else:
                # Local: Connect via STDIO
                logger.info("Connecting to MCP server via STDIO")
                server_params = StdioServerParameters(
                    command=settings.mcp_server_command,
                    args=settings.mcp_server_args_list
                )

                # Connect to server using context manager
                self._stdio_context = stdio_client(server_params)
                read, write = await self._stdio_context.__aenter__()

                # Create session
                self.session = ClientSession(read, write)
                await self.session.__aenter__()

                # Initialize and list tools
                await self.session.initialize()
                tools_list = await self.session.list_tools()

                # Convert MCP tools to Claude-compatible format
                self.tools = self._convert_tools_to_claude_format(tools_list.tools)

                self._connected = True
                logger.info(f"Connected to MCP server via STDIO, loaded {len(self.tools)} tools")

        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            raise

    async def disconnect(self) -> None:
        """Disconnect from the MCP server."""
        try:
            if self._http_client:
                await self._http_client.aclose()
            if self.session:
                await self.session.__aexit__(None, None, None)
            if self._stdio_context:
                await self._stdio_context.__aexit__(None, None, None)
            self._connected = False
            logger.info("Disconnected from MCP server")
        except Exception as e:
            logger.error(f"Error disconnecting from MCP server: {e}")

    def _convert_tools_to_claude_format(self, mcp_tools: List[Any]) -> List[Dict[str, Any]]:
        """
        Convert MCP tool definitions to Claude API format.

        Args:
            mcp_tools: List of tools from MCP server

        Returns:
            List of tools in Claude API format
        """
        claude_tools = []
        for tool in mcp_tools:
            claude_tool = {
                "name": tool.name,
                "description": tool.description or "",
                "input_schema": tool.inputSchema if hasattr(tool, 'inputSchema') else {"type": "object", "properties": {}}
            }
            claude_tools.append(claude_tool)

        return claude_tools

    async def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        """
        Execute a tool via the MCP server.

        Args:
            tool_name: Name of the tool to execute
            tool_input: Input parameters for the tool

        Returns:
            Tool execution result

        Raises:
            Exception: If tool execution fails
        """
        if not self._connected:
            await self.connect()

        try:
            logger.info(f"Executing tool: {tool_name} with input: {tool_input}")

            if self._use_http:
                # Execute via HTTP
                response = await self._http_client.post(
                    f"/mcp/v1/tools/{tool_name}/call",
                    json=tool_input
                )
                response.raise_for_status()
                result = response.json()
                logger.debug(f"Tool {tool_name} result: {result}")
                return result
            else:
                # Execute via STDIO
                result = await self.session.call_tool(tool_name, tool_input)
                logger.debug(f"Tool {tool_name} result: {result}")
                return result.content

        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            raise

    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Get the list of available tools in Claude format.

        Returns:
            List of tool definitions
        """
        return self.tools

    async def health_check(self) -> bool:
        """
        Check if the MCP server is healthy.

        Returns:
            True if connected and healthy, False otherwise
        """
        try:
            if not self._connected:
                await self.connect()
            return self._connected
        except Exception:
            return False


# Global MCP client instance
mcp_client = MCPClient()
