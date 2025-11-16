# Trello AI Assistant - Project Specification

## Project Overview

**Goal**: Build a proof-of-concept web application that demonstrates the improvement of using Claude API over a local small LLM for AI-assisted Trello ticket management.

**Purpose**: Showcase to stakeholders how Claude API provides superior conversational AI capabilities, better context understanding, and more natural interaction compared to the current implementation using a small local model.

### Current Pain Points with Existing System
- Local small LLM is adequate at classification but very poor at conversation
- Struggles with prompt following and natural dialogue
- Difficult to gather ticket requirements conversationally
- Poor user experience overall

### Expected Improvements with Claude
- Natural, context-aware conversations
- Better at gathering missing information through dialogue
- Strong instruction following for multi-step ticket creation
- Superior understanding of user intent
- Native tool use support

---

## Technical Stack

### Frontend
- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite
- **Key Libraries**: 
  - React hooks for state management
  - Fetch/Axios for API calls
  - CSS framework (TBD - keep minimal for POC)

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Key Libraries**:
  - `anthropic` - Claude API client
  - `mcp` - MCP client for tool server
  - `pydantic` - Data validation
  - `python-dotenv` - Environment configuration

### MCP Server
- **Framework**: FastMCP
- **Integration**: Trello API
- **Authentication**: Trello API Key + Token

### External APIs
- **Claude API**: Anthropic Claude (model: claude-sonnet-4-20250514)
- **Trello API**: REST API v1

---

## Architecture

### High-Level Flow
```
User Input (Frontend)
    ↓
FastAPI Backend
    ↓
Build Claude API Request (with conversation history + system prompt + available tools)
    ↓
Claude API Call
    ↓
Response Parsing (text response OR tool call request)
    ↓
IF Tool Call Needed:
    → MCP Client → FastMCP Server → Trello API
    → Format Tool Result
    → Send back to Claude API with tool result
    → Get final response from Claude
    ↓
ELSE:
    → Return text response to frontend
    ↓
Update Conversation History
    ↓
Send Response to Frontend
```

### Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React + TS)                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Chat Interface                                      │   │
│  │  - Message history display                           │   │
│  │  - User input field                                  │   │
│  │  - Tool call indicators (show when tools are used)   │   │
│  │  - Loading states                                    │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │ POST /api/chat
                         │ { message: string, session_id: string }
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  BACKEND (FastAPI)                           │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  API Endpoints                                        │  │
│  │  - POST /api/chat - Main chat endpoint               │  │
│  │  - GET /api/health - Health check                    │  │
│  │  - POST /api/session/reset - Clear conversation      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Session Manager (In-Memory)                         │  │
│  │  - Store conversation history per session            │  │
│  │  - sessions: Dict[session_id, List[Message]]         │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Claude Service                                       │  │
│  │  - Build messages array with full conversation       │  │
│  │  - Include system prompt                             │  │
│  │  - Provide tool definitions from MCP                 │  │
│  │  - Parse response for tool_use blocks                │  │
│  │  - Handle tool execution loop                        │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  MCP Client                                           │  │
│  │  - Connect to FastMCP server                         │  │
│  │  - Execute tool calls                                │  │
│  │  - Format tool results                               │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────────────┬──────────────────┬──────────────────────┘
                    │                  │
                    │                  └─────────────────┐
                    ▼                                    ▼
         ┌──────────────────┐              ┌─────────────────────────┐
         │   Claude API     │              │   FastMCP Server        │
         │   (Anthropic)    │              │  ┌──────────────────┐  │
         └──────────────────┘              │  │  Trello Tools    │  │
                                           │  │  Implementation  │  │
                                           │  └──────────────────┘  │
                                           └───────────┬─────────────┘
                                                       │
                                                       ▼
                                           ┌──────────────────┐
                                           │   Trello API     │
                                           │   (REST v1)      │
                                           └──────────────────┘
