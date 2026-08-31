# Data Model and Object References

> **Type:** Study notes

## Why interviewers ask this

Almost every "gotcha" Python question — mutable default arguments, aliasing bugs, `is` vs `==`
mistakes, unexpected shared state in Django model instances — traces back to one fact: **Python
variables are names bound to objects, not boxes that hold values.** An interviewer who asks "what
does this print?" on a 5-line snippet is checking whether you actually understand this model or
whether you've been pattern-matching syntax for 3 years without it. This also directly explains
real production bugs: two DRF serializer fields silently pointing at the same list, or a Django
queryset cached object being mutated in one request and reused in another.

## The core model

In C, `int x = 5;` allocates a box named `x` and puts `5` in it. In Python, `x = 5` creates an
`int` object `5` somewhere in memory, and makes the name `x` point to it. Assignment **never
copies the object** — it binds a name to an existing object.

```python
a = [1, 2, 3]
b = a          # b is NOT a copy — b and a are two names for the same list object
b.append(4)
print(a)       # [1, 2, 3, 4]  <- a changed too, because there's only one object
print(a is b)  # True — same object identity
```

Every value in Python — `5`, `"hi"`, `[1, 2]`, a function, a class, `None` — is an object with
three properties: **identity** (a unique id, stable for its lifetime — `id(obj)`), **type**
(fixed for its lifetime), and **value** (may or may not be mutable — see
[Mutable vs Immutable](02_mutable_vs_immutable.md)).

## `id()` and `is` vs `==`

- `id(obj)` returns a unique integer for the object's identity — in CPython this is implemented as
  the object's memory address, but treat that as an implementation detail, not a guarantee.
- `is` compares **identity** (`id(a) == id(b)`) — "are these literally the same object in memory?"
- `==` compares **value** by calling `a.__eq__(b)` — "do these represent the same value?"

```python
x = [1, 2, 3]
y = [1, 2, 3]
print(x == y)  # True  -> same value
print(x is y)  # False -> two distinct list objects with equal contents
```

**Rule of thumb interviewers expect:** use `is` only for `None`, `True`, `False`, and sentinel
objects (`is None`, never `== None`) — because those are guaranteed singletons. Use `==` for
everything else, including strings and numbers, even though `is` sometimes *appears* to work on
them (see interning below) — relying on that is a bug waiting to happen.

## The `__eq__` / `__hash__` contract

If you override `__eq__` on a class, Python sets `__hash__` to `None` unless you also define it —
because the contract is: **if `a == b`, then `hash(a) == hash(b)` must also hold.** Break this and
the object silently breaks as a dict key or set member (it can appear "missing" even when an equal
object is present).

```python
class UserId:
    def __init__(self, value: int):
        self.value = value

    def __eq__(self, other):
        return isinstance(other, UserId) and self.value == other.value

    def __hash__(self):
        return hash(self.value)  # must be consistent with __eq__

u1, u2 = UserId(7), UserId(7)
print(u1 == u2)                  # True — same logical value
s = {u1}
print(u2 in s)                   # True — works only because __hash__ matches __eq__
```
If you only define `__eq__` and skip `__hash__`, `UserId` instances become unhashable
(`TypeError: unhashable type`) — a very common bug when adding value-equality to a class that used
to rely on default identity-based `__eq__`/`__hash__`.

## Interning gotchas: "why did `is` work there but not here"

CPython caches (**interns**) small integers (`-5` to `256`) and some string literals that look
like identifiers, as a memory/performance optimization — **not a language guarantee.**

```python
a = 100
b = 100
print(a is b)      # True  -> small ints are cached, both names point to the same object

c = 1000
d = 1000
print(c is d)      # False in the general case (True at the same REPL line sometimes,
                    #  due to compiler constant-folding — never rely on it)

s1 = "hello"
s2 = "hello"
print(s1 is s2)     # True  -> compile-time string literal interning

s3 = "".join(["h", "e", "l", "l", "o"])
print(s3 is s1)      # False -> built at runtime, not interned automatically
print(s3 == s1)       # True  -> values are equal, identity is not
```
The teaching point: `is` "working" on small ints/literal strings is a CPython implementation
detail you must not rely on. This is a classic interview trap question specifically to see if you
say "always use `==` for value comparison" or if you've internalized a false belief that `is`
works for numbers/strings generally.

## Interview questions

**Q1: What's the difference between `is` and `==`? When would you ever use `is`?**
A: `is` checks object identity (same object in memory); `==` checks value equality via `__eq__`.
Use `is` for singleton checks (`None`, `True`, `False`) and sentinel objects; use `==` for
everything else.

**Q2: Why does `a = [1,2]; b = a; b.append(3)` change `a` too?**
A: `b = a` binds a second name to the same list object — no copy happens. Both names reference one
mutable object, so mutating through either name is visible through both.

**Q3: If I override `__eq__` on a class, why might instances suddenly fail as dict keys?**
A: Python sets `__hash__` to `None` when `__eq__` is defined without `__hash__`, since a stale
default hash could violate the equal-objects-must-have-equal-hashes contract. You must
explicitly define `__hash__` too if the object should remain hashable.

**Q4: `100 is 100` prints `True`, but `1000 is 1000` sometimes prints `False`. Why?**
A: CPython interns small integers (-5 to 256) as a cache optimization. Larger ints are allocated
fresh each time in general, so identity is not guaranteed. This is an implementation detail, not
a language spec — never write code that depends on it.

## Exercises

1. Write a `Point` class with `x`, `y` fields, define `__eq__` for value equality, then try to put
   two equal `Point` instances into a `set` before and after adding `__hash__` — observe the
   `TypeError` and fix it.
2. Predict the output of `a = "hi"; b = "h" + "i"; print(a is b, a == b)` then run it and explain
   any surprise using the interning rules above (compile-time constant folding often makes this
   `True` — contrast with building the string via `input()` or `.join()` at runtime, which won't
   intern).
