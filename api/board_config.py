"""
Board routing configuration for mapping request types to Trello boards.
"""
from typing import Dict, Optional

# Board routing configuration
# Maps request types to their corresponding Trello board IDs
BOARD_ROUTING: Dict[str, Dict[str, str]] = {
    "desktop_support": {
        "board_id": "674213d1c000f649b4ad902f",
        "board_name": "Desktop Support"
    },
    "facilities_support": {
        "board_id": "691b97abf5a738a85fb76c02",
        "board_name": "Facilities Support"
    },
    "missing_report": {
        "board_id": "691886780f0565105e671559",
        "board_name": "Engineering"
    },
    "new_report": {
        "board_id": "691886780f0565105e671559",
        "board_name": "Engineering"
    },
    "enhancement_request": {
        "board_id": "691886780f0565105e671559",
        "board_name": "Engineering"
    }
}


def get_board_for_request_type(request_type: Optional[str]) -> Optional[str]:
    """
    Get the appropriate board ID for a given request type.

    Args:
        request_type: The type of request (desktop_support, facilities_support, etc.)

    Returns:
        Board ID if found, None otherwise
    """
    if not request_type:
        return None

    board_config = BOARD_ROUTING.get(request_type)
    if board_config:
        return board_config["board_id"]

    return None


def get_board_name_for_request_type(request_type: Optional[str]) -> Optional[str]:
    """
    Get the board name for a given request type.

    Args:
        request_type: The type of request

    Returns:
        Board name if found, None otherwise
    """
    if not request_type:
        return None

    board_config = BOARD_ROUTING.get(request_type)
    if board_config:
        return board_config["board_name"]

    return None


def get_all_boards() -> Dict[str, Dict[str, str]]:
    """
    Get all board routing configurations.

    Returns:
        Dictionary of all board routing configurations
    """
    return BOARD_ROUTING.copy()
