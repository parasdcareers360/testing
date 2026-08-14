# Hard — Burst Balloons

**Source**: LeetCode #312
**Pattern**: Dynamic Programming — Interval / Range
**Difficulty**: Hard

## Problem Statement
You are given `n` balloons, indexed from `0` to `n-1`. Each balloon is painted with a number on it, represented by an array `nums`. You are asked to burst all the balloons.

If you burst the `i`-th balloon, you will get `nums[left] * nums[i] * nums[right]` coins, where `left` and `right` are the adjacent indices of `i` at the moment of bursting (after previous balloons have already been removed and the remaining balloons have "closed the gap" to become each other's neighbors). If `left` or `right` does not exist (i.e., `i` is currently at an end), treat the missing neighbor's value as `1`.

Return the maximum coins you can collect by bursting all the balloons in some order.

## Constraints
- `n == nums.length`
- `1 <= n <= 500`
- `0 <= nums[i] <= 100`

## Examples
1. Input: `nums = [3, 1, 5, 8]` -> Output: `167`
   Explanation: One optimal order: burst balloon at index 1 (`3*1*5=15`, remaining `[3,5,8]`), then index 1 (`3*5*8=120`, remaining `[3,8]`), then index 0 (`1*3*8=24`, remaining `[8]`), then index 0 (`1*8*1=8`). Total: `15+120+24+8=167`.
2. Input: `nums = [1, 5]` -> Output: `10`
   Explanation: Burst index 0 first: `1*1*5=5`, remaining `[5]`. Then burst it: `1*5*1=5`. Total: `5+5=10`. (Bursting index 1 first gives the same total by symmetry: `1*5*1=5` then `1*1*1=1` = 6... actually checking order matters: bursting index 1 first gives `1*5*1=5`, then remaining `[1]` gives `1*1*1=1`, total `6`. So bursting index 0 first (total 10) is strictly better — this shows order matters and greedy doesn't work.)

## Intuition — Why This Pattern
**Brute force**: Try every one of the `n!` orders of bursting balloons, simulate each, and track the maximum total coins. Completely infeasible even for `n` around 15-20, let alone 500.

**What's inefficient**: The naive way to think about this problem is "which balloon do I burst first?" — but that's the wrong direction, because bursting a balloon changes who is adjacent to whom for *every remaining choice*, making the subproblems entangled and hard to define cleanly in terms of "first" decisions.

**The key reframing (why this is Hard)**: Instead of asking "which balloon do I burst first," ask **"which balloon do I burst LAST within a given range?"** This reframing is the crucial insight that makes the problem decompose into independent interval subproblems: if balloon `k` is the *last* one burst within an open range `(i, j)` (using two virtual boundary balloons of value 1 at positions `i` and `j`, which are guaranteed to still be present since everything strictly between them is gone), then when we finally burst `k`, its neighbors are exactly `nums[i]` and `nums[j]` (the untouched boundary values) — regardless of the order in which everything else in `(i, j)` was burst before it. This decouples the range `(i, k)` and `(k, j)` into two fully independent subproblems, which is exactly the interval-DP decomposition: `dp[i][j] = max over k in (i,j) of dp[i][k] + dp[k][j] + nums[i]*nums[k]*nums[j]`.

This is a bigger leap than typical interval DP (like palindrome problems) because the "combine two sub-ranges" step requires the non-obvious trick of padding the array with sentinel 1s and reasoning about bursting order *backwards* (last-to-burst, not first-to-burst) — this is what escalates it from Medium interval DP to Hard.

**State**: Pad `nums` with a `1` at both ends, calling the padded array `balloons` of length `n+2` (indices `0..n+1`, where index `0` and index `n+1` are the sentinel 1s). Define:

`dp[i][j]` = maximum coins obtainable by bursting **all balloons strictly between** indices `i` and `j` (exclusive on both ends), given that `balloons[i]` and `balloons[j]` are still present as boundaries (never burst as part of this subproblem).

## Approach
1. Pad the array: `balloons = [1] + nums + [1]`. Let `m = len(balloons)` (i.e., `n + 2`).
2. Create a 2D table `dp` of size `m x m`, initialized to all `0`. `dp[i][j] = 0` whenever `j <= i + 1` (no balloons strictly between them — base case, nothing to burst).
3. Iterate by increasing **gap length** `L` from `2` to `m - 1` (gap = number of positions between `i` and `j`, i.e., `j - i`). For each `i` from `0` to `m - 1 - L`, let `j = i + L`:
   For each `k` strictly between `i` and `j` (i.e., `k` from `i+1` to `j-1`) — `k` is the balloon burst **last** within `(i, j)`:
   `dp[i][j] = max(dp[i][j], dp[i][k] + dp[k][j] + balloons[i] * balloons[k] * balloons[j])`
4. The final answer is `dp[0][m-1]` (bursting everything strictly between the two sentinel boundaries, i.e., all of the original balloons).

## Dry Run
Example: `nums = [3, 1, 5, 8]`. Padded: `balloons = [1, 3, 1, 5, 8, 1]` (indices 0..5). Expected output: `167`.

We want `dp[0][5]`. Ranges are indexed by `(i, j)` with gap `L = j - i`.

**Gap L=2** (ranges with exactly one balloon strictly between `i` and `j`): only choice for `k` is the single balloon between them.
- `dp[0][2]` (balloon at k=1, value 3): `dp[0][1] + dp[1][2] + balloons[0]*balloons[1]*balloons[2] = 0+0+1*3*1 = 3`
- `dp[1][3]` (k=2, value 1): `= 0+0+3*1*5 = 15`
- `dp[2][4]` (k=3, value 5): `= 0+0+1*5*8 = 40`
- `dp[3][5]` (k=4, value 8): `= 0+0+5*8*1 = 40`

**Gap L=3** (two balloons strictly between):
- `dp[0][3]` (balloons at k=1 or k=2 between i=0,j=3):
  - k=1: `dp[0][1]+dp[1][3]+balloons[0]*balloons[1]*balloons[3] = 0+15+1*3*5=15+15=30`
  - k=2: `dp[0][2]+dp[2][3]+balloons[0]*balloons[2]*balloons[3] = 3+0+1*1*5=3+5=8`
  - max = 30
- `dp[1][4]` (k=2 or k=3 between i=1,j=4):
  - k=2: `dp[1][2]+dp[2][4]+balloons[1]*balloons[2]*balloons[4]=0+40+3*1*8=40+24=64`
  - k=3: `dp[1][3]+dp[3][4]+balloons[1]*balloons[3]*balloons[4]=15+0+3*5*8=15+120=135`
  - max = 135
- `dp[2][5]` (k=3 or k=4 between i=2,j=5):
  - k=3: `dp[2][3]+dp[3][5]+balloons[2]*balloons[3]*balloons[5]=0+40+1*5*1=40+5=45`
  - k=4: `dp[2][4]+dp[4][5]+balloons[2]*balloons[4]*balloons[5]=40+0+1*8*1=40+8=48`
  - max = 48

**Gap L=4** (three balloons strictly between):
- `dp[0][4]` (k in {1,2,3}, i=0,j=4):
  - k=1: `dp[0][1]+dp[1][4]+balloons[0]*balloons[1]*balloons[4]=0+135+1*3*8=135+24=159`
  - k=2: `dp[0][2]+dp[2][4]+balloons[0]*balloons[2]*balloons[4]=3+40+1*1*8=43+8=51`
  - k=3: `dp[0][3]+dp[3][4]+balloons[0]*balloons[3]*balloons[4]=30+0+1*5*8=30+40=70`
  - max = 159
- `dp[1][5]` (k in {2,3,4}, i=1,j=5):
  - k=2: `dp[1][2]+dp[2][5]+balloons[1]*balloons[2]*balloons[5]=0+48+3*1*1=48+3=51`
  - k=3: `dp[1][3]+dp[3][5]+balloons[1]*balloons[3]*balloons[5]=15+40+3*5*1=55+15=70`
  - k=4: `dp[1][4]+dp[4][5]+balloons[1]*balloons[4]*balloons[5]=135+0+3*8*1=135+24=159`
  - max = 159

**Gap L=5** (all four original balloons strictly between i=0, j=5):
- `dp[0][5]` (k in {1,2,3,4}):
  - k=1: `dp[0][1]+dp[1][5]+balloons[0]*balloons[1]*balloons[5]=0+159+1*3*1=159+3=162`
  - k=2: `dp[0][2]+dp[2][5]+balloons[0]*balloons[2]*balloons[5]=3+48+1*1*1=51+1=52`
  - k=3: `dp[0][3]+dp[3][5]+balloons[0]*balloons[3]*balloons[5]=30+40+1*5*1=70+5=75`
  - k=4: `dp[0][4]+dp[4][5]+balloons[0]*balloons[4]*balloons[5]=159+0+1*8*1=159+8=167`
  - max = **167**

Final answer: `dp[0][5] = 167`, matching the expected output (achieved by bursting balloon k=4, i.e., original index 3 with value 8, last — consistent with the example's optimal order).

## Solution (Python 3)
```python
def max_coins(nums: list[int]) -> int:
    balloons = [1] + nums + [1]
    m = len(balloons)
    dp = [[0] * m for _ in range(m)]

    for length in range(2, m):  # gap length j - i
        for i in range(0, m - length):
            j = i + length
            best = 0
            for k in range(i + 1, j):  # k = last balloon burst within (i, j)
                coins = dp[i][k] + dp[k][j] + balloons[i] * balloons[k] * balloons[j]
                if coins > best:
                    best = coins
            dp[i][j] = best

    return dp[0][m - 1]


if __name__ == "__main__":
    print(max_coins([3, 1, 5, 8]))  # Expected: 167
    print(max_coins([1, 5]))         # Expected: 10
```

## Complexity Analysis
- Time: O(n^3) — O(n^2) ranges, each requiring an O(n) scan over possible "last burst" choices `k`.
- Space: O(n^2) for the DP table.

## Key Takeaways
- The signature trick of this problem — think about which item is removed **last** within a range rather than first — is a powerful general technique whenever removing/merging an element changes its neighbors' adjacency (also used in Remove Boxes and some matrix-chain-style problems).
- Padding the array with sentinel boundary values (`1` on each side) avoids special-casing "no left/right neighbor" throughout the recurrence — a small trick that greatly simplifies the implementation.
- Common mistake: trying to model this as "which balloon do I burst first," which does not decompose into independent subproblems because bursting order changes adjacency for every subsequent choice — only the "burst last" framing yields clean independent left/right subproblems.
- Related/variant problems to try next: **Minimum Cost to Merge Stones** (LeetCode #1000, interval DP merging adjacent piles with an extra "group size divisible by k-1" constraint) and **Remove Boxes** (LeetCode #546, an even harder interval DP with an additional "count of same-colored boxes carried along" state dimension).
