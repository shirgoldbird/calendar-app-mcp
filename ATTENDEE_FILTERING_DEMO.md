# Attendee Filtering Feature

## Overview

The calendar-app-mcp now supports filtering events by attendee email and status. This allows you to find events where specific people have responded in specific ways.

## Attendee Status Values

Each attendee can have one of the following status values:

- `accepted` - Attendee has accepted the invitation
- `declined` - Attendee has declined the invitation
- `tentative` - Attendee's response is tentative (maybe)
- `pending` - Invitation is pending (no response yet)
- `unknown` - Status is unknown
- `delegated` - Attendee has delegated the meeting
- `completed` - Meeting is completed
- `in-process` - Meeting is in process

## Usage

### Filter by Attendee Email

Find all events where a specific person is an attendee:

```python
# Using the MCP tool
get_events(
    from_date="2024-02-01",
    to_date="2024-02-29",
    attendee_email="john@example.com"
)
```

The email filter is case-insensitive and supports partial matching. For example, `"john"` would match `john@example.com`, `john.doe@company.com`, etc.

### Filter by Attendee Status

Find all events where any attendee has a specific status:

```python
# Find all events with accepted invitations
get_events(
    from_date="2024-02-01",
    to_date="2024-02-29",
    attendee_status="accepted"
)

# Find all events with declined invitations
get_events(
    from_date="2024-02-01",
    to_date="2024-02-29",
    attendee_status="declined"
)
```

### Filter by Both Email and Status

Find events where a specific person has a specific response status:

```python
# Find events where john@example.com has accepted
get_events(
    from_date="2024-02-01",
    to_date="2024-02-29",
    attendee_email="john@example.com",
    attendee_status="accepted"
)
```

### Using with Search

The `search` tool also supports attendee filtering:

```python
# Search for "standup" meetings where john@example.com has accepted
search(
    search_term="standup",
    from_date="2024-02-01",
    to_date="2024-02-29",
    attendee_email="john@example.com",
    attendee_status="accepted"
)
```

## Event Data Structure

Each event includes a `participants` array with attendee information:

```json
{
  "title": "Team Meeting",
  "participants": [
    {
      "name": "John Doe",
      "email": "john@example.com",
      "status": "accepted",
      "type": "person",
      "role": "required",
      "is_organizer": false
    },
    {
      "name": "Jane Smith",
      "email": "jane@example.com",
      "status": "declined",
      "type": "person",
      "role": "optional",
      "is_organizer": false
    }
  ]
}
```

## Common Use Cases

### 1. Find meetings waiting for your response
```python
get_events(
    attendee_email="your.email@example.com",
    attendee_status="pending"
)
```

### 2. See what meetings a colleague has accepted
```python
get_events(
    attendee_email="colleague@example.com",
    attendee_status="accepted"
)
```

### 3. Find meetings where someone declined
```python
get_events(
    attendee_email="person@example.com",
    attendee_status="declined"
)
```

### 4. Check tentative meetings for a specific attendee
```python
get_events(
    attendee_email="manager@example.com",
    attendee_status="tentative"
)
```

## Technical Details

- The filtering happens after events are fetched from the macOS Calendar API
- Email matching is case-insensitive and supports partial matches
- Status matching is case-insensitive and requires exact matches
- When both email and status filters are specified, BOTH conditions must match
- Events are only included once even if multiple participants match the criteria
- The filtering works with all existing parameters (calendars, date ranges, all_day_only, busy_only)
