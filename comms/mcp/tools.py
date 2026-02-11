"""Tool definitions and handlers for the Comms MCP server."""

import asyncio
import json
import logging
from typing import Any

from ..clients import gmail, calendar, grain, sheets, ashby

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

TOOL_DEFINITIONS: list[dict[str, Any]] = [
    # --- Email Reading ---
    {
        "name": "search_emails",
        "description": (
            "Search Gmail with query syntax (from:, subject:, after:, is:inbox, etc.). "
            "Returns id, threadId, subject, from, date, snippet for each result."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Gmail search query (e.g. 'is:inbox newer_than:1d')",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results (default 20)",
                    "default": 20,
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "read_email",
        "description": (
            "Read a specific email message by ID. "
            "Returns full body, headers, and attachment names."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "message_id": {
                    "type": "string",
                    "description": "The Gmail message ID",
                },
            },
            "required": ["message_id"],
        },
    },
    {
        "name": "read_thread",
        "description": (
            "Read an entire email thread by threadId. "
            "Returns all messages chronologically with full body."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "thread_id": {
                    "type": "string",
                    "description": "The Gmail thread ID",
                },
            },
            "required": ["thread_id"],
        },
    },
    # --- Email Writing ---
    {
        "name": "draft_email",
        "description": (
            "Create a draft email. Saved to Drafts, NOT sent. "
            "Use reply_to_message_id to thread as a reply."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "to": {
                    "type": "string",
                    "description": "Recipient email address(es)",
                },
                "subject": {
                    "type": "string",
                    "description": "Email subject line",
                },
                "body": {
                    "type": "string",
                    "description": "Email body (plain text)",
                },
                "cc": {
                    "type": "string",
                    "description": "CC email address(es)",
                    "default": "",
                },
                "reply_to_message_id": {
                    "type": "string",
                    "description": "Message ID to reply to (threads the reply)",
                    "default": "",
                },
            },
            "required": ["to", "subject", "body"],
        },
    },
    {
        "name": "send_draft",
        "description": "Send a previously created draft by its draftId.",
        "input_schema": {
            "type": "object",
            "properties": {
                "draft_id": {
                    "type": "string",
                    "description": "The Gmail draft ID to send",
                },
            },
            "required": ["draft_id"],
        },
    },
    {
        "name": "archive_email",
        "description": "Archive an email by removing it from the inbox.",
        "input_schema": {
            "type": "object",
            "properties": {
                "message_id": {
                    "type": "string",
                    "description": "The Gmail message ID to archive",
                },
            },
            "required": ["message_id"],
        },
    },
    {
        "name": "send_email",
        "description": (
            "Compose and immediately send an email (no draft review step)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "to": {
                    "type": "string",
                    "description": "Recipient email address(es)",
                },
                "subject": {
                    "type": "string",
                    "description": "Email subject line",
                },
                "body": {
                    "type": "string",
                    "description": "Email body (plain text)",
                },
                "cc": {
                    "type": "string",
                    "description": "CC email address(es)",
                    "default": "",
                },
            },
            "required": ["to", "subject", "body"],
        },
    },
    # --- Calendar ---
    {
        "name": "list_calendar_events",
        "description": (
            "List calendar events for a date (default: today). "
            "Returns title, time, attendees with email/RSVP, description, meet link."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "Date in YYYY-MM-DD format (defaults to today)",
                    "default": "",
                },
            },
            "required": [],
        },
    },
    {
        "name": "get_calendar_event",
        "description": "Get full details of a specific calendar event by ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "event_id": {
                    "type": "string",
                    "description": "The Google Calendar event ID",
                },
            },
            "required": ["event_id"],
        },
    },
    # --- Grain ---
    {
        "name": "list_grain_recordings",
        "description": (
            "List Grain recordings for a date (default: today). "
            "Returns title, date, duration, participants."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "Date in YYYY-MM-DD format (defaults to today)",
                    "default": "",
                },
            },
            "required": [],
        },
    },
    {
        "name": "get_grain_transcript",
        "description": (
            "Get full transcript of a Grain recording (Speaker: line format)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "recording_id": {
                    "type": "string",
                    "description": "The Grain recording ID",
                },
            },
            "required": ["recording_id"],
        },
    },
    # --- Google Sheets ---
    {
        "name": "read_spreadsheet",
        "description": (
            "Read values from a Google Spreadsheet range. "
            "Returns rows as lists of cell values."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "spreadsheet_id": {
                    "type": "string",
                    "description": "The spreadsheet ID from the URL",
                },
                "range": {
                    "type": "string",
                    "description": "A1 notation range (e.g. 'Sheet1!A:Z' or 'Sheet1!A1:D10')",
                    "default": "Sheet1!A:Z",
                },
            },
            "required": ["spreadsheet_id"],
        },
    },
    {
        "name": "append_rows",
        "description": (
            "Append rows to a Google Spreadsheet. "
            "Each row is a list of cell values."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "spreadsheet_id": {
                    "type": "string",
                    "description": "The spreadsheet ID from the URL",
                },
                "range": {
                    "type": "string",
                    "description": "A1 notation range to append to (e.g. 'Sheet1!A:Z')",
                    "default": "Sheet1!A:Z",
                },
                "rows": {
                    "type": "array",
                    "description": "List of rows, each row is a list of cell values",
                    "items": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
            },
            "required": ["spreadsheet_id", "rows"],
        },
    },
    {
        "name": "update_cells",
        "description": (
            "Update specific cells in a Google Spreadsheet range. "
            "Use A1 notation for the range (e.g. 'Sheet1!H5' or 'Sheet1!A1:D2')."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "spreadsheet_id": {
                    "type": "string",
                    "description": "The spreadsheet ID from the URL",
                },
                "range": {
                    "type": "string",
                    "description": "A1 notation range to update (e.g. 'Sheet1!H5')",
                },
                "values": {
                    "type": "array",
                    "description": "2D array of values to write",
                    "items": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
            },
            "required": ["spreadsheet_id", "range", "values"],
        },
    },
    # --- Ashby ATS ---
    {
        "name": "search_ashby_candidates",
        "description": "Search Ashby ATS candidates by name.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Candidate name to search for",
                },
            },
            "required": ["name"],
        },
    },
    {
        "name": "get_ashby_application",
        "description": (
            "Get Ashby application details including current stage and interview plan."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "application_id": {
                    "type": "string",
                    "description": "The Ashby application ID",
                },
            },
            "required": ["application_id"],
        },
    },
    {
        "name": "list_ashby_interview_stages",
        "description": "List ordered interview stages for an interview plan.",
        "input_schema": {
            "type": "object",
            "properties": {
                "interview_plan_id": {
                    "type": "string",
                    "description": "The Ashby interview plan ID",
                },
            },
            "required": ["interview_plan_id"],
        },
    },
    {
        "name": "list_ashby_archive_reasons",
        "description": "List available archive/rejection reasons in Ashby.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "submit_ashby_feedback",
        "description": "Submit interview scorecard feedback for an application.",
        "input_schema": {
            "type": "object",
            "properties": {
                "application_id": {
                    "type": "string",
                    "description": "The Ashby application ID",
                },
                "summary": {
                    "type": "string",
                    "description": "Interview feedback summary",
                },
                "score": {
                    "type": "integer",
                    "description": "Overall score (1-4)",
                    "minimum": 1,
                    "maximum": 4,
                },
                "recommendation": {
                    "type": "string",
                    "description": (
                        "Recommendation: definitely_yes, strong_yes, yes, "
                        "no, strong_no, definitely_no"
                    ),
                },
            },
            "required": ["application_id", "summary", "score", "recommendation"],
        },
    },
    {
        "name": "progress_ashby_candidate",
        "description": "Move a candidate to the next interview stage in Ashby.",
        "input_schema": {
            "type": "object",
            "properties": {
                "application_id": {
                    "type": "string",
                    "description": "The Ashby application ID",
                },
                "interview_stage_id": {
                    "type": "string",
                    "description": "The target interview stage ID",
                },
            },
            "required": ["application_id", "interview_stage_id"],
        },
    },
    {
        "name": "reject_ashby_candidate",
        "description": "Archive/reject a candidate with a rejection email in Ashby.",
        "input_schema": {
            "type": "object",
            "properties": {
                "application_id": {
                    "type": "string",
                    "description": "The Ashby application ID",
                },
                "archive_reason_id": {
                    "type": "string",
                    "description": "The archive reason ID",
                },
                "rejection_template_id": {
                    "type": "string",
                    "description": "Rejection email template ID",
                    "default": "07e79d76-8a03-44ac-9c2d-76ad5d4e3ab7",
                },
            },
            "required": ["application_id", "archive_reason_id"],
        },
    },
]

