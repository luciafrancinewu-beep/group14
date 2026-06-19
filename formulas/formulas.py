#!/usr/bin/env python3
"""Formula reference for @Group14bot"""
import json, os, shutil, sys
from datetime import datetime, timezone

DATA = os.path.expanduser("~/.openclaw/workspace/formulas/data.json")
BACKUP = os.path.expanduser("~/.openclaw/workspace/formulas/backups")

DEFAULT_FORMULAS = {
    "quadratics": [
        {"name": "Standard Form", "formula": "ax² + bx + c = 0", "notes": "a ≠ 0"},
        {"name": "Quadratic Formula", "formula": "x = [-b ± √(b² - 4ac)] / 2a", "notes": "Solves ax² + bx + c = 0"},
        {"name": "Discriminant", "formula": "Δ = b² - 4ac", "notes": "Δ > 0: 2 real roots, Δ = 0: 1 real root, Δ < 0: no real roots"},
        {"name": "Sum of Roots", "formula": "α + β = -b / a", "notes": "For ax² + bx + c = 0"},
        {"name": "Product of Roots", "formula": "αβ = c / a", "notes": "For ax² + bx + c = 0"},
        {"name": "Vertex Form", "formula": "y = a(x - h)² + k", "notes": "Vertex at (h, k)"},
        {"name": "Vertex x-coord", "formula": "h = -b / 2a", "notes": "Axis of symmetry"},
        {"name": "Vertex y-coord", "formula": "k = f(h) = c - b²/4a", "notes": "Max/min value"},
        {"name": "Factored Form", "formula": "y = a(x - p)(x - q)", "notes": "Roots at x = p, x = q"},
        {"name": "Completing Square", "formula": "x² + bx = (x + b/2)² - (b/2)²", "notes": "Half the coefficient, square it"},
    ],
    "forces": [
        {"name": "Newton's 2nd Law", "formula": "F = ma", "notes": "Force = mass × acceleration"},
        {"name": "Weight", "formula": "W = mg", "notes": "Weight = mass × gravitational field (g ≈ 9.81 m/s²)"},
        {"name": "Friction", "formula": "F_f = μN", "notes": "μ = coefficient of friction, N = normal force"},
        {"name": "Static Friction (max)", "formula": "F_s(max) = μ_s N", "notes": "μ_s = coefficient of static friction"},
        {"name": "Kinetic Friction", "formula": "F_k = μ_k N", "notes": "μ_k = coefficient of kinetic friction (μ_k < μ_s)"},
        {"name": "Hooke's Law", "formula": "F = -kx", "notes": "k = spring constant, x = displacement"},
        {"name": "Spring Potential Energy", "formula": "E_e = ½kx²", "notes": "Elastic potential energy stored"},
        {"name": "Pressure", "formula": "P = F / A", "notes": "Pressure = Force / Area"},
        {"name": "Density", "formula": "ρ = m / V", "notes": "Density = mass / volume"},
        {"name": "Buoyancy", "formula": "F_b = ρVg", "notes": "Archimedes' principle"},
        {"name": "Net Force", "formula": "F_net = ΣF", "notes": "Vector sum of all forces"},
        {"name": "Tension (pulley)", "formula": "T = m(g ± a)", "notes": "+ for upward acceleration"},
    ],
    "moments": [
        {"name": "Moment / Torque", "formula": "M = F × d", "notes": "Moment = Force × perpendicular distance from pivot"},
        {"name": "Principle of Moments", "formula": "ΣM_cw = ΣM_ccw", "notes": "For equilibrium: clockwise = anticlockwise"},
        {"name": "Couple", "formula": "C = F × d", "notes": "Two equal opposite forces, d = distance between them"},
        {"name": "Torque (vector)", "formula": "τ = r × F", "notes": "Cross product of position and force vectors"},
        {"name": "Angular Force from Torque", "formula": "τ = Iα", "notes": "τ = torque, I = moment of inertia, α = angular accel"},
        {"name": "Center of Mass", "formula": "x_cm = Σmx / Σm", "notes": "Weighted average position of mass"},
        {"name": "Leverage", "formula": "F_out × d_out = F_in × d_in", "notes": "Work input = Work output (ideal)"},
        {"name": "Moment of Inertia (point)", "formula": "I = mr²", "notes": "Point mass at distance r from axis"},
    ],
}

def load():
    if not os.path.exists(DATA):
        os.makedirs(os.path.dirname(DATA), exist_ok=True)
        os.makedirs(BACKUP, exist_ok=True)
        save(DEFAULT_FORMULAS.copy())
    with open(DATA) as f:
        return json.load(f)

