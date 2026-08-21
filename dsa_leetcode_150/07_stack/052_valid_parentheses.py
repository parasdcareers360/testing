"""
LeetCode Top Interview 150 — #52 (LeetCode #20)
Valid Parentheses
Category: Stack | Difficulty: Easy

Problem
-------
Given a string `s` containing just the characters '(', ')', '{', '}', '[' and ']', determine if
the input string is valid.

An input string is valid if:
1. Open brackets must be closed by the same type of bracket.
2. Open brackets must be closed in the correct order.
3. Every close bracket has a corresponding open bracket of the same type.

Constraints
-----------
- 1 <= s.length <= 10^4
- s consists of parentheses only: '()[]{}'

Examples
--------
Example 1:
    Input: s = "()"
    Output: true

Example 2:
    Input: s = "()[]{}"
    Output: true

Example 3:
    Input: s = "(]"
    Output: false

Example 4:
    Input: s = "([])"
    Output: true

Intuition
---------
Every time we see a closing bracket, it must cancel out the *most recently opened*, *still
unclosed* bracket — that "most recent first" behavior is exactly a stack (LIFO). Push every
opening bracket; when a closing bracket arrives, it must match whatever is on top of the stack
right now. If it doesn't match (wrong type) or the stack is empty (nothing to close), the string
is invalid immediately. At the end, the stack must be empty — any leftover opening brackets were
never closed. There isn't a meaningfully different "brute force" here (the only real alternative,
repeatedly deleting adjacent matched pairs like "()" or "[]" from the string until nothing
changes, is just a slower, string-mutating simulation of the same stack idea), so it's included
below purely as a naive baseline contrast.
"""


# ============================================================
# Approach 1: Brute Force (repeated string reduction)
# ============================================================
# Idea: repeatedly strip any adjacent matched pair ("()", "[]", "{}") from
# the string until no more pairs can be removed. Valid iff the string ends
# up empty. This simulates a stack using string slicing instead of a real
# stack, so it's correct but far more expensive.
# Time:  O(n^2) — each pass scans the string and removal shifts characters
# Space: O(n) — new string created each pass
def solve_brute_force(s: str) -> bool:
    pairs = ("()", "[]", "{}")
    changed = True
    while changed:
        changed = False
        for p in pairs:
            if p in s:
                s = s.replace(p, "")
                changed = True
    return s == ""


# ============================================================
# Approach 2: Optimal (stack)
# ============================================================
# Idea: push opening brackets; on a closing bracket, pop and check it
# matches the expected opener. Empty stack at the end means everything
# was closed.
# Dry run: s = "([])"
#   '(' -> push '(' -> stack=['(']
#   '[' -> push '[' -> stack=['(','[']
#   ']' -> pop '[' -> matches ']' -> stack=['(']
#   ')' -> pop '(' -> matches ')' -> stack=[]
#   stack empty -> True
# Time:  O(n) — single pass, each char pushed/popped at most once
# Space: O(n) — worst case all opening brackets (e.g. "((((")
def solve_optimal(s: str) -> bool:
    closing_to_opening = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in s:
        if ch in closing_to_opening:
            if not stack or stack.pop() != closing_to_opening[ch]:
                return False
        else:
            stack.append(ch)
    return not stack


# ============================================================
# Key Takeaways
# ============================================================
# - "Most recent unmatched thing must be resolved first" is the classic
#   signal for a stack: nested/paired structures (brackets, HTML tags,
#   recursive call frames) all share this LIFO matching property.
# - Common mistake: forgetting to check for an empty stack before popping
#   (a lone closing bracket like ")" would otherwise crash or be missed),
#   and forgetting to check the stack is empty at the very end (unclosed
#   openers like "(()" would otherwise wrongly report valid).
# - Related/variant problems to try next: Generate Parentheses, Longest
#   Valid Parentheses, Remove Invalid Parentheses, Simplify Path.


if __name__ == "__main__":
    tests = [
        (("()",), True),
        (("()[]{}",), True),
        (("(]",), False),
        (("([])",), True),
        (("(",), False),
        (("]",), False),
        (("([)]",), False),
        (("{[]}",), True),
        (("",), True),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:20s} -> {result!r}  [{status}]")
