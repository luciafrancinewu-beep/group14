"""
Email Categorizer — Industry-standard heuristic classification for JARVIS.
Categories: pending, low_concern, mild, critical, spam, scam

Uses weighted multi-dimensional scoring across:
  - Phishing indicators (header/content/URL)
  - Scam/fraud indicators (financial lures, social engineering)
  - Spam indicators (bulk marketing, unsolicited commercial)
  - Urgency indicators (social engineering pressure)
  - URL heuristics (shorteners, brand mimicry, suspicious TLDs)
  - Sender analysis (mismatched display names, suspicious patterns)
"""

import re

CATEGORIES = [
    ("pending", "⏳", "Pending", "rgba(245,158,11,0.15)", "#f59e0b"),
    ("low_concern", "🟢", "Not So Much Concern", "rgba(16,185,129,0.15)", "#10b981"),
    ("mild", "🟡", "Mild", "rgba(234,179,8,0.15)", "#eab308"),
    ("critical", "🔴", "Critical", "rgba(239,68,68,0.15)", "#ef4444"),
    ("spam", "📣", "Spam", "rgba(139,92,246,0.15)", "#8b5cf6"),
    ("scam", "💰", "Scam", "rgba(249,115,22,0.15)", "#f97316"),
]

# ─── BRAND DOMAINS (legitimate) ────────────────────────────────────────────
BRAND_DOMAINS = {
    "paypal": "paypal.com", "amazon": "amazon.com", "google": "google.com",
    "apple": "apple.com", "microsoft": "microsoft.com", "netflix": "netflix.com",
    "facebook": "facebook.com", "instagram": "instagram.com", "twitter": "twitter.com",
    "linkedin": "linkedin.com", "dropbox": "dropbox.com", "dhl": "dhl.com",
    "fedex": "fedex.com", "ups": "ups.com", "hsbc": "hsbc.com",
    "ocbc": "ocbc.com", "dbs": "dbs.com", "uob": "uob.com.sg",
    "posb": "posb.com.sg", "maybank": "maybank.com",
    "singtel": "singtel.com", "starhub": "starhub.com", "m1": "m1.com.sg",
    "grab": "grab.com", "shopee": "shopee.sg", "lazada": "lazada.sg",
    "carousell": "carousell.com", "gov.sg": "gov.sg",
    "singpass": "singpass.gov.sg", "cpf": "cpf.gov.sg",
    "iras": "iras.gov.sg", "mom": "mom.gov.sg", "ica": "ica.gov.sg",
}

# ─── PHISHING — Weight 3 each ──────────────────────────────────────────────
PHISHING_PATTERNS = [
    # Account security
    "verify your account", "verify your identity", "confirm your account",
    "confirm your identity", "verify account", "verify identity",
    # Suspicious activity
    "unusual activity", "suspicious activity", "unusual sign-in",
    "unusual login", "suspicious login", "unauthorized access",
    "unauthorized login", "login attempt", "new login",
    # Account warnings
    "account suspended", "account limited", "account blocked",
    "account locked", "account restricted", "account on hold",
    "account compromised", "account closure", "account termination",
    "delete your account", "closing your account", "account deleted",
    "account closing", "account will be deleted",
    "closing and deleting", "closing & deleting",
    # Security actions
    "security alert", "security notice", "security breach",
    "data breach", "security measure", "security check",
    # Reset/update
    "reset password", "change password", "update password",
    "update your information", "update payment", "update billing",
    "billing information", "payment information", "credit card on file",
    # Urgent action
    "secure your account", "protect your account", "restore access",
    "reactivate account", "recover account",
    # Common phishing subjects
    "action required", "attention required", "important notice",
    "important information", "account notice",
    # Singapore-specific
    "digibank", "internet banking", "ibanking",
    "bank alert", "unauthorised transaction",
    "pending transaction", "failed transaction",
    "dbs alert", "posb alert", "ocbc alert",
    "verify your transaction", "confirm transaction",
    # FTC guide patterns
    "problem with your account", "account on hold",
    "billing problem", "billing issue", "payment issue",
    "confirm your information", "confirm your details",
    "update your payment", "payment details",
    "unrecognized invoice", "fake invoice", "invoice attached",
    "government refund", "tax refund", "stimulus",
    "free coupon", "free gift card", "exclusive coupon",
    "click to pay", "make a payment",
    "your account has been compromised",
    "unusual sign in attempt", "unauthorised sign in",
    "claim a reward", "avoid a penalty",
    "call immediately", "call us now", "contact support immediately",
    "suspicious sign in", "new device signed in",
    "your password is expiring", "password expired",
    "mailbox full", "storage full", "quota exceeded",
    "delivery failed", "message blocked",
    "reactivate your account", "re-activate",
]

