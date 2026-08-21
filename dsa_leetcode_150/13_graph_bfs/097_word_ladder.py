"""
LeetCode Top Interview 150 — #97 (LeetCode #127)
Word Ladder
Category: Graph BFS | Difficulty: Hard

Problem
-------
A transformation sequence from word `beginWord` to word `endWord` using a dictionary `wordList`
is a sequence of words `beginWord -> s1 -> s2 -> ... -> sk` such that:

- Every adjacent pair of words differs by exactly one letter.
- Every `si` for `1 <= i <= k` is in `wordList`. Note that `beginWord` does not need to be in
  `wordList`.
- `sk == endWord`.

Given two words `beginWord` and `endWord`, and a dictionary `wordList`, return the number of
words in the **shortest** transformation sequence from `beginWord` to `endWord`, or 0 if no such
sequence exists.

Constraints
-----------
- 1 <= beginWord.length <= 10
- endWord.length == beginWord.length
- 1 <= wordList.length <= 5000
- wordList[i].length == beginWord.length
- beginWord, endWord, and wordList[i] consist of lowercase English letters
- beginWord != endWord
- All the words in wordList are unique

Examples
--------
Example 1:
    Input: beginWord = "hit", endWord = "cog", wordList = ["hot","dot","dog","lot","log","cog"]
    Output: 5
    Explanation: One shortest transformation sequence is
    "hit" -> "hot" -> "dot" -> "dog" -> "cog", which has 5 words.

Example 2:
    Input: beginWord = "hit", endWord = "cog", wordList = ["hot","dot","dog","lot","log"]
    Output: 0
    Explanation: endWord "cog" is not in wordList, so no valid transformation sequence exists.

Intuition
---------
Same shape as Minimum Genetic Mutation (#96): words are nodes, an edge connects two words that
differ by exactly one letter, and we want the shortest path — so BFS layer-by-layer from
`beginWord`. The naive way to find neighbors of a word is to compare it against every other word
in the dictionary character-by-character, which is O(wordCount * L) per node and gets expensive
as `wordList` grows to thousands of entries. A much better technique: precompute a map from
**wildcard patterns** (e.g. "h*t" for "hot" with the middle letter blanked) to every word that
matches that pattern. Then a word's neighbors are found by generating its L wildcard patterns and
looking each up in O(1) — no scanning the dictionary at all. The best approach layers bidirectional
BFS on top of the pattern map: grow the search from both `beginWord` and `endWord` at once,
expanding whichever frontier is smaller, which shrinks the explored state space dramatically when
the ladder is long or the dictionary is dense.
"""

from typing import List
from collections import deque, defaultdict


# ============================================================
# Approach 1: Brute Force (BFS, compare against every word)
# ============================================================
# Idea: BFS over words; a neighbor of the current word is any unvisited
# word in the dictionary that differs by exactly one letter, found by
# scanning the whole word list and diffing character by character.
# Time:  O(W^2 * L) where W = len(wordList), L = word length
# Space: O(W) for visited set and queue
def solve_brute_force(beginWord: str, endWord: str, wordList: List[str]) -> int:
    word_set = set(wordList)
    if endWord not in word_set:
        return 0

    def one_letter_apart(a: str, b: str) -> bool:
        diffs = 0
        for ca, cb in zip(a, b):
            if ca != cb:
                diffs += 1
                if diffs > 1:
                    return False
        return diffs == 1

    visited = {beginWord}
    queue = deque([(beginWord, 1)])
    while queue:
        word, length = queue.popleft()
        if word == endWord:
            return length
        for candidate in word_set:
            if candidate not in visited and one_letter_apart(word, candidate):
                visited.add(candidate)
                queue.append((candidate, length + 1))
    return 0


