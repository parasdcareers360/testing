# OOP, SOLID, and Composition vs. Inheritance

> **Type:** Study notes

## Why interviewers ask this

Every mid-to-senior backend interview eventually asks "how would you design this class structure?"
— and SOLID gives interviewers a vocabulary to probe whether you can reason about maintainability,
not just get something working. Liskov Substitution is the one candidates get wrong most often (it
sounds abstract until you see the classic square/rectangle example), and "composition over
inheritance" is the single most common piece of design feedback in real code review — knowing when
to reach for each is a strong signal of production experience. See also
[SOLID principles](../07_low_level_design/fundamentals/solid_principles.md) and
[design patterns](../07_low_level_design/fundamentals/design_patterns.md) for design-pattern-level
applications of these ideas.

## The 4 OOP pillars, briefly

- **Encapsulation** — bundling data and the methods that operate on it, hiding internal state
  behind a public interface (Python convention: `_protected`, `__name_mangled`, properties).
- **Abstraction** — exposing *what* an object does, hiding *how* (an ORM's `.save()` hides the SQL).
- **Inheritance** — a class reuses/extends another class's behavior (`class Manager(Employee)`).
- **Polymorphism** — different classes respond to the same interface/method call in their own way
  (`shape.area()` behaves differently for `Circle` vs. `Square`, no `if isinstance` needed).

## SOLID, each with a short example

### S — Single Responsibility Principle
A class should have one reason to change.
```python
# Violates SRP: mixes DB access, business rules, and email formatting
class Order:
    def save(self): ...
    def calculate_total(self): ...
    def send_confirmation_email(self): ...

# Better: split by responsibility
class Order:
    def calculate_total(self): ...

class OrderRepository:
    def save(self, order: Order): ...

class OrderNotifier:
    def send_confirmation(self, order: Order): ...
```
If a change to email templates forces you to touch the same class as a change to pricing rules,
you've likely violated SRP.

### O — Open/Closed Principle
Open for extension, closed for modification — add new behavior without editing existing, tested
code.
```python
# Violates OCP: every new discount type means editing this function
def apply_discount(order, discount_type):
    if discount_type == "percentage":
        ...
    elif discount_type == "flat":
        ...
    # adding "bogo" means editing this function again

# Better: polymorphism instead of branching
class DiscountStrategy(Protocol):
    def apply(self, total: float) -> float: ...

class PercentageDiscount:
    def __init__(self, pct: float): self.pct = pct
    def apply(self, total: float) -> float: return total * (1 - self.pct)

class FlatDiscount:
    def __init__(self, amount: float): self.amount = amount
    def apply(self, total: float) -> float: return max(0, total - self.amount)

def apply_discount(order, strategy: DiscountStrategy) -> float:
    return strategy.apply(order.total)
```
Adding `BogoDiscount` now means writing a new class, not editing `apply_discount`.

### L — Liskov Substitution Principle
Subtypes must be substitutable for their base type without breaking correctness — the classic
trap:
```python
class Rectangle:
    def __init__(self, w: float, h: float):
        self.w, self.h = w, h
    def set_width(self, w): self.w = w
    def set_height(self, h): self.h = h
    def area(self): return self.w * self.h

class Square(Rectangle):
    def set_width(self, w):
        self.w = self.h = w   # forced, to keep it a square
    def set_height(self, h):
        self.w = self.h = h

def resize_and_check(rect: Rectangle):
    rect.set_width(4)
    rect.set_height(5)
    assert rect.area() == 20     # PASSES for Rectangle, FAILS for Square (area == 25)
```
`Square` is a `Rectangle` mathematically, but not behaviorally — code written correctly against
`Rectangle`'s contract breaks when given a `Square`. This means `Square` should **not** inherit from
`Rectangle`; a shared `Shape` interface (or no inheritance relationship at all) is the fix. The
general lesson: inheritance should model "is substitutable for," not just "is conceptually a kind
of."

### I — Interface Segregation Principle
Don't force a class to implement methods it doesn't need.
```python
# Violates ISP: a read-only repository is forced to implement write methods
class Repository(Protocol):
    def get(self, id): ...
    def save(self, obj): ...
    def delete(self, id): ...

# Better: split into focused interfaces
class ReadableRepository(Protocol):
    def get(self, id): ...

class WritableRepository(Protocol):
    def save(self, obj): ...
    def delete(self, id): ...

class CachedReadOnlyRepo:          # only implements what it actually needs
    def get(self, id): ...
```
A `ReportGenerator` that only ever reads data shouldn't be forced to stub out `save`/`delete` just
to satisfy one fat interface.

### D — Dependency Inversion Principle
Depend on abstractions, not concrete implementations — high-level modules shouldn't import
low-level details directly.
```python
# Violates DIP: OrderService is hard-wired to a specific email provider
class OrderService:
    def __init__(self):
        self.mailer = SendgridMailer()   # concrete dependency baked in

# Better: depend on an abstraction, inject the concrete implementation
class EmailSender(Protocol):
    def send(self, to: str, subject: str, body: str) -> None: ...

class OrderService:
    def __init__(self, mailer: EmailSender):
        self.mailer = mailer             # any EmailSender works — SendGrid, SES, a test double
```
This is exactly what Django/DRF dependency injection patterns and pytest fixtures rely on for
testability — swap `SendgridMailer` for a `FakeMailer` in tests without touching `OrderService`.

## Composition vs. inheritance

Inheritance models "is-a"; composition models "has-a"/"uses-a." A deep inheritance hierarchy looks
clean on a whiteboard but becomes brittle fast — a change to a base class ripples through every
subclass, and it forces a rigid one-parent-per-class taxonomy on a problem that's usually more
flexible than that.

```python
# Inheritance-heavy: brittle, and Python has no multiple-dispatch to save you
# when a payment processor needs to mix behaviors from two "families"
class PaymentProcessor:
    def process(self, amount): raise NotImplementedError

class CreditCardProcessor(PaymentProcessor):
    def process(self, amount): ...

class CreditCardProcessorWithFraudCheck(CreditCardProcessor):
    def process(self, amount): ...

class CreditCardProcessorWithFraudCheckAndRetry(CreditCardProcessorWithFraudCheck):
    def process(self, amount): ...   # this hierarchy only grows in one dimension
```

```python
# Composition: inject the pieces you need, combine freely
class PaymentGateway:
    def charge(self, amount: float) -> str: ...

class FraudCheck:
    def check(self, amount: float) -> bool: ...

class RetryPolicy:
    def should_retry(self, attempt: int, error: Exception) -> bool: ...

class PaymentProcessor:
    def __init__(
        self,
        gateway: PaymentGateway,
        fraud_check: FraudCheck | None = None,
        retry_policy: RetryPolicy | None = None,
    ):
        self.gateway = gateway
        self.fraud_check = fraud_check
        self.retry_policy = retry_policy

    def process(self, amount: float) -> str:
        if self.fraud_check and not self.fraud_check.check(amount):
            raise ValueError("flagged as fraudulent")
        return self.gateway.charge(amount)

# any combination, no new subclass needed:
processor = PaymentProcessor(StripeGateway(), fraud_check=BasicFraudCheck())
```

Any new combination (fraud check + no retry, retry + no fraud check, a completely new gateway) is
just a different set of constructor arguments — no new class in a hierarchy required. The rule of
thumb to say out loud in an interview: **"favor composition over inheritance"** doesn't mean never
use inheritance — small, shallow hierarchies (1-2 levels) that model genuine is-a relationships
with stable contracts (like a Django `Model` subclass) are fine. Reach for composition when
behavior needs to be mixed-and-matched, swapped at runtime, or when the hierarchy would otherwise
grow in more than one dimension (as above: processor type × fraud-check × retry policy).

## Interview questions

**Q: Give an example of violating Liskov Substitution that isn't the square/rectangle one.**
A: A `ReadOnlyList` that inherits from a mutable `List` interface but raises on `.append()` —
code written against `List` that calls `.append()` breaks when given a `ReadOnlyList`, even though
conceptually a read-only list "is a" list.

**Q: Why favor composition over inheritance in a payment-processing system specifically?**
A: Payment behavior varies along multiple independent axes (provider, fraud-check strategy, retry
policy, currency handling) — inheritance forces you to pick one axis as the "primary" hierarchy and
then explodes subclasses for every combination of the others; composition lets you inject each
concern independently and combine them freely, and lets you swap one piece (e.g. mock the gateway)
in tests without touching the rest.

**Q: How does Dependency Inversion relate to testability?**
A: If a class depends on a concrete implementation (e.g. `SendgridMailer` instantiated inside
`__init__`), you can't test it without hitting the real service or monkeypatching internals. If it
depends on an abstraction (`EmailSender` protocol) injected via the constructor, tests just pass a
fake/stub implementation — this is why DI-friendly code and testable code are usually the same
code.

**Q: Is a Django `Model` subclass a violation of "favor composition"?**
A: No — it's a shallow (usually 1-level), stable is-a relationship with a contract Django itself
defines and controls; the "favor composition" guidance is about *your* multi-axis business logic
hierarchies, not about framework base classes designed for single-level inheritance.

## Exercises

1. Take the `CreditCardProcessorWithFraudCheckAndRetry` inheritance chain above and identify what
   happens when you need a `PayPalProcessor` that also needs fraud-check-and-retry — how many
   classes do you end up writing under the inheritance approach vs. the composition approach?
2. Write a small `NotificationService` that composes an injected `Channel` (e.g. `EmailChannel`,
   `SMSChannel`, both implementing a `send(message: str) -> None` protocol) instead of subclassing
   per channel type, then add a `SlackChannel` without modifying `NotificationService`.
