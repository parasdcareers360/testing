"""
Design Patterns in Python — #18
Memento (Behavioral Pattern)

Intent
------
Capture and externalize an object's internal state so it can be restored to that state later,
without violating the object's encapsulation — the code holding onto the saved state (the
history) should not be able to see or fiddle with what's inside it. The object being saved is
the only thing that knows how to produce a snapshot of itself and how to restore from one; the
history-keeper just stores opaque snapshots and hands them back on request.

Problem / Motivation
---------------------
Picture a text editor that needs an undo feature. The obvious first instinct is to make the
editor expose every piece of its internal state — `get_text()`, `set_text()`, `get_cursor()`,
`set_cursor()` — so that some external `UndoHistory` object can read the current state before an
edit and write it back on undo. That "works," but now the editor's entire internal
representation is part of its public API purely to serve undo — any other code can also call
`set_text()`/`set_cursor()` directly and corrupt the editor's state, and if the editor later adds
new internal fields (say, a selection range), every place that manually saves/restores state has
to be found and updated too. The undo feature has forced the editor to give up control over its
own internals.

Structure
---------
The Originator (the object whose state changes over time) knows how to produce a Memento — a
snapshot of its own state — and how to restore itself from one. The Memento exposes no public
way for outside code to read or modify what it holds; only the Originator that created it can
unpack it. The Caretaker (e.g. an undo history) stores a sequence of Mementos and can hand one
back to the Originator to restore, but never looks inside them or manipulates their contents.

When to Use
-----------
- You need to save and restore an object's state (undo/redo, checkpoints, save games,
  rollback-on-failure transactions) without exposing that state's internal representation to the
  code managing the history.
- You want snapshots to be truly opaque to the history-keeper, so the Originator is free to
  change its internal representation later without breaking anything that manages the history.

When NOT to Use
----------------
- If the object's state is already simple, immutable, and fine to expose (a plain dataclass with
  no invariants to protect), just copy it directly — Memento's encapsulation guarantees aren't
  buying you anything.
- Storing a full snapshot on every change can be expensive for large objects; if state changes
  are naturally expressible as small reversible operations instead, consider Command (undo via
  "do the inverse operation") rather than storing whole-object snapshots.

Related / Commonly Confused Patterns
--------------------------------------
- Command: both commonly support undo, but they undo differently — Command undoes by running an
  inverse *operation*, Memento undoes by restoring a previously captured *state* snapshot. They
  can be combined (a Command stores a Memento of the state it's about to change).
- Prototype: both involve copying an object's state, but Prototype's `clone()` produces a new,
  fully-independent, usable object of the same type; a Memento is an opaque, typically
  unusable-on-its-own capsule whose only purpose is to be handed back to its Originator later.
"""


# ============================================================
# Anti-pattern: the naive way, and why it hurts
# ============================================================
# The editor exposes get/set for every piece of its internal state purely so an external
# UndoHistory can save and restore it. Now ANYTHING can call set_text()/set_cursor() directly
# and corrupt the editor's state -- the undo feature has forced internals to become public API,
# and if the editor grows a new field (e.g. a selection range) every external save/restore site
# has to be found and updated.
class TextEditorNaive:
    def __init__(self):
        self.text = ""
        self.cursor = 0

    def type_text(self, s: str) -> None:
        self.text = self.text[: self.cursor] + s + self.text[self.cursor :]
        self.cursor += len(s)


class UndoHistoryNaive:
    def __init__(self):
        self._snapshots: list[tuple[str, int]] = []

    def save(self, editor: TextEditorNaive) -> None:
        # Reaches directly into editor internals -- nothing stops it from also being *written*.
        self._snapshots.append((editor.text, editor.cursor))

    def undo(self, editor: TextEditorNaive) -> None:
        if self._snapshots:
            editor.text, editor.cursor = self._snapshots.pop()


