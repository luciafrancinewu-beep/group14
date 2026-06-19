---
name: "math"
description: "Perform mathematical calculations, algebra, calculus, statistics, and numeric reasoning using Python."
---

# Math Skill

Perform mathematical computations accurately using Python and available tooling.

## When to Use

- Arithmetic / numeric calculations (anything beyond trivial mental math)
- Algebra (solving equations, systems, factoring, symbolic manipulation)
- Calculus (derivatives, integrals, limits, series)
- Linear algebra (vectors, matrices, eigenvalues, decompositions)
- Statistics and probability (descriptive stats, distributions, hypothesis tests, regression)
- Geometry and trigonometry
- Number theory (modular arithmetic, primes, GCD/LCM)
- Unit conversions, percentage calculations, financial math
- Graphing / visualization
- Verifying numeric claims or results

## How to Use

### 1. Use Python for Math

Use `exec` to run Python for any nontrivial calculation. Python's `math` module covers basic functions, and `sympy` handles symbolic math.

```python
import math, statistics, itertools, fractions, decimal, random
```

```python
import sympy as sp  # symbolic algebra, calculus, solving
```

### 2. Typical Patterns

**Arithmetic:**
```python
print(1234 * 5678)
print((15 + 3) / 4)
```

**Algebra (solve equation):**
```python
x = sp.symbols('x')
sol = sp.solve(sp.Eq(x**2 + 3*x - 10, 0), x)
print(sol)
```

**Calculus:**
```python
x = sp.symbols('x')
expr = x**3 * sp.sin(x)
deriv = sp.diff(expr, x)
integral = sp.integrate(expr, x)
limit = sp.limit(sp.sin(x)/x, x, 0)
print(deriv, integral, limit)
```

**Statistics:**
```python
data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
mean = statistics.mean(data)
stdev = statistics.stdev(data)
median = statistics.median(data)
print(mean, stdev, median)
```

**Linear Algebra:**
```python
import numpy as np
A = np.array([[1, 2], [3, 4]])
b = np.array([5, 6])
x = np.linalg.solve(A, b)
print(x)
```

### 3. Precision

- Use `decimal.Decimal` for financial/currency math that needs exact decimal representation.
- Use `fractions.Fraction` for exact rational arithmetic.
- Default float is fine for most scientific/statistical work.

### 4. Visualization

When a graph would help explain the answer, use `matplotlib` (if available) or a quick ASCII sketch, or generate an SVG via a sub-agent.

### 5. Units

- Always confirm units are consistent before calculating.
- Convert between units explicitly (e.g., meters to feet, Celsius to Fahrenheit).
- Use dimensional analysis when checking work.

## What Not to Do

- Don't do complex math in your head or with prompt-level arithmetic — use Python.
- Don't approximate when exact answers are possible (use fractions or symbolic forms).
- Don't skip intermediate steps when showing work is important — print each step.
- Don't forget to handle edge cases (division by zero, negative square roots, etc.).

## Examples

**Percentage of a number:**
```python
pct = 15
num = 200
result = num * (pct / 100)
print(result)  # 30.0
```

**Quadratic formula:**
```python
import cmath
a, b, c = 1, -3, 2
disc = b**2 - 4*a*c
x1 = (-b + cmath.sqrt(disc)) / (2*a)
x2 = (-b - cmath.sqrt(disc)) / (2*a)
print(x1, x2)  # (2+0j) (1+0j)
```

**System of equations:**
```python
x, y = sp.symbols('x y')
sol = sp.solve([sp.Eq(2*x + y, 10), sp.Eq(x - y, 2)], (x, y))
print(sol)  # {x: 4, y: 2}
```

**Integration:**
```python
x = sp.symbols('x')
def_int = sp.integrate(x**2, (x, 0, 1))
print(def_int)  # 1/3
```
