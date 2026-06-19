#!/usr/bin/env python3
"""
JARVIS Email Summary — Prints a 30-minute digest to stdout.
Output is picked up by OpenClaw cron agentTurn for channel delivery.
"""

import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from collections import Counter

QUEUE_FILE = Path("/home/ubuntu/.openclaw/workspace/email-queue.json")


def load_queue():
    if QUEUE_FILE.exists():
        return json.loads(QUEUE_FILE.read_text())
    return []


def generate_summary():
    queue = load_queue()
    now = datetime.now(timezone.utc)
    thirty_min_ago = now - timedelta(minutes=30)

    recent = [e for e in queue if e["timestamp"] >= thirty_min_ago.isoformat()]
    total = len(queue)
    recent_count = len(recent)

    if recent_count == 0:
        print("📊 **JARVIS Email Summary**")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━")
        sgt = now + timedelta(hours=8)
        print(f"🕐 {sgt.strftime('%H:%M SGT')}")
        print(f"🟢 **No new emails** in the last 30 minutes.")
        print(f"📚 Total tracked: {total} emails")
        print()
        print(f"📊 [Dashboard](https://mail.group14.ydsp.tnkr.be/)")
        return

    # Categories in recent
    cat_counts = Counter(e.get("category", "unknown") for e in recent)
    prio_counts = Counter(e.get("priority", "?") for e in recent)
    high_risk = sum(1 for e in recent if e.get("url_count", 0) > 0)

    print("📊 **JARVIS Email Summary**")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━")
    sgt = now + timedelta(hours=8)
    print(f"🕐 {sgt.strftime('%H:%M SGT')}")
    print(f"📨 **{recent_count} email(s)** received in last 30 min")
    print(f"├─ By category: {', '.join(f'{k}: {v}' for k, v in cat_counts.most_common())}")
    print(f"├─ High priority: {prio_counts.get('high', 0)} | Low: {prio_counts.get('low', 0)}")
    print(f"└─ 🔗 Suspicious links: {high_risk}")
    print(f"📚 Total tracked: {total}")
    print()

    # List recent emails
    print(f"**Recent emails:**")
    for e in reversed(recent[-8:]):
        subject = e.get("subject", "(no subject)")[:70]
        sender = e.get("sender", "unknown")[:30]
        cat = e.get("category", "?")
        prio = e.get("priority", "?")
        ts_dt = datetime.fromisoformat(e.get("timestamp", ""))
        if ts_dt.tzinfo is None:
            ts_dt = ts_dt.replace(tzinfo=timezone.utc)
        ts_sgt = ts_dt + timedelta(hours=8)
        ts = ts_sgt.strftime("%H:%M")
        badge = "🚨" if cat == "critical" else "⚠️" if cat in ("mild", "scam") else "📧"
        print(f"{badge} `{ts}` **{subject}**")
        print(f"   ┗ From: {sender} | {cat} | priority: {prio}")

    print()
    print(f"📊 [Dashboard](https://mail.group14.ydsp.tnkr.be/) | [Webhook](https://email-webhook.group14.ydsp.tnkr.be/)")


if __name__ == "__main__":
    generate_summary()