# ---------------------------------------------------------------------------
# Tool handlers
# ---------------------------------------------------------------------------


async def handle_search_emails(arguments: dict) -> str:
    results = await asyncio.to_thread(
        gmail.search_emails,
        query=arguments["query"],
        max_results=arguments.get("max_results", 20),
    )
    return json.dumps(results, indent=2)


async def handle_read_email(arguments: dict) -> str:
    result = await asyncio.to_thread(
        gmail.read_email, message_id=arguments["message_id"]
    )
    return json.dumps(result, indent=2)


async def handle_read_thread(arguments: dict) -> str:
    results = await asyncio.to_thread(
        gmail.read_thread, thread_id=arguments["thread_id"]
    )
    return json.dumps(results, indent=2)


async def handle_draft_email(arguments: dict) -> str:
    result = await asyncio.to_thread(
        gmail.draft_email,
        to=arguments["to"],
        subject=arguments["subject"],
        body=arguments["body"],
        cc=arguments.get("cc", ""),
        reply_to_message_id=arguments.get("reply_to_message_id", ""),
    )
    return json.dumps(result, indent=2)


async def handle_send_draft(arguments: dict) -> str:
    result = await asyncio.to_thread(
        gmail.send_draft, draft_id=arguments["draft_id"]
    )
    return json.dumps(result, indent=2)


