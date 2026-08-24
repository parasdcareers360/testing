"""
Design Patterns in Python — #15
Interpreter (Behavioral Pattern)

Intent
------
Given a small language (a grammar), represent each grammar rule as a class, and give that class
an `interpret()` method so that a sentence in the language can be evaluated by building a tree
of these objects and walking it. Interpreter is about turning a grammar directly into a class
hierarchy: one class per production rule, composed the same way the grammar itself composes.

Problem / Motivation
---------------------
Say a pricing system needs to evaluate small discount expressions like `"10 + 5 - 3"` that get
configured by non-programmers in a spreadsheet column, not hard-coded. The naive approach is a
single function that manually walks the string character-by-character (or token-by-token) with
nested if/elif, keeping track of "current running total" and "current operator" as loose local
variables. That works for `+`/`-` on flat sequences, but it doesn't scale: there's no real
structure to extend when someone asks for parentheses or multiplication, because the parsing and
the evaluating are smashed into one undifferentiated procedure with no tree to represent
"what was actually parsed" as data you could inspect, cache, or reuse.

Structure
---------
Each grammar rule becomes an Expression class implementing a common `interpret()` method.
Terminal rules (like a literal number) are TerminalExpression classes that just return their
value. Non-terminal rules (like "add two expressions") are NonterminalExpression classes that
hold references to their sub-expressions and combine the results of interpreting them
recursively. A sentence in the language becomes a tree built from these objects (the Abstract
Syntax Tree), and evaluating it is just calling `interpret()` on the root.

When to Use
-----------
- You have a small, well-defined grammar (arithmetic expressions, simple boolean rules, a tiny
  query filter language) that's worth representing as real structure, not just parsed once and
  thrown away.
- The grammar is simple enough that a class-per-rule hierarchy stays manageable — Interpreter is
  explicitly for *small* languages.

When NOT to Use
----------------
- For anything beyond a small grammar, Interpreter's one-class-per-rule approach becomes
  unwieldy fast — real language implementation reaches for parser generators, formal grammars,
  or existing expression libraries (or just Python's own `eval`/`ast` module for arithmetic-like
  needs) rather than hand-rolling more classes.
- If you just need to evaluate one specific, fixed expression rather than parse arbitrary
  sentences in a language, this is over-engineering — a plain function is enough.

Related / Commonly Confused Patterns
--------------------------------------
- Composite: Interpreter's expression tree *is* a Composite structure (a NonterminalExpression
  is a composite of other Expressions) — Interpreter specializes Composite specifically for
  representing and evaluating a grammar, rather than an arbitrary part-whole hierarchy.
- Visitor: a large expression tree is often traversed with a Visitor instead of putting more and
  more operations directly on the Expression classes themselves (e.g. adding a `pretty_print()`
  method to every Expression class vs. one PrettyPrintVisitor that knows how to handle each
  node type).

A note on Implementation 2: this file has no separate "Pythonic idiom" section. The recursive
tree of small classes IS the idiomatic way to represent a grammar in Python too — there's no
distinct alternative structure that captures "a composed AST with a recursive evaluation step"
more idiomatically than what's already below. (You could reach for Python's own `eval()` on a
string, but that solves a different problem — arbitrary code execution risk aside, it gives you
no inspectable tree, which is the entire point of this pattern.)
"""

from abc import ABC, abstractmethod


# ============================================================
# Anti-pattern: the naive way, and why it hurts
# ============================================================
# One function parses AND evaluates in the same pass, tracking a running total and a pending
# operator as loose local state. There is no tree -- nothing you could hold onto, cache, or
# extend. Adding parentheses or a new operator means rewriting the token-walking loop itself.
def evaluate_naive(expression: str) -> int:
    tokens = expression.split()
    total = int(tokens[0])
    i = 1
    while i < len(tokens):
        op = tokens[i]
        value = int(tokens[i + 1])
        if op == "+":
            total += value
        elif op == "-":
            total -= value
        else:
            raise ValueError(f"unsupported operator: {op}")
        i += 2
    return total


