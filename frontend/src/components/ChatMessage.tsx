import type { Message } from '../types';
import { TicketCard } from './TicketCard';
import './ChatMessage.css';
import ReactMarkdown from 'react-markdown';

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
        {/* Show created tickets first, before the message */}
        {message.created_tickets && message.created_tickets.length > 0 && (
          <div className="created-tickets">
            {message.created_tickets.map((ticket) => (
              <TicketCard key={ticket.id} ticket={ticket} />
            ))}
          </div>
        )}

        {/* Then show the message content */}
        <div className="message-content">
          <ReactMarkdown>{message.content}</ReactMarkdown>
        </div>

        <div className="message-time">{formattedTime}</div>
      </div>
    </div>
  );
}
