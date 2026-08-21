"""
LeetCode Top Interview 150 — #120 (LeetCode #4)
Median of Two Sorted Arrays
Category: Binary Search | Difficulty: Hard

Problem
-------
Given two sorted arrays `nums1` and `nums2` of size `m` and `n` respectively, return the median
of the two sorted arrays (i.e. the median of the combined, still-sorted array of size `m + n`).

The overall run time complexity should be O(log(m+n)).

Constraints
-----------
- nums1.length == m
- nums2.length == n
- 0 <= m <= 1000
- 0 <= n <= 1000
- 1 <= m + n <= 2000
- -10^6 <= nums1[i], nums2[i] <= 10^6
- nums1 and nums2 are each sorted in non-decreasing order.

Examples
--------
Example 1:
    Input: nums1 = [1,3], nums2 = [2]
    Output: 2.00000
    Explanation: merged = [1,2,3], median is 2.

Example 2:
    Input: nums1 = [1,2], nums2 = [3,4]
    Output: 2.50000
    Explanation: merged = [1,2,3,4], median is (2+3)/2 = 2.5.

Intuition
---------
The obvious approach is to merge both sorted arrays into one sorted array of size m+n (a linear
two-pointer merge, exactly like the merge step of merge sort) and then read off the middle
element(s) — correct, and O(m+n), but the problem demands O(log(m+n)), which means we can't
afford to look at every element. The median only needs the combined array split into a "left
half" and "right half" of (near-)equal size where every left value <= every right value — we
never actually need those halves *sorted internally*, just correctly partitioned. So instead of
merging, binary search directly on **how many elements of the smaller array go into the left
half**: for any candidate split `i` of `nums1`, there's exactly one matching split `j` of `nums2`
that makes the two halves the right total size. Check if that split is valid (the largest element
on the left of both arrays is <= the smallest element on the right of both); if not, binary search
adjusts `i` up or down. Binary searching over the smaller array's index range (size min(m,n))
gives O(log(min(m,n))), well within the O(log(m+n)) requirement.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force
# ============================================================
# Idea: two-pointer merge of both sorted arrays into one combined sorted
# list (never re-sort — both inputs are already sorted), then directly
# index the middle element(s).
# Time:  O(m+n) — a single linear merge pass
# Space: O(m+n) — the merged array
def solve_brute_force(nums1: List[int], nums2: List[int]) -> float:
    merged = []
    i = j = 0
    while i < len(nums1) and j < len(nums2):
        if nums1[i] <= nums2[j]:
            merged.append(nums1[i])
            i += 1
        else:
            merged.append(nums2[j])
            j += 1
    merged.extend(nums1[i:])
    merged.extend(nums2[j:])

    total = len(merged)
    mid = total // 2
    if total % 2 == 1:
        return float(merged[mid])
    return (merged[mid - 1] + merged[mid]) / 2.0


# ============================================================
# Approach 2: Optimal (partition via binary search)
# ============================================================
# Idea: always binary search over the SMALLER array (call it A, the other
# B) to keep the search space to O(log(min(m,n))). For a candidate cut `i`
# in A (0..len(A)), the matching cut in B is forced: `j = half - i`, where
# `half = (m+n+1)//2` is how many elements the combined left half must
# hold (the "+1" makes the left half the larger one when m+n is odd, which
# simplifies the odd-length median to just `max(left)`).
#   left of A  = A[i-1] (or -inf if i == 0)
#   right of A = A[i]   (or +inf if i == len(A))
#   left of B  = B[j-1] (or -inf if j == 0)
#   right of B = B[j]   (or +inf if j == len(B))
# The cut is valid when leftA <= rightB and leftB <= rightA (every element
# in the combined left half is <= every element in the combined right
# half). If leftA > rightB, A's cut is too far right -> move it left
# (hi = i-1). If leftB > rightA, A's cut is too far left -> move it right
# (lo = i+1). At a valid cut: odd total -> answer is max(leftA, leftB);
# even total -> answer is average of max(leftA,leftB) and min(rightA,rightB).
# Dry run: nums1=[1,3], nums2=[2]  (A=nums2=[2] since it's smaller, B=[1,3])
#   m=1 n=2, half=(1+2+1)//2=2, lo=0 hi=1
#   i=0 -> j=2: leftA=-inf rightA=2, leftB=B[1]=3 rightB=+inf
#     leftA<=rightB(yes) but leftB=3 > rightA=2 -> invalid, lo=i+1=1
#   i=1 -> j=1: leftA=A[0]=2 rightA=+inf, leftB=B[0]=1 rightB=B[1]=3
#     leftA=2<=rightB=3 and leftB=1<=rightA=+inf -> valid!
#   total=3 (odd) -> answer = max(leftA, leftB) = max(2,1) = 2
# Time:  O(log(min(m,n)))
# Space: O(1)
def solve_optimal(nums1: List[int], nums2: List[int]) -> float:
    # Ensure A is the smaller array so the binary search range is minimal.
    A, B = (nums1, nums2) if len(nums1) <= len(nums2) else (nums2, nums1)
    m, n = len(A), len(B)
    total = m + n
    half = (total + 1) // 2  # size of the combined left half

    lo, hi = 0, m
    while lo <= hi:
        i = (lo + hi) // 2  # elements of A in the left half
        j = half - i        # elements of B in the left half (forced)

        left_a = A[i - 1] if i > 0 else float("-inf")
        right_a = A[i] if i < m else float("inf")
        left_b = B[j - 1] if j > 0 else float("-inf")
        right_b = B[j] if j < n else float("inf")

        if left_a <= right_b and left_b <= right_a:
            if total % 2 == 1:
                return float(max(left_a, left_b))
            return (max(left_a, left_b) + min(right_a, right_b)) / 2.0
        elif left_a > right_b:
            hi = i - 1  # A's cut is too far right, pull it left
        else:
            lo = i + 1  # A's cut is too far left, push it right

    raise ValueError("Input arrays are not sorted (no valid partition found)")


# ============================================================
# Key Takeaways
# ============================================================
# - The core trick generalizes "binary search on the answer's shape"
#   instead of "binary search for a value": here we search over how many
#   elements go left/right, not over element values themselves, using the
#   sentinel -inf/+inf pattern to cleanly handle a cut at either end of an
#   array without special-casing.
# - Common mistake: binary searching over the LARGER array (or either one
#   arbitrarily) instead of always the smaller — that still works
#   correctly but loses the O(log(min(m,n))) guarantee, and can crash if
#   the "always search nums1" array happens to be empty while the other
#   isn't (j = half - i could go out of the valid 0..n range).
# - Related/variant problems to try next: Kth Smallest Element in a Sorted
#   Matrix, Find K-th Smallest Pair Distance, Split Array Largest Sum (all
#   "binary search on the answer" problems).


if __name__ == "__main__":
    tests = [
        (([1, 3], [2]), 2.0),
        (([1, 2], [3, 4]), 2.5),
        (([], [1]), 1.0),
        (([2], []), 2.0),
        (([], [2, 3]), 2.5),
        (([1, 2, 3, 4, 5], []), 3.0),
        (([1, 3, 5, 7, 9], [2, 4, 6, 8, 10]), 5.5),
        (([1, 2], []), 1.5),
        (([1, 1, 1], [1, 1, 1]), 1.0),
        (([-5, -3, -1], [-2, 0, 4]), -1.5),
        (([100000], [-100000]), 0.0),
        (([1], [2, 3, 4, 5, 6]), 3.5),
        (([1, 2, 3], [4, 5, 6, 7, 8, 9]), 5.0),
    ]

    approaches = [solve_brute_force, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if abs(result - expected) < 1e-9 else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:40s} -> {result!r}  [{status}]")
