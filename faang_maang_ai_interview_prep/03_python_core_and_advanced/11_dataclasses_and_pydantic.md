# Dataclasses and Pydantic

> **Type:** Study notes

## Why interviewers ask this

Plain classes with hand-written `__init__`/`__eq__`/`__repr__` are boilerplate-heavy; interviewers
want to see you know the modern, idiomatic way to define data-holding classes, and — more
importantly for a DRF candidate — that you know *when* a dataclass is enough and when you actually
need runtime validation (Pydantic). This is a direct extension of
[type hints and mypy](09_type_hints_and_mypy.md): dataclasses use type hints for structure only,
Pydantic uses the same hint syntax but *enforces* it at runtime, which is exactly what a DRF
serializer does for incoming request data.

## `@dataclass` basics

```python
from dataclasses import dataclass, field

@dataclass
class Point:
    x: float
    y: float

p1 = Point(1.0, 2.0)
p2 = Point(1.0, 2.0)
print(p1)        # Point(x=1.0, y=2.0)  -- auto-generated __repr__
print(p1 == p2)  # True                 -- auto-generated __eq__ (field-by-field)
```

`@dataclass` auto-generates `__init__`, `__repr__`, and `__eq__` from the annotated fields —
exactly the boilerplate you'd otherwise write by hand.

### Mutable default values need `field(default_factory=...)`

```python
@dataclass
class Order:
    id: int
    items: list[str] = field(default_factory=list)   # NOT items: list[str] = []
    metadata: dict = field(default_factory=dict)
```

`items: list = []` would raise `ValueError` at class-definition time in a dataclass (unlike a
regular function default, where a mutable default silently becomes a shared trap across calls) —
dataclasses catch this specific footgun for you and force `default_factory` instead.

### `frozen=True` — immutability

```python
@dataclass(frozen=True)
class Money:
    amount: int
    currency: str

m = Money(100, "USD")
m.amount = 200   # raises dataclasses.FrozenInstanceError
```

`frozen=True` makes instances hashable (if all fields are hashable) and prevents attribute
reassignment after `__init__` — useful for value objects that should never change after creation,
like a `Money` amount or a coordinate, and required if you want to use instances as dict keys or
put them in a `set`.

### `__post_init__` — validation/derived fields after construction

```python
@dataclass
class Rectangle:
    width: float
    height: float
    area: float = field(init=False)   # not a constructor param; computed after

    def __post_init__(self):
        if self.width <= 0 or self.height <= 0:
            raise ValueError("width and height must be positive")
        self.area = self.width * self.height

r = Rectangle(3, 4)
print(r.area)   # 12
```

`__post_init__` runs automatically right after the generated `__init__` — the natural place for
validation logic or computing a derived field, but note this is **not the same as real runtime type
validation**: `Rectangle(width="3", height=4)` still constructs fine (no `TypeError`) because
dataclasses don't check that the value passed actually matches the annotated type — only mypy would
catch that mismatch, and only statically, not at runtime.

## When a dataclass is enough vs. when you need Pydantic

A dataclass is a **plain container with structure** — it organizes fields and gives you
`__init__`/`__repr__`/`__eq__` for free, but it does not validate or coerce data at runtime beyond
what you write yourself in `__post_init__`.

Reach for **Pydantic** instead when:
- Data is coming from an **untrusted external source** (API request body, uploaded file, message
  queue payload) and needs to be validated/coerced at the boundary, not just structured internally.
- You need **automatic type coercion** (a query param arrives as `"30"`, you want it as `int(30)`).
- You need **serialization** to/from JSON built in (`.model_dump()`, `.model_dump_json()`,
  `.model_validate_json()`) without writing it by hand.
- You want **field-level validators** with clear, structured error messages you can return directly
  in an API response — this is the same job a DRF `Serializer` does, and if you've written DRF
  serializers, Pydantic models will feel immediately familiar.

