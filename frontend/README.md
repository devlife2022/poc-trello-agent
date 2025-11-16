# Trello AI Assistant - Frontend

React + TypeScript frontend with a cosmic/space theme for the AI-assisted Trello ticket management POC.

## Features

- **Cosmic Space Theme**: Animated starfield background with gradient effects
- **Glowing Status Orb**: Visual indicator showing system status (Ready, Processing, Communicating, Error)
- **Chat Interface**: Clean message display with user/assistant differentiation
- **Chat Locking**: Automatically locks after first exchange to control context window
- **Session Management**: UUID-based sessions stored in localStorage
- **New Chat Button**: Easy conversation reset with backend session cleanup
- **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

- React 18+ with TypeScript
- Vite (build tool)
- Pure CSS (no external UI frameworks)
- Fetch API for backend communication

## Prerequisites

- Node.js 18+ and npm
- Backend API running on http://localhost:8000

## Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env if needed (default points to localhost:8000)
```

Environment variables:
```env
VITE_API_BASE_URL=http://localhost:8000
```

### 3. Run Development Server

```bash
npm run dev
```

The app will be available at http://localhost:5173

## Building for Production

```bash
# Build
npm run build

# Preview production build
npm run preview
```

The built files will be in the `dist/` directory.

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── StatusOrb.tsx         # Glowing status orb
│   │   ├── StatusOrb.css         # Orb animations
│   │   ├── ChatMessage.tsx       # Message bubble component
│   │   ├── ChatMessage.css       # Message styling
│   │   ├── ChatInput.tsx         # Input field + send button
│   │   └── ChatInput.css         # Input styling
│   ├── services/
│   │   └── api.ts                # API client
│   ├── types/
│   │   └── index.ts              # TypeScript interfaces
│   ├── utils/
│   │   └── session.ts            # Session management
│   ├── App.tsx                   # Main app component
│   ├── App.css                   # Main app styling + cosmic theme
│   ├── index.css                 # Global styles
│   └── main.tsx                  # React entry point
├── .env.example                  # Environment template
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

## Features Explained

### Cosmic Theme

The background features three layers of animated stars moving at different speeds, creating a parallax effect. The color scheme uses deep space blues and purples with glowing elements.

### Status Orb

The orb has four states:
- **Ready** (Blue): Calm pulsing, waiting for input
- **Processing** (Purple): Faster pulsing with throb animation
- **Communicating** (Green/Cyan): Rotating hue with rapid pulse
- **Error** (Red): Shake animation on error

### Chat Locking

After sending the first message:
- Input field is disabled
- "New Chat" button appears
- Prevents multiple requests in same conversation
- Helps control Claude's context window size

### Session Management

- Generates UUID on first visit
- Stores in localStorage
- Persists across page refreshes
- "New Chat" generates new session ID
- Backend session is also reset

## Usage

1. **Start Conversation**: Type a message and hit Enter or click Send
2. **Wait for Response**: Watch the orb change states (Processing → Communicating → Ready)
3. **Read Response**: Assistant message appears below your message
4. **Start New Chat**: Click "New Chat" button to reset and ask another question

## Chat Flow

```
User types message
    ↓
Message sent to backend
    ↓
Orb shows "Processing"
    ↓
Backend processes with Claude
    ↓
Orb shows "Communicating"
    ↓
Response received
    ↓
Orb shows "Ready"
    ↓
Chat locks (input disabled)
    ↓
"New Chat" button appears
```

## API Integration

The frontend communicates with the backend via three endpoints:

### POST /api/chat
Send user message and receive assistant response.

### POST /api/session/reset
Clear backend session history.

### GET /api/health
Check backend health.

## Troubleshooting

### "Cannot connect to backend"

**Check:**
1. Backend is running on http://localhost:8000
2. CORS is configured correctly in backend
3. `.env` has correct API_BASE_URL

### Messages not sending

**Check:**
1. Input is not disabled (check if locked)
2. Backend health endpoint returns 200
3. Network tab shows request is sent

## Browser Support

- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- IE11: ❌ Not supported

## License

Part of the Trello AI Assistant POC project.
