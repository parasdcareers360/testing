"""
Stack & Monotonic Stack — reusable Python skeletons.

Not solutions to specific problems — these are the boilerplate shapes to recognize and adapt
quickly under interview time pressure. Copy the relevant shape into solutions/ and adapt it.
"""

from typing import List


# ---------------------------------------------------------------------------
# Shape 1: basic stack — matching / validation
# ---------------------------------------------------------------------------
def is_valid_parentheses_template(s: str) -> bool:
    pairs = {")": "(", "]": "[", "}": "{"}
    stack: List[str] = []
    for ch in s:
        if ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
        else:
            stack.append(ch)
    return not stack


# ---------------------------------------------------------------------------
# Shape 2: basic stack — expression evaluation (Reverse Polish Notation)
# ---------------------------------------------------------------------------
def eval_rpn_template(tokens: List[str]) -> int:
    stack: List[int] = []
    ops = {"+", "-", "*", "/"}
    for tok in tokens:
        if tok in ops:
            b, a = stack.pop(), stack.pop()
            if tok == "+":
                result = a + b
            elif tok == "-":
                result = a - b
            elif tok == "*":
                result = a * b
            else:
                result = int(a / b)  # truncate toward zero
            stack.append(result)
        else:
            stack.append(int(tok))
    return stack[-1]


# ---------------------------------------------------------------------------
# Shape 3: monotonic stack — next greater element (value payoff)
# ---------------------------------------------------------------------------
def next_greater_element_template(nums: List[int]) -> List[int]:
    result = [-1] * len(nums)
    stack: List[int] = []  # indices, values increasing from bottom to top
    for i, x in enumerate(nums):
        while stack and nums[stack[-1]] < x:
            result[stack.pop()] = x
        stack.append(i)
    return result


# ---------------------------------------------------------------------------
# Shape 4: monotonic stack — distance payoff (Daily Temperatures)
# ---------------------------------------------------------------------------
def daily_temperatures_template(temps: List[int]) -> List[int]:
    result = [0] * len(temps)
    stack: List[int] = []
    for i, t in enumerate(temps):
        while stack and temps[stack[-1]] < t:
            prev = stack.pop()
            result[prev] = i - prev
        stack.append(i)
    return result


if __name__ == "__main__":
    assert is_valid_parentheses_template("()[]{}") is True
    assert is_valid_parentheses_template("(]") is False
    assert is_valid_parentheses_template("([)]") is False
    assert is_valid_parentheses_template("{[]}") is True

    assert eval_rpn_template(["2", "1", "+", "3", "*"]) == 9
    assert eval_rpn_template(["4", "13", "5", "/", "+"]) == 6

    assert next_greater_element_template([2, 1, 2, 4, 3]) == [4, 2, 4, -1, -1]
    assert next_greater_element_template([1, 2, 3]) == [2, 3, -1]

    assert daily_temperatures_template([73, 74, 75, 71, 69, 72, 76, 73]) == [
        1, 1, 4, 2, 1, 1, 0, 0,
    ]

    print("All template shapes verified.")