# ─── SCAM/FRAUD — Weight 2 each ────────────────────────────────────────────
SCAM_PATTERNS = [
    # Lottery / Prize (expanded)
    "lottery", "you won", "you have won", "congratulations",
    "congratulations you won", "congratulations, you have won",
    "cash prize", "grand prize", "prize claim", "claim your prize",
    "winning number", "lucky winner", "selected as winner",
    "lucky draw", "lucky", "draw", "prize",
    # Inheritance / next of kin
    "inheritance", "next of kin", "sole heir", "late relative",
    "unclaimed funds", "unclaimed inheritance",
    # Investment
    "investment opportunity", "guaranteed return", "guaranteed profit",
    "high yield", "double your money", "risk free investment",
    "crypto investment", "bitcoin investment", "forex trading",
    # Money transfer
    "wire transfer", "bank transfer", "western union", "money gram",
    "money order", "gift card", "cryptocurrency", "bitcoin",
    "ethereum", "processing fee", "advance fee", "transfer fee",
    "release fee", "clearance fee",
    # Romance / relationship (expanded)
    "lonely", "single", "looking for love", "dating",
    "military deployed", "oil platform", "doctor overseas",
    "thinking of you", "from across the world", "miss you",
    "looking for", "special someone", "special partner",
    "honest partner", "military base", "deployed",
    "syria", "afghanistan", "iraq", "united nations",
    "peacekeeping", "medical mission", "red cross",
    "doctors without borders", "pen pal", "meeting you",
    "was destiny", "fate brought us", "meant to be",
    "my dear", "my dearest", "my love", "sweetheart",
    "can't stop thinking", "you are the one",
    "wifey", "husband", "soulmate", "true love",
    "shipping cost", "travel expenses", "visa fees",
    "come visit me", "bring you here", "start a life",
    "together forever", "never met anyone like you",
    "you are beautiful", "you are amazing",
    "i need your help", "i need you", "trust you",
    "only you can", "please help me", "help me get",
    # Tech support
    "virus detected", "your computer", "tech support",
    "microsoft support", "apple support", "remote access",
    "screen sharing", "your ip", "your device",
    # Employment
    "work from home", "earn money from home", "make money fast",
    "easy money", "passive income", "data entry job",
    "mystery shopper", "envelope stuffing",
    # Generic scam
    "sole beneficiary", "confidential", "top secret",

    # Singapore-specific scam patterns (from DBS scam guide)
    "too good to be true", "quick money", "easy money fast",
    # Money mule
    "money mule", "use your bank account", "personal bank account",
    "let someone else use your bank", "bank account for their business",
    # Job scams
    "part time job", "simple task", "do this task", "complete this task",
    "data entry clerk", "just do tasks", "earn commission",
    # QR code scams
    "scan qr code", "qr code", "scan the qr",
    # Malware / remote access
    "accessibility permission", "google play protect",
    "disable security", "install app from", "install this app",
    "screen sharing", "remote control",
    # Impersonation types from DBS
    "government agency", "official from", "ministry of",
    "authority", "regulatory", "official notice",
    # Singpass
    "singpass", "sing pass",
    # Fake invoice patterns (FTC/Microsoft)
    "fake invoice", "unrecognized charge", "unauthorized charge",
    "subscription renewal", "auto renewal", "auto-renewal",
    "your subscription", "trial ended", "trial expiring",
    "payment declined", "card declined", "transaction declined",
    "overdue invoice", "past due", "outstanding balance",
    "final demand", "payment reminder",
    # Tech support callback (Microsoft)
    "virus alert", "security warning", "your computer is infected",
    "call support", "call technician", "call microsoft",
    "windows support", "microsoft certified",
    # Government refund/rebate (FTC)
    "government rebate", "stimulus payment", "relief fund",
    "covid relief", "pandemic relief", "economic impact",
    # Business impersonation
    "ceo fraud", "business email compromise",
    "director request", "executive request",
]

# ─── CEO FRAUD / BUSINESS EMAIL COMPROMISE — Weight 4 ─────────────────────
BEC_PATTERNS = [
    "wire transfer", "urgent payment", "pay immediately",
    "ceo request", "director request", "executive request",
    "confidential request", "authorize payment", "approve payment",
    "gift card", "purchase gift cards", "send money",
    "change bank details", "update banking", "new banking information",
    "pay invoice", "outstanding invoice", "overdue payment",
    "i'm in a meeting", "i'm traveling", "need your help",
    "can you do this urgently", "discretion required",
]

# ─── SPAM — Weight 1 each ──────────────────────────────────────────────────
SPAM_PATTERNS = [
    # Commercial
    "buy now", "shop now", "order now", "click here", "act now",
    "limited time", "offer expires", "hurry", "don't miss",
    "exclusive offer", "special offer", "limited offer",
    "free", "free trial", "free shipping", "free download",
    "discount", "save", "deal", "bargain", "clearance",
    "subscribe", "unsubscribe", "newsletter", "weekly digest",
    # Generic
    "you have been selected", "congratulations",
    "earn money", "make money", "work from home",
    "online business", "financial freedom",
    # Weight loss / Health
    "weight loss", "lose weight", "diet pill",
    "natural remedy", "miracle cure", "anti aging",
    # Adult
    "single", "dating", "meet singles", "adult",
    # White noise / system notifications
    "encountered error", "encountered", "scenario",
    "integration webhook", "webhook error",
    "automated notification", "system notification",
    "do not reply", "noreply", "no-reply",
    "account in progress", "deleting your account",
    "hi jarvis",
    # Commercial patterns
    "sale", "sale today", "big sale", "stock photo",
    "pre-approved", "pre approved", "limited spots",
    "act fast", "while stocks last", "members only",
]

# ─── KNOWN NEWS DOMAINS (legitimate senders → auto low_concern) ─────
NEWS_DOMAINS = [
    # Singapore
    "straitstimes.com", "straitstimes",
    "channelnewsasia.com", "cna",
    "todayonline.com", "todayonline",
    "businesstimes.com.sg",
    "zaobao.com.sg",
    "mothership.sg",
    "theindependent.sg",
    "mustsharenews.com",
    "asiaone.com",
    # International
    "bbc.com", "bbc.co.uk", "bbc",
    "cnn.com",
    "reuters.com",
    "apnews.com",
    "nytimes.com",
    "theguardian.com",
    "washingtonpost.com",
    "wsj.com",
    "bloomberg.com",
    "npr.org",
    "theverge.com",
    "techcrunch.com",
    "wired.com",
    "nature.com",
    "nationalgeographic.com",
]


# ─── ACADEMIC KEYWORDS (student → auto low_concern) ─────────────────
ACADEMIC_KEYWORDS = [
    "homework", "assignment", "mathematics", "math",
    "grade", "submission", "deadline", "final notice",
    "academic", "student", "class", "course",
    "exam", "quiz", "test", "project",
    "report card", "transcript", "enrollment",
    "suspension", "assessment",
]

# ─── URGENCY — Weight 3 (in subject) / 2 (in body) ────────────────────────
URGENCY_PATTERNS = [
    "urgent", "critical", "immediate", "immediately",
    "action required", "time sensitive", "time-limited",
    "respond now", "respond immediately", "reply now",
    "expires today", "expires soon", "last chance",
    "final notice", "final warning", "deadline",
    "within 24 hours", "within 48 hours", "today only",
    "account will be", "will be suspended", "will be closed",
    "will be terminated", "will be locked",
    "closing your account", "deleting your account",
    "account closing", "account deletion",
    "failure to", "fail to", "or else", "or your account",
]

# ─── DISPLAY-NAME SPOOFING CHECK ───────────────────────────────────────────
SPOOFED_NAMES = [
    "paypal", "amazon", "google", "apple", "microsoft", "netflix",
    "facebook", "instagram", "twitter", "linkedin", "dropbox",
    "dhl", "fedex", "ups", "hsbc", "ocbc", "dbs", "uob", "posb",
    "maybank", "bank", "support", "security", "admin", "service",
    "account", "alert", "notification", "team", "helpdesk",
    "customer service", "customer support",
]


def extract_domain_from_sender(sender: str) -> str:
    """Extract the email domain from a sender string like 'Name <user@domain.com>'."""
    match = re.search(r'@([^\s>]+)', sender)
    return match.group(1).lower() if match else sender.lower()


