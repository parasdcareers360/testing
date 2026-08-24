"""
Design Patterns in Python — #13
Chain of Responsibility (Behavioral Pattern)

Intent
------
Give more than one object a chance to handle a request, without the sender needing to know
which object will actually handle it. You link candidate handlers into a chain and pass the
request along it: each handler either deals with the request itself or forwards it to the next
handler in line. The sender only ever talks to the *first* handler — it stays completely
decoupled from how many handlers exist or which one ends up doing the work.

Problem / Motivation
---------------------
Picture a support-ticket system: a ticket might be resolvable by a first-line support agent, or
it might need to escalate to a senior agent, or all the way up to a manager for anything
involving a refund. The naive way to write this is one function with a big if/elif chain
checking ticket severity and deciding who handles it — and that function has to know about
*every* level of support and *all* the escalation rules in one place. Add a new tier (say, a
"security team" for account-compromise tickets) and you're back in that same function again,
threading a new branch into logic that already has three other people's concerns tangled into
it.

Structure
---------
Each Handler holds a reference to the next handler in the chain and exposes a uniform
`handle(request)` method. A ConcreteHandler inspects the request; if it can handle it, it does
so (and typically stops the chain); if not, it forwards the request to `self._next.handle(...)`
unconditionally. The client builds the chain once (wiring handler -> next -> next) and only ever
calls `handle()` on the head of the chain.

When to Use
-----------
- More than one object *might* handle a request, and the right handler isn't known until
  runtime (it depends on inspecting the request itself).
- You want to issue a request without hard-coding which receiver handles it, and you want to be
  able to change the set of handlers or their order without touching the sender's code.
- A pipeline of optional processing steps, where each step can either act and stop, or pass
  through untouched (validation pipelines, middleware, event filters).

When NOT to Use
----------------
- If exactly one handler is ever responsible and that's a compile-time-known fact, a chain is
  needless indirection — just call that handler directly.
- If every request must always be seen by every handler in a fixed order (not "first one that
  can handle it, stop"), you may just want a plain list of steps applied in sequence, not a
  request-passing chain with the possibility of nobody handling it (a real failure mode you must
  guard against — see the demo below).

Related / Commonly Confused Patterns
--------------------------------------
- Decorator: structurally similar (both wrap/link objects that each hold a reference to a
  "next" object), but intent differs — Decorator's whole point is that *every* link in the
  chain runs and adds behavior; Chain of Responsibility's point is that the request stops at
  whichever single link handles it, and the rest may never run at all.
- Composite: a chain can be seen as a degenerate, linear Composite, but Composite is about
  part-whole hierarchies (usually all children participate), not about picking one handler.
"""


# ============================================================
# Anti-pattern: the naive way, and why it hurts
# ============================================================
# One function knows about every support tier and every escalation rule at once. Adding a new
# tier (or changing the threshold for an existing one) means editing this same function, and
# the routing logic for "level 1" and "manager" are smashed together with no way to reuse or
# reorder them independently.
def route_ticket_naive(ticket: dict) -> str:
    severity = ticket["severity"]
    involves_refund = ticket.get("involves_refund", False)

    if severity == "low":
        return f"Level1Support resolved ticket #{ticket['id']} ({ticket['subject']})"
    elif severity == "medium":
        return f"Level2Support resolved ticket #{ticket['id']} ({ticket['subject']})"
    elif severity == "high" or involves_refund:
        # Refunds always need a manager, regardless of severity -- that rule is now buried
        # inside an unrelated severity if/elif chain instead of living with "manager" logic.
        return f"Manager resolved ticket #{ticket['id']} ({ticket['subject']})"
    else:
        return f"UNHANDLED ticket #{ticket['id']} -- no tier matched!"


# ============================================================
# Implementation 1: Classic (OOP / GoF-style, linked Handler objects)
# ============================================================
# Idea: each handler is an object that owns a link to "the next handler" and a uniform
# handle() entry point. A ConcreteHandler only knows its own rule for "can I handle this?" --
# it has zero knowledge of how many handlers come after it or what they do.
from abc import ABC, abstractmethod


class SupportHandler(ABC):
    def __init__(self):
        self._next: "SupportHandler | None" = None

    def set_next(self, handler: "SupportHandler") -> "SupportHandler":
        self._next = handler
        return handler  # returning handler lets callers chain .set_next(a).set_next(b)

    def handle(self, ticket: dict) -> str:
        if self._can_handle(ticket):
            return self._resolve(ticket)
        if self._next is not None:
            return self._next.handle(ticket)
        return f"UNHANDLED ticket #{ticket['id']} -- fell off the end of the chain!"

    @abstractmethod
    def _can_handle(self, ticket: dict) -> bool: ...

    @abstractmethod
    def _resolve(self, ticket: dict) -> str: ...


class Level1Support(SupportHandler):
    def _can_handle(self, ticket: dict) -> bool:
        return ticket["severity"] == "low" and not ticket.get("involves_refund", False)

    def _resolve(self, ticket: dict) -> str:
        return f"Level1Support resolved ticket #{ticket['id']} ({ticket['subject']})"