```

---

## Session Persistence Recommendation

### Approach: **In-Memory Session Storage**

**Rationale for POC:**
- Simple implementation (Python dictionary)
- No external dependencies (Redis, database)
- Adequate for single-user demo
- Fast performance
- Acceptable to lose conversations on server restart

**Implementation:**
```python
# backend/session_manager.py
sessions: Dict[str, List[Dict]] = {}

def get_conversation_history(session_id: str) -> List[Dict]:
    return sessions.get(session_id, [])

def add_message(session_id: str, message: Dict):
    if session_id not in sessions:
        sessions[session_id] = []
    sessions[session_id].append(message)

def clear_session(session_id: str):
    if session_id in sessions:
        del sessions[session_id]
```

**Session ID Generation:**
- Frontend generates UUID on mount
- Stores in React state (or localStorage for persistence across page refreshes)
- Sends with every API request

**For Production (Future):**
- Consider Redis for multi-instance deployments
- Consider PostgreSQL for persistent conversation logs
- Add session expiration (TTL)
- Add conversation archival

---

## Supported Ticket Types

### 1. Missing Report Tickets
**Description**: Reports that were expected but not received or are missing from the system.

**Required Information:**
- Report name/type
- Expected delivery date/time
- Who should have submitted it
- Impact/urgency level
- Any error messages or symptoms

**Example User Request:**
"I didn't receive the daily sales report this morning"

### 2. New Report Tickets
**Description**: Requests for new reports or report types that don't currently exist.

**Required Information:**
- Report purpose/objective
- Required data/metrics
- Frequency (daily, weekly, monthly, etc.)
- Intended audience/recipients
- Data sources needed
- Format preferences (PDF, Excel, dashboard, etc.)

**Example User Request:**
"We need a new monthly customer retention report"

### 3. IT Support Tickets
**Description**: General IT-related support requests (hardware, software, access, etc.).

**Required Information:**
- Issue description
- Affected system/application/hardware
- When issue started
- Impact on work
- User affected (if not the requester)
- Priority level
- Any error messages or codes

**Example User Request:**
"My computer won't connect to the VPN"

---

## Request Classification System

### Classification Hierarchy

```
User Input
    ↓
┌─────────────────────────────────────────┐
│  Primary Classification                 │
│  - Information Request                  │
│  - Work Request (Ticket Creation)       │
│  - Miscellaneous/Off-Topic              │
└─────────────────────────────────────────┘
    ↓
IF Information Request:
    → Query Trello (search, get details, list items)
    → Provide information to user
    
IF Work Request:
    ↓
    ┌─────────────────────────────────────┐
    │  Secondary Classification            │
    │  - Missing Report                    │
    │  - New Report                        │
    │  - IT Support                        │
    └─────────────────────────────────────┘
    ↓
    Gather Required Information (conversational)
    ↓
    Confirm Details with User
    ↓
    Create Trello Card
    
IF Miscellaneous:
    → Politely redirect to supported use cases
    → Provide examples of valid requests
```

### Classification Examples

**Information Requests:**
- "Show me all open IT tickets"
- "What's the status of ticket #123?"
- "List all missing report tickets from this week"
- "Are there any high-priority issues?"

**Work Requests:**
- "I need to report a missing dashboard"
- "Create a ticket for a new weekly metrics report"
- "My laptop screen is flickering"
- "The morning email report didn't arrive today"

**Miscellaneous (Redirect):**
- "What's the weather?"
- "Tell me a joke"
- "How do I make a sandwich?"
- General conversation unrelated to Trello/tickets

---

## MCP Server Tools

### Tool Definitions

#### 1. `search_trello_cards`
**Purpose**: Search for Trello cards based on various criteria

**Parameters:**
```json
{
  "query": "string (optional) - Text search in card names and descriptions",
  "list_name": "string (optional) - Filter by list name",
  "label": "string (optional) - Filter by label",
  "limit": "number (optional, default: 10) - Max cards to return"
}
```

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
      "due": "ISO date string or null",
      "url": "https://trello.com/c/..."
    }
  ],
  "count": 10
}
```

#### 2. `get_trello_card_details`
**Purpose**: Get full details of a specific card

