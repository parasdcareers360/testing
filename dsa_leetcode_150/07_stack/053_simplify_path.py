"""
LeetCode Top Interview 150 — #53 (LeetCode #71)
Simplify Path
Category: Stack | Difficulty: Medium

Problem
-------
Given an absolute path for a Unix-style file system, which begins with a slash '/', transform
it into its simplified canonical path.

Rules for a Unix-style file system:
- A single period '.' represents the current directory.
- A double period '..' represents the previous/parent directory.
- Multiple consecutive slashes such as '//' are treated as a single slash '/'.
- Any sequence of periods that does not match the rules above (e.g. '...') is treated as a
  valid, ordinary directory name.

The simplified canonical path must:
- Start with a single slash '/'.
- Directories are separated by exactly one slash '/'.
- End without a trailing slash, unless it is the root directory "/" itself.
- Not contain "." or ".." as directory names.

Return the simplified canonical path.

Constraints
-----------
- 1 <= path.length <= 3000
- path consists of English letters, digits, period '.', slash '/', or '_'.
- path is a valid absolute Unix path.

Examples
--------
Example 1:
    Input: path = "/home/"
    Output: "/home"
    Explanation: The trailing slash is removed.

Example 2:
    Input: path = "/home//foo/"
    Output: "/home/foo"
    Explanation: Multiple consecutive slashes are replaced by a single one.

Example 3:
    Input: path = "/home/user/Documents/../Pictures"
    Output: "/home/user/Pictures"
    Explanation: "../" pops "Documents" (the directory most recently entered), leaving us back
    inside "user", and then "Pictures" is entered from there.

Example 4:
    Input: path = "/../"
    Output: "/"
    Explanation: Going one level up from the root directory is not possible, so we stay at "/".

Intuition
---------
Splitting the path on '/' turns it into a sequence of tokens, and each token tells us exactly
what to do with a stack of directory names we've "entered": an empty token or "." means do
nothing (consecutive slashes / current dir), ".." means step back out of the directory we most
recently entered (pop, if there's anything to pop — popping past the root is a no-op, not an
error), and anything else is a real directory name to push. This is naturally a stack problem
because "go up one level" always cancels the *most recently entered* directory, the same LIFO
property as matching brackets. Once every token is processed, joining the stack back together
with '/' gives the canonical path.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force (manual character scanning)
# ============================================================
# Idea: walk the string manually, character by character, hand-building
# each component between slashes, and apply the same push/pop/skip logic
# without relying on str.split. Functionally equivalent to the optimal
# approach but reimplements tokenization by hand — more code, same
# complexity, useful mainly as a "do it without library help" exercise.
# Time:  O(n) where n = len(path)
# Space: O(n) — stack of components
def solve_brute_force(path: str) -> str:
    stack: List[str] = []
    i, n = 0, len(path)
    while i < n:
        if path[i] == "/":
            i += 1
            continue
        j = i
        while j < n and path[j] != "/":
            j += 1
        component = path[i:j]
        if component == "." or component == "":
            pass
        elif component == "..":
            if stack:
                stack.pop()
        else:
            stack.append(component)
        i = j
    return "/" + "/".join(stack)


# ============================================================
# Approach 2: Optimal (split + stack)
# ============================================================
# Idea: str.split("/") already tokenizes on slashes (collapsing consecutive
# slashes into empty-string tokens we simply skip), so we just apply the
# push/pop/skip rule per token.
# Dry run: path = "/home/user/Documents/../Pictures"
#   split("/") -> ['', 'home', 'user', 'Documents', '..', 'Pictures']
#   '' -> skip
#   'home' -> push -> ['home']
#   'user' -> push -> ['home', 'user']
#   'Documents' -> push -> ['home', 'user', 'Documents']
#   '..' -> pop -> ['home', 'user']
#   'Pictures' -> push -> ['home', 'user', 'Pictures']
#   join -> "/home/user/Pictures"
# Time:  O(n)
# Space: O(n)
def solve_optimal(path: str) -> str:
    stack: List[str] = []
    for component in path.split("/"):
        if component == "" or component == ".":
            continue
        elif component == "..":
            if stack:
                stack.pop()
        else:
            stack.append(component)
    return "/" + "/".join(stack)


# ============================================================
# Key Takeaways
# ============================================================
# - Path normalization is a stack problem in disguise: ".." always undoes
#   the most recently pushed directory, the same LIFO pattern as bracket
#   matching or undo/redo history.
# - Common mistake: popping unconditionally on ".." without checking the
#   stack is non-empty — going above the root must be a silent no-op, not
#   an error or a negative-index bug.
# - Related/variant problems to try next: Valid Parentheses, Basic
#   Calculator (also tokenizes + uses a stack), Min Stack.


if __name__ == "__main__":
    tests = [
        (("/home/",), "/home"),
        (("/home//foo/",), "/home/foo"),
        (("/home/user/Documents/../Pictures",), "/home/user/Pictures"),
        (("/../",), "/"),
        (("/a/./b/../../c/",), "/c"),
        (("/...",), "/..."),
        (("/a/../../b/../c//.//",), "/c"),
        (("/",), "/"),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:45s} -> {result!r}  [{status}]")
