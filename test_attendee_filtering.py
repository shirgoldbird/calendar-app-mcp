#!/usr/bin/env python3
"""Test script for attendee filtering functionality."""

import sys
from calendar_app.models.event_store import CalendarEventStore
from calendar_app.tools.mcp_server import setup_mcp_server

# Mock context for testing
class MockContext:
    def info(self, msg):
        print(f"[INFO] {msg}", file=sys.stderr)

    def warning(self, msg):
        print(f"[WARN] {msg}", file=sys.stderr)

    def report_progress(self, current, total):
        print(f"[PROGRESS] {current}/{total}", file=sys.stderr)

def main():
    print("Testing attendee filtering...\n")

    # Create event store
    event_store = CalendarEventStore(quiet=False)

    # Set up MCP server
    mcp = setup_mcp_server(event_store)

    # Create mock context
    ctx = MockContext()

    print("\n" + "="*80)
    print("TEST 1: Filter by attendee email")
    print("="*80)
    try:
        # This would normally be called by the MCP framework
        # For testing, we'll manually call the underlying logic
        from calendar_app.tools.mcp_server import setup_mcp_server
        from datetime import datetime, timedelta

        # Get events for next 30 days
        from_date = datetime.now().strftime("%Y-%m-%d")
        to_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

        print(f"\nSearching for events from {from_date} to {to_date}")
        email = input("\nEnter attendee email to filter by (or press Enter to skip): ").strip()

        if email:
            result = event_store.get_events_and_reminders(
                from_date=datetime.now(),
                to_date=datetime.now() + timedelta(days=30)
            )

            events = result.get("events", [])
            print(f"\nTotal events found: {len(events)}")

            # Apply filtering
            filtered_events = []
            email_lower = email.lower()
            for event in events:
                participants = event.get("participants", [])
                for participant in participants:
                    participant_email = participant.get("email", "")
                    if participant_email and email_lower in participant_email.lower():
                        filtered_events.append(event)
                        break

            print(f"Events with attendee '{email}': {len(filtered_events)}\n")

            for event in filtered_events[:5]:  # Show first 5
                print(f"\n  - {event.get('title')}")
                print(f"    Start: {event.get('start_time')}")
                participants = event.get("participants", [])
                print(f"    Attendees: {len(participants)}")
                for p in participants:
                    print(f"      * {p.get('name')} ({p.get('email')}) - {p.get('status')}")

        print("\n" + "="*80)
        print("TEST 2: Filter by attendee status")
        print("="*80)

        status = input("\nEnter status to filter by (accepted/declined/tentative/pending) or press Enter to skip: ").strip()

        if status:
            result = event_store.get_events_and_reminders(
                from_date=datetime.now(),
                to_date=datetime.now() + timedelta(days=30)
            )

            events = result.get("events", [])

            # Apply filtering
            filtered_events = []
            status_lower = status.lower()
            for event in events:
                participants = event.get("participants", [])
                for participant in participants:
                    participant_status = participant.get("status", "").lower()
                    if participant_status == status_lower:
                        filtered_events.append(event)
                        break

            print(f"\nEvents with status '{status}': {len(filtered_events)}\n")

            for event in filtered_events[:5]:  # Show first 5
                print(f"\n  - {event.get('title')}")
                print(f"    Start: {event.get('start_time')}")
                participants = event.get("participants", [])
                matching_participants = [p for p in participants if p.get('status', '').lower() == status_lower]
                print(f"    Attendees with status '{status}': {len(matching_participants)}")
                for p in matching_participants:
                    print(f"      * {p.get('name')} ({p.get('email')})")

    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
