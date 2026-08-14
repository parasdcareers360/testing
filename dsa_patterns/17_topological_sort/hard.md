# Hard — Alien Dictionary

**Source**: LeetCode #269 (Premium)
**Pattern**: Topological Sort
**Difficulty**: Hard

## Problem Statement
There is a new alien language that uses the English alphabet, but possibly in a different order than we know. You are given a list of strings `words` from the alien language's dictionary, where the strings in `words` are **sorted lexicographically** by the rules of this new language.

Derive the order of letters in this language, based on the given `words`. Return a string containing the unique letters in the order deduced from `words`, using the smallest possible letter set implied by the input. If the order is invalid (contradictory — i.e., no valid ordering can exist), return an empty string `""`. If there are multiple valid orders, return any one of them.

To determine ordering constraints between two adjacent words in the sorted list, compare them character by character until you find the first position where they differ; the letter from the first word at that position must come before the letter from the second word in the alien alphabet. If one word is a strict prefix of the other (e.g., `"abc"` and `"ab"`), no new ordering constraint is created *unless* the shorter word does not come first — if the longer word comes before its own prefix (e.g., `"abc"` before `"ab"`), that is a contradiction and the input is invalid.

## Constraints
- `1 <= words.length <= 100`
- `1 <= words[i].length <= 100`
- `words[i]` consists of only lowercase English letters.
- All characters used are among `'a'` through `'z'` (at most 26 distinct letters).

## Examples
**Example 1**
```
Input: words = ["wrt", "wrf", "er", "ett", "rftt"]
Output: "wertf"
```
Explanation: Comparing "wrt" & "wrf" → 't' before 'f'. "wrf" & "er" → 'w' before 'e'. "er" & "ett" → 'r' before 't'. "ett" & "rftt" → 'e' before 'r'. Combining all constraints (w<e, e<r, r<t, t<f) gives a valid topological order "wertf".

**Example 2**
```
Input: words = ["z", "x", "z"]
Output: ""
```
Explanation: "z" & "x" implies z before x. "x" & "z" implies x before z. These two constraints contradict each other (a cycle z->x->z), so no valid ordering exists.

**Example 3**
```
Input: words = ["abc", "ab"]
Output: ""
```
Explanation: "abc" comes before "ab" in the given sorted list, but "abc" is not a valid predecessor of its own prefix "ab" under any alphabet ordering (a shorter prefix must always sort before a longer string that extends it). This is a contradiction, so the answer is "".

**Example 4**
```
Input: words = ["ab", "abc"]
Output: any permutation of "a", "b", "c" (e.g. "abc", "bca", "cab" are all accepted)
```
Explanation: "ab" is a strict prefix of "abc" with the shorter word appearing first, which is valid and creates no contradiction. However, comparing them character by character never finds a differing position, so no ordering constraint between any pair of letters is derived at all. With zero constraints among {a, b, c}, every one of the 3! orderings is an equally valid topological sort, including one that happens to put 'b' before 'a'.

## Intuition — Why This Pattern
**Brute force**: Try every one of the 26! permutations of the alphabet and check whether all the words are sorted according to that permutation. This is astronomically infeasible (26! is about 4 * 10^26).

**A better but still weak idea**: extract pairwise letter-order constraints from *every pair* of words in the list (not just adjacent ones), then try to merge them. This produces O(n^2) comparisons for n words, most of which are redundant — if word[i] < word[i+1] and word[i+1] < word[i+2] are both satisfied, word[i] < word[i+2] is automatically implied and doesn't need to be extracted separately.

**The insight**: Because `words` is already sorted according to the alien alphabet, only **adjacent** pairs of words need to be compared to extract "letter X comes before letter Y" constraints — comparing non-adjacent pairs gives no new information beyond what's transitively implied by the chain of adjacent comparisons. Each such constraint is a directed edge X -> Y in a graph over the (at most 26) distinct letters used. The full valid letter order is then just a topological sort of this small graph: if the graph has a cycle, the order is contradictory (return `""`); otherwise, any valid topological order is an acceptable answer. This turns an intractable search over permutations into an O(C) graph problem, where C is the total number of characters across all words (bounded by 26 nodes and at most 26*25/2 edges, plus the prefix-validity check).

## Approach
1. Initialize a graph as an adjacency structure (set of neighbors) over all distinct letters found in `words`, and an `in_degree` map initialized to 0 for every distinct letter.
2. For each pair of adjacent words `(w1, w2)` in `words` (i.e., `words[i]` and `words[i+1]`):
   a. Compare characters at the same index until the first mismatch is found.
   b. If a mismatch is found at position `k` (`w1[k] != w2[k]`), and there is no existing edge `w1[k] -> w2[k]` yet, add the edge and increment `in_degree[w2[k]]`. Stop comparing this pair (no further characters matter).
   c. If no mismatch is found up through the shorter word's length (one is a prefix of the other), check lengths: if `len(w1) > len(w2)`, this is a contradiction (a longer word cannot precede its own prefix) — return `""` immediately.
