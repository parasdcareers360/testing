"""
Design Patterns in Python — #21
Strategy (Behavioral Pattern)

Intent
------
Define a family of interchangeable algorithms, encapsulate each one, and make them swappable at
runtime independently of the client that uses them. The client picks which algorithm to use (or
is handed one), and the surrounding code that *invokes* the algorithm never has to change when a
new variant is added.

Problem / Motivation
---------------------
An e-commerce cart needs to apply a discount at checkout, but which discount depends on the
customer: some get a flat percentage off, some get a fixed amount off, some (during a
promotion) get "buy one get one" pricing, and new promotion types get invented every quarter by
marketing. The naive approach is a `calculate_total()` method with an `if promo_type ==
"percentage": ... elif promo_type == "fixed": ... elif promo_type == "bogo": ...` chain. Every
new promotion means editing this one method again, and it grows a new branch forever -- worse,
if two other places in the codebase also need to price a cart (an admin preview screen, a
receipt generator), the same if/elif chain has to be duplicated or imported everywhere.

Structure
---------
A Context (the shopping cart) holds a reference to a Strategy object and delegates the
swappable part of its work to it, calling a single well-known method (e.g. `apply(total)`). Each
ConcreteStrategy implements that method with a different algorithm. The client chooses which
strategy to hand the context -- the context itself never decides between algorithms, it just
executes whichever one it currently holds.

When to Use
-----------
- Several interchangeable algorithms exist for the same job, and you want to select one at
  runtime without a growing conditional in the code that uses it.
- You want to unit-test each algorithm variant in isolation, independent of the context that
  uses it.
- New variants are added often enough that "add a class/function" beats "add another branch to
  a shared conditional."

When NOT to Use
----------------
- If there's only one algorithm and no realistic prospect of a second, Strategy is pure
  overhead -- just write the logic inline.
- Don't build a Strategy *class hierarchy* in Python for algorithms simple enough to be a
  one-liner function -- that's exactly the case the Pythonic variant below exists to avoid.

Related / Commonly Confused Patterns
--------------------------------------
- State: identical structure (context + swappable object behind a common interface), opposite
  intent. Strategy's active algorithm is chosen and set by the *client* from outside, and the
  context never swaps it on its own; State's current state object changes *itself*, from the
  inside, as a side effect of handling actions. If the "strategy" starts reassigning itself based
  on its own logic, it has become a State.
- Template Method: also varies part of an algorithm, but via subclassing and overriding a
  protected step inside a fixed skeleton, rather than composing in a whole separate strategy
  object at runtime. Strategy favors composition; Template Method favors inheritance.
"""


# ============================================================
# Anti-pattern: the naive way, and why it hurts
# ============================================================
# calculate_total() has to know about every discount type that exists, by name, forever. Adding
# a new promotion means finding and editing this exact if/elif chain -- and if a receipt
# generator or an admin preview needs the same pricing logic, this whole block gets copy-pasted.
class CartNaive:
    def __init__(self, subtotal: float, promo_type: str):
        self.subtotal = subtotal
        self.promo_type = promo_type

    def calculate_total(self) -> float:
        if self.promo_type == "percentage":
            return round(self.subtotal * 0.9, 2)  # hardcoded 10% off
        elif self.promo_type == "fixed":
            return round(max(self.subtotal - 15.0, 0.0), 2)  # hardcoded $15 off
        elif self.promo_type == "none":
            return round(self.subtotal, 2)
        else:
            raise ValueError(f"unknown promo_type: {self.promo_type}")


# ============================================================
# Implementation 1: Classic (OOP / GoF-style)
# ============================================================
# Idea: Cart (Context) holds a DiscountStrategy and delegates pricing to it via one shared
# method, apply(). Each ConcreteStrategy is a real class implementing a different pricing rule.
# Cart itself contains zero knowledge of what "percentage off" or "fixed off" actually means --
# it just calls strategy.apply(subtotal).
from abc import ABC, abstractmethod


class DiscountStrategy(ABC):
    @abstractmethod
    def apply(self, subtotal: float) -> float: ...


class PercentageDiscount(DiscountStrategy):
    def __init__(self, percent_off: float):
        self.percent_off = percent_off

    def apply(self, subtotal: float) -> float:
        return round(subtotal * (1 - self.percent_off / 100), 2)


class FixedAmountDiscount(DiscountStrategy):
    def __init__(self, amount_off: float):
        self.amount_off = amount_off

    def apply(self, subtotal: float) -> float:
        return round(max(subtotal - self.amount_off, 0.0), 2)


class NoDiscount(DiscountStrategy):
    def apply(self, subtotal: float) -> float:
        return round(subtotal, 2)


class Cart:
    def __init__(self, subtotal: float, discount: DiscountStrategy):
        self.subtotal = subtotal
        self.discount = discount

    def calculate_total(self) -> float:
        return self.discount.apply(self.subtotal)


