"""Environment-based configuration."""

import json
import os
from dataclasses import dataclass, field

from google.oauth2 import service_account


GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.modify",
]

CALENDAR_SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
]

SHEETS_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]

DRIVE_SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
]


@dataclass
class GoogleConfig:
    delegated_user: str = field(
        default_factory=lambda: os.environ.get(
            "GOOGLE_DELEGATED_USER", "mel@develophealth.ai"
        )
    )

    def get_credentials(self, scopes: list[str]) -> service_account.Credentials:
        raw_json = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if not raw_json:
            raise ValueError("Missing GOOGLE_APPLICATION_CREDENTIALS environment variable")
        credentials_info = json.loads(raw_json)
        creds = service_account.Credentials.from_service_account_info(
            credentials_info, scopes=scopes
        )
        return creds.with_subject(self.delegated_user)


@dataclass
class GrainConfig:
    api_token: str = field(
        default_factory=lambda: os.environ.get("GRAIN_WORKSPACE_API_TOKEN", "")
    )
    base_url: str = field(
        default_factory=lambda: os.environ.get(
            "GRAIN_API_BASE_URL", "https://api.grain.com/_/public-api/v2"
        ).rstrip("/")
    )


@dataclass
class SlackConfig:
    bot_token: str = field(
        default_factory=lambda: os.environ.get("SLACK_BOT_TOKEN", "")
    )
    user_token: str = field(
        default_factory=lambda: os.environ.get("SLACK_USER_TOKEN", "")
    )


@dataclass
class NotionConfig:
    api_token: str = field(
        default_factory=lambda: os.environ.get("NOTION_API_TOKEN", "")
    )
    base_url: str = "https://api.notion.com/v1"
    api_version: str = "2022-06-28"


@dataclass
class AshbyConfig:
    api_key: str = field(
        default_factory=lambda: os.environ.get("ASHBY_API_KEY", "")
    )
    base_url: str = "https://api.ashbyhq.com"
