"""
Design Patterns in Python — #19
Observer (Behavioral Pattern)

Intent
------
Define a one-to-many dependency between objects so that when one object (the subject) changes
state, all of its dependents (the observers) are notified and updated automatically. The subject
doesn't need to know anything about who its observers are beyond a common notification
interface — new observers can be added, and old ones removed, without touching the subject's
code at all.

Problem / Motivation
---------------------
Imagine a stock ticker that tracks a live price. Several parts of a UI need to react whenever
that price changes: a "current price" label, a price-history chart, and a threshold alert that
should fire when the price crosses some value. The naive approach is for the ticker to know
about each of these consumers by name and call them directly — but then every time you add a
new display (say, a mobile push notifier), you have to go back and edit the ticker's update
method to add another direct call. The ticker, which should only be responsible for "the price
changed," ends up coupled to UI widgets, alerting logic, and anything else that ever wants to
know about a price tick.

Structure
---------
A Subject maintains a list of Observer references and exposes attach()/detach() methods to
manage that list, plus a notify() method that walks the list and calls update() on each one when
its own state changes. Each ConcreteObserver implements update() to react in its own way. The
Subject depends only on the abstract Observer interface, never on any concrete observer type.

When to Use
-----------
- One object's state change must be reflected in an open-ended, changing set of other objects,
  and you don't want the state-holder to know their concrete types.
- You want to broadcast an event to multiple interested parties without tight coupling (event
  systems, UI data-binding, pub/sub within a single process).

When NOT to Use
----------------
- When there's exactly one consumer and it's unlikely to grow — a direct method call is simpler
  and easier to trace than going through a subscription mechanism.
- When notification order or delivery guarantees matter a lot (e.g. "observer B must see the
  update before observer C fails") — plain Observer gives no ordering or error-isolation
  contract; you'd need to layer that on top, or reach for a proper message queue instead.
- Watch for the "observer leak": forgetting to detach() an observer whose owning object has gone
  away keeps it alive and reacting to events it should no longer care about.

Related / Commonly Confused Patterns
--------------------------------------
- Mediator: Mediator centralizes communication between peer objects so they don't reference each
  other directly; Observer is a simpler, one-directional broadcast from one subject to many
  listeners, with no coordination logic in between.
- Pub/Sub (messaging systems): the distributed-systems cousin of Observer — same broadcast idea,
  but decoupled further via a message broker, often across processes/machines rather than one
  in-memory subject and its listeners.
"""


# ============================================================
# Anti-pattern: the naive way, and why it hurts
# ============================================================
# The ticker calls each consumer by name, directly, inside set_price(). Adding a new display
# means editing this method again -- the ticker is now coupled to a label, a chart, AND an
# alert, none of which it should need to know about.
class StockTickerNaive:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.price = 0.0
        self.price_label_text = ""
        self.chart_points: list[float] = []
        self.alert_triggered = False

    def set_price(self, price: float) -> None:
        self.price = price
        # Every consumer hard-wired in here. Adding "mobile push notification" means
        # another line in this exact method, forever.
        self.price_label_text = f"{self.symbol}: ${price:.2f}"
        self.chart_points.append(price)
        if price > 150.0:
            self.alert_triggered = True


# ============================================================
# Implementation 1: Classic (OOP / GoF-style)
# ============================================================
# Idea: the ticker (Subject) holds a list of Observer objects and only ever calls the abstract
# update() method on them. It has zero knowledge of what a PriceLabel or PriceChart actually
# does -- new observer types can be attached at runtime with no change to StockTicker at all.
from abc import ABC, abstractmethod


class Observer(ABC):
    @abstractmethod
    def update(self, symbol: str, price: float) -> None: ...


class StockTicker:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self._price = 0.0
        self._observers: list[Observer] = []

    def attach(self, observer: Observer) -> None:
        self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)

    def set_price(self, price: float) -> None:
        self._price = price
        self._notify()

    def _notify(self) -> None:
        for observer in self._observers:
            observer.update(self.symbol, self._price)


class PriceLabel(Observer):
    def __init__(self):
        self.text = ""

    def update(self, symbol: str, price: float) -> None:
        self.text = f"{symbol}: ${price:.2f}"
        print(f"  [label] {self.text}")


