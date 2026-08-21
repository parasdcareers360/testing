"""
LeetCode Top Interview 150 — #100 (LeetCode #212)
Word Search II
Category: Trie | Difficulty: Hard

Problem
-------
Given an `m x n` grid of characters `board` and a list of strings `words`, return all words from
`words` that can be constructed from letters of sequentially adjacent cells, where adjacent cells
are horizontally or vertically neighboring. The same cell letter may not be used more than once
in a single word.

Constraints
-----------
- m == board.length
- n == board[i].length
- 1 <= m, n <= 12
- board[i][j] is a lowercase English letter
- 1 <= words.length <= 3 * 10^4
- 1 <= words[i].length <= 10
- words[i] consists of lowercase English letters
- All the strings of words are unique

Examples
--------
Example 1:
    Input: board = [["o","a","a","n"],["e","t","a","e"],["i","h","k","r"],["i","f","l","v"]],
           words = ["oath","pea","eat","rain"]
    Output: ["eat","oath"]

Example 2:
    Input: board = [["a","b"],["c","d"]], words = ["abcb"]
    Output: []
    Explanation: "abcb" would need to reuse the cell holding 'b', which isn't allowed.

Intuition
---------
The direct approach is to reuse plain Word Search: for each word independently, DFS/backtrack
over the board trying every starting cell to see if that word can be traced out. This works but
is wasteful when `words` is long — for W words we redo a full board DFS from scratch W times, and
many words share common prefixes (e.g. "oath" and "oat") that end up re-explored repeatedly with
no memory of what was already tried. The optimal technique flips the loop: build a single Trie out
of all the words first, then do **one** DFS pass over the board, walking the Trie alongside the
board path. At each board cell we only recurse into neighbors if the current path's letters still
form a valid prefix in the Trie — the moment no word starts with the letters seen so far, that
whole branch is pruned immediately, regardless of how many words share it. This turns "W separate
searches" into "one search that explores all words' prefixes simultaneously," and letting the Trie
mark found words directly avoids needing a separate substring check per node.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force (search the board once per word)
# ============================================================
# Idea: for each word, run an independent backtracking DFS from every cell,
# exactly like the standalone Word Search problem, checking whether that
# one word can be traced. No sharing of work between words.
# Time:  O(W * m * n * 4^L) where W = len(words), L = max word length —
#        each word triggers its own full board search
# Space: O(L) recursion depth per search
def solve_brute_force(board: List[List[str]], words: List[str]) -> List[str]:
    if not board or not board[0]:
        return []
    rows, cols = len(board), len(board[0])

    def exists(word: str) -> bool:
        def dfs(r: int, c: int, i: int) -> bool:
            if i == len(word):
                return True
            if not (0 <= r < rows and 0 <= c < cols):
                return False
            if board[r][c] != word[i]:
                return False
            original = board[r][c]
            board[r][c] = "#"
            found = (
                dfs(r + 1, c, i + 1)
                or dfs(r - 1, c, i + 1)
                or dfs(r, c + 1, i + 1)
                or dfs(r, c - 1, i + 1)
            )
            board[r][c] = original
            return found

        for r in range(rows):
            for c in range(cols):
                if dfs(r, c, 0):
                    return True
        return False

    return [word for word in words if exists(word)]


# ============================================================
# Approach 2: Optimal (build one Trie, DFS the board once)
# ============================================================
# Idea: insert every word into a Trie so shared prefixes are stored once.
# Do a single DFS sweep over all board cells; at each step, only continue
# into a neighbor if the accumulated path is a prefix present in the Trie
# (an O(1) child lookup) — this prunes dead branches for *all* words at
# once instead of testing each word's full length independently. When a
# Trie node marks the end of a word, record it and null out that marker so
# the same word isn't reported twice via a different path.
# Dry run: words=["oath","oat"], board has path o-a-t at (0,0)-(0,1)-(1,1)
#   Trie: root -> o -> a -> t(end="oat") -> h(end="oath")
#   DFS from (0,0)='o': root has child 'o' -> descend
#     (0,1)='a': node 'o' has child 'a' -> descend
#       (1,1)='t': node 'oa' has child 't', node.word="oat" -> record "oat"
#         continue to (2,1) or wherever 'h' is -> if found, record "oath"
#   Both words found in one combined traversal, sharing the o->a->t walk.
# Time:  O(m*n*4^L) worst case for the DFS (same asymptotic bound as brute
#        force in the worst case), but the shared-prefix pruning makes it
#        dramatically faster in practice; O(sum of word lengths) to build
#        the Trie.
# Space: O(sum of word lengths) for the Trie + O(L) recursion depth
class TrieNode:
    __slots__ = ("children", "word")

    def __init__(self):
        self.children = {}
        self.word = None  # set to the full word string at a terminal node


def solve_optimal(board: List[List[str]], words: List[str]) -> List[str]:
    if not board or not board[0]:
        return []
    rows, cols = len(board), len(board[0])

    root = TrieNode()
    for word in words:
        node = root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
        node.word = word

    found = []

    def dfs(r: int, c: int, node: TrieNode) -> None:
        ch = board[r][c]
        child = node.children.get(ch)
        if child is None:
            return  # no word in the Trie continues with this letter

        if child.word is not None:
            found.append(child.word)
            child.word = None  # avoid duplicate reporting

        original = board[r][c]
        board[r][c] = "#"  # mark visited so we don't reuse this cell
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] != "#":
                dfs(nr, nc, child)
        board[r][c] = original

        # Prune the Trie: once a leaf has no children and no word ending
        # here, drop it from its parent so future DFS calls skip it faster.
        if not child.children:
            node.children.pop(ch, None)

    for r in range(rows):
        for c in range(cols):
            dfs(r, c, root)

    return found


# ============================================================
# Key Takeaways
# ============================================================
# - When searching a grid/text for many target strings at once, build one
#   Trie from all targets first so shared prefixes are explored (and
#   pruned) together instead of redoing the same work per target.
# - The Trie lets the DFS prune a branch the instant no remaining word
#   shares that prefix — an O(1) child-lookup check replaces re-testing
#   each word's full length independently.
# - Common mistakes: forgetting to null out a found word's marker (causes
#   duplicates if two paths reach the same word), and forgetting to mark
#   cells visited/unvisited (`board[r][c] = "#"` then restore) to avoid
#   reusing a cell within one word.
# - Related/variant problems to try next: Word Search, Implement Trie
#   (Prefix Tree), Design Add and Search Words Data Structure.


if __name__ == "__main__":
    tests = [
        (
            (
                [
                    ["o", "a", "a", "n"],
                    ["e", "t", "a", "e"],
                    ["i", "h", "k", "r"],
                    ["i", "f", "l", "v"],
                ],
                ["oath", "pea", "eat", "rain"],
            ),
            ["eat", "oath"],
        ),
        (([["a", "b"], ["c", "d"]], ["abcb"]), []),
        (([["a"]], ["a"]), ["a"]),
        (
            (
                [["a", "b"], ["c", "d"]],
                ["ab", "cb", "ad", "bd", "ac", "ca", "da", "bc", "db", "adcb", "dabc", "abb", "acb"],
            ),
            ["ab", "bd", "ac", "ca", "db"],
        ),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            board_copy = [row[:] for row in args[0]]
            result = fn(board_copy, list(args[1]))
            status = "OK" if sorted(result) == sorted(expected) else "FAIL"
            print(f"{fn.__name__:20s} words={args[1]!r:70s} -> {sorted(result)!r}  [{status}]")
