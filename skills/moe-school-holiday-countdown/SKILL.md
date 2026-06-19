---
name: "moe-school-holiday-countdown"
description: "Count weekdays until next MOE JC school holiday. Discord-interactive."
---

# MOE JC School Holiday Countdown

Counts how many **weekdays (Mon–Fri)** remain until the next MOE Junior College school holiday. Primary interaction is through **Discord** — invoked by a command or keyword.

## Holiday Data (MOE JC 2026)

| Holiday | Start Date | End Date |
|---------|-----------|---------|
| March Holiday | 14 Mar 2026 | 22 Mar 2026 |
| June Holiday | 30 May 2026 | 28 Jun 2026 |
| September Holiday | 5 Sep 2026 | 13 Sep 2026 |
| Year-End Holiday (JC) | 28 Nov 2026 | 31 Dec 2026 |

## How It Works

1. **Get today's date** in Singapore time (UTC+8).
2. **Find the next holiday** — iterate through holidays sorted by start date; pick the first whose start date is >= today.
3. **If currently in a holiday** — check if today falls between any holiday's start and end (inclusive).
4. **Count weekdays** — iterate day-by-day from today until the holiday start date. Count only Mon–Fri.
5. **Return result.**

### Edge Cases

- **In a holiday** — "You're on holiday! Enjoy your break! 🏖️ (X days remaining)"
- **After year-end** — "School year is over! 🎓"
- **A-Level exam period (JC2)** — JC2 Term IV ends at the end of A-Level exams, which is variable. For JC2 students, consider the September holiday the last fixed break.

## Discord Integration

### Triggers
Respond to any of these in Discord:
- `!holidays`
- `!schoolcountdown`
- `!countdown`
- Natural language: "how many days until holidays", "school days left", etc.

### Handler Logic
When triggered:
1. Run `scripts/countdown.js` (Node.js)
2. The script outputs a formatted countdown string
3. Reply in the Discord channel with the output

### Example Discord Output
```
📅 **School Holiday Countdown (JC)**

Today: Thu, 18 Jun 2026

🏖️ You're on **June Holiday**!
   Ends: 2026-06-28
   Weekdays of holiday remaining: 6

Next holiday: **September Holiday** (2026-09-05 – 2026-09-13)
   Term starts: Mon, 29 Jun 2026 💀
   School weekdays until then: **50**

Stay strong, soldier. 🫡
```

### Bot Implementation
In the Discord bot message handler, add:
```javascript
const { getCountdown } = require('./skills/moe-school-holiday-countdown/scripts/countdown.js');

// On trigger message:
if (msg.content.match(/^!(holidays|schoolcountdown|countdown)\b/i) ||
    msg.content.match(/\b(how many|school) days.*(holiday|left)\b/i)) {
  const result = getCountdown();
  msg.channel.send(result);
}
```

## Files

```
skills/moe-school-holiday-countdown/
├── SKILL.md                          # This file
├── assets/
│   └── moe-holidays-2026.json        # Holiday date data
└── scripts/
    └── countdown.js                  # Core countdown logic
```

## Run Locally

```bash
node skills/moe-school-holiday-countdown/scripts/countdown.js
```

## Maintenance

Update this skill annually when MOE releases the new school calendar (typically July of the preceding year).
- Replace `assets/moe-holidays-2026.json` with the new year's data
- Update the holiday table in this file
- Update the year references in `scripts/countdown.js`
