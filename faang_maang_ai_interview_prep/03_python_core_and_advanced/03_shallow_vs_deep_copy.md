# Shallow vs Deep Copy

> **Type:** Study notes

## Why interviewers ask this

"Copying" a Python object is not one operation — it's a spectrum from "new reference to the same
object" to "fully independent object graph," and picking the wrong point on that spectrum causes
real bugs: a Django view that copies a serialized dict "for safety" but still shares a nested list
with the original, so mutating the "copy" corrupts cached data. Interviewers use this to test
whether you understand [object references](01_data_model_and_object_references.md) applied to
nested structures, and whether you know the performance cost of reaching for `deepcopy` reflexively.

## The three levels

```python
import copy

original = {"name": "alice", "roles": ["admin", "editor"]}

no_copy   = original                    # same object — not a copy at all
shallow   = copy.copy(original)         # new dict, but roles list is SHARED
deep      = copy.deepcopy(original)     # new dict AND new roles list, fully independent
```

| Operation | New top-level container? | Nested mutable objects shared? |
|---|---|---|
| `b = a` | No — same object | N/A, it's the same object |
| `copy.copy(a)` / `a.copy()` / `list(a)` / slicing `a[:]` | Yes | Yes — shared with original |
| `copy.deepcopy(a)` | Yes | No — recursively copied |

## Shallow copy silently sharing nested state (real broken example)

```python
import copy

user_template = {"name": "", "tags": ["new-user"]}

def create_user(name):
    user = copy.copy(user_template)   # looks safe — "I copied it!"
    user["name"] = name
    return user

alice = create_user("alice")
bob = create_user("bob")

alice["tags"].append("vip")           # mutating alice's tags list in place
print(bob["tags"])                    # ['new-user', 'vip']  <- BUG: bob got alice's tag too!
print(alice["tags"] is user_template["tags"])   # True — shallow copy never touched the nested list
```
`copy.copy` only copies the *outer* dict — the `"tags"` key in every copy still points at the
exact same list object as `user_template["tags"]`. This is the same class of bug as the mutable
default argument, just introduced via an explicit (but insufficient) copy call instead of a
default argument.

**Fix — use `deepcopy`, or reconstruct manually:**
```python
def create_user_fixed(name):
    user = copy.deepcopy(user_template)   # tags list is now independent
    user["name"] = name
    return user

# Manual reconstruction is often clearer and faster when the shape is known and simple:
def create_user_manual(name):
    return {"name": name, "tags": list(user_template["tags"])}
```
Manual reconstruction (`list(...)`, `dict(...)`, or a comprehension) is usually preferred in
real code over `deepcopy` when you know the exact shape — it's faster, and it's explicit about
what's actually being copied instead of "copy the entire graph, whatever it turns out to be."

## `__copy__` and `__deepcopy__` hooks

Custom classes can control their own copy behavior by implementing `__copy__(self)` and
`__deepcopy__(self, memo)`. Without them, `copy`/`deepcopy` fall back to introspecting
`__dict__` generically.

```python
class Connection:
    def __init__(self, host, socket):
        self.host = host
        self.socket = socket   # not something we want duplicated

    def __deepcopy__(self, memo):
        # keep the same underlying socket, deep-copy everything else
        new = Connection.__new__(Connection)
        memo[id(self)] = new
        new.host = copy.deepcopy(self.host, memo)
        new.socket = self.socket   # intentionally shared, not duplicated
        return new
```
The `memo` dict is how `deepcopy` avoids infinite recursion on cyclic references and avoids
duplicating an object that's referenced from multiple places in the same graph — always pass it
through when you call `copy.deepcopy` recursively inside a custom `__deepcopy__`.

## Performance cost of `deepcopy`

`deepcopy` walks the *entire* object graph recursively, pickling-style, and maintains a memo dict
to detect cycles and shared references. On a large nested structure (e.g., a big parsed JSON
response, a Django queryset serialized to nested dicts/lists), this is measurably slower than a
shallow copy or manual reconstruction — O(total nodes in the graph), with real per-node overhead
from the generic dispatch machinery.

```python
import copy, timeit

big = {"items": [{"id": i, "meta": {"tags": ["a", "b"]}} for i in range(10_000)]}

t_shallow = timeit.timeit(lambda: copy.copy(big), number=1000)
t_deep    = timeit.timeit(lambda: copy.deepcopy(big), number=100)  # fewer reps, it's slower
print(t_shallow, t_deep)   # deepcopy is roughly 2-3 orders of magnitude slower per-call here
```
`deepcopy` also correctly handles **cyclic structures** (an object that references itself,
directly or indirectly) via the memo dict — a naive recursive copy without memoization would
infinite-loop or stack-overflow on those. That correctness is exactly why it's slower: it's doing
real bookkeeping, not just blindly recursing.

**Practical guidance to say out loud in an interview:** default to shallow copy or manual
reconstruction when you know the structure is flat or you control what needs independence; reach
for `deepcopy` when the structure is deep/unknown/possibly cyclic and correctness matters more
than the performance cost.

## Interview questions

**Q1: What's the difference between `copy.copy` and `copy.deepcopy`?**
A: `copy.copy` creates a new top-level container but nested mutable objects are still shared
references with the original. `copy.deepcopy` recursively copies the entire object graph so
nothing is shared.

**Q2: Give a real example where a shallow copy causes a bug.**
A: Copying a dict template with `copy.copy` where one value is a list — mutating that list on one
"copy" mutates it on every other copy and the original, because the list itself was never
duplicated, only the outer dict.

**Q3: When would you avoid `deepcopy` even though it's "more correct"?**
A: When the structure is large and you know its exact shape — manual reconstruction (list/dict
comprehension) is faster and more explicit. Also when the object intentionally holds a shared
resource (a socket, DB connection, file handle) that shouldn't be duplicated — override
`__deepcopy__` to keep that reference shared.

**Q4: How does `deepcopy` avoid infinite recursion on a self-referencing object?**
A: It maintains a `memo` dict keyed by `id()` of already-copied objects; before copying an object
it checks whether it's already in the memo and reuses that copy instead of recursing again.

## Exercises

1. Reproduce the `create_user` bug above with `copy.copy`, confirm the shared list with `is`, then
   fix it two ways: `copy.deepcopy` and manual reconstruction — compare the resulting code.
2. Build a small cyclic structure (`a = {}; a["self"] = a`) and call `copy.deepcopy(a)` — confirm
   it doesn't crash, then explain why a naive hand-written recursive copy function without a memo
   dict would.
