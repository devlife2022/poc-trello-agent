import type { Message } from '../types';
import './ChatMessage.css';

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const formattedTime = message.timestamp.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <div className={`chat-message chat-message--${message.role}`}>
      <div className="message-bubble">
        <div className="message-content">{message.content}</div>
        <div className="message-time">{formattedTime}</div>
      </div>
    </div>
  );
}
