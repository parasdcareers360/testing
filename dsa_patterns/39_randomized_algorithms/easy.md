# Easy — Linked List Random Node

**Source**: LeetCode #382
**Pattern**: Reservoir Sampling / Randomized Algorithms
**Difficulty**: Easy

## Problem Statement
You are given the head of a singly linked list, and the length of the list is **not known to you in advance** (you should not simply walk the list once to compute its length and then treat this as a solved problem — the point of the exercise is to design an algorithm that works even for a list whose length is unknown or that is being read as a stream).

Design a class `Solution` that:
- Is initialized with the head of a singly-linked list, `Solution(head)`.
- Has a method `getRandom()` that returns the value of a **random node** from the list, such that **every node has an equal probability of being chosen**, no matter how many times `getRandom()` is called.

You must not load all node values into an array and then just call `random.choice` on that array as your final answer (that trivializes the "unknown length / streaming" constraint the pattern exists to solve) — instead use **reservoir sampling** so the algorithm only ever needs a single pass over the list per call and O(1) extra memory (excluding the list itself).

## Constraints
- The number of nodes in the linked list is in the range `[1, 10^4]`.
- `-10^4 <= Node.val <= 10^4`.
- At most `10^4` calls will be made to `getRandom`.
- You must implement `getRandom` using O(1) extra space per call (not counting the input list), and it must not assume the list length is known ahead of time.

## Examples
**Example 1**
Input: list = `[1, 2, 3]`, then call `getRandom()` several times.
Output: Each call returns `1`, `2`, or `3`, each with probability `1/3`.
Explanation: Over many calls, the empirical distribution of returned values converges to a uniform distribution over the 3 nodes.

**Example 2**
Input: list = `[7]`, then call `getRandom()`.
Output: `7`.
Explanation: With only one node, it is always returned — probability 1.

## Intuition — Why This Pattern
**Naive approach**: Walk the entire list once to collect all values into a Python list/array, then on every `getRandom()` call do `random.choice(array)`. This is correct and simple, but it requires O(n) extra memory to store a duplicate copy of every value, and — more importantly for the pattern this problem teaches — it assumes you *can* materialize the whole sequence at once. If the "list" were instead an unbounded stream you're reading element by element (which is the real-world scenario this problem is modeling), you cannot store the whole thing or even know in advance how long it is.

**The insight (reservoir sampling)**: We want to pick 1 item uniformly at random from a stream of unknown length, seeing each element exactly once, using O(1) memory. The trick: keep a "reservoir" of 1 item (the current answer). When you encounter the i-th element (1-indexed) of the stream, replace the reservoir with that element with probability `1/i`. Otherwise keep the reservoir unchanged.

**Why this gives a uniform distribution**: By induction, after processing i elements, each of the i elements seen so far is equally likely (probability `1/i`) to be the one sitting in the reservoir. When the (i+1)-th element arrives, it becomes the reservoir with probability `1/(i+1)`. Every element that was already in with probability `1/i` survives being overwritten with probability `1 - 1/(i+1) = i/(i+1)`, so its new probability is `(1/i) * (i/(i+1)) = 1/(i+1)`. So all i+1 elements end up with equal probability `1/(i+1)`. This is exactly what we want, and it uses O(1) extra memory and one pass, regardless of how long the stream/list turns out to be.

## Approach
1. In the constructor, just store the `head` pointer (do not copy values into an array).
2. In `getRandom()`:
   a. Initialize `result = head.val` and `count = 1` (this represents seeing the 1st node).
   b. Initialize a pointer `node = head.next`.
   c. While `node` is not `None`:
      - Increment `count` (this is the index, 1-indexed, of the current node in the stream).
      - Generate a random integer `j` uniformly from `[0, count - 1]` (i.e., `count` possible values, 0-indexed).
      - If `j == 0` (this happens with probability `1/count`), set `result = node.val` (replace the reservoir).
      - Advance `node = node.next`.
   d. Return `result`.