# ============================================================
# Approach 2: Optimal (BFS with precomputed wildcard-pattern adjacency)
# ============================================================
# Idea: for each word, generate its L "wildcard" patterns (one per position,
# with that position blanked to '*') and build a map pattern -> [words that
# match it]. Two words are neighbors iff they share a pattern. BFS expands a
# word by generating its L patterns and looking up matches in O(1) per
# pattern, instead of scanning the whole dictionary.
# Dry run: beginWord="hit", endWord="cog",
#          wordList=["hot","dot","dog","lot","log","cog"]
#   pattern map includes "*ot"->[hot,dot,lot], "*og"->[dog,log,cog], ...
#   BFS: "hit"(1) -> patterns "*it","h*t","hi*" -> only "hot" matches "h*t"
#        -> push "hot"(2)
#        "hot"(2) -> "*ot" matches dot,lot -> push dot(3), lot(3)
#        "dot"(3) -> "*og"? no, "dot" patterns are "*ot","d*t","do*" ->
#          "do*" matches "dog" -> push dog(4)
#        "lot"(3) -> "lo*" matches "log" -> push log(4)
#        "dog"(4) -> "*og" matches "cog" -> push cog(5)
#        pop cog(5) == endWord -> return 5
# Time:  O(W * L^2) to build the map + O(W * L^2) for BFS (each word
#        generates L patterns of length L)
# Space: O(W * L) for the pattern map
def solve_optimal(beginWord: str, endWord: str, wordList: List[str]) -> int:
    word_set = set(wordList)
    if endWord not in word_set:
        return 0

    L = len(beginWord)
    pattern_map = defaultdict(list)
    for word in word_set:
        for i in range(L):
            pattern = word[:i] + "*" + word[i + 1:]
            pattern_map[pattern].append(word)

    visited = {beginWord}
    queue = deque([(beginWord, 1)])
    while queue:
        word, length = queue.popleft()
        if word == endWord:
            return length
        for i in range(L):
            pattern = word[:i] + "*" + word[i + 1:]
            for neighbor in pattern_map[pattern]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, length + 1))
            # Once a pattern's matches are all consumed for this BFS layer,
            # clearing it avoids re-scanning the same bucket from later words.
            pattern_map[pattern] = []
    return 0


# ============================================================
# Approach 3: Best (bidirectional BFS with the pattern map)
# ============================================================
# Idea: combine the wildcard-pattern trick with bidirectional BFS. Grow
# frontiers from beginWord and endWord simultaneously, always expanding the
# smaller one, and stop as soon as the two frontiers share a word. This
# bounds the explored state space to roughly two balls of radius d/2 instead
# of one ball of radius d, which matters a lot when the ladder is long.
# Time:  O(W * L^2) worst case, far fewer states explored in practice
# Space: O(W * L)
def solve_best(beginWord: str, endWord: str, wordList: List[str]) -> int:
    word_set = set(wordList)
    if endWord not in word_set:
        return 0

    L = len(beginWord)
    pattern_map = defaultdict(list)
    for word in word_set | {beginWord}:
        for i in range(L):
            pattern = word[:i] + "*" + word[i + 1:]
            pattern_map[pattern].append(word)

    def patterns_of(word: str):
        return (word[:i] + "*" + word[i + 1:] for i in range(L))

    front_start = {beginWord}
    front_end = {endWord}
    visited = {beginWord, endWord}
    length = 1  # words visited so far on the shortest path being built

    while front_start and front_end:
        if len(front_start) > len(front_end):
            front_start, front_end = front_end, front_start

        next_front = set()
        for word in front_start:
            for pattern in patterns_of(word):
                for neighbor in pattern_map.get(pattern, []):
                    if neighbor in front_end:
                        return length + 1
                    if neighbor not in visited:
                        visited.add(neighbor)
                        next_front.add(neighbor)
        front_start = next_front
        length += 1

    return 0


# ============================================================
# Key Takeaways
# ============================================================
# - Word Ladder is BFS shortest-path over an implicit graph where edges are
#   "differs by exactly one letter" — recognize this shape whenever a
#   problem asks for the minimum number of single-step transformations.
# - Precomputing a wildcard-pattern -> words map turns neighbor lookup from
#   an O(W) scan into an O(1) bucket fetch, which is the difference between
#   TLE and passing on large dictionaries.
# - Bidirectional BFS is the strongest technique whenever both the start and
#   the target are known upfront — expanding the smaller frontier each round
#   keeps the two searches balanced and meeting quickly.
# - Related/variant problems to try next: Minimum Genetic Mutation, Word
#   Ladder II (reconstruct all shortest paths), Open the Lock.


if __name__ == "__main__":
    tests = [
        (("hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"]), 5),
        (("hit", "cog", ["hot", "dot", "dog", "lot", "log"]), 0),
        (("a", "c", ["a", "b", "c"]), 2),
        (("hot", "dog", ["hot", "dog"]), 0),
        (("cat", "cog", ["cat", "cot", "cog"]), 3),
    ]

    approaches = [solve_brute_force, solve_optimal, solve_best]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:75s} -> {result!r}  [{status}]")
