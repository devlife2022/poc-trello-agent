export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
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
  requires_new_chat?: boolean;
  error?: string;
}

export type OrbStatus = 'ready' | 'processing' | 'communicating' | 'error';
