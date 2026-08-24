"""
Design Patterns in Python — #8
Composite (Structural Pattern)

Intent
------
Compose objects into tree structures to represent part-whole hierarchies, and let client code
treat an individual object and a group of objects through the exact same interface. Composite
means the code that operates on "one file" and the code that operates on "an entire directory
tree of files and subdirectories" can be the literal same code, with no special-casing for
whether you're holding a leaf or a whole subtree.

Problem / Motivation
---------------------
Say you're building a filesystem-usage report: given a File, print its size; given a Directory,
sum the sizes of everything inside it, including nested subdirectories. The naive approach
writes a function that checks `isinstance(node, File)` vs `isinstance(node, Directory)` and
branches accordingly. That's manageable for one operation, but every new operation (print a
tree view, count files, find the largest file) needs its own `isinstance` branch pair, and every
branch has to correctly recurse into subdirectories by hand. The File/Directory type distinction
leaks into every single piece of client code that ever walks the tree, instead of living in one
place.

Structure
---------
Component defines the common interface both leaves and containers share (e.g. `size()`,
`display(indent)`). Leaf (File) implements Component directly with no children. Composite
(Directory) also implements Component, but additionally holds a list of child Components (which
may themselves be Leaves or further Composites) and implements each operation by delegating to
and combining the results of its children. Client code holds a `Component` reference and calls
`size()` or `display()` on it without ever needing to know whether it's holding a single File or
an entire Directory subtree — the recursion is entirely internal to Composite.

When to Use
-----------
- Your data is naturally a part-whole tree (filesystem, UI widget hierarchy, org chart,
  nested menu, AST/expression tree) and you want operations to work uniformly whether applied to
  one node or an entire subtree.
- You want client code to stop caring about "is this a leaf or a group" — that check, and the
  recursion it implies, should live in exactly one place (the Composite), not scattered across
  every caller.

When NOT to Use
----------------
- If your data isn't actually hierarchical (no meaningful "contains" relationship), Composite
  adds a tree structure and a shared interface for no real benefit — a flat collection is
  simpler and clearer.
- Making every operation available on both Leaf and Composite can force awkward no-op or
  raise-NotImplementedError methods on Leaf for operations that only make sense on containers
  (e.g. `add_child()`) — that's a real cost of full interface uniformity, worth naming rather
  than hiding.

Related / Commonly Confused Patterns
--------------------------------------
- Decorator: also a recursive, self-referential object structure (an object wrapping an object
  of the same interface), but Decorator always wraps exactly *one* object to add behavior;
  Composite holds *zero or more* children to represent a part-whole tree.
- Visitor: frequently paired with Composite to add new operations over a tree (print, sum,
  search) without editing every Component subclass each time — Composite defines the tree shape,
  Visitor defines an external operation that walks it.
- Iterator: often used to traverse a Composite's tree without exposing its internal recursive
  structure to the client doing the traversal.
"""


# ============================================================
# Anti-pattern: the naive way, and why it hurts
# ============================================================
# Client code has to know the concrete type of every node and branch on it. Every new operation
# needs its own isinstance-based traversal, and it's easy to forget to recurse correctly into
# nested subdirectories in one of the branches.
class FileNaive:
    def __init__(self, name: str, size_kb: int):
        self.name = name
        self.size_kb = size_kb


class DirectoryNaive:
    def __init__(self, name: str):
        self.name = name
        self.children = []  # list of FileNaive or DirectoryNaive


def total_size_naive(node) -> int:
    if isinstance(node, FileNaive):
        return node.size_kb
    elif isinstance(node, DirectoryNaive):
        total = 0
        for child in node.children:
            total += total_size_naive(child)  # every operation re-implements this recursion
        return total
    else:
        raise TypeError(f"unknown node type: {type(node)}")
    # A second operation (e.g. "print a tree view") means writing this exact isinstance/recurse
    # dance all over again from scratch.


