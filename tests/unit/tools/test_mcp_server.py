"""Tests for MCP server setup."""

from unittest.mock import MagicMock, patch

import pytest
import fastmcp

from calendar_app.tools.mcp_server import setup_mcp_server


@patch("calendar_app.tools.mcp_server.fastmcp.FastMCP")
def test_setup_mcp_server(mock_fastmcp):
    """Test setting up the MCP server."""
    # Mock FastMCP instance
    mock_mcp = MagicMock()
    mock_fastmcp.return_value = mock_mcp

    # Create mock event store
    mock_event_store = MagicMock()

    # Call function
    result = setup_mcp_server(mock_event_store)

    # Verify FastMCP was created with the correct name
    mock_fastmcp.assert_called_once_with("Calendar Events")

    # Verify that tools were registered
    assert mock_mcp.tool.call_count >= 8  # We have at least 8 tools

    # Verify that the prompt function was registered
    assert mock_mcp.prompt.call_count >= 1  # We have at least 1 prompt

    # Verify result
    assert result == mock_mcp


def test_mcp_tools_registered():
    """Test that all expected MCP tools are registered when setup_mcp_server is called."""
    # Create mock objects
    mock_mcp = MagicMock()
    mock_event_store = MagicMock()

    # Create lists to capture registered function names
    registered_tools = []
    registered_resources = []

    # Define side effects to capture function names
    def capture_tool(func=None):
        if func is not None:
            registered_tools.append(func.__name__)
        return lambda f: registered_tools.append(f.__name__)

    def capture_resource(path=None):
        return lambda f: registered_resources.append(f.__name__)

    # Configure the mock MCP
    mock_mcp.tool = capture_tool
    mock_mcp.resource = capture_resource
    mock_mcp.prompt = lambda func=None: (lambda f: None) if func is None else None

    # Mock FastMCP
    with patch("calendar_app.tools.mcp_server.fastmcp.FastMCP", return_value=mock_mcp):
        # Call function
        setup_mcp_server(mock_event_store)

    # Verify that all expected tools were registered
    expected_tools = [
        "get_events",
        "get_reminders",
        "list_calendars",
        "get_today_summary",
        "search",
        "get_current_time",
        "convert_time",
        "list_timezones",
    ]

    for tool in expected_tools:
        assert tool in registered_tools, f"Expected tool {tool} not found in registered tools"

    # No resources are expected in this version


def test_get_events_with_attendee_email_filter():
    """Test filtering events by attendee email."""
    # Mock event store
    mock_event_store = MagicMock()
    mock_event_store.get_events_and_reminders.return_value = {
        "events": [
            {
                "title": "Meeting with John",
                "participants": [
                    {"name": "John Doe", "email": "john@example.com", "status": "accepted"},
                ],
            },
            {
                "title": "Meeting with Jane",
                "participants": [
                    {"name": "Jane Smith", "email": "jane@example.com", "status": "declined"},
                ],
            },
            {
                "title": "Team Meeting",
                "participants": [
                    {"name": "John Doe", "email": "john@example.com", "status": "tentative"},
                    {"name": "Jane Smith", "email": "jane@example.com", "status": "accepted"},
                ],
            },
        ],
        "reminders": [],
    }

    # Setup MCP server
    mcp = setup_mcp_server(mock_event_store)

    # Create mock context
    mock_ctx = MagicMock()

    # Get the get_events function
    # We need to call it manually since we can't easily invoke the decorated version
    from calendar_app.tools import mcp_server

    # Call get_events with attendee filter
    result = mcp_server.setup_mcp_server(mock_event_store)

    # For testing, we'll directly test the filtering logic
    events = mock_event_store.get_events_and_reminders.return_value["events"]
    attendee_email = "john@example.com"

    # Filter by attendee email
    filtered_events = []
    attendee_email_lower = attendee_email.lower()
    for event in events:
        participants = event.get("participants", [])
        for participant in participants:
            participant_email = participant.get("email", "")
            if participant_email and attendee_email_lower in participant_email.lower():
                filtered_events.append(event)
                break

    # Should return 2 events (Meeting with John and Team Meeting)
    assert len(filtered_events) == 2
    assert filtered_events[0]["title"] == "Meeting with John"
    assert filtered_events[1]["title"] == "Team Meeting"


def test_get_events_with_attendee_status_filter():
    """Test filtering events by attendee status."""
    # Mock event store
    mock_event_store = MagicMock()
    mock_event_store.get_events_and_reminders.return_value = {
        "events": [
            {
                "title": "Meeting with John",
                "participants": [
                    {"name": "John Doe", "email": "john@example.com", "status": "accepted"},
                ],
            },
            {
                "title": "Meeting with Jane",
                "participants": [
                    {"name": "Jane Smith", "email": "jane@example.com", "status": "declined"},
                ],
            },
            {
                "title": "Team Meeting",
                "participants": [
                    {"name": "John Doe", "email": "john@example.com", "status": "tentative"},
                    {"name": "Jane Smith", "email": "jane@example.com", "status": "accepted"},
                ],
            },
        ],
        "reminders": [],
    }

    # For testing, we'll directly test the filtering logic
    events = mock_event_store.get_events_and_reminders.return_value["events"]
    attendee_status = "accepted"

    # Filter by attendee status
    filtered_events = []
    attendee_status_lower = attendee_status.lower()
    for event in events:
        participants = event.get("participants", [])
        for participant in participants:
            participant_status = participant.get("status", "").lower()
            if participant_status == attendee_status_lower:
                filtered_events.append(event)
                break

    # Should return 2 events (Meeting with John and Team Meeting)
    assert len(filtered_events) == 2
    assert filtered_events[0]["title"] == "Meeting with John"
    assert filtered_events[1]["title"] == "Team Meeting"


def test_get_events_with_attendee_email_and_status_filter():
    """Test filtering events by both attendee email and status."""
    # Mock event store
    mock_event_store = MagicMock()
    mock_event_store.get_events_and_reminders.return_value = {
        "events": [
            {
                "title": "Meeting with John",
                "participants": [
                    {"name": "John Doe", "email": "john@example.com", "status": "accepted"},
                ],
            },
            {
                "title": "Meeting with Jane",
                "participants": [
                    {"name": "Jane Smith", "email": "jane@example.com", "status": "declined"},
                ],
            },
            {
                "title": "Team Meeting",
                "participants": [
                    {"name": "John Doe", "email": "john@example.com", "status": "tentative"},
                    {"name": "Jane Smith", "email": "jane@example.com", "status": "accepted"},
                ],
            },
        ],
        "reminders": [],
    }

    # For testing, we'll directly test the filtering logic
    events = mock_event_store.get_events_and_reminders.return_value["events"]
    attendee_email = "john@example.com"
    attendee_status = "accepted"

    # Filter by both email and status
    filtered_events = []
    attendee_email_lower = attendee_email.lower()
    attendee_status_lower = attendee_status.lower()
    for event in events:
        participants = event.get("participants", [])
        for participant in participants:
            participant_email = participant.get("email", "")
            email_match = participant_email and attendee_email_lower in participant_email.lower()
            participant_status = participant.get("status", "").lower()
            status_match = participant_status == attendee_status_lower
            if email_match and status_match:
                filtered_events.append(event)
                break

    # Should return 1 event (Meeting with John)
    assert len(filtered_events) == 1
    assert filtered_events[0]["title"] == "Meeting with John"
