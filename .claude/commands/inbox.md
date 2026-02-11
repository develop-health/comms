---
description: Triage today's inbox emails
allowed-tools: [Task, Read, Glob, Grep]
---

# Inbox Triage

You are guiding the user through their daily inbox triage. Follow these steps in order.

## Step 1 — Pull inbox

Call `search_emails` with query `is:inbox` and `max_results: 500`.

## Step 2 — Deduplicate by thread

The API returns individual messages, but Gmail shows threads. Group messages by `threadId` and keep only the **latest message** per thread. This is the list you triage — one entry per thread.

Note: Gmail's inbox counter (e.g. "Inbox 9") only counts **unread** threads. The API returns **all** threads with the INBOX label, including read ones shown in Gmail's "Everything else" section. Triage ALL of them — the goal is inbox zero.

## Step 3 — Triage threads

Present each thread as a **one-line summary**: sender, subject, snippet, time of latest message.

Categorize every thread into one of four buckets:
- **Urgent** — needs a response today, time-sensitive, from key contacts
- **Important** — needs a response, but not immediately time-critical
- **Can wait** — informational, low priority, can be handled later
- **Skip** — newsletters, notifications, automated emails, no action needed

Show the triage as a grouped list and ask the user to confirm or adjust the categorization before proceeding.

## Step 3 — Work through Urgent + Important emails

Process each email starting with **Urgent**, then **Important**:

1. Read the full thread using `read_thread` with the email's threadId
2. Present a context summary: thread history and what seems to be needed
3. Ask the user: **"Want me to draft a reply?"**
   - If yes: draft the reply using `draft_email` with `reply_to_message_id` set to the latest message ID in the thread. Show the draft to the user.
   - User approves → call `send_draft` with the draftId, then `archive_email` the original message
   - User wants edits → revise and re-draft
   - User skips → move to next email

## Step 4 — Handle Skip emails

After working through Urgent + Important, offer to batch-archive all **Skip** emails. Use `archive_email` for each one the user confirms.

## Step 5 — Summary

Recap the session:
- Number of emails handled
- Number of drafts sent
- Number of emails archived
- List any **Can wait** emails with their subjects for later reference