def check_sender_spoofing(subject: str, sender: str) -> int:
    """
    Check if the display name claims to be a brand but the email domain
    doesn't match the brand's real domain.
    Returns spoofing score (0-4).
    """
    sender_lower = sender.lower()
    subject_lower = subject.lower()

    # Check for brand names in display name or subject
    for brand, real_domain in BRAND_DOMAINS.items():
        if brand in sender_lower or brand in subject_lower:
            # Extract the actual email domain
            email_domain = extract_domain_from_sender(sender)
            # Check if the domain matches the real domain or is a subdomain of it
            if email_domain == real_domain or email_domain.endswith("." + real_domain):
                return 0  # Legitimate
            # Check for brand but wrong domain = spoofing
            if brand in email_domain or brand.replace(" ", "") in email_domain:
                return 2  # Brand in domain but wrong domain
            return 4  # Brand name but completely different domain = HIGH spoofing

    # Check for generic spoofed names (support, security, etc.)
    for name in ["support", "security", "admin", "helpdesk", "service", "notification", "alert", "team"]:
        if name in sender_lower:
            email_domain = extract_domain_from_sender(sender)
            # If generic name but from a personal email domain
            if any(d in email_domain for d in ["gmail.com", "yahoo.com", "hotmail.com",
                                                 "outlook.com", "live.com", "aol.com",
                                                 "qq.com", "163.com", "mail.ru"]):
                return 3  # "Support" from Gmail = suspicious
    return 0


def analyze_urls(urls: list, text: str) -> dict:
    """
    Analyze URLs for phishing/spam indicators.
    Returns dict with scores and flags.
    """
    result = {
        "suspicious_count": 0,
        "shortened_count": 0,
        "brand_mimicry_count": 0,
        "score": 0,
    }

    if not urls:
        return result

    shorteners = ["bit.ly", "tinyurl", "tiny.cc", "shorturl", "rb.gy",
                   "ow.ly", "is.gd", "buff.ly", "goo.gl", "t.co",
                   "shorte.st", "adf.ly", "bc.vc", "cutt.ly", "short.link"]

    suspicious_tlds = [".xyz", ".top", ".click", ".gq", ".ml", ".tk",
                        ".cf", ".ga", ".loan", ".work", ".review", ".date",
                        ".download", ".men", ".win", ".bid", ".trade"]

    for url in urls:
        url_lower = url.lower()

        # Check URL shorteners
        if any(s in url_lower for s in shorteners):
            result["shortened_count"] += 1
            result["score"] += 3

        # Check suspicious TLDs
        if any(url_lower.endswith(t) for t in suspicious_tlds):
            result["suspicious_count"] += 1
            result["score"] += 2

        # Check for brand names in URL (brand mimicry)
        for brand, real_domain in BRAND_DOMAINS.items():
            if brand in url_lower:
                # Check if it's actually the real domain
                if real_domain not in url_lower and brand + "." not in url_lower:
                    result["brand_mimicry_count"] += 1
                    result["score"] += 3
        
        # Character-substitution mimicry: dbs → d8s, paypal → paypa1, microsoft → rnicrosoft
        domain_match = re.search(r'https?://([^/]+)', url_lower)
        if domain_match:
            raw_domain = domain_match.group(1).replace('www.', '')
            domain_base = raw_domain.split('.')[0] if '.' in raw_domain else raw_domain
            from_char_sub = {'0':'o', '1':'l', '2':'z', '3':'e', '4':'a',
                             '5':'s', '6':'g', '7':'t', '8':'b', '9':'g'}
            for brand, real_domain in BRAND_DOMAINS.items():
                if domain_base == brand:
                    continue
                # Check substitution attacks: micr0soft, paypa1, d8s
                subbed = domain_base
                for wrong_char, right_char in from_char_sub.items():
                    subbed = subbed.replace(wrong_char, right_char)
                if subbed == brand:
                    result["brand_mimicry_count"] += 1
                    result["score"] += 4
                    break
                # Check rn- prefix mimicry: rnicrosoft (m→rn)
                if domain_base.startswith('rn') and domain_base[2:] == brand[1:]:
                    result["brand_mimicry_count"] += 1
                    result["score"] += 4
                    break
                # Check vv- prefix mimicry: vvindows (w→vv)
                if domain_base.startswith('vv') and domain_base[2:] == brand[1:]:
                    result["brand_mimicry_count"] += 1
                    result["score"] += 4
                    break

        # Check for IP address URLs (phishing often uses raw IPs)
        if re.match(r'https?://\d+\.\d+\.\d+\.\d+', url_lower):
            result["suspicious_count"] += 1
            result["score"] += 3

        # Check for suspicious keywords in URL path
        for kw in ["login", "verify", "secure", "update", "confirm",
                    "account", "signin", "auth", "paypal", "banking"]:
            if kw in url_lower:
                result["score"] += 1
                break

        # Check for @ symbol in URL (tricks users about the domain)
        if "@" in url_lower:
            result["score"] += 2

        # Check for extra long or deeply nested paths
        path_parts = url_lower.split("/")
        if len(path_parts) > 5:
            result["score"] += 1

    return result


def generate_one_line(subject: str, sender: str, body: str, urls: list) -> str:
    """Generate a concise one-sentence summary — not just copy-paste."""
    import re as _re

    # Clean the body
    clean = _re.sub(r'<[^>]+>', ' ', body)
    clean = _re.sub(r'\s+', ' ', clean).strip()

    # Split into sentences
    sentences = _re.split(r'(?<=[.!?])\s+', clean)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

    if not sentences:
        sentences = [clean[:150]] if clean else []

    if not sentences:
        return subject[:80] or "(no content)"

    # Action words that indicate the main point
    action_words = [
        "verify", "confirm", "reset", "update", "submit",
        "click", "download", "view", "check", "review",
        "pay", "send", "transfer", "claim",
        "sign", "register", "apply", "join", "schedule",
        "deadline", "due", "expire",
        "urgent", "immediately", "important", "critical",
        "please", "request", "require", "need",
        "your account", "your order", "your invoice",
    ]

    # Score each sentence
    best = sentences[0]
    best_score = -1

    for s in sentences:
        s_lower = s.lower()
        score = sum(2 for w in action_words if w in s_lower)
        # Prefer medium-length sentences
        if 30 < len(s) < 180:
            score += 1
        # Boost first sentence slightly
        if s == sentences[0]:
            score += 1
        if score > best_score:
            best_score = score
            best = s

    # Truncate cleanly
    summary = best.strip()
    if len(summary) > 140:
        summary = summary[:140].rsplit(" ", 1)[0] + "..."

    # Prepend subject if summary is too short/generic
    if len(summary) < 25 and subject:
        return f"{subject[:60]}: {summary}"

    return summary[:150]


