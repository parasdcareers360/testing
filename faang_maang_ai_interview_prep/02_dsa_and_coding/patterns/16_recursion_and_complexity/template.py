"""
Recursion & Complexity — reusable Python skeletons.

Not solutions to specific problems — these are the boilerplate shapes to recognize and adapt
quickly under interview time pressure. Copy the relevant shape into solutions/ and adapt it.
"""

import sys
from functools import lru_cache
from typing import List, Union


# ---------------------------------------------------------------------------
# Shape 1: basic recursion -- base case + recursive case (linear recursion)
# ---------------------------------------------------------------------------
def factorial_recursive(n: int) -> int:
    if n <= 1:              # base case
        return 1
    return n * factorial_recursive(n - 1)   # recursive case


def factorial_iterative(n: int) -> int:
    """Same result, no call stack growth -- the conversion described in concept.md."""
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


# ---------------------------------------------------------------------------
# Shape 2: three ways to compute fibonacci -- naive O(2^n), memoized O(n), iterative O(n)/O(1)
# ---------------------------------------------------------------------------
def fib_naive(n: int) -> int:
    if n <= 1:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)


@lru_cache(maxsize=None)
def fib_memoized(n: int) -> int:
    if n <= 1:
        return n
    return fib_memoized(n - 1) + fib_memoized(n - 2)


def fib_iterative(n: int) -> int:
    if n <= 1:
        return n
    prev2, prev1 = 0, 1
    for _ in range(2, n + 1):
        prev2, prev1 = prev1, prev2 + prev1
    return prev1


# ---------------------------------------------------------------------------
# Shape 3: recursive binary search -- T(n) = T(n/2) + O(1) -> O(log n)
# ---------------------------------------------------------------------------
def binary_search_recursive(nums: List[int], target: int, lo: int = 0, hi: int = None) -> int:
    if hi is None:
        hi = len(nums) - 1
    if lo > hi:              # base case: search space exhausted
        return -1
    mid = (lo + hi) // 2
    if nums[mid] == target:
        return mid
    if nums[mid] < target:
        return binary_search_recursive(nums, target, mid + 1, hi)
    return binary_search_recursive(nums, target, lo, mid - 1)


# ---------------------------------------------------------------------------
# Shape 4: recursion -> explicit-stack iteration (for arbitrarily deep nested structures)
# ---------------------------------------------------------------------------
NestedList = List[Union[int, "NestedList"]]


def sum_nested_list_recursive(items: NestedList) -> int:
    total = 0
    for item in items:
        if isinstance(item, list):
            total += sum_nested_list_recursive(item)
        else:
            total += item
    return total


def sum_nested_list_iterative(items: NestedList) -> int:
    """Same result as the recursive version, but using an explicit stack instead of the
    Python call stack -- avoids RecursionError on very deeply nested input."""
    total = 0
    stack: list = list(items)
    while stack:
        item = stack.pop()
        if isinstance(item, list):
            stack.extend(item)
        else:
            total += item
    return total


# ---------------------------------------------------------------------------
# Shape 5: amortized analysis -- dynamic array doubling (Python list.append's O(1) amortized)
# ---------------------------------------------------------------------------
class DynamicArray:
    def __init__(self) -> None:
        self._capacity = 1
        self._size = 0
        self._data = [None] * self._capacity

    def __len__(self) -> int:
        return self._size

    def __getitem__(self, i: int):
        if not 0 <= i < self._size:
            raise IndexError(i)
        return self._data[i]

    def append(self, value) -> None:
        if self._size == self._capacity:
            self._capacity *= 2
            new_data = [None] * self._capacity
            for i in range(self._size):
                new_data[i] = self._data[i]
            self._data = new_data
        self._data[self._size] = value
        self._size += 1


if __name__ == "__main__":
    # Shape 1
    assert factorial_recursive(5) == 120
    assert factorial_recursive(0) == 1
    assert factorial_iterative(5) == 120
    assert factorial_recursive(10) == factorial_iterative(10)

    # Shape 2: all three agree
    for n in range(15):
        assert fib_naive(n) == fib_memoized(n) == fib_iterative(n)
    assert fib_iterative(30) == 832040

    # Shape 3
    nums = [1, 3, 5, 7, 9, 11, 13]
    assert binary_search_recursive(nums, 7) == 3
    assert binary_search_recursive(nums, 1) == 0
    assert binary_search_recursive(nums, 13) == 6
    assert binary_search_recursive(nums, 4) == -1

    # Shape 4: recursive and iterative agree on a normal case
    nested = [1, [2, 3, [4, 5]], 6, [[7]]]
    assert sum_nested_list_recursive(nested) == 28
    assert sum_nested_list_iterative(nested) == 28

    # Shape 4 continued: iterative survives a depth that breaks recursion
    deep = 1
    for _ in range(3000):
        deep = [deep]
    old_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(1000)
    try:
        raised = False
        try:
            sum_nested_list_recursive(deep)
        except RecursionError:
            raised = True
        assert raised, "expected RecursionError on deeply nested recursive call"
        assert sum_nested_list_iterative(deep) == 1
    finally:
        sys.setrecursionlimit(old_limit)

    # Shape 5
    arr = DynamicArray()
    for i in range(20):
        arr.append(i)
    assert len(arr) == 20
    assert [arr[i] for i in range(20)] == list(range(20))

    print("All template shapes verified.")
