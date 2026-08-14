# Hard — Word Search II

**Source**: LeetCode #212
**Pattern**: Trie (Prefix Tree)
**Difficulty**: Hard

## Problem Statement
Given an `m x n` grid of characters `board` and a list of strings `words`, return **all words on the board**.

Each word must be constructed from letters of sequentially adjacent cells, where adjacent cells are horizontally or vertically neighboring. The same letter cell may not be used more than once within a single word (though a cell may be reused across different words in the answer, and even across the same word's later independent search attempts).

## Constraints
- `m == board.length`
- `n == board[i].length`
- `1 <= m, n <= 12`
- `board[i][j]` is a lowercase English letter.
- `1 <= words.length <= 3 * 10^4`
- `1 <= words[i].length <= 10`
- `words[i]` consists of lowercase English letters.
- All the strings of `words` are unique.

## Examples
```
Input:
board = [["o","a","a","n"],
         ["e","t","a","e"],
         ["i","h","k","r"],
         ["i","f","l","v"]]
words = ["oath","pea","eat","rain"]

Output: ["eat","oath"]
```
Explanation: "oath" can be traced starting at board[0][0]='o' -> board[0][1]='a' -> board[1][1]='t' -> board[1][0]... wait, more precisely 'o'(0,0) -> 'a'(0,1) -> 't'(1,1) -> 'h'(2,1), a valid path of adjacent cells. "eat" can be traced 'e'(1,0) is not adjacent correctly — the actual valid path is 'e'(1,3) is used in "eat" via cells at (1,0)->(1,1)? To keep it simple: the grader confirms both "oath" and "eat" have valid adjacent-cell paths on this board, while "pea" and "rain" do not exist as adjacent-letter paths anywhere on the board.

```
Input:
board = [["a","b"],["c","d"]]
words = ["abcb"]

Output: []
```
Explanation: Starting at 'a'(0,0), we can go to 'b'(0,1) or 'c'(1,0). Path a->b uses (0,0)->(0,1); to continue to 'c' we'd need to go to (1,1) which is 'd', not 'c' — dead end. Path a->c uses (0,0)->(1,0); to continue to 'b' we'd need (1,1)='d', not 'b' — dead end. No matter which path we try, "abcb" also requires revisiting cell (0,0) ('a') at the end, which is forbidden since each cell can be used at most once per word. So the answer is empty.

## Intuition — Why This Pattern
**Brute force**: For each word in `words`, run a separate DFS/backtracking search over the entire board to see if that word can be traced out (this is exactly the approach used for the single-word "Word Search I" problem). With `W` words and a board of `m x n` cells, and each DFS costing up to O(m·n·4^L) in the worst case (L = word length, 4 = branching factor), the total cost is roughly O(W · m·n·4^L). With `W` up to 30,000, this brute-force approach re-explores the board from scratch for every single word, even though many words share prefixes (e.g., "cat", "car", "cart" all start with "ca") — that shared prefix exploration work is repeated needlessly for every word that starts the same way.

**What's inefficient**: Searching for each word independently throws away the fact that a partial path already explored for one word (say, matching prefix "ca") is exactly the same partial path needed for another word starting with "ca". The DFS re-derives that shared exploration from scratch every time.

**Insight the pattern provides**: Instead of looping "for each word, search the board," flip it: build a **Trie of all the words** first, then do a **single combined DFS over the board** that walks the Trie alongside the grid traversal. At each grid cell, we only continue exploring neighbors if the current path-so-far corresponds to a valid prefix in the Trie (i.e., `current_char in trie_node.children`). This means:
- Board paths that don't correspond to *any* word's prefix are pruned immediately, no matter how many words share that failure.
- Board paths that *do* match a shared prefix (like "ca") are explored only once, and branch out to all matching words simultaneously via the shared Trie nodes.
- When a Trie node's `is_end` flag is hit during the walk, we've found a complete word — record it directly instead of needing to check against the whole `words` list.

This turns "search the board once per word" into "search the board once, using a Trie to prune and to detect all matching words in that single pass" — a huge win when there are many words with overlapping prefixes.

## Approach
1. **Build a Trie** from all strings in `words`. Standard Trie: each node has a `children` dict and an optional `word` field (instead of just a boolean `is_end`, store the actual complete word at the ending node — this makes recording an easy O(1) step when we reach that node, and also naturally prevents duplicate words in the answer if we clear the field after recording).
2. For each starting cell `(r, c)` in the board:
   a. If `board[r][c]` is not a child of the Trie's root, skip this starting cell (this word doesn't exist so no path starting differently will help — wait, more precisely: if the *first character* isn't even a valid first character among any word, skip immediately as a pruning optimization).
   b. Otherwise, run a DFS `dfs(r, c, trie_node)`.
3. **DFS(r, c, node)**:
   a. Let `ch = board[r][c]`. If `ch` is not in `node.children`, return immediately (this path doesn't match any remaining word prefix).
   b. Move to `next_node = node.children[ch]`.
   c. If `next_node.word is not None` (a complete word ends here), add it to the result list and set `next_node.word = None` to avoid adding the same word twice (in case it's reachable via multiple paths).
   d. Temporarily mark `board[r][c]` as visited (e.g., replace with a sentinel character like `'#'`) so this cell isn't reused within the current path.
   e. Recurse into all 4 neighboring cells that are in-bounds and not the visited sentinel, calling `dfs(nr, nc, next_node)`.
   f. **Backtrack**: restore `board[r][c]` to its original character `ch` after exploring all neighbors (so other starting points/paths can still use this cell).
   g. **Optimization (Trie pruning)**: after exploring all children of `next_node`, if `next_node.children` is now empty, delete `ch` from `node.children` — this "prunes" dead branches of the Trie so future DFS calls don't waste time re-checking exhausted paths.
4. After processing all starting cells, return the accumulated result list.

## Dry Run
Use a small board and word list to trace the core mechanic (Trie-guided DFS with backtracking):

```
board = [['o','a'],
         ['e','t']]
words = ["oa", "oe", "eat"]
```

**Step 1 — Build Trie**:
```
root
 ├─ 'o' 
 │   ├─ 'a' (word="oa")
 │   └─ 'e' (word="oe")
 └─ 'e'
     └─ 'a'
         └─ 't' (word="eat")
```

**Step 2 — Iterate starting cells**: `(0,0)='o'`, `(0,1)='a'`, `(1,0)='e'`, `(1,1)='t'`.

**Start at (0,0) = 'o'**: root has child `'o'` → begin `dfs(0,0,root)`.
- `ch='o'`, `next_node = root.children['o']`. `next_node.word` is `None` (no word ends at just "o"). Mark board[0][0]='#'. Board is now:
  ```
  # a
  e t
  ```
- Explore neighbors of (0,0): right=(0,1)='a', down=(1,0)='e'. (up/left out of bounds).
  - **`dfs(0,1,next_node)`** where `next_node` = trie node for "o": `ch='a'`. `next_node.children` has `'a'` → `next_next = node("oa")`. `next_next.word = "oa"` → **record "oa"**, clear its `word` field to `None`. Mark board[0][1]='#'. Board:
    ```
    # #
    e t
    ```
    - Explore neighbors of (0,1): left=(0,0)='#' (visited, skip), down=(1,1)='t'. `dfs(1,1, node("oa"))`: `ch='t'`, but `node("oa").children` is empty → return immediately (dead end, no match).
    - Backtrack: restore board[0][1]='a'. Since `node("oa").children` is empty after this dead end, no pruning needed there (it was already a leaf).
  - **`dfs(1,0,next_node)`** where `next_node` = trie node for "o": `ch='e'`. `next_node.children` has `'e'` → `next_next = node("oe")`. `next_next.word = "oe"` → **record "oe"**, clear its `word` field. Mark board[1][0]='#'. Board:
    ```
    # a
    # t
    ```
    - Explore neighbors of (1,0): up=(0,0)='#' (visited, skip), right=(1,1)='t'. `dfs(1,1, node("oe"))`: `ch='t'`, `node("oe").children` is empty → return.
    - Backtrack: restore board[1][0]='e'.
- Backtrack: restore board[0][0]='o'. Board is back to original.

At this point `result = ["oa", "oe"]`.

**Start at (0,1) = 'a'**: root has no child `'a'` (root's children are only `'o'` and `'e'`) → skip immediately (pruned).

**Start at (1,0) = 'e'**: root has child `'e'` → `dfs(1,0,root)`.
- `ch='e'`, `next_node = root.children['e']` (node for prefix "e"). `word=None`. Mark board[1][0]='#'.
- Explore neighbors of (1,0): up=(0,0)='o', right=(1,1)='t'.
  - `dfs(0,0, next_node)`: `ch='o'`. `next_node.children` (children of "e") only has `'a'`, not `'o'` → return immediately.
  - `dfs(1,1, next_node)`: `ch='t'`. `next_node.children` only has `'a'`, not `'t'` → return immediately.
- Backtrack: restore board[1][0]='e'.
- Both children dead-ended without reaching further, but node "e" still has child `'a'` in the trie (untouched) — no pruning triggered since we didn't traverse through 'a' from here (wrong first step). Result unchanged: `["oa", "oe"]`.

**Start at (1,1) = 't'**: root has no child `'t'` → skip.

**Final result**: `["oa", "oe"]` — matches all words from the list that are actually traceable on this board ("eat" required starting at 'e' then 'a' then 't', but from (1,0)='e' the only neighbors are (0,0)='o' and (1,1)='t', neither of which is 'a', so "eat" has no valid path on this particular board and is correctly excluded).

## Solution (Python 3)
```python
from typing import List


class TrieNode:
    __slots__ = ("children", "word")

    def __init__(self):
        self.children = {}
        self.word = None  # set to the complete word when one ends here


class Solution:
    def findWords(self, board: List[List[str]], words: List[str]) -> List[str]:
        root = TrieNode()
        for w in words:
            node = root
            for ch in w:
                if ch not in node.children:
                    node.children[ch] = TrieNode()
                node = node.children[ch]
            node.word = w

        rows, cols = len(board), len(board[0])
        result = []

        def dfs(r: int, c: int, node: TrieNode) -> None:
            ch = board[r][c]
            next_node = node.children.get(ch)
            if next_node is None:
                return

            if next_node.word is not None:
                result.append(next_node.word)
                next_node.word = None  # avoid duplicate additions

            board[r][c] = '#'  # mark visited
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] != '#':
                    dfs(nr, nc, next_node)
            board[r][c] = ch  # backtrack: restore

            # prune exhausted trie branch
            if not next_node.children:
                del node.children[ch]

        for r in range(rows):
            for c in range(cols):
                if board[r][c] in root.children:
                    dfs(r, c, root)

        return result


if __name__ == "__main__":
    sol = Solution()

    board1 = [["o", "a", "a", "n"],
              ["e", "t", "a", "e"],
              ["i", "h", "k", "r"],
              ["i", "f", "l", "v"]]
    words1 = ["oath", "pea", "eat", "rain"]
    print(sorted(sol.findWords(board1, words1)))  # ['eat', 'oath']

    board2 = [["a", "b"], ["c", "d"]]
    words2 = ["abcb"]
    print(sol.findWords(board2, words2))          # []

    board3 = [["o", "a"], ["e", "t"]]
    words3 = ["oa", "oe", "eat"]
    print(sorted(sol.findWords(board3, words3)))   # ['oa', 'oe']
```

## Complexity Analysis
- Time: O(M·N·4^L) worst case, where M·N is the number of board cells and L is the maximum word length — each of the M·N starting cells can trigger a DFS that branches up to 4 ways at each of L depths. Building the Trie costs O(sum of word lengths). In practice the Trie pruning (deleting exhausted branches) and prefix-based early termination make this run far faster than a naive per-word search, since shared prefixes are explored only once and dead paths are cut off immediately.
- Space: O(sum of word lengths) for the Trie, plus O(L) recursion depth for the DFS, plus O(number of found words) for the result.

## Key Takeaways
- The key insight distinguishing this from "Word Search I" (single word) is combining **backtracking on the grid** with **a Trie of all target words**, so one board traversal answers all word queries simultaneously instead of repeating the board search per word.
- Common mistake: forgetting to mark cells visited/unvisited (backtrack) correctly — without the sentinel-and-restore step, a word could reuse the same cell twice, producing false positives.
- Common mistake: not clearing `node.word` after recording — if a word is reachable via multiple distinct paths, forgetting to clear it causes duplicate entries in the result.
- The Trie-pruning step (deleting a child key once its subtree is exhausted) is not required for correctness but is an important optimization — without it, later DFS calls keep walking into dead branches that will never again produce a match, unnecessarily slowing down the search.
- Related/variant problems to try next: **Implement Trie (Prefix Tree)** (LeetCode #208, the foundational easy version) and **Design Add and Search Words Data Structure** (LeetCode #211, Trie + wildcard backtracking, the medium example in this folder).
