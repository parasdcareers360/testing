# Designing for Extensibility ("Now Add X")

> **Type:** Study notes

Every LLD interview follows the same choreography: you design something that satisfies the stated
requirements, then the interviewer adds one. This file is the general version of the pattern that
[`solid_principles.md`](solid_principles.md) covers principle-by-principle — here it's about the
*habit* of designing extension points before you're asked to, not after.

## Why interviewers ask this

A design that only works for the requirements you were told about first is indistinguishable, on
the first pass, from a design that anticipated change — the "now add X" follow-up is how an
interviewer tells them apart in 5 minutes instead of guessing. It's also the most realistic part of
the interview: production requirements always grow, and the candidates who struggle here are
usually the ones who also struggle with this in real codebases — over-fitting the first version of
a class to the first version of the requirements.

## The habit: identify the "spine" vs. the "variation"

Before writing a class, separate what's structurally stable (the *spine* — always true for this
domain) from what's likely to vary (the *variation* — new types, new rules, new channels). Put the
spine in a concrete class; put the variation behind an interface.

| Domain | Spine (stable) | Variation (likely to grow) |
|---|---|---|
| Parking lot | A vehicle occupies a spot for a duration, then pays | *How* the fee is calculated |
| Notification service | A message goes out to a recipient | *Which channel(s)* it goes out on |
| Payment workflow | An order transitions through states | *Which* payment method processed it |
| Rate limiter | Requests are counted against a limit | *Which algorithm* (fixed window, sliding window, token bucket) does the counting |

This table itself is a fast thing to sketch in the first 2 minutes of any LLD interview — it
directly predicts which class should be a `Protocol`/interface with multiple implementations.

## The concrete move: name the seam before you're asked

Don't wait for "now add X" to introduce an interface — introduce it for the *one* piece of the
domain most likely to vary, and say why, before the interviewer asks:

```python
# Weak: fee logic is inline, "now add a new pricing rule" forces editing ParkingLot
class ParkingLot:
    def unpark(self, ticket) -> float:
        hours = ticket.duration_hours()
        if self.vehicle_type == "car":
            return hours * 2.0
        return hours * 1.0

# Strong: the variation is a seam from the start
from typing import Protocol

class FeeStrategy(Protocol):
    def calculate(self, ticket) -> float: ...

class ParkingLot:
    def __init__(self, fee_strategy: FeeStrategy):
        self.fee_strategy = fee_strategy

    def unpark(self, ticket) -> float:
        return self.fee_strategy.calculate(ticket)
```
The second version costs one extra class up front and pays for itself the moment "now add a
weekend flat rate" lands — you write `WeekendFlatFeeStrategy` and change nothing else.

## The trap: over-applying this and building speculative abstraction

The opposite failure is just as visible to an interviewer: wrapping *everything* in an interface
"just in case," including things with no realistic variation (e.g. a `VehicleFactory` for a domain
with exactly two hardcoded vehicle types and no stated plan to add more). This reads as not
understanding *why* you'd add a seam, just pattern-matching "interfaces are good." The test to say
out loud: *"is this the piece of the domain the interviewer is likely to grow, or am I guessing?"*
Use the table above — spine stays concrete, variation gets the interface, and only the variation.

## Composition over inheritance, applied to extensibility specifically

Inheritance hierarchies resist unplanned extension because a new requirement often doesn't fit
cleanly into an existing branch (see the LSP section of
[`solid_principles.md`](solid_principles.md#lsp-the-interviewers-new-subtype-breaks-an-assumption-your-base-class-made)).
Composition — injecting a strategy/dependency instead of subclassing to override behavior — is
almost always the safer default in an interview, because it keeps the class doing the extending
free to combine with future variations without a combinatorial explosion of subclasses:

```python
# Inheritance: N notification channels x M optional behaviors (logging, retry) = up to N*M subclasses
class EmailNotifierWithLoggingAndRetry(EmailNotifier): ...

# Composition: N + M classes, combined freely at construction time
notifier = RetryNotifier(LoggingNotifier(EmailNotifier()))
```
Full treatment of Decorator (used above) is in
[`design_patterns.md`](design_patterns.md#decorator--extensible-behavior).

## A checklist to run silently before you finish any LLD design

1. **Which part of this domain did the prompt hint might grow?** (multiple vehicle types, multiple
   payment methods, multiple notification channels — these are usually explicit or one small
   inference away).
2. **Does that part sit behind an interface, or is it a branch/`if-elif` inside a concrete class?**
   If it's a branch, that's your one pre-emptive fix before the interviewer asks.
3. **Am I adding an interface anywhere the prompt gives no signal of variation?** If yes, cut it —
   unjustified abstraction reads as worse than a clean concrete class.
4. **If asked "now add X" right now, which classes would I edit vs. which would I add?** Editing
   existing, already-designed classes is the answer that costs you interview time; adding new ones
   that implement an existing interface is the answer that doesn't.

## Interview questions

**Q: How do you decide what to make extensible up front vs. what to leave concrete?**
A: Identify the "spine" of the domain (structurally stable behavior) vs. the "variation" (what's
explicitly stated or strongly implied to have multiple current or future forms — pricing rules,
notification channels, payment methods) and only put the variation behind an interface. Making
everything extensible is itself a mistake — it signals pattern-matching over understanding.

**Q: The interviewer says "now support Apple Pay" on a payment workflow you designed with a single
concrete `CreditCardProcessor` class called directly inside `OrderService`. What's the fix, and
what would you do differently starting over?**
A: Fix: extract a `PaymentProcessor` interface, make `CreditCardProcessor` one implementation,
inject it into `OrderService` instead of hardcoding it. Starting over: recognize "payment method" as
a variation point from the prompt (payment methods almost always multiply) and design the interface
from the first draft instead of waiting for the follow-up.

**Q: What's the risk of over-applying this advice?**
A: Speculative interfaces for parts of the domain with no real variation signal — it adds
indirection an interviewer has to read through for no payoff, and suggests you're following a
rule rather than reasoning about *this* design.

## Exercises

1. Take [`../exercises/notification_service.md`](../exercises/notification_service.md)'s design
   and identify, before reading its "extensibility" section, which one class you'd make an
   interface first — then check your answer against the file.
2. Pick any exercise in this module you've already completed and ask yourself the 4-item checklist
   above against your own draft, not the worked answer — note anywhere you built an unjustified
   abstraction.