**Parameters:**
```json
{
  "card_id": "string - Trello card ID"
}
```

**Returns:**
```json
{
  "id": "card_id",
  "name": "Card title",
  "desc": "Full description",
  "list_name": "Current list",
  "labels": ["label1", "label2"],
  "due": "ISO date string or null",
  "members": ["member1", "member2"],
  "comments": [
    {
      "date": "ISO date",
      "author": "username",
      "text": "comment text"
    }
  ],
  "attachments": [],
  "url": "https://trello.com/c/..."
}
```

#### 3. `list_trello_boards`
**Purpose**: List available Trello boards

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

#### 4. `list_trello_lists`
**Purpose**: List all lists in a specific board

**Parameters:**
```json
{
  "board_id": "string - Trello board ID"
}
```

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

#### 5. `create_trello_card`
**Purpose**: Create a new Trello card

**Parameters:**
```json
{
  "board_id": "string - Target board ID",
  "list_id": "string - Target list ID",
  "name": "string - Card title",
  "desc": "string - Card description",
  "labels": "array of strings (optional) - Label names to apply",
  "due": "string (optional) - ISO date string for due date"
}
```

**Returns:**
```json
{
  "success": true,
  "card": {
    "id": "new_card_id",
    "name": "Card title",
    "url": "https://trello.com/c/...",
    "list_name": "Target list name"
  }
}
```

---

## System Prompt Design

### Core System Prompt Structure

```
You are a Trello ticket management assistant for [Company Name]. Your role is to help users:
1. Find information about existing Trello tickets
2. Create new tickets for missing reports, new report requests, or IT support issues

CLASSIFICATION RULES:
You must first classify every user request into one of three categories:
- Information Request: User wants to know about existing tickets
- Work Request: User wants to create a new ticket
- Miscellaneous: Off-topic or unrelated to Trello/tickets

INFORMATION REQUESTS:
When users ask about existing tickets, use the search_trello_cards or get_trello_card_details tools to find and present the information clearly.

WORK REQUESTS:
When users want to create a ticket, follow these steps:
1. Classify the ticket type: Missing Report, New Report, or IT Support
2. Identify what information is required (see below)
3. Ask conversational questions to gather missing information
4. Confirm all details with the user before creating the ticket
5. Use create_trello_card to create the ticket once confirmed

TICKET TYPE REQUIREMENTS:

Missing Report Tickets require:
- Report name/type
- Expected delivery date/time
- Who should have submitted it
- Impact/urgency level
- Any error messages or symptoms

New Report Tickets require:
- Report purpose/objective
- Required data/metrics
- Frequency (daily, weekly, monthly, etc.)
- Intended audience/recipients
- Data sources needed
- Format preferences

IT Support Tickets require:
- Issue description
- Affected system/application/hardware
- When issue started
- Impact on work
- Priority level
- Any error messages

GATHERING INFORMATION:
- Ask for ONE piece of information at a time
- Be conversational and natural, not robotic
- If user provides partial information, acknowledge what you have and ask for what's missing
- Don't repeat information the user already provided
- Use the context of the conversation to infer details when reasonable

MISCELLANEOUS REQUESTS:
If a request is off-topic, politely redirect:
"I'm specifically designed to help with Trello ticket management. I can help you:
- Find information about existing tickets
- Create new tickets for missing reports, new report requests, or IT support issues

How can I help you with one of these?"

TOOL USE:
- Always search for existing tickets when relevant before creating duplicates
- Use list_trello_boards and list_trello_lists to help users specify where tickets should be created
- Format tool results in a user-friendly way
- If a tool call fails, explain the error clearly and offer alternatives

TONE:
- Professional but friendly
- Efficient - don't over-explain
- Patient when gathering information
- Clear and concise in responses
```

### System Prompt Variables
These should be configurable:
- `{company_name}` - Company name
- `{default_board_id}` - Default board for ticket creation
- `{ticket_lists}` - Mapping of ticket types to list IDs

---

## API Message Flow Examples

### Example 1: Simple Information Request

