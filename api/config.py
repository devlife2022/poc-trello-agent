"""
Configuration management for the FastAPI backend.
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Claude API Configuration
    anthropic_api_key: str
    claude_model: str = "claude-sonnet-4-20250514"
    claude_max_tokens: int = 4096

    # MCP Server Configuration
    mcp_server_command: str = "python"
    mcp_server_args: str = "../mcp-server/server.py"

    # API Configuration
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins string into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def mcp_server_args_list(self) -> List[str]:
        """Parse MCP server args into a list."""
        return [arg.strip() for arg in self.mcp_server_args.split(",") if arg.strip()]


# Global settings instance
settings = Settings()
