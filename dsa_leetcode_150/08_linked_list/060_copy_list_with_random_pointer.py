"""
LeetCode Top Interview 150 — #60 (LeetCode #138)
Copy List with Random Pointer
Category: Linked List | Difficulty: Medium

Problem
-------
A linked list of length `n` is given such that each node contains an additional random pointer,
which could point to any node in the list, or to `null`.

Construct a *deep copy* of the list. The deep copy should consist of exactly `n` brand new nodes,
where each new node has its value set to the value of its corresponding original node. Both the
`next` and `random` pointer of every new node must point to new nodes in the copied list, such
that the pointers in the copied list represent the same list state as the original — none of the
new nodes may point to any node in the *original* list.

Return the head of the copied linked list.

The list is represented as a list of `n` pairs `[val, random_index]`, where `random_index` is the
index (0-indexed) of the node that node `i`'s random pointer points to, or `null` if it points to
nothing.

Constraints
-----------
- 0 <= n <= 1000
- -10^4 <= Node.val <= 10^4
- Node.random is null or is pointing to some node in the linked list.

Examples
--------
Example 1:
    Input: head = [[7,null],[13,0],[11,4],[10,2],[1,0]]
    Output: [[7,null],[13,0],[11,4],[10,2],[1,0]]

Example 2:
    Input: head = [[1,1],[2,1]]
    Output: [[1,1],[2,1]]

Example 3:
    Input: head = [[3,null],[3,0],[3,null]]
    Output: [[3,null],[3,0],[3,null]]

Intuition
---------
The hard part isn't copying `next` — it's that `random` can point *forward* to a node we haven't
cloned yet, so we can't just clone-and-wire in a single naive pass. The truly naive fix (Approach
1) clones the `next` chain first, then for every `random` pointer does a linear scan of the
*original* list to find that node's position and mirrors it in the new list — correct, but O(n)
work per node for O(n) nodes. The standard fix is a hashmap from original node -> its clone: one
pass creates every clone (so any node can be looked up in O(1) regardless of order), a second pass
uses the map to wire `next` and `random` in O(1) each. That's O(n) time but pays O(n) extra space
for the map. The clever O(1)-extra-space trick: temporarily splice each clone directly after its
original (A -> A' -> B -> B' -> ...), so "the clone of X" is always just `X.next` — no hashmap
needed. A pointer pass then wires `random` using that property, and a final pass un-weaves the two
lists back apart.
"""

from typing import Optional


class Node:
    def __init__(self, x: int, next: "Optional[Node]" = None, random: "Optional[Node]" = None):
        self.val = int(x)
        self.next = next
        self.random = random


def build_random_list(pairs) -> Optional[Node]:
    if not pairs:
        return None
    nodes = [Node(val) for val, _ in pairs]
    for i in range(len(nodes) - 1):
        nodes[i].next = nodes[i + 1]
    for node, (_, ridx) in zip(nodes, pairs):
        node.random = nodes[ridx] if ridx is not None else None
    return nodes[0]


def random_list_to_pairs(head: Optional[Node]):
    nodes = []
    node = head
    while node is not None:
        nodes.append(node)
        node = node.next
    index = {id(n): i for i, n in enumerate(nodes)}
    return [[n.val, index[id(n.random)] if n.random is not None else None] for n in nodes]


def shares_a_node_with(head: Optional[Node], original_ids) -> bool:
    """True if any node reachable from `head` is literally one of the original nodes."""
    node = head
    while node is not None:
        if id(node) in original_ids:
            return True
        node = node.next
    return False


# ============================================================
# Approach 1: Brute Force (clone next, linear-search random)
# ============================================================
# Idea: clone the `next` chain first (positions line up 1:1 with the
# original). For each node's `random` pointer, find *which* original node it
# is by scanning the original list from the front until we hit it by
# identity, then point the clone's `random` at the clone in that same slot.
# Time:  O(n^2) — an O(n) scan for every node's random pointer
# Space: O(n) — the array of original-node references + n clones
def solve_brute_force(head: Optional[Node]) -> Optional[Node]:
    if head is None:
        return None

    orig_nodes = []
    node = head
    while node is not None:
        orig_nodes.append(node)
        node = node.next

    new_nodes = [Node(n.val) for n in orig_nodes]
    for i in range(len(new_nodes) - 1):
        new_nodes[i].next = new_nodes[i + 1]

    for i, n in enumerate(orig_nodes):
        if n.random is not None:
            idx = 0
            while orig_nodes[idx] is not n.random:  # naive linear search
                idx += 1
            new_nodes[i].random = new_nodes[idx]

    return new_nodes[0]