def generate_longer_summary(subject: str, sender: str, body: str, urls: list) -> str:
    """Generate a slightly longer summary for the detail view."""
    body_clean = body[:800].strip().replace('\n', ' ').replace('\r', '')
    url_info = f"Contains {len(urls)} link(s)" if urls else "No links found"
    return (
        f"📧 **Subject:** {subject[:100]}\n"
        f"👤 **From:** {sender[:80]}\n"
        f"🔗 **{url_info}**\n\n"
        f"📝 {body_clean[:600]}"
    )


def detect_gibberish(subject: str, body: str) -> int:
    """Detect random/gibberish text that doesn't form real words.
    Returns a score (0-5) indicating how likely it is gibberish.
    """
    import re as _re
    score = 0
    text = f"{subject} {body}"

    # ── ALL-CAPS body detection ──
    # If body is mostly ALL CAPS with real words but no email structure (greeting, signature),
    # it's likely dramatic nonsense / song lyrics / spam text
    body_cleaned = body.strip()
    if len(body_cleaned) > 30:
        # Count uppercase letters vs total letters
        letters = [c for c in body_cleaned if c.isalpha()]
        if letters:
            upper_ratio = sum(1 for c in letters if c.isupper()) / len(letters)
            if upper_ratio > 0.85:
                # Check for absence of normal email structure
                # Use word-boundary matching so 'to:' doesn't match 'into:' etc.
                body_lower = body_cleaned.lower()
                has_greeting = any(
                    g in body_lower 
                    for g in ['dear ', 'hi ', 'hello ', 'hey ', 'greetings']
                ) or bool(re.search(r'\bto\b', body_lower)) or bool(re.search(r'\bfrom\b', body_lower))
                has_sig = any(s in body_lower for s in ['regards', 'sincerely', 'thanks,', 'best,', 'cheers,', 'sent from', '---'])
                # It's dramatic/poetic all-caps text - no greeting, no signature = spam
                if not has_greeting:
                    score += 3
                    # If it reads like song lyrics (no formal structure at all)
                    lines = body_cleaned.split('\n')
                    if len(lines) >= 3:
                        score += 1  # Multi-line all-caps = extra suspicious
    
    # ── Detect poetic/song lyric structure ──
    # Multiple short lines, each capitalized like verse
    if len(body_cleaned) > 50:
        lines = [l.strip() for l in body_cleaned.split('\n') if l.strip()]
        if len(lines) >= 3:
            # Check if ALL lines start with capital letter
            capital_lines = sum(1 for l in lines if l and l[0].isupper())
            if capital_lines == len(lines) and capital_lines >= 3:
                # Check average line length (poetry tends to have short lines)
                avg_len = sum(len(l) for l in lines) / len(lines)
                if avg_len < 60:  # Short lines like verse
                    body_lower = body_cleaned.lower()
                    has_greeting = any(
                        g in body_lower 
                        for g in ['dear ', 'hi ', 'hello ', 'hey ', 'greetings']
                    ) or bool(re.search(r'\bto\b', body_lower)) or bool(re.search(r'\bfrom\b', body_lower))
                    if not has_greeting:
                        score += 2

    # 1. Check for keyboard-mash patterns (asdf, qwerty, fdsa, etc.)
    keyboard_mashes = ['asdf', 'qwerty', 'qwert', 'qwe', 'asd', 'fdsa', 'zxcv',
                       'xcvb', 'cvbn', 'vbnm', 'qwertyuiop', 'asdfghjkl',
                       'zxcvbnm', 'poiuyt', 'mnbvc', 'lkjh', 'rewq']
    for mash in keyboard_mashes:
        if mash in text.lower():
            score += 2
            break

    # 2. Check for repeated single characters (aaaaaaaa, bbbbbb, etc.)
    import re
    if re.search(r'(.)\1{4,}', text):  # Same char repeated 5+ times
        score += 2

    # 3. Check for repeating patterns (hihihi, lololol, hahaha, etc.)
    # Catches any 2-char pattern repeated 3+ times
    if re.search(r'(.{2})\1{2,}', text):
        score += 3
    # Catches any 1-char-with-separator pattern (h_i_h_i_h_i, x x x x, etc.)
    if re.search(r'(.)(?:\W?\1){4,}', text):
        score += 2

    # 3b. Lorem ipsum / placeholder text (common in test spam)
    lorem = ['lorem ipsum', 'lorem', 'ipsum', 'dolor sit amet',
             'consectetur', 'adipiscing', 'placeholder text',
             'sample text', 'test test test', 'content here']
    for l in lorem:
        if l in text.lower():
            score += 2
            break

    # 3c. Base64-like / hex strings (long alphanumeric without spaces)
    long_seqs = re.findall(r'[a-zA-Z0-9+/=]{20,}', text)
    if len(long_seqs) >= 2:
        score += 2
    elif len(long_seqs) >= 1:
        score += 1

    # 3d. Repeated identical words (spam list padding)
    words_count = re.findall(r'\b\w+\b', text.lower())
    if len(words_count) >= 5:
        unique_ratio = len(set(words_count)) / len(words_count)
        if unique_ratio < 0.3:  # Less than 30% unique words
            score += 2

    # 3e. Very high ratio of non-alphanumeric chars (emoji spam, symbols)
    if len(text) > 10:
        alnum = sum(1 for c in text if c.isalnum() or c.isspace())
        non_alnum_ratio = 1 - (alnum / len(text))
        if non_alnum_ratio > 0.4:  # 40%+ symbols/emojis
            score += 2

    # 4. Check subject for random character sequences
    # A real word should have vowels mixed with consonants
    subject_clean = re.sub(r'[^a-zA-Z]', '', subject)
    if len(subject_clean) > 2:
        # Count consonant runs (3+ consecutive consonants = suspicious)
        cons_runs = re.findall(r'[bcdfghjklmnpqrstvwxyz]{3,}', subject_clean, re.IGNORECASE)
        if cons_runs:
            total_cons = sum(len(r) for r in cons_runs)
            if total_cons > len(subject_clean) * 0.6:  # 60%+ consonants
                score += 2

        # Check if subject has no real words (no vowels = impossible for real words)
        if not re.search(r'[aeiou]', subject_clean, re.IGNORECASE):
            score += 3

    # 4b. Pure numeric gibberish (just numbers or numbers + random letters)
    body_clean_nospace = ''.join(body.split())
    if len(body_clean_nospace) > 2:
        # Check if mostly numbers
        num_count = sum(1 for c in body_clean_nospace if c.isdigit())
        if num_count > 0 and num_count / max(len(body_clean_nospace), 1) > 0.7:
            score += 3  # Mostly numbers = gibberish
        # Single repeated character (like sssssssss)
        unique_chars = len(set(body_clean_nospace.lower()))
        if len(body_clean_nospace) >= 5 and unique_chars <= 2:
            score += 3

    # 5. Check for very short body with no recognizable words
    body_words = [w for w in body.split() if len(w) > 1]
    body_lower = body.lower()
    subject_lower = subject.lower()
    
    # Basic common English words for reference
    common_words = {'the','a','an','is','are','was','were','be','been','has','have',
        'had','do','does','did','will','would','can','could','should','may','might',
        'this','that','these','those','it','its','we','our','you','your','they','their',
        'he','she','him','her','his','my','me','i','not','no','yes','ok','okay','please',
        'thank','thanks','dear','hello','hi','hey','greetings','help','need','want',
        'get','make','go','come','take','see','know','think','say','tell','ask','reply',
        'send','receive','check','confirm','update','change','reset','verify','login',
        'logout','sign','account','email','message','call','text','info','information',
        'update','status','order','payment','invoice','receipt','shipping','delivery',
        'track','tracking','link','click','visit','open','view','download','file','attach',
        'document','photo','picture','image','video','audio','call','meeting','schedule',
        'time','date','today','tomorrow','yesterday','now','later','soon','urgent',
        'important','critical','alert','warning','notice','security','privacy','policy',
        'terms','conditions','support','service','help','faq','contact','phone','mobile',
        'subscribe','unsubscribe','newsletter','offer','deal','sale','discount','free',
        'gift','bonus','win','won','prize','lucky','congratulations','selected','chosen',
        'test','testing','example','sample','demo','trial','start','stop','pause',
        'continue','finish','complete','done','success','fail','error','warning','info',
        'bot','robot','automated','system','notification','alert','reminder'}
    
    # Check body words: if very few match common words, likely gibberish
    if len(body_words) <= 4:
        words_found = sum(1 for w in body_words if w.lower() in common_words or len(w) <= 1)
        if len(body_words) > 0 and words_found == 0:
            score += 3  # No real words in body
        elif len(body_words) > 0 and words_found <= 1:
            score += 2
    
    # Check subject words: if subject is more than 3 chars and has no common words
    subject_words = [w for w in subject_lower.split() if len(w) > 1]
    if subject_words:
        sub_words_found = sum(1 for w in subject_words if w in common_words)
        if sub_words_found == 0:
            score += 1
            # If subject is longer than 5 chars and has NO common words, very suspicious
            if len(subject_clean) > 5:
                score += 1
    
    # 6. Check for unusual character:letter ratio
    if len(text) > 10:
        special_chars = sum(1 for c in text if c in '!@#$%^&*()_+-=[]{}|;:,.<>?/~`')
        if special_chars > len(text) * 0.3:  # 30%+ special characters
            score += 2

    return min(score, 5)


