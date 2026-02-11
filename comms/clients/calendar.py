"""Google Calendar API client — list/get events."""

from datetime import datetime, timedelta

from googleapiclient.discovery import build

from ..config import GoogleConfig, CALENDAR_SCOPES


def _get_service():
    config = GoogleConfig()
    creds = config.get_credentials(CALENDAR_SCOPES)
    return build("calendar", "v3", credentials=creds)


def _format_event(event: dict) -> dict:
    start = event.get("start", {})
    end = event.get("end", {})
    attendees = []
    for a in event.get("attendees", []):
        attendees.append({
            "email": a.get("email", ""),
            "displayName": a.get("displayName", ""),
            "responseStatus": a.get("responseStatus", ""),
            "self": a.get("self", False),
        })
    return {
        "id": event.get("id", ""),
        "summary": event.get("summary", ""),
        "start": start.get("dateTime", start.get("date", "")),
        "end": end.get("dateTime", end.get("date", "")),
        "attendees": attendees,
        "description": event.get("description", ""),
        "hangoutLink": event.get("hangoutLink", ""),
        "htmlLink": event.get("htmlLink", ""),
        "status": event.get("status", ""),
    }


def list_calendar_events(date: str = "") -> list[dict]:
    """List events for a date (YYYY-MM-DD). Defaults to today."""
    service = _get_service()
    if date:
        day = datetime.strptime(date, "%Y-%m-%d")
    else:
        day = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    time_min = day.isoformat() + "Z"
    time_max = (day + timedelta(days=1)).isoformat() + "Z"

    resp = service.events().list(
        calendarId="primary",
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    return [_format_event(e) for e in resp.get("items", [])]


def get_calendar_event(event_id: str) -> dict:
    """Full details of a specific event by ID."""
    service = _get_service()
    event = service.events().get(
        calendarId="primary", eventId=event_id
    ).execute()
    return _format_event(event)