**Request 1 (User):**
```json
{
  "session_id": "abc123",
  "message": "Show me all open IT support tickets"
}
```

**Backend → Claude:**
```json
{
  "model": "claude-sonnet-4-20250514",
  "max_tokens": 4096,
  "system": [{"type": "text", "text": "<system_prompt>"}],
  "messages": [
    {"role": "user", "content": "Show me all open IT support tickets"}
  ],
  "tools": [<tool_definitions>]
}
```

**Claude Response:**
```json
{
  "content": [
    {
      "type": "tool_use",
      "id": "toolu_123",
      "name": "search_trello_cards",
      "input": {
        "label": "IT Support",
        "list_name": "Open",
        "limit": 20
      }
    }
  ]
}
```

**Backend → MCP Server:** Execute tool

**MCP Response:**
```json
{
  "cards": [
    {"id": "1", "name": "VPN connection issues", "desc": "...", ...},
    {"id": "2", "name": "Laptop screen flickering", "desc": "...", ...}
  ],
  "count": 2
}
```

**Backend → Claude (with tool result):**
```json
{
  "model": "claude-sonnet-4-20250514",
  "max_tokens": 4096,
  "system": [{"type": "text", "text": "<system_prompt>"}],
  "messages": [
    {"role": "user", "content": "Show me all open IT support tickets"},
    {
      "role": "assistant",
      "content": [
        {
          "type": "tool_use",
          "id": "toolu_123",
          "name": "search_trello_cards",
          "input": {...}
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "tool_result",
          "tool_use_id": "toolu_123",
          "content": "<mcp_response_json>"
        }
      ]
    }
  ],
  "tools": [<tool_definitions>]
}
```

**Claude Final Response:**
```json
{
  "content": [
    {
      "type": "text",
      "text": "I found 2 open IT support tickets:\n\n1. **VPN connection issues** - ..."
    }
  ]
}
```

**Backend → Frontend:**
```json
{
  "message": "I found 2 open IT support tickets:\n\n1. **VPN connection issues** - ...",
  "tool_calls": [
    {
      "tool": "search_trello_cards",
      "status": "success"
    }
  ]
}
```

### Example 2: Multi-Turn Ticket Creation

**Turn 1 (User):**
```
"I need to report a missing report"
```

**Claude Response (No tool call):**
```
I'll help you create a ticket for a missing report. To get started, which report are you missing?
```

**Turn 2 (User):**
```
"The daily sales summary"
```

**Claude Response (No tool call):**
```
Got it - the daily sales summary report is missing. When were you expecting to receive this report?
```

**Turn 3 (User):**
```
"This morning by 9 AM, but it never arrived"
```

**Claude Response (No tool call):**
```
Understood. Who typically submits this report, and how urgent is this issue for you?
```

**Turn 4 (User):**
```
"The sales team sends it automatically. It's pretty urgent since we need it for the morning standup"
```

**Claude Response (No tool call):**
```
Perfect, I have all the information I need. Let me confirm the details:

- Missing Report: Daily Sales Summary
- Expected: Today at 9 AM
- Submitted by: Sales team (automatic)
- Urgency: High (needed for morning standup)

Should I create this ticket?
```

**Turn 5 (User):**
```
"Yes, please"
```

**Claude Response (With tool call):**
```json
{
  "content": [
    {
      "type": "tool_use",
      "id": "toolu_456",
      "name": "create_trello_card",
      "input": {
        "board_id": "board123",
        "list_id": "list789",
        "name": "Missing Report: Daily Sales Summary",
        "desc": "Report: Daily Sales Summary\nExpected: Today at 9 AM\nSubmitted by: Sales team (automatic)\nUrgency: High - needed for morning standup\nReported by: User\nReported at: 2025-11-13 10:30 AM",
        "labels": ["Missing Report", "High Priority"]
      }
    }
  ]
}
```

**After Tool Execution:**
```
I've created your ticket for the missing Daily Sales Summary report. You can track it here: [Trello Card Link]

The ticket has been marked as high priority and assigned to the Missing Reports list.
```

