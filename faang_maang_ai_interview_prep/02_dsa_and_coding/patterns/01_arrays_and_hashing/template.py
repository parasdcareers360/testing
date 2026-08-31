"""
Arrays & Hashing — reusable Python skeletons.

Not solutions to specific problems — these are the boilerplate shapes to recognize and adapt
quickly under interview time pressure. Copy the relevant shape into solutions/ and adapt it.
"""

from collections import Counter, defaultdict
from typing import Dict, List, Tuple


# ---------------------------------------------------------------------------
# Shape 1: one-pass complement lookup (two-sum family)
# ---------------------------------------------------------------------------
def complement_lookup_template(nums: List[int], target: int) -> List[int]:
    seen: Dict[int, int] = {}  # value -> index (or count, depending on the problem)
    for i, x in enumerate(nums):
        complement = target - x
        if complement in seen:
            return [seen[complement], i]
        seen[x] = i
    return []


# ---------------------------------------------------------------------------
# Shape 2: frequency map
# ---------------------------------------------------------------------------
def frequency_map_template(items: List[str]) -> Counter:
    return Counter(items)


# ---------------------------------------------------------------------------
# Shape 3: group by canonical key
# ---------------------------------------------------------------------------
def group_by_key_template(items: List[str]) -> List[List[str]]:
    groups: Dict[Tuple[str, ...], List[str]] = defaultdict(list)
    for s in items:
        key = tuple(sorted(s))  # swap for whatever canonical form the problem needs
        groups[key].append(s)
    return list(groups.values())


# ---------------------------------------------------------------------------
# Shape 4: prefix sums
# ---------------------------------------------------------------------------
def build_prefix_sums(nums: List[int]) -> List[int]:
    prefix = [0] * (len(nums) + 1)
    for i, x in enumerate(nums):
        prefix[i + 1] = prefix[i] + x
    return prefix


def range_sum(prefix: List[int], left: int, right: int) -> int:
    """Sum of nums[left:right] (right exclusive) using a prefix array from build_prefix_sums."""
    return prefix[right] - prefix[left]


# ---------------------------------------------------------------------------
# Shape 5: set-based membership / dedup
# ---------------------------------------------------------------------------
def dedup_preserving_order(items: List[int]) -> List[int]:
    seen = set()
    result = []
    for x in items:
        if x not in seen:
            seen.add(x)
            result.append(x)
    return result


if __name__ == "__main__":
    assert complement_lookup_template([2, 7, 11, 15], 9) == [0, 1]
    assert dict(frequency_map_template(["a", "b", "a"])) == {"a": 2, "b": 1}
    groups = group_by_key_template(["eat", "tea", "tan", "ate", "nat", "bat"])
    assert sorted(sorted(g) for g in groups) == sorted(
        sorted(g) for g in [["eat", "tea", "ate"], ["tan", "nat"], ["bat"]]
    )
    prefix = build_prefix_sums([1, 2, 3, 4, 5])
    assert range_sum(prefix, 1, 4) == 2 + 3 + 4
    assert dedup_preserving_order([1, 2, 1, 3, 2, 4]) == [1, 2, 3, 4]
    print("All template shapes verified.")
