"""
Simple test script for Trello client - tests without MCP layer.
Run this to verify your Trello API credentials and basic functionality.
"""
import sys

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from trello_client import TrelloClient
import json


def print_json(data):
    """Pretty print JSON data."""
    print(json.dumps(data, indent=2))


def main():
    print("=" * 60)
    print("Testing Trello Client")
    print("=" * 60)

    try:
        # Initialize client
        print("\n1. Initializing Trello client...")
        client = TrelloClient()
        print("✓ Client initialized successfully")
        print(f"  Default Board ID: {client.default_board_id}")

        # Test: List boards
        print("\n2. Testing: List all boards")
        boards = client.get_boards()
        print(f"✓ Found {len(boards)} boards:")
        for board in boards:
            print(f"  - {board['name']} (ID: {board['id']})")

        if not boards:
            print("\n⚠ No boards found. Please create a Trello board first.")
            return

        # Test: Get lists from first board (or default board)
        test_board_id = client.default_board_id or boards[0]['id']
        print(f"\n3. Testing: Get lists from board {test_board_id}")
        lists = client.get_lists(test_board_id)
        print(f"✓ Found {len(lists)} lists:")
        for lst in lists:
            print(f"  - {lst['name']} (ID: {lst['id']}, Cards: {lst['card_count']})")

        # Test: Search for cards
        print(f"\n4. Testing: Search for cards in board")
        search_result = client.search_cards(board_id=test_board_id, limit=5)
        print(f"✓ Found {search_result['count']} cards:")
        for card in search_result['cards']:
            print(f"  - {card['name']}")
            print(f"    List: {card['list_name']}")
            print(f"    Labels: {', '.join(card['labels']) if card['labels'] else 'None'}")
            print(f"    URL: {card['url']}")

        # Test: Get card details (if any cards exist)
        if search_result['cards']:
            first_card_id = search_result['cards'][0]['id']
            print(f"\n5. Testing: Get details for card {first_card_id}")
            details = client.get_card_details(first_card_id)
            print(f"✓ Card details retrieved:")
            print(f"  Name: {details['name']}")
            print(f"  List: {details['list_name']}")
            print(f"  Members: {', '.join(details['members']) if details['members'] else 'None'}")
            print(f"  Comments: {len(details['comments'])}")
        else:
            print("\n⚠ No cards found to test card details")

        # Test: Create card (optional - uncomment to test)
        print("\n6. Testing: Create new card")
        print("⚠ Skipping card creation test to avoid cluttering your board")
        print("  To test card creation, uncomment the code in this script")

        # Uncomment below to test card creation:
        """
        if lists:
            test_list_id = lists[0]['id']
            print(f"  Creating test card in list: {lists[0]['name']}")
            create_result = client.create_card(
                board_id=test_board_id,
                list_id=test_list_id,
                name="Test Card - MCP Server",
                desc="This is a test card created by the MCP server test script",
                labels=["IT Support"],  # Adjust based on your board's labels
            )
            if create_result['success']:
                print(f"✓ Card created successfully:")
                print(f"  Name: {create_result['card']['name']}")
                print(f"  URL: {create_result['card']['url']}")
            else:
                print(f"✗ Card creation failed: {create_result.get('error')}")
        """

        print("\n" + "=" * 60)
        print("✓ All tests completed successfully!")
        print("=" * 60)

    except ValueError as e:
        print(f"\n✗ Configuration Error: {e}")
        print("\nMake sure you have:")
        print("1. Created a .env file (copy from .env.example)")
        print("2. Added your TRELLO_API_KEY")
        print("3. Added your TRELLO_API_TOKEN")
        print("4. Added your TRELLO_DEFAULT_BOARD_ID (optional)")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nDebug information:")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
