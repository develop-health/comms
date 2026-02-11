---
description: Draft follow-up emails from today's meetings
allowed-tools: [Task, Read, Glob, Grep]
---

# Meeting Follow-ups

You are helping the user send follow-up emails after today's meetings. Follow these steps in order.

## Step 1 — Gather context (do both in parallel)

Call these two tools simultaneously:
- `list_calendar_events` (no arguments — defaults to today)
- `list_grain_recordings` (no arguments — defaults to today)

Wait for both to return before proceeding.

## Step 2 — Match recordings to events

For each calendar event today, check if a matching Grain recording exists by comparing:
- Meeting title / subject keywords
- Attendee names or email addresses
- Time overlap

Classify each event:
- **Interview** — the calendar event description contains an Ashby URL (e.g. `app.ashbyhq.com`) or the title suggests a candidate interview
- **External meeting** — has external attendees, not an interview
- **Internal/skip** — focus blocks, internal 1:1s, etc.

Present a list of today's meetings with their status: has recording, no recording, interview, or internal/skip.

Ask the user which meetings they want to follow up on.

## Step 3 — Process each selected meeting

### For interview events (with Grain transcript):

1. Fetch the transcript using `get_grain_transcript`
2. Summarize: key strengths, concerns, and action items from the interview
3. Extract the candidate name from the calendar event title
4. Search for the candidate in Ashby using `search_ashby_candidates`
5. For the matching candidate, get the application using `get_ashby_application`
6. Show: candidate name, current stage, job title
7. Ask: **"Progress, Reject, or Hold?"**
   - **Progress** →
     - Ask the user for a score (1-4) and brief recommendation
     - Submit feedback via `submit_ashby_feedback`
     - Get the interview plan stages via `list_ashby_interview_stages` to determine the next stage
     - Move candidate via `progress_ashby_candidate`
   - **Reject** →
     - Ask the user for a score (1-4) and brief recommendation
     - Submit feedback via `submit_ashby_feedback`
     - Fetch archive reasons via `list_ashby_archive_reasons` and ask user to pick one
     - Reject via `reject_ashby_candidate` (uses default rejection email template)
   - **Hold** →
     - Ask the user for a score (1-4) and brief recommendation
     - Submit feedback via `submit_ashby_feedback` only, no stage change
8. Optionally ask if the user wants to draft a follow-up email to the hiring team or candidate

### For non-interview meetings:

1. Show the meeting details: title, time, attendees (with email and RSVP status)
2. If a Grain recording exists, fetch the transcript using `get_grain_transcript`
3. Summarize the key discussion points and any action items from the transcript
4. Ask: **"Should I draft a follow-up email?"**
   - If yes: draft using `draft_email` with attendee emails as recipients. Include a brief meeting recap and any action items from the transcript. Show the draft.
   - User approves → `send_draft`
   - User wants edits → revise and re-draft
   - User skips → move to next meeting

## Step 4 — Summary

Recap the session:
- Number of meetings reviewed
- Number of follow-ups sent
- Number of candidates progressed/rejected/held
- Any meetings skipped
