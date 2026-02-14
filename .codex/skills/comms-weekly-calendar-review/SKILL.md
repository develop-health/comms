---
name: comms-weekly-calendar-review
description: Run a start-of-week calendar review in Codex using Comms MCP tools (list_calendar_events, update_calendar_event, draft_email, send_draft).
---

# Comms Weekly Calendar Review

Use this workflow for start-of-week planning and conflict cleanup.

## Workflow

1. Fetch the week:
   - Compute remaining weekdays from today through Friday.
   - Call `list_calendar_events` for each day (parallel if possible).
   - Deduplicate by event `id`.
   - Exclude cancelled events (`status == cancelled`).

2. Week overview:
   - Per day: meeting count, total meeting hours, estimated free time in a 9:00-18:00 window.
   - Flag overloaded days (6+ meeting hours).
   - Show total weekly load.

3. Pending RSVPs:
   - Find events where self attendee has `responseStatus == needsAction`.
   - Show title, time, organizer, attendees, `htmlLink`.
   - Ask user to respond manually in Google Calendar via link.

4. No-agenda check for internal meetings:
   - Internal means all attendee emails are `@develophealth.ai`.
   - If description is empty, ask user for agenda text.
   - Call `update_calendar_event` with `event_id` and `description`.

5. Detect conflicts:
   - Ignore all-day events (date-only start value).
   - Ignore declined events where self attendee `responseStatus == declined`.
   - Conflict rule: `A.start < B.end AND B.start < A.end`.
   - Do not treat back-to-back (`A.end == B.start`) as conflict.
   - Group overlaps into conflict clusters.

6. Resolve conflicts:
   - Present overlapping window and all conflicting events.
   - Mark personal blocks (no attendees or only self) as non-reschedulable by email.
   - For meetings user chooses to reschedule:
   - Draft via `draft_email`:
     - `to`: non-self attendee emails
     - `cc`: `bot@blockit.com`
     - `subject`: `Reschedule: {event title}`
     - short, warm body asking for a new time
   - On approval, call `send_draft`.

7. Summarize:
   - Total load and busiest day.
   - RSVP count surfaced.
   - No-agenda count and updated count.
   - Conflict and reschedule counts.
