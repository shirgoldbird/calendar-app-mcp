"""Tests for attendee filtering utilities."""

import pytest

from calendar_app.utils.attendee_filter import (
    filter_events_by_attendee,
    _should_include_solo_event,
    _event_matches_attendee_criteria,
)


class TestFilterEventsByAttendee:
    """Tests for filter_events_by_attendee function."""

    def test_no_filters_returns_all_events(self):
        """Test that no filters returns all events unchanged."""
        events = [
            {"title": "Event 1", "participants": []},
            {"title": "Event 2", "participants": [{"email": "test@example.com"}]},
        ]
        result = filter_events_by_attendee(events, None, None)
        assert result == events
        assert len(result) == 2

    def test_email_filter_only(self):
        """Test filtering by email address only."""
        events = [
            {
                "title": "Meeting with John",
                "participants": [
                    {"name": "John Doe", "email": "john@example.com", "status": "accepted"}
                ],
            },
            {
                "title": "Meeting with Jane",
                "participants": [
                    {"name": "Jane Smith", "email": "jane@example.com", "status": "declined"}
                ],
            },
            {
                "title": "Team Meeting",
                "participants": [
                    {"name": "John Doe", "email": "john@example.com", "status": "tentative"},
                    {"name": "Jane Smith", "email": "jane@example.com", "status": "accepted"},
                ],
            },
        ]

        result = filter_events_by_attendee(events, "john@example.com", None)
        assert len(result) == 2
        assert result[0]["title"] == "Meeting with John"
        assert result[1]["title"] == "Team Meeting"

    def test_email_filter_case_insensitive(self):
        """Test that email filtering is case-insensitive."""
        events = [
            {
                "title": "Meeting",
                "participants": [{"email": "John@Example.COM", "status": "accepted"}],
            }
        ]

        result = filter_events_by_attendee(events, "john@example.com", None)
        assert len(result) == 1

        result = filter_events_by_attendee(events, "JOHN@EXAMPLE.COM", None)
        assert len(result) == 1

    def test_email_filter_partial_match(self):
        """Test that email filtering supports partial matching."""
        events = [
            {
                "title": "Meeting",
                "participants": [{"email": "john.doe@example.com", "status": "accepted"}],
            }
        ]

        result = filter_events_by_attendee(events, "john", None)
        assert len(result) == 1

        result = filter_events_by_attendee(events, "doe", None)
        assert len(result) == 1

        result = filter_events_by_attendee(events, "example.com", None)
        assert len(result) == 1

    def test_status_filter_only(self):
        """Test filtering by status only."""
        events = [
            {
                "title": "Meeting 1",
                "participants": [{"email": "john@example.com", "status": "accepted"}],
            },
            {
                "title": "Meeting 2",
                "participants": [{"email": "jane@example.com", "status": "declined"}],
            },
            {
                "title": "Meeting 3",
                "participants": [
                    {"email": "john@example.com", "status": "tentative"},
                    {"email": "jane@example.com", "status": "accepted"},
                ],
            },
        ]

        result = filter_events_by_attendee(events, None, "accepted")
        assert len(result) == 2
        assert result[0]["title"] == "Meeting 1"
        assert result[1]["title"] == "Meeting 3"

    def test_status_filter_case_insensitive(self):
        """Test that status filtering is case-insensitive."""
        events = [
            {
                "title": "Meeting",
                "participants": [{"email": "john@example.com", "status": "ACCEPTED"}],
            }
        ]

        result = filter_events_by_attendee(events, None, "accepted")
        assert len(result) == 1

        result = filter_events_by_attendee(events, None, "ACCEPTED")
        assert len(result) == 1

    def test_combined_email_and_status_filter(self):
        """Test filtering by both email and status."""
        events = [
            {
                "title": "Meeting 1",
                "participants": [{"email": "john@example.com", "status": "accepted"}],
            },
            {
                "title": "Meeting 2",
                "participants": [{"email": "john@example.com", "status": "declined"}],
            },
            {
                "title": "Meeting 3",
                "participants": [
                    {"email": "john@example.com", "status": "tentative"},
                    {"email": "jane@example.com", "status": "accepted"},
                ],
            },
        ]

        result = filter_events_by_attendee(events, "john@example.com", "accepted")
        assert len(result) == 1
        assert result[0]["title"] == "Meeting 1"

    def test_solo_event_with_accepted_status_filter(self):
        """Test that solo events (no participants) are included when filtering by 'accepted' status only."""
        events = [
            {"title": "Solo Event", "participants": [], "calendar": "user@example.com"},
            {
                "title": "Meeting",
                "participants": [{"email": "other@example.com", "status": "accepted"}],
            },
        ]

        result = filter_events_by_attendee(events, None, "accepted")
        assert len(result) == 2
        assert result[0]["title"] == "Solo Event"
        assert result[1]["title"] == "Meeting"

    def test_solo_event_with_declined_status_filter_excluded(self):
        """Test that solo events are excluded when filtering by non-accepted status."""
        events = [
            {"title": "Solo Event", "participants": [], "calendar": "user@example.com"},
            {
                "title": "Meeting",
                "participants": [{"email": "other@example.com", "status": "declined"}],
            },
        ]

        result = filter_events_by_attendee(events, None, "declined")
        assert len(result) == 1
        assert result[0]["title"] == "Meeting"

    def test_solo_event_with_email_matching_calendar(self):
        """Test that solo events are included when email matches calendar name."""
        events = [
            {"title": "Solo Event", "participants": [], "calendar": "user@example.com"},
            {
                "title": "Other Event",
                "participants": [{"email": "other@example.com", "status": "accepted"}],
            },
        ]

        result = filter_events_by_attendee(events, "user@example.com", None)
        assert len(result) == 1
        assert result[0]["title"] == "Solo Event"

    def test_solo_event_with_email_and_accepted_status(self):
        """Test solo events with both email and accepted status."""
        events = [
            {"title": "Solo Event", "participants": [], "calendar": "user@example.com"},
        ]

        result = filter_events_by_attendee(events, "user@example.com", "accepted")
        assert len(result) == 1
        assert result[0]["title"] == "Solo Event"

    def test_solo_event_with_email_and_declined_status_excluded(self):
        """Test that solo events are excluded when email matches but status is not accepted."""
        events = [
            {"title": "Solo Event", "participants": [], "calendar": "user@example.com"},
        ]

        result = filter_events_by_attendee(events, "user@example.com", "declined")
        assert len(result) == 0

    def test_empty_events_list(self):
        """Test that empty events list returns empty list."""
        result = filter_events_by_attendee([], "test@example.com", "accepted")
        assert result == []

    def test_events_with_missing_participants_field(self):
        """Test handling of events without participants field."""
        events = [{"title": "Event", "calendar": "user@example.com"}]

        # Should be treated as solo event
        result = filter_events_by_attendee(events, None, "accepted")
        assert len(result) == 1

    def test_participants_with_missing_email_field(self):
        """Test handling of participants without email field."""
        events = [
            {
                "title": "Meeting",
                "participants": [{"name": "John Doe", "status": "accepted"}],
            }
        ]

        result = filter_events_by_attendee(events, "john", None)
        assert len(result) == 0  # No email to match

    def test_participants_with_missing_status_field(self):
        """Test handling of participants without status field."""
        events = [
            {
                "title": "Meeting",
                "participants": [{"email": "john@example.com", "name": "John Doe"}],
            }
        ]

        result = filter_events_by_attendee(events, None, "accepted")
        assert len(result) == 0  # No status to match

    def test_multiple_participants_one_match(self):
        """Test that event is included if at least one participant matches."""
        events = [
            {
                "title": "Team Meeting",
                "participants": [
                    {"email": "john@example.com", "status": "declined"},
                    {"email": "jane@example.com", "status": "accepted"},
                    {"email": "bob@example.com", "status": "tentative"},
                ],
            }
        ]

        result = filter_events_by_attendee(events, "jane", "accepted")
        assert len(result) == 1

    def test_event_not_duplicated_with_multiple_matches(self):
        """Test that an event appears only once even if multiple participants match."""
        events = [
            {
                "title": "Team Meeting",
                "participants": [
                    {"email": "john@example.com", "status": "accepted"},
                    {"email": "jane@example.com", "status": "accepted"},
                ],
            }
        ]

        result = filter_events_by_attendee(events, None, "accepted")
        assert len(result) == 1

    def test_all_status_values(self):
        """Test filtering with all valid status values."""
        statuses = [
            "accepted",
            "declined",
            "tentative",
            "pending",
            "unknown",
            "delegated",
            "completed",
            "in-process",
        ]

        for status in statuses:
            events = [
                {
                    "title": f"Meeting {status}",
                    "participants": [{"email": "test@example.com", "status": status}],
                }
            ]

            result = filter_events_by_attendee(events, None, status)
            assert len(result) == 1, f"Failed for status: {status}"

    def test_my_status_filter(self):
        """Test filtering by my_status (user's own response)."""
        events = [
            {
                "title": "Meeting 1",
                "calendar": "owner@example.com",
                "participants": [
                    {"email": "owner@example.com", "status": "accepted"},
                    {"email": "other@example.com", "status": "declined"},
                ],
            },
            {
                "title": "Meeting 2",
                "calendar": "owner@example.com",
                "participants": [
                    {"email": "owner@example.com", "status": "declined"},
                    {"email": "other@example.com", "status": "accepted"},
                ],
            },
            {
                "title": "Meeting 3",
                "calendar": "owner@example.com",
                "participants": [
                    {"email": "owner@example.com", "status": "accepted"},
                ],
            },
        ]

        # Filter by my_status="accepted" should find events where owner accepted
        result = filter_events_by_attendee(events, None, None, my_status="accepted")
        assert len(result) == 2
        assert result[0]["title"] == "Meeting 1"
        assert result[1]["title"] == "Meeting 3"

        # Filter by my_status="declined" should find events where owner declined
        result = filter_events_by_attendee(events, None, None, my_status="declined")
        assert len(result) == 1
        assert result[0]["title"] == "Meeting 2"


