#!/usr/bin/env node
/**
 * MOE JC School Holiday Countdown
 * Counts weekdays until the next JC school holiday.
 * Input: nothing (uses current date)
 * Output: formatted countdown string
 */

const holidays = [
  { name: "March Holiday", start: "2026-03-14", end: "2026-03-22" },
  { name: "June Holiday", start: "2026-05-30", end: "2026-06-28" },
  { name: "September Holiday", start: "2026-09-05", end: "2026-09-13" },
  { name: "Year-End Holiday (JC)", start: "2026-11-28", end: "2026-12-31" }
];

function parseDate(s) {
  return new Date(s + "T00:00:00.000Z");
}

function isWeekend(d) {
  const day = d.getUTCDay();
  return day === 0 || day === 6;
}

function countWeekdays(from, to) {
  let count = 0;
  const d = new Date(from);
  d.setUTCDate(d.getUTCDate() + 1);
  while (d <= to) {
    if (!isWeekend(d)) count++;
    d.setUTCDate(d.getUTCDate() + 1);
  }
  return count;
}

function formatDate(d) {
  const months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  const days = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];
  return `${days[d.getUTCDay()]}, ${d.getUTCDate()} ${months[d.getUTCMonth()]} ${d.getUTCFullYear()}`;
}

function getCountdown() {
  const today = new Date();
  // Rebase to UTC midnight for comparison
  const todayUtc = new Date(Date.UTC(today.getUTCFullYear(), today.getUTCMonth(), today.getUTCDate()));

  let lines = [];
  lines.push("📅 **School Holiday Countdown (JC)**");
  lines.push("");
  lines.push(`Today: ${formatDate(todayUtc)}`);

  // Check if currently in a holiday
  let currentHoliday = null;
  for (const h of holidays) {
    const hs = parseDate(h.start);
    const he = parseDate(h.end);
    if (todayUtc >= hs && todayUtc <= he) {
      currentHoliday = h;
      break;
    }
  }

  if (currentHoliday) {
    const he = parseDate(currentHoliday.end);
    const hdays = countWeekdays(todayUtc, he);
    lines.push("");
    lines.push(`🏖️ You're on **${currentHoliday.name}**!`);
    lines.push(`   Ends: ${currentHoliday.end}`);
    lines.push(`   Weekdays of holiday remaining: ${hdays}`);
  }

  // Find next holiday
  let nextIdx = -1;
  for (let i = 0; i < holidays.length; i++) {
    const hs = parseDate(holidays[i].start);
    if (hs > todayUtc) {
      nextIdx = i;
      break;
    }
  }

  if (nextIdx === -1) {
    lines.push("");
    lines.push("🎓 School year is over!");
  } else {
    const nh = holidays[nextIdx];
    const countFrom = currentHoliday ? parseDate(currentHoliday.end) : todayUtc;
    const schoolDays = countWeekdays(countFrom, parseDate(nh.start));
    const termStart = new Date(countFrom);
    termStart.setUTCDate(termStart.getUTCDate() + 1);

    lines.push("");
    lines.push(`Next holiday: **${nh.name}** (${nh.start} – ${nh.end})`);
    if (currentHoliday) {
      lines.push(`   Term starts: ${formatDate(termStart)} 💀`);
    }
    lines.push(`   School weekdays until then: **${schoolDays}**`);
    lines.push("");
    lines.push("Stay strong, soldier. 🫡");
  }

  return lines.join("\n");
}

// If run directly, print output
if (require.main === module) {
  console.log(getCountdown());
}

module.exports = { getCountdown };
