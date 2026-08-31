# Coding Interview Communication Framework

> **Type:** Study notes

The single most common reason a technically-correct solution still gets a "no hire" is
communication, not correctness. Use this 7-step framework on **every** practice problem, not just
mocks and real interviews — it needs to be automatic by the time it matters.

## The 7 steps

### 1. Clarify the problem
Restate the problem in your own words before doing anything else. Ask about:
- Input constraints (size, range, can it be empty/null?)
- Output format
- Are there duplicates? Is the input sorted? Can values be negative?
- Any ambiguity in the prompt ("return the index" — 0-indexed or 1-indexed?)

> "So I have an array of integers, possibly with duplicates, and I need to find two indices whose
> values sum to a target. Can the same element be used twice? Is there always exactly one
> solution?"

### 2. Discuss examples and edge cases
Walk through the given example out loud. Then propose 1-2 edge cases yourself before coding:
empty input, single element, all-same elements, already-sorted/reverse-sorted, negative numbers,
very large input. This does double duty: it catches ambiguity from step 1, and it gives you test
cases for step 6 for free.

### 3. Explain the brute force
Even if you already see the optimal approach, say the brute force out loud first, with its
complexity. This shows range and gives the interviewer a checkpoint to redirect you if you've
misunderstood the problem, before you've invested in a wrong optimal approach.

> "The brute force is checking every pair, which is O(n²) time. I think we can do better with a
> hash map — let me think through that."

### 4. Derive the optimized approach
Narrate your thinking, don't just announce the answer. Interviewers are grading the *reasoning
path*, not just whether you happen to know the trick.

> "Since I need to find a complement for each number, and I want O(1) lookups, a hash map from
> value to index lets me check 'have I seen target - x before' in one pass instead of nested loops."

### 5. Code cleanly
- Use meaningful variable names (`left`/`right`, not `i`/`j`, for two pointers — unless `i`/`j` is
  genuinely the clearest convention for that structure, e.g. nested loop indices).
- Narrate briefly as you type ("I'll initialize a hash map here...") without narrating every
  keystroke.
- Handle the edge cases you identified in step 2 explicitly if they're not naturally covered.

### 6. Test manually
Trace your code against the example from step 2 by hand, on the whiteboard/editor, updating
variable values as you go. Don't just say "looks right" — actually trace at least one edge case
too. This is where you catch off-by-one errors before the interviewer has to point them out.

### 7. State time and space complexity
Explicitly state Big-O for both time and space, and briefly justify it ("O(n) time since we do one
pass, O(n) space for the hash map in the worst case where all values are unique").

## Common failure modes this framework prevents

- **Silent coding**: interviewer has no idea what you're thinking, can't help if you're going down
  a wrong path, and you seem less senior even with correct code.
- **Skipping brute force**: looks like you got lucky or memorized the answer rather than reasoned
  to it — hurts you even when the optimal solution is right.
- **No edge case discussion**: you ship code that crashes on empty input in front of the
  interviewer, which is an easy, avoidable "no hire" signal.
- **Silent debugging**: if your manual trace finds a bug, talk through the fix out loud rather than
  going quiet and fixing it — the interviewer is still grading you during the fix.

## A note on pacing

In a 45-minute round, roughly: 5 min clarify + examples, 5 min brute force + approach discussion,
20-25 min coding, 5-10 min testing + complexity + follow-ups. If you're 15 minutes in and still on
step 3, say so out loud and propose moving forward — interviewers respect visible time-awareness.
