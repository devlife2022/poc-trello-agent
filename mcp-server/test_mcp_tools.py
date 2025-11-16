"""
Test script for MCP tools - tests the Trello client functions directly.
This simulates the functionality that the MCP tools will use.
"""
import sys

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import json
from trello_client import TrelloClient


def print_json(data):
    """Pretty print JSON data."""
    print(json.dumps(data, indent=2))


def main():
    print("=" * 60)
    print("Testing MCP Tool Functions")
    print("=" * 60)

    try:
        # Initialize client
        client = TrelloClient()
        print("✓ Trello client initialized")

        # Test 1: List boards
        print("\n1. Testing: get_boards()")
        print("-" * 60)
        boards = client.get_boards()
        result = {"boards": boards}
        print_json(result)

        if not boards:
            print("\n⚠ No boards found. Create a Trello board first.")
            return

        # Get a board ID to test with
        test_board_id = boards[0]['id']
        print(f"\nUsing board: {boards[0]['name']} (ID: {test_board_id})")

        # Test 2: List lists in board
        print("\n2. Testing: get_lists(board_id)")
        print("-" * 60)
        lists = client.get_lists(test_board_id)
        result = {"lists": lists}
        print_json(result)

        if not lists:
            print("\n⚠ No lists found in board. Create some lists first.")
            return

        # Test 3: Search cards
        print("\n3. Testing: search_cards(limit=5)")
        print("-" * 60)
        result = client.search_cards(board_id=test_board_id, limit=5)
        print_json(result)

        cards = result.get('cards', [])

        # Test 4: Get card details (if cards exist)
        if cards:
            print("\n4. Testing: get_card_details(card_id)")
            print("-" * 60)
            test_card_id = cards[0]['id']
            details = client.get_card_details(test_card_id)
            print_json(details)
        else:
            print("\n⚠ No cards found to test get_card_details")

        # Test 5: Search with filters
        print("\n5. Testing: search_cards(query='test', limit=3)")
        print("-" * 60)
        result = client.search_cards(board_id=test_board_id, query="test", limit=3)
        print_json(result)

        # Test 6: Create card (optional)
        print("\n6. Testing: create_card()")
        print("-" * 60)
        print("⚠ Skipping to avoid cluttering your board")
        print("Uncomment the code below to test card creation")

        """
        # Uncomment to test card creation
        if lists:
            test_list_id = lists[0]['id']
            result = client.create_card(
                board_id=test_board_id,
                list_id=test_list_id,
                name="Test Card from MCP Tool",
                desc="Created via test_mcp_tools.py script",
                labels=["IT Support"]  # Adjust based on your labels
            )
            print_json(result)
        """

        print("\n" + "=" * 60)
        print("✓ All MCP tool function tests completed!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
