# Trello MCP Server

FastMCP server providing Trello integration tools for the AI Assistant POC.

## Overview

This MCP (Model Context Protocol) server exposes Trello API functionality as tools that can be used by Claude and other AI models. It implements 5 core tools for searching, viewing, and creating Trello cards.

## Features

### Available Tools

1. **search_trello_cards** - Search for cards based on query, list, or label
2. **get_trello_card_details** - Get full details of a specific card
3. **list_trello_boards** - List all available boards
4. **list_trello_lists** - List all lists in a board
5. **create_trello_card** - Create a new card with optional labels and due date

## Prerequisites

- Python 3.11 or higher
- Trello account with API access
- Trello API Key and Token

## Getting Trello API Credentials

### 1. Create a Power-Up (Required)

As of 2025, you must create a Power-Up to get API access (it's just a formality):

1. Go to https://trello.com/power-ups/admin
2. Click **"New"** or **"Create a Power-Up"**
3. Fill in the required fields:
   - **Name**: "My API Access" (or any name)
   - **Workspace**: Select your workspace
   - **Email**: Your email address
   - **Author**: Your name
4. Click **"Create"**

### 2. Generate API Key

1. Click on your newly created Power-Up
2. Navigate to the **"API Key"** tab
3. Click **"Generate a new API Key"**
4. Copy the API Key that appears

### 3. Generate API Token

1. On the same page, click the **"Token"** link next to your API Key
2. Or manually visit (replace `YOUR_API_KEY` with your actual key):
   ```
   https://trello.com/1/authorize?expiration=never&scope=read,write&response_type=token&key=YOUR_API_KEY
   ```
3. Click **"Allow"**
4. Copy the token from the redirected page

**Token Parameters:**
- `expiration=never` - Token never expires (good for development)
- `scope=read,write` - Full read/write access (required for creating cards)

### 4. Get Board ID

1. Open your Trello board in a web browser
2. Add `.json` to the end of the URL
3. Look for the `"id"` field in the JSON response
4. Example: If URL is `https://trello.com/b/abc123/my-board`, visit `https://trello.com/b/abc123/my-board.json`

## Setup

1. **Create virtual environment** (recommended):
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   ```bash
   # Copy example env file
   cp .env.example .env

   # Edit .env and add your credentials
   TRELLO_API_KEY=your_api_key_here
   TRELLO_API_TOKEN=your_api_token_here
   TRELLO_DEFAULT_BOARD_ID=your_board_id_here
   ```

## Running the Server

```bash
python server.py
```

The server will start and expose the Trello tools via the MCP protocol.

## Usage Examples

### Connecting from Backend

The FastAPI backend will connect to this MCP server to execute tools. Example usage:

```python
from mcp import ClientSession

# Connect to MCP server
session = ClientSession("stdio", "python", ["server.py"])

# Search for cards
result = await session.call_tool("search_trello_cards", {
    "query": "bug",
    "label": "High Priority",
    "limit": 5
})

# Create a card
result = await session.call_tool("create_trello_card", {
    "list_id": "list_id_here",
    "name": "New Bug Report",
    "desc": "Description of the bug",
    "labels": ["Bug", "High Priority"]
})
```

## Tool Specifications

### search_trello_cards

**Parameters:**
- `query` (optional): Text to search in card names and descriptions
- `list_name` (optional): Filter by list name
- `label` (optional): Filter by label name
- `limit` (default: 10): Maximum number of cards to return

**Returns:**
```json
{
  "cards": [
    {
      "id": "card_id",
      "name": "Card title",
      "desc": "Card description",
      "list_name": "List name",
      "labels": ["label1", "label2"],
      "due": "2025-11-15T10:00:00.000Z",
      "url": "https://trello.com/c/..."
    }
  ],
  "count": 1
}
```

### get_trello_card_details

**Parameters:**
- `card_id` (required): Trello card ID

**Returns:**
```json
{
  "id": "card_id",
  "name": "Card title",
  "desc": "Full description",
  "list_name": "Current list",
  "labels": ["label1"],
  "due": "2025-11-15T10:00:00.000Z",
  "members": ["username1"],
  "comments": [
    {
      "date": "2025-11-13T09:00:00.000Z",
      "author": "username",
      "text": "Comment text"
    }
  ],
  "attachments": [],
  "url": "https://trello.com/c/..."
}
```

### list_trello_boards

**Parameters:** None

**Returns:**
```json
{
  "boards": [
    {
      "id": "board_id",
      "name": "Board name",
      "url": "https://trello.com/b/..."
    }
  ]
}
```

### list_trello_lists

**Parameters:**
- `board_id` (required): Trello board ID

**Returns:**
```json
{
  "lists": [
    {
      "id": "list_id",
      "name": "List name",
      "card_count": 5
    }
  ]
}
```

### create_trello_card

**Parameters:**
- `list_id` (required): ID of the list to create card in
- `name` (required): Card title
- `desc` (optional): Card description
- `board_id` (optional): Board ID (uses default if not provided)
- `labels` (optional): Array of label names to apply
- `due` (optional): Due date in ISO format

**Returns:**
```json
{
  "success": true,
  "card": {
    "id": "new_card_id",
    "name": "Card title",
    "url": "https://trello.com/c/...",
    "list_name": "List name"
  }
}
```

## Testing

You can test the tools independently before integrating with the backend:

```bash
# Test with MCP inspector (if available)
mcp dev server.py

# Or create a simple test script
python test_tools.py
```

Example test script ([test_tools.py]
```python
from trello_client import TrelloClient

client = TrelloClient()

# Test listing boards
boards = client.get_boards()
print(f"Found {len(boards)} boards")

# Test searching cards
results = client.search_cards(query="test", limit=5)
print(f"Found {results['count']} cards")

# Test getting card details (replace with real card ID)
# details = client.get_card_details("card_id_here")
# print(details)
```

## Trello Board Setup for POC

For the POC demo, set up your Trello board with:

**Lists:**
- Backlog
- Open
- In Progress
- Resolved

**Labels:**
- Missing Report (red)
- New Report (blue)
- IT Support (green)
- High Priority (orange)
- Medium Priority (yellow)
- Low Priority (gray)

## Error Handling

All tools return error information in the response if something goes wrong:

```json
{
  "error": "Error message here",
  "cards": [],
  "count": 0
}
```

## Rate Limiting

Trello API has rate limits (300 requests per 10 seconds). The client implements basic error handling but does not implement rate limiting logic. For production use, consider adding:

- Request queuing
- Exponential backoff
- Rate limit tracking

## Project Structure

```
mcp-server/
├── server.py              # FastMCP server entry point
├── trello_client.py       # Trello API wrapper
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment variables
├── .env                  # Your actual credentials (not committed)
└── README.md            # This file
```

## Troubleshooting

### Authentication Errors

If you get authentication errors:
1. Verify your API key and token are correct
2. Check that the token has read and write permissions
3. Ensure the token hasn't expired

### Board/List Not Found

If tools can't find your board or lists:
1. Verify the board ID is correct
2. Check that your API token has access to the board
3. Ensure the board isn't private/restricted

### Connection Issues

If the backend can't connect to the MCP server:
1. Check that the server is running
2. Verify the server URL/port configuration
3. Check firewall settings if running on different machines

## Next Steps

After setting up the MCP server:
1. Test each tool independently with your Trello board
2. Proceed to Phase 2: Backend implementation
3. The backend will connect to this server to execute tools on behalf of Claude

## License

Part of the Trello AI Assistant POC project.
