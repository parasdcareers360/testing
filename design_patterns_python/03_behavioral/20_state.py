"""
Design Patterns in Python — #20
State (Behavioral Pattern)

Intent
------
Let an object alter its behavior when its internal state changes, so that it appears to change
its class. Instead of a single class holding a pile of conditional logic that checks "what mode
am I in" before deciding what to do, each mode becomes its own object, and the main object just
delegates to whichever mode-object is currently active.

Problem / Motivation
---------------------
Consider an order in an e-commerce system: it moves through Pending -> Paid -> Shipped ->
Delivered, and certain actions are only legal in certain states (you can't ship an order that
hasn't been paid; you can't refund one that's already delivered, at least not through this
code path). The naive approach stores the state as a string or enum on the Order and gates every
method with `if self.status == "pending": ... elif self.status == "paid": ...`. Every new
status, and every method that needs to behave differently per status, adds another branch to
every one of those conditionals. The transition rules end up scattered across the class instead
of living anywhere in particular.

Structure
---------
A Context (here, Order) holds a reference to a current State object and delegates
state-dependent behavior to it. Each ConcreteState implements the shared State interface and
decides, for itself, what a given action does in that state and what state comes next --
including calling back into the Context to actually perform the transition (`context.state =
NextState()`). No separate Pythonic variant is shown below -- a dict-of-functions rewrite would
just relocate the same conditionals into a lookup table without giving each state a place to
decide its own next state, so it wouldn't be a genuinely distinct angle. The Context's public
methods become thin delegation calls; all the "is this
transition legal" logic lives inside the state classes themselves.

When to Use
-----------
- An object's behavior depends heavily on a finite set of internal modes/statuses, and that
  behavior needs to change together, consistently, when the mode changes.
- The transition rules between states are non-trivial (some transitions are illegal, or trigger
  side effects) and keeping them in one place (each state's class) is clearer than spreading
  conditionals across every method.

When NOT to Use
----------------
- For a handful of states with trivial, rarely-changing behavior -- a status enum plus a couple
  of `if` statements is easier to read than a class per state.
- If the "states" don't actually have distinct behavior, just distinct data -- that's a plain
  enum/flag, not a State pattern candidate.

Related / Commonly Confused Patterns
--------------------------------------
- Strategy: State and Strategy have *identical structure* (a context delegating to a swappable
  object behind a common interface) but opposite intent. Strategy's algorithm is chosen and
  handed in by the *client* ("use quicksort here"), and the context doesn't switch it on its
  own. State's current state is changed by the *state object itself*, in response to actions or
  internal logic ("PaidState decides that after `ship()` the next state is ShippedState") --
  the client never picks a state directly. If you find your "Strategy" secretly swapping itself
  out based on its own logic, it's actually a State.
- Chain of Responsibility: also passes control between objects, but CoR forwards a single
  request along a chain looking for a handler; State swaps which single object handles *all*
  future requests until the next transition.
"""


# ============================================================
# Anti-pattern: the naive way, and why it hurts
# ============================================================
# Every method re-checks self.status, and every new status means editing pay(), ship(),
# deliver(), and cancel() all over again. The legal-transition rules for "paid" are smeared
# across four different methods instead of living in one place.
class OrderNaive:
    def __init__(self, order_id: str):
        self.order_id = order_id
        self.status = "pending"

    def pay(self) -> None:
        if self.status == "pending":
            self.status = "paid"
            print(f"  [naive] order {self.order_id} paid")
        else:
            print(f"  [naive] cannot pay order in status {self.status}")

    def ship(self) -> None:
        if self.status == "paid":
            self.status = "shipped"
            print(f"  [naive] order {self.order_id} shipped")
        else:
            print(f"  [naive] cannot ship order in status {self.status}")

    def deliver(self) -> None:
        if self.status == "shipped":
            self.status = "delivered"
            print(f"  [naive] order {self.order_id} delivered")
        else:
            print(f"  [naive] cannot deliver order in status {self.status}")

    def cancel(self) -> None:
        if self.status in ("pending", "paid"):
            self.status = "cancelled"
            print(f"  [naive] order {self.order_id} cancelled")
        else:
            print(f"  [naive] cannot cancel order in status {self.status}")


# ============================================================
# Implementation 1: Classic (OOP / GoF-style)
# ============================================================
# Idea: Order (Context) holds a current OrderState and forwards every action to it. Each
# ConcreteState decides, for its own state, whether an action is legal, what happens, and what
# the next state is -- by directly setting order.state. Order itself no longer contains any
# "which status am I in" branching at all.
from abc import ABC, abstractmethod


class OrderState(ABC):
    name: str

    @abstractmethod
    def pay(self, order: "Order") -> None: ...

    @abstractmethod
    def ship(self, order: "Order") -> None: ...

    @abstractmethod
    def deliver(self, order: "Order") -> None: ...

    @abstractmethod
    def cancel(self, order: "Order") -> None: ...


