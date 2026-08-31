# Common Mistakes — Bit Manipulation

> **Type:** Study notes

- **Forgetting Python ints are arbitrary-precision (no fixed 32-bit wraparound).** `~x` in Python is
  `-x - 1`, not "flip 32 bits" like in C/Java — code that assumes a fixed bit width (e.g. computing a
  two's-complement negative by flipping 32 bits) needs an explicit mask like `x & 0xFFFFFFFF` to
  behave like fixed-width languages; without it, results silently differ from what a Java/C++
  candidate's identical-looking code would produce.
- **Confusing `is_power_of_two`'s edge cases.** `x = 0` passes `x & (x-1) == 0` (since `0 & -1 == 0`
  in Python) despite not being a power of two — always guard with `x > 0` first. Negative `x` is
  also not a power of two but can pass the AND check depending on representation; the `x > 0` guard
  handles both.
- **Using `x & (x - 1)` on `x = 0` without a loop guard.** `count_set_bits`'s `while x:` loop
  correctly terminates immediately when `x = 0`, but a hand-rolled version that forgets the falsy
  check (`while True: x &= x - 1`) infinite-loops since `0 & -1 == 0` forever in Python's
  arbitrary-precision arithmetic — always loop on `while x:`, not a fixed iteration count.
- **Reaching for XOR when elements can appear more than twice.** The XOR-cancels-pairs trick only
  works for "exactly two occurrences cancel out" — extending it to "appears three times except one"
  needs a genuinely different technique (bit-count-mod-3 per position, see `concept.md` exercise 1),
  not just XOR-ing more values.
- **Off-by-one in bit indexing.** `1 << i` sets bit `i` counting from 0 at the least-significant bit
  — mixing this up with 1-indexed bit positions (common when a problem statement says "the i-th bit"
  ambiguously) produces a mask one position off; always clarify with a concrete example (`1 << 0 ==
  1`, `1 << 3 == 8`) rather than assuming.
- **Bitmask subset enumeration silently blowing up for large n.** `1 << n` masks means `n = 20` is
  already ~1M iterations and `n = 30` is over a billion — this pattern is only appropriate when the
  problem constraints explicitly say `n` is small (typically stated or implied as `n <= 20`); for
  larger `n`, this is a strong signal the intended solution is DP over bitmask states, not brute-force
  enumeration, or an entirely different pattern.
- **Using `^` when the problem actually wants boolean XOR/logical operators.** Python's `^` is
  bitwise XOR on integers but also works as logical XOR on booleans (`True ^ False == True`) — this
  mostly works by luck; be explicit about whether you're operating on ints or bools so the intent is
  clear when narrating.