def save(data):
    os.makedirs(os.path.dirname(DATA), exist_ok=True)
    with open(DATA, 'w') as f:
        json.dump(data, f, indent=2)
    # backup
    os.makedirs(BACKUP, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    with open(f"{BACKUP}/formulas_{ts}.json", 'w') as f:
        json.dump(data, f)
    # keep last 10
    backups = sorted([f for f in os.listdir(BACKUP) if f.startswith("formulas_")])
    for old in backups[:-10]:
        os.remove(os.path.join(BACKUP, old))

def add(subject, name, formula, notes=""):
    data = load()
    if subject not in data:
        data[subject] = []
    # check duplicate
    for f in data[subject]:
        if f["name"].lower() == name.lower():
            return f"⚠️ `{name}` already exists in **{subject}**. Use `update` instead."
    data[subject].append({"name": name, "formula": formula, "notes": notes or ""})
    save(data)
    return f"✅ Added `{name}` to **{subject}**"

def remove(subject, name):
    data = load()
    if subject not in data:
        return f"❌ Subject **{subject}** not found."
    before = len(data[subject])
    data[subject] = [f for f in data[subject] if f["name"].lower() != name.lower()]
    if len(data[subject]) == before:
        return f"❌ `{name}` not found in **{subject}**."
    save(data)
    return f"🗑️ Removed `{name}` from **{subject}**"

def list_subjects():
    data = load()
    subs = list(data.keys())
    if not subs:
        return "📋 No formulas saved yet."
    return "📋 **Subjects:**\n" + "\n".join(f"  • **{s}** ({len(data[s])} formulas)" for s in sorted(subs))

def list_formulas(subject):
    data = load()
    if subject not in data:
        return f"❌ Subject **{subject}** not found."
    forms = data[subject]
    if not forms:
        return f"📋 No formulas in **{subject}**."
    lines = [f"📋 **{subject.title()}** formulas:"]
    for i, f in enumerate(forms, 1):
        lines.append(f"\n`{i}.` **{f['name']}**")
        lines.append(f"   `{f['formula']}`")
        if f.get("notes"):
            lines.append(f"   _{f['notes']}_")
    return "\n".join(lines)

def get(subject, name):
    data = load()
    if subject not in data:
        return f"❌ Subject **{subject}** not found."
    for f in data[subject]:
        if f["name"].lower() == name.lower():
            return f"**{f['name']}** ({subject})\n`{f['formula']}`\n_{f['notes']}_" if f.get("notes") else f"**{f['name']}** ({subject})\n`{f['formula']}`"
    # try partial match
    matches = [f for f in data[subject] if name.lower() in f["name"].lower()]
    if matches:
        lines = [f"Did you mean one of these in **{subject}**?:"]
        for m in matches:
            lines.append(f"  • `{m['name']}`")
        return "\n".join(lines)
    return f"❌ `{name}` not found in **{subject}**."

def search(query):
    data = load()
    q = query.lower()
    results = []
    for sub, forms in data.items():
        for f in forms:
            if q in f["name"].lower() or q in f["formula"].lower() or q in f.get("notes", "").lower():
                results.append((sub, f))
    if not results:
        return f"🔍 No results for `{query}`."
    lines = [f"🔍 Results for `{query}`:"]
    for sub, f in results:
        lines.append(f"\n  **{f['name']}** ({sub})")
        lines.append(f"  `{f['formula']}`")
    return "\n".join(lines)

def help_text():
    return (
        "📐 **Formula commands:**\n"
        "  `formula list` — List all subjects\n"
        "  `formula list <subject>` — Show formulas in a subject\n"
        "  `formula get <subject> <name>` — Get a specific formula\n"
        "  `formula search <query>` — Search all formulas\n"
        "  `formula add <subject> <name> = <formula>` — Add a formula\n"
        "  `formula add <subject> <name> = <formula> // notes` — With notes\n"
        "  `formula remove <subject> <name>` — Remove a formula\n\n"
        "**Pre-loaded:** quadratics, forces, moments"
    )

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(help_text())
        sys.exit(0)
    
    action = sys.argv[1]
    
    if action == "add":
        if len(sys.argv) < 5 or "=" not in " ".join(sys.argv[2:]):
            print("Usage: formula add <subject> <name> = <formula> [// notes]")
            sys.exit(1)
        rest = " ".join(sys.argv[2:])
        eq_pos = rest.index("=")
        subject_name = rest[:eq_pos].strip()
        formula_part = rest[eq_pos+1:].strip()
        # Split subject and name from the left part
        parts = subject_name.split(None, 1)
        if len(parts) < 2:
            print("Usage: formula add <subject> <name> = <formula>")
            sys.exit(1)
        subject = parts[0]
        name = parts[1]
        notes = ""
        if " // " in formula_part:
            formula_part, notes = formula_part.split(" // ", 1)
        print(add(subject, name, formula_part.strip(), notes.strip()))
    
    elif action == "remove":
        if len(sys.argv) < 4:
            print("Usage: formula remove <subject> <name>")
            sys.exit(1)
        print(remove(sys.argv[2], " ".join(sys.argv[3:])))
    
    elif action == "list":
        if len(sys.argv) >= 3:
            print(list_formulas(" ".join(sys.argv[2:])))
        else:
            print(list_subjects())
    
    elif action == "get":
        if len(sys.argv) < 4:
            print("Usage: formula get <subject> <name>")
            sys.exit(1)
        print(get(" ".join(sys.argv[2:-1]), sys.argv[-1]))
    
    elif action == "search":
        if len(sys.argv) < 3:
            print("Usage: formula search <query>")
            sys.exit(1)
        print(search(" ".join(sys.argv[2:])))
    
    else:
        print(help_text())
