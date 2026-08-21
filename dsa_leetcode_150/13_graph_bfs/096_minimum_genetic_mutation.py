"""
LeetCode Top Interview 150 — #96 (LeetCode #433)
Minimum Genetic Mutation
Category: Graph BFS | Difficulty: Medium

Problem
-------
A gene string is represented by an 8-character-long string, with each character chosen from
`'A'`, `'C'`, `'G'`, `'T'`.

Suppose there is a gene string `startGene` that needs to mutate into a gene string `endGene`.
One mutation is defined as changing exactly one character in the gene string.

There is also a `bank` of valid gene mutations. A gene must be in `bank` to be a valid intermediate
mutation — every gene along the mutation path from `startGene` to `endGene` (except `startGene`
itself) must appear in `bank`.

Given `startGene`, `endGene`, and `bank`, return the minimum number of mutations needed to mutate
`startGene` to `endGene`. If there is no such mutation path, return -1.

Note: `startGene` is assumed to be valid, so it doesn't need to appear in `bank`.

Constraints
-----------
- 0 <= bank.length <= 10
- startGene.length == endGene.length == bank[i].length == 8
- startGene, endGene, and bank[i] consist of only the characters ['A', 'C', 'G', 'T']

Examples
--------
Example 1:
    Input: startGene = "AACCGGTT", endGene = "AACCGGTA", bank = ["AACCGGTA"]
    Output: 1

Example 2:
    Input: startGene = "AACCGGTT", endGene = "AAACGGTA", bank = ["AACCGGTA","AACCGCTA","AAACGGTA"]
    Output: 2

Intuition
---------
This is shortest-path-in-an-unweighted-graph in disguise: each valid gene string (in `bank`, plus
the start) is a node, and an edge connects two genes that differ in exactly one character. Since
every edge has the same "cost" (one mutation), BFS from `startGene` finds the minimum number of
mutations to reach `endGene`, if reachable at all. The brute-force way to find neighbors of a gene
is to compare it against every other gene in `bank` and count differing characters — fine since
`bank` has at most 10 entries. The more scalable technique (and the one that generalizes to Word
Ladder, problem #97, where the dictionary can be huge) is to *generate* neighbors directly by
trying all 4 characters at each of the 8 positions and checking membership in a set — this avoids
the O(bank) comparison per node and turns each expansion into O(8 * 4) work regardless of bank
size.
"""

from typing import List
from collections import deque


# ============================================================
# Approach 1: Brute Force (BFS, compare against every bank entry)
# ============================================================
# Idea: BFS over gene strings; a neighbor of the current gene is any gene in
# `bank` that differs by exactly one character. Finding neighbors costs
# O(bank * 8) per node since we scan the whole bank and diff each string.
# Time:  O(bank^2 * 8) in the worst case (each BFS pop rescans the bank)
# Space: O(bank) for the visited set and queue
def solve_brute_force(startGene: str, endGene: str, bank: List[str]) -> int:
    if startGene == endGene:
        return 0
    if endGene not in bank:
        return -1

    def one_mutation_apart(a: str, b: str) -> bool:
        diffs = 0
        for ca, cb in zip(a, b):
            if ca != cb:
                diffs += 1
                if diffs > 1:
                    return False
        return diffs == 1

    visited = {startGene}
    queue = deque([(startGene, 0)])
    while queue:
        gene, steps = queue.popleft()
        if gene == endGene:
            return steps
        for candidate in bank:
            if candidate not in visited and one_mutation_apart(gene, candidate):
                visited.add(candidate)
                queue.append((candidate, steps + 1))
    return -1


