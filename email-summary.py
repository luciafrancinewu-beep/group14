#!/usr/bin/env python3
"""
JARVIS Email Summary — Posts a 30-minute digest to Discord.
Designed to be run via cron every 30 minutes.

Flow:
  1. Read email queue from last 30 min
  2. Count emails, group by sender/status
  3. Post summary to Discord with links to analysis pages
"""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ─── CONFIG ─────────────────────────────────────────────────────────────────
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1516338500239364126/CLQOWiim9L3ZxhtSMRjCFs_f98MNNN_hu6jvCEQnR2D34SnOkz9m9yj2Ya0I67pp7635"
QUEUE_FILE = Path("/home/ubuntu/.openclaw/workspace/email-queue.json")
BASE_ANALYSIS_URL = "http://group14.ydsp.tnkr.be:8099/analysis"
BASE_QUEUE_URL = "http://group14.ydsp.tnkr.be:8099"
# ────────────────────────────────────────────────────────────────────────────


def load_queue():
    if QUEUE_FILE.exists():
        return json.loads(QUEUE_FILE.read_text())
    return []


def post_summary():
    queue = load_queue()
    now = datetime.now(timezone.utc)
    thirty_min_ago = now - timedelta(minutes=30)

    # Filter emails from last 30 min
    recent = [e for e in queue if e["timestamp"] >= thirty_min_ago.isoformat()]

    total = len(queue)
    recent_count = len(recent)
    pending = sum(1 for e in queue if e["jarvis_status"] == "pending")
    high_risk = sum(1 for e in recent if e.get("url_count", 0) > 0)

    # Build summary message
    if recent_count == 0:
        content = (
            f"📊 **JARVIS Email Summary** — {now.strftime('%H:%M UTC')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🟢 **No new emails** in the last 30 minutes.\n"
            f"📚 **Total tracked:** {total} emails"
        )
    else:
        # List recent emails with analysis links
        email_lines = []
        for e in reversed(recent[-5:]):  # max 5 in summary
            subject = e.get("subject", "(no subject)")[:60]
            sender = e.get("sender", "unknown")[:30]
            url_count = e.get("url_count", 0)
            analysis_link = f"{BASE_ANALYSIS_URL}/{e['id']}"
            link_indicator = "🔗" if url_count > 0 else "📧"
            email_lines.append(
                f"{link_indicator} **{subject}**\n"
                f"   ┗ From: {sender} · "
                f"[View Analysis]({analysis_link})"
            )

        content = (
            f"📊 **JARVIS Email Summary** — {now.strftime('%H:%M UTC')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📨 **{recent_count} email(s)** received in last 30 min\n"
            f"🔗 **{high_risk}** contain suspicious links\n"
            f"⏳ **{pending}** pending JARVIS analysis\n"
            f"📚 **{total}** total tracked\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{chr(10).join(email_lines)}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 [Full Queue Status]({BASE_QUEUE_URL})"
        )

    payload = json.dumps({"content": content}).encode()
    req = urllib.request.Request(
        DISCORD_WEBHOOK,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        urllib.request.urlopen(req)
        print(f"[{now.isoformat()}] Summary posted: {recent_count} recent emails")
    except urllib.error.HTTPError as e:
        print(f"Discord error: {e.code} {e.read().decode()[:200]}")


if __name__ == "__main__":
    post_summary()
