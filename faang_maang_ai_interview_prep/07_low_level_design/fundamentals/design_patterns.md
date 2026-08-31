# Design Patterns for LLD Interviews

> **Type:** Study notes

## Why interviewers ask this

LLD interviews reuse the same handful of GoF patterns over and over because most "design a system"
prompts (parking lot, elevator, rate limiter, notification service) reduce to a small set of
recurring shapes: pick an algorithm at runtime, notify subscribers of a change, create objects
without hardcoding their type, guarantee one shared instance, change behavior as an object's state
changes, or bolt on behavior without a new subclass per combination. Knowing the full 23-pattern GoF
catalogue isn't the point — recognizing which of these ~6 shapes a requirement matches, and
implementing it fast in Python, is.

## If the interviewer asks for X, consider pattern Y

| Interviewer says... | Pattern | Why |
|---|---|---|
| "different pricing/algorithm rules that can be swapped" | **Strategy** | Interchangeable algorithms behind one interface, chosen by the caller |
| "notify multiple parts of the system when something happens" | **Observer** | Subscribers register for events, publisher doesn't know who they are |
| "create objects but the exact type isn't known until runtime" | **Factory** | Centralizes object creation, callers depend on an interface not a constructor |
| "exactly one shared instance of this (config, connection pool, logger)" | **Singleton** | Controls instantiation so only one instance ever exists — see [thread safety](thread_safety_and_concurrency.md) for why naive versions break under concurrency |
| "behavior changes based on the object's current status/lifecycle" | **State** | Object delegates to a state object that can swap itself out |
| "add optional behavior/features without an explosion of subclasses" | **Decorator** | Wraps an object to add behavior, stackable, same interface as the original |

## Strategy — interchangeable algorithms

Context holds an algorithm object and delegates to it; new algorithms are new classes, not new
branches. Full treatment: [solid_principles.md](solid_principles.md) (OCP section) and
[oop_design.md](oop_design.md).

```python
class FeeStrategy(Protocol):
    def calculate(self, hours: int) -> float: ...

class HourlyFeeStrategy:
    def calculate(self, hours: int) -> float:
        return hours * 2.0

class ParkingSpot:
    def __init__(self, fee_strategy: FeeStrategy):
        self.fee_strategy = fee_strategy   # swappable at runtime
```

## Observer — event notification

A subject keeps a list of observers and calls a common method on all of them when its state
changes; the subject never needs to know what an observer does with the notification. Classic fit
for `notification_service.md` and any "multiple parts of the system react to one event" prompt.

```python
class Subject:
    def __init__(self):
        self._observers: list["Observer"] = []

    def subscribe(self, observer: "Observer") -> None:
        self._observers.append(observer)

    def notify(self, event: str) -> None:
        for obs in self._observers:
            obs.update(event)

class Observer(Protocol):
    def update(self, event: str) -> None: ...

class EmailObserver:
    def update(self, event: str) -> None:
        print(f"emailing about: {event}")
```

## Factory — flexible object creation

A dedicated method/class decides which concrete type to instantiate, so callers depend on an
interface (`Vehicle`) instead of hardcoding `Car()` / `Bike()` constructors everywhere.

```python
class Vehicle(Protocol):
    def wheel_count(self) -> int: ...

class Car:
    def wheel_count(self) -> int: return 4

class Bike:
    def wheel_count(self) -> int: return 2

def vehicle_factory(kind: str) -> Vehicle:
    return {"car": Car, "bike": Bike}[kind]()
```

The branching lives in exactly one place (the factory) instead of scattered across every call site
that needs a `Vehicle`.

## Singleton — shared state

Exactly one instance for the process lifetime — a rate limiter's counter store, a shared config, a
connection pool. Naive Python implementations aren't thread-safe; see
[thread_safety_and_concurrency.md](thread_safety_and_concurrency.md) for the double-checked-locking
fix.

```python
class RateLimiterRegistry:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._counters = {}
        return cls._instance
```

## State — lifecycle-driven behavior

An object's behavior changes based on its current state, and the state object itself decides the
next transition — a natural fit for `elevator.md` (idle/moving/door-open) or an order lifecycle
(pending/shipped/delivered).

```python
class ElevatorState(Protocol):
    def request(self, elevator: "Elevator", floor: int) -> None: ...

class IdleState:
    def request(self, elevator: "Elevator", floor: int) -> None:
        elevator.state = MovingState()
        print(f"moving to floor {floor}")

class MovingState:
    def request(self, elevator: "Elevator", floor: int) -> None:
        print("already moving, queuing request")

class Elevator:
    def __init__(self):
        self.state: ElevatorState = IdleState()

    def request_floor(self, floor: int) -> None:
        self.state.request(self, floor)
```

Strategy and State look identical in code shape (context + swappable object behind an interface) —
the difference is *who* changes the active object. In Strategy, the client sets it from outside and
it never changes itself. In State, the state object reassigns `elevator.state` itself as a side
effect of handling a request.

## Decorator — extensible behavior

Wraps an object to add behavior while exposing the same interface, so decorations stack without a
subclass per combination (e.g. `notification_service.md`: base send + logging + retry, in any
combination).

```python
class Notifier(Protocol):
    def send(self, message: str) -> None: ...

class BaseNotifier:
    def send(self, message: str) -> None:
        print(f"sending: {message}")

class LoggingNotifier:
    def __init__(self, wrapped: Notifier):
        self.wrapped = wrapped

    def send(self, message: str) -> None:
        print(f"[log] about to send: {message}")
        self.wrapped.send(message)

notifier = LoggingNotifier(BaseNotifier())
```

Without Decorator, "add logging" × "add retry" × "add rate limiting" needs a subclass per
combination; with it, each concern wraps once and combinations are just nesting order.

## Interview questions

**Q: How do you tell Strategy and State apart when a design could look like either?**
A: Ask who changes the active object. If it's the client, from outside, choosing based on
information the object itself doesn't have — Strategy. If the object reassigns its own active
behavior as a consequence of handling a call — State.

**Q: When would you reach for Factory instead of just calling constructors directly?**
A: When the concrete type to instantiate depends on runtime input (a string, a config value, a
class of a base type) and more than one call site needs that decision — centralizing it means a new
type is one new factory branch instead of an edit everywhere the type is constructed.

**Q: Why is Decorator preferred over subclassing for combinable optional behavior?**
A: Subclassing for N independent optional behaviors needs up to 2^N subclasses to cover every
combination; decorators compose by nesting, so N behaviors need only N decorator classes and any
combination is just wrapping order.

## Exercises

1. Take the `notifier` Decorator example above and add a `RetryNotifier` that retries `send()` up
   to 3 times on exception, then compose `RetryNotifier(LoggingNotifier(BaseNotifier()))` — confirm
   both concerns fire in the right order.
2. Sketch (class names + method signatures only, no bodies) which of the six patterns above you'd
   reach for in [`../exercises/rate_limiter.md`](../exercises/rate_limiter.md) and
   [`../exercises/elevator.md`](../exercises/elevator.md) before opening either file, then check
   your guess against the actual exercise.