def categorize(subject: str, sender: str, body: str, urls: list) -> str:
    """
    Classify an email into one of the 6 categories using weighted heuristic scoring.
    Returns: "pending" | "low_concern" | "mild" | "critical" | "spam" | "scam"
    """
    text = f"{subject} {sender} {body}".lower()
    subject_lower = subject.lower()

    # ── Initialize scores ──
    phishing_score = 0
    scam_score = 0
    bec_score = 0
    spam_score = 0
    urgency_score = 0

    # ── 1. Sender spoofing analysis ──
    spoofing_score = check_sender_spoofing(subject, sender)
    if spoofing_score >= 4:
        phishing_score += 6  # Strong spoofing = likely phishing
    elif spoofing_score >= 2:
        phishing_score += 3

    # ── 2. Gibberish/random text detection (spam) ──
    gibberish_score = detect_gibberish(subject, body)
    spam_score += gibberish_score

    # ── 3. URL analysis ──
    url_result = analyze_urls(urls, text)
    phishing_score += url_result["score"]

    # ── 3. Phishing pattern matching ──
    for pattern in PHISHING_PATTERNS:
        if pattern in text:
            # Higher weight if in subject
            if pattern in subject_lower:
                phishing_score += 4
            else:
                phishing_score += 3

    # ── 4. Scam pattern matching ──
    for pattern in SCAM_PATTERNS:
        if pattern in text:
            if pattern in subject_lower:
                scam_score += 3
            else:
                scam_score += 2

    # ── 5. BEC (CEO Fraud) pattern matching ──
    for pattern in BEC_PATTERNS:
        if pattern in text:
            bec_score += 4

    # ── 6. Urgency/ pressure analysis (only matters if tied to money/account/prize/crypto) ──
    urgency_keywords = ["account", "password", "login", "verify", "bank", "payment",
                         "money", "pay", "card", "crypto", "bitcoin", "wallet",
                         "prize", "won", "lottery", "claim", "gift card",
                         "suspended", "limited", "blocked", "security", "alert",
                         "homework", "grade", "assignment", "exam", "math",
                         "mathematics", "class", "course", "deadline",
                         "submission", "student", "academic"]
    raw_urgency = 0
    for pattern in URGENCY_PATTERNS:
        if pattern in subject_lower:
            raw_urgency += 3
        elif pattern in text:
            raw_urgency += 2
    # Only apply urgency if it's paired with a trigger keyword
    if raw_urgency > 0 and any(kw in text for kw in urgency_keywords):
        urgency_score = raw_urgency

    # ── 7. Spam pattern matching ──
    for pattern in SPAM_PATTERNS:
        if pattern in text:
            spam_score += 1

    # ── 8. Additional heuristics ──

    # Generic greeting check (phishing often lacks personalization)
    for greeting in ["dear customer", "dear user", "dear member",
                      "dear client", "dear sir", "dear madam",
                      "dear beneficiary", "dear winner", "dear email user",
                      "valued customer", "valued member"]:
        if greeting in text:
            phishing_score += 1
            break

    # Multiple exclamation marks (urgency/ unprofessional) - only if paired with triggers
    urgency_triggers_check = ["account", "password", "login", "verify", "bank", "payment",
                               "money", "pay", "card", "crypto", "prize", "won", "claim",
                               "suspended", "limited", "security", "alert", "gift"]
    if "!!" in text and any(kw in text for kw in urgency_triggers_check):
        urgency_score += 1

    # ALL CAPS subject - only if paired with triggers
    caps_ratio = sum(1 for c in subject if c.isupper()) / max(len(subject), 1)
    if len(subject) > 5 and caps_ratio > 0.6 and any(kw in text for kw in urgency_triggers_check):
        urgency_score += 2

    # Check for HTML-only emails (common in phishing)
    if "<html" in body.lower() or "<a href" in body.lower():
        phishing_score += 1

    # Check for mismatched Reply-To
    if "reply-to" in text[:500].lower():
        phishing_score += 1

    # Check for very short body (potential tracking-only email)
    body_words = len(body.split())
    if body_words < 5 and urls:
        phishing_score += 1

    # ── FINAL CLASSIFICATION ──

    # Priority 1: BEC / CEO Fraud
    if bec_score >= 6:
        return "scam"

    # Priority 2: Strong URL score (shorteners + brand mimicry)
    if url_result["shortened_count"] >= 2 and url_result["brand_mimicry_count"] >= 1:
        return "scam"
    if url_result["score"] >= 5:
        return "scam"

    # ── Incorporate 15-signal analysis ──
    signals = analyze_signals(subject, sender, body, urls)
    scam_score += signals["scam_score"]
    phishing_score += signals["phishing_score"]
    spam_score += signals["spam_score"]
    # Add extra urgency from signals (urgency pressure + grammar anomalies)
    # Urgency only counts towards critical/scam if paired with money/account/prize/crypto
    urgency_trigger_words = [
        "account", "password", "login", "verify", "bank", "payment",
        "money", "pay", "card", "crypto", "bitcoin", "wallet",
        "prize", "won", "lottery", "claim", "gift card",
        "suspended", "limited", "blocked", "security", "alert",
        "homework", "grade", "assignment", "exam", "math",
        "mathematics", "deadline", "submission", "student", "academic",
    ]
    has_urgency_trigger = any(w in text for w in urgency_trigger_words)

    if "urgency_pressure" in signals["signals"] and has_urgency_trigger:
        urgency_score += min(len(signals["signals"]["urgency_pressure"]) * 2, 4)

    # ── FINAL CLASSIFICATION ──

    # ── CONTEXT-AWARE OVERRIDE ──
    # Owner: student coder, no bank accounts.
    # Bank/money/prize/password email + generic greeting or urgency = auto scam.
    scam_trigger_kw = ["bank","account","money","payment","transfer",
        "prize","won","win","lucky","congratulations",
        "password","login","verify","security","alert",
        "crypto","bitcoin","gift card"]
    has_scam_trigger = any(kw in text for kw in scam_trigger_kw)
    has_generic = any(g in text for g in ["dear customer","dear user","dear sir",
        "dear madam","valued customer","dear winner","dear beneficiary",
        "dear client","dear member","dear email user",
        "dear account holder","dear applicant","dear resident",
        "to whom it may concern"])
    has_urgency_scam = raw_urgency >= 2
    context_flags = sum([has_scam_trigger, has_generic, has_urgency_scam])
    if context_flags >= 2:
        scam_score += 4
    if context_flags >= 3:
        return "scam"

    # ── NEWS DOMAIN OVERRIDE ──
    # If sender is from a known news source, drop to low_concern
    sender_lower = sender.lower()
    for news_domain in NEWS_DOMAINS:
        if news_domain in sender_lower:
            # Extract domain from email
            import re as _re2
            email_match = _re2.search(r'@([\w.-]+)', sender_lower)
            if email_match:
                email_domain = email_match.group(1)
                if news_domain in email_domain:
                    return "low_concern"
            else:
                if news_domain in sender_lower:
                    return "low_concern"

    # ── ACADEMIC OVERRIDE (student context) ──
    # Zero out scam scores so academic emails can still show urgency/critical
    subj_lower = subject.lower()
    body_lower = body.lower() if body else ""
    is_academic = any(kw in subj_lower or kw in body_lower for kw in ACADEMIC_KEYWORDS)
    if is_academic:
        # Zero out scam/phishing scores so academic emails are not flagged as scams
        scam_score = 0
        bec_score = 0
        phishing_score = 0

    # ── PRIORITY CLASSIFICATION ──
    # Priority 1: BEC / CEO Fraud
    if bec_score >= 6:
        return "scam"

    # Priority 2: Strong URL score (shorteners + brand mimicry)
    if url_result["shortened_count"] >= 2 and url_result["brand_mimicry_count"] >= 1:
        return "scam"
    if url_result["score"] >= 5:
        return "scam"

    # Priority 3: Phishing + Spoofing combo
    if spoofing_score >= 3 and phishing_score >= 4:
        return "scam"

    # Priority 4: Signal-level overrides (highest confidence)
    if signals["otp_request"] or signals["safe_handling"]:
        return "scam"

    # Priority 5: Pure scam patterns
    if scam_score >= 6:
        return "scam"

    # Priority 6: Phishing with urgency → scam
    if phishing_score >= 6 and urgency_score >= 2:
        return "scam"

    # Priority 7: Scam/phishing detection → scam
    if phishing_score >= 5 or scam_score >= 3:
        return "scam"

    # Priority 8: Pure high urgency
    if urgency_score >= 5:
        return "critical"

    # Priority 9: BEC low score
    if bec_score >= 3:
        return "critical"

    # Priority 10: Urgency + any scam/phishing → scam
    if urgency_score >= 3 and (phishing_score >= 2 or scam_score >= 2):
        return "scam"

    # Priority 11: Strong spam
    if spam_score >= 3:
        return "spam"

    # Priority 12: Spam + urgency
    if spam_score >= 2 and urgency_score >= 2:
        return "spam"

    # Priority 13: Mild (some indicators but low confidence)
    total_score = phishing_score + scam_score + spam_score + bec_score + urgency_score + spoofing_score
    if total_score >= 2 or phishing_score >= 2 or scam_score >= 2 or spam_score >= 2:
        return "mild"

    # Priority 14: Default
    return "low_concern"


