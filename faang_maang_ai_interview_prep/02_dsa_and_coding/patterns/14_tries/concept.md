# Tries (Prefix Trees)

> **Type:** Study notes

## Why interviewers ask this

Tries test whether you can design a data structure from scratch rather than just apply a built-in
one — there's no `dict`-based one-liner that gives you prefix search, so the interviewer gets to see
raw class-design instincts (what state does each node hold, what's the invariant). It's also a
practical structure this candidate's background touches indirectly: autocomplete, search-as-you-type,
and Elasticsearch's own prefix/edge-ngram queries are trie-adjacent, so it's a natural pairing with
"tell me about a search feature you built."

## The core idea

A trie is a tree where **each path from the root spells out a prefix**, and nodes are shared between
words with common prefixes. Instead of storing whole strings, you store one character per edge, so
`"car"` and `"cart"` share the `c -> a -> r` path and diverge only at the last node. This makes
prefix queries ("does anything start with `ca`?") O(length of prefix) instead of O(n · length)
scanning every string.

Recognize this pattern when you see:
- "Implement autocomplete / typeahead"
- "Check if a word (or prefix) exists in a dictionary"
- Word search on a grid where you need to prune paths that can't possibly extend to a valid word
- Longest common prefix among a set of strings
- IP routing / longest-prefix-match style problems (same idea, different alphabet)

## Node structure: dict-of-children vs. fixed-size array

Two ways to store a node's children, both valid — the trade-off is worth stating out loud:

```python
# Option A: dict of children -- works for any alphabet (unicode, mixed case), sparse-friendly
class TrieNodeDict:
    def __init__(self):
        self.children: dict[str, "TrieNodeDict"] = {}
        self.is_word: bool = False


# Option B: fixed-size array of children -- O(1) exact indexing, faster in practice,
# but wastes space when the alphabet is large or the branching factor is low
class TrieNodeArray:
    ALPHABET_SIZE = 26  # lowercase a-z only

    def __init__(self):
        self.children: list = [None] * self.ALPHABET_SIZE
        self.is_word: bool = False

    @staticmethod
    def index(ch: str) -> int:
        return ord(ch) - ord("a")
```
Default to the dict version in interviews unless told the alphabet is small and fixed (lowercase
English letters) — it's simpler to write correctly under time pressure and handles arbitrary input
without a bounds check. Mention the array version as the "if I know it's exactly a-z, I'd use a
fixed-size array for speed" follow-up.

## Core operations

```python
class Trie:
    def __init__(self):
        self.root = TrieNodeDict()

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNodeDict()
            node = node.children[ch]
        node.is_word = True

    def _find_node(self, prefix: str) -> "TrieNodeDict | None":
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node

    def search(self, word: str) -> bool:
        """Exact word match -- must end on a node marked is_word."""
        node = self._find_node(word)
        return node is not None and node.is_word

    def starts_with(self, prefix: str) -> bool:
        """Prefix match -- any word in the trie starts with this, don't require is_word."""
        return self._find_node(prefix) is not None
```
The `search` vs. `starts_with` distinction is the single most commonly tested detail: `search`
requires the terminal node's `is_word` flag to be `True` (so `"car"` inserted alone means
`search("ca")` is `False`), while `starts_with` only requires the path to exist. Say this difference
out loud before coding — it's the part interviewers watch for.

## Applications

### Word Search II (grid + trie pruning)
Build a trie of all target words, then DFS the grid — at each cell, only recurse into a neighbor if
the current path is still a valid prefix in the trie. This prunes dead-end DFS branches in O(1) per
step instead of re-checking "is this still a possible prefix of *any* target word" against every
word individually.

```python
def find_words(board: list[list[str]], words: list[str]) -> list[str]:
    trie = Trie()
    for w in words:
        trie.insert(w)

    rows, cols = len(board), len(board[0])
    found: set[str] = set()

    def dfs(r: int, c: int, node: TrieNodeDict, path: str) -> None:
        ch = board[r][c]
        if ch not in node.children:
            return  # prune: no target word continues with this letter
        nxt = node.children[ch]
        path += ch
        if nxt.is_word:
            found.add(path)

        board[r][c] = "#"  # mark visited
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] != "#":
                dfs(nr, nc, nxt, path)
        board[r][c] = ch  # backtrack

    for r in range(rows):
        for c in range(cols):
            dfs(r, c, trie.root, "")
    return list(found)
```

### Autocomplete
Find the node for the typed prefix (`_find_node`), then DFS the subtree under it collecting every
`is_word` node — the typed prefix guarantees you're only ever exploring completions of what the user
already typed, never re-scanning the whole dictionary.

## Complexity to know cold

| Operation | Time | Space |
|---|---|---|
| `insert(word)` | O(L) where L = len(word) | O(L) new nodes worst case |
| `search(word)` | O(L) | O(1) extra |
| `starts_with(prefix)` | O(L) | O(1) extra |
| Building trie of n words, avg length L | O(n·L) | O(n·L) worst case (no shared prefixes) |
| Word Search II on r×c grid, n words avg length L | O(n·L + r·c·4^L) worst case | O(n·L) for the trie |

Compare this to a plain `set` of words: `search`/`starts_with`-for-exact-match is also O(L) in a
set, but a set **cannot** answer "does any word start with this prefix" without scanning every
entry — that's the capability a trie adds that a hash set can't give you.

## Exercises

1. Implement `Trie` with `insert`/`search`/`starts_with` from memory, then verify: insert `"apple"`,
   confirm `search("apple")` is `True`, `search("app")` is `False`, `starts_with("app")` is `True`.
2. Extend your trie with a `count_words_with_prefix(prefix)` method (store a counter on each node
   incremented during `insert`) and use it to answer "how many words start with `pre`" in O(len(pre))
   instead of O(n) — this is the shape autocomplete ranking/frequency features actually use.