# ============================================================
# Implementation 1: Classic (OOP / GoF-style, an Expression class tree / AST)
# ============================================================
# Idea: one class per grammar rule. NumberExpression is a terminal (a leaf holding a literal
# value); AddExpression/SubtractExpression are nonterminals that each hold two child Expressions
# and combine their interpreted results. Parsing builds the tree once; interpret() is a plain
# recursive walk of that tree -- and the tree itself is a reusable, inspectable object, not a
# transient loop variable.
class Expression(ABC):
    @abstractmethod
    def interpret(self) -> int: ...


class NumberExpression(Expression):
    """Terminal expression: a leaf node holding a literal integer."""

    def __init__(self, value: int):
        self._value = value

    def interpret(self) -> int:
        return self._value

    def __repr__(self) -> str:
        return str(self._value)


class AddExpression(Expression):
    """Nonterminal expression: combines two sub-expressions with +."""

    def __init__(self, left: Expression, right: Expression):
        self._left = left
        self._right = right

    def interpret(self) -> int:
        return self._left.interpret() + self._right.interpret()

    def __repr__(self) -> str:
        return f"({self._left!r} + {self._right!r})"


class SubtractExpression(Expression):
    """Nonterminal expression: combines two sub-expressions with -."""

    def __init__(self, left: Expression, right: Expression):
        self._left = left
        self._right = right

    def interpret(self) -> int:
        return self._left.interpret() - self._right.interpret()

    def __repr__(self) -> str:
        return f"({self._left!r} - {self._right!r})"


def parse(expression: str) -> Expression:
    """
    Builds the Expression tree from a space-separated infix string like "3 + 5 - 2".
    Left-associative, no operator precedence beyond left-to-right (kept genuinely small, as the
    pattern calls for) -- but crucially, the *result* is a tree object, not just a number.
    """
    tokens = expression.split()
    tree: Expression = NumberExpression(int(tokens[0]))
    i = 1
    while i < len(tokens):
        op, operand = tokens[i], NumberExpression(int(tokens[i + 1]))
        if op == "+":
            tree = AddExpression(tree, operand)
        elif op == "-":
            tree = SubtractExpression(tree, operand)
        else:
            raise ValueError(f"unsupported operator: {op}")
        i += 2
    return tree


# ============================================================
# Key Takeaways
# ============================================================
# - Interpreter's payoff is having a real tree of objects that represents a parsed sentence --
#   that tree can be interpreted, but it could just as well be pretty-printed, optimized, or
#   analyzed, because it's data, not a transient stack of local variables in a parsing loop.
# - Common misuse: reaching for a class-per-rule hierarchy for a language complex enough that it
#   really needs a proper parser/grammar tool -- Interpreter only stays clean for genuinely
#   small grammars.
# - No separate Pythonic variant here: the recursive class-per-node tree already IS the
#   idiomatic Python structure for representing and walking a small AST.
# - Related pattern to compare: Composite -- the Expression tree is a Composite; Interpreter is
#   that same structure applied specifically to evaluating a grammar.


if __name__ == "__main__":
    print("--- Anti-pattern: parse-and-evaluate fused into one loop, no tree ---")
    print(f"  evaluate_naive('3 + 5 - 2') = {evaluate_naive('3 + 5 - 2')}")
    assert evaluate_naive("3 + 5 - 2") == 6

    print("\n--- Classic: build an Expression tree (AST), then interpret() it ---")
    tree = parse("3 + 5 - 2")
    print(f"  parsed tree: {tree!r}")
    print(f"  tree.interpret() = {tree.interpret()}")
    assert tree.interpret() == 6
    assert repr(tree) == "((3 + 5) - 2)"

    # Because the tree is a real object, it can be reused/reinterpreted without reparsing --
    # something the anti-pattern's fused loop has no way to offer.
    tree2 = parse("100 - 40 + 5")
    print(f"  parsed tree: {tree2!r} -> {tree2.interpret()}")
    assert tree2.interpret() == 65

    # Manually composing the tree directly (no parser at all) works identically, showing the
    # classes really do compose the way the grammar composes:
    manual = AddExpression(NumberExpression(10), SubtractExpression(NumberExpression(4), NumberExpression(1)))
    print(f"  hand-built tree: {manual!r} -> {manual.interpret()}")
    assert manual.interpret() == 13

    print("\nThe tree built by parse() is inspectable data (see the repr), not just a number --")
    print("that's what a one-shot evaluator loop can never give you.")
