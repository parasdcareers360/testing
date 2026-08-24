"""
Design Patterns in Python — #3
Abstract Factory (Creational Pattern)

Intent
------
Provide an interface for creating *families* of related or dependent objects without specifying
their concrete classes. Where Factory Method hands back a single product, Abstract Factory hands
back a whole matched set — and guarantees the pieces in that set are mutually compatible (all
"light theme" widgets, never a light-theme button paired with a dark-theme checkbox by mistake).

Problem / Motivation
---------------------
Say a UI toolkit renders widgets in a chosen theme — light or dark. Each theme needs its own
Button and Checkbox, styled consistently. The naive approach passes a `theme` string down into
every widget constructor, and every place that builds a widget checks `if theme == "dark"`. This
scales badly in two ways: the same branching logic is duplicated everywhere widgets get created,
and — more dangerously — nothing stops a caller from accidentally building a `LightButton` next
to a `DarkCheckbox` on the same screen, because the "family" of widgets that belong together is
never enforced anywhere. It only lives in the programmer's head.

Structure
---------
An AbstractFactory declares a creation method per product type in the family (e.g.
`create_button()`, `create_checkbox()`). Each ConcreteFactory (LightThemeFactory,
DarkThemeFactory) implements all of those methods, always returning products from the *same*
family. Client code is handed one concrete factory instance and builds everything through it —
it never picks individual product classes, so it's structurally impossible to mismatch a button
from one family with a checkbox from another.

When to Use
-----------
- A system needs to work with multiple families of related products, and products within a
  family must be used together (a theme's widgets, a database driver's Connection+Cursor+
  Transaction classes, an OS-abstraction layer's File+Process+Socket classes).
- You want to swap an entire family of products at once (switch the whole app from light to dark
  theme) via a single configuration point, without touching the code that uses the widgets.

When NOT to Use
----------------
- If there's only one product type (not a family of several that must match), you want plain
  Factory Method (#2), not Abstract Factory — the "family consistency" guarantee is the whole
  point of this pattern, and it's wasted machinery if there's nothing to keep consistent.
- Adding a new product *type* to the family (e.g. every theme now also needs a Slider) means
  touching the abstract interface and every single concrete factory — that cost is worth paying
  for the consistency guarantee, but it's real and grows with the number of families.

Related / Commonly Confused Patterns
--------------------------------------
- Factory Method: Abstract Factory is often implemented as a cluster of Factory Methods, one per
  product in the family — see `create_button`/`create_checkbox` below, each of which is a Factory
  Method in its own right.
- Builder: both separate "what gets constructed" from client code, but Builder is about
  assembling one complex object step-by-step; Abstract Factory is about choosing which *family*
  of simple, ready-made objects to hand out.
"""

from abc import ABC, abstractmethod


# ============================================================
# Anti-pattern: the naive way, and why it hurts
# ============================================================
# Every widget constructor re-checks the theme string, and nothing enforces that a screen built
# with theme="dark" doesn't end up with a stray light-themed piece slipped in by a typo or a
# copy-pasted line. The "these belong together" rule lives only in the programmer's discipline.
def render_button_naive(theme: str) -> str:
    if theme == "light":
        return "[Button: white bg, black text]"
    elif theme == "dark":
        return "[Button: black bg, white text]"
    raise ValueError(f"unknown theme: {theme}")


def render_checkbox_naive(theme: str) -> str:
    if theme == "light":
        return "[Checkbox: white bg, gray border]"
    elif theme == "dark":
        return "[Checkbox: black bg, silver border]"
    raise ValueError(f"unknown theme: {theme}")


def render_screen_naive(theme: str) -> None:
    print(render_button_naive(theme))
    # Bug: copy-pasted this line and forgot to update the theme argument. Nothing catches it —
    # the screen silently renders a mismatched checkbox.
    print(render_checkbox_naive("light"))


# ============================================================
# Implementation 1: Classic (OOP / GoF-style, family of factories via ABCs)
# ============================================================
# Idea: the abstract product interfaces (Button, Checkbox) are matched by an AbstractFactory
# interface with one creation method per product type. Each ConcreteFactory is guaranteed, by
# construction, to only ever hand back products from its own family — there's no code path that
# lets a LightThemeFactory return a DarkCheckbox.
class Button(ABC):
    @abstractmethod
    def render(self) -> str:
        ...


