"""
Design Patterns in Python — #14
Command (Behavioral Pattern)

Intent
------
Turn a request into a stand-alone object that carries everything needed to perform an action
(and, often, to undo it). Instead of the caller invoking a method directly on a receiver, it
invokes `execute()` on a Command object that wraps that call. This lets you queue commands,
log them, pass them around as values, and — crucially — support undo/redo, because the object
representing "what just happened" still exists after the action ran.

Problem / Motivation
---------------------
Think of a text editor with an undo button. If "type character" and "delete word" are just
direct method calls on the document (`doc.insert(...)`, `doc.delete_word(...)`), then by the
time the user hits Ctrl+Z, that information is gone — the call already returned, nothing
recorded what happened or how to reverse it. The naive fix people reach for is a growing
if/elif dispatcher keyed by action name, storing raw dicts of "what to undo", which quickly
turns into a parallel, error-prone shadow implementation of every operation, doubled — one path
to do the thing, another ad hoc path to figure out how to undo it later, and the two drift out
of sync as features are added.

Structure
---------
A Command object bundles a receiver reference plus whatever parameters the action needs, and
exposes a uniform `execute()` (and, where undo matters, `undo()`). An Invoker (the editor's
toolbar, a macro recorder, a remote control button) holds Commands and calls `execute()` without
knowing what concrete action it triggers. Because each executed Command is itself a value, an
Invoker can also keep a history stack of them and walk it backwards to undo.

When to Use
-----------
- You need undo/redo, a request queue, or a log/replay of actions — anything where "the action"
  needs to outlive the moment it was triggered.
- You want to parameterize UI components (buttons, menu items, macro keys) with an action
  without those components knowing anything about what the action does.
- You want to decouple the object that invokes an operation from the object that knows how to
  perform it (e.g. a generic "remote control" that can trigger arbitrary device actions).

When NOT to Use
----------------
- If you never need to queue, log, delay, or undo the action, wrapping a direct method call in a
  Command object is pure ceremony — just call the method.
- Undo support in particular has real cost: every command needs enough captured state to reverse
  itself correctly, which can mean deep-copying data the command touches. Don't add undo to
  operations nobody will ever want to undo.

Related / Commonly Confused Patterns
--------------------------------------
- Strategy: structurally near-identical (an object wrapping a bit of behavior), but intent
  differs — Strategy swaps *how* a fixed operation is done (interchangeable algorithms for the
  same goal); Command represents a request to *do something* as an object, often with undo and
  a history, which Strategy has no notion of.
- Memento: often used together with Command's undo — Memento captures a snapshot of receiver
  state, while Command captures the *action*; a command's undo() sometimes restores a Memento
  it took before executing.
"""

from abc import ABC, abstractmethod
from functools import partial


# ============================================================
# Anti-pattern: the naive way, and why it hurts
# ============================================================
# The editor dispatches on a string action name, and "undo" is a hand-rolled, hard-coded mirror
# of "do" that has to be kept in sync by hand. Add a new action (e.g. "replace") and you must
# remember to also add its undo branch here -- nothing forces that, and the two chains of logic
# for the same feature live nowhere near each other conceptually.
class TextDocumentNaive:
    def __init__(self):
        self.text = ""
        self._last_action = None
        self._last_args = None

    def perform(self, action: str, *args):
        if action == "insert":
            (text,) = args
            self.text += text
            self._last_action, self._last_args = "insert", (text,)
        elif action == "delete_last":
            (n,) = args
            removed = self.text[-n:] if n else ""
            self.text = self.text[:-n] if n else self.text
            self._last_action, self._last_args = "undelete", (removed,)
        else:
            raise ValueError(f"unknown action: {action}")

    def undo_last(self):
        if self._last_action == "insert":
            (text,) = self._last_args
            self.text = self.text[: -len(text)] if text else self.text
        elif self._last_action == "undelete":
            (removed,) = self._last_args
            self.text += removed
        # ^ this branch has to exactly mirror perform()'s branches, forever, by hand.


# ============================================================
# Implementation 1: Classic (OOP / GoF-style, Command objects with execute()/undo())
# ============================================================
# Idea: each editing action is its own object. It captures whatever state it needs to reverse
# itself the moment it's created/executed, so undo() never has to "figure out" what happened --
# it just replays the inverse of what this exact object already did.
class TextDocument:
    def __init__(self):
        self.text = ""


class Command(ABC):
    @abstractmethod
    def execute(self) -> None: ...

    @abstractmethod
    def undo(self) -> None: ...


class InsertCommand(Command):
    def __init__(self, doc: TextDocument, text: str):
        self._doc = doc
        self._text = text

    def execute(self) -> None:
        self._doc.text += self._text

    def undo(self) -> None:
        self._doc.text = self._doc.text[: -len(self._text)] if self._text else self._doc.text


