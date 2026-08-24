"""
Design Patterns in Python — #10
Facade (Structural Pattern)

Intent
------
Provide a single, simplified entry point to a set of classes in a complex subsystem. Facade
doesn't add new capability — every subsystem class it wraps is still fully usable on its own —
it just gives most callers a narrow, high-level door instead of forcing them to learn the whole
building's floor plan to get one thing done.

Problem / Motivation
---------------------
Placing an order in an e-commerce backend touches several independent subsystems: check the
warehouse has stock, reserve it, charge the customer's card, book a shipment, and send a
confirmation email — each with its own class, its own method names, and its own rules about
what has to happen before what (you can't charge a card for something out of stock; you
shouldn't book shipping before payment clears). If every call site that places an order — the
web checkout handler, the CLI admin tool, the retry job for failed orders — has to know and
correctly repeat that five-step dance, the coordination logic gets duplicated, and any call site
that gets the order wrong (e.g. ships before charging) creates a real bug, not just messy code.

Structure
---------
A Facade class sits in front of several subsystem classes (here: Inventory, Payment, Shipping,
Notifications) that it holds references to. The Facade exposes a small number of high-level
methods (`place_order`); each one internally calls the right subsystem methods in the right
order, with the right error handling. Client code depends only on the Facade's simple interface
and never talks to the subsystem classes directly — though it still *can*, since Facade doesn't
hide or restrict them, it just makes bypassing it unnecessary for the common case.

When to Use
-----------
- A workflow requires coordinating several subsystem objects in a specific order, and that
  coordination logic would otherwise be duplicated at every call site.
- You want to give client code (or an outer layer, like a web handler or CLI) a small, stable
  API surface that insulates it from subsystem internals that may change.
- You're integrating a legacy or third-party system with a messy API and want one clean
  interface at the boundary, without rewriting the messy parts underneath.

When NOT to Use
----------------
- Don't add a Facade in front of a subsystem that's already simple — a facade over one class
  with one method is just an extra layer of indirection with no payoff.
- Don't let the Facade grow "god object" tendencies by stuffing unrelated workflows into it;
  if it starts accumulating dozens of loosely related methods, that's a sign you need several
  smaller facades, not one that does everything.
- Don't use a Facade to *enforce* restricted access — it's a convenience wrapper, not a security
  boundary. Subsystem classes remain directly reachable; use Proxy if you need to gate access.

Related / Commonly Confused Patterns
--------------------------------------
- Adapter: Adapter changes an interface so it matches what a client expects (translation);
  Facade simplifies an interface that's already usable but verbose to coordinate
  (simplification). You adapt one mismatched class; you facade several correctly-shaped ones.
- Mediator: Mediator centralizes *communication between peer objects that talk back to each
  other*; Facade centralizes *one-directional calls from a client into a subsystem* that doesn't
  call back. Facade's subsystem classes typically don't know the Facade exists.
- Singleton: a Facade is often implemented as a single shared instance in practice, but that's
  an implementation detail, not part of what makes it a Facade.
"""


# ============================================================
# Anti-pattern: the naive way, and why it hurts
# ============================================================
# Each subsystem is fine in isolation. The pain is that every call site placing an order has to
# know the correct sequence AND correctly unwind partial work on failure. Here the CLI path and
# the web path each reimplement (and can each get subtly wrong) the same five-step dance.
class InventoryService:
    def __init__(self):
        self._stock = {"widget": 4, "gadget": 0}

    def has_stock(self, sku: str, qty: int) -> bool:
        return self._stock.get(sku, 0) >= qty

    def reserve(self, sku: str, qty: int) -> None:
        self._stock[sku] -= qty
        print(f"  [inventory] reserved {qty}x {sku}")

    def release(self, sku: str, qty: int) -> None:
        self._stock[sku] += qty
        print(f"  [inventory] released {qty}x {sku} back to stock")


class PaymentGateway:
    def charge(self, card_token: str, amount_cents: int) -> str:
        print(f"  [payment] charged {amount_cents}c to card {card_token}")
        return f"txn_{card_token[-4:]}_{amount_cents}"


class ShippingService:
    def book(self, address: str, sku: str, qty: int) -> str:
        print(f"  [shipping] booked shipment of {qty}x {sku} to {address}")
        return f"ship_{sku}_{qty}"


class NotificationService:
    def send_confirmation(self, email: str, order_summary: str) -> None:
        print(f"  [notify] emailed {email}: {order_summary}")


def place_order_naive_web_handler(sku: str, qty: int, card_token: str, address: str, email: str):
    # The web checkout handler reimplements the whole dance...
    inventory = InventoryService()
    payment = PaymentGateway()
    shipping = ShippingService()
    notifications = NotificationService()

    if not inventory.has_stock(sku, qty):
        print("  [web handler] out of stock, aborting")
        return None
    inventory.reserve(sku, qty)
    txn_id = payment.charge(card_token, qty * 1999)
    shipping.book(address, sku, qty)
    notifications.send_confirmation(email, f"{qty}x {sku}, txn {txn_id}")
    return txn_id