# ============================================================
# Implementation 1: Classic (OOP / GoF-style, opaque Memento + Originator + Caretaker)
# ============================================================
# Idea: the Memento's state fields are name-mangled (double underscore) so nothing outside
# TextEditor can read or write them -- only TextEditor itself (via the mangled name, which
# Python resolves relative to the *defining* class) can unpack a memento it created. The
# Caretaker (UndoHistory) only ever calls save()/restore() on the editor; it never touches a
# memento's contents.
from abc import ABC, abstractmethod


class Memento(ABC):
    """Marker interface: deliberately exposes NOTHING -- not even a way to name what's inside."""


class _TextEditorMemento(Memento):
    def __init__(self, text: str, cursor: int):
        # Leading double-underscore -> name-mangled to _TextEditorMemento__text, unreachable by
        # accident from outside this class, including from TextEditor (a different class) unless
        # TextEditor explicitly asks this class to hand the state back via a defined method.
        self.__text = text
        self.__cursor = cursor

    def _state(self) -> tuple[str, int]:
        # Deliberately "hidden" (leading underscore = internal-use convention): only meant to be
        # called by the Originator that produced this memento, never by the Caretaker.
        return self.__text, self.__cursor


class TextEditor:
    """The Originator: the only object that knows how to create or unpack its own Mementos."""

    def __init__(self):
        self._text = ""
        self._cursor = 0

    def type_text(self, s: str) -> None:
        self._text = self._text[: self._cursor] + s + self._text[self._cursor :]
        self._cursor += len(s)

    @property
    def text(self) -> str:
        return self._text

    def save(self) -> Memento:
        return _TextEditorMemento(self._text, self._cursor)

    def restore(self, memento: Memento) -> None:
        if not isinstance(memento, _TextEditorMemento):
            raise TypeError("restore() requires a memento created by this TextEditor")
        self._text, self._cursor = memento._state()


class UndoHistory:
    """The Caretaker: stores opaque Mementos, never looks inside them."""

    def __init__(self):
        self._history: list[Memento] = []

    def record(self, memento: Memento) -> None:
        self._history.append(memento)

    def undo(self) -> Memento | None:
        return self._history.pop() if self._history else None


# ============================================================
# Implementation 2: Pythonic idiom (immutable snapshot via copy.deepcopy + a plain list)
# ============================================================
# Idea: rather than hand-building an opaque Memento class, capture state as a `dataclass(frozen=
# True)` snapshot produced by copy.deepcopy, and store a plain list of them. Encapsulation still
# holds -- the frozen dataclass can't be mutated even if a caller peeks at it -- but there's no
# name-mangling trick and no separate Memento class hierarchy: the "memento" is just an immutable
# value object, which is a natural fit for Python's dataclasses instead of translated Java.
from copy import deepcopy
from dataclasses import dataclass, field


@dataclass(frozen=True)
class GameCheckpoint:
    level: int
    inventory: tuple[str, ...]
    health: int


class GameCharacter:
    """The Originator, working with plain (frozen, hence safe) snapshots."""

    def __init__(self):
        self.level = 1
        self.inventory: list[str] = []
        self.health = 100

    def save_checkpoint(self) -> GameCheckpoint:
        # deepcopy protects against the inventory list being mutated later out from under the
        # snapshot -- the checkpoint is a true point-in-time copy, not a live reference.
        return GameCheckpoint(self.level, tuple(deepcopy(self.inventory)), self.health)

    def load_checkpoint(self, checkpoint: GameCheckpoint) -> None:
        self.level = checkpoint.level
        self.inventory = list(checkpoint.inventory)
        self.health = checkpoint.health


@dataclass
class CheckpointHistory:
    """The Caretaker -- just a list; a frozen dataclass needs no protection from the outside."""

    checkpoints: list[GameCheckpoint] = field(default_factory=list)

    def record(self, checkpoint: GameCheckpoint) -> None:
        self.checkpoints.append(checkpoint)

    def undo(self) -> GameCheckpoint | None:
        return self.checkpoints.pop() if self.checkpoints else None


