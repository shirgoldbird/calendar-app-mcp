"""Utility functions for filtering events by attendee criteria."""


def filter_events_by_attendee(
    events, attendee_email=None, attendee_status=None, my_status=None
):
    """
    Filter events by attendee email and/or status.

    Args:
        events: List of event dictionaries
        attendee_email: Email to filter by (case-insensitive partial match)
        attendee_status: Status to filter by (case-insensitive exact match)
        my_status: Filter by the calendar owner's own response status (convenience parameter)

    Returns:
        List of filtered events
    """
    # If my_status is specified, extract owner email from events and use it
    if my_status:
        owner_email = _extract_owner_email(events)
        if owner_email:
            attendee_email = owner_email
            attendee_status = my_status

    if not attendee_email and not attendee_status:
        return events

    filtered_events = []
    attendee_email_lower = attendee_email.lower() if attendee_email else None
    attendee_status_lower = attendee_status.lower() if attendee_status else None

    for event in events:
        participants = event.get("participants", [])

        # Special case: include solo events (no participants) in these scenarios:
        # 1. Filtering by "accepted" status only (implicit acceptance of own events)
        # 2. Filtering by email that matches the calendar owner (user's own events)
        if not participants:
            if _should_include_solo_event(
                event, attendee_email_lower, attendee_status_lower
            ):
                filtered_events.append(event)
                continue

        # Check if any participant matches the criteria
        if _event_matches_attendee_criteria(
            participants, attendee_email_lower, attendee_status_lower
        ):
            filtered_events.append(event)

    return filtered_events


def _should_include_solo_event(event, attendee_email_lower, attendee_status_lower):
    """Determine if a solo event (no participants) should be included."""
    # Case 1: Accepted status without email filter
    if attendee_status_lower == "accepted" and not attendee_email_lower:
        return True

    # Case 2: Email filter matches calendar name (owner email)
    if attendee_email_lower:
        calendar_name = event.get("calendar", "").lower()
        if attendee_email_lower in calendar_name:
            # If status is also specified, only include if it's "accepted"
            if not attendee_status_lower or attendee_status_lower == "accepted":
                return True

    return False


def _event_matches_attendee_criteria(participants, attendee_email_lower, attendee_status_lower):
    """Check if any participant in the event matches the filter criteria."""
    for participant in participants:
        # Check email match (case-insensitive partial match)
        email_match = True
        if attendee_email_lower:
            participant_email = participant.get("email", "")
            email_match = (
                participant_email and attendee_email_lower in participant_email.lower()
            )

        # Check status match (case-insensitive exact match)
        status_match = True
        if attendee_status_lower:
            participant_status = participant.get("status", "").lower()
            status_match = participant_status == attendee_status_lower

        # If both conditions match, this event should be included
        if email_match and status_match:
            return True

    return False


def _extract_owner_email(events):
    """
    Extract the calendar owner's email from events.

    Looks through events to find one with participants and extracts the owner's
    email by finding a participant whose email matches the calendar name.

    Args:
        events: List of event dictionaries

    Returns:
        Owner email string, or None if not found
    """
    for event in events:
        calendar = event.get("calendar", "")
        participants = event.get("participants", [])

        # Try to find a participant whose email matches/appears in the calendar name
        for participant in participants:
            participant_email = participant.get("email", "")
            if participant_email and participant_email.lower() in calendar.lower():
                return participant_email

    # Fallback: if no match found, just return None
    # The calendar field itself might be the email in some cases
    if events and "@" in events[0].get("calendar", ""):
        return events[0].get("calendar")

    return None
