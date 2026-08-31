# OOP Application in LLD Interviews

> **Type:** Study notes

## Why interviewers ask this

Anyone who's read a book on classes can define `class`, `__init__`, and inheritance. What an LLD
interview actually tests is different: can you take a fuzzy word problem ("design a parking lot"),
carve it into classes with clear responsibilities, and keep that model coherent as the interviewer
pushes new requirements at you mid-conversation ("now add electric vehicle charging spots," "now
support hourly and monthly pricing"). That's a proxy for what you do every day turning a product
ticket into a Django app's models and services — the skill being graded is **managing complexity as
scope grows**, not "do you know what a class is."

## From word problem to classes: the process

1. **Extract nouns and verbs from the prompt.** Nouns become candidate classes (`ParkingLot`,
   `Spot`, `Vehicle`, `Ticket`); verbs become candidate methods (`park()`, `unpark()`,
   `calculate_fee()`).
2. **Assign one responsibility per class.** If a noun's verbs don't cohere around one job, split
   it — this is Single Responsibility Principle applied at the modeling stage, before you've
   written a line of code. See [SOLID principles](solid_principles.md).
3. **Decide relationships** between the classes you found (see below) — this is where most
   candidates lose points, because it's easy to default to inheritance for everything.
4. **Say your assumptions out loud** ("I'll assume one vehicle occupies exactly one spot, no
   motorcycles sharing a car spot — let me know if that's wrong") before coding. Interviewers
   deliberately leave gaps; naming them shows you think in edge cases without being told to.
5. **Code the skeleton first** — class names, key attributes, method signatures — before filling in
   logic bodies. A working skeleton that compiles conceptually is worth more than one fleshed-out
   class and four you never got to.

## has-a vs is-a vs uses-a

These three relationships are the actual vocabulary of step 3, and confusing them is the single
most common LLD mistake.

| Relationship | Meaning | Python shape | Example |
|---|---|---|---|
| **is-a** | Subtype substitutable for supertype | inheritance (`class B(A)`) | `CreditCardPayment(PaymentMethod)` |
| **has-a** (composition) | Owns a part; part's lifetime tied to owner | attribute holding another object, created/owned by `self` | `Car` has an `Engine` — engine is destroyed with the car |
| **has-a** (aggregation) | Holds a reference to a part with independent lifetime | attribute holding an object passed in, not owned | `ParkingLot` has `Spot`s that could theoretically be reused elsewhere |
| **uses-a** (dependency) | Calls another object's methods without storing it long-term | parameter passed into a method, not stored | `ParkingLot.park()` uses a `FeeCalculator` passed in per call |

```python
class Engine:
    def start(self) -> None: ...

class Car:
    def __init__(self):
        self.engine = Engine()          # has-a (composition) — Car creates and owns it

class ElectricCar(Car):                 # is-a — substitutable wherever Car is expected
    def charge(self) -> None: ...

class Mechanic:
    def repair(self, car: Car) -> None: # uses-a — Mechanic doesn't own the Car
        car.engine.start()
```

The interview-relevant test for is-a: **"is every instance of B always usable wherever an A is
expected?"** If a `Square` inherits `Rectangle` but breaks `set_width`/`set_height` independence,
it fails that test (see Liskov in [solid_principles.md](solid_principles.md)) — model it as has-a
or a shared interface instead. When in doubt, prefer has-a/uses-a: it's the safer default because
it doesn't lock you into a hierarchy you'll have to unwind when the interviewer adds a requirement
that breaks it.

## Why this matters beyond "do you know classes"

A junior answer hardcodes today's requirements. A strong answer leaves *seams* — places a new class
can be added without editing existing ones — because the interviewer's next move is almost always
"now add X." If your `ParkingLot.calculate_fee()` is an `if vehicle_type == "car": ... elif ==
"bike":` block, "now add monthly subscribers with a flat fee" forces you to edit tested code under
time pressure, live, while explaining yourself. If it's a `FeeStrategy` object handed to
`ParkingLot`, the new requirement is a new class that plugs in — see
[extensible_code_design.md](extensible_code_design.md) and
[design_patterns.md](design_patterns.md). This is exactly why interviewers frame LLD as
"requirements arrive incrementally" rather than handing you the full spec up front: they're timing
how expensive your first draft makes the second draft.

## Interview questions

**Q: How do you decide between inheritance and composition when modeling a word problem?**
A: Ask whether the "is-a" test holds for every instance, not just typical ones (see Liskov above).
If the subtype would ever need to violate or stub out part of the parent's contract, or if the
relationship needs to change at runtime, use composition. Default to composition when unsure —
it's cheaper to add an inheritance relationship later than to unwind one.

**Q: You designed `Vehicle` → `Car`, `Bike` with inheritance. The interviewer says "now vehicles can
switch between electric and gas mid-lifetime for a hybrid." What do you do?**
A: That's a sign the fuel/power behavior should be composed in (`self.engine: EngineType`), not
baked into the class hierarchy — a hybrid can't inherit from both `ElectricCar` and `GasCar` in a
single-inheritance-friendly design, so extract "engine behavior" into its own composed object.

**Q: Why not just make every class do everything and skip the modeling step?**
A: It works for the first requirement and collapses on the second — a `ParkingLot` god-class mixing
spot allocation, fee calculation, and payment processing means every new requirement touches the
same 300-line class, which is exactly the kind of change interviewers use to test whether your
design survives contact with a follow-up.

## Exercises

1. Take "design a library management system" and do steps 1-3 above on paper: list nouns/verbs,
   assign responsibilities, and classify every relationship you find as is-a/has-a/uses-a before
   writing any code.
2. Take your `ParkingLot` design (or sketch one) and have a friend (or yourself, later) add "support
   valet parking where an attendant moves cars between spots." Identify which of your classes had
   to change vs. which just got a new class alongside them — that ratio is a rough proxy for how
   good your original seams were.
