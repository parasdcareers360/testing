"""
LeetCode Top Interview 150 — #17 (LeetCode #13)
Roman to Integer
Category: Array / String | Difficulty: Easy

Problem
-------
Roman numerals are represented by seven symbols: I=1, V=5, X=10, L=50, C=100, D=500, M=1000.
Normally symbols are combined left-to-right largest-to-smallest and their values summed (e.g.
II = 2, XII = 12), but six specific cases use subtraction instead: IV=4, IX=9, XL=40, XC=90,
CD=400, CM=900 (a smaller-value symbol placed immediately before a larger one is subtracted).

Given a roman numeral string `s`, convert it to an integer.

Constraints
-----------
- 1 <= s.length <= 15
- s contains only the characters ('I', 'V', 'X', 'L', 'C', 'D', 'M')
- It is guaranteed that `s` is a valid roman numeral in the range [1, 3999]

Examples
--------
Example 1:
    Input: s = "III"
    Output: 3

Example 2:
    Input: s = "LVIII"
    Output: 58
    Explanation: L = 50, V = 5, III = 3.

Example 3:
    Input: s = "MCMXCIV"
    Output: 1994
    Explanation: M = 1000, CM = 900, XC = 90, IV = 4.

Intuition
---------
A roman numeral has no meaningful "brute force vs optimal" split — the whole problem is a single
linear scan with a lookup table, so there isn't a slower alternative worth contrasting against a
faster one; the only real design choice is *how* you detect the subtractive cases. One way is to
look ahead: compare each symbol's value to the value right after it, and subtract instead of add
whenever the next symbol is larger (IV: I=1 is less than V=5, so subtract 1 instead of adding it).
An equally clean alternative scans right-to-left and simply subtracts whenever the current symbol
is smaller than the running maximum seen so far from the right — that maximum "remembers" whether
a bigger symbol is still to come without needing an explicit lookahead index.
"""


# ============================================================
# Approach 1: Left-to-right with lookahead
# ============================================================
# Idea: map each symbol to its value; scan left to right, and whenever the
# current symbol's value is less than the *next* symbol's value, it's a
# subtractive pair (like IV or CM) so subtract it instead of adding it.
# Time:  O(n) — single pass over the string
# Space: O(1) — fixed-size lookup table
def solve_lookahead(s: str) -> int:
    values = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total = 0
    n = len(s)
    for i in range(n):
        curr = values[s[i]]
        if i + 1 < n and curr < values[s[i + 1]]:
            total -= curr
        else:
            total += curr
    return total


# ============================================================
# Approach 2: Right-to-left with running max
# ============================================================
# Idea: scan from the end. Track the largest value seen so far (from the
# right). If the current symbol's value is smaller than that running max,
# a bigger symbol appears later in the string (to its right), meaning this
# is a subtractive case, so subtract; otherwise add and update the max.
# Dry run: s="MCMXCIV"
#   V=5: max=0 -> 5>=0 -> total=5, max=5
#   I=1: 1<5 -> subtractive -> total=5-1=4
#   C=100: 100>=5 -> total=104, max=100
#   X=10: 10<100 -> subtractive -> total=104-10=94
#   M=1000: 1000>=100 -> total=1094, max=1000
#   C=100: 100<1000 -> subtractive -> total=1094-100=994
#   M=1000: 1000>=1000 -> total=1994, max=1000
#   result: 1994
# Time:  O(n) — single pass over the string
# Space: O(1) — fixed-size lookup table
def solve_optimal(s: str) -> int:
    values = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total = 0
    max_seen = 0
    for ch in reversed(s):
        val = values[ch]
        if val < max_seen:
            total -= val
        else:
            total += val
            max_seen = val
    return total


# ============================================================
# Key Takeaways
# ============================================================
# - A "subtractive pair" in roman numerals is fully determined by local
#   comparison: a smaller symbol immediately followed by (or, scanning
#   backward, preceding) a larger one gets subtracted instead of added.
# - Common mistake: hardcoding the six two-letter subtractive pairs (IV, IX,
#   XL, XC, CD, CM) as string substitutions instead of using the general
#   "compare adjacent values" rule — the general rule is shorter and needs
#   no special-casing.
# - Related/variant problems to try next: Integer to Roman (the inverse
#   problem), Excel Sheet Column Number (another symbol-to-value mapping).


if __name__ == "__main__":
    tests = [
        (("III",), 3),
        (("LVIII",), 58),
        (("MCMXCIV",), 1994),
        (("IV",), 4),
        (("IX",), 9),
        (("MMMCMXCIX",), 3999),
        (("I",), 1),
    ]

    approaches = [solve_lookahead, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:25s} -> {result!r}  [{status}]")
