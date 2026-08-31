# Common Mistakes — Arrays & Hashing

> **Type:** Study notes

- **Checking the wrong direction on complement lookup.** Inserting into `seen` *before* checking
  for the complement lets an element pair with itself (`nums[i] + nums[i] == target` incorrectly
  matching when there's only one such element). Always check first, insert second, in a single
  pass — see `template.py` Shape 1.
- **Using a `list` for membership checks in a loop.** `x in some_list` is O(n); inside a loop this
  silently turns an intended O(n) solution into O(n²). If you need repeated membership checks,
  convert to a `set` first.
- **Forgetting hashability requirements.** You can't use a `list` as a dict key or set member
  (unhashable) — this bites people converting a sub-array into a canonical key; use `tuple(...)`
  instead of leaving it as a `list`.
- **Mutating a dict while iterating over it.** `for k in d: del d[k]` raises `RuntimeError:
  dictionary changed size during iteration`. Iterate over `list(d.keys())` (or `d.items()`) if you
  need to mutate during the loop.
- **Off-by-one in prefix sums.** The prefix array should be length `n + 1` with `prefix[0] = 0`, so
  `range_sum(l, r) = prefix[r] - prefix[l]` works for `l == 0` too. Building a length-`n` prefix
  array without the leading zero forces awkward special-casing for ranges starting at index 0.
- **Assuming dict insertion order doesn't matter.** Since Python 3.7 dicts preserve insertion
  order — some problems (e.g. "first non-repeating character") rely on this being guaranteed
  behavior, not an implementation detail, so it's safe to use, but be aware `set` does **not**
  preserve order, which trips people who assume it behaves like a dict.
- **Not clarifying case sensitivity / whitespace for string-key problems** (anagrams, grouping) —
  ask whether input is normalized before assuming `"Eat"` and `"eat"` group together.
