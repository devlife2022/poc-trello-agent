import type { CreatedTicket } from '../types';
import './TicketCard.css';

interface TicketCardProps {
  ticket: CreatedTicket;
}

export function TicketCard({ ticket }: TicketCardProps) {
  return (
    <a
      href={ticket.url}
      target="_blank"
      rel="noopener noreferrer"
      className="ticket-card"
    >
      <div className="ticket-header">
        <span className="ticket-icon">🎫</span>
        <span className="ticket-board">{ticket.board_name}</span>
      </div>
      <div className="ticket-title">{ticket.name}</div>
      <div className="ticket-footer">
        <span className="ticket-list">{ticket.list_name}</span>
        <span className="ticket-link">
          View in Trello <span className="arrow">→</span>
        </span>
      </div>
    </a>
  );
}
