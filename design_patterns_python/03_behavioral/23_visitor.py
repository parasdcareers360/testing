"""
Design Patterns in Python — #23
Visitor (Behavioral Pattern)

Intent
------
Let you define a new operation over a set of related classes without modifying those classes'
source code. Instead of scattering operation-specific logic across every element class (or
worse, into `isinstance` checks in a central function), each element exposes one uniform
`accept(visitor)` method, and each new operation becomes a brand-new Visitor class implementing
one `visit_X` method per element type — added entirely alongside the existing code, not inside
it.

Problem / Motivation
---------------------
Picture a small vector-graphics/CAD tool with a handful of shape classes: `Circle`, `Square`,
`Triangle`. It needs several unrelated operations on those shapes: compute area, export to XML,
pretty-print a description. The naive approach is one function per operation that branches on
`isinstance(shape, Circle)` / `isinstance(shape, Square)` / ... Every time a new operation is
added, that same `isinstance` chain has to be reproduced again in a new function; every time a
new shape is added, EVERY existing operation function has to be found and given a new branch.
The operations and the shape types end up in a many-to-many tangle where nothing is the single
place responsible for "how Circle behaves" or "what area-calculation covers."

Structure
---------
An Element interface declares `accept(visitor)`; each ConcreteElement implements it by calling
back the matching `visit_ConcreteElement(self)` method on the visitor — this is "double
dispatch": which `visit_` method runs depends on BOTH the element's type and the visitor's type,
resolved without a single `isinstance` check anywhere. A Visitor interface declares one
`visit_X` method per ConcreteElement; a ConcreteVisitor implements a full operation across every
element type in one class. Adding a new operation means adding a new Visitor subclass — no
Element class changes. Adding a new Element type means adding a `visit_X` method to every
existing Visitor — the one real cost of this pattern.

When to Use
-----------
- You have a stable, rarely-changing set of element types, but need to keep adding new
  *operations* over them (area, export, validation, pretty-printing) without touching or
  recompiling the element classes each time.
- Related operations that logically belong together (e.g. "everything XML export needs to know
  about every shape") are better grouped in one Visitor class than smeared one method per shape.

When NOT to Use
----------------
- If you only have one operation and it's unlikely to grow, Visitor's double-dispatch machinery
  is pure overhead — a simple method on each element beats it.
- If the *element* types change far more often than operations do, Visitor inverts the cost in
  the wrong direction: every new element type forces you to revisit every existing Visitor class,
  which is exactly the "add a branch everywhere" problem this pattern exists to avoid elsewhere.

Related / Commonly Confused Patterns
--------------------------------------
- Iterator: often used together — Iterator supplies the traversal order over a structure,
  Visitor supplies the operation run at each stop — but Iterator is about *order of access*,
  Visitor is about *what runs* once you're there.
- Strategy: both let you plug in different behavior, but Strategy swaps one algorithm as a whole
  for a single object, while Visitor dispatches to a *different method per concrete type* across
  a whole family of unrelated element classes in one pass.
"""


# ============================================================
# Anti-pattern: the naive way, and why it hurts
# ============================================================
# One function per operation, each branching on isinstance(). Add a new operation (say,
# "pretty_print") and it needs its own fresh isinstance chain, duplicating the "what type is
# this shape" logic that area() and to_xml() already have. Add a new shape and EVERY one of
# these functions has to be found and given a new branch, or it silently mishandles the new type.
import math


class CircleNaive:
    def __init__(self, radius: float):
        self.radius = radius


class SquareNaive:
    def __init__(self, side: float):
        self.side = side


class TriangleNaive:
    def __init__(self, base: float, height: float):
        self.base = base
        self.height = height


def area_naive(shape) -> float:
    if isinstance(shape, CircleNaive):
        return math.pi * shape.radius**2
    elif isinstance(shape, SquareNaive):
        return shape.side**2
    elif isinstance(shape, TriangleNaive):
        return 0.5 * shape.base * shape.height
    raise TypeError(f"area_naive: unknown shape type {type(shape).__name__}")


