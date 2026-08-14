# Hard — Ones and Zeroes

**Source**: LeetCode #474
**Pattern**: Dynamic Programming — Knapsack (0/1, Unbounded, Subset Sum)
**Difficulty**: Hard

## Problem Statement
You are given an array of binary strings `strs` and two integers `m` and `n`.

Return the size of the largest possible subset of `strs` such that there are **at most** `m` `0`'s and `n` `1`'s **in total** across all the strings in that subset.

A set `x` is a subset of a set `y` if all elements of `x` are also elements of `y`. Each string in `strs` can be used at most once.

## Constraints
- `1 <= strs.length <= 600`
- `1 <= strs[i].length <= 100`
- `strs[i]` consists only of digits `'0'` and `'1'`.
- `1 <= m, n <= 100`

## Examples
1. Input: `strs = ["10", "0001", "111001", "1", "0"], m = 5, n = 3` -> Output: `4`
   Explanation: The largest subset using at most 5 zeros and 3 ones is `{"10", "0001", "1", "0"}`. It uses `0+3+1+1 = ...` let's count precisely: "10" has one 0 and one 1; "0001" has three 0s and one 1; "1" has zero 0s and one 1; "0" has one 0 and zero 1s. Total zeros = 1+3+0+1 = 5, total ones = 1+1+1+0 = 3. Both within budget (5 zeros, 3 ones), and this subset has 4 strings — the maximum achievable.
2. Input: `strs = ["10", "0", "1"], m = 1, n = 1` -> Output: `2`
   Explanation: The largest subset is `{"0", "1"}` — using 1 zero and 1 one. Adding "10" would need a second zero and a second one, exceeding the budget.

## Intuition — Why This Pattern
**Brute force**: Try every one of the `2^len(strs)` subsets, sum the zeros and ones used by each, and check the budget constraint `m, n`. With `len(strs)` up to 600, this is astronomically infeasible.

**What's inefficient**: The decision "should I include this string" only affects two running totals — zeros used and ones used — and the *maximum subset size* achievable from a given remaining zero/one budget is a self-contained subproblem that gets recomputed repeatedly across different subset orderings in brute force.

**The twist vs. standard knapsack**: Standard 0/1 knapsack has a single capacity dimension (`dp[w]`). Here, each "item" (string) consumes **two resources simultaneously** — some number of zeros and some number of ones — against **two independent capacity budgets** `m` and `n`. This is a **2D-capacity 0/1 knapsack**: the "weight" of an item is a pair `(zeros(str), ones(str))`, and there's no single scalar capacity — we need a full 2D `dp[i][j]` table representing "budget of `i` zeros and `j` ones remaining/used." This doubles the DP's dimensionality compared to standard subset-sum/partition knapsack, which is the core difficulty escalation for this problem.

**State**: `dp[i][j]` = the maximum number of strings we can select using **at most** `i` zeros and **at most** `j` ones in total.

## Approach
1. Create a 2D array `dp` of size `(m+1) x (n+1)`, all initialized to `0` (using 0 strings costs 0 zeros and 0 ones, achieving count 0 — this doubles as correct base case for every `(i, j)`).
2. For each string `s` in `strs`:
   a. Count `zeros = s.count('0')` and `ones = s.count('1')`.
   b. For `i` from `m` down to `zeros` (backwards — 0/1 knapsack, use each string at most once):
      For `j` from `n` down to `ones` (backwards on the second capacity dimension too):
      `dp[i][j] = max(dp[i][j], dp[i - zeros][j - ones] + 1)`
      (Either skip this string — keep `dp[i][j]` as is — or take it, adding 1 to the best count achievable with `zeros` fewer 0-budget and `ones` fewer 1-budget.)
3. After processing every string, the answer is `dp[m][n]` — the max subset size achievable within the full `m`-zero, `n`-one budget.

Both capacity loops (`i` and `j`) must go backwards within the same string's update, exactly like 1D 0/1 knapsack — otherwise a string could be "reused" within the same pass by contaminating a still-to-be-updated cell with a value that already includes it.

## Dry Run
Example: `strs = ["10", "0001", "111001", "1", "0"]`, `m = 5, n = 3`. Expected output: `4`.

Precompute (zeros, ones) for each string:
- "10" -> (1, 1)
- "0001" -> (3, 1)
- "111001" -> (2, 4) -- note: this string alone needs 4 ones, but `n = 3`, so it can never be selected (any cell with `j < 4` simply never uses it — the backward loop `j` from `3` down to `4` is an empty range, so this string contributes nothing to the table).
- "1" -> (0, 1)
- "0" -> (1, 0)

Initialize `dp` as a `6 x 4` grid of all zeros (rows i=0..5 zeros-budget, columns j=0..3 ones-budget).

**Process "10" (zeros=1, ones=1)**: for i from 5 down to 1, j from 3 down to 1: `dp[i][j] = max(dp[i][j], dp[i-1][j-1]+1)`. Since everything is currently 0, this sets `dp[i][j] = 1` for every `i>=1, j>=1`.

```
dp after "10":
      j=0 j=1 j=2 j=3
i=0:   0   0   0   0
i=1:   0   1   1   1
i=2:   0   1   1   1
i=3:   0   1   1   1
i=4:   0   1   1   1
i=5:   0   1   1   1
```

