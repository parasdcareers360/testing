# 07 — Low-Level Design (LLD)

> **Type:** Study notes (index)

Object-oriented design at the class level — "design a parking lot / elevator / rate limiter"
prompts graded on class boundaries, extensibility, and whether your design survives a live
follow-up requirement. This is a different skill from high-level system design (scale, boxes and
arrows, distributed trade-offs), which lives in [`../06_system_design/`](../06_system_design/) —
interviewers usually run them as separate rounds, and conflating them (e.g. reaching for
"add a cache layer" when the interviewer wants a `FeeStrategy` interface) is itself a signal you
haven't done LLD before.

## Fundamentals

Read these first — every exercise below reuses them instead of re-explaining the concept inline.

| # | Topic | File |
|---|---|---|
| 1 | OOP design (encapsulation, composition vs. inheritance in practice) | [`fundamentals/oop_design.md`](fundamentals/oop_design.md) |
| 2 | SOLID principles — how violations surface mid-interview | [`fundamentals/solid_principles.md`](fundamentals/solid_principles.md) |
| 3 | Design patterns for LLD interviews (the ~6 that actually recur) | [`fundamentals/design_patterns.md`](fundamentals/design_patterns.md) |
| 4 | UML class diagrams with Mermaid | [`fundamentals/uml_class_diagrams_mermaid.md`](fundamentals/uml_class_diagrams_mermaid.md) |
| 5 | Thread safety & concurrency in a design | [`fundamentals/thread_safety_and_concurrency.md`](fundamentals/thread_safety_and_concurrency.md) |
| 6 | Designing for extensibility ("now add X") | [`fundamentals/extensible_code_design.md`](fundamentals/extensible_code_design.md) |

## Exercises

Each is a complete worked design — requirements → class model → design decisions → trade-offs →
what's in/out of scope for a 3-YOE candidate — not just a prompt. Roughly ordered easiest to
hardest.

| # | Exercise | File | Core pattern(s) |
|---|---|---|---|
| 1 | Parking lot | [`exercises/parking_lot.md`](exercises/parking_lot.md) | Strategy |
| 2 | Elevator system | [`exercises/elevator.md`](exercises/elevator.md) | State |
| 3 | Library management system | [`exercises/library_management.md`](exercises/library_management.md) | Strategy, Observer |
| 4 | Splitwise (expense-sharing) | [`exercises/splitwise.md`](exercises/splitwise.md) | Strategy |
| 5 | In-memory LRU/LFU cache | [`exercises/cache.md`](exercises/cache.md) | Strategy |
| 6 | Rate limiter (as a class, not a distributed system) | [`exercises/rate_limiter.md`](exercises/rate_limiter.md) | Strategy |
| 7 | Notification service | [`exercises/notification_service.md`](exercises/notification_service.md) | Observer, Decorator, Factory |
| 8 | Payment workflow | [`exercises/payment_workflow.md`](exercises/payment_workflow.md) | State, Strategy, ISP |

## How to work through an LLD exercise

1. **Read the relevant fundamentals first** — every exercise names which patterns/principles it
   leans on in the table above.
2. **Attempt it cold, on paper or a whiteboard tool, in 30-40 minutes.** Write the requirements
   list, sketch the class diagram, and write 1-2 key methods in Python before reading the file's
   answer — the exercise is in producing the design under time pressure, not recognizing a correct
   one when you read it.
3. **Then have someone (or your own second pass) say "now add X"** — every exercise file includes
   at least one such follow-up. If your first draft needs a rewrite to absorb it, that's the
   signal to revisit [`fundamentals/extensible_code_design.md`](fundamentals/extensible_code_design.md).
4. **Compare against the file's worked answer**, not to find "the" correct design — LLD rarely has
   one — but to check whether your class boundaries and extension points are defensible even if
   they differ from the example.

Related: [DSA patterns](../02_dsa_and_coding/) for the coding round, [system design](../06_system_design/)
for the HLD round — a FAANG/MAANG loop for a 3-YOE backend candidate typically includes one of
each plus this LLD round.