class Checkbox(ABC):
    @abstractmethod
    def render(self) -> str:
        ...


class LightButton(Button):
    def render(self) -> str:
        return "[Button: white bg, black text]"


class LightCheckbox(Checkbox):
    def render(self) -> str:
        return "[Checkbox: white bg, gray border]"


class DarkButton(Button):
    def render(self) -> str:
        return "[Button: black bg, white text]"


class DarkCheckbox(Checkbox):
    def render(self) -> str:
        return "[Checkbox: black bg, silver border]"


class WidgetFactory(ABC):
    """AbstractFactory: one creation method per product in the family."""

    @abstractmethod
    def create_button(self) -> Button:
        ...

    @abstractmethod
    def create_checkbox(self) -> Checkbox:
        ...


class LightThemeFactory(WidgetFactory):
    def create_button(self) -> Button:
        return LightButton()

    def create_checkbox(self) -> Checkbox:
        return LightCheckbox()


class DarkThemeFactory(WidgetFactory):
    def create_button(self) -> Button:
        return DarkButton()

    def create_checkbox(self) -> Checkbox:
        return DarkCheckbox()


def render_screen(factory: WidgetFactory) -> None:
    """Client code: only ever talks to WidgetFactory/Button/Checkbox — never a concrete class."""
    button = factory.create_button()
    checkbox = factory.create_checkbox()
    print(button.render())
    print(checkbox.render())


# ============================================================
# Key Takeaways
# ============================================================
# - Abstract Factory's real payoff is a *structural* guarantee: given one factory instance, it
#   is impossible to accidentally mix families, because every product comes from the same
#   object. That's strictly stronger than "please remember to pass the same theme string
#   everywhere," which is a convention, not a guarantee.
# - A dict-of-dicts (`{"light": {"button": LightButton, "checkbox": LightCheckbox}, ...}`) can
#   express the same lookup table, but it throws away that guarantee — nothing stops
#   `registry["light"]["checkbox"] = DarkCheckbox` from compiling and running. The ABC-based
#   classic form earns its ceremony here specifically because consistency is the whole point;
#   that's why this file doesn't force a "Pythonic" Implementation 2.
# - Common misuse: reaching for Abstract Factory when there's really only one product type. If
#   `create_checkbox` is the only method on your factory, you've built Factory Method (#2) with
#   extra steps.
# - Related pattern to compare: Builder (#4) — assembles one complex object piece-by-piece;
#   Abstract Factory selects among several complete, ready-made *families* of simple objects.


if __name__ == "__main__":
    print("--- Anti-pattern: theme strings threaded everywhere, easy to mismatch ---")
    render_screen_naive("dark")  # button is dark, checkbox is light -- the bug is live

    print("\n--- Classic: LightThemeFactory ---")
    render_screen(LightThemeFactory())

    print("\n--- Classic: DarkThemeFactory ---")
    render_screen(DarkThemeFactory())

    # The guarantee in action: every product pulled from one factory belongs to the same family.
    dark_factory = DarkThemeFactory()
    btn = dark_factory.create_button()
    chk = dark_factory.create_checkbox()
    assert isinstance(btn, DarkButton)
    assert isinstance(chk, DarkCheckbox)

    light_factory = LightThemeFactory()
    btn2 = light_factory.create_button()
    chk2 = light_factory.create_checkbox()
    assert isinstance(btn2, LightButton)
    assert isinstance(chk2, LightCheckbox)

    # Swapping the whole family is a one-line change at the call site, not a scattered edit.
    for factory in (LightThemeFactory(), DarkThemeFactory()):
        b, c = factory.create_button(), factory.create_checkbox()
        same_family = type(b).__name__.startswith(type(factory).__name__.replace("ThemeFactory", ""))
        assert same_family, "button and checkbox families must match"

    print("\nAbstract Factory confirmed: no mismatched families possible via the factory interface.")