# ============================================================
# Key Takeaways
# ============================================================
# - The point of Memento isn't just "save some state" -- it's saving state WITHOUT the
#   history-keeper being able to read or mutate it. That's why the classic implementation goes
#   out of its way to make the memento opaque (name-mangled fields, only unpacked by the
#   Originator that made it).
# - A frozen dataclass is a very natural Pythonic memento: immutability alone stops the Caretaker
#   from corrupting it, so you don't need name-mangling tricks to get the same safety guarantee.
# - Common misuse: storing a *live reference* to mutable internal state instead of a real copy
#   (e.g. saving `editor.text` if it were a mutable list) -- that's not a snapshot at all, it's
#   an alias, and later mutation silently corrupts "saved" history. Always copy.
# - Related pattern to compare: Command -- both support undo, but Command undoes by running an
#   inverse operation, Memento undoes by restoring a captured snapshot; they combine well (a
#   Command can carry the Memento of the state it's about to overwrite).


if __name__ == "__main__":
    print("--- Anti-pattern: UndoHistory reaches directly into editor internals ---")
    ed_n = TextEditorNaive()
    hist_n = UndoHistoryNaive()
    hist_n.save(ed_n)
    ed_n.type_text("Hello")
    hist_n.save(ed_n)
    ed_n.type_text(", world")
    print(f"  text before undo: {ed_n.text!r}")
    hist_n.undo(ed_n)
    print(f"  text after undo:  {ed_n.text!r}")
    assert ed_n.text == "Hello"
    # Nothing stops arbitrary code from bypassing the API entirely -- that's the actual problem:
    ed_n.text = "CORRUPTED BY OUTSIDE CODE"
    assert ed_n.text == "CORRUPTED BY OUTSIDE CODE"
    print("  (and any code anywhere could just do `ed_n.text = ...` directly -- no protection)")

    print("\n--- Classic: TextEditor + opaque Memento + UndoHistory ---")
    editor = TextEditor()
    history = UndoHistory()
    history.record(editor.save())
    editor.type_text("Hello")
    history.record(editor.save())
    editor.type_text(", world")
    print(f"  text before undo: {editor.text!r}")
    editor.restore(history.undo())
    print(f"  text after undo:  {editor.text!r}")
    assert editor.text == "Hello"
    editor.restore(history.undo())
    assert editor.text == ""
    print(f"  text after second undo: {editor.text!r}")

    # Prove the memento is genuinely opaque -- there's no public way to read its state:
    m = editor.save()
    assert not hasattr(m, "text") and not hasattr(m, "_text")
    print("  memento exposes no public state attributes: OK (encapsulation holds)")

    print("\n--- Pythonic: GameCharacter + frozen-dataclass checkpoints ---")
    hero = GameCharacter()
    checkpoints = CheckpointHistory()
    checkpoints.record(hero.save_checkpoint())

    hero.level = 2
    hero.inventory.append("sword")
    hero.health = 80
    checkpoints.record(hero.save_checkpoint())

    hero.level = 3
    hero.inventory.append("shield")
    hero.health = 40
    print(f"  hero before rollback: level={hero.level}, inv={hero.inventory}, hp={hero.health}")

    hero.load_checkpoint(checkpoints.undo())
    print(f"  hero after 1 rollback: level={hero.level}, inv={hero.inventory}, hp={hero.health}")
    assert hero.level == 2 and hero.inventory == ["sword"] and hero.health == 80

    hero.load_checkpoint(checkpoints.undo())
    print(f"  hero after 2 rollbacks: level={hero.level}, inv={hero.inventory}, hp={hero.health}")
    assert hero.level == 1 and hero.inventory == [] and hero.health == 100

    # Prove checkpoints are true copies, not live references to hero.inventory:
    snap = hero.save_checkpoint()
    hero.inventory.append("potion")
    assert snap.inventory == ()  # unaffected by the later mutation -- a real snapshot
    print("  checkpoint snapshot unaffected by later mutation of hero.inventory: OK")

    print("\nBoth implementations restore prior state without letting the history-keeper")
    print("read or mutate what it's storing -- that opacity is the whole point of Memento.")
