"""Notion API client — search pages, read page content."""

import requests

from ..config import NotionConfig


def _get_config() -> NotionConfig:
    config = NotionConfig()
    if not config.api_token:
        raise ValueError("Missing NOTION_API_TOKEN environment variable")
    return config


def _headers(config: NotionConfig) -> dict:
    return {
        "Authorization": f"Bearer {config.api_token}",
        "Content-Type": "application/json",
        "Notion-Version": config.api_version,
    }


def _get_title(page: dict) -> str:
    """Extract page title from properties."""
    props = page.get("properties", {})
    for prop in props.values():
        if prop.get("type") == "title":
            title_parts = prop.get("title", [])
            return "".join(t.get("plain_text", "") for t in title_parts)
    return ""


def search_pages(query: str, max_results: int = 20) -> list[dict]:
    """Search Notion pages and databases by query text."""
    config = _get_config()
    payload = {
        "query": query,
        "page_size": min(max_results, 100),
        "sort": {
            "direction": "descending",
            "timestamp": "last_edited_time",
        },
    }
    resp = requests.post(
        f"{config.base_url}/search",
        headers=_headers(config),
        json=payload,
    )
    resp.raise_for_status()
    results = resp.json().get("results", [])
    pages = []
    for item in results:
        pages.append({
            "id": item.get("id", ""),
            "type": item.get("object", ""),
            "title": _get_title(item),
            "url": item.get("url", ""),
            "last_edited": item.get("last_edited_time", ""),
        })
    return pages


def _extract_block_text(block: dict) -> str:
    """Extract plain text from a single Notion block."""
    block_type = block.get("type", "")
    type_data = block.get(block_type, {})
    rich_text = type_data.get("rich_text", [])
    text = "".join(t.get("plain_text", "") for t in rich_text)

    if block_type in ("heading_1", "heading_2", "heading_3"):
        return f"\n{text}\n"
    elif block_type == "bulleted_list_item":
        return f"  - {text}"
    elif block_type == "numbered_list_item":
        return f"  1. {text}"
    elif block_type == "to_do":
        checked = type_data.get("checked", False)
        marker = "[x]" if checked else "[ ]"
        return f"  {marker} {text}"
    elif block_type == "code":
        return f"```\n{text}\n```"
    elif block_type == "divider":
        return "---"
    elif text:
        return text
    return ""


def read_page(page_id: str) -> dict:
    """Read full content of a Notion page. Returns blocks as plain text."""
    config = _get_config()

    # Get page metadata
    page_resp = requests.get(
        f"{config.base_url}/pages/{page_id}",
        headers=_headers(config),
    )
    page_resp.raise_for_status()
    page = page_resp.json()

    # Get page blocks (content)
    blocks_text = []
    cursor = None
    while True:
        params = {"page_size": 100}
        if cursor:
            params["start_cursor"] = cursor
        blocks_resp = requests.get(
            f"{config.base_url}/blocks/{page_id}/children",
            headers=_headers(config),
            params=params,
        )
        blocks_resp.raise_for_status()
        data = blocks_resp.json()

        for block in data.get("results", []):
            line = _extract_block_text(block)
            if line:
                blocks_text.append(line)

        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")

    return {
        "id": page.get("id", ""),
        "title": _get_title(page),
        "url": page.get("url", ""),
        "last_edited": page.get("last_edited_time", ""),
        "content": "\n".join(blocks_text),
    }
