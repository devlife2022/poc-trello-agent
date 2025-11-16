# Trello AI Assistant - FastAPI Backend

FastAPI backend service for the AI-assisted Trello ticket management POC. Integrates Claude API with the MCP server to provide conversational ticket management capabilities.

## Overview

This backend service:
- Handles chat conversations with users via Claude API
- Manages conversation sessions in memory
- Connects to the MCP server to execute Trello operations
- Supports customizable prompts for different request types
- Provides health monitoring and session management

## Features

- **Chat Endpoint**: Process user messages with Claude and execute Trello tools
- **Session Management**: Track conversation history per session
- **Prompt System**: Base prompt + request-type specific prompts (missing_report, new_report, it_support)
- **Tool Execution Loop**: Automatic multi-turn tool use handling
- **Health Checks**: Monitor Claude API and MCP server connectivity
- **CORS Support**: Ready for frontend integration

## Prerequisites

- Python 3.11 or higher
- Anthropic API key (Claude)
- MCP server running (from ../mcp-server)
- Trello credentials (configured in MCP server)

## Getting Claude API Key

1. Sign up at https://console.anthropic.com
2. Navigate to API Keys section
3. Create a new API key
4. Copy the key (starts with `sk-ant-`)

## Setup

### 1. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your credentials
```

Required environment variables:
```env
ANTHROPIC_API_KEY=sk-ant-your-api-key-here
```

**Note:** Trello credentials are configured in `../mcp-server/.env`, not in the API's `.env` file. The MCP server manages its own Trello API access.

### 4. Verify MCP Server

Ensure the MCP server is set up and can run:
```bash
cd ../mcp-server
python server.py
```

Press Ctrl+C to stop it. The API backend will start it automatically.

## Running the Server

### Development Mode (with auto-reload)

```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

## API Endpoints

### POST /api/chat

Process a user message and get AI response.

**Request:**
```json
{
  "session_id": "unique-session-id",
  "message": "I need to report a missing report"
}
```

**Response:**
```json
{
  "message": "I'll help you create a ticket for the missing report. Which report are you referring to?",
  "tool_calls": [],
  "error": null
}
```

### POST /api/session/reset

Clear a conversation session.

**Request:**
```json
{
  "session_id": "unique-session-id"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Session cleared successfully"
}
```

### GET /api/health

Check health status of the API and its dependencies.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-15T10:30:00",
  "claude_api": "connected",
  "mcp_server": "connected",
  "active_sessions": 3
}
```

## Prompt System

The backend uses a flexible prompt system with:

### Base Prompt
Located at: `prompts/base_prompt.txt`

Contains core instructions for:
- Classification rules (Information Request, Work Request, Miscellaneous)
- General behavior guidelines
- Tool use instructions
- Tone and style

### Request-Type Specific Prompts

Located at `prompts/`:
- `missing_report.txt` - Instructions for missing report tickets
- `new_report.txt` - Instructions for new report requests
- `it_support.txt` - Instructions for IT support tickets

**Customizing Prompts:**
1. Edit the relevant .txt file in the `prompts/` directory
2. Restart the server to load changes
3. Or use the prompt reload endpoint (if implemented)

The system combines the base prompt with request-type specific instructions automatically.

## Project Structure

```
api/
├── main.py                 # FastAPI application entry point
├── config.py               # Configuration and settings
├── models.py               # Pydantic models for API
├── session_manager.py      # In-memory session storage
├── claude_service.py       # Claude API integration
├── mcp_client.py           # MCP client for tool execution
├── prompt_manager.py       # Prompt loading and management
├── prompts/
│   ├── base_prompt.txt     # Base system prompt
│   ├── missing_report.txt  # Missing report instructions
│   ├── new_report.txt      # New report instructions
│   └── it_support.txt      # IT support instructions
├── requirements.txt        # Python dependencies
├── .env.example           # Example environment variables
├── .env                   # Your actual config (not committed)
└── README.md             # This file
```

## Architecture

### Request Flow

```
1. User sends message → POST /api/chat
2. Backend retrieves conversation history from session manager
3. Backend calls Claude API with:
   - System prompt (base + request-type specific)
   - Conversation history
   - Available tools from MCP server