3. Run Kahn's algorithm (BFS topological sort) over the letter graph: start with all letters at in-degree 0 in a queue, repeatedly pop a letter, append to the result, and decrement in-degree of its neighbors, pushing any that reach 0.
4. If the resulting order contains all distinct letters seen in `words`, return it as a string. Otherwise (a cycle blocked some letters), return `""`.

## Dry Run
Example 1: `words = ["wrt", "wrf", "er", "ett", "rftt"]`.

- Distinct letters: {w, r, t, f, e} → 5 nodes. `in_degree = {w:0, r:0, t:0, f:0, e:0}`, `graph = {w:[], r:[], t:[], f:[], e:[]}`.
- Compare adjacent pair ("wrt", "wrf"): index 0 'w'='w', index 1 'r'='r', index 2 't'!='f' → mismatch. Add edge `t -> f`. `graph[t]=[f]`, `in_degree[f]=1`.
- Compare ("wrf", "er"): index 0 'w'!='e' → mismatch immediately. Add edge `w -> e`. `graph[w]=[e]`, `in_degree[e]=1`.
- Compare ("er", "ett"): index 0 'e'='e', index 1 'r'!='t' → mismatch. Add edge `r -> t`. `graph[r]=[t]`, `in_degree[t]=1`.
- Compare ("ett", "rftt"): index 0 'e'!='r' → mismatch. Add edge `e -> r`. `graph[e]=[r]`, `in_degree[r]=1`.
- Final graph: `w->e`, `e->r`, `r->t`, `t->f`. In-degrees: `w:0, e:1, r:1, t:1, f:1`.
- Kahn's: queue starts with letters at in-degree 0 → `[w]`.
  - Pop `w` → order = "w". Neighbor `e`: in_degree[e] 1→0, push. queue=[e].
  - Pop `e` → order = "we". Neighbor `r`: in_degree[r] 1→0, push. queue=[r].
  - Pop `r` → order = "wer". Neighbor `t`: in_degree[t] 1→0, push. queue=[t].
  - Pop `t` → order = "wert". Neighbor `f`: in_degree[f] 1→0, push. queue=[f].
  - Pop `f` → order = "wertf". No neighbors. queue=[].
- All 5 letters present in order → return `"wertf"`. Matches expected output.

## Solution (Python 3)
```python
from collections import deque, defaultdict
from typing import List


def alien_order(words: List[str]) -> str:
    # Collect all distinct letters.
    letters = set()
    for w in words:
        letters.update(w)

    graph = defaultdict(set)
    in_degree = {c: 0 for c in letters}

    for w1, w2 in zip(words, words[1:]):
        min_len = min(len(w1), len(w2))
        found_diff = False
        for i in range(min_len):
            c1, c2 = w1[i], w2[i]
            if c1 != c2:
                if c2 not in graph[c1]:
                    graph[c1].add(c2)
                    in_degree[c2] += 1
                found_diff = True
                break
        if not found_diff and len(w1) > len(w2):
            # w1 is longer than its own prefix w2 but appears before it: contradiction.
            return ""

    queue = deque([c for c in letters if in_degree[c] == 0])
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for nbr in graph[node]:
            in_degree[nbr] -= 1
            if in_degree[nbr] == 0:
                queue.append(nbr)

    if len(order) != len(letters):
        return ""  # Cycle detected.

    return "".join(order)


if __name__ == "__main__":
    print(alien_order(["wrt", "wrf", "er", "ett", "rftt"]))  # Expected: "wertf"
    print(alien_order(["z", "x", "z"]))                       # Expected: ""
    print(alien_order(["abc", "ab"]))                          # Expected: ""
    print(alien_order(["ab", "abc"]))                          # Expected: any permutation of {a,b,c} (no constraints derived)
```

## Complexity Analysis
- Time: O(C) where C is the total number of characters across all words — each adjacent word pair comparison stops at the first mismatch, so total comparison work is bounded by the total character count. The topological sort itself runs on at most 26 nodes and at most 26*25/2 edges, which is O(1) relative to input size, but is generally expressed as O(V + E) = O(26 + 26^2) = O(1)-ish, so overall time is dominated by O(C).
- Space: O(1) extra for the graph/in-degree structures (bounded by 26 letters), plus O(C) implicitly for storing the input words themselves.

## Key Takeaways
- The key trick that makes this tractable is realizing only **adjacent** words need pairwise comparison — non-adjacent relationships are transitively implied once every adjacent pair contributes its constraint edges.
- The "prefix contradiction" edge case (a longer word appearing before its own prefix) is easy to miss and is a classic source of wrong answers — always check `len(w1) > len(w2)` when no character mismatch is found.
- Avoid adding duplicate edges between the same pair of letters (it silently inflates in-degree counts and breaks Kahn's algorithm) — use a set for each node's neighbor list.
- Related/variant problems to try next: Course Schedule II (simpler topological sort without the string-comparison extraction step), Sequence Reconstruction (checking topological sort uniqueness), Verifying an Alien Dictionary (LC #953, an easier related problem that only checks whether words are sorted given a known order).
