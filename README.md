# Trello AI Assistant - POC

An AI-powered conversational interface for managing Trello tickets using Claude API.

## 🚀 Live Demo

- **Frontend**: `https://YOUR_GITHUB_USERNAME.github.io/poc-trello-agent/`
- **Backend API**: `https://trello-ai-backend.onrender.com`

## 📋 Overview

This proof-of-concept demonstrates how Claude API provides superior conversational AI capabilities for Trello ticket management compared to small local LLMs. The system can:

- **Answer questions** about existing Trello tickets
- **Create new tickets** through natural conversation
- **Classify requests** into categories (Missing Report, New Report, IT Support)
- **Gather information** conversationally to complete ticket creation

## 🏗️ Architecture

```
┌─────────────────────────────────┐
│   Frontend (React + TypeScript) │
│   Deployed on GitHub Pages      │
└────────────┬────────────────────┘
             │ HTTPS
             ▼
┌─────────────────────────────────┐
│   Backend (FastAPI)             │
│   Deployed on Render            │
│   - Session management          │
│   - Claude API integration      │
└────────┬──────────────┬─────────┘
         │              │
         │              └──────────┐
         ▼                         ▼
┌──────────────┐        ┌──────────────────┐
│  Claude API  │        │  MCP Server      │
│  (Anthropic) │        │  (Render)        │
└──────────────┘        │  - Trello Tools  │
                        └────────┬─────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │   Trello API     │
                        └──────────────────┘
```

## 🛠️ Tech Stack

### Frontend
- React 19 + TypeScript
- Vite (build tool)
- Deployed on **GitHub Pages** (FREE)

### Backend
- FastAPI (Python 3.11)
- Anthropic Claude API
- MCP (Model Context Protocol)
- Deployed on **Render** (FREE tier)

### MCP Server
- FastMCP framework
- Trello API integration
- Deployed on **Render** (FREE tier)

## 💰 Hosting Cost: $0/month

- GitHub Pages: **FREE**
- Render (2 services): **FREE** (750 hours/month each)

## 🚀 Quick Deployment

### Prerequisites
- GitHub account
- Render account ([render.com](https://render.com))
- Anthropic API key ([console.anthropic.com](https://console.anthropic.com))
- Trello API key & token

### Deploy in 20 Minutes

Follow the step-by-step guide: **[QUICK_START.md](./QUICK_START.md)**

For detailed configuration: **[DEPLOYMENT.md](./DEPLOYMENT.md)**

## 🧪 Local Development

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/poc-trello-agent.git
cd poc-trello-agent
```

### 2. Set up environment variables
```bash
# Copy example files
cp .env.example .env
cp frontend/.env.example frontend/.env.local

# Edit .env and add your API keys
```

### 3. Start MCP Server
```bash
cd mcp-server
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python server.py
```

### 4. Start Backend
```bash
cd api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### 5. Start Frontend
```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173` to see the app!

## 📁 Project Structure

```
poc-trello-agent/
├── .github/
│   └── workflows/
│       └── deploy-frontend.yml    # GitHub Pages deployment
├── frontend/                       # React frontend
│   ├── src/
│   │   ├── components/            # UI components
│   │   ├── services/              # API client
│   │   └── types/                 # TypeScript types
│   ├── .env.example               # Environment template
│   ├── .env.production            # Production config
│   └── vite.config.ts             # Vite configuration
├── api/                            # FastAPI backend
│   ├── main.py                    # API entry point
│   ├── config.py                  # Configuration
│   ├── claude_service.py          # Claude API integration
│   ├── mcp_client.py              # MCP client
│   ├── session_manager.py         # In-memory sessions
│   ├── render.yaml                # Render config
│   └── requirements.txt           # Python dependencies
├── mcp-server/                     # MCP tool server
│   ├── server.py                  # FastMCP server
│   ├── trello_client.py           # Trello API wrapper
│   ├── render.yaml                # Render config
│   └── requirements.txt           # Python dependencies
├── PROJECT_SPEC.md                 # Full specification
├── DEPLOYMENT.md                   # Detailed deployment guide
├── QUICK_START.md                  # Quick deployment guide
├── .env.example                    # Environment template
└── README.md                       # This file
```

## 🔧 Configuration

### Environment Variables

**Backend (api/.env)**:
- `ANTHROPIC_API_KEY` - Claude API key
- `TRELLO_API_KEY` - Trello API key
- `TRELLO_API_TOKEN` - Trello token
- `TRELLO_DEFAULT_BOARD_ID` - Default board ID
- `CORS_ORIGINS` - Allowed origins (comma-separated)

**Frontend (frontend/.env.local)**:
- `VITE_API_BASE_URL` - Backend API URL

## 📚 API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Main Endpoints

- `POST /api/chat` - Send a chat message
- `POST /api/session/reset` - Reset conversation session
- `GET /api/health` - Health check

## 🧰 MCP Tools

The MCP server provides these tools to Claude:

1. **search_trello_cards** - Search for cards by query, list, or label
2. **get_trello_card_details** - Get full details of a specific card
3. **list_trello_boards** - List available boards
4. **list_trello_lists** - List all lists in a board
5. **create_trello_card** - Create a new card

## ✨ Features

- **Natural conversation** - Claude understands context and asks follow-up questions
- **Multi-turn dialogue** - Gathers ticket information conversationally
- **Request classification** - Automatically categorizes requests
- **Tool use** - Native Claude function calling for Trello operations
- **Session management** - Maintains conversation history
- **Real-time updates** - Shows tool execution in UI

## 🎯 Supported Use Cases

### 1. Information Requests
- "Show me all open IT support tickets"
- "What's the status of ticket XYZ?"
- "List missing report tickets from this week"

### 2. Ticket Creation
- **Missing Report**: "The daily sales report didn't arrive this morning"
- **New Report**: "We need a monthly customer retention report"
- **IT Support**: "My laptop won't connect to VPN"

## 🐛 Troubleshooting

See [DEPLOYMENT.md](./DEPLOYMENT.md#-troubleshooting) for common issues and solutions.

## 📝 License

This is a proof-of-concept project for demonstration purposes.

## 🤝 Contributing

This is a POC project. Feel free to fork and modify for your own use!

## 📞 Support

For issues or questions:
1. Check [DEPLOYMENT.md](./DEPLOYMENT.md#-troubleshooting)
2. Review [PROJECT_SPEC.md](./PROJECT_SPEC.md)
3. Open an issue on GitHub

---

**Built with ❤️ using Claude API**