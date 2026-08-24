# Style Guide — design_patterns_python

Every file in this repo is one classic GoF design pattern, taught as a single self-contained,
directly-runnable `.py` tutorial. Follow this template exactly for consistency.

## File template

```python
"""
Design Patterns in Python — #<global_no>
<Pattern Name> (<Category> Pattern)

Intent
------
<One clear paragraph: what problem this pattern exists to solve, GoF-style. Written for a
learner, not copy-pasted jargon.>

Problem / Motivation
---------------------
<A short narrative describing a concrete situation where the problem shows up, tied directly
to the Anti-pattern code below — the reader should see the pain BEFORE seeing the fix.>

Structure
---------
<A short text description of the participants/roles and how they relate to each other, e.g.
"Subject holds a list of Observers and notifies them on state change; each ConcreteObserver
implements update()." No ASCII UML diagrams needed — plain prose naming the roles is enough.>

When to Use
-----------
- <2-4 concrete bullet points>

When NOT to Use
----------------
- <1-3 bullet points — every pattern has a cost (indirection, extra classes, complexity); name
  it honestly. E.g. "Don't reach for Visitor if you only have one operation and it's unlikely
  to grow — a simple method beats double-dispatch machinery.">

Related / Commonly Confused Patterns
--------------------------------------
- <1-3 bullet points, e.g. "Strategy vs State: same structure, different intent — State's
  transitions are driven by the object itself, Strategy's algorithm choice is driven by the
  client.">
"""


# ============================================================
# Anti-pattern: the naive way, and why it hurts
# ============================================================
# Real, runnable code showing the problem THIS pattern solves, without the pattern applied.
# Keep it short but genuine — not a strawman. Comment on specifically what goes wrong as the
# code grows (e.g. "adding a new shape means editing this if/elif chain in three places").
...


# ============================================================
# Implementation 1: Classic (OOP / GoF-style)
# ============================================================
# The textbook implementation using explicit classes/interfaces, matching how the pattern is
# usually taught in Java/C++ GoF material, translated idiomatically into Python (use ABCs from
# `abc` where the pattern calls for an interface).
...


# ============================================================
# Implementation 2: Pythonic idiom   (OMIT ENTIRELY if there's no genuinely distinct
# alternative — do not pad with a cosmetic rename of Implementation 1)
# ============================================================
# A second, idiomatic-Python way to achieve the same intent using first-class functions,
# closures, generators, decorators, dataclasses, or stdlib features. Explain in a comment WHY
# this is more idiomatic (fewer moving parts, leans on a language feature Java/C++ don't have).
...


# ============================================================
# Key Takeaways
# ============================================================
# - the core insight/trade-off this pattern teaches
# - a common misuse or misconception (e.g. over-applying it, confusing it with a lookalike)
# - 1-2 related patterns worth comparing against


if __name__ == "__main__":
    # A realistic, runnable demo — not a toy `foo`/`bar` example. Exercise BOTH
    # implementations if two exist, with printed output and/or assert statements that make it
    # obvious the pattern is actually doing its job (e.g. show the anti-pattern's rigidity
    # failing in a way the pattern's flexibility doesn't).
    ...
```

## Hard rules

1. **Every implementation must be real, correct, runnable code** — never a stub, never `pass`,
   never `# TODO`. If you cannot fully implement something correctly, don't include it.
2. **The Anti-pattern section is always required** — it's the motivating pain, and it's what
   makes "why does this pattern exist" concrete instead of abstract. It doesn't need to be
   long, but it must be real code, not a description.
3. **Implementation 2 (Pythonic idiom) is optional** — include it only when Python genuinely
   offers a distinct, idiomatic alternative achieving the same intent (most patterns do:
   Singleton via metaclass/module/decorator instead of a lazy-init classmethod; Factory Method
   via a dict-based registry instead of subclassing; Strategy via first-class functions instead
   of a class hierarchy; Iterator via a generator instead of an explicit `__iter__`/`__next__`
   class; Observer via a plain callback-list instead of an ABC hierarchy; Command via closures
   instead of Command objects; Template Method via a hook-function parameter instead of
   subclassing; Decorator (the pattern) contrasted explicitly with Python's `@decorator` syntax
   — a great teaching moment on how they're related but not the same thing). If there's no real
   second angle, skip Implementation 2 and say so in one line in the Intuition/Structure
   section rather than forcing a fake variant.
4. Use `abc.ABC` / `abc.abstractmethod` for "interface" roles in the Classic implementation
   where the pattern calls for one — that's the idiomatic Python way to express a GoF
   interface, not a style violation.
5. **Every file must execute cleanly**: after writing a file, run `python3 <path>` yourself and
   confirm exit code 0 with no unhandled exceptions or tracebacks. Fix the code (not the demo)
   if it fails.
6. Keep comments purposeful — explain the *why* of a design choice, not a line-by-line
   narration of what the code obviously does.
7. Filenames, numbering, and pattern order are fixed by `MANIFEST.md` — do not rename, skip,
   reorder, or invent extra patterns.
8. Demos should feel like small pieces of a real system (a notification system, a payment
   pipeline, a document exporter, a game entity, a UI widget toolkit) rather than
   `Animal`/`Shape` toy hierarchies wherever a more concrete domain fits naturally — this makes
   the "when would I actually reach for this" question answer itself.

## Reference example

See `01_creational/01_singleton.py` once it exists for the target tone, depth, and structure —
match its quality exactly.
