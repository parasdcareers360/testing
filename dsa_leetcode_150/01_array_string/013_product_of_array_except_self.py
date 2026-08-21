"""
LeetCode Top Interview 150 — #13 (LeetCode #238)
Product of Array Except Self
Category: Array / String | Difficulty: Medium

Problem
-------
Given an integer array `nums`, return an array `answer` such that `answer[i]` is equal to the
product of all the elements of `nums` except `nums[i]`.

You must write an algorithm that runs in O(n) time and does not use the division operator. (The
output array does not count as extra space for space-complexity purposes.)

Constraints
-----------
- 2 <= nums.length <= 10^5
- -30 <= nums[i] <= 30
- The product of any prefix or suffix of nums is guaranteed to fit in a 32-bit integer.

Examples
--------
Example 1:
    Input: nums = [1,2,3,4]
    Output: [24,12,8,6]

Example 2:
    Input: nums = [-1,1,0,-3,3]
    Output: [0,0,9,0,0]

Intuition
---------
The most obvious idea is: compute the total product of the whole array, then answer[i] =
total / nums[i]. It's O(n), but it's disqualified twice over -- the problem forbids division, and
even ignoring that rule, it breaks the moment any element is 0 (division by zero, and worse, if
there are *two or more* zeros, every answer should be 0, but the naive "total/nums[i]" trick can't
even express that safely). We include it as the "brute force" baseline specifically to show why it
fails, with the zero special-casing bolted on. The real fix drops division entirely: answer[i] is
just (product of everything to i's left) * (product of everything to i's right), so precompute a
prefix-products array and a suffix-products array in two linear passes, then multiply them
elementwise -- no division, and zeros are handled automatically since a 0 anywhere in the left or
right range correctly zeroes out that side's product. The final refinement notices the prefix and
suffix arrays are never needed *simultaneously* for the same index: build prefix products directly
into the output array first, then do a second pass from the right, folding the suffix product into
a single running variable instead of a whole second array -- same O(n) time, but O(1) extra space
beyond the required output array.
"""

from typing import List


# ============================================================
# Approach 1: Brute Force (division-based, with zero-handling caveat)
# ============================================================
# Idea: compute the product of all elements, then divide it by nums[i] for
# each position. Violates the problem's "no division" constraint and needs
# explicit special-casing for zeros (division by zero is undefined, and a
# single zero vs. multiple zeros change the correct answer entirely) --
# included only as the naive, division-based baseline.
# Time:  O(n)
# Space: O(1) extra (excluding output)
def solve_brute_force(nums: List[int]) -> List[int]:
    zero_count = nums.count(0)
    if zero_count >= 2:
        return [0] * len(nums)

    if zero_count == 1:
        # Every position is 0 except the one that *is* the zero, whose
        # answer is the product of every other (necessarily nonzero) value.
        product_nonzero = 1
        for x in nums:
            if x != 0:
                product_nonzero *= x
        return [product_nonzero if x == 0 else 0 for x in nums]

    total = 1
    for x in nums:
        total *= x
    return [total // x for x in nums]


# ============================================================
# Approach 2: Better (prefix and suffix product arrays)
# ============================================================
# Idea: build prefix[i] = product of nums[0..i-1], and suffix[i] = product
# of nums[i+1..n-1], each via one linear pass, then answer[i] =
# prefix[i] * suffix[i]. No division; zeros are handled naturally since a
# zero anywhere in a range zeroes that range's product.
# Time:  O(n)
# Space: O(n) — the two auxiliary arrays
def solve_better(nums: List[int]) -> List[int]:
    n = len(nums)
    prefix = [1] * n
    suffix = [1] * n

    for i in range(1, n):
        prefix[i] = prefix[i - 1] * nums[i - 1]
    for i in range(n - 2, -1, -1):
        suffix[i] = suffix[i + 1] * nums[i + 1]

    return [prefix[i] * suffix[i] for i in range(n)]


# ============================================================
# Approach 3: Optimal (O(1) extra space, excluding output array)
# ============================================================
# Idea: reuse the output array itself to hold prefix products first (same
# left-to-right pass as Approach 2, written directly into `answer`). Then
# do a second pass from the right, but instead of a full suffix array,
# fold the running suffix product into a single variable and multiply it
# into `answer[i]` in place as we go.
# Dry run: nums = [1,2,3,4]
#   pass 1 (prefix into answer): answer = [1, 1, 2, 6]
#     (answer[0]=1; answer[1]=1*1=1; answer[2]=1*2=2; answer[3]=2*3=6)
#   pass 2 (fold suffix product `right` from the end, right starts at 1):
#     i=3: answer[3] = 6 * 1 = 6;  right = 1*4 = 4
#     i=2: answer[2] = 2 * 4 = 8;  right = 4*3 = 12
#     i=1: answer[1] = 1 * 12 = 12; right = 12*2 = 24
#     i=0: answer[0] = 1 * 24 = 24; right = 24*1 = 24
#   result: [24, 12, 8, 6]
# Time:  O(n)
# Space: O(1) extra (beyond the required output array)
def solve_optimal(nums: List[int]) -> List[int]:
    n = len(nums)
    answer = [1] * n

    for i in range(1, n):
        answer[i] = answer[i - 1] * nums[i - 1]

    right = 1
    for i in range(n - 1, -1, -1):
        answer[i] *= right
        right *= nums[i]

    return answer


# ============================================================
# Key Takeaways
# ============================================================
# - "Product/sum except self" problems are the classic use case for
#   prefix/suffix decomposition: answer[i] = combine(left-of-i, right-of-i)
#   computed in two linear passes, no need to recompute per index.
# - Common mistake: reaching for division as the "obvious" O(n) solution —
#   it's disallowed here, and even when allowed it silently breaks on
#   zeros unless you special-case them explicitly.
# - Related/variant problems to try next: Trapping Rain Water (also
#   solved via prefix/suffix arrays folded into O(1) space), Maximum
#   Product Subarray, Range Sum Query (prefix sums).


if __name__ == "__main__":
    tests = [
        (([1, 2, 3, 4],), [24, 12, 8, 6]),
        (([-1, 1, 0, -3, 3],), [0, 0, 9, 0, 0]),
        (([0, 0],), [0, 0]),
        (([2, 3],), [3, 2]),
        (([-1, -1, -1, -1],), [-1, -1, -1, -1]),
        (([5, 0, 3, 2],), [0, 30, 0, 0]),
    ]

    approaches = [solve_brute_force, solve_better, solve_optimal]
    for args, expected in tests:
        for fn in approaches:
            result = fn(*args)
            status = "OK" if result == expected else "FAIL"
            print(f"{fn.__name__:20s} args={args!r:40s} -> {result!r}  [{status}]")
