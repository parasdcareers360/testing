"""
Heaps & Priority Queues — reusable Python skeletons.

Not solutions to specific problems — these are the boilerplate shapes to recognize and adapt
quickly under interview time pressure. Copy the relevant shape into solutions/ and adapt it.
"""

import heapq
from collections import Counter
from typing import List, Tuple


# ---------------------------------------------------------------------------
# Shape 1: max-heap via negation
# ---------------------------------------------------------------------------
class MaxHeap:
    """Wraps heapq to behave like a max-heap by negating values on the way in/out."""

    def __init__(self):
        self._data: List[int] = []

    def push(self, val: int) -> None:
        heapq.heappush(self._data, -val)

    def pop(self) -> int:
        return -heapq.heappop(self._data)

    def peek(self) -> int:
        return -self._data[0]

    def __len__(self) -> int:
        return len(self._data)


# ---------------------------------------------------------------------------
# Shape 2: top-K pattern (bounded min-heap)
# ---------------------------------------------------------------------------
def top_k_frequent_template(nums: List[int], k: int) -> List[int]:
    counts = Counter(nums)
    heap: List[Tuple[int, int]] = []
    for val, freq in counts.items():
        heapq.heappush(heap, (freq, val))
        if len(heap) > k:
            heapq.heappop(heap)
    return [val for freq, val in heap]


def k_largest_template(nums: List[int], k: int) -> List[int]:
    heap: List[int] = []
    for x in nums:
        heapq.heappush(heap, x)
        if len(heap) > k:
            heapq.heappop(heap)
    return sorted(heap, reverse=True)


# ---------------------------------------------------------------------------
# Shape 3: merge K sorted lists
# ---------------------------------------------------------------------------
def merge_k_sorted_template(lists: List[List[int]]) -> List[int]:
    heap: List[Tuple[int, int, int]] = []
    for i, lst in enumerate(lists):
        if lst:
            heapq.heappush(heap, (lst[0], i, 0))

    result: List[int] = []
    while heap:
        val, i, j = heapq.heappop(heap)
        result.append(val)
        if j + 1 < len(lists[i]):
            heapq.heappush(heap, (lists[i][j + 1], i, j + 1))
    return result


# ---------------------------------------------------------------------------
# Shape 4: two-heap running median
# ---------------------------------------------------------------------------
class MedianFinderTemplate:
    def __init__(self):
        self.small: List[int] = []  # max-heap (negated) — lower half
        self.large: List[int] = []  # min-heap — upper half

    def add_num(self, num: int) -> None:
        heapq.heappush(self.small, -num)
        heapq.heappush(self.large, -heapq.heappop(self.small))
        if len(self.large) > len(self.small):
            heapq.heappush(self.small, -heapq.heappop(self.large))

    def find_median(self) -> float:
        if len(self.small) > len(self.large):
            return -self.small[0]
        return (-self.small[0] + self.large[0]) / 2


if __name__ == "__main__":
    mh = MaxHeap()
    for x in [5, 1, 3, 9, 2]:
        mh.push(x)
    assert mh.pop() == 9
    assert mh.peek() == 5
    assert len(mh) == 4

    assert sorted(top_k_frequent_template([1, 1, 1, 2, 2, 3], 2)) == [1, 2]
    assert k_largest_template([3, 1, 5, 12, 2, 11], 3) == [12, 11, 5]

    merged = merge_k_sorted_template([[1, 4, 5], [1, 3, 4], [2, 6]])
    assert merged == sorted(merged)
    assert merged == [1, 1, 2, 3, 4, 4, 5, 6]

    mf = MedianFinderTemplate()
    for num, expected in [(5, 5), (15, 10.0), (1, 5), (3, 4.0)]:
        mf.add_num(num)
        assert mf.find_median() == expected, (num, mf.find_median(), expected)

    print("All template shapes verified.")