# ============================================================
# Approach 3: Optimal (hashmap: original node -> clone)
# ============================================================
# Idea: first pass creates a clone for every original node and records the
# mapping original -> clone, so "find the clone of any node" becomes an O(1)
# lookup instead of a scan. Second pass wires next/random on each clone using
# the map (mapping[None] would KeyError, so use .get, which returns None).
# Dry run: pairs = [[1,1],[2,1]]  (node0.random -> node1, node1.random -> node1)
#   pass 1: map = {N0:C0, N1:C1}  (clones created, unlinked so far)
#   pass 2: C0.next=map[N1]=C1, C0.random=map[N1]=C1
#            C1.next=map.get(None)=None, C1.random=map[N1]=C1
#   result clone pairs: [[1,1],[2,1]] -- matches original structure exactly
# Time:  O(n) — two linear passes   Space: O(n) — the original->clone map
def solve_optimal(head: Optional[Node]) -> Optional[Node]:
    if head is None:
        return None

    mapping = {}
    node = head
    while node is not None:
        mapping[node] = Node(node.val)
        node = node.next

    node = head
    while node is not None:
        mapping[node].next = mapping.get(node.next)
        mapping[node].random = mapping.get(node.random)
        node = node.next

    return mapping[head]


# ============================================================
# Approach 4: Best / Alternate Optimal (interleaved clones, O(1) space)
# ============================================================
# Idea: instead of a hashmap, make "the clone of X" discoverable for free by
# weaving each clone directly after its original: A -> A' -> B -> B' -> ...
# Now `original.next` IS the clone, so `original.random.next` is the clone of
# `original.random` -- exactly what a clone's `random` should point at. A
# final pass un-weaves the two lists back into separate chains.
# Time:  O(n) — three linear passes   Space: O(1) extra (no map, no array)
def solve_best(head: Optional[Node]) -> Optional[Node]:
    if head is None:
        return None

    # 1. Weave: A -> A' -> B -> B' -> ...
    node = head
    while node is not None:
        clone = Node(node.val)
        clone.next = node.next
        node.next = clone
        node = clone.next

    # 2. Wire random pointers using the weave: clone of X is always X.next.
    node = head
    while node is not None:
        if node.random is not None:
            node.next.random = node.random.next
        node = node.next.next

    # 3. Un-weave: restore the original list, extract the cloned list.
    old = head
    new_head = head.next
    new = new_head
    while old is not None:
        old.next = old.next.next
        new.next = new.next.next if new.next is not None else None
        old = old.next
        new = new.next

    return new_head


# ============================================================
# Key Takeaways
# ============================================================
# - Whenever a structure has pointers that can reference *any* other node
#   (not just neighbors), you need some O(1) way to map "old node" -> "new
#   node" before you can wire those pointers cheaply — a hashmap is the
#   general tool, weaving-into-the-same-structure is the space-optimized one.
# - Common mistake: forgetting that `mapping.get(None)` must return `None`
#   (not KeyError) so nodes whose `next`/`random` is null copy correctly —
#   using `mapping[x]` directly instead of `.get(x)` crashes on those nodes.
# - Related/variant problems to try next: Clone Graph (same hashmap-of-
#   originals-to-clones idea on a graph), Copy List with Random Pointer
#   variants, LRU Cache (another problem built on a hand-rolled node graph).


if __name__ == "__main__":
    tests = [
        ([[7, None], [13, 0], [11, 4], [10, 2], [1, 0]]),
        ([[1, 1], [2, 1]]),
        ([[3, None], [3, 0], [3, None]]),
        ([]),
        ([[1, None]]),
    ]

    approaches = [solve_brute_force, solve_optimal, solve_best]
    for pairs in tests:
        for fn in approaches:
            original = build_random_list(pairs)
            original_ids = set()
            node = original
            while node is not None:
                original_ids.add(id(node))
                node = node.next

            copy = fn(original)
            result_pairs = random_list_to_pairs(copy)
            no_shared_nodes = not shares_a_node_with(copy, original_ids)
            status = "OK" if result_pairs == pairs and no_shared_nodes else "FAIL"
            print(f"{fn.__name__:20s} input={pairs!r:45s} -> {result_pairs!r}  [{status}]")
