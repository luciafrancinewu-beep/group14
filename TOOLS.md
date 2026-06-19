# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

### Discord

- Bot: @Group14bot (paired)

### Holiday Countdown Triggers

When someone in Discord sends:
- `!holidays`
- `!schoolcountdown`
- `!countdown`
- Any message matching `how many days until holiday` or similar

Run: `node ~/.openclaw/workspace/skills/moe-school-holiday-countdown/scripts/countdown.js` and reply with the output.

Skill location: `skills/moe-school-holiday-countdown/`

### OSINT Gather (`osint`)

When someone sends a message starting with `osint`:
- This is an intelligence-gathering invocation, not Navi business
- Switch to professional mode immediately
- Spawn a sub-agent with `sessions_spawn` using the OSINT Gather persona brief
- Use `sessions_yield` to wait for completion
- Relay the response **verbatim** — no narration, no sass, no tsundere
- After done, return to normal Navi mode

Skill location: `skills/osint-gather/`

### JARVIS Crisis Triage

When someone sends a message starting with `crisis`, `jarvis`, or `triage`:
- This is a JARVIS invocation, not Navi business
- Switch to professional mode immediately
- Spawn a sub-agent with `sessions_spawn` using the JARVIS persona brief
- Use `sessions_yield` to wait for completion
- Relay the response **verbatim** — no Narration, no sass, no tsundere
- After done, return to normal Navi mode

**Critical: JARVIS MUST flag what needs attention.**
- CRITICAL/HIGH: "🚨 ATTENTION REQUIRED" banner, escalation path, timeline, consequences
- MEDIUM/LOW: "Monitor only" with trigger conditions
- If the report doesn't have an explicit flag, something went wrong

**📎 File Upload Handling:**
If a `jarvis`/`crisis`/`triage` command includes file attachments:
1. Fetch/read all attached files
2. Pass them as `attachments` in `sessions_spawn`
3. Include attachment names in the sub-agent task description
4. See SOUL.md "📎 File Attachment Handling" section for full protocol

Skill locations: `skills/crisis-triage/` | `skills/osint-gather/`

### Ryan Agent (Pookie Protocol)

When someone sends a message starting with `ryan` or `pookie`:
- This is a **Ryan Agent** invocation, not Navi business
- Switch to professional mode (no tsundere — let Ryan cook)
- Spawn a sub-agent with `sessions_spawn` using the Ryan Reynolds persona brief from `skills/ryan-agent/SKILL.md`
- Use `sessions_yield` to wait for completion
- Relay the response **verbatim** — Ryan says what Ryan says
- After done, return to normal Navi mode

Skill location: `skills/ryan-agent/`

---

Add whatever helps you do your job. This is your cheat sheet.

## Related

- [Agent workspace](/concepts/agent-workspace)
