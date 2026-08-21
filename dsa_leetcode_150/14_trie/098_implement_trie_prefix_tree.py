"""
LeetCode Top Interview 150 — #98 (LeetCode #208)
Implement Trie (Prefix Tree)
Category: Trie | Difficulty: Medium

Problem
-------
A trie (pronounced "try"), also called a prefix tree, is a tree data structure used to
efficiently store and retrieve keys in a dataset of strings. It powers things like autocomplete
and spellcheckers because it lets many words share the same storage for their common prefixes.

Implement the `Trie` class:
- `Trie()` initializes the trie object.
- `void insert(String word)` inserts the string `word` into the trie.
- `boolean search(String word)` returns `true` if `word` was previously inserted into the trie
  (as a complete word, not just a prefix), `false` otherwise.
- `boolean startsWith(String prefix)` returns `true` if there is a previously inserted word that
  has `prefix` as a prefix, `false` otherwise.

Constraints
-----------
- 1 <= word.length, prefix.length <= 2000
- word and prefix consist only of lowercase English letters
- At most 3 * 10^4 calls in total will be made to insert, search, and startsWith

Examples
--------
Example 1:
    Input:
        ["Trie", "insert", "search", "search", "startsWith", "insert", "search"]
        [[], ["apple"], ["apple"], ["app"], ["app"], ["app"], ["app"]]
    Output:
        [null, null, true, false, true, null, true]
    Explanation:
        trie = Trie()
        trie.insert("apple")
        trie.search("apple")     # True  — "apple" was inserted
        trie.search("app")       # False — "app" was never inserted as a whole word
        trie.startsWith("app")   # True  — "apple" starts with "app"
        trie.insert("app")
        trie.search("app")       # True  — now "app" was inserted too

Intuition
---------
A "brute force" trie isn't really a trie at all: just keep a set of every inserted word.
`insert`/`search` are then O(word length) hash operations, which is already fast — but
`startsWith` has no way to jump straight to "does any stored word begin with this prefix"
without scanning every stored word and checking it, which is O(total characters stored) per
call. The fix is to actually share structure between words with common prefixes: a tree where
each edge is one character, and a node is a valid "word end" if some inserted word stops there.
Walking from the root along `prefix`'s characters either falls off the tree (no match) or lands
on a node — meaning some inserted word shares that prefix — in O(prefix length), independent of
how many words are stored. The two real trie implementations below differ only in how each
node stores its children: a hashmap keyed by character (simple, flexible, handles any alphabet)
versus a fixed-size array of 26 slots (faster constant factor and less memory overhead since
this problem's alphabet is fixed to lowercase English letters).
"""

from typing import Dict, List, Optional


# ============================================================
# Approach 1: Brute Force (plain set of whole words)
# ============================================================
# Idea: store every inserted word verbatim in a set. insert/search are fast
# hash operations, but startsWith has no shared structure to exploit, so it
# must scan every stored word.
# Time:  insert O(L), search O(L), startsWith O(n * L) where n = words stored,
#        L = string length
# Space: O(total characters across all inserted words)
class TrieBruteForce:
    def __init__(self):
        self.words = set()

    def insert(self, word: str) -> None:
        self.words.add(word)

    def search(self, word: str) -> bool:
        return word in self.words

    def startsWith(self, prefix: str) -> bool:
        return any(w.startswith(prefix) for w in self.words)


# ============================================================
# Approach 2: Better (nested-dict trie)
# ============================================================
# Idea: each node is a plain dict mapping character -> child node dict, plus
# a sentinel key (here "$is_word") marking whether a complete word ends at
# that node. insert/search/startsWith all just walk the dict chain one
# character at a time.
# Time:  insert O(L), search O(L), startsWith O(L) — independent of how many
#        words are stored, because shared prefixes reuse the same nodes
# Space: O(total distinct character-paths across all inserted words)
class TrieDict:
    END = "$is_word"  # sentinel key that can't collide with a lowercase letter

    def __init__(self):
        self.root: Dict = {}

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            node = node.setdefault(ch, {})
        node[self.END] = True

    def search(self, word: str) -> bool:
        node = self._walk(word)
        return node is not None and self.END in node

    def startsWith(self, prefix: str) -> bool:
        return self._walk(prefix) is not None

    def _walk(self, s: str) -> Optional[Dict]:
        node = self.root
        for ch in s:
            if ch not in node:
                return None
            node = node[ch]
        return node


