# Communication Tips — Bit Manipulation

> **Type:** Study notes

Applying the [7-step framework](../../coding_interview_framework.md) specifically to this pattern:

- **Clarify (step 1):** ask about the numeric range and whether negative numbers are possible — bit
  tricks that assume non-negative fixed-width integers (like a naive power-of-two check) can behave
  unexpectedly on negatives, and asking this up front heads off a wrong-answer surprise during
  testing.
- **Recognize the pattern out loud when it's "in disguise.**" A lot of this pattern's difficulty is
  that the problem never says "bits" — "enumerate all subsets" or "every element appears twice
  except one" don't sound like bit-manipulation problems on first read. Say the translation
  explicitly: "this is asking for the element that doesn't pair up, which is exactly what XOR-ing
  the whole array gives me, since pairs cancel out" — naming *why* you jumped to bits is the signal,
  not just producing the one-liner.
- **Brute force (step 3):** state the non-bit-trick baseline first — for "find the single number,"
  that's a hash-set/Counter approach at O(n) time, O(n) space; then introduce the XOR version as
  "same O(n) time, but O(1) space since I don't need to store anything." This framing makes clear the
  bit trick is a *space* optimization here, not a speed one — get that trade-off right rather than
  overselling it as strictly better.
- **Derive optimized approach (step 4):** for identities like `x & (x-1)`, briefly justify *why* it
  works rather than reciting it as a memorized fact — "subtracting 1 flips all trailing zeros to
  ones and the lowest set bit to zero, so ANDing with the original clears just that lowest set bit."
  Interviewers can tell the difference between "I memorized this trick" and "I understand why it
  works," and the latter survives being asked a slightly different bit-trick question.
- **Testing (step 6):** trace at least one example in actual binary, not just decimal — write
  `12 = 0b1100` next to your trace of `count_set_bits(12)` so the interviewer can follow the bit-level
  reasoning, not just watch decimal numbers change. This is the one pattern where showing binary
  explicitly, even briefly, meaningfully helps communication.
- **Complexity (step 7):** be precise about what's O(1) — a single bitwise op is O(1), but "count set
  bits via Brian Kernighan" is O(k) where k is the *number of set bits*, not O(1) and not O(32) — say
  which one you mean rather than a blanket "O(1) because it's just bit operations."
- **Common interviewer follow-up:** "can you do this without extra memory?" is almost always already
  answered by the bit-trick version itself (O(1) space) — point that out proactively rather than
  waiting to be asked, since it's the main reason this pattern exists as an alternative to a hash-set
  solution.