---

## Frontend Requirements

### Chat Interface Components

#### 1. Message Display
```typescript
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  toolCalls?: ToolCall[];
}

interface ToolCall {
  tool: string;
  status: 'executing' | 'success' | 'error';
  error?: string;
}
```

#### 2. Tool Call Indicators
Display when tools are being used:
- "🔍 Searching Trello cards..."
- "📝 Creating ticket..."
- "✅ Ticket created successfully"
- "❌ Error: Could not connect to Trello"

#### 3. Message Input
- Text input field
- Send button (or Enter key)
- Disable during API calls
- Clear after sending

#### 4. Session Management
- Generate session ID on component mount
- Store in React state
- Optional: Persist to localStorage
- "New Conversation" button to reset

### API Integration

```typescript
// api/chat.ts
export interface ChatRequest {
  session_id: string;
  message: string;
}

export interface ChatResponse {
  message: string;
  tool_calls?: ToolCall[];
  error?: string;
}

export async function sendMessage(request: ChatRequest): Promise<ChatResponse> {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  
  if (!response.ok) {
    throw new Error('API request failed');
  }
  
  return response.json();
}
```

---

## Backend Requirements

### Project Structure
```
backend/
├── main.py                 # FastAPI app entry point
├── config.py               # Configuration and environment variables
├── models.py               # Pydantic models
├── session_manager.py      # In-memory session storage
├── claude_service.py       # Claude API integration
├── mcp_client.py           # MCP client for tool execution
├── tools.py                # Tool definitions and descriptions
├── system_prompt.py        # System prompt template
├── requirements.txt        # Python dependencies
└── .env                    # Environment variables (not committed)
```

### Environment Variables
```
ANTHROPIC_API_KEY=sk-ant-...
TRELLO_API_KEY=...
TRELLO_API_TOKEN=...
TRELLO_DEFAULT_BOARD_ID=...
MCP_SERVER_URL=...
CORS_ORIGINS=http://localhost:5173
```

### Key Endpoints

#### POST /api/chat
**Request:**
```json
{
  "session_id": "uuid",
  "message": "user message text"
}
```

**Response:**
```json
{
  "message": "assistant response text",
  "tool_calls": [
    {
      "tool": "search_trello_cards",
      "status": "success"
    }
  ]
}
```

#### POST /api/session/reset
**Request:**
```json
{
  "session_id": "uuid"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Session cleared"
}
```

#### GET /api/health
**Response:**
```json
{
  "status": "healthy",
  "claude_api": "connected",
  "mcp_server": "connected"
}
```

### Tool Execution Loop Logic

```python
async def process_message(session_id: str, user_message: str) -> dict:
    # 1. Get conversation history
    history = session_manager.get_conversation_history(session_id)
    
    # 2. Add user message to history
    history.append({"role": "user", "content": user_message})
    
    # 3. Build Claude API request
    request = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 4096,
        "system": system_prompt,
        "messages": history,
        "tools": tool_definitions
    }
    
    tool_calls_made = []
    
    # 4. Tool execution loop
    while True:
        # Call Claude API
        response = await claude_client.messages.create(**request)
        
        # Check if response contains tool use
        tool_use_blocks = [
            block for block in response.content 
            if block.type == "tool_use"
        ]
        
        if not tool_use_blocks:
            # No more tool calls, we have the final response
            final_text = "".join([
                block.text for block in response.content 
                if block.type == "text"
            ])
            
            # Add assistant response to history
            history.append({
                "role": "assistant",
                "content": response.content
            })
            
            # Save updated history
            session_manager.set_conversation_history(session_id, history)
            
            return {
                "message": final_text,
                "tool_calls": tool_calls_made
            }
        
        # Execute tool calls
        tool_results = []
        for tool_use in tool_use_blocks:
            tool_name = tool_use.name
            tool_input = tool_use.input
            
            try:
                # Execute tool via MCP
                result = await mcp_client.execute_tool(tool_name, tool_input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": json.dumps(result)
                })
                tool_calls_made.append({
                    "tool": tool_name,
                    "status": "success"
                })
            except Exception as e:
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": f"Error: {str(e)}",
                    "is_error": True
                })
                tool_calls_made.append({
                    "tool": tool_name,
                    "status": "error",
                    "error": str(e)
                })
        
        # Add assistant response with tool use to history
        history.append({
            "role": "assistant",
            "content": response.content
        })
        
        # Add tool results to history as next user message
        history.append({
            "role": "user",
            "content": tool_results
        })
        
        # Update request for next iteration
        request["messages"] = history
```