class Level2Support(SupportHandler):
    def _can_handle(self, ticket: dict) -> bool:
        return ticket["severity"] == "medium" and not ticket.get("involves_refund", False)

    def _resolve(self, ticket: dict) -> str:
        return f"Level2Support resolved ticket #{ticket['id']} ({ticket['subject']})"


class ManagerSupport(SupportHandler):
    def _can_handle(self, ticket: dict) -> bool:
        # A manager takes anything involving a refund (regardless of severity) or high severity
        # -- this rule now lives entirely inside ManagerSupport, not smeared across a big
        # if/elif chain that also handles Level1/Level2's business.
        return ticket.get("involves_refund", False) or ticket["severity"] == "high"

    def _resolve(self, ticket: dict) -> str:
        return f"Manager resolved ticket #{ticket['id']} ({ticket['subject']})"


# ============================================================
# Implementation 2: Pythonic idiom (a list of handler functions processed in a loop)
# ============================================================
# Idea: in Python, a "handler" doesn't need to be an object with a `_next` pointer at all --
# it can just be a plain function with the signature `(ticket) -> str | None` (return None to
# mean "not my job, try the next one"). The chain itself becomes an ordinary list, walked with
# a for-loop. This drops the linked-object machinery entirely: reordering, inserting, or
# removing a handler is just a list edit, and there's no wiring step to forget.
def level1_fn(ticket: dict) -> str | None:
    if ticket["severity"] == "low" and not ticket.get("involves_refund", False):
        return f"Level1Support resolved ticket #{ticket['id']} ({ticket['subject']})"
    return None


def level2_fn(ticket: dict) -> str | None:
    if ticket["severity"] == "medium" and not ticket.get("involves_refund", False):
        return f"Level2Support resolved ticket #{ticket['id']} ({ticket['subject']})"
    return None


def manager_fn(ticket: dict) -> str | None:
    if ticket.get("involves_refund", False) or ticket["severity"] == "high":
        return f"Manager resolved ticket #{ticket['id']} ({ticket['subject']})"
    return None


def route_ticket_functional(ticket: dict, handlers: list) -> str:
    for handler in handlers:
        result = handler(ticket)
        if result is not None:
            return result
    return f"UNHANDLED ticket #{ticket['id']} -- fell off the end of the chain!"


# ============================================================
# Key Takeaways
# ============================================================
# - The sender (whoever calls handle()) never names a specific handler class -- it only knows
#   about the head of the chain. That's the decoupling this pattern buys you.
# - A chain can fail to handle a request if you forget a catch-all at the end -- that's a real
#   risk, not a theoretical one, so always design either a default handler or an explicit
#   "unhandled" fallback (both implementations here do this).
# - In Python, "a handler" is often better modeled as a function returning None-or-result than
#   as a class with a `_next` pointer -- the linked-object machinery is only worth it when
#   handlers carry meaningful internal state or need polymorphic dispatch beyond a simple check.
# - Related pattern to compare: Decorator -- looks similar (linked wrappers), but every
#   Decorator layer runs, whereas Chain of Responsibility stops at the first handler that can.


if __name__ == "__main__":
    tickets = [
        {"id": 101, "subject": "password reset", "severity": "low"},
        {"id": 102, "subject": "app crashes on login", "severity": "medium"},
        {"id": 103, "subject": "data loss bug", "severity": "high"},
        {"id": 104, "subject": "wants money back", "severity": "low", "involves_refund": True},
        {"id": 105, "subject": "mystery issue", "severity": "unknown"},
    ]

    print("--- Anti-pattern: one function entangling every tier's rules ---")
    for t in tickets:
        print(" ", route_ticket_naive(t))

    print("\n--- Classic: linked Handler chain (Level1 -> Level2 -> Manager) ---")
    level1 = Level1Support()
    level2 = Level2Support()
    manager = ManagerSupport()
    level1.set_next(level2).set_next(manager)

    for t in tickets:
        print(" ", level1.handle(t))

    assert "Level1Support" in level1.handle(tickets[0])
    assert "Level2Support" in level1.handle(tickets[1])
    assert "Manager" in level1.handle(tickets[2])
    assert "Manager" in level1.handle(tickets[3])  # refund escalates past severity="low"
    assert "UNHANDLED" in level1.handle(tickets[4])

    print("\n--- Pythonic: list of handler functions walked in a loop ---")
    chain = [level1_fn, level2_fn, manager_fn]
    for t in tickets:
        print(" ", route_ticket_functional(t, chain))

    assert "Manager" in route_ticket_functional(tickets[3], chain)
    assert "UNHANDLED" in route_ticket_functional(tickets[4], chain)

    print("\nBoth chains route identically to the naive version, but adding/reordering a tier")
    print("now means editing exactly one handler (or one list entry) -- not the whole chain.")
