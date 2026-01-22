#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Manual test script for the KeyringHandler functionality.

This script provides an interactive menu to test various KeyringHandler
features including password storage, retrieval, deletion, and key inspection.
"""

import sys
from cepces.keyring import KeyringHandler


def print_banner():
    """Print a welcome banner."""
    print("\n" + "=" * 60)
    print("  KeyringHandler Manual Test Script")
    print("=" * 60)


def print_menu():
    """Print the main menu options."""
    print("\nAvailable Tests:")
    print("  1. Check keyring support")
    print("  2. Set password for a user")
    print("  3. Get password for a user")
    print("  4. Delete password for a user")
    print("  5. Dump key information (debug)")
    print("  6. Run full workflow test")
    print("  q. Quit")
    print()


def test_support():
    """Test if kernel keyring is supported."""
    print("\n--- Testing kernel keyring support ---")
    handler = KeyringHandler()
    is_supported = handler.is_supported()

    print(f"Kernel keyring supported: {is_supported}")
    if is_supported:
        print(f"keyctl path: {handler._keyctl_path}")
        print(f"Service name: {handler.service_name}")
    else:
        print("Warning: kernel keyring is not available on this system")
        print(
            "Please install keyutils "
            "(e.g., 'sudo dnf install keyutils' on Fedora)"
        )

    return is_supported


def test_set_password():
    """Test setting a password in the kernel keyring."""
    print("\n--- Testing password storage ---")
    handler = KeyringHandler()

    if not handler.is_supported():
        print("Error: kernel keyring is not available")
        return

    username = input("Enter username: ").strip()
    if not username:
        print("Error: username cannot be empty")
        return

    password = input("Enter password to store: ").strip()
    if not password:
        print("Error: password cannot be empty")
        return

    # Show key info before setting password
    print("\nKey information BEFORE setting password:")
    dump_key_info(handler, username)

    try:
        handler.set_password(username, password)
        print(f"\n✓ Successfully stored password for user '{username}'")
        print("\nKey information AFTER setting password:")
        dump_key_info(handler, username)
    except Exception as e:
        print(f"\n✗ Failed to store password: {e}")


def test_get_password():
    """Test retrieving a password from the kernel keyring."""
    print("\n--- Testing password retrieval ---")
    handler = KeyringHandler()

    if not handler.is_supported():
        print("Error: kernel keyring is not available")
        return

    username = input("Enter username: ").strip()
    if not username:
        print("Error: username cannot be empty")
        return

    password = handler.get_password(username)

    if password:
        print(f"✓ Password retrieved for user '{username}'")
        print(f"Password: {'*' * len(password)}")
        print(f"Password length: {len(password)} characters")
        print(f"Actual password: {password}")
        print("\nKey information:")
        dump_key_info(handler, username)
    else:
        print(f"✗ No password found for user '{username}'")


def test_delete_password():
    """Test deleting a password from the kernel keyring."""
    print("\n--- Testing password deletion ---")
    handler = KeyringHandler()

    if not handler.is_supported():
        print("Error: kernel keyring is not available")
        return

    username = input("Enter username: ").strip()
    if not username:
        print("Error: username cannot be empty")
        return

    # Show key info before deletion
    print("\nKey information before deletion:")
    dump_key_info(handler, username)

    result = handler.delete_password(username)

    if result:
        print(f"✓ Successfully deleted password for user '{username}'")
    else:
        print(
            f"✗ Failed to delete password (may not exist) for user "
            f"'{username}'"
        )


def test_dump_key():
    """Test dumping key information from the kernel keyring."""
    print("\n--- Testing key information dump ---")
    handler = KeyringHandler()

    if not handler.is_supported():
        print("Error: kernel keyring is not available")
        return

    username = input("Enter username: ").strip()
    if not username:
        print("Error: username cannot be empty")
        return

    dump_key_info(handler, username)


def dump_key_info(handler: KeyringHandler, username: str):
    """Helper function to dump and display key information.

    Args:
        handler: KeyringHandler instance
        username: Username for which to dump key information
    """
    key_info = handler.dump_key(username)

    if key_info:
        print(f"Key information for user '{username}':")
        print(f"  Key ID:      {key_info['key_id']}")
        print(f"  Key Type:    {key_info['key_type']}")
        print(f"  UID:         {key_info['uid']}")
        print(f"  GID:         {key_info['gid']}")
        print(f"  Permissions: {key_info['perms']}")
        print(f"  Description: {key_info['description']}")
    else:
        print(f"No key found for user '{username}'")


def test_full_workflow():
    """Run a complete workflow test: set, get, dump, delete."""
    print("\n" + "=" * 60)
    print("  Running Full Workflow Test")
    print("=" * 60)

    handler = KeyringHandler()
    is_supported = test_support()

    if not is_supported:
        print("\nSkipping workflow test as kernel keyring is not available")
        return

    test_username = "test_user_" + str(id(handler))[-6:]
    test_password = "test_password_123"

    print(f"\nUsing test username: {test_username}")
    print(f"Using test password: {test_password}")

    # Step 1: Set password
    print("\n[Step 1/5] Setting password...")
    try:
        handler.set_password(test_username, test_password)
        print("✓ Password set successfully")
    except Exception as e:
        print(f"✗ Failed to set password: {e}")
        return

    # Step 2: Dump key info
    print("\n[Step 2/5] Dumping key information...")
    dump_key_info(handler, test_username)

    # Step 3: Retrieve password
    print("\n[Step 3/5] Retrieving password...")
    retrieved_password = handler.get_password(test_username)
    if retrieved_password == test_password:
        print(f"✓ Password retrieved successfully: {retrieved_password}")
        print("✓ Retrieved password matches original")
    else:
        print(
            f"✗ Password mismatch! Expected: {test_password}, "
            f"Got: {retrieved_password}"
        )

    # Step 4: Update password
    print("\n[Step 4/5] Updating password to a new value...")
    new_password = "updated_password_456"
    try:
        handler.set_password(test_username, new_password)
        print("✓ Password updated successfully")
        retrieved_new = handler.get_password(test_username)
        if retrieved_new == new_password:
            print(f"✓ New password verified: {retrieved_new}")
        else:
            print("✗ New password mismatch!")
    except Exception as e:
        print(f"✗ Failed to update password: {e}")

    # Step 5: Delete password
    print("\n[Step 5/5] Deleting password...")
    if handler.delete_password(test_username):
        print("✓ Password deleted successfully")
        # Verify deletion
        if handler.get_password(test_username) is None:
            print("✓ Deletion verified - password no longer exists")
        else:
            print("✗ Deletion verification failed - password still exists")
    else:
        print("✗ Failed to delete password")

    print("\n" + "=" * 60)
    print("  Workflow Test Completed")
    print("=" * 60)


def main():
    """Main function to run the interactive test menu."""
    print_banner()

    while True:
        print_menu()
        choice = input("Enter your choice: ").strip().lower()

        if choice == "1":
            test_support()
        elif choice == "2":
            test_set_password()
        elif choice == "3":
            test_get_password()
        elif choice == "4":
            test_delete_password()
        elif choice == "5":
            test_dump_key()
        elif choice == "6":
            test_full_workflow()
        elif choice in ("q", "quit", "exit"):
            print("\nExiting test script. Goodbye!")
            sys.exit(0)
        else:
            print(f"\nInvalid choice: '{choice}'. Please try again.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
        sys.exit(0)
