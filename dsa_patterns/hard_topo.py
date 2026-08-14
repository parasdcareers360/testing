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
