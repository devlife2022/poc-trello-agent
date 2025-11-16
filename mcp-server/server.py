"""
FastMCP server for Trello integration.
Provides tools for searching, viewing, and creating Trello cards.
"""
from fastmcp import FastMCP
from trello_client import TrelloClient
from typing import Optional, List

# Initialize FastMCP server
mcp = FastMCP("Trello MCP Server")

# Initialize Trello client
trello_client = TrelloClient()


@mcp.tool()
def search_trello_cards(
    query: Optional[str] = None,
    list_name: Optional[str] = None,
    label: Optional[str] = None,
    limit: int = 10
) -> dict:
    """
    Search for Trello cards based on various criteria.

    Args:
        query: Text search in card names and descriptions (optional)
        list_name: Filter by list name (optional)
        label: Filter by label name (optional)
        limit: Maximum number of cards to return (default: 10)

    Returns:
        Dictionary containing matching cards and total count
    """
    try:
        result = trello_client.search_cards(
            query=query,
            list_name=list_name,
            label=label,
            limit=limit
        )
        return result
    except Exception as e:
        return {
            "error": str(e),
            "cards": [],
            "count": 0
        }


@mcp.tool()
def get_trello_card_details(card_id: str) -> dict:
    """
    Get full details of a specific Trello card.

    Args:
        card_id: The Trello card ID

    Returns:
        Dictionary containing card details including comments, members, and attachments
    """
    try:
        result = trello_client.get_card_details(card_id)
        return result
    except Exception as e:
        return {
            "error": str(e)
        }


@mcp.tool()
def list_trello_boards() -> dict:
    """
    List all available Trello boards for the authenticated user.

    Returns:
        Dictionary containing list of boards with their IDs, names, and URLs
    """
    try:
        boards = trello_client.get_boards()
        return {
            "boards": boards
        }
    except Exception as e:
        return {
            "error": str(e),
            "boards": []
        }


@mcp.tool()
def list_trello_lists(board_id: str) -> dict:
    """
    List all lists in a specific Trello board.

    Args:
        board_id: The Trello board ID

    Returns:
        Dictionary containing lists with their IDs, names, and card counts
    """
    try:
        lists = trello_client.get_lists(board_id)
        return {
            "lists": lists
        }
    except Exception as e:
        return {
            "error": str(e),
            "lists": []
        }


@mcp.tool()
def create_trello_card(
    list_id: str,
    name: str,
    desc: str = "",
    board_id: Optional[str] = None,
    labels: Optional[List[str]] = None,
    due: Optional[str] = None
) -> dict:
    """
    Create a new Trello card.

    Args:
        list_id: ID of the list to create the card in (required)
        name: Card title (required)
        desc: Card description (optional)
        board_id: Board ID (optional, uses default if not provided)
        labels: List of label names to apply (optional)
        due: Due date in ISO format (optional)

    Returns:
        Dictionary containing success status and created card details
    """
    try:
        result = trello_client.create_card(
            board_id=board_id,
            list_id=list_id,
            name=name,
            desc=desc,
            labels=labels,
            due=due
        )
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


if __name__ == "__main__":
    import os

    # Check if running in production (Render)
    port = os.getenv("PORT")

    if port:
        # Production: Run as HTTP server
        import uvicorn
        print(f"Starting MCP server in HTTP mode on port {port}")
        # FastMCP provides http_app for HTTP transport
        uvicorn.run(mcp.http_app, host="0.0.0.0", port=int(port))
    else:
        # Local development: Run in STDIO mode for Claude Desktop
        print("Starting MCP server in STDIO mode")
        mcp.run()
