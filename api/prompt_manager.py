"""
Prompt management system for handling base and request-type specific prompts.
"""
from pathlib import Path
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class PromptManager:
    """Manages system prompts with support for base and request-type specific prompts."""

    def __init__(self, prompts_dir: str = "prompts"):
        """
        Initialize the prompt manager.

        Args:
            prompts_dir: Directory containing prompt files
        """
        self.prompts_dir = Path(__file__).parent / prompts_dir
        self.base_prompt: Optional[str] = None
        self.request_type_prompts: Dict[str, str] = {}
        self._load_prompts()

    def _load_prompts(self) -> None:
        """Load all prompt files from the prompts directory."""
        try:
            # Load base prompt
            base_prompt_path = self.prompts_dir / "base_prompt.txt"
            if base_prompt_path.exists():
                self.base_prompt = base_prompt_path.read_text(encoding="utf-8")
                logger.info("Loaded base prompt")
            else:
                logger.warning(f"Base prompt not found at {base_prompt_path}")
                self.base_prompt = self._get_fallback_base_prompt()

            # Load request type prompts
            request_types = ["missing_report", "new_report", "it_support", "enhancement_request"]
            for request_type in request_types:
                prompt_path = self.prompts_dir / f"{request_type}.txt"
                if prompt_path.exists():
                    self.request_type_prompts[request_type] = prompt_path.read_text(encoding="utf-8")
                    logger.info(f"Loaded {request_type} prompt")
                else:
                    logger.warning(f"Prompt for {request_type} not found at {prompt_path}")

        except Exception as e:
            logger.error(f"Error loading prompts: {e}")
            self.base_prompt = self._get_fallback_base_prompt()

    def _get_fallback_base_prompt(self) -> str:
        """Return a basic fallback prompt if file loading fails."""
        return """You are a helpful Trello ticket management assistant.
Help users find information about existing tickets and create new tickets when needed.
Be conversational, ask clarifying questions, and confirm details before taking actions."""

    def get_system_prompt(self, request_type: Optional[str] = None) -> str:
        """
        Get the complete system prompt, optionally including request-type specific instructions.

        Args:
            request_type: Optional request type (missing_report, new_report, it_support, enhancement_request)

        Returns:
            Complete system prompt
        """
        if not self.base_prompt:
            return self._get_fallback_base_prompt()

        # Start with base prompt
        prompt = self.base_prompt

        # Add request-type specific instructions if available
        if request_type and request_type in self.request_type_prompts:
            # Replace placeholder with actual instructions
            placeholder = "[PLACEHOLDER: Request-type specific instructions will be inserted here based on classification]"
            if placeholder in prompt:
                prompt = prompt.replace(placeholder, self.request_type_prompts[request_type])
            else:
                # If no placeholder, append to end
                prompt += "\n\n" + self.request_type_prompts[request_type]

            logger.debug(f"Using system prompt with {request_type} instructions")
        else:
            # Remove placeholder if no specific type
            placeholder = "[PLACEHOLDER: Request-type specific instructions will be inserted here based on classification]"
            prompt = prompt.replace(placeholder, "")
            logger.debug("Using base system prompt only")

        return prompt.strip()

    def reload_prompts(self) -> None:
        """Reload all prompts from disk (useful for development)."""
        logger.info("Reloading prompts...")
        self._load_prompts()

    def get_available_request_types(self) -> list:
        """Get list of available request types."""
        return list(self.request_type_prompts.keys())


# Global prompt manager instance
prompt_manager = PromptManager()
