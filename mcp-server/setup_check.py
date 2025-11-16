"""
Quick setup check script - verifies your environment is ready for testing.
Run this first before running any other tests.
"""
import os
import sys
from pathlib import Path

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def check_file_exists(filepath, description):
    """Check if a file exists."""
    if Path(filepath).exists():
        print(f"✓ {description}")
        return True
    else:
        print(f"✗ {description}")
        return False


def check_env_var(var_name, required=True):
    """Check if an environment variable is set."""
    value = os.getenv(var_name)
    if value:
        # Mask the value for security
        masked = value[:4] + "..." + value[-4:] if len(value) > 8 else "***"
        print(f"✓ {var_name} is set ({masked})")
        return True
    else:
        status = "✗" if required else "⚠"
        print(f"{status} {var_name} is not set" + (" (required)" if required else " (optional)"))
        return not required


def check_python_version():
    """Check Python version."""
    version = sys.version_info
    if version >= (3, 11):
        print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"⚠ Python version: {version.major}.{version.minor}.{version.micro} (3.11+ recommended)")
        return True


def check_package_installed(package_name):
    """Check if a Python package is installed."""
    try:
        __import__(package_name)
        print(f"✓ {package_name} is installed")
        return True
    except ImportError:
        print(f"✗ {package_name} is not installed")
        return False


def main():
    print("=" * 70)
    print("MCP Server Setup Check")
    print("=" * 70)

    all_checks_passed = True

    # Check 1: Python version
    print("\n1. Checking Python version...")
    all_checks_passed &= check_python_version()

    # Check 2: Required files
    print("\n2. Checking required files...")
    all_checks_passed &= check_file_exists("server.py", "server.py exists")
    all_checks_passed &= check_file_exists("trello_client.py", "trello_client.py exists")
    all_checks_passed &= check_file_exists("requirements.txt", "requirements.txt exists")

    env_exists = check_file_exists(".env", ".env file exists")
    if not env_exists:
        print("  → Run: cp .env.example .env")
        print("  → Then edit .env with your Trello credentials")
    all_checks_passed &= env_exists

    # Check 3: Environment variables (load from .env if it exists)
    if env_exists:
        print("\n3. Checking environment variables...")
        from dotenv import load_dotenv
        load_dotenv()

        all_checks_passed &= check_env_var("TRELLO_API_KEY", required=True)
        all_checks_passed &= check_env_var("TRELLO_API_TOKEN", required=True)
        check_env_var("TRELLO_DEFAULT_BOARD_ID", required=False)
    else:
        print("\n3. Skipping environment variable check (.env not found)")

    # Check 4: Python packages
    print("\n4. Checking Python packages...")
    packages_ok = True
    packages_ok &= check_package_installed("dotenv")
    packages_ok &= check_package_installed("requests")
    packages_ok &= check_package_installed("fastmcp")
    packages_ok &= check_package_installed("pydantic")

    if not packages_ok:
        print("  → Run: pip install -r requirements.txt")
    all_checks_passed &= packages_ok

    # Summary
    print("\n" + "=" * 70)
    if all_checks_passed:
        print("✓ Setup check passed! You're ready to test the MCP server.")
        print("\nNext steps:")
        print("  1. Run: python test_trello_client.py")
        print("  2. If that works, run: python test_mcp_tools.py")
        print("  3. See TESTING.md for detailed testing guide")
    else:
        print("✗ Setup check found issues. Please fix the items marked with ✗ above.")
        print("\nQuick fix checklist:")
        print("  □ Create .env file: cp .env.example .env")
        print("  □ Add Trello credentials to .env")
        print("  □ Install packages: pip install -r requirements.txt")
    print("=" * 70)

    return 0 if all_checks_passed else 1


if __name__ == "__main__":
    sys.exit(main())
