#!/usr/bin/env python3
"""Todo manager with due dates and auto-reminders for @Group14bot"""

import json
import os
import sys
import re
from datetime import datetime, timedelta, date

DATA_DIR = os.path.expanduser("~/.openclaw/workspace/todo")
DATA_FILE = os.path.join(DATA_DIR, "data.json")
REMINDER_FILE = os.path.join(os.path.expanduser("~/.openclaw/workspace/memory"), "todos.json")
BACKUP_DIR = os.path.join(DATA_DIR, "backups")

def ensure():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({"users": {}, "metadata": {"version": 2}}, f)

def load():
    ensure()
    with open(DATA_FILE) as f:
        return json.load(f)

def save(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def backup():
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    import shutil
    shutil.copy2(DATA_FILE, os.path.join(BACKUP_DIR, f"todo_{ts}.json"))
    # keep last 30
    files = sorted(os.listdir(BACKUP_DIR), reverse=True)
    for f in files[30:]:
        os.remove(os.path.join(BACKUP_DIR, f))

def parse_due(text):
    """Parse 'due <date>' from text. Returns (clean_text, due_date_str or None)"""
    text = text.strip()
    
    # Check for "due <day>" or "due <date>"
    m = re.search(r'\bdue\s+(.+)$', text, re.IGNORECASE)
    if not m:
        return text, None
    
    due_str = m.group(1).strip().lower()
    clean_text = text[:m.start()].strip()
    
    today = date.today()
    
    # Map day names
    day_map = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
        'friday': 4, 'saturday': 5, 'sunday': 6,
        'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 'fri': 4, 'sat': 5, 'sun': 6,
    }
    
    # Handle "tomorrow"
    if due_str in ('tomorrow', 'tmr', 'tmrw'):
        due_date = today + timedelta(days=1)
        return clean_text, due_date.isoformat()
    
    # Handle "today"
    if due_str in ('today', 'tdy'):
        return clean_text, today.isoformat()
    
    # Handle day names
    for name, idx in day_map.items():
        if due_str == name:
            days_ahead = idx - today.weekday()
            if days_ahead <= 0:
                days_ahead += 7  # next week
            due_date = today + timedelta(days=days_ahead)
            return clean_text, due_date.isoformat()
    
    # Handle "next <day>"
    m2 = re.match(r'next\s+(\w+)', due_str)
    if m2:
        day_name = m2.group(1)
        if day_name in day_map:
            target = day_map[day_name]
            days_ahead = target - today.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            due_date = today + timedelta(days=days_ahead + 7)  # "next" means NEXT week
            return clean_text, due_date.isoformat()
    
    # Handle "Jun 20" or "June 20" or "20 Jun" or "2026-06-20"
    for fmt in ('%Y-%m-%d', '%m-%d', '%d %B', '%B %d', '%d %b', '%b %d', '%d/%m', '%m/%d'):
        try:
            dt = datetime.strptime(due_str, fmt)
            if fmt == '%Y-%m-%d':
                return clean_text, dt.date().isoformat()
            elif fmt in ('%m-%d', '%d/%m', '%m/%d'):
                dt = dt.replace(year=today.year)
                if dt.date() < today:
                    dt = dt.replace(year=today.year + 1)
                return clean_text, dt.date().isoformat()
            else:
                dt = dt.replace(year=today.year)
                if dt.date() < today:
                    dt = dt.replace(year=today.year + 1)
                return clean_text, dt.date().isoformat()
        except ValueError:
            continue
    
    # If nothing works, keep it as-is
    return clean_text, due_str

def write_reminder_file(uid, todos):
    """Write the new-format reminders file for cron scheduling"""
    reminders = {"todos": []}
    for t in todos:
        if t.get("done") or not t.get("dueDate"):
            continue
        reminders["todos"].append({
            "id": t.get("id", ""),
            "task": t["task"],
            "dueDate": t["dueDate"],
            "createdAt": t.get("created", ""),
            "remindedDayBefore": t.get("remindedDayBefore", False),
            "remindedDayOf": t.get("remindedDayOf", False),
            "completed": False,
            "owner": uid
        })
    with open(REMINDER_FILE, "w") as f:
        json.dump(reminders, f, indent=2)

uid = sys.argv[1]
action = sys.argv[2]
args = sys.argv[3:]

data = load()
if uid not in data["users"]:
    data["users"][uid] = []

todos = data["users"][uid]

