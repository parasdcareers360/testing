"""
LeetCode Top Interview 150 — #99 (LeetCode #211)
Design Add and Search Words Data Structure
Category: Trie | Difficulty: Medium

Problem
-------
Design a data structure that supports adding new words and searching for a word, where the
search word may contain the dot character `.` as a wildcard that can match any single letter.

Implement the `WordDictionary` class:
- `WordDictionary()` initializes the object.
- `void addWord(word)` adds `word` to the data structure; it can be matched later.
- `bool search(word)` returns `true` if there is a previously added string that matches `word`.
  `word` may contain `.` characters, each of which can match any one letter, and otherwise
  matching must be exact.

Constraints
-----------
- 1 <= word.length <= 25
- word in addWord consists of lowercase English letters
- word in search consists of '.' or lowercase English letters
- There will be at most 2 dots in word for a search query
- At most 10^4 calls will be made in total to addWord and search

Examples
--------
Example 1:
    Input:
        ["WordDictionary", "addWord", "addWord", "addWord", "search", "search", "search", "search"]
        [[], ["bad"], ["dad"], ["mad"], ["pad"], ["bad"], [".ad"], ["b.."]]
    Output:
        [null, null, null, null, false, true, true, true]
    Explanation:
        wd = WordDictionary()
        wd.addWord("bad")
        wd.addWord("dad")
        wd.addWord("mad")
        wd.search("pad")   # False — "pad" was never added
        wd.search("bad")   # True  — exact match
        wd.search(".ad")   # True  — "." matches 'b', 'd', or 'm'; "bad"/"dad"/"mad" all match
        wd.search("b..")   # True  — "." matches 'a', "." matches 'd'; "bad" matches

Intuition
---------
Without any wildcard, this would be exactly Implement Trie: walk down matching characters and
check an end-of-word flag. The wildcard is what breaks a plain single-pointer walk — a `.` can
match any of up to 26 children at that position, so there's no longer one deterministic path to
follow. The brute-force fallback is to keep every added word in a flat list and, for each search,
pattern-match it against every stored word individually (checking length and character-by-character
compatibility) — correct, but O(n * L) per search with no structure sharing at all. A trie still
helps enormously here: store words in a standard trie, and when `search` hits a `.`, branch into
*every* non-null child at that node (a small DFS/backtracking step) instead of just one; a plain
letter still follows its single matching edge deterministically. Because at most 2 dots are
guaranteed per query, this branching stays cheap in practice even though its worst case is
exponential in the number of dots.
"""

from typing import Dict, List, Optional


# ============================================================
# Approach 1: Brute Force (flat list of words, pattern-match each)
# ============================================================
# Idea: addWord just appends to a list. search checks every stored word of
# the same length, comparing character by character and treating '.' as a
# wildcard that matches anything.
# Time:  addWord O(1) amortized; search O(n * L) — n stored words, L = word
#        length, no structure shared between words at all
# Space: O(total characters across all added words)
class WordDictionaryBruteForce:
    def __init__(self):
        self.words: List[str] = []

    def addWord(self, word: str) -> None:
        self.words.append(word)

    def search(self, word: str) -> bool:
        for candidate in self.words:
            if len(candidate) != len(word):
                continue
            if all(wc == "." or wc == cc for wc, cc in zip(word, candidate)):
                return True
        return False


# ============================================================
# Approach 2: Optimal (trie + DFS branching on '.')
# ============================================================
# Idea: addWord builds a standard nested-dict trie. search walks the pattern
# recursively: a literal letter follows its single child edge (or fails
# immediately if that edge doesn't exist); a '.' tries every existing child
# and succeeds if *any* branch leads to a full match at the pattern's end.
# Dry run: addWord("bad"), addWord("dad"), addWord("mad"), search(".ad")
#   trie root has children 'b','d','m', each leading to ...->a->d (is_word)
#   search(".ad") at root, pattern[0]='.': try every child of root
#     child 'b': recurse search("ad") from node b -> 'a' matches -> 'd'
#                matches -> end of pattern, node.is_word=True -> MATCH
#   first branch already succeeds -> return True (no need to try d/m branches)
# Time:  addWord O(L). search: O(L) when no dots (single deterministic
#        path); worst case O(26^d * L) where d = number of dots (each dot
#        branches into up to 26 children) — bounded tightly here since the
#        problem guarantees at most 2 dots per query
# Space: O(total distinct character-paths across all added words), plus
#        O(L) recursion depth per search call
class WordDictionary:
    END = "$is_word"

    def __init__(self):
        self.root: Dict = {}

    def addWord(self, word: str) -> None:
        node = self.root
        for ch in word:
            node = node.setdefault(ch, {})
        node[self.END] = True

    def search(self, word: str) -> bool:
        return self._match(word, 0, self.root)

    def _match(self, word: str, i: int, node: Dict) -> bool:
        if i == len(word):
            return self.END in node

        ch = word[i]
        if ch == ".":
            for key, child in node.items():
                if key != self.END and self._match(word, i + 1, child):
                    return True
            return False

        child = node.get(ch)
        return child is not None and self._match(word, i + 1, child)


# ============================================================
# Key Takeaways
# ============================================================
# - Wildcards turn a deterministic trie walk into a small backtracking
#   search: a literal character still has exactly one edge to follow, but a
#   wildcard must fan out into every existing child and succeed if any
#   branch reaches a valid end-of-word at the pattern's end.
# - Common mistake: forgetting to check the end-of-word marker when the
#   pattern is exhausted (i == len(word)) — reaching a node at all only
#   means some longer word passes through it, not that a word ends there.
# - The trie's win over brute force shrinks as the number of wildcards
#   grows (branching factor 26 per dot); it stays fast here specifically
#   because the problem caps queries at 2 dots.
# - Related/variant problems to try next: Implement Trie (Prefix Tree),
#   Word Search II, Regular Expression Matching (a harder wildcard variant).


if __name__ == "__main__":
    def run_ops(cls, operations, args):
        results = []
        obj = None
        for op, arg in zip(operations, args):
            if op == "WordDictionary":
                obj = cls()
                results.append(None)
            else:
                results.append(getattr(obj, op)(*arg))
        return results

    tests = [
        (
            ["WordDictionary", "addWord", "addWord", "addWord",
             "search", "search", "search", "search"],
            [[], ["bad"], ["dad"], ["mad"], ["pad"], ["bad"], [".ad"], ["b.."]],
            [None, None, None, None, False, True, True, True],
        ),
        (
            ["WordDictionary", "addWord", "search", "search", "search", "search"],
            [[], ["a"], ["."], ["a"], [".."], ["ab"]],
            [None, None, True, True, False, False],
        ),
        (
            ["WordDictionary", "addWord", "addWord", "search", "search"],
            [[], ["at"], ["and"], ["a."], ["a.."]],
            [None, None, None, True, True],
        ),
    ]

    classes = [WordDictionaryBruteForce, WordDictionary]
    for operations, args, expected in tests:
        for cls in classes:
            result = run_ops(cls, operations, args)
            status = "OK" if result == expected else "FAIL"
            print(f"{cls.__name__:24s} ops={operations!r:75s} -> {result!r}  [{status}]")
