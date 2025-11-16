"""
In-memory session manager for storing conversation history.
"""
from typing import Dict, List, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages conversation sessions in memory."""

    def __init__(self, session_timeout_minutes: int = 60):
        """
        Initialize the session manager.

        Args:
            session_timeout_minutes: Minutes of inactivity before session expires
        """
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = timedelta(minutes=session_timeout_minutes)

    def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get conversation history for a session.

        Args:
            session_id: Session identifier

        Returns:
            List of messages in the conversation
        """
        self._cleanup_expired_sessions()

        if session_id not in self.sessions:
            logger.info(f"Creating new session: {session_id}")
            self.sessions[session_id] = {
                "messages": [],
                "created_at": datetime.now(),
                "last_activity": datetime.now()
            }

        # Update last activity
        self.sessions[session_id]["last_activity"] = datetime.now()

        return self.sessions[session_id]["messages"]

    def add_message(self, session_id: str, message: Dict[str, Any]) -> None:
        """
        Add a message to the conversation history.

        Args:
            session_id: Session identifier
            message: Message to add (dict with 'role' and 'content')
        """
        if session_id not in self.sessions:
            self.get_conversation_history(session_id)  # Initialize if needed

        self.sessions[session_id]["messages"].append(message)
        self.sessions[session_id]["last_activity"] = datetime.now()

        logger.debug(f"Added message to session {session_id}: {message.get('role')}")

    def set_conversation_history(self, session_id: str, messages: List[Dict[str, Any]]) -> None:
        """
        Replace the entire conversation history for a session.

        Args:
            session_id: Session identifier
            messages: Complete list of messages
        """
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "messages": [],
                "created_at": datetime.now(),
                "last_activity": datetime.now()
            }

        self.sessions[session_id]["messages"] = messages
        self.sessions[session_id]["last_activity"] = datetime.now()

        logger.debug(f"Set conversation history for session {session_id}: {len(messages)} messages")

    def clear_session(self, session_id: str) -> bool:
        """
        Clear a specific session.

        Args:
            session_id: Session identifier

        Returns:
            True if session existed and was cleared, False otherwise
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Cleared session: {session_id}")
            return True
        return False

    def get_active_session_count(self) -> int:
        """
        Get the number of active sessions.

        Returns:
            Number of sessions
        """
        self._cleanup_expired_sessions()
        return len(self.sessions)

    def _cleanup_expired_sessions(self) -> None:
        """Remove sessions that have been inactive for too long."""
        now = datetime.now()
        expired_sessions = [
            session_id
            for session_id, data in self.sessions.items()
            if now - data["last_activity"] > self.session_timeout
        ]

        for session_id in expired_sessions:
            del self.sessions[session_id]
            logger.info(f"Expired session removed: {session_id}")

    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """
        Get information about a session.

        Args:
            session_id: Session identifier

        Returns:
            Dictionary with session metadata
        """
        if session_id not in self.sessions:
            return {
                "exists": False
            }

        data = self.sessions[session_id]
        return {
            "exists": True,
            "message_count": len(data["messages"]),
            "created_at": data["created_at"],
            "last_activity": data["last_activity"],
            "age_minutes": (datetime.now() - data["created_at"]).total_seconds() / 60
        }


# Global session manager instance
session_manager = SessionManager(session_timeout_minutes=60)