async def handle_archive_email(arguments: dict) -> str:
    result = await asyncio.to_thread(
        gmail.archive_email, message_id=arguments["message_id"]
    )
    return json.dumps(result, indent=2)


async def handle_send_email(arguments: dict) -> str:
    result = await asyncio.to_thread(
        gmail.send_email,
        to=arguments["to"],
        subject=arguments["subject"],
        body=arguments["body"],
        cc=arguments.get("cc", ""),
    )
    return json.dumps(result, indent=2)


async def handle_list_calendar_events(arguments: dict) -> str:
    results = await asyncio.to_thread(
        calendar.list_calendar_events,
        date=arguments.get("date", ""),
    )
    return json.dumps(results, indent=2)


async def handle_get_calendar_event(arguments: dict) -> str:
    result = await asyncio.to_thread(
        calendar.get_calendar_event,
        event_id=arguments["event_id"],
    )
    return json.dumps(result, indent=2)


async def handle_list_grain_recordings(arguments: dict) -> str:
    results = await asyncio.to_thread(
        grain.list_grain_recordings,
        date=arguments.get("date", ""),
    )
    return json.dumps(results, indent=2)


async def handle_get_grain_transcript(arguments: dict) -> str:
    result = await asyncio.to_thread(
        grain.get_grain_transcript,
        recording_id=arguments["recording_id"],
    )
    return result  # Already a string (plain text transcript)


async def handle_read_spreadsheet(arguments: dict) -> str:
    result = await asyncio.to_thread(
        sheets.read_spreadsheet,
        spreadsheet_id=arguments["spreadsheet_id"],
        range=arguments.get("range", "Sheet1!A:Z"),
    )
    return json.dumps(result, indent=2)


