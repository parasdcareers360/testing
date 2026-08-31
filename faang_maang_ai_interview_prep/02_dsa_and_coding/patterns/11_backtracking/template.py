"""
Backtracking — reusable Python skeletons.

Not solutions to specific problems — these are the boilerplate shapes to recognize and adapt
quickly under interview time pressure. Copy the relevant shape into solutions/ and adapt it.
"""

from typing import List, Set


# ---------------------------------------------------------------------------
# Shape 1: subsets — include/exclude each element (start-index recursion)
# ---------------------------------------------------------------------------
def subsets_template(nums: List[int]) -> List[List[int]]:
    result: List[List[int]] = []

    def backtrack(start: int, path: List[int]) -> None:
        result.append(path[:])  # every node in the tree is a valid subset
        for i in range(start, len(nums)):
            path.append(nums[i])
            backtrack(i + 1, path)
            path.pop()  # un-choose

    backtrack(0, [])
    return result


# ---------------------------------------------------------------------------
# Shape 2: permutations — order matters, track "used" instead of a start index
# ---------------------------------------------------------------------------
def permutations_template(nums: List[int]) -> List[List[int]]:
    result: List[List[int]] = []
    used = [False] * len(nums)

    def backtrack(path: List[int]) -> None:
        if len(path) == len(nums):
            result.append(path[:])
            return
        for i in range(len(nums)):
            if used[i]:
                continue
            used[i] = True
            path.append(nums[i])
            backtrack(path)
            path.pop()
            used[i] = False

    backtrack([])
    return result


# ---------------------------------------------------------------------------
# Shape 3: combinations — choose k of n, fixed output size, with pruning
# ---------------------------------------------------------------------------
def combinations_template(n: int, k: int) -> List[List[int]]:
    result: List[List[int]] = []

    def backtrack(start: int, path: List[int]) -> None:
        if len(path) == k:
            result.append(path[:])
            return
        remaining_needed = k - len(path)
        for i in range(start, n - remaining_needed + 2):
            path.append(i)
            backtrack(i + 1, path)
            path.pop()

    backtrack(1, [])
    return result


# ---------------------------------------------------------------------------
# Shape 4: constraint satisfaction with explicit validity check (N-Queens shape)
# ---------------------------------------------------------------------------
def solve_n_queens_template(n: int) -> List[List[str]]:
    result: List[List[str]] = []
    cols: Set[int] = set()
    diagonals: Set[int] = set()
    anti_diagonals: Set[int] = set()
    placement = [-1] * n

    def backtrack(row: int) -> None:
        if row == n:
            board = []
            for r in range(n):
                line = "".join("Q" if c == placement[r] else "." for c in range(n))
                board.append(line)
            result.append(board)
            return
        for col in range(n):
            if col in cols or (row - col) in diagonals or (row + col) in anti_diagonals:
                continue  # prune before recursing, not after
            cols.add(col)
            diagonals.add(row - col)
            anti_diagonals.add(row + col)
            placement[row] = col
            backtrack(row + 1)
            cols.remove(col)
            diagonals.remove(row - col)
            anti_diagonals.remove(row + col)

    backtrack(0)
    return result


# ---------------------------------------------------------------------------
# Shape 5: subsets with duplicate elements — sort first, skip same-value siblings
# ---------------------------------------------------------------------------
def subsets_with_dup_template(nums: List[int]) -> List[List[int]]:
    nums = sorted(nums)
    result: List[List[int]] = []

    def backtrack(start: int, path: List[int]) -> None:
        result.append(path[:])
        for i in range(start, len(nums)):
            if i > start and nums[i] == nums[i - 1]:
                continue  # skip duplicate siblings at this recursion depth
            path.append(nums[i])
            backtrack(i + 1, path)
            path.pop()

    backtrack(0, [])
    return result


if __name__ == "__main__":
    # Shape 1: subsets of [1, 2, 3] -> 2^3 = 8 subsets
    subs = subsets_template([1, 2, 3])
    assert len(subs) == 8
    assert sorted(sorted(s) for s in subs) == sorted(
        sorted(s)
        for s in [[], [1], [2], [3], [1, 2], [1, 3], [2, 3], [1, 2, 3]]
    )

    # Shape 2: permutations of [1, 2, 3] -> 3! = 6 permutations
    perms = permutations_template([1, 2, 3])
    assert len(perms) == 6
    assert sorted(perms) == sorted(
        [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]
    )

    # Shape 3: choose 2 of 4 -> C(4, 2) = 6 combinations
    combos = combinations_template(4, 2)
    assert len(combos) == 6
    assert sorted(combos) == sorted(
        [[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]
    )

    # Shape 4: N-Queens for n=4 has exactly 2 solutions
    queens = solve_n_queens_template(4)
    assert len(queens) == 2

    # Shape 5: subsets with duplicates -> no duplicate subsets in the output
    dup_subs = subsets_with_dup_template([1, 2, 2])
    assert sorted(sorted(s) for s in dup_subs) == sorted(
        sorted(s) for s in [[], [1], [2], [1, 2], [2, 2], [1, 2, 2]]
    )
    assert len(dup_subs) == 6

    print("All template shapes verified.")
