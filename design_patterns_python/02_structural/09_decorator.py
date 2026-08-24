"""
Design Patterns in Python — #9
Decorator (Structural Pattern)

Intent
------
Attach additional responsibilities to an object dynamically by wrapping it in another object
that implements the *same* interface. Decorator lets you add behavior to individual objects at
runtime, in any combination, without subclassing every combination up front and without touching
the wrapped object's own code.

Problem / Motivation
---------------------
Say you're pricing drinks at a coffee shop: a plain Coffee costs $2.00, and customers can add
milk (+$0.50) and/or sugar (+$0.25), each independently, in any combination. The naive approach
is a subclass per combination: `Coffee`, `CoffeeWithMilk`, `CoffeeWithSugar`,
`CoffeeWithMilkAndSugar`. That's already four classes for two optional extras; a third extra
(whipped cream) would double it again to eight, because each new add-on has to be combined with
every existing combination. The cost and description logic for "milk" is duplicated across every
subclass that includes it, instead of existing in exactly one place.

Structure
---------
Component defines the interface shared by the plain object and every wrapped version of it
(e.g. `cost()`, `describe()`). ConcreteComponent (Coffee) is the base object with no extras.
Decorator is itself a Component that *wraps* another Component (held by reference) and delegates
to it, adding its own behavior before or after the delegated call. ConcreteDecorators
(MilkDecorator, SugarDecorator) each add one specific responsibility. Because a Decorator is a
Component, decorators can be stacked arbitrarily deep — wrapping a Coffee in MilkDecorator, then
wrapping that in SugarDecorator — and the client calls `cost()`/`describe()` on the outermost
wrapper without needing to know how many layers are underneath.

A note on naming: Python's `@decorator` function syntax is not just a coincidentally-shared name
— it's a genuine, real-world application of this exact GoF pattern, applied to functions instead
of objects. `@decorator` wraps a function in another callable that implements the same "calling
interface" (takes the same args, returns a result) and adds behavior around the call — logging,
timing, caching, retrying — without changing the original function's code. Implementation 1
below shows the classic object-wrapping form the pattern is taught with; Implementation 2 shows
the identical intent expressed as a Python function decorator, to make the connection concrete
rather than asserted.

When to Use
-----------
- You need to add optional, combinable responsibilities to individual objects (or functions) at
  runtime, and subclassing for every combination would explode combinatorially.
- You want responsibilities to be added and removed independently of each other and of the base
  object's own code (logging, caching, compression, encryption, pricing add-ons).

When NOT to Use
----------------
- If the set of combinations is small and fixed, plain subclassing is simpler to read — Decorator
  pays off specifically when combinations multiply or need to be assembled at runtime.
- Deeply stacked decorators can be hard to debug (a bug could be in any layer, and stack traces
  get noisy) — don't reach for Decorator just to avoid a single well-named boolean flag or
  parameter.

Related / Commonly Confused Patterns
--------------------------------------
- Composite: structurally similar (both self-referential, same-interface wrapping), but
  Composite holds zero-or-more children to represent a part-whole tree, while Decorator always
  wraps exactly one object to add behavior to it.
- Adapter: also wraps an object, but Adapter changes the *interface* to reconcile a mismatch;
  Decorator keeps the interface identical and adds *behavior*.
- Proxy: same wrapping shape again, but Proxy controls *access* to the wrapped object (lazy
  loading, permission checks, remote calls) rather than adding to its behavior — the wrapped
  object's contract is preserved unchanged either way, which is why these three are easy to mix
  up structurally despite having different intents.
"""


# ============================================================
# Anti-pattern: the naive way, and why it hurts
# ============================================================
# One subclass per combination of extras. Two optional add-ons already need four classes; a
# third add-on would require eight, and the pricing/description logic for "milk" is duplicated
# in every subclass that includes it.
class CoffeeNaive:
    def cost(self) -> float:
        return 2.00

    def describe(self) -> str:
        return "Coffee"


class CoffeeWithMilkNaive(CoffeeNaive):
    def cost(self) -> float:
        return 2.00 + 0.50

    def describe(self) -> str:
        return "Coffee + Milk"


class CoffeeWithSugarNaive(CoffeeNaive):
    def cost(self) -> float:
        return 2.00 + 0.25

    def describe(self) -> str:
        return "Coffee + Sugar"


class CoffeeWithMilkAndSugarNaive(CoffeeNaive):
    def cost(self) -> float:
        return 2.00 + 0.50 + 0.25  # duplicated math, now in a THIRD place

    def describe(self) -> str:
        return "Coffee + Milk + Sugar"
    # A third add-on (whipped cream) doubles this to eight classes, each re-deriving its own
    # slice of the same additive cost/description logic.


# ============================================================
# Implementation 1: Classic Decorator (object-wrapping, GoF-style)
# ============================================================
# CoffeeDecorator wraps a Component and IS-A Component itself, so decorators stack: each layer
# delegates to the one it wraps, then adds its own bit on top. Any combination of add-ons is
# just a different order of wrapping — no new classes needed per combination.
from abc import ABC, abstractmethod


class Beverage(ABC):
    @abstractmethod
    def cost(self) -> float:
        raise NotImplementedError

    @abstractmethod
    def describe(self) -> str:
        raise NotImplementedError