# ============================================================
# Approach 3: Optimal (array-of-26-children TrieNode)
# ============================================================
# Idea: same tree shape as Approach 2, but each node stores its children in
# a fixed-size list of 26 slots (one per lowercase letter) instead of a
# hashmap. Indexing a list by ord(ch) - ord('a') avoids hashing overhead
# and keeps nodes compact — the standard interview-ready trie for a fixed,
# small alphabet.
# Dry run: insert("apple"), insert("app"), then search("app")
#   insert("apple"): root -> a -> p -> p -> l -> e, mark e.is_word = True
#   insert("app"):   root -> a -> p -> p (nodes a,p,p already exist, reused),
#                     mark the second p.is_word = True
#   search("app"): walk root->a->p->p, all children exist, final node's
#                   is_word is True -> return True
#   search("appl"): walk root->a->p->p->l, node exists but l.is_word is
#                   False (only "apple" passes through it, not "appl" itself)
#                   -> return False
# Time:  insert O(L), search O(L), startsWith O(L)
# Space: O(total distinct character-paths across all inserted words),
#        with a smaller constant factor per node than the dict version
class TrieNode:
    __slots__ = ("children", "is_word")

    def __init__(self):
        self.children: List[Optional["TrieNode"]] = [None] * 26
        self.is_word = False


class TrieArray:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            idx = ord(ch) - ord("a")
            if node.children[idx] is None:
                node.children[idx] = TrieNode()
            node = node.children[idx]
        node.is_word = True

    def search(self, word: str) -> bool:
        node = self._walk(word)
        return node is not None and node.is_word

    def startsWith(self, prefix: str) -> bool:
        return self._walk(prefix) is not None

    def _walk(self, s: str) -> Optional[TrieNode]:
        node = self.root
        for ch in s:
            idx = ord(ch) - ord("a")
            if node.children[idx] is None:
                return None
            node = node.children[idx]
        return node


# ============================================================
# Key Takeaways
# ============================================================
# - A trie's whole value proposition is sharing storage/work across common
#   prefixes; any implementation that can't answer "does some prefix exist"
#   without rescanning every stored word (like a plain set) defeats the
#   purpose for startsWith-style queries.
# - Common mistake: conflating "prefix exists in the tree" with "word was
#   inserted" — a node can be reachable (some longer word passes through it)
#   without being a valid end-of-word itself; that's what the is_word /
#   sentinel flag is for.
# - Array-of-26 vs hashmap children is a pure constant-factor / alphabet-size
#   tradeoff, not an asymptotic one — use array-of-26 when the alphabet is
#   small and fixed, a dict when it's large, sparse, or unknown (e.g. unicode).
# - Related/variant problems to try next: Design Add and Search Words Data
#   Structure, Word Search II, Replace Words, Longest Word in Dictionary.


if __name__ == "__main__":
    def run_ops(cls, operations, args):
        results = []
        obj = None
        for op, arg in zip(operations, args):
            if op == "Trie":
                obj = cls()
                results.append(None)
            else:
                results.append(getattr(obj, op)(*arg))
        return results

    tests = [
        (
            ["Trie", "insert", "search", "search", "startsWith", "insert", "search"],
            [[], ["apple"], ["apple"], ["app"], ["app"], ["app"], ["app"]],
            [None, None, True, False, True, None, True],
        ),
        (
            ["Trie", "insert", "startsWith", "search", "insert", "search"],
            [[], ["a"], ["a"], ["a"], ["a"], ["a"]],
            [None, None, True, True, None, True],
        ),
        (
            ["Trie", "search", "startsWith", "insert", "search", "startsWith", "startsWith"],
            [[], ["cat"], ["cat"], ["cat"], ["cat"], ["ca"], ["dog"]],
            [None, False, False, None, True, True, False],
        ),
    ]

    classes = [TrieBruteForce, TrieDict, TrieArray]
    for operations, args, expected in tests:
        for cls in classes:
            result = run_ops(cls, operations, args)
            status = "OK" if result == expected else "FAIL"
            print(f"{cls.__name__:20s} ops={operations!r:75s} -> {result!r}  [{status}]")