def to_xml_naive(shape) -> str:
    if isinstance(shape, CircleNaive):
        return f'<circle radius="{shape.radius}"/>'
    elif isinstance(shape, SquareNaive):
        return f'<square side="{shape.side}"/>'
    elif isinstance(shape, TriangleNaive):
        return f'<triangle base="{shape.base}" height="{shape.height}"/>'
    raise TypeError(f"to_xml_naive: unknown shape type {type(shape).__name__}")
    # ^ pretty_print_naive() would need this exact isinstance chain a THIRD time.


# ============================================================
# Implementation 1: Classic (OOP / GoF-style, accept() + visit_X() double dispatch)
# ============================================================
# Idea: no isinstance() anywhere. Each shape's accept() calls the visitor method that matches
# ITS OWN type; Python picks which accept() runs via normal polymorphism (single dispatch on the
# shape), and that accept() then picks which visit_X runs (single dispatch on the visitor) --
# together that's double dispatch, resolved entirely through method calls.
from abc import ABC, abstractmethod


class ShapeVisitor(ABC):
    @abstractmethod
    def visit_circle(self, circle: "Circle") -> object: ...

    @abstractmethod
    def visit_square(self, square: "Square") -> object: ...

    @abstractmethod
    def visit_triangle(self, triangle: "Triangle") -> object: ...


class Shape(ABC):
    @abstractmethod
    def accept(self, visitor: ShapeVisitor) -> object: ...


class Circle(Shape):
    def __init__(self, radius: float):
        self.radius = radius

    def accept(self, visitor: ShapeVisitor) -> object:
        return visitor.visit_circle(self)


class Square(Shape):
    def __init__(self, side: float):
        self.side = side

    def accept(self, visitor: ShapeVisitor) -> object:
        return visitor.visit_square(self)


class Triangle(Shape):
    def __init__(self, base: float, height: float):
        self.base = base
        self.height = height

    def accept(self, visitor: ShapeVisitor) -> object:
        return visitor.visit_triangle(self)


class AreaVisitor(ShapeVisitor):
    """One operation, all shape types, in one place -- adding this class touched zero Shapes."""

    def visit_circle(self, circle: Circle) -> float:
        return math.pi * circle.radius**2

    def visit_square(self, square: Square) -> float:
        return square.side**2

    def visit_triangle(self, triangle: Triangle) -> float:
        return 0.5 * triangle.base * triangle.height


class XmlExportVisitor(ShapeVisitor):
    """A second, unrelated operation -- added alongside AreaVisitor, not merged into it."""

    def visit_circle(self, circle: Circle) -> str:
        return f'<circle radius="{circle.radius}"/>'

    def visit_square(self, square: Square) -> str:
        return f'<square side="{square.side}"/>'

    def visit_triangle(self, triangle: Triangle) -> str:
        return f'<triangle base="{triangle.base}" height="{triangle.height}"/>'


# ============================================================
# Implementation 2: Pythonic idiom (functools.singledispatch instead of accept()/visit_X())
# ============================================================
# Idea: Python's stdlib already gives you type-based dispatch without hand-rolling accept() on
# every element -- @singledispatch turns "one function, dispatched by the type of its first
# argument" into a decorator, and @<func>.register adds a new type's implementation without
# touching the base function or the shape classes at all. This drops the Element-side accept()
# method entirely: shapes stay plain data classes with zero knowledge that Visitor exists.
from functools import singledispatch
from dataclasses import dataclass


@dataclass
class Circle2:
    radius: float


@dataclass
class Square2:
    side: float


@dataclass
class Triangle2:
    base: float
    height: float


@singledispatch
def area(shape) -> float:
    raise TypeError(f"area: unsupported shape type {type(shape).__name__}")


@area.register
def _(shape: Circle2) -> float:
    return math.pi * shape.radius**2


@area.register
def _(shape: Square2) -> float:
    return shape.side**2


@area.register
def _(shape: Triangle2) -> float:
    return 0.5 * shape.base * shape.height


