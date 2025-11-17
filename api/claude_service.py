"""
Claude API service for handling conversations and tool use.
"""
from typing import List, Dict, Any, Optional
import logging
import json
from anthropic import Anthropic
from config import settings
from mcp_client import mcp_client
from prompt_manager import prompt_manager
from board_config import get_board_for_request_type, get_all_boards
from models import ToolCall

logger = logging.getLogger(__name__)


class ClaudeService:
    """Service for interacting with Claude API."""

    def __init__(self):
        """Initialize the Claude service."""
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.claude_model
        self.max_tokens = settings.claude_max_tokens

    async def process_message(
        self,
        user_message: str,
        conversation_history: List[Dict[str, Any]],
        request_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a user message through Claude with tool execution loop.

        Args:
            user_message: The user's message
            conversation_history: Previous conversation messages
            request_type: Optional request type for specialized prompts

        Returns:
            Dictionary with response message and tool calls made
        """
        # Ensure MCP client is connected
        if not await mcp_client.health_check():
            raise Exception("MCP server not available")

        # Get system prompt
        system_prompt = prompt_manager.get_system_prompt(request_type)

        # Add board routing information to system prompt
        board_routing_info = self._get_board_routing_info()
        system_prompt = f"{system_prompt}\n\n{board_routing_info}"

        # Build messages array with conversation history + new message
        messages = conversation_history.copy()
        messages.append({"role": "user", "content": user_message})

        # Get tool definitions
        tools = mcp_client.get_tools()

        # Track tool calls made
        tool_calls_made: List[ToolCall] = []

        # Track created tickets
        created_tickets = []

        # Track if any action-requiring tools were executed (tools that modify Trello)
        action_tools_executed = False
        action_tool_names = set()  # Empty set - don't auto-lock after ticket creation (allows multi-ticket conversations)

        # Tool execution loop
        max_iterations = 10  # Prevent infinite loops
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            try:
                # Call Claude API
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    system=system_prompt,
                    messages=messages,
                    tools=tools if tools else None
                )

                # Check if response contains tool use
                tool_use_blocks = [
                    block for block in response.content
                    if block.type == "tool_use"
                ]

                if not tool_use_blocks:
                    # No more tool calls, we have the final response
                    final_text = "".join([
                        block.text for block in response.content
                        if block.type == "text"
                    ])

                    # Add assistant response to history
                    messages.append({
                        "role": "assistant",
                        "content": response.content
                    })

                    logger.info(f"Conversation completed in {iteration} iterations")

                    return {
                        "message": final_text,
                        "tool_calls": tool_calls_made,
                        "created_tickets": created_tickets,
                        "requires_new_chat": action_tools_executed,
                        "updated_history": messages
                    }

                # Execute tool calls
                tool_results = []
                for tool_use in tool_use_blocks:
                    tool_name = tool_use.name
                    tool_input = tool_use.input

                    logger.info(f"Tool requested: {tool_name}")

                    try:
                        # Execute tool via MCP
                        result = await mcp_client.execute_tool(tool_name, tool_input)

                        # Check if this is an action tool that was successfully executed
                        if tool_name in action_tool_names:
                            action_tools_executed = True

                        # Track created tickets
                        if tool_name == "create_trello_card":
                            ticket_info = self._extract_ticket_info(result, tool_input)
                            if ticket_info:
                                created_tickets.append(ticket_info)

                        # Format result for Claude
                        result_content = self._format_tool_result(result)

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_use.id,
                            "content": result_content
                        })

                        tool_calls_made.append(ToolCall(
                            tool=tool_name,
                            status="success"
                        ))

                    except Exception as e:
                        logger.error(f"Tool execution failed for {tool_name}: {e}")

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_use.id,
                            "content": f"Error executing tool: {str(e)}",
                            "is_error": True
                        })

                        tool_calls_made.append(ToolCall(
                            tool=tool_name,
                            status="error",
                            error=str(e)
                        ))

                # Add assistant response with tool use to history
                messages.append({
                    "role": "assistant",
                    "content": response.content
                })

                # Add tool results as next user message
                messages.append({
                    "role": "user",
                    "content": tool_results
                })

                # Continue loop to get Claude's response to the tool results

            except Exception as e:
                logger.error(f"Error in Claude API call: {e}")
                raise

        # If we hit max iterations, return what we have
        logger.warning(f"Reached max iterations ({max_iterations})")
        return {
            "message": "I apologize, but I'm having trouble completing this request. Please try again or rephrase your question.",
            "tool_calls": tool_calls_made,
            "created_tickets": created_tickets,
            "requires_new_chat": action_tools_executed,
            "updated_history": messages,
            "error": "Max iterations reached"
        }

    def _get_board_routing_info(self) -> str:
        """
        Generate board routing information to include in system prompt.

        Returns:
            Formatted string with board routing instructions
        """
        boards = get_all_boards()

        routing_info = "BOARD ROUTING:\n"
        routing_info += "When creating tickets, you MUST use the correct board_id based on the request type:\n\n"

        for request_type, board_config in boards.items():
            routing_info += f"- {request_type}: board_id=\"{board_config['board_id']}\" ({board_config['board_name']})\n"

        routing_info += "\nIMPORTANT: Always include the board_id parameter when calling create_trello_card to ensure tickets are created on the correct board."

        return routing_info

    def _extract_ticket_info(self, result: Any, tool_input: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """
        Extract ticket information from create_trello_card result.

        Args:
            result: Tool execution result
            tool_input: Original tool input parameters

        Returns:
            Dictionary with ticket info or None if extraction fails
        """
        try:
            # Parse result if it's a list of ContentBlock objects
            result_dict = {}
            if isinstance(result, list):
                # Extract text from ContentBlock objects
                for item in result:
                    if hasattr(item, 'text'):
                        result_dict = json.loads(item.text)
                        break
            elif isinstance(result, str):
                result_dict = json.loads(result)
            elif isinstance(result, dict):
                result_dict = result
            else:
                return None

            # Check if card was created successfully
            if not result_dict.get("success"):
                return None

            card_data = result_dict.get("card", {})
            board_id = tool_input.get("board_id", "")

            # Get board name from board_id
            board_name = "Unknown Board"
            for req_type, board_config in get_all_boards().items():
                if board_config["board_id"] == board_id:
                    board_name = board_config["board_name"]
                    break

            return {
                "id": card_data.get("id", ""),
                "name": card_data.get("name", ""),
                "url": card_data.get("url", ""),
                "board_name": board_name,
                "list_name": card_data.get("list_name", "")
            }

        except Exception as e:
            logger.error(f"Error extracting ticket info: {e}")
            return None

    def _format_tool_result(self, result: Any) -> str:
        """
        Format tool result for Claude.

        Args:
            result: Tool execution result (may be list of ContentBlock objects from MCP)

        Returns:
            Formatted string result
        """
        if isinstance(result, str):
            return result
        elif isinstance(result, list):
            # Handle list of ContentBlock objects from MCP
            # Each ContentBlock may have a .text attribute (TextContent)
            text_parts = []
            for item in result:
                if hasattr(item, 'text'):
                    # TextContent object - extract the text
                    text_parts.append(item.text)
                elif hasattr(item, 'type') and item.type == 'text' and hasattr(item, 'text'):
                    # Alternative check for TextContent
                    text_parts.append(item.text)
                elif isinstance(item, str):
                    text_parts.append(item)
                elif isinstance(item, dict):
                    # If it's a dict, serialize it
                    text_parts.append(json.dumps(item, indent=2))
                else:
                    # Fallback to string representation
                    text_parts.append(str(item))

            return '\n'.join(text_parts) if text_parts else str(result)
        elif isinstance(result, dict):
            return json.dumps(result, indent=2)
        else:
            return str(result)

    async def health_check(self) -> bool:
        """
        Check if Claude API is accessible.

        Returns:
            True if accessible, False otherwise
        """
        try:
            # Simple check - just verify we have a client and API key
            return bool(self.client and settings.anthropic_api_key)
        except Exception:
            return False


# Global Claude service instance
claude_service = ClaudeService()
