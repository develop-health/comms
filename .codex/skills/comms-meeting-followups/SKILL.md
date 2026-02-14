---
name: comms-meeting-followups
description: Run post-meeting follow-up workflows in Codex using Comms MCP tools, including interview handling with Ashby.
---

# Comms Meeting Follow-ups

Use this workflow when the user wants follow-up emails and interview actions after today's meetings.

## Workflow

1. Gather context in parallel:
   - `list_calendar_events` for today.
   - `list_grain_recordings` for today.

2. Match events to recordings:
   - Match by title keywords, attendee overlap, and time overlap.
   - Classify events:
     - `Interview`: title/description suggests candidate interview or includes Ashby URL.
     - `External meeting`: non-interview meeting with outside attendees.
     - `Internal/skip`: focus blocks or internal-only meetings.
   - Ask user which meetings to process.

3. Process selected meetings:
   - Interview path:
     - Pull transcript with `get_grain_transcript`.
     - Summarize strengths, concerns, and action items.
     - Identify candidate and call `search_ashby_candidates`.
     - Pull application with `get_ashby_application`.
     - Ask user: `Progress`, `Reject`, or `Hold`.
     - Collect score/recommendation and call `submit_ashby_feedback`.
     - If `Progress`: call `list_ashby_interview_stages`, then `progress_ashby_candidate`.
     - If `Reject`: call `list_ashby_archive_reasons`, then `reject_ashby_candidate`.
   - Non-interview path:
     - Show meeting details and attendees.
     - If recording exists, summarize transcript and action items.
     - Ask whether to draft follow-up.
     - If yes, call `draft_email`; on approval call `send_draft`.

4. Summarize:
   - Meetings reviewed, follow-ups sent.
   - Candidate outcomes: progressed/rejected/held.
   - Skipped items.
