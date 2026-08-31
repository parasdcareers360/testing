"""
PREFIX SUM PATTERN — TUTORIAL
==============================

WHAT IS IT?
-----------
A prefix sum (a.k.a. cumulative sum) array stores running totals:

    prefix[i] = arr[0] + arr[1] + ... + arr[i-1]

Once built, the sum of ANY subarray arr[l..r] (inclusive) can be answered
in O(1) time instead of O(n):

    sum(l, r) = prefix[r + 1] - prefix[l]

WHY IT'S THE "BEST APPROACH" FOR A WHOLE CLASS OF PROBLEMS
------------------------------------------------------------
Brute force for range-sum-style problems recomputes the sum every time by
walking the subarray again -> O(n) per query, O(n * q) overall for q queries.

Prefix sum trades a one-time O(n) preprocessing cost for O(1) answers per
query. This is the single biggest lever in array problems, so it's usually
the FIRST thing to consider whenever you see:

  - "sum of subarray from i to j" asked multiple times
  - "count subarrays whose sum equals k"
  - "find an index that splits the array into two equal-sum halves"
  - "difference/imbalance between left side and right side of an index"
  - 2D grid versions: "sum of a submatrix" (2D prefix sum)

RECOGNIZING THE PATTERN (checklist)
------------------------------------
Ask yourself:
  1. Does the problem repeatedly ask about a SUM (or count/average) over a
     CONTIGUOUS range?
  2. Would recomputing that sum from scratch each time be wasteful?
  3. Is the array static (not changing) during the queries?
        -> If mutable + frequent updates, look at Fenwick Tree / Segment
           Tree instead (prefix sum doesn't handle updates efficiently).

If 1-3 hold, prefix sum is almost always the right call.

THE CORE RECIPE (memorize this shape)
---------------------------------------
    prefix = [0] * (n + 1)          # prefix[0] = 0 sentinel avoids edge cases
    for i in range(n):
        prefix[i + 1] = prefix[i] + arr[i]

    # sum of arr[l..r] inclusive:
    range_sum = prefix[r + 1] - prefix[l]

Using a size-(n+1) array with prefix[0] = 0 is the key trick: it means
"sum of the first 0 elements" is defined, so range_sum(0, r) doesn't need
a special case.

COMPLEXITY
----------
  Build prefix array:      O(n) time, O(n) space
  Each range-sum query:    O(1) time

Below: the core building block, followed by the pattern applied to four
classic interview problems that all reduce to "prefix sum + a small twist".
"""


def prefix_sum(arr):
    """
    Build a prefix sum array with a leading 0 sentinel.

    prefix[i] = sum of arr[0..i-1]  (prefix[0] == 0)

    This is the shape to reach for by default: it makes range queries
    branch-free (see range_sum below).
    """
    n = len(arr)
    prefix = [0] * (n + 1)
    for i in range(n):
        prefix[i + 1] = prefix[i] + arr[i]
    return prefix


def range_sum(prefix, l, r):
    """O(1) sum of the original array's elements from index l to r inclusive."""
    return prefix[r + 1] - prefix[l]


# ---------------------------------------------------------------------------
# PATTERN APPLICATIONS
# ---------------------------------------------------------------------------

def subarray_sum_equals_k(arr, k):
    """
    LeetCode 560: Count the number of contiguous subarrays that sum to k.

    Twist on the base pattern: instead of storing the whole prefix array,
    we stream the running sum and use a hashmap to remember how many times
    each prefix sum value has occurred so far.

    Why it works:
        If running_sum - k has been seen `c` times before the current
        index, that means there are `c` earlier positions where the
        subarray between them and here sums to exactly k.

    Time: O(n)   Space: O(n)
    """
    count = 0
    running_sum = 0
    seen = {0: 1}  # empty prefix (sum 0) occurs once, handles subarrays starting at index 0

    for num in arr:
        running_sum += num
        count += seen.get(running_sum - k, 0)
        seen[running_sum] = seen.get(running_sum, 0) + 1

    return count


