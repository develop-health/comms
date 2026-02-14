---
description: Daily meeting prep
allowed-tools: [Task, Read, Glob, Grep]
---

# Daily Meeting Prep

You are helping the user prepare for today's meetings by pulling relevant context for each one. Follow these steps in order.

## Step 1 — Pull today's calendar and recent recordings (all in parallel)

Call these three tools simultaneously:
- `list_calendar_events` (no arguments — defaults to today)
- `list_grain_recordings` (no arguments — defaults to today)
- `list_grain_recordings` with `date` set to yesterday's date (for recent context)

Wait for all three to return before proceeding.

## Step 2 — Present the day and classify meetings

Show a timeline view of today's meetings. For each meeting show: time, title, attendees, and whether a Grain recording already exists (from today's recordings).

Classify each meeting into one of two buckets:
- **Prep needed** — external meetings, 1:1s, BD/sales calls, investor meetings, interviews, anything with outside attendees or a specific agenda
- **Low prep** — recurring standups, all-hands, focus/work blocks, lunch holds

Present the classified timeline and ask the user which meetings they want to prep for. Default suggestion: all "Prep needed" meetings.

## Step 3 — Deep prep for each selected meeting

For each selected meeting, gather context in parallel:
1. **Recent emails** — `search_emails` for threads involving the meeting's attendees (use each attendee's email address, query like `from:attendee@example.com OR to:attendee@example.com newer_than:14d`). Skip the user's own email address.
2. **Slack activity** — `search_slack` for messages from/mentioning key attendees by name (recent messages)
3. **Past recordings** — from the Grain recordings already fetched in Step 1, match any that involve the same attendees or have similar titles

Then present a per-meeting briefing:
- **Attendees** — who's coming (with role/company context if apparent from email signatures or calendar details)
- **Recent email threads** — subject line and snippet for each relevant thread, grouped by attendee
- **Slack context** — any relevant recent messages or threads
- **Related recordings** — any matched Grain recordings from today or yesterday involving the same people
- **Suggested talking points** — open threads to follow up on, unanswered questions, action items from recent emails or recordings

## Step 4 — Drill deeper

After presenting all briefings, ask the user if they want to:
- Read a full email thread (`read_thread`)
- Read a full Slack thread (`read_slack_thread`)
- Get a Grain transcript summary (`get_grain_transcript`)
- Move on with their day

Loop until the user is satisfied.
