---
name: comms-daily-meeting-prep
description: Run daily meeting prep in Codex using Comms MCP tools (calendar, grain, gmail, slack) and produce per-meeting briefings.
---

# Comms Daily Meeting Prep

Use this workflow when the user asks for prep context for today's meetings.

## Workflow

1. Gather base context in parallel:
   - `list_calendar_events` for today.
   - `list_grain_recordings` for today.
   - `list_grain_recordings` for yesterday.

2. Build a timeline and classify meetings:
   - Show time, title, attendees, and whether a matching Grain recording exists.
   - Buckets:
     - `Prep needed`: external meetings, 1:1s, BD/sales, investor calls, interviews, agenda-heavy sessions.
     - `Low prep`: standups, all-hands, focus blocks, lunch holds.
   - Ask user which meetings to prep (default to all `Prep needed`).

3. Deep prep for selected meetings:
   - For each meeting, gather in parallel:
     - Emails: `search_emails` per attendee with `from:`/`to:` and `newer_than:14d`.
     - Slack: `search_slack` with attendee names and meeting keywords.
     - Recordings: match from already fetched today/yesterday Grain recordings by title/attendee overlap.
   - Present per-meeting briefing:
     - Attendees and likely role/company context.
     - Recent relevant email threads.
     - Relevant Slack context.
     - Related Grain recordings.
     - Suggested talking points and open follow-ups.

4. Drill deeper loop:
   - Offer:
     - `read_thread` for full email thread.
     - `read_slack_thread` for full Slack thread.
     - `get_grain_transcript` for transcript summary.
   - Repeat until user is done.

## Notes

- Skip user's own email when building attendee email queries.
- Keep prep output compact and decision-focused.
