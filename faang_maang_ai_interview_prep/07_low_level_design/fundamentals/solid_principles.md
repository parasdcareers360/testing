# SOLID Principles — the LLD Interview Trap

> **Type:** Study notes

This file assumes you already know what each SOLID letter stands for — full definitions and
language-level examples live in
[`10_oop_solid_composition_vs_inheritance.md`](../../03_python_core_and_advanced/10_oop_solid_composition_vs_inheritance.md).
This file is narrower: it's about **how SOLID violations actually surface in an LLD interview**,
which is almost never "spot the violation in this static code" — it's "your design just got a new
requirement, and now the violation is a live problem you have to fix out loud."

## Why interviewers ask this

Nobody fails an LLD interview by mislabeling which letter is which. Candidates fail because their
first draft has a SOLID violation baked in, the interviewer says "now add feature X" — which is
standard interview choreography, not a trick — and the candidate either doesn't notice their design
just broke, or notices but doesn't know how to refactor live without a full rewrite. Interviewers
use "now add X" specifically because it's the cheapest way to test whether your design has real
extension points or just happens to work for the requirements you were told about first.

## The classic mid-interview trap, principle by principle

### SRP: the interviewer adds a second reason to change
You design `ParkingLot` with `park()`, `unpark()`, `calculate_fee()`, `send_receipt_email()`. It
works. Then: "now add SMS receipts alongside email." If `send_receipt_email()` is inline in
`ParkingLot`, you're editing a class that also owns spot allocation to add a notification channel —
two unrelated reasons to change, now visibly tangled. The fix to say out loud: extract a
`ReceiptNotifier` interface; `ParkingLot` calls `notifier.send(receipt)` without knowing
if that's email, SMS, or both.

### OCP: the interviewer adds a new variant of something you branched on
You write `calculate_fee()` with `if vehicle_type == "car": ... elif "bike": ...`. Then: "now add a
flat monthly-subscriber rate." Every branching design forces you back into the same function under
time pressure. The fix: a `FeeStrategy` per vehicle/plan type, injected into `ParkingLot` — see
[design_patterns.md](design_patterns.md) (Strategy) and the worked before/after in
[extensible_code_design.md](extensible_code_design.md).

```python
# What breaks under "now add a new type":
def calculate_fee(vehicle_type: str, hours: int) -> float:
    if vehicle_type == "car":
        return hours * 2.0
    elif vehicle_type == "bike":
        return hours * 1.0
    # every new vehicle/plan type means editing this function again, live, in the interview

# What survives it:
class FeeStrategy(Protocol):
    def calculate(self, hours: int) -> float: ...

class CarFeeStrategy:
    def calculate(self, hours: int) -> float: return hours * 2.0

class MonthlySubscriberFeeStrategy:
    def calculate(self, hours: int) -> float: return 0.0  # flat rate, billed separately
```

### LSP: the interviewer's new subtype breaks an assumption your base class made
You model `Spot` with a `park(vehicle)` that assumes any `Vehicle` fits. Then: "now add
motorcycle-only compact spots and oversized-vehicle spots." If `CompactSpot.park()` has to silently
reject cars by raising where `Spot.park()` never did, callers written against `Spot` now need to
know which subtype they have — that's an LSP break appearing live. The fix: make spot-vehicle
compatibility an explicit check (`spot.can_fit(vehicle)`) callers use before calling `park()`,
rather than a hidden precondition that only some subtypes enforce.

### ISP: the interviewer adds a capability only some implementers need
You define one `PaymentMethod` interface with `charge()`, `refund()`, `save_for_later()`. Then:
"now add Cash on Delivery as a payment method." COD can't meaningfully implement `save_for_later()`
or arguably `refund()` the same way a card does — you either stub methods that raise
`NotImplementedError` (a code smell interviewers notice immediately) or split the interface. The
fix: separate `Chargeable`, `Refundable`, `Storable` so COD only implements `Chargeable`.

### DIP: the interviewer asks how you'd test or swap a piece
You wire `OrderService.__init__` to construct a concrete `SqlOrderRepository` directly. Then: "how
would you unit test this without a database?" or "now support an in-memory cache-backed repository
for hot orders." If the concrete class is constructed inside `__init__`, both questions require
editing `OrderService`. The fix: accept an abstraction (`OrderRepository` protocol) through the
constructor — this is exactly the DI pattern from Django/DRF fixtures, applied at the design stage
before code exists.

## How to signal this thinking in the interview

Say the failure mode before it happens: *"I'll model fee calculation as a strategy object rather
than branching on vehicle type, since pricing rules are the part most likely to grow."* That single
sentence tells the interviewer you're aware of OCP without naming-dropping it, and it pre-empts the
"now add a new type" follow-up — sometimes the interviewer skips straight to a harder follow-up
because you've already shown the easy one won't trip you up.

## Interview questions

**Q: The interviewer says "now support refunds" on a payment system you designed with one
`PaymentMethod.charge()` method. What's the SOLID-flavored way to extend it?**
A: Check whether every payment type can meaningfully support refunds (probably not — e.g. cash).
Add a separate `Refundable` interface (ISP) rather than adding `refund()` to the base interface and
stubbing it with `raise NotImplementedError` for methods that can't support it.

**Q: How is "now add X" different from just testing whether you know more code?**
A: It's testing whether your *existing* classes need to change to accommodate X. A design with good
seams absorbs X as a new class; a design with SOLID violations requires editing tested code live —
the interviewer is timing the size of your diff, not your typing speed.

**Q: Which SOLID violation is most likely to be invisible until a mid-interview follow-up exposes
it?**
A: LSP, usually — an inheritance hierarchy that looks fine for the first 2-3 subtypes often hides an
assumption (like "any vehicle fits any spot") that only a later, more specific subtype (compact
spot, oversized spot) breaks.

## Exercises

1. Take the `CarFeeStrategy`/branching example above, implement the full `FeeStrategy` protocol
   version, then add a `WeekendFlatFeeStrategy` without touching `ParkingLot` or the existing
   strategy classes.
2. Design a `NotificationService` with a single `send()` method for email only, then extend it to
   support SMS and push notifications while keeping `NotificationService` itself unmodified — note
   which SOLID letter each step of the exercise exercises.
