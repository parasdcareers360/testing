# Easy — Implement Trie (Prefix Tree)

**Source**: LeetCode #208
**Pattern**: Trie (Prefix Tree)
**Difficulty**: Easy

## Problem Statement
A **trie** (pronounced "try") or **prefix tree** is a tree data structure used to efficiently store and retrieve keys in a dataset of strings. There are various applications of this data structure, such as autocomplete and spell checker.

Implement the Trie class with the following operations:

- `Trie()` Initializes the trie object.
- `void insert(String word)` Inserts the string `word` into the trie.
- `boolean search(String word)` Returns `true` if the string `word` is in the trie (i.e., was previously inserted via `insert`), and `false` otherwise.
- `boolean startsWith(String prefix)` Returns `true` if there is a previously inserted string `word` that has the string `prefix` as a prefix, and `false` otherwise.

You must design the data structure so that all three operations run efficiently (proportional to the length of the word/prefix, not to the number of stored words).

## Constraints
- `1 <= word.length, prefix.length <= 2000`
- `word` and `prefix` consist only of lowercase English letters.
- At most `3 * 10^4` calls in total will be made to `insert`, `search`, and `startsWith`.

## Examples
```
Input:
["Trie", "insert", "search", "search", "startsWith", "insert", "search"]
[[], ["apple"], ["apple"], ["app"], ["app"], ["app"], ["app"]]

Output:
[null, null, true, false, true, null, true]
```
Explanation:
1. `Trie trie = new Trie();` — create empty trie.
2. `trie.insert("apple");` — inserts "apple".
3. `trie.search("apple");` → `true` — "apple" was inserted exactly.
4. `trie.search("app");` → `false` — "app" was never inserted as a complete word (only as a prefix of "apple").
5. `trie.startsWith("app");` → `true` — "apple" starts with "app".
6. `trie.insert("app");` — now "app" is also inserted as a complete word.
7. `trie.search("app");` → `true` — now "app" itself was inserted.

A second example: inserting `"cat"`, `"car"`, `"card"` then `startsWith("ca")` → `true`, `search("ca")` → `false` (never inserted as whole word), `search("car")` → `true`.

## Intuition — Why This Pattern
**Brute force**: Store all inserted words in a list (or a hash set). For `search(word)`, do an O(1) hash lookup on the whole word — that part is actually fine. But for `startsWith(prefix)`, a hash set of complete words is useless because it only supports exact-match lookups; you'd have to scan every stored word and check if it starts with `prefix`, costing O(total characters stored) per query.

**What's inefficient**: The brute force treats each word as an opaque blob. It never exploits the fact that many words share prefixes ("apple", "app", "application" all share "app"). Re-scanning every word for every prefix query wastes work that is common across queries.

**Insight the Trie provides**: Build a tree where each edge represents one character, and paths from the root spell out prefixes. Every node that is shared by multiple words is stored only once. This means:
- Checking whether any word starts with a prefix reduces to just following the prefix's characters down the tree — O(length of prefix), independent of how many words are stored.
- Checking whether a complete word exists reduces to following its characters and checking a special "end of word" marker on the final node.

This shared-prefix reuse is exactly what makes autocomplete-style and prefix-search problems fast, and it is the defining idea of the Trie pattern.

## Approach
1. Define a `TrieNode` with:
   - a dictionary/array `children` mapping character → child `TrieNode`.
   - a boolean flag `is_end` marking that a word ends at this node.
2. The `Trie` class holds a `root` node (an empty `TrieNode`, representing the empty prefix).
3. **`insert(word)`**:
   a. Start at `root`.
   b. For each character `c` in `word`, if `c` is not already a child of the current node, create a new `TrieNode` for it.
   c. Move to that child node.
   d. After processing all characters, mark the final node's `is_end = True`.
