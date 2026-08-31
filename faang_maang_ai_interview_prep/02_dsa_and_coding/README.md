# 02 — DSA and Coding

> **Type:** Study notes (index)

DSA organized **by pattern**, not just by data structure — the way you actually recognize problems
in an interview is "this smells like sliding window," not "this is about arrays." 16 patterns,
roughly in the order most curricula (and most interview loops) build on each other.

Read [`coding_interview_framework.md`](coding_interview_framework.md) first — the 7-step
communication framework you should use on every problem below, not just in real interviews.

## Patterns, in suggested order

| # | Pattern | Folder |
|---|---|---|
| 1 | Arrays & Hashing | [`patterns/01_arrays_and_hashing/`](patterns/01_arrays_and_hashing/) |
| 2 | Two Pointers | [`patterns/02_two_pointers/`](patterns/02_two_pointers/) |
| 3 | Sliding Window | [`patterns/03_sliding_window/`](patterns/03_sliding_window/) |
| 4 | Stack & Monotonic Stack | [`patterns/04_stack_and_monotonic_stack/`](patterns/04_stack_and_monotonic_stack/) |
| 5 | Linked Lists | [`patterns/05_linked_lists/`](patterns/05_linked_lists/) |
| 6 | Binary Search | [`patterns/06_binary_search/`](patterns/06_binary_search/) |
| 7 | Intervals | [`patterns/07_intervals/`](patterns/07_intervals/) |
| 8 | Trees & BSTs | [`patterns/08_trees_and_bsts/`](patterns/08_trees_and_bsts/) |
| 9 | Heaps & Priority Queues | [`patterns/09_heaps_and_priority_queues/`](patterns/09_heaps_and_priority_queues/) |
| 10 | Graphs (BFS/DFS/topo sort/shortest paths/union-find) | [`patterns/10_graphs/`](patterns/10_graphs/) |
| 11 | Backtracking | [`patterns/11_backtracking/`](patterns/11_backtracking/) |
| 12 | Greedy | [`patterns/12_greedy/`](patterns/12_greedy/) |
| 13 | Dynamic Programming | [`patterns/13_dynamic_programming/`](patterns/13_dynamic_programming/) |
| 14 | Tries | [`patterns/14_tries/`](patterns/14_tries/) |
| 15 | Bit Manipulation | [`patterns/15_bit_manipulation/`](patterns/15_bit_manipulation/) |
| 16 | Recursion & Complexity Analysis | [`patterns/16_recursion_and_complexity/`](patterns/16_recursion_and_complexity/) |

## Every pattern folder has the same 5 files + a solutions folder

| File | Purpose |
|---|---|
| `concept.md` | What the pattern is, when to recognize it, worked examples |
| `template.py` | Runnable Python skeleton/boilerplate for the pattern |
| `common_mistakes.md` | Specific bugs and misconceptions people hit with this pattern |
| `communication_tips.md` | How to talk through *this specific pattern* using the 7-step framework |
| `problem_tracker.md` | Curated Easy/Medium/Hard problem list with a status table |
| `solutions/` | Empty — write your own attempts here before checking references |

## How to work through a pattern

1. Read `concept.md`.
2. Skim `template.py` — don't memorize it, understand the shape.
3. Pick 2-3 problems from `problem_tracker.md` (start Easy, move to Medium) and solve them in
   `solutions/` using the 7-step framework, timed.
4. Read `common_mistakes.md` — check whether you made any of them.
5. Read `communication_tips.md` before your next mock interview that might touch this pattern.
6. Come back per `../00_master_plan/revision_schedule.md`.
