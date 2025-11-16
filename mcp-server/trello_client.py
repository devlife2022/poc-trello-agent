"""
Trello API client wrapper for interacting with Trello REST API v1.
"""
import os
import requests
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class TrelloClient:
    """Wrapper for Trello API interactions."""

    BASE_URL = "https://api.trello.com/1"

    def __init__(self):
        self.api_key = os.getenv("TRELLO_API_KEY")
        self.api_token = os.getenv("TRELLO_API_TOKEN")
        self.default_board_id = os.getenv("TRELLO_DEFAULT_BOARD_ID")

        if not self.api_key or not self.api_token:
            raise ValueError("TRELLO_API_KEY and TRELLO_API_TOKEN must be set in environment")

    def _get_auth_params(self) -> Dict[str, str]:
        """Get authentication parameters for API requests."""
        return {
            "key": self.api_key,
            "token": self.api_token
        }

    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None,
                     data: Optional[Dict] = None) -> Any:
        """Make an authenticated request to Trello API."""
        url = f"{self.BASE_URL}/{endpoint}"
        auth_params = self._get_auth_params()

        if params:
            params.update(auth_params)
        else:
            params = auth_params

        try:
            if method == "GET":
                response = requests.get(url, params=params, timeout=10)
            elif method == "POST":
                response = requests.post(url, params=params, json=data, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Trello API request failed: {str(e)}")

    def get_boards(self) -> List[Dict[str, Any]]:
        """Get all boards for the authenticated user."""
        boards = self._make_request("GET", "members/me/boards")
        return [
            {
                "id": board["id"],
                "name": board["name"],
                "url": board.get("url", "")
            }
            for board in boards
        ]

    def get_lists(self, board_id: str) -> List[Dict[str, Any]]:
        """Get all lists in a board."""
        lists = self._make_request("GET", f"boards/{board_id}/lists")

        # Get card counts for each list
        result = []
        for lst in lists:
            cards = self._make_request("GET", f"lists/{lst['id']}/cards")
            result.append({
                "id": lst["id"],
                "name": lst["name"],
                "card_count": len(cards)
            })

        return result

    def search_cards(self, board_id: Optional[str] = None, query: Optional[str] = None,
                    list_name: Optional[str] = None, label: Optional[str] = None,
                    limit: int = 10) -> Dict[str, Any]:
        """
        Search for cards based on various criteria.

        Args:
            board_id: Board to search in (defaults to default board)
            query: Text search in card names and descriptions
            list_name: Filter by list name
            label: Filter by label name
            limit: Maximum number of cards to return
        """
        board_id = board_id or self.default_board_id
        if not board_id:
            raise ValueError("board_id must be provided or TRELLO_DEFAULT_BOARD_ID must be set")

        # Get all cards from the board
        cards = self._make_request("GET", f"boards/{board_id}/cards")

        # Get board lists for list name mapping
        lists = self._make_request("GET", f"boards/{board_id}/lists")
        list_map = {lst["id"]: lst["name"] for lst in lists}

        # Get board labels for label mapping
        labels_data = self._make_request("GET", f"boards/{board_id}/labels")

        # Filter cards based on criteria
        filtered_cards = []
        for card in cards:
            # Apply filters
            if query and query.lower() not in card["name"].lower() and query.lower() not in card.get("desc", "").lower():
                continue

            card_list_name = list_map.get(card["idList"], "")
            if list_name and list_name.lower() not in card_list_name.lower():
                continue

            # Get card labels
            card_label_names = []
            for label_id in card.get("idLabels", []):
                for lbl in labels_data:
                    if lbl["id"] == label_id:
                        card_label_names.append(lbl["name"])

            if label and not any(label.lower() in lbl.lower() for lbl in card_label_names):
                continue

            # Add to results
            filtered_cards.append({
                "id": card["id"],
                "name": card["name"],
                "desc": card.get("desc", ""),
                "list_name": card_list_name,
                "labels": card_label_names,
                "due": card.get("due"),
                "url": card.get("url", "")
            })

            if len(filtered_cards) >= limit:
                break

        return {
            "cards": filtered_cards,
            "count": len(filtered_cards)
        }

    def get_card_details(self, card_id: str) -> Dict[str, Any]:
        """Get full details of a specific card."""
        # Get card data
        card = self._make_request("GET", f"cards/{card_id}")

        # Get list name
        list_data = self._make_request("GET", f"lists/{card['idList']}")
        list_name = list_data["name"]

        # Get label names
        label_names = [label["name"] for label in card.get("labels", [])]

        # Get members
        members = [member["username"] for member in card.get("members", [])]

        # Get comments (actions of type commentCard)
        actions = self._make_request("GET", f"cards/{card_id}/actions",
                                     params={"filter": "commentCard"})
        comments = [
            {
                "date": action["date"],
                "author": action["memberCreator"]["username"],
                "text": action["data"]["text"]
            }
            for action in actions
        ]

        return {
            "id": card["id"],
            "name": card["name"],
            "desc": card.get("desc", ""),
            "list_name": list_name,
            "labels": label_names,
            "due": card.get("due"),
            "members": members,
            "comments": comments,
            "attachments": card.get("attachments", []),
            "url": card.get("url", "")
        }

    def create_card(self, board_id: Optional[str], list_id: str, name: str,
                   desc: str = "", labels: Optional[List[str]] = None,
                   due: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new Trello card.

        Args:
            board_id: Board to create card in
            list_id: List to create card in
            name: Card title
            desc: Card description
            labels: List of label names to apply
            due: Due date (ISO format string)
        """
        board_id = board_id or self.default_board_id
        if not board_id:
            raise ValueError("board_id must be provided or TRELLO_DEFAULT_BOARD_ID must be set")

        # Prepare card data
        card_data = {
            "idList": list_id,
            "name": name,
            "desc": desc
        }

        if due:
            card_data["due"] = due

        # Create card
        card = self._make_request("POST", "cards", data=card_data)

        # Add labels if specified
        if labels:
            # Get board labels
            board_labels = self._make_request("GET", f"boards/{board_id}/labels")
            label_map = {lbl["name"].lower(): lbl["id"] for lbl in board_labels}

            # Add matching labels to card
            for label_name in labels:
                label_id = label_map.get(label_name.lower())
                if label_id:
                    self._make_request("POST", f"cards/{card['id']}/idLabels",
                                      params={"value": label_id})

        # Get list name for response
        list_data = self._make_request("GET", f"lists/{list_id}")

        return {
            "success": True,
            "card": {
                "id": card["id"],
                "name": card["name"],
                "url": card.get("url", ""),
                "list_name": list_data["name"]
            }
        }
