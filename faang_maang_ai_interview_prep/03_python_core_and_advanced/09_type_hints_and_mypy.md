# Type Hints and mypy

> **Type:** Study notes

## Why interviewers ask this

Type hints signal whether you write code meant to be maintained by a team, not just code that runs
once. Interviewers ask about this to check two things: can you read/write reasonably modern typed
Python, and do you understand what static typing actually buys you (catching bugs *before*
runtime) versus what it doesn't (it changes nothing at runtime — Python never enforces annotations
on its own). This file also sets up [dataclasses and Pydantic](11_dataclasses_and_pydantic.md),
where the difference between static-only hints and runtime-validated hints becomes concrete.

## Basic syntax

```python
def greet(name: str, times: int = 1) -> str:
    return (name + " ") * times

age: int = 30
scores: list[int] = [90, 85, 77]
lookup: dict[str, int] = {"a": 1}
maybe_user: str | None = None          # modern (3.10+) union syntax
maybe_user2: Optional[str] = None      # older, equivalent, from typing
```

Since Python 3.9, built-in generics (`list[int]`, `dict[str, int]`, `tuple[int, ...]`) work
directly — no need to import `List`/`Dict` from `typing` anymore, though you'll still see the old
style in older codebases. `X | None` (3.10+) is the modern spelling of `Optional[X]`; they mean
exactly the same thing.

```python
from typing import Union
def parse(value: Union[str, int]) -> int:   # pre-3.10 style; str | int is the 3.10+ equivalent
    return int(value)
```

## Generics and `TypeVar`

```python
from typing import TypeVar

T = TypeVar("T")

def first(items: list[T]) -> T:
    return items[0]
```

`TypeVar` says "whatever type goes in is the type that comes out" — `first([1, 2, 3])` is inferred
as returning `int`, `first(["a", "b"])` as returning `str`. Without it, `first`'s return type would
have to be `Any` or a specific type, losing the "same type in, same type out" relationship. Python
3.12 introduced simpler generic syntax:

```python
def first(items: list[T]) -> T:   # 3.12+: def first[T](items: list[T]) -> T:
    return items[0]

class Stack[T]:            # 3.12+ generic class syntax
    def __init__(self) -> None:
        self.items: list[T] = []

    def push(self, item: T) -> None:
        self.items.append(item)

    def pop(self) -> T:
        return self.items.pop()
```

## `Protocol` — structural typing

```python
from typing import Protocol

class Serializable(Protocol):
    def to_dict(self) -> dict: ...

def send(payload: Serializable) -> None:
    print(payload.to_dict())

class Order:                     # no inheritance from Serializable needed
    def to_dict(self) -> dict:
        return {"id": self.id}

send(Order())  # type-checks fine — "duck typing" made explicit and checkable
```

`Protocol` is Python's answer to "I don't care what class this is, I care what it can do" — it lets
mypy check duck-typed code (which Python encourages) without forcing an inheritance relationship.
This is the typed equivalent of Go's interfaces: **structural** typing (does it have the right
shape?) rather than **nominal** typing (does it explicitly inherit from the right class?).

## What mypy actually catches — and doesn't

Type hints are annotations only; **Python does not enforce them at runtime**:

```python
def add(a: int, b: int) -> int:
    return a + b

add("1", "2")   # runs fine at runtime -> "12" — Python never checks the hint
```

mypy is a **static analyzer** — it reads your code without running it and flags mismatches:

```bash
mypy myapp/
# myapp/billing.py:12: error: Argument 1 to "add" has incompatible type "str"; expected "int"
```

What mypy catches:
- Passing the wrong type to a function/method.
- Accessing an attribute that doesn't exist on the inferred type.
- Returning the wrong type from a function.
- `None`-safety issues (calling a method on something typed `X | None` without a None check first).

What mypy does **not** catch:
- Anything at runtime — a hint is purely documentation to the type checker; nothing stops
  `add("1", "2")` from actually running and returning `"12"`.
- Data coming from outside your type system unless you validate it — a `request.data["age"]` from a
  DRF view is `Any` until you actually parse/cast it; mypy has no way to know the JSON body matches
  your hints unless something (like Pydantic) validates it at the boundary.
- Dynamic attribute assignment, `**kwargs` shapes, monkey-patching, and most metaprogramming, unless
  carefully typed with `TypedDict`/`Protocol`/overloads.
- Logic bugs that are type-correct (e.g. `subtract` implemented as addition — both sides are
  `int`, mypy has nothing to say).

## Bridge to Pydantic

This is the key distinction to articulate clearly in an interview: **type hints + mypy are
compile-time-only** (well, "static analysis time" — Python has no compile step that enforces types)
— they never run and never validate real data. **Pydantic uses the same hint syntax but adds
runtime validation**: it actually inspects incoming data (e.g. a JSON request body) at runtime and
raises if it doesn't match, which is exactly what you need at an API boundary where the data is
untrusted user input, not something mypy already checked for you.

```python
# mypy-only: hints, never checked at runtime
def create_user(name: str, age: int) -> None: ...

# Pydantic: hints ARE the validation, checked every time an instance is built
from pydantic import BaseModel

class CreateUserRequest(BaseModel):
    name: str
    age: int

CreateUserRequest(name="Ann", age="30")   # OK — Pydantic coerces the numeric string "30" to int 30
CreateUserRequest(name="Ann", age="abc")  # raises ValidationError at runtime — "abc" isn't an int
```

See [dataclasses and Pydantic](11_dataclasses_and_pydantic.md) for the full comparison and when to
reach for each.

## Interview questions

**Q: Does adding type hints change how fast or how correctly your code runs?**
A: No — CPython ignores annotations at runtime (aside from making them available via
`__annotations__` for introspection). They only affect you if a tool like mypy, an IDE, or a
library like Pydantic/FastAPI reads and acts on them.

**Q: What's the difference between `Optional[str]` and `str | None`?**
A: Identical meaning; `str | None` is the 3.10+ syntax, `Optional[str]` (from `typing`) is the
older equivalent still common in codebases targeting 3.9 or earlier, or where union syntax isn't
used elsewhere.

**Q: When would you reach for `Protocol` instead of an abstract base class (ABC)?**
A: When you want to type-check duck-typed code without forcing implementers to explicitly inherit
from a base class — useful for third-party classes you don't control, or when you want structural
("has this method") rather than nominal ("is a subclass of this") typing.

**Q: If mypy passes clean, does that mean the code has no bugs?**
A: No — mypy only proves internal type consistency, not correctness of logic, not runtime behavior
on untrusted input, and not anything about code paths it can't statically reason about (e.g. heavy
use of `Any`, `# type: ignore`, or dynamic attributes silently defeats it).

**Q: How would you gradually introduce mypy into an existing large Django codebase with no
type hints?**
A: Start with `mypy --ignore-missing-imports` on a narrow, high-value module (e.g. billing logic),
use `# type: ignore[code]` sparingly with a reason, and use a per-module strictness config
(`[mypy-myapp.legacy.*] ignore_errors = True`) so you can ratchet strictness up module-by-module
rather than fixing the whole codebase at once.

## Exercises

1. Write a small function `safe_get(d: dict[str, T], key: str, default: T) -> T` typed with
   `TypeVar`, then run it through mypy with an intentionally wrong call (e.g. passing a `default`
   of a different type than the dict's values) and read the error message.
2. Define a `Protocol` called `HasArea` with an `area(self) -> float` method, write two unrelated
   classes (`Circle`, `Rectangle`) that satisfy it without inheriting from it, and write a
   `total_area(shapes: list[HasArea]) -> float` function that works on both.
