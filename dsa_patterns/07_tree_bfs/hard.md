# Hard — Word Ladder

**Source**: LeetCode #127
**Pattern**: Tree BFS (BFS on an implicit graph)
**Difficulty**: Hard

## Problem Statement
You are given two words, `beginWord` and `endWord`, both of the same length, and a dictionary `wordList`. A **transformation sequence** from `beginWord` to `endWord` is a sequence of words `beginWord -> s1 -> s2 -> ... -> sk` such that:
- Every adjacent pair of words differs by exactly one letter.
- Every word `si` (for `1 <= i <= k`) must exist in `wordList`. Note that `beginWord` does not need to be in `wordList`.
- `sk == endWord`.

Given `beginWord`, `endWord`, and `wordList`, return the number of words in the **shortest** transformation sequence from `beginWord` to `endWord`, or `0` if no such sequence exists.

## Constraints
- `1 <= beginWord.length <= 10`
- `endWord.length == beginWord.length`
- `1 <= wordList.length <= 5000`
- `wordList[i].length == beginWord.length`
- `beginWord`, `endWord`, and every word in `wordList` consist of lowercase English letters only.
- `beginWord != endWord`
- All words in `wordList` are unique.

## Examples
**Example 1**
Input: `beginWord = "hit"`, `endWord = "cog"`, `wordList = ["hot","dot","dog","lot","log","cog"]`
Output: `5`
Explanation: One shortest transformation is `"hit" -> "hot" -> "dot" -> "dog" -> "cog"`, which has 5 words total.

**Example 2**
Input: `beginWord = "hit"`, `endWord = "cog"`, `wordList = ["hot","dot","dog","lot","log"]`
Output: `0`
Explanation: `endWord = "cog"` is not in `wordList`, so no valid transformation sequence can end at it.

## Intuition — Why This Pattern
A brute-force approach would explore every possible transformation path via DFS/backtracking: from the current word, try changing each letter to each of the 25 alternatives, recurse if the result is a valid dictionary word not yet used, and backtrack otherwise. This *can* find a valid path, but DFS naturally finds *some* path first, not necessarily the *shortest* one — guaranteeing minimality would require exploring all possible paths to their ends and comparing lengths, which is exponential and wasteful.

The key realization: this is secretly a shortest-path problem on an unweighted implicit graph, where each dictionary word (plus `beginWord`) is a "node," and an edge connects two words if they differ by exactly one letter. "Shortest path in an unweighted graph" is exactly the signature that BFS solves optimally — BFS explores all nodes at distance 1, then all nodes at distance 2, and so on, so the very first time it reaches `endWord`, that path is guaranteed to be the shortest possible, with no need to explore further or compare alternatives.

## Approach
1. Put `wordList` into a set `word_set` for O(1) membership checks. If `endWord` is not in `word_set`, return `0` immediately (it can never be reached).
2. Initialize a queue with the pair `(beginWord, 1)` (word, current path length so far, counting `beginWord` itself), and a `visited` set containing `beginWord`.
3. While the queue is non-empty:
   a. Pop `(word, level)` from the front.
   b. If `word == endWord`, return `level`.
   c. For every position `i` in the word, and every lowercase letter `c` different from `word[i]`: build `candidate = word[:i] + c + word[i+1:]`.
   d. If `candidate` is in `word_set` and not yet in `visited`: mark it visited, and enqueue `(candidate, level + 1)`.
4. If the queue empties out without ever reaching `endWord`, return `0`.

## Dry Run
Input: `beginWord = "hit"`, `endWord = "cog"`, `wordList = ["hot","dot","dog","lot","log","cog"]`

`word_set = {"hot","dot","dog","lot","log","cog"}`. `"cog"` is present, so we proceed.

| Step | Popped (word, level) | New candidates found in word_set (unvisited) | Queue after |
|------|------------------------|-----------------------------------------------|-------------|
| 1 | `("hit", 1)` | `"hot"` | `[("hot", 2)]` |
| 2 | `("hot", 2)` | `"dot"`, `"lot"` | `[("dot", 3), ("lot", 3)]` |
| 3 | `("dot", 3)` | `"dog"` | `[("lot", 3), ("dog", 4)]` |
| 4 | `("lot", 3)` | `"log"` | `[("dog", 4), ("log", 4)]` |
| 5 | `("dog", 4)` | `"cog"` | `[("log", 4), ("cog", 5)]` |
| 6 | `("log", 4)` | (`"cog"` already visited) | `[("cog", 5)]` |
| 7 | `("cog", 5)` | word == endWord! | — |

At step 7, `word == endWord`, so we return `level = 5`. This matches the expected output and corresponds exactly to the path `hit -> hot -> dot -> dog -> cog` (5 words).

## Solution (Python 3)
```python
from collections import deque
from typing import List


def ladder_length(begin_word: str, end_word: str, word_list: List[str]) -> int:
    word_set = set(word_list)
    if end_word not in word_set:
        return 0

    queue = deque([(begin_word, 1)])
    visited = {begin_word}
    alphabet = "abcdefghijklmnopqrstuvwxyz"

    while queue:
        word, level = queue.popleft()
        if word == end_word:
            return level
        for i in range(len(word)):
            for c in alphabet:
                if c == word[i]:
                    continue
                candidate = word[:i] + c + word[i + 1:]
                if candidate in word_set and candidate not in visited:
                    visited.add(candidate)
                    queue.append((candidate, level + 1))

    return 0


if __name__ == "__main__":
    print(ladder_length("hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"]))  # Expected: 5
    print(ladder_length("hit", "cog", ["hot", "dot", "dog", "lot", "log"]))         # Expected: 0
```

## Complexity Analysis
- Time: O(N * L^2 * 26), where `N` is the number of words in `wordList` and `L` is the word length — for each word dequeued, we generate `L * 26` candidates, each costing O(L) to build the string and O(L) to hash for the set lookup.
- Space: O(N * L) for `word_set` and `visited`.

## Key Takeaways
- "Shortest number of steps/transformations between two states" is a strong signal to model the problem as an implicit graph and run BFS, not DFS — DFS finds *a* path, BFS guarantees the *shortest* one.
- Common mistake: marking a word visited only *after* popping it from the queue instead of at the moment it's enqueued — this lets the same word be added to the queue multiple times from different parents, wasting work and potentially breaking the level count.
- For very large dictionaries, a bidirectional BFS (growing the search simultaneously from `beginWord` and `endWord` and stopping when the two frontiers meet) dramatically reduces the search space — a standard follow-up optimization for this exact problem.
- Related/variant problems to try next: **Word Ladder II** (return every shortest transformation sequence, not just the count), **Rotting Oranges** (multi-source BFS on a grid), **Minimum Genetic Mutation**.