4. Claude responds with text and/or tool calls
5. If tool calls:
   a. Backend executes tools via MCP client
   b. MCP client calls MCP server
   c. MCP server executes Trello API calls
   d. Results returned to Claude
   e. Claude processes results and responds
6. Backend updates conversation history
7. Response sent to frontend
```

### Tool Execution Loop

The `claude_service.py` implements an automatic tool execution loop:
1. Send message to Claude with available tools
2. If Claude requests tools, execute them via MCP
3. Send tool results back to Claude
4. Repeat until Claude returns final text response
5. Maximum 10 iterations to prevent infinite loops

## Session Management

Sessions are stored in memory with the following features:
- Automatic creation on first use
- 60-minute timeout after last activity
- Automatic cleanup of expired sessions
- Support for multiple concurrent sessions

**Session Best Practices:**
- Generate a UUID for each user/browser session
- Store session ID in browser localStorage
- Reset session when starting a new conversation
- Sessions are lost on server restart (expected for POC)

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Claude API key | Required |
| `CLAUDE_MODEL` | Claude model to use | claude-sonnet-4-20250514 |
| `CLAUDE_MAX_TOKENS` | Max tokens per response | 4096 |
| `MCP_SERVER_COMMAND` | Command to run MCP server | python |
| `MCP_SERVER_ARGS` | Args for MCP server | ../mcp-server/server.py |
| `CORS_ORIGINS` | Allowed CORS origins | localhost:5173,localhost:3000 |
| `API_HOST` | API host | 0.0.0.0 |
| `API_PORT` | API port | 8000 |

### Logging

Logs are configured in `main.py`:
- Level: INFO
- Format: Timestamp - Logger - Level - Message
- Logs to console (stdout)

To change log level, edit `main.py`:
```python
logging.basicConfig(level=logging.DEBUG)  # More verbose
```

## Testing

### Manual Testing with curl

**Chat request:**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-123",
    "message": "Show me all open IT tickets"
  }'
```

**Health check:**
```bash
curl http://localhost:8000/api/health
```

**Reset session:**
```bash
curl -X POST http://localhost:8000/api/session/reset \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test-123"}'
```

### Interactive API Testing

Visit http://localhost:8000/docs for Swagger UI where you can:
- See all available endpoints
- Test endpoints interactively
- View request/response schemas
- Download OpenAPI spec

## Troubleshooting

### "MCP server not available"

**Check:**
1. MCP server path is correct in `.env`
2. MCP server can run standalone: `cd ../mcp-server && python server.py`
3. MCP server has correct Trello credentials
4. Check logs for connection errors

### "Anthropic API error"

**Check:**
1. `ANTHROPIC_API_KEY` is set correctly
2. API key is valid and not expired
3. Account has sufficient credits
4. Network can reach api.anthropic.com

### "Tool execution failed"

**Check:**
1. MCP server is running
2. Trello API credentials are valid
3. Board ID exists and is accessible
4. Check MCP server logs for errors

### CORS errors from frontend

**Fix:**
1. Add frontend URL to `CORS_ORIGINS` in `.env`
2. Restart the API server
3. Clear browser cache

### Sessions not persisting

**Expected behavior:**
- Sessions are stored in memory
- Lost on server restart
- This is intentional for the POC
- For production, implement Redis or database storage

## Performance Considerations

### Current Limitations (POC)
- In-memory sessions (not scaled across instances)
- Sequential tool execution (not parallelized)
- No caching of tool results
- No rate limiting

### For Production
- Use Redis for session storage
- Implement response caching
- Add rate limiting per session/IP
- Parallelize independent tool calls
- Add request queuing for high load
- Implement timeout handling
- Add retry logic for API calls

## Security

**Current Setup:**
- CORS restricted to configured origins
- No authentication (add for production)
- API keys in environment variables (good)
- Logs may contain sensitive data (review before production)

**Production Recommendations:**
- Add user authentication (JWT, OAuth)
- Implement rate limiting
- Add input validation and sanitization
- Use HTTPS only
- Rotate API keys regularly
- Implement audit logging
- Add request signing

## Next Steps

After setting up the backend:
1. Test with curl or Swagger UI
2. Verify Claude and MCP connectivity
3. Test conversation flows
4. Customize prompts as needed
5. Proceed to frontend development (Phase 3)

## License

Part of the Trello AI Assistant POC project.
