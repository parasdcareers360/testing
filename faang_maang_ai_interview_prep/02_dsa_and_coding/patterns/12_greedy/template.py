"""
Greedy — reusable Python skeletons.

Not solutions to specific problems — these are the boilerplate shapes to recognize and adapt
quickly under interview time pressure. Copy the relevant shape into solutions/ and adapt it.
"""

import heapq
from typing import List, Tuple


# ---------------------------------------------------------------------------
# Shape 1: interval scheduling — sort by END time, greedily pick non-overlapping
# ---------------------------------------------------------------------------
def max_non_overlapping_intervals(intervals: List[Tuple[int, int]]) -> int:
    intervals = sorted(intervals, key=lambda pair: pair[1])
    count = 0
    last_end = float("-inf")
    for start, end in intervals:
        if start >= last_end:
            count += 1
            last_end = end
    return count


# ---------------------------------------------------------------------------
# Shape 2: peak concurrency (Meeting Rooms II) — sort by START time, reuse via heap
# ---------------------------------------------------------------------------
def min_meeting_rooms(intervals: List[Tuple[int, int]]) -> int:
    intervals = sorted(intervals, key=lambda pair: pair[0])
    room_end_times: List[int] = []
    for start, end in intervals:
        if room_end_times and room_end_times[0] <= start:
            heapq.heapreplace(room_end_times, end)
        else:
            heapq.heappush(room_end_times, end)
    return len(room_end_times)


# ---------------------------------------------------------------------------
# Shape 3a: Jump Game — track farthest reachable index, one pass
# ---------------------------------------------------------------------------
def can_jump(nums: List[int]) -> bool:
    farthest = 0
    for i, x in enumerate(nums):
        if i > farthest:
            return False
        farthest = max(farthest, i + x)
    return True


# ---------------------------------------------------------------------------
# Shape 3b: Jump Game II — minimum jumps to reach the end
# ---------------------------------------------------------------------------
def jump_game_min_jumps(nums: List[int]) -> int:
    jumps = 0
    current_end = 0
    farthest = 0
    for i in range(len(nums) - 1):
        farthest = max(farthest, i + nums[i])
        if i == current_end:
            jumps += 1
            current_end = farthest
    return jumps


# ---------------------------------------------------------------------------
# Shape 4: running-total reset (Gas Station shape)
# ---------------------------------------------------------------------------
def can_complete_circuit(gas: List[int], cost: List[int]) -> int:
    if sum(gas) < sum(cost):
        return -1
    total = 0
    start = 0
    for i in range(len(gas)):
        total += gas[i] - cost[i]
        if total < 0:
            start = i + 1
            total = 0
    return start


if __name__ == "__main__":
    # Shape 1: classic non-overlapping intervals example
    assert max_non_overlapping_intervals([(1, 2), (2, 3), (3, 4), (1, 3)]) == 3

    # Shape 2: overlapping meetings needing 2 concurrent rooms
    assert min_meeting_rooms([(0, 30), (5, 10), (15, 20)]) == 2
    assert min_meeting_rooms([(7, 10), (2, 4)]) == 1

    # Shape 3a: Jump Game reachability
    assert can_jump([2, 3, 1, 1, 4]) is True
    assert can_jump([3, 2, 1, 0, 4]) is False

    # Shape 3b: Jump Game II minimum jumps
    assert jump_game_min_jumps([2, 3, 1, 1, 4]) == 2

    # Shape 4: Gas Station — a valid circuit exists starting at index 3
    gas = [1, 2, 3, 4, 5]
    cost = [3, 4, 5, 1, 2]
    assert can_complete_circuit(gas, cost) == 3
    # Not enough total fuel anywhere -> no valid start
    assert can_complete_circuit([2, 3, 4], [3, 4, 3]) == -1

    print("All template shapes verified.")