class PriceChart(Observer):
    def __init__(self):
        self.points: list[float] = []

    def update(self, symbol: str, price: float) -> None:
        self.points.append(price)
        print(f"  [chart] plotted point #{len(self.points)}: {price:.2f}")


class ThresholdAlert(Observer):
    def __init__(self, threshold: float):
        self.threshold = threshold
        self.triggered = False

    def update(self, symbol: str, price: float) -> None:
        if price > self.threshold and not self.triggered:
            self.triggered = True
            print(f"  [alert] {symbol} crossed ${self.threshold:.2f}!")


# ============================================================
# Implementation 2: Pythonic idiom (plain callbacks instead of Observer objects)
# ============================================================
# Idea: in Python, "an object with a single update() method" and "a plain function" are
# interchangeable from the caller's point of view -- there's no need for a one-method ABC when a
# callable already satisfies that contract. Subscribers are just functions appended to a list;
# notify() simply calls each one. This drops the Observer interface entirely and reads more
# naturally for anyone used to event-driven Python (e.g. how `signal.connect` or a simple
# pub/sub bus often works).
from typing import Callable

PriceCallback = Callable[[str, float], None]


class StockTickerFunctional:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self._price = 0.0
        self._callbacks: list[PriceCallback] = []

    def subscribe(self, callback: PriceCallback) -> None:
        self._callbacks.append(callback)

    def unsubscribe(self, callback: PriceCallback) -> None:
        self._callbacks.remove(callback)

    def set_price(self, price: float) -> None:
        self._price = price
        for callback in self._callbacks:
            callback(self.symbol, price)


# ============================================================
# Key Takeaways
# ============================================================
# - Observer's core value is decoupling "something changed" from "here's everyone who reacts to
#   it" -- the subject only ever talks to an abstract notification contract, so the list of
#   reactors can grow or shrink without touching the subject.
# - In Python, that abstract contract doesn't have to be a class hierarchy: a list of plain
#   functions (closures included) satisfies the same role with less ceremony, since Python
#   doesn't need a named interface to call something back.
# - Common misuse: forgetting to detach() an observer whose owner has been discarded -- it keeps
#   receiving updates and can leak memory or fire logic against stale state.
# - Related pattern to compare: Mediator, which coordinates many-to-many communication between
#   peers, versus Observer's one-to-many broadcast from a single subject.


if __name__ == "__main__":
    print("--- Anti-pattern: ticker hard-wired to every consumer ---")
    naive = StockTickerNaive("ACME")
    naive.set_price(120.0)
    naive.set_price(155.0)
    print(f"label: {naive.price_label_text}, points: {naive.chart_points}, "
          f"alert: {naive.alert_triggered}")
    assert naive.alert_triggered

    print("\n--- Classic: StockTicker notifying Observer objects ---")
    ticker = StockTicker("ACME")
    label = PriceLabel()
    chart = PriceChart()
    alert = ThresholdAlert(threshold=150.0)
    ticker.attach(label)
    ticker.attach(chart)
    ticker.attach(alert)

    ticker.set_price(120.0)
    ticker.set_price(155.0)
    assert label.text == "ACME: $155.00"
    assert chart.points == [120.0, 155.0]
    assert alert.triggered

    # Detaching removes it from future notifications, with no change to StockTicker itself.
    ticker.detach(chart)
    ticker.set_price(160.0)
    assert chart.points == [120.0, 155.0]  # unchanged -- chart stopped listening
    print(f"chart points after detach: {chart.points}  <- no longer growing")

    print("\n--- Pythonic: plain callback functions as observers ---")
    functional_ticker = StockTickerFunctional("WIDGE")
    seen_prices: list[float] = []

    def log_to_console(symbol: str, price: float) -> None:
        print(f"  [callback] {symbol} ticked to ${price:.2f}")

    def record(symbol: str, price: float) -> None:
        seen_prices.append(price)

    functional_ticker.subscribe(log_to_console)
    functional_ticker.subscribe(record)
    functional_ticker.set_price(42.0)
    functional_ticker.set_price(43.5)
    assert seen_prices == [42.0, 43.5]

    functional_ticker.unsubscribe(log_to_console)
    functional_ticker.set_price(44.0)
    assert seen_prices == [42.0, 43.5, 44.0]
    print(f"seen_prices: {seen_prices}")

    print("\nAll Observer variants confirmed: subject broadcasts, listeners react independently.")