def find_pivot_index(arr):
    """
    LeetCode 724: Find the "equilibrium index" — an index where the sum of
    everything to the left equals the sum of everything to the right.

    Twist: we don't even need the full prefix array. Compute the total
    sum once, then walk left-to-right tracking left_sum; right_sum is
    derived as total - left_sum - arr[i].

    Time: O(n)   Space: O(1)
    """
    total = sum(arr)
    left_sum = 0
    for i, num in enumerate(arr):
        right_sum = total - left_sum - num
        if left_sum == right_sum:
            return i
        left_sum += num
    return -1


def max_subarray_len_equals_k(arr, k):
    """
    LeetCode 325: Length of the LONGEST subarray summing to exactly k.

    Twist: same "seen sums" idea as subarray_sum_equals_k, but we store the
    *earliest index* at which each prefix sum occurred (first occurrence
    maximizes the resulting subarray length).

    Time: O(n)   Space: O(n)
    """
    first_seen = {0: -1}  # prefix sum 0 occurs "before" index 0
    running_sum = 0
    best_len = 0

    for i, num in enumerate(arr):
        running_sum += num
        if running_sum - k in first_seen:
            best_len = max(best_len, i - first_seen[running_sum - k])
        if running_sum not in first_seen:
            first_seen[running_sum] = i

    return best_len


def matrix_block_sum(matrix, r1, c1, r2, c2):
    """
    2D prefix sum: sum of the submatrix with top-left (r1, c1) and
    bottom-right (r2, c2), both inclusive.

    Same idea as 1D, extended with inclusion-exclusion over both axes:

        prefix[i][j] = sum of all cells (0..i-1, 0..j-1)

        block_sum = prefix[r2+1][c2+1]
                  - prefix[r1][c2+1]      # remove rows above
                  - prefix[r2+1][c1]      # remove columns to the left
                  + prefix[r1][c1]        # add back double-removed corner

    Build time: O(rows * cols)   Each query: O(1)
    """
    rows, cols = len(matrix), len(matrix[0])
    prefix = [[0] * (cols + 1) for _ in range(rows + 1)]

    for i in range(rows):
        for j in range(cols):
            prefix[i + 1][j + 1] = (
                matrix[i][j]
                + prefix[i][j + 1]
                + prefix[i + 1][j]
                - prefix[i][j]
            )

    return (
        prefix[r2 + 1][c2 + 1]
        - prefix[r1][c2 + 1]
        - prefix[r2 + 1][c1]
        + prefix[r1][c1]
    )


# ---------------------------------------------------------------------------
# DEMO
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    arr = [1, 2, 3, 4, 5]
    prefix = prefix_sum(arr)
    print(f"Original array : {arr}")
    print(f"Prefix sum     : {prefix}")
    print(f"sum(1, 3)      : {range_sum(prefix, 1, 3)}  (expect 2+3+4=9)")

    print()
    nums = [1, 1, 1]
    print(f"subarray_sum_equals_k({nums}, k=2) -> {subarray_sum_equals_k(nums, 2)}  (expect 2)")

    print()
    balanced = [1, 7, 3, 6, 5, 6]
    print(f"find_pivot_index({balanced}) -> {find_pivot_index(balanced)}  (expect 3)")

    print()
    longest = [1, -1, 5, -2, 3]
    print(f"max_subarray_len_equals_k({longest}, k=3) -> {max_subarray_len_equals_k(longest, 3)}  (expect 4)")

    print()
    grid = [
        [3, 0, 1, 4, 2],
        [5, 6, 3, 2, 1],
        [1, 2, 0, 1, 5],
        [4, 1, 0, 1, 7],
        [1, 0, 3, 0, 5],
    ]
    print(f"matrix_block_sum(grid, 2,1,4,3) -> {matrix_block_sum(grid, 2, 1, 4, 3)}  (expect 8)")
