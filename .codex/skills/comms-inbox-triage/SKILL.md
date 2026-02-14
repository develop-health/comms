---
name: comms-inbox-triage
description: Run a daily inbox triage workflow in Codex using Comms MCP tools (search_emails, read_thread, draft_email, send_draft, archive_email).
---

# Comms Inbox Triage

Use this workflow when the user wants to triage today's inbox and drive toward inbox zero.

## Workflow

1. Pull inbox:
   - Call `search_emails` with `query: is:inbox` and `max_results: 500`.

2. Deduplicate by thread:
   - Group messages by `threadId`.
   - Keep the latest message in each thread.
   - Triage one row per thread.

3. Categorize threads:
   - Show sender, subject, snippet, and timestamp.
   - Buckets: `Urgent`, `Important`, `Can wait`, `Skip`.
   - Ask user to confirm or adjust before continuing.

4. Process `Urgent` then `Important`:
   - Call `read_thread` for context.
   - Ask if user wants a reply draft.
   - If yes, call `draft_email` with `reply_to_message_id` set to the latest message id.
   - If approved, call `send_draft`, then `archive_email` for the handled message.
   - If edits requested, revise and re-draft.

5. Process `Skip`:
   - Offer batch archive.
   - Call `archive_email` for each confirmed message.

6. Summarize:
   - Count handled threads, sent drafts, archived items.
   - List `Can wait` subjects for later.

## Notes

- Inbox API results may include read threads still labeled `INBOX`; triage all returned threads.
- Keep responses concise and action-oriented.