class Coffee(Beverage):
    """ConcreteComponent: the plain object, no extras."""

    def cost(self) -> float:
        return 2.00

    def describe(self) -> str:
        return "Coffee"


class BeverageDecorator(Beverage):
    """Base Decorator: wraps a Beverage and delegates to it. Itself IS a Beverage."""

    def __init__(self, wrapped: Beverage):
        self._wrapped = wrapped

    def cost(self) -> float:
        return self._wrapped.cost()

    def describe(self) -> str:
        return self._wrapped.describe()


class MilkDecorator(BeverageDecorator):
    def cost(self) -> float:
        return self._wrapped.cost() + 0.50  # delegate, then add this layer's own contribution

    def describe(self) -> str:
        return self._wrapped.describe() + " + Milk"


class SugarDecorator(BeverageDecorator):
    def cost(self) -> float:
        return self._wrapped.cost() + 0.25

    def describe(self) -> str:
        return self._wrapped.describe() + " + Sugar"


# Adding whipped cream later needs exactly ONE new class, not a new class per existing
# combination — it composes with everything that already exists.
class WhippedCreamDecorator(BeverageDecorator):
    def cost(self) -> float:
        return self._wrapped.cost() + 0.75

    def describe(self) -> str:
        return self._wrapped.describe() + " + Whipped Cream"


# ============================================================
# Implementation 2: The SAME pattern, expressed via Python's native @decorator syntax
# ============================================================
# This is not a loose analogy — it's the identical structural idea applied to functions instead
# of objects. A function decorator takes a callable (the Component), and returns a NEW callable
# (the Decorator) that implements the same "calling interface" (same args in, a result out) and
# wraps the original call with extra behavior. Stacking @decorators is exactly the same as
# nesting BeverageDecorator instances above — each @-line wraps the function returned by the
# @-line below it, closest to the def first.
import functools
import time


def logged(fn):
    """Decorator: wraps `fn`, adding logging around the call, same call signature preserved."""

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        print(f"  [log] calling {fn.__name__}(args={args}, kwargs={kwargs})")
        result = fn(*args, **kwargs)
        print(f"  [log] {fn.__name__} returned {result}")
        return result

    return wrapper


def timed(fn):
    """Another decorator, same shape: same interface in, added behavior around the call."""

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        elapsed_ms = (time.perf_counter() - start) * 1000
        print(f"  [timed] {fn.__name__} took {elapsed_ms:.3f}ms")
        return result

    return wrapper


# Stacking these two is structurally identical to wrapping Coffee in MilkDecorator then
# SugarDecorator above: @timed wraps the raw function first, then @logged wraps THAT wrapper —
# same "wrap an object that implements the same interface" chain, just for callables.
@logged
@timed
def brew_price(base_cost: float, extras_cost: float) -> float:
    return round(base_cost + extras_cost, 2)


# ============================================================
# Key Takeaways
# ============================================================
# - Decorator's core trick is that the wrapper implements the SAME interface as what it wraps,
#   so wrapped and unwrapped objects (or decorated and undecorated functions) are
#   interchangeable to any caller — that's what makes stacking work with zero special-casing.
# - Python's `@decorator` syntax is a genuine real-world instance of this pattern, not a naming
#   coincidence: a function decorator is a Decorator (in the GoF sense) whose Component interface
#   is "a callable with this call signature," applied to functions instead of objects — compare
#   `MilkDecorator(Coffee())` to `logged(brew_price)`, they're the same move.
# - Common misuse: reaching for a deep decorator stack (object OR function) when a single
#   well-named parameter or boolean flag would do — decorators earn their keep specifically when
#   responsibilities need to combine and recombine independently.
# - Related patterns to compare: Composite (children vs. exactly-one-wrapped object) and Proxy
#   (controls access rather than adding behavior) — both share Decorator's "wrap an object of
#   the same interface" shape but solve a different problem with it.


if __name__ == "__main__":
    print("--- Anti-pattern: one subclass per combination of extras ---")
    print(f"  {CoffeeWithMilkAndSugarNaive().describe()}: ${CoffeeWithMilkAndSugarNaive().cost():.2f}")
    print("  (a 3rd extra would require FOUR more subclasses to cover every combination)")

    print("\n--- Classic Decorator: stack any combination of wrappers, no new classes needed ---")
    plain = Coffee()
    print(f"  {plain.describe()}: ${plain.cost():.2f}")

    milk_coffee = MilkDecorator(plain)
    print(f"  {milk_coffee.describe()}: ${milk_coffee.cost():.2f}")

    fancy = WhippedCreamDecorator(SugarDecorator(MilkDecorator(plain)))
    print(f"  {fancy.describe()}: ${fancy.cost():.2f}")

    assert isinstance(fancy, Beverage) and isinstance(milk_coffee, Beverage)
    assert plain.cost() == 2.00
    assert milk_coffee.cost() == 2.50
    assert fancy.cost() == 2.00 + 0.50 + 0.25 + 0.75

    print("\n--- Implementation 2: the same intent via Python's native @decorator syntax ---")
    price = brew_price(2.00, 1.50)
    print(f"  final price via stacked @logged/@timed function decorators: ${price:.2f}")
    assert price == 3.50
    assert brew_price.__name__ == "brew_price"  # functools.wraps preserved the identity/metadata

    print("\nBoth forms are the same Decorator pattern: wrap, preserve interface, add behavior.")
