"""Gmail API client — search, read, draft, send."""

import base64
from email.mime.text import MIMEText
from typing import Any

from googleapiclient.discovery import build

from ..config import GoogleConfig, GMAIL_SCOPES


def _get_service():
    config = GoogleConfig()
    creds = config.get_credentials(GMAIL_SCOPES)
    return build("gmail", "v1", credentials=creds)


def _get_plain_text_body(payload: dict) -> str:
    """Recursively extract plain-text body from a Gmail message payload."""
    if "parts" in payload:
        for part in payload["parts"]:
            body = _get_plain_text_body(part)
            if body:
                return body
    else:
        mime_type = payload.get("mimeType", "")
        if mime_type == "text/plain":
            data = payload.get("body", {}).get("data")
            if data:
                return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
    return ""


def _header(headers: list[dict], name: str) -> str:
    for h in headers:
        if h["name"].lower() == name.lower():
            return h["value"]
    return ""


def _format_message(msg: dict) -> dict[str, Any]:
    headers = msg.get("payload", {}).get("headers", [])
    return {
        "id": msg["id"],
        "threadId": msg["threadId"],
        "subject": _header(headers, "Subject"),
        "from": _header(headers, "From"),
        "to": _header(headers, "To"),
        "cc": _header(headers, "Cc"),
        "date": _header(headers, "Date"),
        "snippet": msg.get("snippet", ""),
        "labelIds": msg.get("labelIds", []),
    }


def _format_message_full(msg: dict) -> dict[str, Any]:
    result = _format_message(msg)
    result["body"] = _get_plain_text_body(msg.get("payload", {}))
    # List attachment names
    attachments = []
    for part in msg.get("payload", {}).get("parts", []):
        filename = part.get("filename")
        if filename:
            attachments.append(filename)
    result["attachments"] = attachments
    return result


def search_emails(query: str, max_results: int = 20) -> list[dict]:
    """Search Gmail with query syntax. Returns message summaries."""
    service = _get_service()
    resp = service.users().messages().list(
        userId="me", q=query, maxResults=max_results
    ).execute()

    messages = resp.get("messages", [])
    if not messages:
        return []

    results = []
    for m in messages:
        msg = service.users().messages().get(
            userId="me", id=m["id"], format="metadata",
            metadataHeaders=["Subject", "From", "To", "Cc", "Date"],
        ).execute()
        results.append(_format_message(msg))
    return results


def read_email(message_id: str) -> dict:
    """Read a specific message by ID. Full body + headers + attachments."""
    service = _get_service()
    msg = service.users().messages().get(
        userId="me", id=message_id, format="full"
    ).execute()
    return _format_message_full(msg)


def read_thread(thread_id: str) -> list[dict]:
    """Read entire email thread by threadId. All messages chronologically."""
    service = _get_service()
    thread = service.users().threads().get(
        userId="me", id=thread_id, format="full"
    ).execute()
    return [_format_message_full(msg) for msg in thread.get("messages", [])]


def draft_email(
    to: str,
    subject: str,
    body: str,
    cc: str = "",
    reply_to_message_id: str = "",
) -> dict:
    """Create a draft. Returns draftId and message metadata."""
    service = _get_service()
    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject
    if cc:
        message["cc"] = cc

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    draft_body: dict[str, Any] = {"message": {"raw": raw}}
    if reply_to_message_id:
        # Set threadId so Gmail threads the reply
        orig = service.users().messages().get(
            userId="me", id=reply_to_message_id, format="metadata",
            metadataHeaders=["Subject", "Message-ID"],
        ).execute()
        thread_id = orig.get("threadId")
        if thread_id:
            draft_body["message"]["threadId"] = thread_id
        # Set In-Reply-To and References headers
        orig_headers = orig.get("payload", {}).get("headers", [])
        orig_message_id = _header(orig_headers, "Message-ID")
        if orig_message_id:
            message["In-Reply-To"] = orig_message_id
            message["References"] = orig_message_id
            # Re-encode with the new headers
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            draft_body["message"]["raw"] = raw

    draft = service.users().drafts().create(userId="me", body=draft_body).execute()
    return {
        "draftId": draft["id"],
        "messageId": draft["message"]["id"],
        "threadId": draft["message"].get("threadId", ""),
    }


def send_draft(draft_id: str) -> dict:
    """Send a previously created draft by draftId."""
    service = _get_service()
    result = service.users().drafts().send(
        userId="me", body={"id": draft_id}
    ).execute()
    return {
        "messageId": result["id"],
        "threadId": result.get("threadId", ""),
        "labelIds": result.get("labelIds", []),
    }


def archive_email(message_id: str) -> dict:
    """Archive an email by removing the INBOX label from all messages in its thread."""
    service = _get_service()
    # Get the threadId for this message
    msg = service.users().messages().get(
        userId="me", id=message_id, format="minimal"
    ).execute()
    thread_id = msg.get("threadId")
    # Archive the entire thread
    service.users().threads().modify(
        userId="me",
        id=thread_id,
        body={"removeLabelIds": ["INBOX"]},
    ).execute()
    return {"status": "archived", "messageId": message_id, "threadId": thread_id}


def send_email(
    to: str,
    subject: str,
    body: str,
    cc: str = "",
) -> dict:
    """Compose and immediately send an email (no draft review step)."""
    service = _get_service()
    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject
    if cc:
        message["cc"] = cc

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    result = service.users().messages().send(
        userId="me", body={"raw": raw}
    ).execute()
    return {
        "messageId": result["id"],
        "threadId": result.get("threadId", ""),
        "labelIds": result.get("labelIds", []),
    }
