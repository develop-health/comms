"""Grain API client — list recordings, get transcript."""

from datetime import datetime, timedelta

import requests

from ..config import GrainConfig


def _get_config() -> GrainConfig:
    config = GrainConfig()
    if not config.api_token:
        raise ValueError("Missing GRAIN_WORKSPACE_API_TOKEN environment variable")
    return config


def _headers(config: GrainConfig) -> dict:
    return {
        "Authorization": f"Bearer {config.api_token}",
        "Content-Type": "application/json",
        "Public-Api-Version": "2025-10-31",
    }


def list_grain_recordings(date: str = "") -> list[dict]:
    """List recordings for a date (YYYY-MM-DD). Defaults to today."""
    config = _get_config()

    if date:
        day = datetime.strptime(date, "%Y-%m-%d")
    else:
        day = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    start = day.isoformat() + "Z"
    end = (day + timedelta(days=1)).isoformat() + "Z"

    all_recordings: list[dict] = []
    cursor = None

    while True:
        payload: dict = {"include": {"participants": True}}
        if cursor:
            payload["cursor"] = cursor

        resp = requests.post(
            f"{config.base_url}/recordings",
            headers=_headers(config),
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()

        recordings = data.get("recordings", [])
        for rec in recordings:
            rec_start = rec.get("start_datetime", "")
            if rec_start and not (start <= rec_start < end):
                continue
            all_recordings.append({
                "id": rec.get("id", ""),
                "title": rec.get("title", ""),
                "start_datetime": rec_start,
                "end_datetime": rec.get("end_datetime", ""),
                "duration": rec.get("duration", 0),
                "participants": rec.get("participants", []),
                "url": rec.get("url", ""),
            })

        next_cursor = data.get("cursor")
        if not next_cursor or not recordings:
            break
        cursor = next_cursor

    return all_recordings


def get_grain_transcript(recording_id: str) -> str:
    """Full transcript (Speaker: line format)."""
    config = _get_config()
    resp = requests.get(
        f"{config.base_url}/recordings/{recording_id}/transcript.txt",
        headers=_headers(config),
    )
    resp.raise_for_status()
    return resp.text