@singledispatch
def to_xml(shape) -> str:
    raise TypeError(f"to_xml: unsupported shape type {type(shape).__name__}")


@to_xml.register
def _(shape: Circle2) -> str:
    return f'<circle radius="{shape.radius}"/>'


@to_xml.register
def _(shape: Square2) -> str:
    return f'<square side="{shape.side}"/>'


@to_xml.register
def _(shape: Triangle2) -> str:
    return f'<triangle base="{shape.base}" height="{shape.height}"/>'


# ============================================================
# Key Takeaways
# ============================================================
# - Visitor trades one kind of extensibility for the opposite of the other: new OPERATIONS are
#   free (add a Visitor/register a function), but new ELEMENT TYPES are expensive (every existing
#   Visitor needs a new visit_X / every singledispatch function needs a new @register) -- pick it
#   only when your element types are the stable side of that trade.
# - "Double dispatch" just means the method that ultimately runs depends on TWO types (the
#   element's and the visitor's) instead of one -- accept()/visit_X() achieves that using nothing
#   but ordinary polymorphism, with no isinstance() anywhere.
# - functools.singledispatch collapses the classic pattern's two-sided class hierarchy
#   (Element.accept() + Visitor.visit_X()) into ordinary functions with type-based registration
#   -- the shape classes need not even know Visitor exists, which is a genuine simplification,
#   not just a rename.
# - Related pattern to compare: Iterator -- frequently paired with Visitor (Iterator supplies
#   traversal order over a structure, Visitor supplies what runs at each element).


if __name__ == "__main__":
    shapes_naive = [CircleNaive(3), SquareNaive(4), TriangleNaive(6, 5)]

    print("--- Anti-pattern: isinstance() chains duplicated across every operation ---")
    for s in shapes_naive:
        print(f"  {type(s).__name__}: area={area_naive(s):.2f}  xml={to_xml_naive(s)}")
    assert abs(area_naive(shapes_naive[0]) - math.pi * 9) < 1e-9

    print("\n--- Classic: accept()/visit_X() double dispatch, zero isinstance() ---")
    shapes: list[Shape] = [Circle(3), Square(4), Triangle(6, 5)]
    area_visitor = AreaVisitor()
    xml_visitor = XmlExportVisitor()
    for shape in shapes:
        a = shape.accept(area_visitor)
        x = shape.accept(xml_visitor)
        print(f"  {type(shape).__name__}: area={a:.2f}  xml={x}")

    assert abs(shapes[0].accept(area_visitor) - math.pi * 9) < 1e-9
    assert shapes[1].accept(area_visitor) == 16
    assert shapes[2].accept(area_visitor) == 15.0
    assert shapes[1].accept(xml_visitor) == '<square side="4"/>'

    # Add a brand-new operation without touching Circle/Square/Triangle at all:
    class DescribeVisitor(ShapeVisitor):
        def visit_circle(self, circle: Circle) -> str:
            return f"a circle of radius {circle.radius}"

        def visit_square(self, square: Square) -> str:
            return f"a square with side {square.side}"

        def visit_triangle(self, triangle: Triangle) -> str:
            return f"a triangle with base {triangle.base} and height {triangle.height}"

    describe_visitor = DescribeVisitor()
    print("  new DescribeVisitor operation, added without editing any Shape class:")
    for shape in shapes:
        print(f"    {shape.accept(describe_visitor)}")
    assert "circle" in shapes[0].accept(describe_visitor)

    print("\n--- Pythonic: functools.singledispatch, shapes know nothing about Visitor ---")
    shapes2 = [Circle2(3), Square2(4), Triangle2(6, 5)]
    for shape in shapes2:
        print(f"  {type(shape).__name__}: area={area(shape):.2f}  xml={to_xml(shape)}")

    assert abs(area(shapes2[0]) - math.pi * 9) < 1e-9
    assert area(shapes2[1]) == 16
    assert to_xml(shapes2[2]) == '<triangle base="6" height="5"/>'

    print("\nAll three approaches compute identical areas/XML; only the classic and singledispatch")
    print("versions let you add a whole new operation without editing a single shape class.")
