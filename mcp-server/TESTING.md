# Testing Guide for MCP Server

This guide walks you through testing the MCP server before integrating it with the backend.

## Prerequisites

1. **Trello Board Setup**
   - Create or use an existing Trello board
   - Add some lists (e.g., "Backlog", "Open", "In Progress", "Done")
   - Optionally add some test cards
   - Optionally create labels (e.g., "IT Support", "Bug", "Feature")

2. **Get Trello API Credentials**

   **Create a Power-Up (required as of 2025):**
   - Go to https://trello.com/power-ups/admin
   - Click "New" / "Create a Power-Up"
   - Fill in basic info (Name: "My API Access", select workspace, add email)
   - Click "Create"

   **Get API Key:**
   - Click on your Power-Up
   - Go to "API Key" tab
   - Click "Generate a new API Key"
   - Copy the API Key

   **Get API Token:**
   - On same page, click the "Token" link, OR
   - Visit this URL (replace YOUR_KEY with your actual key):
     ```
     https://trello.com/1/authorize?expiration=never&scope=read,write&response_type=token&key=YOUR_KEY
     ```
   - Click "Allow"
   - Copy the token

   **Get Board ID:**
   - Open your board, add `.json` to URL, and find the `"id"` field

3. **Environment Setup**
   ```bash
   # Create .env file
   cp .env.example .env

   # Edit .env and add your credentials
   # TRELLO_API_KEY=your_key_here
   # TRELLO_API_TOKEN=your_token_here
   # TRELLO_DEFAULT_BOARD_ID=your_board_id_here
   ```

## Testing Methods

### Method 1: Direct Trello Client Testing (Recommended First)

This tests the Trello API wrapper directly, without the MCP layer.

**Run:**
```bash
python test_trello_client.py
```

**What it tests:**
- ✓ API credentials are valid
- ✓ Can connect to Trello
- ✓ Can list boards
- ✓ Can list lists in a board
- ✓ Can search for cards
- ✓ Can get card details
- ✓ (Optional) Can create cards

**Expected Output:**
```
============================================================
Testing Trello Client
============================================================

1. Initializing Trello client...
✓ Client initialized successfully
  Default Board ID: abc123...

2. Testing: List all boards
✓ Found 3 boards:
  - My Project Board (ID: abc123...)
  - Team Board (ID: def456...)
  - Personal Tasks (ID: ghi789...)

3. Testing: Get lists from board abc123...
✓ Found 4 lists:
  - Backlog (ID: list1, Cards: 5)
  - Open (ID: list2, Cards: 3)
  - In Progress (ID: list3, Cards: 2)
  - Done (ID: list4, Cards: 10)

...
```

**Troubleshooting:**
- **"Configuration Error"**: Check your .env file has all required values
- **"Authentication failed"**: Verify your API key and token are correct
- **"Board not found"**: Check the board ID is correct and you have access

---

### Method 2: MCP Tools Testing

This tests the actual MCP tools that will be called by the backend.

**Run:**
```bash
python test_mcp_tools.py
```

**What it tests:**
- ✓ All 5 MCP tools work correctly
- ✓ Tool input/output format is correct
- ✓ Error handling works
- ✓ Tools return expected data structure

**Expected Output:**
```json
============================================================
Testing MCP Tools
============================================================

1. Testing: list_trello_boards()
------------------------------------------------------------
{
  "boards": [
    {
      "id": "abc123",
      "name": "Support Tickets POC",
      "url": "https://trello.com/b/abc123/..."
    }
  ]
}

2. Testing: list_trello_lists(board_id)
------------------------------------------------------------
{
  "lists": [
    {
      "id": "list1",
      "name": "Backlog",
      "card_count": 5
    },
    ...
  ]
}
```

---

### Method 3: Manual Testing with MCP Inspector (Advanced)

FastMCP provides a development mode to inspect and test tools interactively.

**Run:**
```bash
# Start in development mode
python server.py
```

Then use the MCP protocol to call tools. This is more advanced and requires understanding the MCP protocol.

---

### Method 4: Integration Testing with Claude Desktop (Optional)

You can connect the MCP server to Claude Desktop for testing:

1. **Configure Claude Desktop** (`claude_desktop_config.json`):
   ```json
   {
     "mcpServers": {
       "trello": {
         "command": "python",
         "args": ["C:/path/to/mcp-server/server.py"],
         "env": {
           "TRELLO_API_KEY": "your_key",
           "TRELLO_API_TOKEN": "your_token",
           "TRELLO_DEFAULT_BOARD_ID": "your_board_id"
         }
       }
     }
   }
   ```

2. **Restart Claude Desktop**

3. **Test with prompts:**
   - "List all my Trello boards"
   - "Search for cards with 'bug' in the name"
   - "Create a new card called 'Test Card' in the Backlog list"

---

## Test Checklist

Before moving to backend integration, ensure all these work:

- [ ] `test_trello_client.py` runs without errors
- [ ] Can list boards
- [ ] Can list lists from a board
- [ ] Can search for cards (with and without filters)
- [ ] Can get card details
- [ ] Can create a card (test manually by uncommenting)
- [ ] `test_mcp_tools.py` runs without errors
- [ ] All tools return proper JSON structure
- [ ] Error cases return error messages properly

---

## Testing Card Creation

By default, the test scripts skip card creation to avoid cluttering your board. To test card creation:

1. **Edit `test_trello_client.py`**:
   - Uncomment the card creation test section (around line 74)
   - Adjust the `labels` parameter to match your board's labels

2. **Run the test:**
   ```bash
   python test_trello_client.py
   ```

3. **Verify:**
   - Check your Trello board
   - The test card should appear in the first list
   - It should have the labels you specified

4. **Clean up:**
   - Delete the test card from Trello
   - Re-comment the card creation code

---

## Common Issues

### Issue: "No module named 'fastmcp'"
**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: "TRELLO_API_KEY and TRELLO_API_TOKEN must be set"
**Solution:**
- Ensure `.env` file exists in the `mcp-server` directory
- Check that variable names are correct (no typos)
- Ensure no extra spaces or quotes around values

### Issue: "Board not found"
**Solution:**
- Verify the board ID is correct
- Check that your API token has access to the board
- Make sure the board isn't private/restricted

### Issue: "Rate limit exceeded"
**Solution:**
- Wait a few minutes before retrying
- Trello allows 300 requests per 10 seconds
- Reduce the number of test calls

### Issue: Labels not working
**Solution:**
- Ensure labels exist on your board first
- Label names are case-insensitive
- The test will skip labels that don't exist (no error)

---

## Next Steps

Once testing is complete and all tools work:

1. ✓ MCP Server is ready for integration
2. → Move to **Phase 2: Backend Development**
3. → The FastAPI backend will connect to this MCP server
4. → Backend will execute tools on behalf of Claude

---

## Quick Start Testing (TL;DR)

```bash
# 1. Setup environment
cp .env.example .env
# Edit .env with your credentials

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run basic test
python test_trello_client.py

# 4. If that works, test MCP tools
python test_mcp_tools.py

# 5. All green? You're ready for backend integration!
```