def place_order_naive_cli_tool(sku: str, qty: int, card_token: str, address: str, email: str):
    # ...and the CLI admin tool reimplements it again, slightly differently — it forgot to check
    # stock before reserving, a bug the web handler doesn't have. Two copies of "the workflow"
    # means two chances to get it wrong, and they've already diverged.
    inventory = InventoryService()
    payment = PaymentGateway()
    shipping = ShippingService()
    notifications = NotificationService()

    inventory.reserve(sku, qty)  # BUG: no has_stock() check — can go negative
    txn_id = payment.charge(card_token, qty * 1999)
    shipping.book(address, sku, qty)
    notifications.send_confirmation(email, f"{qty}x {sku}, txn {txn_id}")
    return txn_id


# ============================================================
# Implementation 1: Classic (OOP / GoF-style)
# ============================================================
# A single OrderFacade class owns references to the subsystems and exposes one method,
# place_order(), that every call site (web, CLI, retry job) can call identically. The
# coordination order and the failure handling (release reserved stock if payment fails) live in
# exactly one place now.
class OrderFacade:
    def __init__(self):
        self._inventory = InventoryService()
        self._payment = PaymentGateway()
        self._shipping = ShippingService()
        self._notifications = NotificationService()

    def place_order(self, sku: str, qty: int, card_token: str, address: str, email: str) -> str | None:
        if not self._inventory.has_stock(sku, qty):
            print("  [facade] out of stock, order rejected")
            return None

        self._inventory.reserve(sku, qty)
        try:
            txn_id = self._payment.charge(card_token, qty * 1999)
        except Exception:
            self._inventory.release(sku, qty)
            raise

        self._shipping.book(address, sku, qty)
        self._notifications.send_confirmation(email, f"{qty}x {sku}, txn {txn_id}")
        return txn_id


# ============================================================
# Implementation 2: Pythonic idiom (module of top-level functions)
# ============================================================
# A Facade doesn't have to be a class. It's just "one simple entry point in front of several
# subsystem objects" — when the facade itself has no meaningful state or identity of its own
# (nothing about "the order-placing facade" needs to be an instance you hold onto), a plain
# module-level function is a lighter-weight way to express the exact same idea. Python doesn't
# require a class just to group behavior, unlike Java/C++ where a free function coordinating
# other objects isn't idiomatic. Here the subsystems are passed in explicitly rather than
# constructed internally, which also makes this version trivially easier to test with fakes.
def checkout(
    inventory: InventoryService,
    payment: PaymentGateway,
    shipping: ShippingService,
    notifications: NotificationService,
    *,
    sku: str,
    qty: int,
    card_token: str,
    address: str,
    email: str,
) -> str | None:
    if not inventory.has_stock(sku, qty):
        print("  [checkout()] out of stock, order rejected")
        return None

    inventory.reserve(sku, qty)
    try:
        txn_id = payment.charge(card_token, qty * 1999)
    except Exception:
        inventory.release(sku, qty)
        raise

    shipping.book(address, sku, qty)
    notifications.send_confirmation(email, f"{qty}x {sku}, txn {txn_id}")
    return txn_id


# ============================================================
# Key Takeaways
# ============================================================
# - Facade's job is to reduce *how many things a caller needs to know* to get a common task
#   done, not to hide or lock down the subsystem — direct access to InventoryService etc. still
#   works fine for callers with unusual needs.
# - The real payoff shows up when there's more than one call site: the coordination logic (order
#   of operations, failure rollback) is written once instead of being copy-pasted and drifting.
# - A Facade need not be a class — if it has no state of its own, a plain function (or module of
#   functions) is a perfectly idiomatic Python facade with less ceremony.
# - Common confusion: Adapter vs Facade — reach for Adapter when one interface is *wrong-shaped*
#   for the caller; reach for Facade when several interfaces are *individually fine* but tedious
#   to coordinate together.


if __name__ == "__main__":
    print("--- Anti-pattern: two call sites, two copies of the workflow, one has a bug ---")
    place_order_naive_web_handler("widget", 2, "card_4242", "1 Main St", "a@example.com")
    try:
        place_order_naive_cli_tool("gadget", 1, "card_4242", "1 Main St", "b@example.com")
        print("  [cli tool] placed an order for OUT-OF-STOCK gadget — the missing check bit us")
    except Exception as exc:
        print(f"  [cli tool] blew up: {exc}")

    print("\n--- Classic: OrderFacade — one place, correct every time ---")
    facade = OrderFacade()
    txn = facade.place_order("widget", 1, "card_9999", "2 Oak Ave", "c@example.com")
    assert txn is not None
    rejected = facade.place_order("gadget", 5, "card_9999", "2 Oak Ave", "c@example.com")
    assert rejected is None
    print("  gadget order correctly rejected (no stock, no dangling charge)")

    print("\n--- Pythonic: checkout() function facade, subsystems passed in explicitly ---")
    inv, pay, ship, notify = (
        InventoryService(),
        PaymentGateway(),
        ShippingService(),
        NotificationService(),
    )
    txn2 = checkout(
        inv, pay, ship, notify,
        sku="widget", qty=1, card_token="card_1111", address="3 Pine Rd", email="d@example.com",
    )
    assert txn2 is not None
    print("\nBoth facades hide the same five-step dance behind one call.")
