"""Google Sheets API client — read, append, update."""

from typing import Any

from googleapiclient.discovery import build

from ..config import GoogleConfig, SHEETS_SCOPES


def _get_service():
    config = GoogleConfig()
    creds = config.get_credentials(SHEETS_SCOPES)
    return build("sheets", "v4", credentials=creds)


def read_spreadsheet(spreadsheet_id: str, range: str) -> list[list[str]]:
    """Read values from a spreadsheet range. Returns list of rows."""
    service = _get_service()
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=range
    ).execute()
    return result.get("values", [])


def append_rows(
    spreadsheet_id: str, range: str, rows: list[list[Any]]
) -> dict:
    """Append rows to a spreadsheet. Returns update metadata."""
    service = _get_service()
    body = {"values": rows}
    result = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=range,
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body=body,
    ).execute()
    return {
        "updatedRange": result.get("updates", {}).get("updatedRange", ""),
        "updatedRows": result.get("updates", {}).get("updatedRows", 0),
        "updatedCells": result.get("updates", {}).get("updatedCells", 0),
    }


def update_cells(
    spreadsheet_id: str, range: str, values: list[list[Any]]
) -> dict:
    """Update specific cells in a spreadsheet range."""
    service = _get_service()
    body = {"values": values}
    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range,
        valueInputOption="USER_ENTERED",
        body=body,
    ).execute()
    return {
        "updatedRange": result.get("updatedRange", ""),
        "updatedRows": result.get("updatedRows", 0),
        "updatedCells": result.get("updatedCells", 0),
    }
