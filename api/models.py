"""
Pydantic models for API requests and responses.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Literal
from datetime import datetime


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    session_id: str = Field(..., description="Unique session identifier")
    message: str = Field(..., min_length=1, description="User message")


class ToolCall(BaseModel):
    """Information about a tool call made during processing."""
    tool: str = Field(..., description="Name of the tool called")
    status: Literal["executing", "success", "error"] = Field(..., description="Tool execution status")
    error: Optional[str] = Field(None, description="Error message if status is error")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    message: str = Field(..., description="Assistant's response message")
    tool_calls: List[ToolCall] = Field(default_factory=list, description="List of tool calls made")
    requires_new_chat: bool = Field(default=False, description="Whether this response requires starting a new chat (e.g., Trello card was created)")
    error: Optional[str] = Field(None, description="Error message if request failed")


class SessionResetRequest(BaseModel):
    """Request model for session reset endpoint."""
    session_id: str = Field(..., description="Session ID to reset")


class SessionResetResponse(BaseModel):
    """Response model for session reset endpoint."""
    success: bool = Field(..., description="Whether reset was successful")
    message: str = Field(..., description="Status message")


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(..., description="Overall health status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Current server time")
    claude_api: str = Field(..., description="Claude API connection status")
    mcp_server: str = Field(..., description="MCP server connection status")
    active_sessions: int = Field(..., description="Number of active sessions")


class Message(BaseModel):
    """Individual message in conversation history."""
    role: Literal["user", "assistant"] = Field(..., description="Message role")
    content: Any = Field(..., description="Message content (can be text or structured blocks)")
