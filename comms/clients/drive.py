"""Google Drive API client — search files, read documents."""

from googleapiclient.discovery import build

from ..config import GoogleConfig, DRIVE_SCOPES


def _get_service():
    config = GoogleConfig()
    creds = config.get_credentials(DRIVE_SCOPES)
    return build("drive", "v3", credentials=creds)


def _get_docs_service():
    config = GoogleConfig()
    creds = config.get_credentials(DRIVE_SCOPES)
    return build("docs", "v1", credentials=creds)


def _get_slides_service():
    config = GoogleConfig()
    creds = config.get_credentials(DRIVE_SCOPES)
    return build("slides", "v1", credentials=creds)


def search_files(query: str, max_results: int = 20) -> list[dict]:
    """Search Google Drive files. Supports Drive search query syntax."""
    service = _get_service()
    # Wrap user query with fullText search if it doesn't contain operators
    if "'" not in query and ":" not in query:
        drive_query = f"fullText contains '{query}' and trashed = false"
    else:
        drive_query = query
    resp = service.files().list(
        q=drive_query,
        pageSize=max_results,
        fields="files(id,name,mimeType,modifiedTime,webViewLink)",
        orderBy="modifiedTime desc",
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
    ).execute()
    files = resp.get("files", [])
    return [
        {
            "id": f.get("id", ""),
            "name": f.get("name", ""),
            "mimeType": f.get("mimeType", ""),
            "modifiedTime": f.get("modifiedTime", ""),
            "link": f.get("webViewLink", ""),
        }
        for f in files
    ]


def _extract_doc_text(doc: dict) -> str:
    """Extract plain text from a Google Docs document JSON."""
    text_parts = []
    for element in doc.get("body", {}).get("content", []):
        paragraph = element.get("paragraph")
        if not paragraph:
            continue
        for pe in paragraph.get("elements", []):
            text_run = pe.get("textRun")
            if text_run:
                text_parts.append(text_run.get("content", ""))
    return "".join(text_parts)


def read_file(file_id: str) -> dict:
    """Read content of a Google Drive file.

    For Google Docs, returns the full text content.
    For Google Sheets, returns the first sheet values.
    For other types, returns metadata only.
    """
    service = _get_service()
    meta = service.files().get(
        fileId=file_id,
        fields="id,name,mimeType,modifiedTime,webViewLink",
        supportsAllDrives=True,
    ).execute()
    mime = meta.get("mimeType", "")
    result = {
        "id": meta.get("id", ""),
        "name": meta.get("name", ""),
        "mimeType": mime,
        "modifiedTime": meta.get("modifiedTime", ""),
        "link": meta.get("webViewLink", ""),
    }

    if mime == "application/vnd.google-apps.document":
        docs_service = _get_docs_service()
        doc = docs_service.documents().get(documentId=file_id).execute()
        result["content"] = _extract_doc_text(doc)
    elif mime == "application/vnd.google-apps.spreadsheet":
        from ..config import SHEETS_SCOPES
        config = GoogleConfig()
        creds = config.get_credentials(SHEETS_SCOPES)
        sheets_service = build("sheets", "v4", credentials=creds)
        sheet_data = sheets_service.spreadsheets().values().get(
            spreadsheetId=file_id, range="Sheet1!A:Z"
        ).execute()
        result["content"] = sheet_data.get("values", [])
    elif mime == "application/vnd.google-apps.presentation":
        slides_service = _get_slides_service()
        presentation = slides_service.presentations().get(
            presentationId=file_id
        ).execute()
        slides_text = []
        for i, slide in enumerate(presentation.get("slides", []), 1):
            slide_parts = []
            for element in slide.get("pageElements", []):
                shape = element.get("shape", {})
                text_content = shape.get("text", {})
                for text_el in text_content.get("textElements", []):
                    text_run = text_el.get("textRun", {})
                    content = text_run.get("content", "")
                    if content.strip():
                        slide_parts.append(content.strip())
            if slide_parts:
                slides_text.append(f"--- Slide {i} ---\n" + "\n".join(slide_parts))
        result["content"] = "\n\n".join(slides_text)
    else:
        result["content"] = "(Binary or unsupported file type – metadata only)"

    return result