class TestShouldIncludeSoloEvent:
    """Tests for _should_include_solo_event helper function."""

    def test_accepted_status_without_email(self):
        """Test solo event included with accepted status and no email filter."""
        event = {"title": "Solo", "calendar": "user@example.com", "participants": []}
        assert _should_include_solo_event(event, None, "accepted") is True

    def test_non_accepted_status_without_email(self):
        """Test solo event excluded with non-accepted status and no email filter."""
        event = {"title": "Solo", "calendar": "user@example.com", "participants": []}
        assert _should_include_solo_event(event, None, "declined") is False

    def test_email_matches_calendar_no_status(self):
        """Test solo event included when email matches calendar name, no status."""
        event = {"title": "Solo", "calendar": "user@example.com", "participants": []}
        assert _should_include_solo_event(event, "user@example.com", None) is True

    def test_email_matches_calendar_accepted_status(self):
        """Test solo event included when email matches and status is accepted."""
        event = {"title": "Solo", "calendar": "user@example.com", "participants": []}
        assert _should_include_solo_event(event, "user@example.com", "accepted") is True

    def test_email_matches_calendar_non_accepted_status(self):
        """Test solo event excluded when email matches but status is not accepted."""
        event = {"title": "Solo", "calendar": "user@example.com", "participants": []}
        assert _should_include_solo_event(event, "user@example.com", "declined") is False

    def test_email_not_in_calendar(self):
        """Test solo event excluded when email doesn't match calendar."""
        event = {"title": "Solo", "calendar": "user@example.com", "participants": []}
        assert _should_include_solo_event(event, "other@example.com", None) is False

    def test_no_filters(self):
        """Test solo event excluded when no filters specified."""
        event = {"title": "Solo", "calendar": "user@example.com", "participants": []}
        assert _should_include_solo_event(event, None, None) is False