class Order:
    def __init__(self, order_id: str):
        self.order_id = order_id
        self.state: OrderState = PendingState()

    def pay(self) -> None:
        self.state.pay(self)

    def ship(self) -> None:
        self.state.ship(self)

    def deliver(self) -> None:
        self.state.deliver(self)

    def cancel(self) -> None:
        self.state.cancel(self)

    def _refuse(self, action: str) -> None:
        print(f"  [classic] cannot {action} order {self.order_id} while {self.state.name}")


class PendingState(OrderState):
    name = "pending"

    def pay(self, order: Order) -> None:
        order.state = PaidState()
        print(f"  [classic] order {order.order_id} paid -> now {order.state.name}")

    def ship(self, order: Order) -> None:
        order._refuse("ship")

    def deliver(self, order: Order) -> None:
        order._refuse("deliver")

    def cancel(self, order: Order) -> None:
        order.state = CancelledState()
        print(f"  [classic] order {order.order_id} cancelled -> now {order.state.name}")


class PaidState(OrderState):
    name = "paid"

    def pay(self, order: Order) -> None:
        order._refuse("pay")

    def ship(self, order: Order) -> None:
        order.state = ShippedState()
        print(f"  [classic] order {order.order_id} shipped -> now {order.state.name}")

    def deliver(self, order: Order) -> None:
        order._refuse("deliver")

    def cancel(self, order: Order) -> None:
        order.state = CancelledState()
        print(f"  [classic] order {order.order_id} cancelled -> now {order.state.name}")


class ShippedState(OrderState):
    name = "shipped"

    def pay(self, order: Order) -> None:
        order._refuse("pay")

    def ship(self, order: Order) -> None:
        order._refuse("ship")

    def deliver(self, order: Order) -> None:
        order.state = DeliveredState()
        print(f"  [classic] order {order.order_id} delivered -> now {order.state.name}")

    def cancel(self, order: Order) -> None:
        order._refuse("cancel")  # no longer cancellable once shipped


class DeliveredState(OrderState):
    name = "delivered"

    def pay(self, order: Order) -> None:
        order._refuse("pay")

    def ship(self, order: Order) -> None:
        order._refuse("ship")

    def deliver(self, order: Order) -> None:
        order._refuse("deliver")

    def cancel(self, order: Order) -> None:
        order._refuse("cancel")


class CancelledState(OrderState):
    name = "cancelled"

    def pay(self, order: Order) -> None:
        order._refuse("pay")

    def ship(self, order: Order) -> None:
        order._refuse("ship")

    def deliver(self, order: Order) -> None:
        order._refuse("deliver")

    def cancel(self, order: Order) -> None:
        order._refuse("cancel")


# Implementation 2 (Pythonic idiom) is omitted here: the whole point of State is that each
# concrete state owns real, distinct transition logic and decides the next state itself. A
# dict-of-functions or enum-based rewrite would just relocate the naive if/elif into a lookup
# table -- it wouldn't give each state a place to hold its own behavior and decide its own next
# state, which is the actual mechanism this pattern teaches. There's no genuinely distinct
# idiomatic-Python angle beyond what the Classic implementation already is.


# ============================================================
# Key Takeaways
# ============================================================
# - State moves "what can happen in mode X" out of scattered conditionals and into a single
#   class per mode -- each ConcreteState both implements the mode's behavior AND decides the
#   next state, which keeps the transition table from leaking across unrelated methods.
# - Common misuse/misconception: confusing State with Strategy because they look identical in
#   code (context + swappable object + common interface). The tell is *who* changes the current
#   object -- Strategy is set by the client from outside; State changes itself from the inside
#   as a side effect of handling an action.
# - Related pattern to compare: Strategy (same shape, opposite intent -- see Related section
#   above); Chain of Responsibility (forwards one request along many handlers, rather than
#   switching which single handler owns everything going forward).


if __name__ == "__main__":
    print("--- Anti-pattern: status string + if/elif scattered across every method ---")
    naive = OrderNaive("N-1")
    naive.ship()  # illegal: still pending
    naive.pay()
    naive.ship()
    naive.deliver()
    naive.pay()  # illegal: already delivered
    assert naive.status == "delivered"

    print("\n--- Classic: Order delegates to its current OrderState ---")
    order = Order("S-1")
    assert order.state.name == "pending"

    order.ship()  # refused -- PendingState.ship() just prints a refusal, no crash
    order.pay()
    assert order.state.name == "paid"

    order.pay()  # refused -- can't pay twice
    order.ship()
    assert order.state.name == "shipped"

    order.cancel()  # refused -- ShippedState forbids cancellation
    assert order.state.name == "shipped"

    order.deliver()
    assert order.state.name == "delivered"

    order.ship()  # refused -- terminal state
    assert order.state.name == "delivered"

    print("\n--- A second order shows the cancel path is only legal pre-shipment ---")
    order2 = Order("S-2")
    order2.cancel()
    assert order2.state.name == "cancelled"
    order2.pay()  # refused -- cancelled is terminal too
    assert order2.state.name == "cancelled"

    print("\nAll State transitions confirmed: each state enforces its own legal moves.")