---

## MCP Server Requirements

### Project Structure
```
mcp_server/
├── server.py              # FastMCP server entry point
├── trello_client.py       # Trello API wrapper
├── tools/
│   ├── search.py          # search_trello_cards implementation
│   ├── details.py         # get_trello_card_details implementation
│   ├── lists.py           # list_trello_boards, list_trello_lists
│   └── create.py          # create_trello_card implementation
├── requirements.txt       # Python dependencies
└── .env                   # Environment variables
```

### Trello API Configuration

**Board Setup:**
- Create test board named "Support Tickets POC"
- Create lists:
  - "Backlog"
  - "Open"
  - "In Progress"
  - "Resolved"
- Create labels:
  - "Missing Report" (red)
  - "New Report" (blue)
  - "IT Support" (green)
  - "High Priority" (orange)
  - "Medium Priority" (yellow)
  - "Low Priority" (gray)

### Tool Implementation Notes

- Use Trello REST API v1 endpoints
- Implement proper error handling for API failures
- Cache board/list IDs for performance
- Rate limiting awareness (Trello has 300 requests per 10 seconds)
- Return structured, consistent responses

---

## Testing Strategy

### Manual Testing Scenarios

#### Information Request Tests
1. "Show me all open tickets"
2. "What IT support tickets are in progress?"
3. "Find tickets about missing reports"
4. "What's the status of card XYZ?"

#### Ticket Creation Tests

**Missing Report:**
1. Full info upfront: "Create a ticket - the weekly analytics report that was due yesterday from the data team is missing. It's blocking our sprint planning."
2. Minimal info: "I didn't get a report" (should ask questions)
3. Partial info: "The sales dashboard is missing, it was supposed to come this morning"

**New Report:**
1. Full info upfront: "We need a new monthly customer churn report showing retention metrics, data should come from our CRM, and it should go to the executive team"
2. Minimal info: "We need a new report" (should ask questions)

**IT Support:**
1. Full info upfront: "My laptop won't boot up after the latest Windows update. Error code 0x80070002. Started this morning. High priority - can't work without it."
2. Minimal info: "My computer is broken" (should ask questions)

#### Edge Cases
1. Ambiguous request: "Something is wrong" (should clarify)
2. Off-topic: "What's the weather?" (should redirect)
3. Duplicate ticket check: Create similar ticket twice (should search first)
4. Invalid data: Request with impossible dates or malformed info

### Demo Script

**Demo Flow:**
1. Show current implementation (clunky local LLM)
2. Show new implementation with Claude:
   - Natural conversation
   - Context understanding
   - Efficient information gathering
   - Polite error handling
3. Compare:
   - Number of turns to create ticket
   - Quality of conversation
   - Handling of ambiguous requests

**Key Points to Highlight:**
- "Notice how it remembers what we already discussed"
- "See how it asks just one question at a time"
- "Look at how naturally it clarifies ambiguous requests"
- "It actually understands the context of our workflow"

---

## Implementation Phases

### Phase 1: MCP Server (Week 1)
- [ ] Setup FastMCP server
- [ ] Implement Trello API client
- [ ] Implement all 5 tools
- [ ] Test tools independently with Trello sandbox
- [ ] Document tool responses

### Phase 2: Backend (Week 1-2)
- [ ] Setup FastAPI project structure
- [ ] Implement session manager
- [ ] Integrate Claude API
- [ ] Implement tool execution loop
- [ ] Create system prompt
- [ ] Test with Postman/curl
- [ ] Handle error cases

