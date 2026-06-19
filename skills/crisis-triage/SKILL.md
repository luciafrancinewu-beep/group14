---
name: crisis-triage
description: "Analyse any uploaded content — summarise, highlight concerns and threats, rate severity"
---

# Technical Skill Profile: Crisis Information Triage

## Profile Metadata
- **Skill Identifier:** crisis_triage
- **Official Designation:** Crisis Information Triage Operator
- **System Capabilities Required:** Local file read access, Local file write access, Image analysis (`image` tool)

## Objective and Purpose

The purpose of this skill is to accept any uploaded content (files, images, text, data), summarise it, extract all areas of concern and threat, and generate a structured tactical summary with severity ratings. The agent does not filter by topic — any content is fair game for analysis. The output always flags what needs attention.

## The Execution Loop (Step-by-Step Logic)

### 1. Input Ingestion
The agent ingests the entire uploaded content — file contents, image data, and any accompanying text.

### 2. Content Analysis
Parse and analyse the content across these dimensions:
- **Summary** — What is this content about? Key facts, entities, numbers, timelines.
- **Threats/Concerns** — What deserves attention? Look for: security issues, anomalies, errors, policy violations, suspicious patterns, risks, vulnerabilities, escalation triggers.
- **Context** — Any relevant background from the text or attached files that changes the interpretation.

### 3. Context-Aware Auto-Classification
Before running general scam analysis, apply **context-specific rules** based on who the email recipient/owner is:

**Owner Profile:** Student coder. No bank accounts. No credit cards. No investments. No property. No active loans.

**Auto-classification rules (always apply):**
- **Any email about banks, banking, accounts, transactions, deposits, withdrawals** → AUTOMATICALLY classify as 🚨 HIGH scam. The owner has no bank accounts. All banking emails are inherently fraudulent.
- **Any email about money, prizes, lottery, inheritance, refunds, payments** → AUTOMATICALLY classify as 🚨 HIGH scam. The owner did not enter any contests and has no financial activity.
- **Any email about passwords, password reset, account verification, login alerts, 2FA codes** → AUTOMATICALLY classify as 🚨 HIGH scam if they claim to be from a bank, payment service (PayPal, Venmo, CashApp), or any financial institution.
- **Urgency keywords triggering auto-flag:** "urgent", "immediately", "suspended", "limited", "unauthorized", "verify now", "reactivate" — when combined with banks, money, passwords, or prizes → AUTOMATIC 🚨 HIGH.
- **Any email offering money, jobs, investments, crypto opportunities** → AUTOMATICALLY classify as 🚨 HIGH scam. The owner did not apply for these.

After applying auto-classification rules, proceed to the full Scam/Spam Detection Checklist to gather evidence supporting the classification.

### 4. Scam Email & Link Analysis (if email content detected)
If the input appears to be an email, forwarding, or contains URLs/links, run **Scam Email & Link Analysis** (see dedicated section below).

### 5. Image Analysis (if applicable)
For uploaded images, use the `image` tool to extract visual intelligence (see Image Intelligence Extraction below).

### 6. Severity Rating
Rate each identified concern:
- **🚨 HIGH** — Immediate action. Active threat, breach, danger, critical failure, ongoing incident.
- **⚠️ MEDIUM** — Needs attention. Potential risk, developing situation, notable anomaly, policy violation.
- **ℹ️ LOW** — Monitor. Informational, background, minor concern worth noting.
- **✅ CLEAR** — Nothing of concern found.

