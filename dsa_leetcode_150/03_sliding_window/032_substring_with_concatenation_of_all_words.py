"""
LeetCode Top Interview 150 — #32 (LeetCode #30)
Substring with Concatenation of All Words
Category: Sliding Window | Difficulty: Hard

Problem
-------
You are given a string `s` and an array of strings `words`. All strings in `words` have the same
length.

A "concatenated substring" in `s` is a substring that contains all the strings of `words`
concatenated together in any order, with no characters in between and no characters left out.

Return the starting indices of all concatenated substrings in `s`, in any order. `words` may
contain duplicate strings, and each occurrence must be used as a distinct copy when concatenating
(i.e. if `words` has "foo" twice, the substring must contain "foo" twice too).

Constraints
-----------
- 1 <= s.length <= 10^4
- 1 <= words.length <= 5000
- 1 <= words[i].length <= 30
- words[i] and s consist of lowercase English letters.
- The sum of the lengths of all words does not exceed 10^5 (implied by the constraints above,
  and important for reasoning about total work).

Examples
--------
Example 1:
    Input: s = "barfoothefoobarman", words = ["foo","bar"]
    Output: [0,9]
    Explanation: The substring starting at 0 is "barfoo", which is "bar" + "foo" -- both words
    used once each. The substring starting at 9 is "foobar".

Example 2:
    Input: s = "wordgoodgoodgoodbestword", words = ["word","good","best","word"]
    Output: []
    Explanation: "word" appears twice in words, so any valid substring must contain "word" twice;
    no window of s satisfies that here.

Example 3:
    Input: s = "barfoofoobarthefoobarman", words = ["bar","foo","the"]
    Output: [6,9,12]

Intuition
---------
The naive move is to try every starting index in `s`, and for each one greedily peel off
`len(words)` consecutive chunks of length `word_len`, checking whether the multiset of chunks
matches the multiset of `words` — that's O(n * k) starts times chunks, each chunk comparison and
hashmap lookup costing O(word_len), so roughly O(n * k * word_len) which equals O(n * total_len).
The key optimization is to notice that only `word_len` distinct starting offsets matter (0, 1, ...,
word_len - 1) — any window boundary must fall on a "word_len grid" relative to one of those
offsets, since every match is a concatenation of fixed-length words with no gaps. Within a fixed
offset, we can slide a window forward one *word* at a time instead of one *character* at a time,
maintaining a running frequency count of the words currently inside the window (a true sliding
window: add a word on the right, and when a word's count exceeds what's needed — or an
unrecognized chunk appears — shrink from the left, or in the unrecognized-chunk case, jump the
whole window past it). This converts the problem from re-scanning windows from scratch into an
amortized single pass per offset, giving O(n * word_len) total instead of O(n * total_len).
"""

from typing import List
from collections import Counter


# ============================================================
# Approach 1: Brute Force
# ============================================================
# Idea: try every starting index; for each, slice out len(words) consecutive
# word_len-sized chunks and check the multiset of chunks equals the
# multiset of words.
# Time:  O(n * k * word_len) where n = len(s), k = len(words)
# Space: O(k * word_len) for the chunk counter per start
def solve_brute_force(s: str, words: List[str]) -> List[int]:
    if not s or not words or not words[0]:
        return []

    word_len = len(words[0])
    num_words = len(words)
    total_len = word_len * num_words
    target = Counter(words)
    result = []

    for start in range(len(s) - total_len + 1):
        seen = Counter()
        ok = True
        for i in range(num_words):
            chunk_start = start + i * word_len
            chunk = s[chunk_start:chunk_start + word_len]
            seen[chunk] += 1
            if seen[chunk] > target.get(chunk, 0):
                ok = False
                break
        if ok:
            result.append(start)

    return result