# ============================================================
# Implementation 1: Classic (OOP / GoF-style)
# ============================================================
# Component is the shared interface; File is the Leaf, Directory is the Composite. Client code
# calls size()/display() on a plain Component reference — it never needs an isinstance check,
# because Directory's implementation of each method already does the recursing internally.
from abc import ABC, abstractmethod


class Component(ABC):
    @abstractmethod
    def size(self) -> int:
        """Total size in KB — a single file's size, or the sum over an entire subtree."""
        raise NotImplementedError

    @abstractmethod
    def display(self, indent: int = 0) -> str:
        raise NotImplementedError


class File(Component):
    """Leaf: no children, operations act only on itself."""

    def __init__(self, name: str, size_kb: int):
        self.name = name
        self.size_kb = size_kb

    def size(self) -> int:
        return self.size_kb

    def display(self, indent: int = 0) -> str:
        return "  " * indent + f"- {self.name} ({self.size_kb} KB)"


class Directory(Component):
    """Composite: holds children (Files and/or further Directories), delegates to them."""

    def __init__(self, name: str):
        self.name = name
        self._children: list[Component] = []

    def add(self, component: Component) -> "Directory":
        self._children.append(component)
        return self  # allow chaining .add(...).add(...) when building a tree

    def size(self) -> int:
        # Recursion lives here, and only here — client code never has to reimplement it.
        return sum(child.size() for child in self._children)

    def display(self, indent: int = 0) -> str:
        lines = ["  " * indent + f"+ {self.name}/ ({self.size()} KB total)"]
        for child in self._children:
            lines.append(child.display(indent + 1))
        return "\n".join(lines)


# ============================================================
# Key Takeaways
# ============================================================
# - Composite's payoff is uniformity: client code holds one Component reference and never
#   branches on leaf-vs-container — the recursive fan-out lives entirely inside the Composite's
#   own method implementations.
# - No separate "Pythonic" implementation is included here: the whole value of Composite IS the
#   shared-interface tree structure itself — there's no meaningfully distinct alternative angle
#   (a dict-of-dicts could represent similar nesting, but then you lose the shared behavior
#   interface that's the entire point of the pattern, so it wouldn't be a genuine alternative).
# - Common misuse: forcing container-only operations (like add_child) onto the shared Component
#   interface just for uniformity — that makes Leaf either implement a nonsensical method or
#   raise, which is its own kind of interface pollution worth watching for.
# - Related pattern to compare: Decorator — structurally similar (self-referential, same
#   interface) but wraps exactly one object to add behavior, rather than holding many children
#   to represent a whole.


if __name__ == "__main__":
    print("--- Anti-pattern: isinstance branching required at every call site ---")
    naive_root = DirectoryNaive("project")
    naive_root.children.append(FileNaive("readme.md", 4))
    naive_src = DirectoryNaive("src")
    naive_src.children.append(FileNaive("main.py", 12))
    naive_root.children.append(naive_src)
    print(f"  total size via isinstance-branching function: {total_size_naive(naive_root)} KB")

    print("\n--- Classic Composite: uniform Component interface, no isinstance anywhere ---")
    root = Directory("project")
    root.add(File("readme.md", 4))
    root.add(File("setup.cfg", 1))

    src = Directory("src")
    src.add(File("main.py", 12))
    src.add(File("utils.py", 8))

    tests = Directory("tests")
    tests.add(File("test_main.py", 6))
    src.add(tests)  # nested Composite inside a Composite — still just a Component to 'src'

    root.add(src)

    print(root.display())
    print(f"\n  root.size() = {root.size()} KB")
    print(f"  a single leaf, File('readme.md').size() = {File('readme.md', 4).size()} KB")

    # The point: the SAME method call works identically on a lone leaf and an entire subtree.
    def report_size(component: Component) -> int:
        return component.size()

    assert report_size(File("solo.txt", 3)) == 3
    assert report_size(root) == sum(
        [4, 1, 12, 8, 6]
    )  # readme + setup.cfg + main.py + utils.py + test_main.py
    assert root.size() == src.size() + 4 + 1  # src subtree + root's own two direct files

    print("\nComposite let client code treat a single File and a whole Directory tree alike.")