**Process "0001" (zeros=3, ones=1)**: for i from 5 down to 3, j from 3 down to 1: `dp[i][j] = max(dp[i][j], dp[i-3][j-1]+1)`.
- i=5,j=3: max(dp[5][3]=1, dp[2][2]+1=1+1=2) -> 2
- i=5,j=2: max(1, dp[2][1]+1=1+1=2) -> 2
- i=5,j=1: max(1, dp[2][0]+1=0+1=1) -> 1
- i=4,j=3: max(1, dp[1][2]+1=1+1=2) -> 2
- i=4,j=2: max(1, dp[1][1]+1=1+1=2) -> 2
- i=4,j=1: max(1, dp[1][0]+1=0+1=1) -> 1
- i=3,j=3: max(1, dp[0][2]+1=0+1=1) -> 1
- i=3,j=2: max(1, dp[0][1]+1=0+1=1) -> 1
- i=3,j=1: max(1, dp[0][0]+1=0+1=1) -> 1

```
dp after "0001":
      j=0 j=1 j=2 j=3
i=0:   0   0   0   0
i=1:   0   1   1   1
i=2:   0   1   1   1
i=3:   0   1   1   1
i=4:   0   1   2   2
i=5:   0   1   2   2
```

**Process "111001" (zeros=2, ones=4)**: `n=3 < 4`, so the inner loop `j` from `3` down to `4` is empty for every `i` — no updates happen. `dp` unchanged.

**Process "1" (zeros=0, ones=1)**: for i from 5 down to 0, j from 3 down to 1: `dp[i][j] = max(dp[i][j], dp[i][j-1]+1)`.
- i=5,j=3: max(2, dp[5][2]+1=2+1=3) -> 3
- i=5,j=2: max(2, dp[5][1]+1=1+1=2) -> 2
- i=5,j=1: max(1, dp[5][0]+1=0+1=1) -> 1
- i=4,j=3: max(2, dp[4][2]+1=2+1=3) -> 3
- i=4,j=2: max(2, dp[4][1]+1=1+1=2) -> 2
- i=4,j=1: max(1, dp[4][0]+1=1) -> 1
- i=3,j=3: max(1, dp[3][2]+1=1+1=2) -> 2
- i=3,j=2: max(1, dp[3][1]+1=1+1=2) -> 2
- i=3,j=1: max(1, dp[3][0]+1=1) -> 1
- (i=2,1,0 similarly become 1 at j=1)

```
dp after "1":
      j=0 j=1 j=2 j=3
i=0:   0   1   1   1
i=1:   0   1   1   1
i=2:   0   1   1   1
i=3:   0   1   2   2
i=4:   0   1   2   3
i=5:   0   1   2   3
```

**Process "0" (zeros=1, ones=0)**: for i from 5 down to 1, j from 3 down to 0: `dp[i][j] = max(dp[i][j], dp[i-1][j]+1)`.
- i=5,j=3: max(3, dp[4][3]+1=3+1=4) -> **4**
- i=5,j=2: max(2, dp[4][2]+1=2+1=3) -> 3
- (other cells update similarly but j=3,i=5 is what we need)

Final: `dp[5][3] = 4`, matching the expected output. This corresponds to using "0" (1 zero) plus the best 3-zero/3-one combo found after "1" was processed (`dp[4][3] = 3`, from `{"10","0001","1"}` using 1+3+0=4 zeros... let's just trust the table — it correctly reflects `{"10", "0001", "1", "0"}` as stated in the problem's own explanation).

## Solution (Python 3)
```python
def find_max_form(strs: list[str], m: int, n: int) -> int:
    # dp[i][j] = max number of strings selectable using at most i zeros and j ones
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for s in strs:
        zeros = s.count('0')
        ones = s.count('1')
        if zeros > m or ones > n:
            continue  # this string can never fit under the budget; skip entirely

        for i in range(m, zeros - 1, -1):
            for j in range(n, ones - 1, -1):
                dp[i][j] = max(dp[i][j], dp[i - zeros][j - ones] + 1)

    return dp[m][n]


if __name__ == "__main__":
    print(find_max_form(["10", "0001", "111001", "1", "0"], 5, 3))  # Expected: 4
    print(find_max_form(["10", "0", "1"], 1, 1))                     # Expected: 2
```

## Complexity Analysis
- Time: O(L * m * n), where `L = len(strs)` — for each string, update an `m x n` grid.
- Space: O(m * n) for the 2D DP table.

## Key Takeaways
- This problem generalizes 0/1 knapsack from **one** capacity dimension to **two independent capacity dimensions** — the DP table itself becomes 2D per item (`dp[i][j]`), and both dimensions must be iterated backwards within a single item's update to preserve the 0/1 (use-at-most-once) property.
- Common mistake: iterating only one of the two capacity loops backwards (e.g., forgetting that `j` also needs to go from high to low), which allows partial double-counting of a string's contribution.
- Skipping strings whose individual zero or one count already exceeds the respective budget (`zeros > m or ones > n`) is a helpful pruning step, though the backward-loop bounds handle it correctly anyway if omitted.
- Related/variant problems to try next: **Coin Change II** (LeetCode #518, unbounded knapsack counting combinations rather than 0/1 maximizing count) and **Target Sum** (LeetCode #494, single-capacity 0/1 knapsack reached via a clever transformation, good practice before tackling multi-dimensional capacity problems like this one).
