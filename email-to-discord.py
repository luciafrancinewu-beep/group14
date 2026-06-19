#!/usr/bin/env python3
"""
Email-to-Discord bridge: reads stdin (pipded email), posts to Discord webhook.
Usage: pipe email to this script, or use as a forwarder.
"""
import sys, json, urllib.request, email, email.policy

WEBHOOK_URL = "https://discord.com/api/webhooks/1516338500239364126/CLQOWiim9L3ZxhtSMRjCFs_f98MNNN_hu6jvCEQnR2D34SnOkz9m9yj2Ya0I67pp7635"

def parse_email(raw: str) -> dict:
    msg = email.message_from_string(raw, policy=email.policy.default)
    subject = msg["Subject"] or "(no subject)"
    sender = f"{msg['From']}" if msg["From"] else "unknown"
    body = ""

    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            if ctype == "text/plain":
                body = part.get_content()
                break
    else:
        body = msg.get_content() or ""

    return {"subject": subject, "sender": sender, "body": body.strip()}

def post_to_discord(data: dict):
    payload = {
        "content": (
            f"📧 **New Email Forwarded to JARVIS**\n"
            f"**From:** {data['sender']}\n"
            f"**Subject:** {data['subject']}\n"
            f"```{data['body'][:1800]}```\n"
            f"---\n"
            f"`jarvis analyze this email for scams`"
        )
    }
    req = urllib.request.Request(
        WEBHOOK_URL,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    urllib.request.urlopen(req)

if __name__ == "__main__":
    raw = sys.stdin.read()
    if raw.strip():
        parsed = parse_email(raw)
        post_to_discord(parsed)
        print(f"Forwarded: {parsed['subject']} from {parsed['sender']}")
    else:
        print("No email received on stdin.")