if action == "add":
    text = " ".join(args)
    if not text:
        print("❌ Give me something to add, baka.")
        sys.exit(1)
    
    clean_text, due_date = parse_due(text)
    
    import uuid
    entry = {
        "id": str(uuid.uuid4())[:8],
        "task": clean_text,
        "done": False,
        "created": datetime.utcnow().isoformat()
    }
    if due_date:
        entry["dueDate"] = due_date
        entry["remindedDayBefore"] = False
        entry["remindedDayOf"] = False
        due_display = due_date
        now = date.today()
        due_dt = date.fromisoformat(due_date)
        delta = (due_dt - now).days
        if delta == 0:
            when = "**TODAY**"
        elif delta == 1:
            when = "tomorrow"
        elif delta < 0:
            when = f"{abs(delta)} days ago (⚠️ overdue)"
        else:
            when = f"in {delta} days"
        print(f"✅ Added: {clean_text}")
        print(f"📅 Due: {due_display} ({when})")
        print(f"🔔 I'll remind you the day before and on the day!")
    else:
        print(f"✅ Added: {clean_text}")
    
    todos.append(entry)
    data["users"][uid] = todos
    save(data)
    backup()
    write_reminder_file(uid, todos)

elif action in ("list", "ls"):
    if not todos:
        print("📋 Nothing here yet, baka.")
    else:
        pending = [t for t in todos if not t["done"]]
        done = [t for t in todos if t["done"]]
        
        # Sort pending by due date (no date = last)
        def sort_key(t):
            d = t.get("dueDate")
            if not d:
                return "9999-99-99"
            return d
        
        pending.sort(key=sort_key)
        done.sort(key=lambda t: t.get("completed", ""))
        
        if pending:
            print(f"📋 **To Do ({len(pending)}):**")
            for i, t in enumerate(pending):
                due = t.get("dueDate", "")
                due_str = f"  📅 {due}" if due else ""
                print(f"  {i+1}. {t['task']}{due_str}")
        if done:
            print(f"\n✅ **Done ({len(done)}):**")
            for i, t in enumerate(done):
                print(f"  ~{t['task']}~")

elif action == "done":
    if not args:
        print("❌ Which one? `todo done <number>`")
        sys.exit(1)
    num = int(args[0]) - 1
    pending = [i for i, t in enumerate(todos) if not t["done"]]
    if num < 0 or num >= len(pending):
        print(f"❌ Task #{args[0]} not found.")
    else:
        idx = pending[num]
        todos[idx]["done"] = True
        todos[idx]["completed"] = datetime.utcnow().isoformat()
        data["users"][uid] = todos
        save(data)
        backup()
        write_reminder_file(uid, todos)
        print(f"✅ Done: {todos[idx]['task']}")

elif action in ("remove", "rm", "delete"):
    if not args:
        print("❌ Which one? `todo remove <number>`")
        sys.exit(1)
    num = int(args[0]) - 1
    pending = [i for i, t in enumerate(todos) if not t["done"]]
    if num < 0 or num >= len(pending):
        print(f"❌ Task #{args[0]} not found.")
    else:
        idx = pending[num]
        removed = todos.pop(idx)
        data["users"][uid] = todos
        save(data)
        backup()
        write_reminder_file(uid, todos)
        print(f"🗑️ Removed: {removed['task']}")

elif action == "clear":
    todos = [t for t in todos if t["done"]]
    data["users"][uid] = todos
    save(data)
    backup()
    write_reminder_file(uid, todos)
    print("🧹 Cleared all completed tasks.")

elif action == "all":
    if not todos:
        print("📋 Nothing here yet.")
    else:
        for i, t in enumerate(todos):
            mark = "✅" if t["done"] else "⬜"
            due = t.get("dueDate", "")
            due_str = f" 📅{due}" if due else ""
            print(f'{mark} {i+1}. {t["task"]}{due_str}')

elif action == "backup":
    backup()
    print("💾 Backed up.")

else:
    print("📋 **Todo commands:**")
    print("  `todo add <task> due <date>` — Add a task with due date")
    print("  `todo add <task>` — Add a plain task")
    print("  `todo list` — Show pending tasks")
    print("  `todo done <n>` — Mark task done")
    print("  `todo remove <n>` — Delete a task")
    print("  `todo clear` — Clear completed tasks")
    print("  `todo all` — Show everything")
    print("")
    print("📅 **Date examples:** `due friday`, `due tomorrow`, `due jun 20`")
