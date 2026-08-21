"""
LeetCode Top Interview 150 — #55 (LeetCode #150)
Evaluate Reverse Polish Notation
Category: Stack | Difficulty: Medium

Problem
-------
You are given an array of strings `tokens` that represents an arithmetic expression in Reverse
Polish Notation (postfix notation).

Evaluate the expression. Return an integer that represents the value of the expression.

Note that:
- The valid operators are '+', '-', '*', and '/'.
- Each operand may be an integer or another expression's already-computed result.
- Division between two integers always truncates toward zero.
- There will not be any division by zero.
- The input represents a valid arithmetic expression in a reverse polish notation.
- The answer and all intermediate calculations can be represented in a 32-bit integer.

Constraints
-----------
- 1 <= tokens.length <= 10^4
- tokens[i] is either an operator: "+", "-", "*", or "/", or an integer in the range
  [-200, 200].

Examples
--------
Example 1:
    Input: tokens = ["2","1","+","3","*"]
    Output: 9
    Explanation: ((2 + 1) * 3) = 9

Example 2:
    Input: tokens = ["4","13","5","/","+"]
    Output: 6
    Explanation: (4 + (13 / 5)) = 6

Example 3:
    Input: tokens = ["10","6","2","3","*","1","-","4","2","-","/","2","-"]
    Output: 1

Intuition
---------
Postfix notation is built specifically so it never needs parentheses or operator-precedence
rules: an operator always applies to the two operands that immediately precede it in the token
stream. That "two most recent operands" phrasing is a direct match for a stack: scan tokens
left to right, push every number, and whenever an operator is seen, pop the top two numbers
(the second-popped is the left operand, the first-popped is the right operand, since they were
pushed in that order), apply the operator, and push the result back so it becomes available as
an operand for a later operator. There's no meaningfully different brute-force strategy here —
postfix evaluation *is* the stack algorithm; trying to evaluate it any other way (e.g. converting
back to infix with parentheses first) would be strictly more complex for no benefit, so only one
approach is given below.
"""

from typing import List


# ============================================================
# Approach 1: Optimal (single stack)
# ============================================================
# Idea: push operands; on an operator, pop the two most recent operands,
# apply the operator (right operand is popped first, left operand second),
# and push the result back onto the stack.
# Dry run: tokens = ["4","13","5","/","+"]
#   "4"  -> push -> stack=[4]
#   "13" -> push -> stack=[4,13]
#   "5"  -> push -> stack=[4,13,5]
#   "/"  -> pop 5 (right), pop 13 (left) -> 13/5 -> truncate toward 0 -> 2
#           -> push 2 -> stack=[4,2]
#   "+"  -> pop 2 (right), pop 4 (left) -> 4+2=6 -> push 6 -> stack=[6]
#   final stack has one value -> 6
# Time:  O(n) — each token pushed/popped once
# Space: O(n) — stack holds up to ~n/2 operands
def solve_optimal(tokens: List[str]) -> int:
    stack: List[int] = []
    operators = {"+", "-", "*", "/"}
    for tok in tokens:
        if tok in operators:
            right = stack.pop()
            left = stack.pop()
            if tok == "+":
                result = left + right
            elif tok == "-":
                result = left - right
            elif tok == "*":
                result = left * right
            else:
                # Python's // floors toward -inf; the problem requires
                # truncation toward zero, so use int(a / b) semantics via
                # explicit truncating division.
                result = int(left / right)
            stack.append(result)
        else:
            stack.append(int(tok))
    return stack[-1]


# ============================================================
# Key Takeaways
# ============================================================
# - Postfix (RPN) expressions are the canonical "obviously a stack"
#   problem: no precedence rules or parentheses needed because operand
#   order + a stack already encodes evaluation order.
# - Common mistake: swapping the operand order on subtraction/division —
#   the second popped value is the LEFT operand, the first popped is the
#   RIGHT operand, since operands are pushed left-to-right and popped
#   LIFO. Also, Python's `//` floors instead of truncating toward zero,
#   which silently gives wrong answers on negative division.
# - Related/variant problems to try next: Basic Calculator, Basic
#   Calculator II, Different Ways to Add Parentheses.


if __name__ == "__main__":
    tests = [
        ((["2", "1", "+", "3", "*"],), 9),
        ((["4", "13", "5", "/", "+"],), 6),
        ((["10", "6", "2", "3", "*", "1", "-", "4", "2", "-", "/", "2", "-"],), 0),
        ((["18"],), 18),
        ((["4", "-2", "/"],), -2),
        ((["-7", "-3", "+"],), -10),
    ]

    approaches = [solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:65s} -> {result!r}  [{status}]")