### Phase 3: Frontend (Week 2)
- [ ] Setup React + TypeScript + Vite
- [ ] Create chat interface
- [ ] Implement message display
- [ ] Add tool call indicators
- [ ] Connect to backend API
- [ ] Add session management
- [ ] Style and polish UI

### Phase 4: Integration & Testing (Week 2-3)
- [ ] End-to-end testing
- [ ] Test all ticket type flows
- [ ] Test edge cases
- [ ] Performance testing
- [ ] Bug fixes

### Phase 5: Demo Preparation (Week 3)
- [ ] Prepare demo script
- [ ] Create demo Trello board with sample data
- [ ] Document comparison points vs current system
- [ ] Practice demo presentation
- [ ] Get feedback from team

---

## Success Metrics for POC

### Quantitative Metrics
- Fewer conversation turns to create a ticket (target: < 5 turns average)
- Successful ticket creation rate (target: > 95%)
- Tool call success rate (target: > 98%)
- Response time (target: < 3 seconds per interaction)

### Qualitative Metrics
- Naturalness of conversation (vs. current robotic LLM)
- Ability to handle ambiguous requests
- Context retention across turns
- User satisfaction (demo feedback)

### Comparison Points vs Current System
- Conversation quality (subjective but obvious)
- Classification accuracy (should be similar)
- Information gathering efficiency (should be better)
- Error recovery (should be much better)
- Overall user experience (should be significantly better)

---

## Known Limitations & Future Enhancements

### Current Limitations (POC)
- In-memory sessions (lost on restart)
- Single-user only
- No authentication
- No conversation persistence
- No analytics/logging
- No streaming responses
- Limited error recovery

### Future Enhancements (Post-POC)
- Multi-user support with authentication
- Persistent conversation storage
- Streaming responses for better UX
- Advanced search capabilities
- Ticket templates
- Batch operations
- Analytics dashboard
- Integration with other tools (Slack, email)
- Voice input support
- Mobile app

---

## Deployment Considerations

### Development Environment
- Frontend: `npm run dev` (Vite dev server on port 5173)
- Backend: `uvicorn main:app --reload` (port 8000)
- MCP Server: `python server.py` (port configurable)

### Demo/Production Deployment
- **Frontend**: Build with `npm run build`, serve static files
- **Backend**: Run with Gunicorn/Uvicorn workers
- **MCP Server**: Run as separate service
- **Hosting Options**:
  - Simple: All on one VPS (Digital Ocean, Linode)
  - Docker: Containerize each component
  - Cloud: AWS/GCP with load balancer (overkill for POC)

### Environment Setup for Demo
1. Deploy to a stable server (not localhost)
2. Use HTTPS (Let's Encrypt)
3. Ensure Trello API credentials are secured
4. Set up monitoring for uptime
5. Create demo board with sample tickets
6. Share URL with stakeholders

---

## Questions & Decisions Tracker

### Resolved
- ✅ Session persistence: In-memory for POC
- ✅ Streaming: Not for initial version
- ✅ Ticket types: Missing Report, New Report, IT Support
- ✅ UI for tool calls: Yes, show indicators

### To Be Decided
- Frontend CSS framework (Tailwind vs. vanilla CSS vs. other)
- Exact Trello board/list structure for demo
- Demo data to populate
- Hosting provider for demo deployment
- Whether to add conversation export feature

---

## Resources & References

### Documentation Links
- [Claude API Documentation](https://docs.anthropic.com/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Trello API Documentation](https://developer.atlassian.com/cloud/trello/rest/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)

### Key Concepts
- **Tool Use**: Claude's native function calling capability
- **MCP**: Model Context Protocol for standardized tool servers
- **Conversation History**: Critical for Claude to maintain context
- **System Prompt**: Instructions that guide Claude's behavior

---

## Project Status

**Current Phase**: Planning Complete ✅  
**Next Steps**: Begin Phase 1 (MCP Server Implementation)  
**Target Demo Date**: [To Be Determined]  
**Last Updated**: 2025-11-13