# ============================================================
# Implementation 2: Pythonic idiom (a plain function as the strategy)
# ============================================================
# Idea: Python functions are already first-class objects -- they can be stored, passed around,
# and called just like any DiscountStrategy instance. Building a one-method ABC purely to wrap
# "given a number, return a number" is ceremony the language doesn't require: a Callable[[float],
# float] satisfies the exact same contract with no class, no instantiation, and no boilerplate.
# This is the single clearest case in the whole GoF catalogue for "don't build a class hierarchy
# when a function will do" -- Strategy is fundamentally about swapping *behavior*, and in Python,
# behavior is already a first-class value without wrapping it in an object first.
from typing import Callable

DiscountFn = Callable[[float], float]


def percentage_discount(percent_off: float) -> DiscountFn:
    return lambda subtotal: round(subtotal * (1 - percent_off / 100), 2)


def fixed_amount_discount(amount_off: float) -> DiscountFn:
    return lambda subtotal: round(max(subtotal - amount_off, 0.0), 2)


def no_discount(subtotal: float) -> float:
    return round(subtotal, 2)


class CartFunctional:
    def __init__(self, subtotal: float, discount_fn: DiscountFn = no_discount):
        self.subtotal = subtotal
        self.discount_fn = discount_fn

    def calculate_total(self) -> float:
        return self.discount_fn(self.subtotal)


# ============================================================
# Key Takeaways
# ============================================================
# - Strategy's value is letting the *client* choose behavior and hand it to a context, so the
#   context never needs a conditional to pick between algorithms -- it just executes whichever
#   one it was given.
# - In Python, a "strategy" is very often just a function: the class-hierarchy version earns its
#   keep when a strategy needs to carry non-trivial internal state or multiple related methods;
#   a plain function (or a closure carrying config, as `percentage_discount()` shows) is simpler
#   and just as swappable when the strategy is really "one input, one output."
# - Common misuse/misconception: mistaking Strategy for State because the shapes match. The tell
#   is who changes the active object -- see the Related section above.
# - Related pattern to compare: Template Method -- varies an algorithm through inheritance and
#   overridden steps inside a fixed skeleton, rather than swapping in a whole separate object.


if __name__ == "__main__":
    print("--- Anti-pattern: if/elif chain baked into the cart ---")
    naive_pct = CartNaive(100.0, "percentage")
    naive_fixed = CartNaive(100.0, "fixed")
    print(f"percentage: {naive_pct.calculate_total()}, fixed: {naive_fixed.calculate_total()}")
    assert naive_pct.calculate_total() == 90.0
    assert naive_fixed.calculate_total() == 85.0

    print("\n--- Classic: Cart delegates to a DiscountStrategy object ---")
    cart_pct = Cart(100.0, PercentageDiscount(percent_off=20))
    cart_fixed = Cart(100.0, FixedAmountDiscount(amount_off=15))
    cart_none = Cart(50.0, NoDiscount())
    print(f"20% off $100: {cart_pct.calculate_total()}")
    print(f"$15 off $100: {cart_fixed.calculate_total()}")
    print(f"no discount on $50: {cart_none.calculate_total()}")
    assert cart_pct.calculate_total() == 80.0
    assert cart_fixed.calculate_total() == 85.0
    assert cart_none.calculate_total() == 50.0

    # Swapping the strategy at runtime -- Cart itself never had to change.
    cart_pct.discount = FixedAmountDiscount(amount_off=30)
    print(f"same cart, swapped to $30 off: {cart_pct.calculate_total()}")
    assert cart_pct.calculate_total() == 70.0

    print("\n--- Pythonic: a plain function as the strategy, no class hierarchy ---")
    cart_fn_pct = CartFunctional(100.0, percentage_discount(20))
    cart_fn_fixed = CartFunctional(100.0, fixed_amount_discount(15))
    cart_fn_none = CartFunctional(50.0)  # defaults to no_discount
    print(f"20% off $100: {cart_fn_pct.calculate_total()}")
    print(f"$15 off $100: {cart_fn_fixed.calculate_total()}")
    print(f"no discount on $50: {cart_fn_none.calculate_total()}")
    assert cart_fn_pct.calculate_total() == 80.0
    assert cart_fn_fixed.calculate_total() == 85.0
    assert cart_fn_none.calculate_total() == 50.0

    # An ad-hoc, one-off strategy needs nothing more than a lambda -- no new class required.
    cart_fn_pct.discount_fn = lambda subtotal: round(subtotal * 0.5, 2)
    print(f"same cart, swapped to an inline half-off lambda: {cart_fn_pct.calculate_total()}")
    assert cart_fn_pct.calculate_total() == 50.0

    print("\nAll Strategy variants confirmed: pricing algorithm swaps freely, cart stays fixed.")
