# Communication Tips — Binary Search

> **Type:** Study notes

Applying the [7-step framework](../../coding_interview_framework.md) specifically to this pattern:

- **Clarify (step 1):** always ask whether the array is sorted, whether it can contain duplicates,
  and — for "search space" problems — what the valid range of the answer is (e.g. "capacity is at
  least the heaviest single item and at most the sum of all items"). Getting the bounds wrong is the
  most common self-inflicted bug in this pattern.
- **Brute force (step 3):** state the O(n) linear scan first, even though it's obviously not the
  point — for search-space problems, state the brute force as "try every possible answer value from
  `lo` to `hi` and check feasibility," which is exactly the thing binary search speeds up, so saying
  it out loud sets up your step-4 explanation naturally.
- **Derive optimized approach (step 4):** for a disguised binary search (search space, not a sorted
  array), explicitly name the monotonic property before writing code — "if capacity `c` works, any
  capacity greater than `c` also works, so this is monotonic and I can binary search on it." This is
  the single highest-signal sentence you can say in this pattern; interviewers are specifically
  listening for whether you recognize the disguise.
- **Code cleanly (step 5):** commit out loud to one loop idiom before typing — "I'll use `left <
  right` with `right = mid` since I'm searching for a boundary, not an exact match" — so the
  interviewer can follow your bounds instead of being surprised when they don't match the classic
  `left <= right` shape.
- **Testing (step 6):** always trace the 2-element and 1-element cases by hand for this pattern —
  boundary bugs (infinite loops, off-by-one) hide in the smallest inputs, not the large ones. For
  rotated-array search, also trace a case where `target` is not present.
- **Common interviewer follow-up:** "what if there are duplicates?" (rotated search) or "what if
  multiple answers are feasible, return the smallest/largest" (search-space problems) — both are
  usually a one-line tweak (fallback linear shrink; flip which side you keep on `feasible(mid)`) so
  naming the tweak out loud before coding it shows you're ahead of the question, not scrambling to
  react to it.
