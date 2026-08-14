# Medium — Design Add and Search Words Data Structure

**Source**: LeetCode #211
**Pattern**: Trie (Prefix Tree)
**Difficulty**: Medium

## Problem Statement
Design a data structure that supports adding new words and finding if a string matches any previously added string.

Implement the `WordDictionary` class:

- `WordDictionary()` Initializes the object.
- `void addWord(word)` Adds `word` to the data structure, it can be matched later.
- `bool search(word)` Returns `true` if there is any string in the data structure that matches `word`, and `false` otherwise. `word` may contain dots `'.'` where dots can be matched with any one letter (i.e., `'.'` is a single-character wildcard).

## Constraints
- `1 <= word.length <= 25`
- `word` in `addWord` consists of lowercase English letters.
- `word` in `search` consists of `'.'` or lowercase English letters.
- There will be at most `2 * 10^4` calls in total to `addWord` and `search`.

## Examples
```
Input:
["WordDictionary", "addWord", "addWord", "addWord", "search", "search", "search", "search"]
[[], ["bad"], ["dad"], ["mad"], ["pad"], ["bad"], [".ad"], ["b.."]]

Output:
[null, null, null, null, false, true, true, true]
```
Explanation: after adding "bad", "dad", "mad":
- `search("pad")` → `false` (no word "pad" was added, and there is no wildcard here to allow flexibility — it's an exact literal search that fails).
- `search("bad")` → `true` (exact match, "bad" was added).
- `search(".ad")` → `true` ('.' can match 'b', 'd', or 'm' — "bad"/"dad"/"mad" all match).
- `search("b..")` → `true` (the two dots match 'a' and 'd' respectively, matching "bad").

A second example: after `addWord("a")`, `addWord("a")` again (duplicates allowed, harmless), `search("a")` → `true`, `search(".")` → `true` (single dot matches the single-character word "a"), `search("aa")` → `false` (no 2-letter word was added, and length must match exactly since each `.` matches exactly one character).

## Intuition — Why This Pattern
**Brute force**: Store all added words in a list. For `search(word)` with no dots, scan the whole list and compare directly — O(number of words × word length). For a `word` containing dots, you'd need to compare each stored word of the *same length* against the pattern character-by-character (treating `.` as "matches anything"), which is still O(number of words × word length) per query. With up to 20,000 calls, this can degrade badly if many words are stored and many searches contain dots.

**What's inefficient**: Just like the plain Trie problem, a linear scan re-examines every stored word from scratch, ignoring the fact that words share prefixes. But there's a new wrinkle here beyond the basic Trie: the search pattern can contain `'.'`, which means at some position in the traversal we don't know which branch to follow — we might need to explore *multiple* children.

**Insight the pattern provides**: Keep the same Trie structure as in the basic Implement Trie problem (nodes with `children` dict + `is_end` flag). For `addWord`, insertion is identical to before. For `search`, when we encounter a literal character we walk down exactly one branch as usual (O(1) step); when we encounter `'.'`, we branch into a **recursive/backtracking exploration of all children** at that position, trying each one and recursing on the rest of the pattern. This keeps deterministic characters cheap (as in a plain Trie) while only paying extra cost at the positions where wildcards actually appear, rather than scanning every stored word unconditionally.

## Approach
1. Reuse the standard `TrieNode` (children dict + `is_end` flag) and `WordDictionary.root`.
2. **`addWord(word)`**: identical to plain Trie insertion — walk/create nodes character by character, mark the last node's `is_end = True`.
3. **`search(word)`**: implement as a recursive helper `dfs(node, index)`:
   a. **Base case**: if `index == len(word)`, return `node.is_end` (we've consumed the whole pattern; check if a real word ends exactly here).
   b. Let `ch = word[index]`.
   c. If `ch != '.'`:
      - If `ch` is not in `node.children`, return `False` (dead end).
      - Otherwise recurse: `return dfs(node.children[ch], index + 1)`.
   d. If `ch == '.'` (wildcard):
      - For every child `child_node` in `node.children.values()`:
        - If `dfs(child_node, index + 1)` returns `True`, return `True` immediately (short-circuit — we found a match).
      - If no child led to a match, return `False`.
4. Call `dfs(self.root, 0)` to start the search from the root.

## Dry Run
Trace `addWord("bad")`, `addWord("dad")`, `addWord("mad")`, then `search(".ad")`.

**After the three `addWord` calls**, the trie looks like:
```
root
 ├─ 'b' (end=F)
 │   └─ 'a' (end=F)
 │       └─ 'd' (end=T)      <- "bad"
 ├─ 'd' (end=F)
 │   └─ 'a' (end=F)
 │       └─ 'd' (end=T)      <- "dad"
 └─ 'm' (end=F)
     └─ 'a' (end=F)
         └─ 'd' (end=T)      <- "mad"
```

**`search(".ad")`** → call `dfs(root, 0)`, pattern = `.ad`.

- `index=0`, `ch = '.'` (wildcard). Root has 3 children: `'b'`, `'d'`, `'m'`. Try each:
  - Try child `'b'`: recurse `dfs(node_b, 1)`.
    - `index=1`, `ch = 'a'` (literal). `node_b.children` has `'a'` → recurse `dfs(node_ba, 2)`.
      - `index=2`, `ch = 'd'` (literal). `node_ba.children` has `'d'` → recurse `dfs(node_bad, 3)`.
        - `index=3 == len(".ad")=3` → base case. Return `node_bad.is_end` = `True`.
      - Returns `True` up the chain.
    - Returns `True` up the chain.
  - `dfs(node_b, 1)` returned `True`, so the wildcard branch at index 0 short-circuits and returns `True` immediately (no need to try `'d'` or `'m'`).
- Final result: `search(".ad")` → `True`. ✓

(For contrast, if none of the three children had matched — e.g., pattern `.xy` — the loop would try `'b'`, `'d'`, `'m'` in turn, all failing at index 1, and finally return `False` after exhausting all children.)

## Solution (Python 3)
```python
class TrieNode:
    __slots__ = ("children", "is_end")

    def __init__(self):
        self.children = {}
        self.is_end = False


class WordDictionary:
    def __init__(self):
        self.root = TrieNode()

    def addWord(self, word: str) -> None:
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True

    def search(self, word: str) -> bool:
        def dfs(node: TrieNode, index: int) -> bool:
            if index == len(word):
                return node.is_end

            ch = word[index]
            if ch != '.':
                child = node.children.get(ch)
                if child is None:
                    return False
                return dfs(child, index + 1)
            else:
                for child in node.children.values():
                    if dfs(child, index + 1):
                        return True
                return False

        return dfs(self.root, 0)


if __name__ == "__main__":
    wd = WordDictionary()
    wd.addWord("bad")
    wd.addWord("dad")
    wd.addWord("mad")
    print(wd.search("pad"))   # False
    print(wd.search("bad"))   # True
    print(wd.search(".ad"))   # True
    print(wd.search("b.."))   # True

    wd2 = WordDictionary()
    wd2.addWord("a")
    wd2.addWord("a")
    print(wd2.search("a"))    # True
    print(wd2.search("."))    # True
    print(wd2.search("aa"))   # False
```

## Complexity Analysis
- Time:
  - `addWord`: O(L) where L is the word length.
  - `search`: worst case O(26^D × L) where D is the number of dots in the pattern and L is its length — each dot can branch into up to 26 children (lowercase alphabet). In practice this is much faster because failed branches are pruned early (a `child is None` check or a `False` recursive result stops exploration immediately), and D is usually small relative to L.
- Space: O(total characters inserted across all unique prefixes) for the trie itself, plus O(L) recursion stack depth per `search` call.

## Key Takeaways
- The wildcard character turns a simple O(1)-per-step Trie walk into a **backtracking search over Trie children** — this is the key twist that distinguishes this problem from plain Trie lookup.
- Common mistake: forgetting the base case must check `index == len(word)` *and* `node.is_end` together — reaching the end of the pattern string doesn't mean a real word ends there (e.g., searching `"ba"` should fail even though the path `b -> a` exists, because no word ends at that node).
- Common mistake: not short-circuiting on the first successful branch in the wildcard case — always return `True` as soon as one child succeeds instead of checking all of them (correctness is unaffected, but efficiency suffers badly on patterns with many dots).
- Related/variant problems to try next: **Word Search II** (LeetCode #212, Trie + grid DFS — see the hard example in this folder) and **Replace Words** (LeetCode #648, prefix-only Trie lookup).
