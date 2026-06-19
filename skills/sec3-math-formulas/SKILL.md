---
name: "sec3-math-formulas"
description: "Sec 3 Math formula lookup for Discord — given a topic, returns simplified formulas from the syllabus."
---

# Sec 3 Math Formulas

A Skill that looks up and returns simplified formulas for Secondary 3 Mathematics topics. Trigger it in any chat (Discord, WebChat, etc.) and it will give you a clean, readable list of formulas for the topic you specify.

## Topics Covered

| Topic | Key Formulas |
|-------|-------------|
| **Indices** | `a^m × a^n = a^(m+n)`, `a^m ÷ a^n = a^(m-n)`, `(a^m)^n = a^(mn)`, `a^0 = 1`, `a^(-n) = 1/a^n`, `a^(1/n) = ⁿ√a` |
| **Surds** | `√(ab) = √a × √b`, `√(a/b) = √a / √b`, `(√a + √b)(√a - √b) = a - b`, `(√a + √b)² = a + b + 2√(ab)` |
| **Polynomials** | `(a + b)² = a² + 2ab + b²`, `(a - b)² = a² - 2ab + b²`, `(a + b)(a - b) = a² - b²`, `(a + b)³ = a³ + 3a²b + 3ab² + b³`, factor theorem, remainder theorem |
| **Quadratic Equations** | `ax² + bx + c = 0 → x = [-b ± √(b² - 4ac)] / 2a`, `discriminant Δ = b² - 4ac`, sum of roots = `-b/a`, product = `c/a` |
| **Quadratic Functions** | `y = a(x - h)² + k` (vertex form), vertex = `(h, k)`, axis of symmetry `x = h`, completing the square |
| **Linear Inequalities** | Solve like equations — flip sign when × or ÷ by negative, represent on number line |
| **Coordinate Geometry** | gradient `m = (y₂ - y₁)/(x₂ - x₁)`, `y = mx + c`, `y - y₁ = m(x - x₁)`, distance `d = √[(x₂ - x₁)² + (y₂ - y₁)²]`, midpoint `((x₁+x₂)/2, (y₁+y₂)/2)` |
| **Simultaneous Equations** | Substitution, elimination, graphical — also with quadratics |
| **Trigonometry** | `sin θ = opp/hyp`, `cos θ = adj/hyp`, `tan θ = opp/adj`, `sin²θ + cos²θ = 1`, `tan θ = sinθ/cosθ`, sine rule, cosine rule, angle of elevation/depression |
| **Mensuration** | cylinder volume `πr²h`, cone `⅓πr²h`, sphere `⁴⁄₃πr³`, arc length `s = rθ`, sector area `½r²θ` (θ in radians) |
| **Congruence & Similarity** | SSS, SAS, ASA, RHS for congruence. Ratio of areas = `k²`, ratio of volumes = `k³` |
| **Vectors in 2D** | `|v| = √(x² + y²)`, addition/subtraction, scalar multiplication, position vectors, parallel ↔ scalar multiple |
| **Probability** | `P(A) = n(A)/n(S)`, `P(A∪B) = P(A) + P(B) - P(A∩B)`, `P(A') = 1 - P(A)`, tree diagrams |
| **Statistics** | mean `x̄ = Σx/n`, median, mode, standard deviation `σ = √[Σ(x-x̄)²/n]`, histograms, box plots |
| **Sets** | union `∪`, intersection `∩`, complement `'`, subset `⊆`, Venn diagrams: `n(A∪B) = n(A) + n(B) - n(A∩B)` |

## Usage

In any chat where the agent is present, say or mention:

> @Group14Bot formulas for [topic]

For example:
- "formulas for trigonometry"
- "formulas for quadratic equations"
- "formulas for indices"
- "formulas for coordinate geometry"

The agent will reply with a formatted message listing the key formulas for that topic.

You can also ask for multiple topics:
- "formulas for quadratic and inequalities"
- "give me mensuration formulas"
- "list all probability formulas"

## File Structure

```
skills/sec3-math-formulas/
├── SKILL.md          # This file — skill definition
└── formulas.json     # Structured JSON with all formulas for lookup
```

## Formula Data Format (`formulas.json`)

```json
{
  "indices": {
    "display": "Indices",
    "emoji": "🔢",
    "formulas": [
      { "name": "Multiplication", "formula": "a^m × a^n = a^(m+n)" },
      { "name": "Division", "formula": "a^m ÷ a^n = a^(m-n)" },
      { "name": "Power of a power", "formula": "(a^m)^n = a^(mn)" },
      { "name": "Zero exponent", "formula": "a^0 = 1" },
      { "name": "Negative exponent", "formula": "a^(-n) = 1/a^n" },
      { "name": "Fractional exponent", "formula": "a^(1/n) = ⁿ√a" }
    ]
  }
}
```

## Extending

To add more topics or update formulas:
1. Edit `formulas.json` with new entries
2. Add the topic to this SKILL.md's table if desired