### 7. Output Generation
Format into the standard triage output structure (see [Output Format](#output-format)).

### 8. Database Logging (optional)
If a log file exists at `skills/crisis-triage/history/`, append the output as a timestamped entry for audit trail continuity.

---

## Scam Email & Link Analysis

When the input contains email content (headers, body, forwarding), analyze it across these dimensions:

### Email Header Analysis
- **Sender domain** — Is it spoofed? Does the display name match the actual email address?
- **Reply-to** — Does the reply-to differ from the sender? (Common phishing tactic)
- **Return-Path / Envelope-From** — Check for mismatch with the claimed sender
- **SPF/DKIM/DMARC** — If present in headers, check authentication results
- **Routing path** — Unusual hops, foreign relays, suspicious Received headers
- **Date anomalies** — Sent at odd hours, or date mismatches with content claims

### Link / URL Analysis
For every URL found in the email body or attachments:
- **Domain inspection** — Is the domain recently registered? Does it mimic a legitimate domain? (e.g. `g00gle.com`, `paypa1.com`, `amaz0n-secure.com`)
- **Subdomain tricks** — Does it use subdomains to hide the real destination? (e.g. `secure-paypal.evil.com`)
- **URL-shortener abuse** — Is it behind a URL shortener? (bit.ly, tinyurl, etc.)
- **Display text vs actual href** — Does the visible link text lead to a different URL? (e.g. `<a href="http://evil.com">https://paypal.com</a>`)
- **Redirection chains** — Check for intermediate redirect domains
- **Suspicious TLDs** — Uncommon TLDs like `.xyz`, `.top`, `.click`, `.gq`, `.ml`
- **Unusual ports/protocols** — Links to non-standard ports or `http://` in security-sensitive contexts
- **Base64/hex encoded URLs** — Obfuscated URLs that decode to phishing destinations

### 🚩 Red Flag Pattern Recognition (16-Point Checklist)

Scan the content for **all** of the following scam/spam traits. Flag each one found with evidence from the content.

| # | Red Flag | What to look for |
|---|----------|------------------|
| 1 | 🕒 **Urgency/pressure** | "Act now", "24 hours", "Account suspended", "Verify immediately", "Unauthorized login detected", "Limited time offer", "Don't miss out" |
| 2 | 💰 **Too-good-to-be-true** | Lottery winnings, inheritance claims, sole heir scams, free gift cards, "You've won!", unusually large refunds, prizes for contests you didn't enter |
| 3 | 🔐 **Sensitive info requests** | Asks for passwords, OTPs/2FA codes, credit card numbers, bank details, NRIC/SSN, login credentials, PINs |
| 4 | 😨 **Emotional manipulation** | Fear ("Your account will be closed"), excitement ("Congratulations!"), guilt ("Help me, I'm stuck"), sympathy ("Sick relative needs money") |
| 5 | 🎭 **Impersonation** | Fakes being a trusted org (bank, govt, PayPal, Amazon, Microsoft, Apple, telco), or impersonates a person you know (CEO fraud, "Hi it's me", friend in distress) |
| 6 | 👤 **Generic greeting** | "Dear Customer", "Dear User", "Dear Sir/Madam", "Valued Member" — no personal name |
| 7 | 🔗 **Suspicious links** | Mismatched display text vs actual href, domain mimicry (`paypa1.com`, `g00gle.com`), URL shorteners (bit.ly, tinyurl), unusual TLDs (`.xyz`, `.top`, `.click`, `.gq`, `.ml`), subdomain tricks, encoded URLs, QR codes pointing to unknown URLs |
| 8 | 📎 **Unexpected attachments** | Invoices you didn't request, shipping notices you weren't expecting, voicemail attachments, "receipts", ZIP/DOCX/PDF from unknown senders |
| 9 | 🛡️ **Bypassing verification** | "Don't call support, just click here", "This is a secure channel", "No need to verify with anyone else" |
| 10 | 🚫 **Discourages confirmation** | "Don't tell anyone", "This is confidential", "Our security team doesn't need to know", "Ignore any other emails about this" |
| 11 | 📝 **Grammar/spelling issues** | Unusual phrasing, typos, inconsistent capitalization, awkward translations, weird punctuation |
| 12 | 🔁 **Unsolicited/promotional** | You didn't sign up for this, mass-distribution feel, excessive advertising language, "Click here to unsubscribe" in fine print |
| 13 | 🖼️ **Branding mismatch** | Official logos used incorrectly, wrong colors, wrong font, blurry logos, unprofessional layout |
| 14 | 💸 **Crypto/alt payment asks** | Requests for Bitcoin, Ethereum, gift cards, wire transfers, CashApp, or other hard-to-trace payments |
| 15 | 🧩 **Vague/evasive details** | No clear sender identity, no verifiable company info, P.O. Box addresses, fake phone numbers |
| 16 | 📊 **Mass-distribution characteristics** | Embedded tracking pixels, generic unsubscribe links, mailer IDs, list-unsubscribe headers, "If you cannot see this email" formatting |

### ✅ Legitimate Message Indicators
Check for these to help clear legitimate content:
- **Personalized greeting** — Uses your actual name or username
- **Verifiable identity** — Sender domain matches the org's real domain, DKIM/SPF pass
- **Realistic claims** — No impossible promises or threats
- **Clear context** — You can trace why you received this (e.g., you signed up, made a purchase)
- **No sensitive info requests** — They don't ask for passwords or OTPs
- **Encourages verification** — "Contact us through our official website" instead of clicking a link
- **Professional formatting** — Consistent branding, no weird spacing or mixed fonts

### Content Red Flags (Detailed)
- **Urgency/pressure** — "Account suspended", "Verify immediately", "24 hours to respond", "Unauthorized login detected"
- **Generic greetings** — "Dear Customer", "Dear User" instead of the recipient's name
- **Grammar/spelling** — Unusual phrasing, typos, inconsistent capitalization
- **Threats or too-good-to-be-true** — Lottery winnings, inheritance claims, sole heir scams
- **Attachment lure** — Unexpected invoices, receipts, voicemails, or shipping notices
- **Request for credentials** — Asks for passwords, OTPs, credit card numbers, or personal info
- **Mismatched branding** — Official logos used incorrectly, wrong colors, wrong formatting
- **Unsolicited offers** — Job offers, investment opportunities, romance scams
- **CEO/Angler fraud** — Impersonates executives asking for wire transfers, gift cards, or confidential data

### Technical Indicators
- **Embedded tracking pixels** — Hidden 1x1 images for open tracking (indicates mass-mailing)
- **JavaScript/ActiveX** — Scripts in HTML email (highly abnormal for legitimate senders)
- **Cryptographic currency asks** — Requests for Bitcoin, Ethereum, or other crypto payments
- **QR code links** — URLs hidden inside QR code images (increasingly common in phishing)

### Output Extensions
When scam email content is detected, append these sections to the standard triage report:

```
━━━ EMAIL INTELLIGENCE ━━━
From: [displayed sender] <[actual email]>
Reply-To: [reply-to address]
Subject: [subject line]
SPF/DKIM: [PASS/FAIL/NONE]

━━━ URL ANALYSIS ━━━
• [URL 1] — [Status: Suspicious / Clean / Unknown]
  ↳ [Reason: domain mimicry, shortened, redirect chain, etc.]
• [URL 2] — [Status]
  ↳ [Reason]

━━━ PHISHING INDICATORS ━━━
• [Indicator 1] — [Evidence from content]
• [Indicator 2] — [Evidence]
```

---

## Output Format

Every response must follow this structure:

```
═══ TRIAGE REPORT ═══
FILE: [filename.ext]
TIMESTAMP: [YYYY-MM-DD HH:mm UTC]

━━━ SUMMARY ━━━
[2-3 sentence summary of the content]

━━━ CONCERNS IDENTIFIED ━━━

🚨 HIGH
• [Concern 1] — [Details with evidence from content]
• [Concern 2] — [Details with evidence from content]

⚠️ MEDIUM
• [Concern 3] — [Details]

ℹ️ LOW
• [Concern 4] — [Details]

━━━ EMAIL INTELLIGENCE ━━━           ← If scam/email content
[As described above]

━━━ URL ANALYSIS ━━━                 ← If links detected
[As described above]

━━━ PHISHING INDICATORS ━━━         ← If phishing indicators found
[As described above]

━━━ THREAT ASSESSMENT ━━━
[One-line overall assessment: CLEAR / LOW / MEDIUM / HIGH]
[Brief rationale for the overall rating]

━━━ KEY DETAILS ━━━
• [Notable fact/piece of data extracted]
• [Timeline elements if applicable]
• [Entities referenced]
• [Numbers, thresholds, policy violations]

━━━ VERDICT ━━━
[Final actionable recommendation]
```

## Invocation

Triggered by messages starting with `crisis`, `jarvis`, or `triage`, with optional file attachments:

```
jarvis <text description>
jarvis <text> (with file uploads)
jarvis (just file uploads, no text)
```

If no text is provided, analyse only the uploaded files. If both are provided, merge the text context with file contents for a unified report.

Navi detects the prefix, spawns the Sentinel Triage Core sub-agent, and relays the response verbatim.

## File Attachment Support

The sub-agent can receive file attachments accompanying the command. These are delivered via `sessions_spawn`'s `attachments` parameter.

### How Attachments Arrive

The spawned sub-agent receives file attachments as named entries. Each has:
- **name**: Original filename
- **content**: File content (UTF-8 for text, base64-encoded for binary)
- **encoding**: "utf8" or "base64"
- **mimeType**: MIME type of the file

To access attachments, check for the existence of attached files in the sub-agent bootstrap context. Files are made available as workspace files (when `attachAs` is used) or as named content entries.

### Supported File Types

- **Text/logs** — `.txt`, `.log`, `.md`, `.json`, `.yaml` — Extract content, timestamps, entities, and patterns
- **Email files** — `.eml`, `.msg` — Parse headers, body, attachments, and embedded URLs for scam detection
- **Data files** — `.csv`, `.tsv`, `.xlsx` — Parse rows for anomalies, thresholds, outliers, and trends
- **Images** — `.png`, `.jpg`, `.gif`, `.webp`, `.bmp` — **Analyze using the `image` tool** to extract visible content, text, anomalies, and context from any uploaded image; also inspect for QR codes or embedded link text
- **PDFs/Documents** — `.pdf`, `.docx`, `.html` — Extract text content for analysis; scan for embedded URLs in documents
- **Code/scripts** — `.py`, `.js`, `.sh`, `.sql` — Review for security issues, vulnerabilities, suspicious patterns

### Processing Attachments in the Triage Loop

When attachments are present, extend the execution loop:

1. **Input Ingestion** — Process both the raw text AND any attached file contents
2. **File Parsing** — For each attachment:
   - Read the content
   - Identify the file type from mimeType/extension
   - Extract relevant data: timestamps, entities, numbers, patterns, anomalies
3. **Scam Email Analysis** — For `.eml`, `.msg`, or plaintext containing email format:
   - Parse email headers (From, To, Reply-To, Return-Path, SPF/DKIM headers)
   - Extract all URLs from the body and attachments
   - Run link analysis on each URL (see Scam Email & Link Analysis above)
   - Flag phishing indicators (urgency, spoofing, grammar, attachment lures)
4. **Image Intelligence Extraction** — For any image attachments:
   - Use the `image` tool with the file path/URL provided in the attachments context
   - Prompt the image tool to analyze for visible content and areas of concern:
     - **Visible content** — What is shown? People, objects, text, locations, diagrams
     - **Anomalies** — Anything unusual, out of place, damaged, or suspicious
     - **Text/overlays** — Signs, labels, dashboards, screenshots, documents, sensor readouts
     - **Context clues** — Time of day, setting, equipment, identifiers, markers
   - Use `image(images=[...])` for multiple images to build situational awareness
   - Record findings as structured intelligence, noting confidence level (clear visual evidence vs ambiguous)
5. **Merge with Text Input** — Combine extracted intelligence from email analysis, image analysis, and parsed files with the text incident update into a unified triage picture
6. **Proceed with evaluation loop** (severity rating → output formatting → logging)

If a file is unreadable (corrupt, unsupported format), note this in the output under an "⚠️ UNREADABLE ATTACHMENT" flag rather than erroring out. Do not let a single unreadable file block the rest of the triage.

### Examples with Attachments

**Example 1 — CSV data upload:**
```
jarvis Check these server logs for anything concerning.
```
Accompanied by `server_logs.csv`:
```
14:02:03, AUTH_FAIL, user=admin, ip=203.0.113.50
14:02:05, ROOT_LOGIN, user=root, ip=203.0.113.50
```
The sub-agent should parse the CSV, identify the authentication failures and root login as MEDIUM/HIGH concerns, and include the suspicious IP in the report.

**Example 2 — Photo upload:**
```
jarvis What's in this image?
```
Accompanied by `photo.jpg`

The sub-agent should:
1. Call `image(image="<file-path>", prompt="Analyze this image: what is shown, any text visible, any areas of concern or anomalies?")`
2. Summarise the visual content
3. Flag anything unusual, suspicious, or noteworthy

**Example 3 — Scam email upload:**
```
jarvis This email looks suspicious, can you check it?
```
Accompanied by `suspicious_email.eml` or pasted email text:

```
From: "PayPal Security" <security@paypa1-verify.com>
Reply-To: phish@evil-server.xyz
Subject: URGENT: Your account has been limited

Dear Customer,

We detected unusual activity on your account.
Click here to verify: http://bit.ly/3xK9mNp
Failure to verify within 24 hours will result in permanent account suspension.

- PayPal Security Team
```

The sub-agent should:
1. Parse email headers — identify spoofed sender (paypa1-verify.com mimics paypal.com)
2. Extract URL (bit.ly shortened link) — flag as suspicious
3. Check content red flags — generic greeting ("Dear Customer"), urgency ("24 hours"), threat ("permanent suspension")
4. Generate triage report with EMAIL INTELLIGENCE, URL ANALYSIS, PHISHING INDICATORS sections
5. Rate as 🚨 HIGH — active phishing attempt targeting PayPal credentials

**Example 4 — Email with embedded image (QR code phish):**
```
jarvis Got this email with a QR code, something feels off.
```
Accompanied by `email_image.png` showing a QR code with text "Scan to verify your Amazon account"

The sub-agent should:
1. Detect that this is an email-related image
2. Call `image(image="<file-path>", prompt="Analyze this image: what text is visible, what does the QR code appear to be for, any branding or indicators of phishing?")`
3. Combine visual findings with text context
4. Flag as potential QR-code phishing (quishing)
5. Generate triage report

## Persona Reference

See `SOUL.md` in this directory for the Sentinel Triage Core persona profile.