4. **`search(word)`**:
   a. Start at `root`.
   b. For each character `c` in `word`, if `c` is not a child of the current node, return `False` immediately (the word can't exist).
   c. Otherwise move to that child.
   d. After consuming all characters, return the final node's `is_end` flag (must be a *complete* stored word, not just a prefix of one).
5. **`startsWith(prefix)`**:
   a. Same traversal as `search`, but once all characters are consumed, return `True` unconditionally (we don't care whether `is_end` is set — just that the path exists).

## Dry Run
Trace through: `insert("apple")`, `search("apple")`, `search("app")`, `startsWith("app")`, `insert("app")`, `search("app")`.

**Initial state**: `root = {children: {}, is_end: False}`

**Step 1 — `insert("apple")`**
Walk `a -> p -> p -> l -> e`, creating a node for each character since the trie is empty:
```
root
 └─ 'a' (end=F)
     └─ 'p' (end=F)
         └─ 'p' (end=F)
             └─ 'l' (end=F)
                 └─ 'e' (end=T)   <- mark end of "apple"
```

**Step 2 — `search("apple")`**
Walk `a -> p -> p -> l -> e`, every step finds an existing child. Land on the node for the final `'e'`. Its `is_end` is `True` → return `True`. ✓

**Step 3 — `search("app")`**
Walk `a -> p -> p`. All three characters exist as children (since "apple" passes through them). Land on the second `'p'` node. Its `is_end` is currently `False` (no word ends there yet) → return `False`. ✓

**Step 4 — `startsWith("app")`**
Same traversal `a -> p -> p` succeeds (path exists) → return `True` regardless of `is_end`. ✓

**Step 5 — `insert("app")`**
Walk `a -> p -> p`; all nodes already exist, so no new nodes are created — we just move down the existing chain. At the end (second `'p'` node), set `is_end = True`.
```
root
 └─ 'a' (end=F)
     └─ 'p' (end=F)
         └─ 'p' (end=T)   <- now marked as end of "app"
             └─ 'l' (end=F)
                 └─ 'e' (end=T)
```

**Step 6 — `search("app")`**
Walk `a -> p -> p`, land on second `'p'` node, `is_end` is now `True` → return `True`. ✓

Final outputs match the expected: `[null, null, True, False, True, null, True]`.

## Solution (Python 3)
```python
class TrieNode:
    __slots__ = ("children", "is_end")

    def __init__(self):
        self.children = {}   # char -> TrieNode
        self.is_end = False


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True

    def _find_node(self, prefix: str):
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node

    def search(self, word: str) -> bool:
        node = self._find_node(word)
        return node is not None and node.is_end

    def startsWith(self, prefix: str) -> bool:
        return self._find_node(prefix) is not None


if __name__ == "__main__":
    trie = Trie()
    trie.insert("apple")
    print(trie.search("apple"))      # True
    print(trie.search("app"))        # False
    print(trie.startsWith("app"))    # True
    trie.insert("app")
    print(trie.search("app"))        # True

    # Second example
    trie2 = Trie()
    for w in ["cat", "car", "card"]:
        trie2.insert(w)
    print(trie2.startsWith("ca"))    # True
    print(trie2.search("ca"))        # False
    print(trie2.search("car"))       # True
```

## Complexity Analysis
- Time: `insert`, `search`, `startsWith` are each O(L) where L is the length of the word/prefix — independent of the number of words already stored.
- Space: O(total number of characters inserted across all unique prefixes) in the worst case — O(sum of word lengths) since each new character in a new prefix path creates one new node; shared prefixes reuse existing nodes.

## Key Takeaways
- The core Trie idea: a node per character, edges labeled by characters, and a boolean marker for "a word ends here" — this single flag is what separates `search` (exact word match) from `startsWith` (prefix match).
- Common mistake: forgetting the `is_end` flag and treating "path exists" as "word exists" — this incorrectly returns `True` for `search("app")` when only "apple" was inserted.
- Common mistake: using a fixed-size array of 26 children (fine for lowercase-only alphabets) vs. a dict (more flexible for Unicode/mixed characters) — pick based on constraints; here a dict is simplest and still O(1) average per step.
- Related/variant problems to try next: **Design Add and Search Words Data Structure** (LeetCode #211, adds wildcard `.` matching — see the medium example in this folder) and **Replace Words** (LeetCode #648, use a Trie of prefixes/roots to replace words in a sentence).