async def handle_append_rows(arguments: dict) -> str:
    result = await asyncio.to_thread(
        sheets.append_rows,
        spreadsheet_id=arguments["spreadsheet_id"],
        range=arguments.get("range", "Sheet1!A:Z"),
        rows=arguments["rows"],
    )
    return json.dumps(result, indent=2)


async def handle_update_cells(arguments: dict) -> str:
    result = await asyncio.to_thread(
        sheets.update_cells,
        spreadsheet_id=arguments["spreadsheet_id"],
        range=arguments["range"],
        values=arguments["values"],
    )
    return json.dumps(result, indent=2)


async def handle_search_ashby_candidates(arguments: dict) -> str:
    results = await asyncio.to_thread(
        ashby.search_candidates, name=arguments["name"]
    )
    return json.dumps(results, indent=2)


async def handle_get_ashby_application(arguments: dict) -> str:
    result = await asyncio.to_thread(
        ashby.get_application, application_id=arguments["application_id"]
    )
    return json.dumps(result, indent=2)


async def handle_list_ashby_interview_stages(arguments: dict) -> str:
    results = await asyncio.to_thread(
        ashby.list_interview_stages,
        interview_plan_id=arguments["interview_plan_id"],
    )
    return json.dumps(results, indent=2)


async def handle_list_ashby_archive_reasons(arguments: dict) -> str:
    results = await asyncio.to_thread(ashby.list_archive_reasons)
    return json.dumps(results, indent=2)


async def handle_submit_ashby_feedback(arguments: dict) -> str:
    result = await asyncio.to_thread(
        ashby.submit_feedback,
        application_id=arguments["application_id"],
        summary=arguments["summary"],
        score=arguments["score"],
        recommendation=arguments["recommendation"],
    )
    return json.dumps(result, indent=2)


async def handle_progress_ashby_candidate(arguments: dict) -> str:
    result = await asyncio.to_thread(
        ashby.progress_candidate,
        application_id=arguments["application_id"],
        interview_stage_id=arguments["interview_stage_id"],
    )
    return json.dumps(result, indent=2)


async def handle_reject_ashby_candidate(arguments: dict) -> str:
    result = await asyncio.to_thread(
        ashby.reject_candidate,
        application_id=arguments["application_id"],
        archive_reason_id=arguments["archive_reason_id"],
        rejection_template_id=arguments.get(
            "rejection_template_id", "07e79d76-8a03-44ac-9c2d-76ad5d4e3ab7"
        ),
    )
    return json.dumps(result, indent=2)


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

TOOL_HANDLERS = {
    "search_emails": handle_search_emails,
    "read_email": handle_read_email,
    "read_thread": handle_read_thread,
    "draft_email": handle_draft_email,
    "send_draft": handle_send_draft,
    "archive_email": handle_archive_email,
    "send_email": handle_send_email,
    "list_calendar_events": handle_list_calendar_events,
    "get_calendar_event": handle_get_calendar_event,
    "list_grain_recordings": handle_list_grain_recordings,
    "get_grain_transcript": handle_get_grain_transcript,
    "read_spreadsheet": handle_read_spreadsheet,
    "append_rows": handle_append_rows,
    "update_cells": handle_update_cells,
    "search_ashby_candidates": handle_search_ashby_candidates,
    "get_ashby_application": handle_get_ashby_application,
    "list_ashby_interview_stages": handle_list_ashby_interview_stages,
    "list_ashby_archive_reasons": handle_list_ashby_archive_reasons,
    "submit_ashby_feedback": handle_submit_ashby_feedback,
    "progress_ashby_candidate": handle_progress_ashby_candidate,
    "reject_ashby_candidate": handle_reject_ashby_candidate,
}


async def call_tool(name: str, arguments: dict) -> str:
    handler = TOOL_HANDLERS.get(name)
    if not handler:
        return json.dumps({"error": f"Unknown tool: {name}"})
    try:
        return await handler(arguments)
    except Exception as e:
        logger.exception(f"Error in tool {name}")
        return json.dumps({"error": str(e)})
