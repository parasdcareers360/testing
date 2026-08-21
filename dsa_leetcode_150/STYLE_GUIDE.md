# Style Guide — dsa_leetcode_150

Every file in this repo is one LeetCode "Top Interview 150" problem, fully solved as a single
self-contained, directly-runnable `.py` tutorial. Follow this template exactly for consistency.

## File template

```python
"""
LeetCode Top Interview 150 — #<global_no> (LeetCode #<official_number>)
<Title>
Category: <Category Name> | Difficulty: <Easy/Medium/Hard>

Problem
-------
<Full problem statement, paraphrased clearly and completely — not copy-pasted verbatim from
LeetCode, but accurate and complete enough that the reader never needs to open the LeetCode page.>

Constraints
-----------
- <constraint 1>
- <constraint 2>
...

Examples
--------
Example 1:
    Input: ...
    Output: ...
    Explanation: ...

Example 2:
    Input: ...
    Output: ...

Intuition
---------
<A short paragraph (3-6 sentences): why the brute-force approach is naive/slow, what specific
insight unlocks each subsequent, better approach. Written like a tutor explaining to a learner,
not just restating the code.>
"""

from typing import List, Optional  # + only the typing/collections imports actually used


# ============================================================
# Approach 1: Brute Force
# ============================================================
# Idea: <one or two lines>
# Time:  O(...)   Space: O(...)
def solve_brute_force(...):
    ...


# ============================================================
# Approach 2: Better   (omit this approach entirely if there is no real
# intermediate technique between brute force and optimal — do not pad)
# ============================================================
# Idea: <one or two lines>
# Time:  O(...)   Space: O(...)
def solve_better(...):
    ...


# ============================================================
# Approach 3: Optimal
# ============================================================
# Idea: <one or two lines>
# Dry run: <a short concrete trace through one example, 3-6 lines of comments>
# Time:  O(...)   Space: O(...)
def solve_optimal(...):
    ...


# ============================================================
# Approach 4: Best / Alternate Optimal   (ONLY add this when a genuinely
# different technique exists at the same or better complexity — e.g.
# Boyer-Moore voting vs hashmap counting for Majority Element, XOR bit
# trick for Single Number, Kadane's vs DP array for Maximum Subarray.
# Do NOT add a 4th approach that is just a cosmetic tweak of Approach 3.)
# ============================================================
def solve_best(...):
    ...


# ============================================================
# Key Takeaways
# ============================================================
# - <the core pattern/insight this problem teaches>
# - <a common mistake to avoid>
# - Related/variant problems to try next: <1-3 names>


if __name__ == "__main__":
    tests = [
        (args_as_tuple, expected),
        ...
    ]
    approaches = [solve_brute_force, solve_optimal]  # list every solve_* defined above, in order
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:40s} -> {result!r}  [{status}]")
```

## Hard rules

1. **Every approach must be real, correct, runnable code** — never a stub, never `pass`, never
   `# TODO`. If you cannot fully implement an approach correctly, drop it rather than fake it.
2. **Brute force is always included**, even when it's just pedagogical contrast (nested loop /
   extra space), UNLESS the problem has no meaningful brute force distinct from the optimal
   approach (rare — e.g. simple math formulas). In that rare case, note why in the Intuition section
   instead of forcing a fake "brute force".
3. **"Better" is optional** — only include it when there's a real, distinct intermediate technique
   (e.g. sort-then-scan before hashmap-in-one-pass). Don't pad with a near-duplicate of Optimal.
4. **"Best"/4th approach is optional** — only for genuinely distinct techniques at comparable or
   better complexity. Most files will have 2-3 approaches, not 4. That's expected and fine.
5. For problems involving linked lists / binary trees / graphs, define the minimal node class
   needed (`class ListNode`, `class TreeNode`, etc.) near the top of the file, and include small
   helper functions to build/print them for the test block (e.g. `build_linked_list`,
   `linked_list_to_list`) so the `__main__` tests are self-contained and runnable.
6. For problems with multiple valid outputs (e.g. `Group Anagrams`, `Permutations`, `3Sum`) the
   test-comparison in `__main__` must normalize before comparing (e.g. sort each list of lists)
   so correct-but-differently-ordered output doesn't print `[FAIL]`.
7. **Every file must execute cleanly**: after writing a file, run `python3 <path>` yourself and
   confirm exit code 0 and no `[FAIL]` lines in the output. Fix the code (not the test) if it
   fails, unless the test itself was wrong.
8. Keep comments purposeful — explain the *why* of each approach and any non-obvious trick, not
   a line-by-line narration of what the code obviously does.
9. Filenames and problem order are fixed by `MANIFEST.md` — do not rename, skip, reorder, or
   invent extra problems.

## Reference example

See `01_array_string/001_merge_sorted_array.py` once it exists (or the earlier example
`dsa_patterns/01_two_pointers/easy.md` in the parent repo) for the target tone/depth of the
Intuition and Key Takeaways prose — thorough but tight, no filler.
