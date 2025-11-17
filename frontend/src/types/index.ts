export interface CreatedTicket {
  id: string;
  name: string;
  url: string;
  board_name: string;
  list_name: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  created_tickets?: CreatedTicket[];
}

export interface ToolCall {
  tool: string;
  status: 'executing' | 'success' | 'error';
  error?: string;
}

export interface ChatRequest {
  session_id: string;
  message: string;
}

export interface ChatResponse {
  message: string;
  tool_calls?: ToolCall[];
  created_tickets?: CreatedTicket[];
  requires_new_chat?: boolean;
  error?: string;
}

export type OrbStatus = 'ready' | 'processing' | 'communicating' | 'error';
