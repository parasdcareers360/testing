"""
Bit Manipulation — reusable Python skeletons.

Not solutions to specific problems — these are the boilerplate shapes to recognize and adapt
quickly under interview time pressure. Copy the relevant shape into solutions/ and adapt it.
"""

from typing import List


# ---------------------------------------------------------------------------
# Shape 1: check / set / clear / toggle a specific bit
# ---------------------------------------------------------------------------
def get_bit(x: int, i: int) -> int:
    return (x >> i) & 1


def set_bit(x: int, i: int) -> int:
    return x | (1 << i)


def clear_bit(x: int, i: int) -> int:
    return x & ~(1 << i)


def toggle_bit(x: int, i: int) -> int:
    return x ^ (1 << i)


# ---------------------------------------------------------------------------
# Shape 2: XOR for "find the unpaired element" family
# ---------------------------------------------------------------------------
def single_number(nums: List[int]) -> int:
    """Every element appears twice except one."""
    result = 0
    for x in nums:
        result ^= x
    return result


# ---------------------------------------------------------------------------
# Shape 3: count set bits -- Brian Kernighan's algorithm
# ---------------------------------------------------------------------------
def count_set_bits(x: int) -> int:
    count = 0
    while x:
        x &= x - 1
        count += 1
    return count


# ---------------------------------------------------------------------------
# Shape 4: power-of-two check
# ---------------------------------------------------------------------------
def is_power_of_two(x: int) -> bool:
    return x > 0 and (x & (x - 1)) == 0


# ---------------------------------------------------------------------------
# Shape 5: subset enumeration via bitmasking
# ---------------------------------------------------------------------------
def all_subsets(nums: List[int]) -> List[List[int]]:
    n = len(nums)
    subsets = []
    for mask in range(1 << n):
        subset = [nums[i] for i in range(n) if mask & (1 << i)]
        subsets.append(subset)
    return subsets


if __name__ == "__main__":
    # Shape 1
    x = 0b1010
    assert get_bit(x, 1) == 1
    assert get_bit(x, 0) == 0
    assert set_bit(x, 0) == 0b1011
    assert clear_bit(x, 1) == 0b1000
    assert toggle_bit(x, 0) == 0b1011
    assert toggle_bit(x, 1) == 0b1000

    # Shape 2
    assert single_number([4, 1, 2, 1, 2]) == 4
    assert single_number([2, 2, 1]) == 1

    # Shape 3
    assert count_set_bits(0) == 0
    assert count_set_bits(12) == 2   # 0b1100
    assert count_set_bits(7) == 3    # 0b0111
    assert count_set_bits(255) == 8  # 0b11111111

    # Shape 4
    assert is_power_of_two(1) is True
    assert is_power_of_two(16) is True
    assert is_power_of_two(0) is False
    assert is_power_of_two(18) is False
    assert is_power_of_two(-4) is False

    # Shape 5
    subsets = all_subsets([1, 2, 3])
    assert len(subsets) == 8
    assert sorted(tuple(sorted(s)) for s in subsets) == sorted(
        tuple(sorted(s))
        for s in [[], [1], [2], [3], [1, 2], [1, 3], [2, 3], [1, 2, 3]]
    )

    print("All template shapes verified.")