class TestEventMatchesAttendeeCriteria:
    """Tests for _event_matches_attendee_criteria helper function."""

    def test_email_match_only(self):
        """Test matching by email only."""
        participants = [{"email": "john@example.com", "status": "accepted"}]
        assert _event_matches_attendee_criteria(participants, "john", None) is True
        assert _event_matches_attendee_criteria(participants, "jane", None) is False

    def test_status_match_only(self):
        """Test matching by status only."""
        participants = [{"email": "john@example.com", "status": "accepted"}]
        assert _event_matches_attendee_criteria(participants, None, "accepted") is True
        assert _event_matches_attendee_criteria(participants, None, "declined") is False

    def test_both_email_and_status_match(self):
        """Test matching both email and status."""
        participants = [
            {"email": "john@example.com", "status": "accepted"},
            {"email": "jane@example.com", "status": "declined"},
        ]
        assert _event_matches_attendee_criteria(participants, "john", "accepted") is True
        assert _event_matches_attendee_criteria(participants, "john", "declined") is False
        assert _event_matches_attendee_criteria(participants, "jane", "declined") is True

    def test_empty_participants_list(self):
        """Test that empty participants list returns False."""
        assert _event_matches_attendee_criteria([], "test", "accepted") is False

    def test_missing_email_field(self):
        """Test handling of missing email field."""
        participants = [{"name": "John", "status": "accepted"}]
        assert _event_matches_attendee_criteria(participants, "john", None) is False

    def test_missing_status_field(self):
        """Test handling of missing status field."""
        participants = [{"email": "john@example.com", "name": "John"}]
        assert _event_matches_attendee_criteria(participants, None, "accepted") is False
