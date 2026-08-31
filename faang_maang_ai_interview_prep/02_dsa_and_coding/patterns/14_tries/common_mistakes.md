# Common Mistakes — Tries

> **Type:** Study notes

- **Confusing `search` with `starts_with`.** Forgetting to check `node.is_word` in `search` means
  `search("ca")` returns `True` just because `"car"` was inserted — the path existing is not the same
  as a complete word ending there. This is the #1 bug interviewers watch for; always check
  `is_word` on the terminal node for exact-match search.
- **Sharing a single `TrieNode` class instance as a default argument.** `def __init__(self,
  children={})` uses one mutable dict shared across *every* node instance in Python — all nodes end
  up sharing the same `children` dict. Always initialize `self.children = {}` inside `__init__`,
  never as a default parameter value.
- **Not marking `is_word` when a word is a prefix of another already-inserted word.** Inserting
  `"app"` after `"apple"` reuses the existing path down to the `p` node — if you only ever set
  `is_word = True` on newly-created nodes, you'll miss setting it on a node that already existed from
  a longer word. Set `node.is_word = True` unconditionally at the end of the walk, regardless of
  whether nodes were newly created.
- **Using a fixed-size array for children with unfiltered input.** `ord(ch) - ord("a")` assumes
  strictly lowercase `a`-`z`; a stray uppercase letter, digit, or space produces a negative or
  out-of-range index that silently corrupts an unrelated array slot instead of raising immediately.
  If the alphabet isn't guaranteed constrained, use the dict-based node from `concept.md`.
- **Forgetting to prune in grid-search-with-trie problems.** If `dfs` doesn't `return` as soon as
  `ch not in node.children`, you keep exploring board paths that can never complete any target word,
  losing the entire point of using a trie over checking each word independently — the pruning check
  must be the very first thing in the recursive call.
- **Not backtracking the visited marker in Word Search II.** Marking `board[r][c] = "#"` to avoid
  revisiting within one DFS path but forgetting to restore it (`board[r][c] = ch`) after the
  recursive calls return corrupts the board for the *next* starting cell's DFS, silently missing
  valid words that would have reused that cell from a different starting point.
- **Rebuilding the trie inside a loop over queries.** If a problem gives you a fixed dictionary and
  many prefix queries, build the trie **once** before the query loop — building it per-query turns
  an O(n·L + q·L) solution into O(q·n·L), which defeats the reason to use a trie at all.
