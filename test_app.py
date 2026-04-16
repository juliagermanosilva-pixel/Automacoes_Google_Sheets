import pytest
import json
from io import StringIO
import sys
import time

from app import send_message, send_multiple_messages, get_all_messages, get_last_message, API_URL

def capture_print(func, *args, **kwargs):
    """Utility to capture print output of a function."""
    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()
    try:
        func(*args, **kwargs)
    finally:
        sys.stdout = old_stdout
    return mystdout.getvalue()

@pytest.fixture(scope="module")
def seeded_sheet():
    # Clean state is not guaranteed, but let's try to send the 3 messages
    capture_print(send_message, "alice", "alice@example.com")
    time.sleep(1)
    capture_print(send_multiple_messages, [
        {"name": "bob", "email": "bob@example.com"},
        {"name": "charlie", "email": "charlie@example.com"}
    ])
    time.sleep(2)  # Give Sheets a moment to update
    return True

def test_send_message(seeded_sheet):
    output = capture_print(send_message, "testuser", "testuser@example.com")
    assert "Success" in output or "success" in output.lower()

def test_send_multiple_messages(seeded_sheet):
    output = capture_print(send_multiple_messages, [
        {"name": "testuser2", "email": "testuser2@example.com"},
        {"name": "testuser3", "email": "testuser3@example.com"}
    ])
    # Should print success twice
    assert output.lower().count("success") == 2

def test_get_all_messages(seeded_sheet):
    # get_all_messages prints the JSON array
    output = capture_print(get_all_messages)
    data = json.loads(output)
    # There should be at least our test entries present
    assert isinstance(data, list)
    assert any(e["Name"] == "alice" and e["Email"] == "alice@example.com" for e in data)
    assert any(e["Name"] == "bob" and e["Email"] == "bob@example.com" for e in data)
    assert any(e["Name"] == "charlie" and e["Email"] == "charlie@example.com" for e in data)
    assert any(e["Name"] == "testuser2" and e["Email"] == "testuser2@example.com" for e in data)
    assert any(e["Name"] == "testuser3" and e["Email"] == "testuser3@example.com" for e in data)

def test_get_last_message(seeded_sheet):
    output = capture_print(get_last_message)
    last_data = json.loads(output)
    assert last_data["Name"] == "testuser3"
    assert last_data["Email"] == "testuser3@example.com"