# ============================================================
# Approach 2: Optimal (sliding window per starting offset, word-at-a-time)
# ============================================================
# Idea: for each of the word_len possible alignments (offset 0..word_len-1),
# slide a window that grows/shrinks by whole words, maintaining a running
# word-frequency counter for the words currently in the window:
#   - If the next chunk isn't a word in `words` at all, the window can't
#     survive it -- reset the window to start right after this chunk.
#   - If the next chunk IS a word but adding it would exceed how many
#     copies `words` has of it, shrink from the left (dropping words one
#     at a time) until the count is valid again -- exactly like a
#     character-frequency sliding window, but the "characters" are whole
#     words.
#   - Once the window holds exactly num_words words, it's a match --
#     record its start, then evict the leftmost word to keep sliding (so
#     overlapping matches, as in Example 3, are all found).
# Dry run: s="barfoofoobarthefoobarman", words=["bar","foo","the"], word_len=3
#   offset=0: chunks at 0,3,6,9,12,15,18,21 = bar,foo,foo,bar,the,foo,bar,man
#     i=0 "bar": count{bar:1}, window=[0], size1
#     i=1 "foo": count{bar:1,foo:1}, window=[0,3], size2
#     i=2 "foo": target has foo:1, adding would make foo:2>1 -> shrink left
#         until foo count<=1: pop "bar"(idx0) count{bar:0,foo:1} window=[3],
#         still need to fit foo(new): count{bar:0,foo:1}->wait re-add foo:
#         after shrinking, add "foo" -> count{foo:2}? shrink again pop
#         "foo"(idx3) count{foo:1} window=[6], now add new foo -> count{foo:2}
#         still >1 -> shrink pop foo(idx6) window=[] count{}, add foo(idx6)
#         count{foo:1} window=[6]
#     i=3 "bar": count{foo:1,bar:1} window=[6,9] size2
#     i=4 "the": count{foo:1,bar:1,the:1} window=[6,9,12] size3 == num_words
#         -> MATCH start=6; evict leftmost "foo"(idx6) window=[9,12]
#     i=5 "foo": count{bar:1,the:1,foo:1} window=[9,12,15] size3 -> MATCH
#         start=9; evict leftmost "bar"(idx9) window=[12,15]
#     i=6 "bar": count{the:1,foo:1,bar:1} window=[12,15,18] size3 -> MATCH
#         start=12; evict leftmost "the"(idx12) window=[15,18]
#     i=7 "man": not in target -> window resets entirely -> window=[]
#   offsets 1 and 2 yield no additional matches for this example.
#   result (sorted) = [6, 9, 12]
# Time:  O(n * word_len) — each of the n/word_len chunks in each of the
#        word_len offsets is added and removed from its window at most once
# Space: O(k * word_len) for the target/window counters
def solve_optimal(s: str, words: List[str]) -> List[int]:
    if not s or not words or not words[0]:
        return []

    word_len = len(words[0])
    num_words = len(words)
    total_len = word_len * num_words
    n = len(s)
    if n < total_len:
        return []

    target = Counter(words)
    result = []

    for offset in range(word_len):
        window_count: Counter = Counter()
        window_words: List[str] = []  # queue of chunks currently in window, in order

        chunk_start = offset
        while chunk_start + word_len <= n:
            chunk = s[chunk_start:chunk_start + word_len]

            if chunk not in target:
                # Unusable chunk -- nothing spanning it can match, so drop
                # everything and restart fresh right after it.
                window_count.clear()
                window_words.clear()
                chunk_start += word_len
                continue

            window_words.append(chunk)
            window_count[chunk] += 1

            # Shrink from the left while this chunk is over-represented.
            while window_count[chunk] > target[chunk]:
                popped = window_words.pop(0)
                window_count[popped] -= 1

            if len(window_words) == num_words:
                match_start = chunk_start - (num_words - 1) * word_len
                result.append(match_start)
                # Slide by evicting the leftmost word to look for the next match.
                popped = window_words.pop(0)
                window_count[popped] -= 1

            chunk_start += word_len

    return sorted(result)


# ============================================================
# Key Takeaways
# ============================================================
# - When a "window" is made of fixed-length tokens (words) rather than
#   individual characters, slide the window one token at a time and split
#   the scan by starting offset (0..token_len-1) -- each offset is an
#   independent grid of non-overlapping tokens.
# - Common mistake: forgetting that an unrecognized chunk must fully reset
#   the window (not just shrink by one) -- no valid match can span across
#   a chunk that isn't one of the target words at all.
# - Related/variant problems to try next: Minimum Window Substring, Find
#   All Anagrams in a String, Longest Substring Without Repeating
#   Characters.


if __name__ == "__main__":
    tests = [
        (("barfoothefoobarman", ["foo", "bar"]), [0, 9]),
        (("wordgoodgoodgoodbestword", ["word", "good", "best", "word"]), []),
        (("barfoofoobarthefoobarman", ["bar", "foo", "the"]), [6, 9, 12]),
        (("a", ["a"]), [0]),
        (("aaaaaaaaaaaaaa", ["aa", "aa"]), [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),
        (("lingmindraboofooowingdingbarrwingmonkeypoundcake",
          ["fooo", "barr", "wing", "ding", "wing"]), [13]),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            # Order doesn't matter -- normalize by sorting before comparing.
            status = "OK" if sorted(result) == sorted(expected) else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:70s} -> {result!r}  [{status}]")
