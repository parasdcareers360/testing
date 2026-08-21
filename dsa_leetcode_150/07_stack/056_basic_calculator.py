"""
LeetCode Top Interview 150 — #56 (LeetCode #224)
Basic Calculator
Category: Stack | Difficulty: Hard

Problem
-------
Given a string `s` representing a valid mathematical expression, implement a basic calculator to
evaluate it and return the result.

The expression may contain:
  - non-negative integers
  - '+' and '-' operators
  - '(' and ')' for grouping
  - spaces (which should be ignored)

There is no multiplication or division, and you may NOT use `eval()` (or any built-in expression
evaluator) — the whole point of the exercise is to parse and evaluate it yourself.

Constraints
-----------
- 1 <= s.length <= 3 * 10^5
- s consists of digits, '+', '-', '(', ')', and ' '.
- s represents a valid expression.
- '+' is not used as a unary operation (i.e. "+1" and "+(2 + 3)" are invalid).
- '-' may be used as a unary operation (i.e. "-1" and "-(2 + 3)" are valid).
- There is no ')' without a matching '(' and vice versa.
- All numbers in the input are in the range [0, 2^31 - 1].

Examples
--------
Example 1:
    Input: s = "1 + 1"
    Output: 2

Example 2:
    Input: s = "2-1 + 2"
    Output: 3

Example 3:
    Input: s = "(1+(4+5+2)-3)+(6+8)"
    Output: 23

Intuition
---------
There isn't a separate slower "brute force" worth writing here distinct from a direct parse — you
fundamentally have to read the expression once, character by character, tracking sign and nested
parentheses; there's no meaningfully different naive alternative the way there is for search or
counting problems (this is explicitly called out as an allowed exception in the style guide: "the
problem has no meaningful brute force distinct from the optimal approach"). The real design choice
is *how* to handle nested parentheses. The direct-but-clumsy way is recursion: whenever you hit
'(', recursively evaluate the sub-expression until its matching ')', then treat the recursive
result as a single number. That works but pays call-stack overhead and is a bit fiddly to get the
"where did the recursive call stop" bookkeeping right. The clean iterative trick is to use an
explicit stack to simulate that recursion: keep a running `result` and current `sign`; whenever we
hit '(', push the current `(result, sign)` onto the stack and reset them to start evaluating the
sub-expression fresh; whenever we hit ')', pop the saved `(result, sign)` and fold the completed
sub-expression's value back in as `saved_result + saved_sign * sub_result`. This avoids recursion
entirely while handling arbitrarily deep nesting in a single O(n) left-to-right pass.
"""

from typing import List


# ============================================================
# Approach 1: Optimal (explicit stack, single pass)
# ============================================================
# Idea: scan left to right maintaining a running result and the sign to
# apply to the next number. On '(', push (result-so-far, current sign) and
# reset to start the sub-expression fresh. On ')', pop the saved state and
# fold the completed sub-expression back in: result = saved_result +
# saved_sign * result.
# Dry run: s = "(1+(4+5+2)-3)+(6+8)"
#   '(' -> push (0,+1), reset result=0,sign=+1
#   '1' -> result=1
#   '+' -> sign=+1
#   '(' -> push (1,+1), reset result=0,sign=+1
#   '4+5+2' -> result=11
#   '-' -> sign=-1
#   '3' -> result=11-3=8
#   ')' -> pop (1,+1) -> result = 1 + 1*8 = 9
#   ')' -> (outer) pop (0,+1) -> result = 0 + 1*9 = 9
#   '+' -> sign=+1
#   '(' -> push (9,+1), reset result=0,sign=+1
#   '6+8' -> result=14
#   ')' -> pop (9,+1) -> result = 9 + 1*14 = 23
# Time:  O(n) — each character processed once
# Space: O(n) — stack depth in the worst case of fully nested parentheses
def solve_optimal(s: str) -> int:
    stack: List[List[int]] = []  # each frame: [saved_result, saved_sign]
    result = 0
    sign = 1
    i = 0
    n = len(s)

    while i < n:
        ch = s[i]
        if ch.isdigit():
            num = 0
            while i < n and s[i].isdigit():
                num = num * 10 + int(s[i])
                i += 1
            result += sign * num
            continue  # already advanced i past the number
        elif ch == '+':
            sign = 1
        elif ch == '-':
            sign = -1
        elif ch == '(':
            stack.append([result, sign])
            result, sign = 0, 1
        elif ch == ')':
            saved_result, saved_sign = stack.pop()
            result = saved_result + saved_sign * result
        # spaces: nothing to do
        i += 1

    return result


# ============================================================
# Approach 2: Alternate (recursion, mirrors the call stack explicitly)
# ============================================================
# Idea: same core parsing logic as Approach 1, but nested parentheses are
# handled with an actual recursive call (returning both the sub-expression's
# value and the index just past its closing ')') instead of a manual stack.
# Included to show the two are the same algorithm — one uses Python's own
# call stack, the other simulates it explicitly. Not a distinct complexity
# class, so this is presented as an alternate, not a "best".
# Time:  O(n) — each character processed once across all recursive calls
# Space: O(n) — recursion depth in the worst case of fully nested parens
def solve_recursive(s: str) -> int:
    def evaluate(i: int) -> tuple:
        result = 0
        sign = 1
        n = len(s)
        while i < n:
            ch = s[i]
            if ch.isdigit():
                num = 0
                while i < n and s[i].isdigit():
                    num = num * 10 + int(s[i])
                    i += 1
                result += sign * num
                continue
            elif ch == '+':
                sign = 1
                i += 1
            elif ch == '-':
                sign = -1
                i += 1
            elif ch == '(':
                sub_result, next_i = evaluate(i + 1)
                result += sign * sub_result
                i = next_i
            elif ch == ')':
                return result, i + 1
            else:  # space
                i += 1
        return result, i

    value, _ = evaluate(0)
    return value


# ============================================================
# Key Takeaways
# ============================================================
# - Parentheses evaluation is a natural fit for an explicit stack: "save
#   what I had before, start fresh, fold the sub-result back in on close"
#   is exactly how recursive descent parsing works, made iterative.
# - Common mistake: resetting `sign` to +1 on '(' but forgetting to also
#   reset `result` to 0 (or vice versa) — both must reset together, since
#   the sub-expression starts a brand-new accumulation.
# - Related/variant problems to try next: Basic Calculator II (adds * and
#   /, no parentheses), Basic Calculator III (combines both — full
#   expression grammar), Evaluate Reverse Polish Notation.


if __name__ == "__main__":
    tests = [
        (("1 + 1",), 2),
        (("2-1 + 2",), 3),
        (("(1+(4+5+2)-3)+(6+8)",), 23),
        (("- (3 + (4 + 5))",), -12),
        (("2147483647",), 2147483647),
        (("1-(     -2)",), 3),
        (("(1)",), 1),
        (("0",), 0),
    ]

    approaches = [solve_optimal, solve_recursive]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:35s} -> {result!r}  [{status}]")