# ─── 15-SIGNAL DETECTION FRAMEWORK ───────────────────────────────────────

SIGNAL_PATTERNS = {
    "urgency_pressure": [
        "act now", "last chance", "within 1 hour", "within 24 hours",
        "limited time", "offer expires", "hurry", "don't miss",
        "immediately", "right now", "today only", "ends soon",
        "final notice", "final warning", "deadline",
        # Singapore-specific
        "within 1 hour", "before it's too late",
        "immediate action", "respond immediately",
    ],
    "money_request": [
        "gift card", "bitcoin", "crypto", "wire transfer",
        "bank transfer", "western union", "money gram",
        "processing fee", "advance fee", "transfer fee",
        "send money", "send payment", "pay now", "payment required",
        "credit card number", "bank details",
    ],
    "login_request": [
        "verify your account", "verify account", "reset password",
        "confirm password", "sign in", "log in", "login",
        "update your account", "account verification",
        "secure your account", "restore access", "unlock account",
    ],
    "too_good_offer": [
        "free money", "you won", "you have won", "congratulations you won",
        "cash prize", "grand prize", "lottery", "inheritance",
        "guaranteed return", "double your money", "risk free",
        "work from home", "earn money", "passive income",
        "investment opportunity", "high yield",
    ],
    "impersonation": [
        "paypal", "amazon", "apple", "microsoft", "google",
        "netflix", "facebook", "instagram", "linkedin",
        "bank", "dbs", "ocbc", "uob", "hsbc", "maybank",
        "government", "irs", "hsa", "cpf", "police",
        "courrier", "dhl", "fedex", "singpost",
        # Singapore-specific
        "mas", "iras", "mom", "moe", "ica", "lta", "hdb",
        "singpass", "cpf board", "nric", "myinfo",
        "posb", "digibank", "paynow",
    ],
    "suspicious_link": [
        # URL-based - handled in analyze_signals
    ],
    "attachment_risk": [
        ".zip", ".exe", ".scr", ".bat", ".cmd", ".vbs",
        ".js", ".jar", ".msi", ".ps1", ".dll",
        "invoice", "receipt", "payment confirmation",
    ],
    "personal_info_request": [
        "ssn", "social security", "passport", "driver license",
        "password", "otp", "one-time password", "pin number",
        "4-digit pin", "6-digit pin", "security pin",
        "credit card", "card number", "cvv", "cvc",
        "bank account", "routing number", "identity",
        "date of birth", "nric", "fin",
        # Singapore-specific
        "singpass", "sing pass", "myinfo",
        "digibank pin", "digibpin", "digibank user id",
        "digital token", "paynow",
    ],
    "poor_personalization": [
        "dear customer", "dear user", "dear member", "dear client",
        "dear sir", "dear madam", "valued customer", "valued member",
        "to whom it may concern", "dear beneficiary",
    ],
    "threat_language": [
        "account will be closed", "account will be suspended",
        "account will be terminated", "account will be locked",
        "legal action", "police notice", "lawsuit", "court",
        "penalty", "fine", "charged", "criminal",
        "will be reported", "authorities", "investigation",
    ],
    "sender_mismatch": [
        # Handled by check_sender_spoofing
    ],
    "unsolicited_marketing": [
        "buy now", "shop now", "order now", "subscribe",
        "newsletter", "weekly deal", "exclusive offer",
        "unsubscribe", "click here", "limited offer",
    ],
    "grammar_anomalies": [
        # Handled separately below
    ],
    "otp_code_request": [
        "share your otp", "send otp", "verification code",
        "one time password", "otp", "2fa code",
        "confirm your code", "verify code",
    ],
    "safe_handling": [
        "don't tell anyone", "keep this private", "keep secret",
        "don't share this", "confidential", "do not disclose",
        "secret", "between you and me", "not for sharing",
    ],
}


