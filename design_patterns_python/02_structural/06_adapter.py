"""
Design Patterns in Python — #6
Adapter (Structural Pattern)

Intent
------
Convert the interface a class already has into an interface some client code expects, without
modifying either side. Adapter lets objects with incompatible interfaces work together by
inserting a thin translation layer between them — the adaptee keeps doing exactly what it did
before, the client keeps calling what it always called, and the adapter is the only piece of
code that knows both vocabularies at once.

Problem / Motivation
---------------------
Say your checkout flow is built against a `PaymentProcessor` interface with one method:
`charge(dollars: float) -> str`. Now you need to integrate a third-party payment gateway SDK
that you don't control — its client exposes `send_payment(amount_cents: int, currency: str) ->
dict`. The amounts are in cents, not dollars; the return value is a raw dict instead of a
confirmation string; and the method name doesn't match. You can't edit the vendor's SDK, and you
don't want to rewrite your entire checkout flow (and every other `PaymentProcessor` you already
support) around one vendor's particular quirks. Without Adapter, the temptation is to sprinkle
unit-conversion and dict-unpacking logic directly into the checkout code, coupling it tightly to
this one gateway's shape and making it awkward to swap in a different processor later.

Structure
---------
Client code depends only on the Target interface it already understands (`PaymentProcessor`).
Adapter implements that Target interface, but internally holds a reference to the Adaptee (the
third-party gateway) and translates each Target call into the equivalent Adaptee call —
converting arguments, renaming methods, and reshaping return values as needed. The Adaptee
itself is never touched; it has no idea an adapter exists.

When to Use
-----------
- You need to use an existing class (third-party library, legacy code, generated client) whose
  interface doesn't match what your code expects, and you can't or shouldn't modify it.
- You want to introduce a new external dependency without letting its specific API shape leak
  into the rest of your codebase.
- You're migrating from one library/vendor to another and want both to satisfy the same
  interface during the transition.

When NOT to Use
----------------
- If you own both interfaces, just change one of them to match — an adapter is a workaround for
  code you don't control, not a substitute for a clean shared interface.
- Don't adapt speculatively "just in case" a second implementation ever shows up — that's
  premature abstraction. Add the adapter when a second, genuinely different interface exists.

Related / Commonly Confused Patterns
--------------------------------------
- Bridge: structurally similar (both wrap one object inside another), but Bridge is designed
  up-front to let two hierarchies vary independently; Adapter is retrofitted after the fact to
  reconcile one interface that already exists but doesn't fit.
- Facade: Facade simplifies/unifies a *broad* subsystem with a new, simpler interface; Adapter
  translates one *specific* existing interface into another one the client already expects, 1:1.
- Decorator: same "wrap an object" shape, but Decorator keeps the same interface and adds
  behavior; Adapter changes the interface to make it compatible.
"""


# ============================================================
# Anti-pattern: the naive way, and why it hurts
# ============================================================
# The checkout flow reaches directly into the third-party gateway's cents/dict shape. Every
# call site that wants to charge a customer needs to know this vendor's unit convention and
# response format — and if a second gateway is added, this conversion logic gets copy-pasted
# (and inevitably drifts) everywhere a payment is made.
class StripeLikeGatewaySDK:
    """Third-party SDK — not ours to modify. Works in cents, returns a raw dict."""

    def send_payment(self, amount_cents: int, currency: str = "usd") -> dict:
        print(f"  [gateway] processing {amount_cents} {currency} cents via vendor API...")
        return {"status": "succeeded", "id": "ch_12345", "amount_cents": amount_cents}


def checkout_naive(gateway: StripeLikeGatewaySDK, dollars: float) -> None:
    # Every call site duplicates the dollars->cents conversion and dict-unpacking, and is
    # coupled to this one vendor's response shape.
    cents = round(dollars * 100)
    result = gateway.send_payment(cents, "usd")
    if result["status"] == "succeeded":
        print(f"  [naive checkout] charged ${dollars:.2f}, confirmation id={result['id']}")
    else:
        print("  [naive checkout] payment failed")


