"""
LeetCode Top Interview 150 — #24 (LeetCode #68)
Text Justification
Category: Array / String | Difficulty: Hard

Problem
-------
Given an array of strings `words` and a width `maxWidth`, format the text into justified lines
where each line has exactly `maxWidth` characters, and is fully (left and right) justified.

Pack as many words as possible into each line, using a greedy approach: fit as many words as
possible per line without exceeding `maxWidth`, then distribute extra spaces so the line's total
length is exactly `maxWidth`.

Extra spaces between words on a fully-packed line should be distributed as evenly as possible; if
the number of spaces doesn't divide evenly among the gaps, the earlier (leftmost) gaps get one
more space than later gaps. The last line of the output, and any line that contains only a single
word, is left-justified: words are separated by a single space each, and any remaining spaces are
padded at the end of the line (not distributed between words).

Words in `words` never exceed `maxWidth`, and there is at least one word per line.

Constraints
-----------
- 1 <= words.length <= 300
- 1 <= words[i].length <= 20
- words[i] consists of only English letters and symbols.
- 1 <= maxWidth <= 100
- words[i].length <= maxWidth

Examples
--------
Example 1:
    Input: words = ["This", "is", "an", "example", "of", "text", "justification."], maxWidth = 16
    Output:
        [
           "This    is    an",
           "example  of text",
           "justification.  "
        ]

Example 2:
    Input: words = ["What", "must", "be", "acknowledgment", "shall", "be"], maxWidth = 16
    Output:
        [
          "What   must   be",
          "acknowledgment  ",
          "shall be        "
        ]
    Explanation: Note that the last line is "shall be    " instead of "shall     be",
    because the last line must be left-justified instead of fully-justified.
    Note that the second line is also left-justified because it contains only one word.

Example 3:
    Input:
        words = ["Science","is","what","we","understand","well","enough","to","explain",
                  "to","a","computer.","Art","is","everything","else","we","do"]
        maxWidth = 20
    Output:
        [
          "Science  is  what we",
          "understand      well",
          "enough to explain to",
          "a  computer.  Art is",
          "everything  else  we",
          "do                  "
        ]

Intuition
---------
There isn't a meaningfully different "brute force" for this problem the way there is for, say, a
search or counting problem — the task is inherently a single, precise greedy simulation, and any
correct solution ends up doing the same two-phase work: (1) greedily pack as many words as fit on
a line without exceeding maxWidth (greedy packing is provably optimal here — packing fewer words
per line never helps, since every line must eventually be padded to maxWidth anyway), then (2)
distribute the leftover space across the gaps between words on that line. The only real design
decision is how carefully you handle the spacing arithmetic: for a fully-justified line with `k`
words (so `k-1` gaps), the leftover space splits into `total_spaces // (k-1)` base spaces per gap,
with the first `total_spaces % (k-1)` gaps getting one extra space each. Special cases that must
be handled explicitly: the last line (left-justified, single space between words, padding at the
end) and any line with only one word (also left-justified, since there are zero gaps to stretch).
Given that, a single well-organized "optimal" implementation is the right amount of code here —
inventing a separate, artificially slower brute force would just be the same algorithm restated,
which the style guide says to avoid.
"""

from typing import List


# ============================================================
# Approach 1: Optimal (greedy line packing + gap distribution)
# ============================================================
# Idea: walk words left to right, greedily grabbing words onto the current
# line while they still fit (word lengths + at least one space each).
# Once a line is full (or words run out), justify it: full/multi-word lines
# get spaces spread evenly across gaps (extra spaces to the leftmost gaps);
# the last line and single-word lines are left-justified with padding at
# the end.
# Dry run: words=["This","is","an","example"], maxWidth=16
#   line 1 greedily picks "This","is","an" (4+1+2+1+2=10, +"example"(7) would
#     need 10+1+7=18 > 16, so stop) -> 3 words, line length so far = 4+2+2=8
#     total_spaces = 16-8 = 8, gaps = 2 -> 8//2=4 base, 8%2=0 extra
#     -> "This" + "    " + "is" + "    " + "an" = "This    is    an"
# Time:  O(total characters in words + maxWidth * number of lines)
#        i.e. O(n + maxWidth * L) where L is the number of output lines —
#        effectively linear in the total size of the input/output.
# Space: O(maxWidth * L) for the output lines (unavoidable — that's the
#        output itself); O(1) extra bookkeeping per line otherwise.
def solve_optimal(words: List[str], maxWidth: int) -> List[str]:
    result = []
    line: List[str] = []
    line_len = 0  # sum of word lengths on the current line (no spaces yet)

    for word in words:
        # +len(line) accounts for one mandatory space before each word
        # already on the line (i.e. minimum one space between words).
        if line and line_len + len(line) + len(word) > maxWidth:
            result.append(_justify_line(line, line_len, maxWidth))
            line, line_len = [], 0
        line.append(word)
        line_len += len(word)

    if line:
        result.append(_left_justify(line, line_len, maxWidth))

    return result


def _justify_line(line: List[str], line_len: int, maxWidth: int) -> str:
    if len(line) == 1:
        return _left_justify(line, line_len, maxWidth)

    total_spaces = maxWidth - line_len
    gaps = len(line) - 1
    base, extra = divmod(total_spaces, gaps)

    parts = []
    for i, word in enumerate(line[:-1]):
        spaces = base + (1 if i < extra else 0)
        parts.append(word + " " * spaces)
    parts.append(line[-1])
    return "".join(parts)


def _left_justify(line: List[str], line_len: int, maxWidth: int) -> str:
    text = " ".join(line)
    return text + " " * (maxWidth - len(text))


# ============================================================
# Key Takeaways
# ============================================================
# - Greedy word-packing is optimal here because every line pays the same
#   fixed cost (padding to maxWidth) regardless of how many words it holds,
#   so packing as many words as legally fit never makes a later line worse.
# - Common mistake: forgetting that the LAST line and any SINGLE-WORD line
#   are always left-justified (padded only at the end), not space-distributed
#   like a normal full line — and dividing by zero gaps for a one-word line
#   if that case isn't special-cased.
# - Related/variant problems to try next: Word Wrap (DP variant minimizing
#   raggedness instead of exact justification), Reorganize String, Rearrange
#   Words in a Sentence.


if __name__ == "__main__":
    tests = [
        (
            (["This", "is", "an", "example", "of", "text", "justification."], 16),
            ["This    is    an", "example  of text", "justification.  "],
        ),
        (
            (["What", "must", "be", "acknowledgment", "shall", "be"], 16),
            ["What   must   be", "acknowledgment  ", "shall be        "],
        ),
        (
            (
                [
                    "Science", "is", "what", "we", "understand", "well", "enough", "to",
                    "explain", "to", "a", "computer.", "Art", "is", "everything", "else",
                    "we", "do",
                ],
                20,
            ),
            [
                "Science  is  what we",
                "understand      well",
                "enough to explain to",
                "a  computer.  Art is",
                "everything  else  we",
                "do                  ",
            ],
        ),
        ((["a"], 1), ["a"]),
        ((["a", "b", "c", "d"], 5), ["a b c", "d    "]),
    ]

    approaches = [solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:60s} -> {result!r}  [{status}]")