def analyze_signals(subject: str, sender: str, body: str, urls: list) -> dict:
    """Evaluate all 15 scam/spam signals and return detailed results."""
    text = f"{subject} {sender} {body}".lower()
    results = {
        "signals": {},
        "scam_score": 0,
        "phishing_score": 0,
        "spam_score": 0,
        "details": [],
        "otp_request": False,
        "safe_handling": False,
        "high_priority_signals": [],
    }

    # 1. Urgency pressure
    urgency_hits = [p for p in SIGNAL_PATTERNS["urgency_pressure"] if p in text]
    if urgency_hits:
        score = min(len(urgency_hits) * 2, 6)
        results["phishing_score"] += score
        results["signals"]["urgency_pressure"] = urgency_hits
        if score >= 4:
            results["high_priority_signals"].append("Strong urgency pressure")

    # 2. Money request
    money_hits = [p for p in SIGNAL_PATTERNS["money_request"] if p in text]
    if money_hits:
        score = len(money_hits) * 3
        results["scam_score"] += score
        results["signals"]["money_request"] = money_hits
        results["high_priority_signals"].append("Money/payment request")

    # 3. Login request
    login_hits = [p for p in SIGNAL_PATTERNS["login_request"] if p in text]
    if login_hits:
        score = len(login_hits) * 3
        results["phishing_score"] += score
        results["signals"]["login_request"] = login_hits
        results["high_priority_signals"].append("Login/credential request")

    # 4. Too-good offer
    offer_hits = [p for p in SIGNAL_PATTERNS["too_good_offer"] if p in text]
    if offer_hits:
        score = len(offer_hits) * 2
        results["scam_score"] += score
        results["signals"]["too_good_offer"] = offer_hits

    # 5. Impersonation
    impersonation_hits = [p for p in SIGNAL_PATTERNS["impersonation"] if p in text]
    if impersonation_hits:
        results["signals"]["impersonation"] = impersonation_hits
        # Check sender domain mismatch
        sender_lower = sender.lower()
        email_domain = ""
        match = re.search(r'@([\w.-]+)', sender_lower)
        if match:
            email_domain = match.group(1)
        for brand in impersonation_hits:
            if brand in sender_lower and email_domain:
                # Check if real domain matches
                real_domains = {
                    "paypal": "paypal.com", "amazon": "amazon.com",
                    "apple": "apple.com", "google": "google.com",
                    "microsoft": "microsoft.com", "netflix": "netflix.com",
                    "dbs": "dbs.com", "ocbc": "ocbc.com", "uob": "uob.com.sg",
                    "posb": "posb.com.sg", "singpass": "singpass.gov.sg",
                    "iras": "iras.gov.sg", "mom": "mom.gov.sg",
                    "cpf": "cpf.gov.sg",
                }
                real = real_domains.get(brand, f"{brand}.com")
                if real not in email_domain and email_domain != "unknown":
                    results["phishing_score"] += 4
                    results["high_priority_signals"].append(
                        f"Claims '{brand}' but email domain is '{email_domain}'"
                    )

    # 6. Suspicious link
    for u in urls:
        u_lower = u.lower()
        # Check for IP address URLs
        if re.match(r'https?://\d+\.\d+\.\d+\.\d+', u_lower):
            results["phishing_score"] += 3
            results["signals"]["suspicious_link"] = results["signals"].get("suspicious_link", []) + ["IP address URL"]
        # Suspicious TLDs
        suspicious_tlds = [".xyz", ".top", ".click", ".gq", ".ml", ".tk", ".cf", ".ga", ".loan", ".work"]
        for tld in suspicious_tlds:
            if u_lower.endswith(tld):
                results["phishing_score"] += 3
                break
        # Shorteners
        shorteners = ["bit.ly", "tinyurl", "rb.gy", "shorturl", "ow.ly", "is.gd", "buff.ly", "cutt.ly"]
        for s in shorteners:
            if s in u_lower:
                results["phishing_score"] += 2
                break

    # 7. Attachment risk
    attach_hits = [p for p in SIGNAL_PATTERNS["attachment_risk"] if p in text]
    if attach_hits:
        results["spam_score"] += len(attach_hits)
        results["signals"]["attachment_risk"] = attach_hits

    # 8. Personal info request
    info_hits = [p for p in SIGNAL_PATTERNS["personal_info_request"] if p in text]
    if info_hits:
        score = len(info_hits) * 3
        results["phishing_score"] += score
        results["signals"]["personal_info_request"] = info_hits
        results["high_priority_signals"].append("Requests personal/sensitive info")

    # 9. Poor personalization
    generic_hits = [p for p in SIGNAL_PATTERNS["poor_personalization"] if p in text]
    if generic_hits:
        results["spam_score"] += len(generic_hits)
        results["signals"]["poor_personalization"] = generic_hits

    # 10. Threat language
    threat_hits = [p for p in SIGNAL_PATTERNS["threat_language"] if p in text]
    if threat_hits:
        score = len(threat_hits) * 2
        results["phishing_score"] += score
        results["signals"]["threat_language"] = threat_hits
        if score >= 4:
            results["high_priority_signals"].append("Uses threatening language")

    # 11. Sender mismatch (already handled by check_sender_spoofing)

    # 12. Unsolicited marketing
    market_hits = [p for p in SIGNAL_PATTERNS["unsolicited_marketing"] if p in text]
    if market_hits:
        results["spam_score"] += len(market_hits)
        results["signals"]["unsolicited_marketing"] = market_hits

    # 13. Grammar anomalies - multiple exclamation marks and all-caps
    if "!!" in text:
        results["spam_score"] += 1
        results["signals"]["grammar_anomalies"] = ["Excessive exclamation marks"]
    caps_ratio = sum(1 for c in subject if c.isupper()) / max(len(subject), 1)
    if len(subject) > 5 and caps_ratio > 0.6:
        results["spam_score"] += 1
        results["signals"]["grammar_anomalies"] = results["signals"].get("grammar_anomalies", []) + ["ALL CAPS subject"]

    # 14. OTP/code request (HIGHEST RISK)
    otp_hits = [p for p in SIGNAL_PATTERNS["otp_code_request"] if p in text]
    if otp_hits:
        results["phishing_score"] += 5
        results["otp_request"] = True
        results["signals"]["otp_code_request"] = otp_hits
        results["high_priority_signals"].append("🚨 OTP/verification code request")

    # 15. Safe handling / secrecy
    secret_hits = [p for p in SIGNAL_PATTERNS["safe_handling"] if p in text]
    if secret_hits:
        results["scam_score"] += 4
        results["safe_handling"] = True
        results["signals"]["safe_handling"] = secret_hits
        results["high_priority_signals"].append("🚨 Encourages secrecy")

    return results