# ============================================================
# Implementation 1: Classic (OOP / GoF-style)
# ============================================================
# PaymentProcessor is the Target interface our checkout flow already understands. The gateway
# SDK is the Adaptee. StripeGatewayAdapter implements Target and translates every call into the
# Adaptee's vocabulary (dollars -> cents, dict response -> confirmation string) in one place.
from abc import ABC, abstractmethod


class PaymentProcessor(ABC):
    """Target interface: what our checkout flow is written against."""

    @abstractmethod
    def charge(self, dollars: float) -> str:
        """Charge the given amount in dollars; return a confirmation id."""
        raise NotImplementedError


class StripeGatewayAdapter(PaymentProcessor):
    def __init__(self, gateway: StripeLikeGatewaySDK):
        self._gateway = gateway  # the Adaptee, held by reference, never modified

    def charge(self, dollars: float) -> str:
        cents = round(dollars * 100)
        result = self._gateway.send_payment(cents, currency="usd")
        if result["status"] != "succeeded":
            raise RuntimeError("payment declined")
        return result["id"]


# A second processor with a genuinely native PaymentProcessor interface, to show that client
# code can treat the adapted vendor and a native implementation identically.
class NativeBankProcessor(PaymentProcessor):
    def charge(self, dollars: float) -> str:
        print(f"  [native bank] charging ${dollars:.2f} directly...")
        return "bank_txn_98765"


def checkout(processor: PaymentProcessor, dollars: float) -> None:
    # This function knows nothing about cents, dicts, or vendor SDKs — only PaymentProcessor.
    confirmation_id = processor.charge(dollars)
    print(f"  [checkout] charged ${dollars:.2f}, confirmation id={confirmation_id}")


# ============================================================
# Implementation 2: Pythonic idiom (function adapter)
# ============================================================
# Idea: PaymentProcessor.charge() is a single method, so the whole "interface" our client needs
# is really just "a callable that takes dollars and returns a confirmation id." Python doesn't
# require a named class implementing an ABC for that — a closure over the adaptee that exposes
# the right call signature is a complete adapter with less ceremony. This only works because the
# Target interface here is a single method; a multi-method Target still warrants a real class
# (as Bridge and Composite do below).
def make_stripe_adapter(gateway: StripeLikeGatewaySDK):
    def charge(dollars: float) -> str:
        cents = round(dollars * 100)
        result = gateway.send_payment(cents, currency="usd")
        if result["status"] != "succeeded":
            raise RuntimeError("payment declined")
        return result["id"]

    return charge


# ============================================================
# Key Takeaways
# ============================================================
# - Adapter's whole job is translation, not extension: it changes *how you call* something, not
#   *what it does*. If you catch yourself adding new behavior inside an adapter, that behavior
#   belongs in a Decorator instead.
# - The Adaptee is never modified and often can't be (vendor SDK, legacy module, generated
#   client) — that constraint is exactly what makes Adapter the right tool instead of just
#   editing the class.
# - When the Target interface is a single method, a function/closure adapter is often simpler
#   than a full class — Python doesn't need a formal ABC just to satisfy "a callable with this
#   signature."
# - Related pattern to compare: Bridge — looks structurally similar (an object wrapping
#   another) but is designed in *before* two hierarchies diverge, rather than bolted on *after*
#   an interface mismatch is discovered.


if __name__ == "__main__":
    gateway = StripeLikeGatewaySDK()

    print("--- Anti-pattern: checkout code coupled directly to vendor's cents/dict shape ---")
    checkout_naive(gateway, 49.99)

    print("\n--- Classic: PaymentProcessor Target, StripeGatewayAdapter wraps the Adaptee ---")
    adapted = StripeGatewayAdapter(gateway)
    native = NativeBankProcessor()
    # Same checkout() function drives both an adapted third-party gateway and a native
    # implementation — client code never branches on which one it has.
    checkout(adapted, 49.99)
    checkout(native, 19.99)
    assert isinstance(adapted, PaymentProcessor)
    assert isinstance(native, PaymentProcessor)

    print("\n--- Pythonic: function-closure adapter, no class/ABC needed ---")
    charge_fn = make_stripe_adapter(gateway)
    confirmation = charge_fn(9.99)
    print(f"  [checkout] charged $9.99, confirmation id={confirmation}")
    assert confirmation == "ch_12345"

    print("\nAdapter lets incompatible interfaces cooperate without changing either side.")
