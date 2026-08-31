# Mutable vs Immutable

> **Type:** Study notes

## Why interviewers ask this

The mutable-default-argument bug is one of the most commonly cited "real bug you've hit in
production" stories for a reason — it's subtle, it passes code review easily, and it directly
tests whether you understand
[object references](01_data_model_and_object_references.md) rather than the "variables are boxes"
mental model. For a Django/DRF developer, this also matters practically: mutable class-level
attributes on serializers/views, default arguments in utility functions, and shared mutable state
across requests in a WSGI worker are all instances of the same underlying issue.

## Which builtins are which

| Immutable | Mutable |
|---|---|
| `int`, `float`, `complex`, `bool` | `list` |
| `str` | `dict` |
| `tuple` | `set` |
| `frozenset` | `bytearray` |
| `bytes` | most user-defined classes (unless you lock them down) |
| `range` | |

A `tuple` is immutable *itself* (you can't reassign its slots or resize it), but if it contains a
mutable element, that element can still be mutated:
```python
t = ([1, 2], 3)
t[0].append(99)   # legal — mutating the list *inside* the tuple
print(t)           # ([1, 2, 99], 3)
t[1] = 4           # TypeError: 'tuple' object does not support item assignment
```
"Immutable" describes the container's own slots, not transitively everything reachable from it.

## The mutable default argument bug

Default argument values are evaluated **once**, at function *definition* time, not on every call —
and the same object is reused across every call that doesn't override it.

```python
# BROKEN
def add_item(item, basket=[]):
    basket.append(item)
    return basket

cart1 = add_item("apple")
print(cart1)                  # ['apple']
cart2 = add_item("banana")    # forgot to pass a basket again
print(cart2)                  # ['apple', 'banana']  <- BUG: cart1's items leaked in
print(cart1 is cart2)         # True — it's the SAME list object every call
```
This is exactly the shape of a real Django bug: a service function like
`def get_or_create_items(name, cache={})` silently accumulates state across unrelated requests in
the same worker process, because `cache={}` is one dict shared for the life of the process.

**The fix: use `None` as the sentinel default, create the mutable object inside the function body.**
```python
def add_item(item, basket=None):
    if basket is None:
        basket = []          # fresh list every call
    basket.append(item)
    return basket

cart1 = add_item("apple")
cart2 = add_item("banana")
print(cart1, cart2)           # ['apple'] ['banana'] — independent
```
Same rule applies to default `dict`/`set` arguments, and to class attributes defined as mutable
literals (`class Foo: items = []` — shared across *all instances* until an instance sets its own
`self.items`).

## Mutability and hashability

An object must be **hashable** to be used as a `dict` key or a `set` member. Python's rule of
thumb: mutable built-in types are unhashable (`list`, `dict`, `set` all raise `TypeError:
unhashable type`), because a mutable object's hash could change after insertion, breaking the
hash table's internal bucketing invariant.

```python
d = {}
d[(1, 2)] = "ok"          # tuple is immutable and hashable -> fine
d[[1, 2]] = "fails"        # TypeError: unhashable type: 'list'
```
This is why `frozenset` exists (a hashable, immutable `set`) and why you'll see
`tuple(sorted(...))` used as a dict key when you need a "canonical, hashable version" of a
collection — the same trick used for grouping in
[Arrays & Hashing](../02_dsa_and_coding/patterns/01_arrays_and_hashing/concept.md).

## Function arguments: "pass-by-object-reference"

Python is neither pass-by-value (C) nor pass-by-reference (C++ `&`) in the strict sense — it's
**pass-by-object-reference** (sometimes called "call by sharing"): the function parameter is a new
local name bound to the *same object* the caller's argument referenced.

- **Reassigning the parameter inside the function does not affect the caller** — that just rebinds
  the local name to a different object.
- **Mutating the object the parameter refers to** (if it's mutable) *is* visible to the caller,
  because there's still only one object.

```python
def reassign(lst):
    lst = [9, 9, 9]     # rebinds the LOCAL name `lst` only
    return lst

def mutate(lst):
    lst.append(9)        # mutates the shared object

original = [1, 2, 3]
reassign(original)
print(original)          # [1, 2, 3] — unaffected, reassignment didn't touch the caller's object

mutate(original)
print(original)          # [1, 2, 3, 9] — affected, in-place mutation touched the shared object
```

## Interview questions

**Q1: Why is `def f(x=[])` dangerous? How do you fix it?**
A: The default list is created once at function-definition time and reused on every call that
omits the argument, so mutations accumulate across calls. Fix: default to `None`, create the
mutable object inside the function body on each call.

**Q2: Is Python pass-by-value or pass-by-reference?**
A: Neither, strictly — it's "pass-by-object-reference." The parameter is a new name bound to the
same object as the caller's argument. Reassigning the parameter doesn't affect the caller;
mutating the object in place does, if the object is mutable.

**Q3: Why can't you use a `list` as a dict key but you can use a `tuple`?**
A: Dict keys must be hashable, and hashability requires the object's hash to stay constant over
its lifetime. Lists are mutable, so their hash could change after being used as a key, corrupting
the hash table. Tuples are immutable, so their hash is stable — as long as everything inside the
tuple is also hashable.

**Q4: Is a tuple containing a list fully immutable?**
A: No — the tuple's own slots can't be reassigned or resized, but a mutable object stored inside
it can still be mutated. Immutability is not automatically transitive.

## Exercises

1. Reproduce the broken `add_item(item, basket=[])` bug above, confirm with `is` that two calls
   share the same object, then fix it with the `None`-sentinel pattern and confirm independence.
2. Write a function `def make_id_lookup(items, cache={})` used as a cache across calls (the buggy
   pattern) versus one that takes `cache=None` and constructs fresh — call each twice with
   different `items` and explain the diverging output.
