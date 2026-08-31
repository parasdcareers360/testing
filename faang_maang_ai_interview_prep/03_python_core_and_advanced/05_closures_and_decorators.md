# Closures and Decorators

> **Type:** Study notes

## Why interviewers ask this

Decorators are everywhere in a Django/DRF stack — `@login_required`, `@api_view`,
`@transaction.atomic`, `@property`, `@lru_cache`, `@retry` — and every one of them is a plain
function built on the closure mechanism. Interviewers ask you to write one from scratch because it
tests three things at once: understanding of scope/closures, understanding that functions are
first-class objects (see
[Data Model](01_data_model_and_object_references.md)), and whether you know the `functools.wraps`
detail that separates "worked once" code from production-quality code.

## What a closure actually is

A closure is a function that **remembers the variables from its enclosing scope**, even after
that enclosing function has returned. Python implements this by keeping a reference to the "free
variables" (variables used but not defined locally) alongside the function object.

```python
def make_multiplier(factor):
    def multiply(x):
        return x * factor      # `factor` is a free variable, captured from the enclosing scope
    return multiply

double = make_multiplier(2)
triple = make_multiplier(3)
print(double(5), triple(5))    # 10 15 — each closure remembers its own `factor`
print(double.__closure__[0].cell_contents)   # 2 — the captured value, inspectable
```
Each call to `make_multiplier` creates a *new* `factor` binding, so `double` and `triple` don't
interfere with each other — this is exactly how decorator factories (below) give each decorated
function independent configuration.

## `nonlocal`

By default, assigning to a name inside a nested function creates a *new local* name in that
inner scope — it does not modify the enclosing scope's variable. `nonlocal` explicitly tells
Python "this name refers to the nearest enclosing scope's variable, not a new local one."

```python
def make_counter():
    count = 0
    def increment():
        nonlocal count     # without this, `count += 1` raises UnboundLocalError
        count += 1
        return count
    return increment

counter = make_counter()
print(counter(), counter(), counter())   # 1 2 3 — state persists across calls via the closure
```

## Writing a decorator from scratch

A decorator is just a function that takes a function and returns a (usually wrapping) function.
`@decorator` above `def f(): ...` is exactly sugar for `f = decorator(f)`.

```python
def uppercase_result(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result.upper()
    return wrapper

@uppercase_result
def greet(name):
    return f"hello, {name}"

print(greet("alice"))   # HELLO, ALICE
```

## `functools.wraps` and why it matters

Without `functools.wraps`, the wrapper function **replaces** the original's `__name__`,
`__doc__`, and other metadata — breaking introspection, debuggers, and tools like Django's admin
or DRF's auto-generated API docs that read `__name__`/docstrings.

```python
from functools import wraps

def uppercase_result(func):
    @wraps(func)                     # copies __name__, __doc__, __module__, etc. onto wrapper
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs).upper()
    return wrapper

@uppercase_result
def greet(name):
    """Return a greeting for name."""
    return f"hello, {name}"

print(greet.__name__)   # 'greet'      (without @wraps this would print 'wrapper')
print(greet.__doc__)    # 'Return a greeting for name.'  (without @wraps this would be None)
```
Say this out loud in interviews: "always use `functools.wraps` in a real decorator — otherwise
every function you decorate loses its identity for tracebacks, `help()`, and any framework that
inspects `__name__`."

## Decorators with arguments (decorator factories)

`@retry(times=3)` needs an extra layer: a function that takes the decorator's *own* arguments and
returns the actual decorator (which then takes the function and returns the wrapper). Three
nested levels total.

```python
import time
from functools import wraps

def retry(times=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    last_exc = exc
                    print(f"attempt {attempt} failed: {exc}")
                    if attempt < times:
                        time.sleep(delay)
            raise last_exc
        return wrapper
    return decorator

@retry(times=3, delay=0.5)
def flaky_api_call():
    import random
    if random.random() < 0.7:
        raise ConnectionError("simulated network blip")
    return "ok"
```
`retry(times=3, delay=0.5)` runs first and returns `decorator`, which then gets applied to
`flaky_api_call` — this is why decorator factories always need the extra outer layer compared to a
plain decorator.

## A real example: timing decorator

```python
import time
from functools import wraps

def timed(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = time.perf_counter() - start
            print(f"{func.__name__} took {elapsed:.4f}s")
    return wrapper

@timed
def process_batch(pages):
    time.sleep(0.1)   # simulate OCR/PDF processing work
    return len(pages)
```
Using `try/finally` ensures the timing is logged even if `func` raises — a detail interviewers
notice when comparing a "correct" timing decorator to one that silently skips logging on error.

## Interview questions

**Q1: What is a closure?**
A: A function object that captures references to variables from its enclosing scope (free
variables), so it can use those values even after the enclosing function has returned. Each
invocation of the enclosing function creates a fresh, independent set of captured variables.

**Q2: Why do you need `nonlocal` to mutate an enclosing variable from a nested function?**
A: Without it, any assignment to a name inside a nested function is treated as creating a new
local variable in that inner scope (Python decides this at compile time by scanning for
assignments), which shadows the outer variable instead of modifying it, causing
`UnboundLocalError` if you also try to read it before that local assignment.

**Q3: What does `functools.wraps` do and why does it matter?**
A: It copies metadata (`__name__`, `__doc__`, `__module__`, `__wrapped__`, etc.) from the original
function onto the wrapper, so the decorated function still looks like itself to introspection
tools, tracebacks, `help()`, and frameworks that rely on `__name__`.

**Q4: How do you write a decorator that itself takes arguments, like `@retry(times=3)`?**
A: Add an outer function that accepts the decorator's arguments and returns the actual decorator
function, which in turn returns the wrapper — three nested levels: `retry(times) -> decorator(func)
-> wrapper(*args, **kwargs)`.

**Q5: What's `@property` under the hood?**
A: `property` is a decorator (technically a descriptor class) that turns a method into something
accessed like an attribute — `obj.value` calls the getter function instead of requiring
`obj.value()`. It's the same "function that takes a function and returns something else" pattern.

## Exercises

1. Write the `retry` decorator factory above from scratch without looking, apply it to a function
   that fails a fixed number of times before succeeding (use a closure-captured counter), and
   confirm it retries the right number of times.
2. Write a `@timed` decorator, apply it to two functions, then remove `@wraps` and observe
   `help(func)` / `func.__name__` before and after — write one sentence on what broke.