Use a plain `@dataclass` for **internal** data structures — the return type of a service function,
a value object passed between layers of your own code you already trust — where you don't need
validation or JSON (de)serialization, just structure and equality.

## Pydantic v2 example

```python
from pydantic import BaseModel, field_validator, EmailStr
from datetime import date

class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    birth_date: date
    referral_code: str | None = None

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name cannot be blank")
        return v.strip()

    @field_validator("birth_date")
    @classmethod
    def must_be_adult(cls, v: date) -> date:
        age = (date.today() - v).days // 365
        if age < 18:
            raise ValueError("must be at least 18 years old")
        return v

# valid input -> validated, coerced instance
req = SignupRequest(name="  Ann  ", email="ann@example.com", birth_date=date(1990, 1, 1))
print(req.name)               # "Ann" (stripped by the validator)
print(req.model_dump())       # {'name': 'Ann', 'email': 'ann@example.com', ...}
print(req.model_dump_json())  # '{"name":"Ann","email":"ann@example.com",...}'

# invalid input -> raises pydantic.ValidationError with structured, per-field errors
SignupRequest(name="Bob", email="not-an-email", birth_date=date(2020, 1, 1))
```

The failure raises `ValidationError` with a list of per-field problems (which field, what went
wrong) — this is exactly the shape of error you'd hand back as a 400 response body, the same job
`serializer.errors` does in DRF after `serializer.is_valid()` fails.

## Interview questions

**Q: What's the core difference between a `@dataclass` and a Pydantic `BaseModel`?**
A: A dataclass only structures data and generates boilerplate (`__init__`, `__repr__`, `__eq__`);
it does not validate types at runtime. A Pydantic model uses the same annotation syntax but
actively validates and coerces values when an instance is constructed, and raises `ValidationError`
with structured field-level errors when validation fails.

**Q: If dataclasses don't validate types, what stops someone from passing the wrong type?**
A: Nothing, at runtime — only a static type checker like mypy catches it, and only if you actually
run mypy as part of CI. If you need real enforcement (e.g. data from a request body), a dataclass
alone is the wrong tool; that's exactly the gap Pydantic fills.

**Q: How does this map to what you already do in DRF?**
A: A DRF `Serializer`/`ModelSerializer` is doing the same job as a Pydantic model: declaring
expected fields with types, validating/coercing incoming request data, producing structured errors
on failure (`serializer.errors`), and serializing model instances back to JSON
(`serializer.data`) — Pydantic is the framework-agnostic version of that same pattern, which is why
FastAPI uses it in place of DRF serializers.

**Q: Why does `field(default_factory=list)` exist instead of just `field: list = []`?**
A: Because a plain mutable default in a dataclass would be shared across every instance that
doesn't explicitly pass a value (the same classic Python "mutable default argument" trap as
`def f(x=[])`) — dataclasses actually detect this specific case and raise at class-definition time
rather than let it become a hard-to-trace shared-state bug, forcing you to use a factory that
creates a fresh object per instance instead.

**Q: When would you deliberately choose a dataclass over Pydantic even in a Django project?**
A: For internal, already-trusted data passed between your own service-layer functions — e.g. the
return value of a pricing calculation, a value object passed from one internal function to
another — where you want structure and equality but the extra validation/serialization machinery
is unnecessary overhead and an unnecessary dependency for code that never touches untrusted input.

## Exercises

1. Write a `@dataclass(frozen=True)` called `Coordinates` with `lat: float` and `lng: float`, add a
   `__post_init__` that raises `ValueError` if `lat` isn't in `[-90, 90]` or `lng` isn't in
   `[-180, 180]`, and confirm instances are hashable (put two in a `set`).
2. Convert the `SignupRequest` Pydantic model above into an equivalent DRF `Serializer` (using
   `serializers.CharField`, `EmailField`, `DateField`, and a custom `validate_birth_date` method) —
   compare how much boilerplate each approach needs for the same validation rules.
