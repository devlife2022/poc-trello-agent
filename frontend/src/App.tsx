import { useState, useEffect, useRef } from 'react';
import { StatusOrb } from './components/StatusOrb';
import { ChatMessage } from './components/ChatMessage';
import { ChatInput } from './components/ChatInput';
import { apiService } from './services/api';
import { getSessionId, resetSession } from './utils/session';
import type { Message, OrbStatus } from './types';
import './App.css';

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [orbStatus, setOrbStatus] = useState<OrbStatus>('ready');
  const [sessionId, setSessionId] = useState<string>(getSessionId());
  const [isLocked, setIsLocked] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (content: string) => {
    if (isLocked) return;

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setOrbStatus('processing');

    try {
      // Send to API
      const response = await apiService.sendMessage({
        session_id: sessionId,
        message: content,
      });

      setOrbStatus('communicating');

      // Add assistant response
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.message,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setOrbStatus('ready');

      // Lock chat only if a Trello action was performed (e.g., card created)
      if (response.requires_new_chat) {
        setIsLocked(true);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setOrbStatus('error');

      // Add error message
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
      // Don't lock on error - allow user to retry
    }
  };

  const handleNewChat = async () => {
    try {
      // Reset session on backend
      await apiService.resetSession(sessionId);
    } catch (error) {
      console.error('Error resetting session:', error);
    }

    // Generate new session ID
    const newSessionId = resetSession();
    setSessionId(newSessionId);

    // Reset UI state
    setMessages([]);
    setIsLocked(false);
    setOrbStatus('ready');
  };

  return (
    <div className="app">
      {/* Cosmic background */}
      <div className="cosmic-bg">
        <div className="stars"></div>
        <div className="stars2"></div>
        <div className="stars3"></div>
      </div>

      {/* Header with orb */}
      <header className="app-header">
        <h1 className="app-title">Trello AI Assistant</h1>
        <StatusOrb status={orbStatus} />
        {isLocked && (
          <button className="new-chat-button" onClick={handleNewChat}>
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <polyline points="1 4 1 10 7 10"></polyline>
              <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"></path>
            </svg>
            New Chat
          </button>
        )}
      </header>

      {/* Chat container */}
      <main className="chat-container">
        <div className="chat-messages">
          {messages.length === 0 ? (
            <div className="welcome-message">
              <h2>Welcome to Trello AI Assistant</h2>
              <p>I can help you:</p>
              <ul>
                <li>Find information about existing Trello tickets</li>
                <li>Create new tickets for missing reports</li>
                <li>Create new report requests</li>
                <li>Handle IT support issues</li>
              </ul>
              <p className="hint">Start by typing your request below...</p>
            </div>
          ) : (
            <>
              {messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>
      </main>

      {/* Input */}
      <ChatInput onSendMessage={handleSendMessage} disabled={isLocked} />
    </div>
  );
}

export default App;
