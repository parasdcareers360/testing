"""
Design Patterns in Python — #7
Bridge (Structural Pattern)

Intent
------
Decouple an abstraction from its implementation so the two can vary independently. Bridge splits
what would otherwise be one class hierarchy into two separate hierarchies — an Abstraction side
(the high-level operations client code calls) and an Implementation side (the low-level platform
or backend work) — connected by object composition instead of inheritance, so you can mix and
match any Abstraction with any Implementation at runtime.

Problem / Motivation
---------------------
Say you're building a small graphics tool with shapes (Circle, Square, ...) that can be drawn in
different ways (VectorRenderer for SVG-style output, RasterRenderer for pixel-grid output). The
naive approach is a single inheritance hierarchy: `VectorCircle`, `RasterCircle`,
`VectorSquare`, `RasterSquare`. That works for two shapes and two renderers (four classes), but
every new shape multiplies by every existing renderer, and every new renderer multiplies by
every existing shape — the class count grows as shapes × renderers, and adding one renderer
means writing N new classes, one per existing shape. The two concerns (what shape it is, how it
gets drawn) are tangled together in a single hierarchy when they're actually independent axes of
variation.

Structure
---------
Shape is the Abstraction: it holds a reference to a Renderer (the Implementation interface) and
delegates the actual drawing work to it rather than implementing drawing itself. ConcreteShapes
(Circle, Square) extend Shape with shape-specific data (radius, side length) and describe *what*
to draw in terms the Renderer understands. ConcreteRenderers (VectorRenderer, RasterRenderer)
implement *how* primitives get drawn. Because Shape holds a Renderer by composition rather than
inheriting from it, any shape can be paired with any renderer, and new shapes or new renderers
can be added independently — this is the defining trait that separates Bridge from Adapter,
which reconciles one existing mismatched interface rather than pre-splitting two hierarchies
that are meant to grow independently.

When to Use
-----------
- You have two (or more) independent dimensions along which a class needs to vary, and
  inheriting for both would multiply the number of classes combinatorially.
- You want to swap out an implementation at runtime (e.g. switch renderers, switch storage
  backends) without touching the abstraction's client-facing code.
- You're designing this up front, anticipating that both the abstraction and the implementation
  will each grow their own family of variants over time.

When NOT to Use
----------------
- If there's really only one axis of variation (only ever one renderer, say), Bridge adds a
  layer of indirection — an extra interface and an extra composition step — for no payoff. Plain
  inheritance is simpler when there's nothing to decouple from.
- Don't retrofit Bridge onto an interface mismatch discovered after the fact — that's Adapter's
  job. Bridge is a deliberate up-front design split, not a patch.

Related / Commonly Confused Patterns
--------------------------------------
- Adapter: same "object holds a reference to another object" shape, but Adapter is applied
  reactively to make one already-existing, mismatched interface fit — it's not designed in as
  two hierarchies meant to vary independently from day one.
- Strategy: also composition-over-inheritance with an interchangeable interface, but Strategy
  swaps one algorithm inside an otherwise-ordinary object; Bridge structurally splits an entire
  class hierarchy into two hierarchies that both have their own subclasses.
- Abstract Factory: often shows up alongside Bridge to construct matching Abstraction +
  Implementation pairs, but Abstract Factory's job is object creation, not the runtime
  delegation Bridge is built around.
"""


# ============================================================
# Anti-pattern: the naive way, and why it hurts
# ============================================================
# One inheritance hierarchy tangles "what shape" with "how it's rendered." Adding a third
# renderer (say, ASCIIRenderer) means writing VectorCircle/RasterCircle/ASCIICircle *and*
# VectorSquare/RasterSquare/ASCIISquare — every new renderer multiplies across every shape.
class VectorCircleNaive:
    def __init__(self, radius: float):
        self.radius = radius

    def draw(self) -> str:
        return f"<svg><circle r='{self.radius}'/></svg>"


class RasterCircleNaive:
    def __init__(self, radius: float):
        self.radius = radius

    def draw(self) -> str:
        return f"[pixels] filling {int(self.radius * 2)}x{int(self.radius * 2)} grid as a circle"


class VectorSquareNaive:
    def __init__(self, side: float):
        self.side = side

    def draw(self) -> str:
        return f"<svg><rect width='{self.side}' height='{self.side}'/></svg>"


