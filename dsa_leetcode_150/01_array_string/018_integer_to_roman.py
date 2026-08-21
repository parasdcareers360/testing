"""
LeetCode Top Interview 150 — #18 (LeetCode #12)
Integer to Roman
Category: Array / String | Difficulty: Medium

Problem
-------
Roman numerals are represented by seven symbols: I=1, V=5, X=10, L=50, C=100, D=500, M=1000.
Normally symbols are combined left-to-right largest-to-smallest and their values summed, but six
specific cases use subtraction instead: IV=4, IX=9, XL=40, XC=90, CD=400, CM=900.

Given an integer, convert it to a roman numeral.

Constraints
-----------
- 1 <= num <= 3999

Examples
--------
Example 1:
    Input: num = 3749
    Output: "MMMDCCXLIX"
    Explanation: 3000 = MMM, 700 = DCC, 40 = XL, 9 = IX.

Example 2:
    Input: num = 58
    Output: "LVIII"
    Explanation: L = 50, V = 5, III = 3.

Example 3:
    Input: num = 1994
    Output: "MCMXCIV"
    Explanation: M = 1000, CM = 900, XC = 90, IV = 4.

Intuition
---------
The brute force way to think about this is digit-by-digit: split `num` into its thousands,
hundreds, tens, and ones digits, and have a hardcoded lookup table of the roman representation
for each digit (0-9) in each place value (e.g. hundreds digit 4 -> "CD", hundreds digit 9 ->
"CM"). That works but requires four separate hand-built tables (40 entries total) and doesn't
generalize or read cleanly. The cleaner insight: list every value the greedy algorithm could ever
need to subtract — including the six subtractive combos (900, 400, 90, 40, 9, 4) alongside the
seven standard symbol values — sorted from largest to smallest, then greedily take as many copies
of the largest value that still fits as possible before moving to the next. Because 1000, 900,
500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1 covers every reachable "next digit" of a valid roman
numeral, one greedy pass produces the correct string with a single unified table instead of four.
"""


# ============================================================
# Approach 1: Brute Force (digit-by-digit lookup tables)
# ============================================================
# Idea: split num into thousands/hundreds/tens/ones digits and translate
# each digit independently using a hardcoded table for its place value.
# Time:  O(1) — num is capped at 3999, so at most 4 digits, fixed lookups
# Space: O(1) — fixed-size tables
def solve_brute_force(num: int) -> str:
    thousands = ["", "M", "MM", "MMM"]
    hundreds = ["", "C", "CC", "CCC", "CD", "D", "DC", "DCC", "DCCC", "CM"]
    tens = ["", "X", "XX", "XXX", "XL", "L", "LX", "LXX", "LXXX", "XC"]
    ones = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX"]

    return (
        thousands[num // 1000]
        + hundreds[(num % 1000) // 100]
        + tens[(num % 100) // 10]
        + ones[num % 10]
    )


# ============================================================
# Approach 2: Optimal (greedy with a unified value table)
# ============================================================
# Idea: one sorted table of (value, symbol) pairs covering every standard
# and subtractive combination. Repeatedly subtract the largest value that
# still fits into what remains of num, appending its symbol each time.
# Dry run: num=1994
#   1994>=1000 -> "M", num=994
#   994<900? no, 994>=900 -> "CM", num=94
#   94>=90 -> "XC", num=4
#   4>=9? no ... 4>=4 -> "IV", num=0
#   result: "M"+"CM"+"XC"+"IV" = "MCMXCIV"
# Time:  O(1) — at most 13 table entries times a bounded number of repeats
#        per entry (equivalently O(log num) symbols emitted)
# Space: O(1) — fixed-size table
def solve_optimal(num: int) -> str:
    value_symbols = [
        (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
        (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
        (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
    ]

    result = []
    for value, symbol in value_symbols:
        if num == 0:
            break
        count, num = divmod(num, value)
        result.append(symbol * count)

    return "".join(result)


# ============================================================
# Key Takeaways
# ============================================================
# - When a greedy "take the largest piece that fits" strategy is correct,
#   folding the subtractive/special cases (900, 400, 90, 40, 9, 4) directly
#   into the same sorted table as the base values (1000, 500, 100, 50, 10,
#   5, 1) avoids needing separate special-case logic entirely.
# - Common mistake: forgetting to include the subtractive combos in the
#   table (only listing 1000/500/100/50/10/5/1), which produces invalid
#   forms like "VIIII" instead of "IX".
# - Related/variant problems to try next: Roman to Integer (the inverse
#   problem), Integer to English Words (a similar digit-group-to-symbol
#   translation at a larger scale).


if __name__ == "__main__":
    tests = [
        ((3,), "III"),
        ((58,), "LVIII"),
        ((1994,), "MCMXCIV"),
        ((3749,), "MMMDCCXLIX"),
        ((4,), "IV"),
        ((9,), "IX"),
        ((3999,), "MMMCMXCIX"),
        ((1,), "I"),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:15s} -> {result!r}  [{status}]")