# ─── PRIORITY CLASSIFICATION (Student/Coder Profile) ──────────────────────


# ─── PRIORITY CLASSIFICATION (Student/Coder Profile) ──────────────────────

HIGH_PATTERNS = [
    # Assignments & deadlines
    "assignment due", "homework due", "deadline", "submission",
    "due tomorrow", "due today", "due date", "submit by",
    "project deadline", "final submission",
    # Interviews
    "interview", "interview invitation", "interview schedule",
    "technical interview", "behavioral interview",
    "onsite interview", "phone screen",
    # Professor / academic
    "professor", "lecturer", "module coordinator",
    "class announcement", "lecture cancellation",
    "exam schedule", "exam results", "grades posted",
    # Production / work
    "production outage", "production down", "sev1", "sev2",
    "incident response", "critical bug", "security patch",
    "urgent fix", "hotfix", "rollback",
    # University admin
    "enrollment", "registration deadline", "tuition",
    "scholarship", "financial aid",
]

MEDIUM_PATTERNS = [
    # Team & work
    "team meeting", "standup", "sprint", "code review",
    "pull request", "merge request", "pr ", "codebase",
    "team discussion", "retrospective", "sprint planning",
    # Events
    "event invitation", "hackathon", "workshop",
    "tech talk", "webinar", "conference",
    "networking", "career fair",
    # Internships / jobs
    "internship", "internship opportunity",
    "application status", "job offer", "offer letter",
    # Notifications
    "github", "gitlab", "slack", "jira", "linear",
    "notion", "figma", "vercel", "netlify",
    "deploy", "build failed", "test failed",
    # Newsletters (student-relevant)
    "weekly digest", "monthly update",
    "club meeting", "cca", "student council",
]

LOW_PATTERNS = [
    # Marketing
    "marketing", "promotional", "promotion",
    "limited time offer", "buy now", "shop now",
    "discount", "sale", "clearance", "deal",
    # Newsletters
    "newsletter", "weekly roundup", "daily digest",
    "sponsored", "partner offer", "advertisement",
    # Social
    "you have a new follower", "you have a new friend",
    "someone liked your", "new comment",
    "facebook", "instagram", "tiktok", "twitter",
    "linkedin notification",
    # Spammy
    "you won", "congratulations", "free",
    "act now", "limited spots",
    # Retail
    "your order", "shipping confirmation", "order confirmation",
    "track your package", "your receipt",
]


def classify_priority(subject: str, sender: str, body: str) -> str:
    """
    Classify email priority based on student/coder profile.
    Returns "high" | "medium" | "low"
    """
    text = f"{subject} {sender} {body}".lower()

    high_score = sum(2 for p in HIGH_PATTERNS if p in text)
    medium_score = sum(1 for p in MEDIUM_PATTERNS if p in text)
    low_score = sum(1 for p in LOW_PATTERNS if p in text)

    # Check subject line specifically (higher weight)
    subj_lower = subject.lower()
    high_score += sum(3 for p in HIGH_PATTERNS if p in subj_lower)
    medium_score += sum(2 for p in MEDIUM_PATTERNS if p in subj_lower)

    # High priority takes precedence
    if high_score >= 2:
        return "high"

    # Medium
    if medium_score >= 2:
        return "medium"

    # Check if low patterns dominate
    if low_score >= high_score + 1 and low_score >= medium_score:
        return "low"

    # If medium has some signal, default medium
    if medium_score >= 1:
        return "medium"

    # Default to medium (neutral)
    return "medium"
