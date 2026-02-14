# Comms

MCP server that gives [Claude Code](https://docs.anthropic.com/en/docs/claude-code) access to Gmail, Google Calendar, Grain, Google Sheets, Ashby, Slack, Google Drive, and Notion. Built to power daily email triage, meeting follow-ups, and candidate management from the terminal.

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
| `SLACK_BOT_TOKEN` | Slack bot token (`xoxb-`) for channel listing |
| `SLACK_USER_TOKEN` | Slack user token (`xoxp-`) for search, reading, and sending as yourself |
| `NOTION_API_TOKEN` | Notion internal integration token |

The Google service account needs domain-wide delegation with these scopes:
- `gmail.readonly`, `gmail.send`, `gmail.compose`, `gmail.modify`
- `calendar.readonly`
- `spreadsheets`
- `drive.readonly`

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

### Slack
- `search_slack` -- search messages across all joined channels
- `read_slack_thread` -- read a full thread by channel ID and timestamp
- `list_slack_channels` -- list available channels
- `send_slack_message` -- post a message or thread reply

### Google Drive
- `search_drive` -- search files by query (supports Drive search syntax)
- `read_drive_file` -- read content of Docs, Sheets, and Slides by file ID

### Notion
- `search_notion` -- search pages and databases by query
- `read_notion_page` -- read full page content as plain text

## Slash commands

### `/inbox` -- Daily email triage
Pulls your inbox, groups by thread, categorizes as Urgent / Important / Can Wait / Skip, then walks through drafting replies and archiving.

### `/followups` -- Post-meeting follow-ups
Matches today's calendar events to Grain recordings. For interviews, searches Ashby, summarizes the transcript, and offers to submit feedback and progress/reject the candidate. For other meetings, drafts follow-up emails with action items.

### `/prep` -- Daily meeting prep
Pulls today's calendar, classifies meetings by prep needed, then gathers context for each selected meeting: recent emails and Slack messages with attendees, related Grain recordings, and suggested talking points.
