"""
FastAPI backend for Trello AI Assistant POC.
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from datetime import datetime

from config import settings
from models import (
    ChatRequest,
    ChatResponse,
    SessionResetRequest,
    SessionResetResponse,
    HealthResponse,
    ToolCall
)
from session_manager import session_manager
from claude_service import claude_service
from mcp_client import mcp_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown."""
    # Startup
    logger.info("Starting Trello AI Assistant API...")
    try:
        await mcp_client.connect()
        logger.info("MCP client connected")
    except Exception as e:
        logger.error(f"Failed to connect MCP client: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down Trello AI Assistant API...")
    try:
        await mcp_client.disconnect()
        logger.info("MCP client disconnected")
    except Exception as e:
        logger.error(f"Error disconnecting MCP client: {e}")


# Create FastAPI app
app = FastAPI(
    title="Trello AI Assistant API",
    description="Backend API for AI-assisted Trello ticket management",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )


# Endpoints

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Main chat endpoint for processing user messages.

    Args:
        request: Chat request with session ID and message

    Returns:
        Chat response with assistant message and tool calls
    """
    try:
        logger.info(f"Chat request from session {request.session_id}: {request.message[:50]}...")

        # Get conversation history
        history = session_manager.get_conversation_history(request.session_id)

        # Process message through Claude
        result = await claude_service.process_message(
            user_message=request.message,
            conversation_history=history,
            request_type=None  # Could be enhanced to detect request type
        )

        # Update conversation history
        session_manager.set_conversation_history(
            request.session_id,
            result["updated_history"]
        )

        # Return response
        return ChatResponse(
            message=result["message"],
            tool_calls=result.get("tool_calls", []),
            created_tickets=result.get("created_tickets", []),
            requires_new_chat=result.get("requires_new_chat", False),
            error=result.get("error")
        )

    except Exception as e:
        logger.error(f"Error processing chat request: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )


@app.post("/api/session/reset", response_model=SessionResetResponse)
async def reset_session(request: SessionResetRequest) -> SessionResetResponse:
    """
    Reset a conversation session.

    Args:
        request: Session reset request with session ID

    Returns:
        Reset confirmation
    """
    try:
        logger.info(f"Resetting session: {request.session_id}")

        success = session_manager.clear_session(request.session_id)

        if success:
            return SessionResetResponse(
                success=True,
                message="Session cleared successfully"
            )
        else:
            return SessionResetResponse(
                success=False,
                message="Session not found (may have already expired)"
            )

    except Exception as e:
        logger.error(f"Error resetting session: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error resetting session: {str(e)}"
        )


@app.get("/api/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns:
        Health status of the API and its dependencies
    """
    try:
        # Check Claude API
        claude_healthy = await claude_service.health_check()
        claude_status = "connected" if claude_healthy else "disconnected"

        # Check MCP server
        mcp_healthy = await mcp_client.health_check()
        mcp_status = "connected" if mcp_healthy else "disconnected"

        # Overall status
        overall_status = "healthy" if (claude_healthy and mcp_healthy) else "degraded"

        # Get session count
        active_sessions = session_manager.get_active_session_count()

        return HealthResponse(
            status=overall_status,
            timestamp=datetime.now(),
            claude_api=claude_status,
            mcp_server=mcp_status,
            active_sessions=active_sessions
        )

    except Exception as e:
        logger.error(f"Error in health check: {e}", exc_info=True)
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.now(),
            claude_api="error",
            mcp_server="error",
            active_sessions=0
        )


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Trello AI Assistant API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