3. Each call to `getRandom()` independently re-walks the list and independently re-runs this random-replacement process, so calls are statistically independent of each other.

## Dry Run
List: `1 -> 2 -> 3` (nodes with values 1, 2, 3). Trace one call to `getRandom()`, assuming (for illustration) the random draws happen to come out as: at count=2, `j=0`; at count=3, `j=1`.

| Step | node.val | count | random j drawn from [0, count-1] | j==0? | result after this step |
|------|----------|-------|-----------------------------------|-------|-------------------------|
| init | (head=1) | 1     | —                                 | —     | result = 1 (seed with head) |
| 1    | 2        | 2     | j = 0 (drawn from {0,1})          | yes   | result = 2 |
| 2    | 3        | 3     | j = 1 (drawn from {0,1,2})        | no    | result stays 2 |

Final returned value for this particular run: `2`.

If you imagine running this whole process thousands of times with fresh random draws each time, roughly 1/3 of the runs end with `result = 1`, 1/3 end with `result = 2`, and 1/3 end with `result = 3` — that is the uniform guarantee reservoir sampling provides.

## Solution (Python 3)
```python
import random


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class Solution:
    def __init__(self, head: ListNode):
        self.head = head

    def getRandom(self) -> int:
        result = self.head.val
        count = 1
        node = self.head.next
        while node is not None:
            count += 1
            # With probability 1/count, replace the current answer.
            j = random.randint(0, count - 1)
            if j == 0:
                result = node.val
            node = node.next
        return result


def build_linked_list(values):
    head = None
    tail = None
    for v in values:
        n = ListNode(v)
        if head is None:
            head = n
            tail = n
        else:
            tail.next = n
            tail = n
    return head


if __name__ == "__main__":
    head = build_linked_list([1, 2, 3])
    sol = Solution(head)

    # Empirically verify the distribution is roughly uniform over {1, 2, 3}.
    counts = {1: 0, 2: 0, 3: 0}
    trials = 30000
    for _ in range(trials):
        counts[sol.getRandom()] += 1

    print("Empirical distribution over", trials, "trials:", counts)
    for v in (1, 2, 3):
        print(f"  P(value={v}) ~= {counts[v] / trials:.3f} (expected ~0.333)")

    # Single-node list sanity check.
    single = Solution(build_linked_list([7]))
    print("Single node list always returns:", single.getRandom())
```

Expected output of the empirical test: each of `counts[1]`, `counts[2]`, `counts[3]` should be roughly `trials / 3 ≈ 10000`, confirming a near-uniform distribution. The single-node list always prints `7`.

## Complexity Analysis
- Time: O(n) per call to `getRandom()`, where n is the number of nodes in the list (one full traversal per call, since the list's length is unknown up front and there is no auxiliary index).
- Space: O(1) extra space per call (only `result`, `count`, and a traversal pointer — the list itself is not copied).

## Key Takeaways
- Reservoir sampling of size 1: on seeing the i-th stream element, replace your current pick with probability `1/i`. This generalizes to reservoirs of size k (Algorithm R) for "pick k uniform random elements from a stream."
- Common mistake: computing `random.randint(0, i-1) == 0` versus off-by-one errors on whether `count` is 0-indexed or 1-indexed — always double check with a 2-element example that both elements truly get probability 1/2.
- Common mistake: caching the array of values once in the constructor and shuffling/copying it — that defeats the point when the input is a genuine unbounded stream (though it happens to also produce a correct uniform answer for this specific problem, since we do have `head` and can re-walk it — the pattern still asks you to practice the O(1)-memory streaming technique).
- Related/variant problems to try next: **Random Pick Index** (LeetCode #398, reservoir sampling generalized to picking uniformly among matching indices — see the medium.md in this folder) and **Random Pick with Weight** (LeetCode #528, weighted rather than uniform sampling — see hard.md).
