# Comms

MCP server that gives [Claude Code](https://docs.anthropic.com/en/docs/claude-code) access to Gmail, Google Calendar, Grain, Google Sheets, and Ashby. Built to power daily email triage, meeting follow-ups, and candidate management from the terminal.

## Setup

```bash
poetry install
cp .env.example .env  # fill in your credentials
```

### Environment variables

| Variable | Description |
|----------|-------------|
| `GOOGLE_APPLICATION_CREDENTIALS` | JSON string of a Google service account key with domain-wide delegation |
| `GOOGLE_DELEGATED_USER` | Email to impersonate (default: `mel@develophealth.ai`) |
| `GRAIN_WORKSPACE_API_TOKEN` | Grain workspace API token |
| `ASHBY_API_KEY` | Ashby API key with `candidates:read`, `candidates:write`, `interviews:read`, `interviews:write` scopes |

The Google service account needs domain-wide delegation with these scopes:
- `gmail.readonly`, `gmail.send`, `gmail.compose`, `gmail.modify`
- `calendar.readonly`
- `spreadsheets`

### Claude Code configuration

Add to your `.mcp.json`:

```json
{
  "mcpServers": {
    "comms": {
      "command": "poetry",
      "args": ["run", "python", "-m", "comms.mcp"],
      "cwd": "/path/to/comms"
    }
  }
}
```

## Tools

### Gmail
- `search_emails` -- search with Gmail query syntax
- `read_email` / `read_thread` -- read messages and threads
- `draft_email` / `send_draft` / `send_email` -- compose and send
- `archive_email` -- remove from inbox

### Calendar
- `list_calendar_events` / `get_calendar_event` -- read events for a date

### Grain
- `list_grain_recordings` / `get_grain_transcript` -- list recordings and fetch transcripts

### Google Sheets
- `read_spreadsheet` / `append_rows` / `update_cells` -- read and write spreadsheet data

### Ashby ATS
- `search_ashby_candidates` -- find candidates by name
- `get_ashby_application` -- application details and current stage
- `list_ashby_interview_stages` -- ordered stages for an interview plan
- `list_ashby_archive_reasons` -- rejection reasons
- `submit_ashby_feedback` -- submit interview scorecard (auto-discovers the pending interview and feedback form)
- `progress_ashby_candidate` / `reject_ashby_candidate` -- move or reject candidates

## Slash commands

### `/inbox` -- Daily email triage
Pulls your inbox, groups by thread, categorizes as Urgent / Important / Can Wait / Skip, then walks through drafting replies and archiving.

### `/followups` -- Post-meeting follow-ups
Matches today's calendar events to Grain recordings. For interviews, searches Ashby, summarizes the transcript, and offers to submit feedback and progress/reject the candidate. For other meetings, drafts follow-up emails with action items.
