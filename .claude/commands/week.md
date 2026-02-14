---
description: Weekly calendar review
allowed-tools: [Task, Read, Glob, Grep]
---

# Weekly Calendar Review

You are guiding the user through a start-of-week review of their calendar. Follow these steps in order.

## Step 1 — Fetch the week's calendar

Determine the remaining weekdays from today ({{ datetime }}) through Friday. Call `list_calendar_events` for each date in parallel.

Wait for all to return. Aggregate results and deduplicate events by `id`. Exclude cancelled events (status: "cancelled").

## Step 2 — Week overview

Present a day-by-day summary. For each day show:
- Number of meetings
- Total meeting hours
- Estimated free time between meetings (assume 9am–6pm work window)

Flag overloaded days (6+ hours of meetings). Show the overall meeting load for the week (total hours across all days).

## Step 3 — Pending RSVPs

Find events where the user's attendee entry (`self: true`) has `responseStatus: "needsAction"`.

Present each one: title, day/time, organizer, attendees, and `htmlLink` so the user can respond in Google Calendar.

Ask the user if they want to accept or decline each. Since the readonly API can't update RSVP status directly, link to each event for the user to respond manually.

## Step 4 — No-agenda check (internal meetings only)

Find internal meetings where all attendees have @develophealth.ai email addresses AND the `description` is empty or missing.

Present each: title, day/time, attendees.

For each, ask the user what the agenda should be. Then call `update_calendar_event` with the `event_id` and the new `description` to set it directly on the calendar invite. The user can also skip or note for later.

## Step 5 — Conflict detection

Filter out:
- All-day events (start value has no `T` character, i.e. date-only format like "2025-02-10")
- Declined events (attendee with `self: true` and `responseStatus: "declined"`)

Detect overlaps among the remaining events: two events conflict when `A.start < B.end AND B.start < A.end` (parse ISO 8601 with timezone awareness). Back-to-back meetings (A.end == B.start) are NOT conflicts.

Group overlapping events into conflict clusters. If no conflicts are found, say so and move to the summary.

## Step 6 — Resolve conflicts

For each conflict group, present: day, overlapping time window, and for each event: title, time range, attendees.

Flag personal blocks (events with no attendees or only the user) — these can't be rescheduled via email.

Ask the user which meeting in each conflict to reschedule.

For each meeting to reschedule:
1. Collect the non-self attendee email addresses
2. Call `draft_email` with:
   - **To:** non-self attendee emails
   - **CC:** `bot@blockit.com`
   - **Subject:** `Reschedule: {event title}`
   - **Body:** 2–3 sentences in Mel's style asking to find a new time, keeping it short and warm
3. Show the draft to the user for approval
4. On approval → call `send_draft` with the draftId
5. User wants edits → revise and re-draft
6. User skips → move to the next conflict

## Step 7 — Summary

Recap:
- Week meeting load (total hours, busiest day)
- Pending RSVPs surfaced (count)
- No-agenda meetings flagged (count, how many got agendas set)
- Conflicts found and resolved (count)
- Reschedule emails sent (count)