class DeleteLastCommand(Command):
    def __init__(self, doc: TextDocument, n: int):
        self._doc = doc
        self._n = n
        self._removed = ""  # captured at execute() time, so undo() has exact data to restore

    def execute(self) -> None:
        self._removed = self._doc.text[-self._n :] if self._n else ""
        self._doc.text = self._doc.text[: -self._n] if self._n else self._doc.text

    def undo(self) -> None:
        self._doc.text += self._removed


class CommandInvoker:
    """The undo stack: doesn't know what a command *does*, only how to run/reverse it."""

    def __init__(self):
        self._history: list[Command] = []

    def run(self, command: Command) -> None:
        command.execute()
        self._history.append(command)

    def undo(self) -> None:
        if self._history:
            self._history.pop().undo()


# ============================================================
# Implementation 2: Pythonic idiom (plain closures / functools.partial as commands)
# ============================================================
# Idea: a "Command" doesn't have to be a class at all -- it can be a pair of plain callables,
# `(do, undo)`, produced by ordinary functions or functools.partial. Python's first-class
# functions and closures naturally capture the state a Command class would otherwise need
# fields for, so the ABC + subclass boilerplate above collapses into two small factory
# functions returning `(execute_fn, undo_fn)` tuples.
def make_insert(doc: TextDocument, text: str):
    def do():
        doc.text += text

    def undo():
        nonlocal text
        doc.text = doc.text[: -len(text)] if text else doc.text

    return do, undo


def make_delete_last(doc: TextDocument, n: int):
    removed = ""  # closed over by both do() and undo() -- no class fields needed

    def do():
        nonlocal removed
        removed = doc.text[-n:] if n else ""
        doc.text = doc.text[:-n] if n else doc.text

    def undo():
        doc.text += removed

    return do, undo


class FunctionalInvoker:
    def __init__(self):
        self._undo_stack: list = []

    def run(self, do_undo_pair) -> None:
        do, undo = do_undo_pair
        do()
        self._undo_stack.append(undo)

    def undo(self) -> None:
        if self._undo_stack:
            self._undo_stack.pop()()


# functools.partial variant: for a stateless receiver call with no undo needed (e.g. a "macro"
# remote-control button), you often don't even need a closure -- a bound partial IS the command.
def print_status(doc: TextDocument, label: str) -> None:
    print(f"    [{label}] current text: {doc.text!r}")


# ============================================================
# Key Takeaways
# ============================================================
# - The core idea is reifying a request: turning "call this method now" into "here is an object
#   (or callable) representing that call", which can be stored, queued, logged, or reversed
#   later -- that's what makes undo/redo and macro recording possible at all.
# - Common misuse: wrapping every method call in a Command class "for flexibility" when nothing
#   ever queues, logs, or undoes it -- that's just indirection with no payoff.
# - In Python, closures/functools.partial are frequently a lighter-weight Command than a class
#   hierarchy, since captured variables do the job of instance fields for free.
# - Related pattern to compare: Memento -- often paired with Command's undo() to snapshot and
#   restore receiver state, rather than (or alongside) replaying an inverse operation.


if __name__ == "__main__":
    print("--- Anti-pattern: hand-mirrored do/undo string dispatch ---")
    naive = TextDocumentNaive()
    naive.perform("insert", "Hello, ")
    naive.perform("insert", "World!")
    print(f"  text: {naive.text!r}")
    naive.undo_last()
    print(f"  after undo_last(): {naive.text!r}  <- only undoes the MOST RECENT action")
    assert naive.text == "Hello, "

    print("\n--- Classic: Command objects + Invoker with a real undo stack ---")
    doc = TextDocument()
    invoker = CommandInvoker()
    invoker.run(InsertCommand(doc, "Hello, "))
    invoker.run(InsertCommand(doc, "World!"))
    invoker.run(DeleteLastCommand(doc, 6))
    print(f"  text after insert/insert/delete: {doc.text!r}")
    assert doc.text == "Hello, "
    invoker.undo()  # undoes the delete
    print(f"  after 1 undo: {doc.text!r}")
    assert doc.text == "Hello, World!"
    invoker.undo()  # undoes the second insert
    invoker.undo()  # undoes the first insert
    print(f"  after 3 undos total: {doc.text!r}")
    assert doc.text == ""

    print("\n--- Pythonic: closures as commands, functools.partial for a fire-and-forget one ---")
    doc2 = TextDocument()
    finvoker = FunctionalInvoker()
    finvoker.run(make_insert(doc2, "abc"))
    finvoker.run(make_insert(doc2, "def"))
    print(f"  text: {doc2.text!r}")
    assert doc2.text == "abcdef"
    finvoker.undo()
    print(f"  after undo: {doc2.text!r}")
    assert doc2.text == "abc"

    status_button = partial(print_status, doc2, "status-check")
    status_button()  # a partial IS a fully-formed, parameterless command here

    print("\nBoth Command styles give real undo history -- unlike the anti-pattern, which can")
    print("only ever unwind the single most recent action.")