class RasterSquareNaive:
    def __init__(self, side: float):
        self.side = side

    def draw(self) -> str:
        return f"[pixels] filling {int(self.side)}x{int(self.side)} grid as a square"

    # A third renderer (ASCIIRenderer) would require ASCIICircleNaive AND ASCIISquareNaive too —
    # the class count is shapes x renderers, growing multiplicatively in both directions.


# ============================================================
# Implementation 1: Classic (OOP / GoF-style)
# ============================================================
# Two independent hierarchies connected by composition. Shape (Abstraction) holds a Renderer
# (Implementation) and delegates to it; neither hierarchy inherits from the other.
from abc import ABC, abstractmethod


class Renderer(ABC):
    """Implementation hierarchy: HOW a primitive gets drawn."""

    @abstractmethod
    def render_circle(self, radius: float) -> str:
        raise NotImplementedError

    @abstractmethod
    def render_square(self, side: float) -> str:
        raise NotImplementedError


class VectorRenderer(Renderer):
    def render_circle(self, radius: float) -> str:
        return f"<svg><circle r='{radius}'/></svg>"

    def render_square(self, side: float) -> str:
        return f"<svg><rect width='{side}' height='{side}'/></svg>"


class RasterRenderer(Renderer):
    def render_circle(self, radius: float) -> str:
        return f"[pixels] filling {int(radius * 2)}x{int(radius * 2)} grid as a circle"

    def render_square(self, side: float) -> str:
        return f"[pixels] filling {int(side)}x{int(side)} grid as a square"


class Shape(ABC):
    """Abstraction hierarchy: WHAT gets drawn. Holds a Renderer by composition, not inheritance."""

    def __init__(self, renderer: Renderer):
        self._renderer = renderer  # the bridge: a reference across to the other hierarchy

    @abstractmethod
    def draw(self) -> str:
        raise NotImplementedError


class Circle(Shape):
    def __init__(self, renderer: Renderer, radius: float):
        super().__init__(renderer)
        self.radius = radius

    def draw(self) -> str:
        return self._renderer.render_circle(self.radius)  # delegates HOW to the renderer


class Square(Shape):
    def __init__(self, renderer: Renderer, side: float):
        super().__init__(renderer)
        self.side = side

    def draw(self) -> str:
        return self._renderer.render_square(self.side)


# Note: adding a third renderer (e.g. AsciiRenderer) means writing ONE new class implementing
# Renderer — every existing Shape subclass (Circle, Square) works with it immediately, with zero
# new shape classes. That's the combinatorial win Bridge buys over the anti-pattern above.


# ============================================================
# Key Takeaways
# ============================================================
# - Bridge's defining move is composition instead of inheritance across two axes of variation —
#   the abstraction holds a reference to its implementation rather than being built on top of it.
# - The payoff is additive, not multiplicative: N shapes + M renderers means N + M classes
#   (plus the two interfaces), not N x M.
# - This is a two-hierarchy pattern by design, decided up front — don't confuse it with Adapter,
#   which is a one-off patch applied after discovering an interface mismatch in existing code.
# - No separate "Pythonic" implementation is included here: the whole point of Bridge is the
#   two-hierarchy structure connected by composition, and that structure itself already *is* the
#   idiomatic way to express it in Python — there's no meaningfully different second angle the
#   way there is for, say, Singleton or Strategy.


if __name__ == "__main__":
    print("--- Anti-pattern: one hierarchy per shape-x-renderer combination ---")
    print(VectorCircleNaive(5).draw())
    print(RasterSquareNaive(4).draw())
    print("  (a 3rd renderer would require rewriting BOTH VectorX and RasterX classes again)")

    print("\n--- Classic Bridge: Shape (abstraction) x Renderer (implementation), independently ---")
    vector = VectorRenderer()
    raster = RasterRenderer()

    shapes = [
        Circle(vector, radius=5),
        Circle(raster, radius=5),
        Square(vector, side=4),
        Square(raster, side=4),
    ]
    for shape in shapes:
        print(f"  {type(shape).__name__} + {type(shape._renderer).__name__}: {shape.draw()}")

    # Prove the two hierarchies vary independently: swap a shape's renderer at runtime without
    # touching the Shape class at all.
    c = Circle(vector, radius=2)
    before = c.draw()
    c._renderer = raster
    after = c.draw()
    print(f"\n  same Circle instance, swapped renderer: '{before}' -> '{after}'")
    assert before != after

    assert isinstance(vector, Renderer) and isinstance(raster, Renderer)
    assert all(isinstance(s, Shape) for s in shapes)

    print("\nBridge kept shapes and renderers independent — no shapes x renderers explosion.")
