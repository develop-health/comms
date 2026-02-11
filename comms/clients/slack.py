"""Slack API client — search messages, read threads, list channels, send messages.

Uses the user token (xoxp-) for everything so it acts as Mel and has access
to all channels Mel is a member of.
"""

from slack_sdk import WebClient

from ..config import SlackConfig


def _get_config() -> SlackConfig:
    return SlackConfig()


def _bot_client() -> WebClient:
    config = _get_config()
    if not config.bot_token:
        raise ValueError("Missing SLACK_BOT_TOKEN environment variable")
    return WebClient(token=config.bot_token)


def _user_client() -> WebClient:
    config = _get_config()
    if not config.user_token:
        raise ValueError("Missing SLACK_USER_TOKEN environment variable")
    return WebClient(token=config.user_token)


def _resolve_user_name(client: WebClient, user_id: str) -> str:
    """Resolve a Slack user ID to a display name."""
    try:
        resp = client.users_info(user=user_id)
        profile = resp["user"].get("profile", {})
        return profile.get("real_name") or profile.get("display_name") or user_id
    except Exception:
        return user_id


def search_messages(query: str, max_results: int = 20) -> list[dict]:
    """Search Slack messages across all public/joined channels."""
    client = _user_client()
    resp = client.search_messages(query=query, count=max_results)
    matches = resp.get("messages", {}).get("matches", [])
    results = []
    for msg in matches:
        results.append({
            "channel": msg.get("channel", {}).get("name", ""),
            "channel_id": msg.get("channel", {}).get("id", ""),
            "user": msg.get("username", ""),
            "text": msg.get("text", ""),
            "ts": msg.get("ts", ""),
            "permalink": msg.get("permalink", ""),
        })
    return results


def read_thread(channel_id: str, thread_ts: str) -> list[dict]:
    """Read a full Slack thread by channel ID and thread timestamp."""
    client = _user_client()
    resp = client.conversations_replies(channel=channel_id, ts=thread_ts)
    messages = resp.get("messages", [])
    user_cache: dict[str, str] = {}
    results = []
    for msg in messages:
        user_id = msg.get("user", "")
        if user_id and user_id not in user_cache:
            user_cache[user_id] = _resolve_user_name(client, user_id)
        results.append({
            "user": user_cache.get(user_id, user_id),
            "text": msg.get("text", ""),
            "ts": msg.get("ts", ""),
        })
    return results


def list_channels(limit: int = 100) -> list[dict]:
    """List available Slack channels."""
    client = _user_client()
    resp = client.conversations_list(
        types="public_channel,private_channel",
        exclude_archived=True,
        limit=limit,
    )
    channels = resp.get("channels", [])
    return [
        {
            "id": ch.get("id", ""),
            "name": ch.get("name", ""),
            "topic": ch.get("topic", {}).get("value", ""),
            "num_members": ch.get("num_members", 0),
        }
        for ch in channels
    ]


def send_message(channel: str, text: str, thread_ts: str = "") -> dict:
    """Post a message to a Slack channel as Mel (user token)."""
    client = _user_client()
    kwargs = {"channel": channel, "text": text}
    if thread_ts:
        kwargs["thread_ts"] = thread_ts
    resp = client.chat_postMessage(**kwargs)
    return {
        "ok": resp.get("ok", False),
        "channel": resp.get("channel", ""),
        "ts": resp.get("ts", ""),
    }