# ============================================================
# Approach 2: Optimal (BFS, generate neighbors by substitution)
# ============================================================
# Idea: instead of scanning the whole bank to find neighbors, generate every
# possible 1-character mutation of the current gene (8 positions * 4 bases =
# 32 candidates) and check each against a set of valid genes (the bank).
# This decouples expansion cost from bank size entirely.
# Dry run: startGene="AACCGGTT", endGene="AACCGGTA", bank={"AACCGGTA"}
#   pop "AACCGGTT" steps=0 -> mutate last char through A/C/G/T ->
#     "AACCGGTA" is in bank & unvisited -> push ("AACCGGTA", 1)
#   pop "AACCGGTA" steps=1 -> equals endGene -> return 1
# Time:  O(N * 8 * 4) where N = len(bank), each node generates 32 candidates
# Space: O(N) for the visited/bank sets and queue
def solve_optimal(startGene: str, endGene: str, bank: List[str]) -> int:
    if startGene == endGene:
        return 0
    bank_set = set(bank)
    if endGene not in bank_set:
        return -1

    bases = "ACGT"
    visited = {startGene}
    queue = deque([(startGene, 0)])
    while queue:
        gene, steps = queue.popleft()
        if gene == endGene:
            return steps
        for i in range(len(gene)):
            for base in bases:
                if base == gene[i]:
                    continue
                candidate = gene[:i] + base + gene[i + 1:]
                if candidate in bank_set and candidate not in visited:
                    visited.add(candidate)
                    queue.append((candidate, steps + 1))
    return -1


# ============================================================
# Approach 3: Best (bidirectional BFS)
# ============================================================
# Idea: grow a BFS frontier from startGene and another from endGene
# simultaneously, always expanding the smaller frontier. When the two
# frontiers meet, the total mutations found so far is the answer. This
# shrinks the search space from one ball of radius d to two balls of
# radius d/2, which is a huge win when the branching factor is high
# (here 8*3=24 real mutations per node).
# Time:  O(N * 8 * 4) worst case, but explores far fewer states in practice
# Space: O(N)
def solve_best(startGene: str, endGene: str, bank: List[str]) -> int:
    if startGene == endGene:
        return 0
    bank_set = set(bank)
    if endGene not in bank_set:
        return -1

    bases = "ACGT"

    def neighbors(gene: str):
        for i in range(len(gene)):
            for base in bases:
                if base != gene[i]:
                    yield gene[:i] + base + gene[i + 1:]

    front_start = {startGene}
    front_end = {endGene}
    visited = {startGene, endGene}
    steps = 0

    while front_start and front_end:
        # Always expand the smaller frontier to keep work balanced.
        if len(front_start) > len(front_end):
            front_start, front_end = front_end, front_start

        next_front = set()
        for gene in front_start:
            for nxt in neighbors(gene):
                if nxt in front_end:
                    return steps + 1
                if nxt in bank_set and nxt not in visited:
                    visited.add(nxt)
                    next_front.add(nxt)
        front_start = next_front
        steps += 1

    return -1


# ============================================================
# Key Takeaways
# ============================================================
# - Modeling "one character/step change" problems as an unweighted graph and
#   running BFS is the standard way to find the minimum number of edits —
#   this exact pattern reappears in Word Ladder (#97).
# - Generating neighbors by substitution (try all alphabet choices at each
#   position) beats scanning the whole candidate list when the alphabet is
#   small and fixed, decoupling expansion cost from dictionary size.
# - Bidirectional BFS is the best approach when both endpoints are known in
#   advance — it roughly squares the pruning by meeting in the middle.
# - Related/variant problems to try next: Word Ladder, Word Ladder II, Open
#   the Lock.


if __name__ == "__main__":
    tests = [
        (("AACCGGTT", "AACCGGTA", ["AACCGGTA"]), 1),
        (("AACCGGTT", "AAACGGTA", ["AACCGGTA", "AACCGCTA", "AAACGGTA"]), 2),
        (("AACCGGTT", "AAACGGTA", ["AACCGGTA", "AACCGCTA", "AACCGCTT", "AAACGGTA"]), 2),
        (("AACCGGTT", "AACCGGTT", []), 0),
        (("AACCGGTT", "AACCGGTA", []), -1),
    ]

    approaches = [solve_brute_force, solve_optimal, solve_best]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:70s} -> {result!r}  [{status}]")
