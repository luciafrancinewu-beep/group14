#!/usr/bin/env node
/**
 * JARVIS Email Monitor
 * Polls https://mail.group14.ydsp.tnkr.be/api/emails
 * Outputs notification to stdout for OpenClaw cron delivery.
 */

const STATE_FILE = '/home/ubuntu/.openclaw/workspace/skills/crisis-triage/email-monitor-state.json';
const API_BASE = 'https://mail.group14.ydsp.tnkr.be';

const fs = require('fs');
const https = require('https');
const http = require('http');

function fetch(url) {
  return new Promise((resolve, reject) => {
    const mod = url.startsWith('https') ? https : http;
    mod.get(url, { headers: { 'Accept': 'application/json' }, timeout: 10000 }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try { resolve(JSON.parse(data)); }
        catch { resolve(data); }
      });
    }).on('error', reject).on('timeout', function() { this.destroy(); reject(new Error('timeout')); });
  });
}

async function run() {
  let prevState = { total: 0, lastCheck: null, knownIds: [] };
  try {
    if (fs.existsSync(STATE_FILE)) {
      prevState = JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
    }
  } catch {}

  const [stats, emailsData] = await Promise.all([
    fetch(`${API_BASE}/api/stats`).catch(() => ({ total: 0 })),
    fetch(`${API_BASE}/api/emails`).catch(() => ({ emails: [] }))
  ]);

  const emails = emailsData.emails || [];
  const currentTotal = stats.total || emails.length;
  const now = new Date().toISOString();

  const prevIds = new Set(prevState.knownIds || []);
  const newEmails = emails.filter(e => !prevIds.has(e.id));

  let message = '';

  if (newEmails.length > 0) {
    const byCategory = {};
    for (const e of newEmails) {
      const cat = e.category || 'unknown';
      if (!byCategory[cat]) byCategory[cat] = [];
      byCategory[cat].push(e);
    }

    const criticalCount = (byCategory['critical'] || []).length;
    const scamCount = (byCategory['scam'] || []).length;

    message += `📬 **JARVIS Email Monitor**\n`;
    message += `**${newEmails.length} new** email(s) received since last check.\n`;
    message += `Total in inbox: **${currentTotal}**\n\n`;

    if (criticalCount > 0) {
      message += `🚨 **Critical:** ${criticalCount}\n`;
      for (const e of byCategory['critical']) {
        message += `  • [${e.priority}] ${e.subject}\n`;
      }
    }
    if (scamCount > 0) {
      message += `⚠️ **Scam:** ${scamCount}\n`;
      for (const e of byCategory['scam']) {
        message += `  • ${e.subject}\n`;
      }
    }
    if (byCategory['mild']) {
      message += `🟡 **Mild:** ${byCategory['mild'].length}\n`;
    }
    if (byCategory['low_concern']) {
      message += `🟢 **Low Concern:** ${byCategory['low_concern'].length}\n`;
    }

  } else {
    message = `📬 **JARVIS Email Monitor** — All clear.\n`;
    message += `No new emails since last check. Total inbox: **${currentTotal}**`;
  }

  // Save state
  const newState = {
    total: currentTotal,
    lastCheck: now,
    knownIds: emails.map(e => e.id),
    categories: stats
  };
  fs.writeFileSync(STATE_FILE, JSON.stringify(newState, null, 2));

  // Output message (OpenClaw cron will deliver this to Discord)
  console.log(message);
}

run().catch(err => {
  console.error(`❌ JARVIS Email Monitor error: ${err.message}`);
  process.exit(1);
});
