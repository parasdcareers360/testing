# Functions, *args, and **kwargs

> **Type:** Study notes

## Why interviewers ask this

Real Django/DRF codebases lean heavily on flexible function signatures — view methods that accept
`**kwargs` from URL routing, decorators that must transparently forward arbitrary arguments,
manager methods with optional filters. Interviewers check this to see whether you can read and
write signatures that are flexible *without* being a footgun (the classic mutable-default trap),
and whether you understand exactly how positional/keyword arguments get matched to parameters —
that mechanical understanding is what lets you debug a `TypeError: got multiple values for
argument` at 2am.

## Positional, keyword, and default arguments

```python
def create_user(username, email, is_active=True, role="member"):
    return {"username": username, "email": email, "is_active": is_active, "role": role}

create_user("alice", "alice@x.com")                       # positional
create_user(username="alice", email="alice@x.com")        # keyword
create_user("alice", email="alice@x.com", role="admin")   # mixed — positional must come first
```
Defaults are evaluated once at function-definition time — see
[Mutable vs Immutable](02_mutable_vs_immutable.md) for why a mutable default (`role=[]`) is a bug.

## `*args` and `**kwargs` mechanics

`*args` collects extra **positional** arguments into a tuple; `**kwargs` collects extra
**keyword** arguments into a dict. Order in the signature matters:
`def f(pos, *args, kw_only=None, **kwargs)`.

```python
def log_call(name, *args, **kwargs):
    print(f"{name} called with args={args}, kwargs={kwargs}")

log_call("create_user", "alice", "alice@x.com", role="admin")
# create_user called with args=('alice', 'alice@x.com'), kwargs={'role': 'admin'}
```
This is exactly the shape used to write a generic wrapper/decorator that forwards *any* call
signature through unchanged — see
[Closures & Decorators](05_closures_and_decorators.md).

## Unpacking at call sites (`*` and `**`)

The same `*`/`**` syntax, used at a *call site* instead of a *definition*, does the reverse:
spreads a collection into individual arguments.

```python
def create_user(username, email, role="member"):
    return {"username": username, "email": email, "role": role}

args = ["alice", "alice@x.com"]
kwargs = {"role": "admin"}
create_user(*args, **kwargs)
# equivalent to: create_user("alice", "alice@x.com", role="admin")
```
Common real use: forwarding a validated payload dict from a DRF serializer's `.validated_data`
straight into a model constructor: `MyModel.objects.create(**serializer.validated_data)`.

## Keyword-only arguments (`def f(*, x)`)

A bare `*` in the signature marks everything after it as **keyword-only** — it cannot be passed
positionally, even if it has no default. This forces callers to be explicit, which matters a lot
for functions with several same-typed parameters where positional order is easy to mix up.

```python
def resize_image(image, *, width, height):
    ...

resize_image(img, width=800, height=600)   # OK
resize_image(img, 800, 600)                 # TypeError: takes 1 positional argument but 3 were given
```
Real-world reason to use this: `def paginate(queryset, *, page, page_size=20)` prevents someone
from accidentally calling `paginate(qs, 20, 5)` and silently swapping page/page_size.

## Positional-only arguments (`def f(x, /)`)

A `/` in the signature marks everything before it as **positional-only** — callers cannot pass it
by keyword. Useful for parameter names that are implementation details (so you're free to rename
them later without breaking callers), and it's how many CPython builtins are actually defined
(e.g. you can't call `len(obj=x)`).

```python
def power(base, exponent, /, *, modulus=None):
    result = base ** exponent
    return result if modulus is None else result % modulus

power(2, 10)                    # OK — positional
power(base=2, exponent=10)      # TypeError — base/exponent are positional-only
power(2, 10, modulus=1000)      # OK — modulus is keyword-only
```
You can combine all three regions in one signature: positional-only, then normal, then `*args`,
then keyword-only, then `**kwargs`.

## Interview questions

**Q1: What's the difference between `*args` in a function definition vs. at a call site?**
A: In a definition, `*args` *collects* extra positional arguments into a tuple. At a call site,
`*iterable` *unpacks* an iterable into individual positional arguments. Same symbol, opposite
direction — the same is true for `**kwargs` with dicts.

**Q2: Why would you make an argument keyword-only?**
A: To force callers to name it explicitly, preventing positional-order mistakes when there are
multiple parameters of the same type (e.g. `width`/`height`, `page`/`page_size`) — it makes the
call site self-documenting and immune to accidental argument swaps.

**Q3: What does `def f(x, /, y, *, z)` mean?**
A: `x` is positional-only (cannot be passed as `x=...`), `y` is normal (positional or keyword),
`z` is keyword-only (must be passed as `z=...`).

**Q4: How do you write a decorator that works on any function regardless of its signature?**
A: Give the wrapper `*args, **kwargs`, and forward them unchanged to the wrapped function:
`def wrapper(*args, **kwargs): return func(*args, **kwargs)`. This works because `*args`/`**kwargs`
in the wrapper's definition collect whatever was passed, and the same syntax at the call site
re-spreads them.

**Q5: What error do you get if you pass the same argument both positionally and by keyword?**
A: `TypeError: f() got multiple values for argument 'x'` — Python resolves positional arguments
to parameter slots first, then tries to also bind the keyword argument to an already-filled slot.

## Exercises

1. Write `def summarize(*args, **kwargs)` that prints all positional args and all keyword args,
   then call it with a mix of unpacked `*my_list` and `**my_dict` and confirm the output matches
   what you'd get calling it directly.
2. Rewrite `def paginate(queryset, page, page_size=20)` to make `page` and `page_size`
   keyword-only, then update all call sites you'd imagine in a DRF view — explain in one sentence
   why this is safer for a function that will be called from many places in a codebase.
