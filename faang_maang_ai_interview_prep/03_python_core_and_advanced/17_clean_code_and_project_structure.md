# Clean Code and Project Structure

> **Type:** Study notes

## Why interviewers ask this

Live-coding and take-home rounds grade code quality directly — naming, function size, and where
logic lives are visible signal in real time, unlike algorithmic correctness which you can eventually
get to via debugging. For a Django/DRF candidate specifically, "where would this logic live" (model
method? serializer? view? a service function?) is a very common design-adjacent question, because
"fat models, fat views, and no service layer" is the most common real-world Django anti-pattern
interviewers have seen candidates produce.

## Project layout conventions

**`src/` layout vs flat layout.** Flat layout puts the importable package directly at the repo
root (`myapp/`, `setup.py` or `pyproject.toml`, `tests/` all siblings). `src/` layout nests the
package under `src/myapp/`. The practical reason to prefer `src/` layout for a *library/package*
you intend to `pip install`: it prevents accidentally importing the uninstalled local source
instead of the installed package during tests (a flat layout can silently pass tests against
stale local code because the current directory is importable by default). For a Django *project*
(as opposed to a standalone library), the Django convention — `manage.py`, apps as top-level
packages (`orders/`, `users/`, `payments/`) — is the norm and fighting it adds friction for no
benefit; know both, apply the one that fits what you're building.

```
# Django project - conventional flat-ish layout
myproject/
├── manage.py
├── myproject/          # settings package
│   ├── settings/
│   │   ├── base.py
│   │   ├── local.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── orders/              # one app per bounded domain concept
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── services.py      # business logic that doesn't belong in a model/serializer/view
│   ├── tasks.py          # Celery tasks
│   ├── urls.py
│   └── tests/
├── users/
└── requirements/
    ├── base.txt
    └── local.txt
```

**`__init__.py` purpose.** Marks a directory as a regular package (not strictly required for
namespace packages since Python 3.3+, but still the explicit, conventional choice for application
code) and is a natural place for controlling what a package exports (`__all__`) or wiring
package-level setup — e.g. Django's `default_app_config` pattern historically, or re-exporting a
public API surface (`from .client import OCRClient` so callers do `from myapp.ocr import
OCRClient` instead of reaching into a submodule). Keep it near-empty otherwise — real logic
belongs in named modules, not accumulating in `__init__.py`, which makes it hard to find later.

## Separating concerns in a Django/DRF project

The most common real-world anti-pattern this candidate should be ready to discuss: **fat views**
(business logic, validation, and multiple side effects all inline in the view method) or the
opposite failure, **everything crammed into serializers/model methods** until they're doing far
more than serialization/persistence. The fix interviewers want to hear articulated is an explicit
**service layer** — plain functions (or small classes) that hold business logic, called by thin
views and thin serializers.

```python
# Anti-pattern: fat view — business logic, side effects, and HTTP handling all tangled together
class CreateOrderView(APIView):
    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        # business logic inline: inventory check, payment call, email, all in the view
        if not check_inventory(order.items):
            order.delete()
            return Response({"error": "out of stock"}, status=400)
        try:
            charge_payment(order.total, request.user.payment_method)
        except PaymentError:
            order.delete()
            return Response({"error": "payment failed"}, status=402)
        send_order_confirmation_email(order)
        return Response(OrderSerializer(order).data, status=201)
```

```python
# Better: service layer holds the business logic, view stays thin (HTTP concerns only)
# orders/services.py
class OutOfStockError(Exception):
    pass

def create_order(*, user, items) -> Order:
    if not check_inventory(items):
        raise OutOfStockError("one or more items unavailable")
    order = Order.objects.create(user=user, items=items)
    try:
        charge_payment(order.total, user.payment_method)
    except PaymentError:
        order.delete()
        raise
    send_order_confirmation_email(order)
    return order

# orders/views.py
class CreateOrderView(APIView):
    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            order = create_order(user=request.user, **serializer.validated_data)
        except OutOfStockError:
            return Response({"error": "out of stock"}, status=400)
        except PaymentError:
            return Response({"error": "payment failed"}, status=402)
        return Response(OrderSerializer(order).data, status=201)
```
Why this is better: `create_order` is directly unit-testable without spinning up the HTTP layer
(`APIClient`), reusable from a management command or Celery task without duplicating logic, and
the view's job is legible at a glance — parse input, call the service, translate exceptions to HTTP
status codes. This isn't dogma to apply everywhere (a trivial CRUD view with no business logic
doesn't need a service function wrapping `Model.objects.create(**data)`) — the heuristic is: **if a
view does more than "validate input, call one thing, shape output," extract the "one thing" into a
service function.**

The same reasoning applies to models and serializers: a model method like `order.total_with_tax()`
is fine (data-derived, no side effects, belongs with the data); a model method that calls an
external payment API is not (side effects and I/O don't belong on a model — they belong in a
service, both for testability and because model code runs in unexpected places — admin, shell,
migrations — where you don't want network calls firing).

## Naming and function-size heuristics

These are judged **live** in interviews far more than candidates expect — an interviewer watching
you code sees every name you choose and every function you write in real time.

- **Names should answer "what," not restate the type.** `user_list` (redundant) vs `active_users`
  (says what it actually is). `data`/`obj`/`temp`/`result` as a *final* variable name is a signal
  you haven't thought about what the value represents — fine as a scratch name mid-refactor, not
  fine left in.
- **Function size**: if you can't describe what a function does in one sentence without "and," it's
  doing too much and is a candidate for splitting. A rough physical heuristic — a function you can't
  see in full on one screen without scrolling is worth a second look, though this is a smell, not a
  hard rule.
- **Boolean names read as questions**: `is_active`, `has_permission`, `should_retry` — not `active`,
  `permission_flag`, `retry`. This is a small thing interviewers notice because it costs nothing and
  most candidates still get it wrong under pressure.
- **One level of abstraction per function.** A function that mixes "loop over orders, compute tax,
  call the payment gateway, format a response dict" is mixing orchestration with low-level detail —
  extract the tax computation and the response formatting so the top-level function reads as a
  short list of named steps.
- **Say your naming choices out loud in an interview.** "I'm calling this `pending_orders` instead
  of `orders2` because..." costs a few seconds and is exactly the signal graders are listening for.

## Avoiding premature abstraction

The counter-failure mode to fat views/models is over-engineering: introducing an interface,
abstract base class, or plugin/strategy pattern for a case with exactly one implementation and no
concrete plan for a second one. This adds indirection that costs real reading effort for zero
present benefit, and is a common self-inflicted wound in take-homes where a candidate builds a
generic `AbstractPaymentProcessor` framework for a task that only ever calls one payment provider.

Guidance to state in an interview: **abstract when you have a second concrete case, not in
anticipation of one.** Django/DRF itself nudges toward reasonable defaults here — a plain function
or a small class is enough until a real second implementation shows up; refactoring a working
concrete function into an abstraction later, once the shape of the *actual* variation is known, is
cheaper than guessing the right abstraction upfront and being wrong. This connects directly to
[SOLID / Composition vs Inheritance](10_oop_solid_composition_vs_inheritance.md) — favor composition
and concrete code until duplication or a genuine second variant actually appears.

## Interview questions

**Q1: Where should business logic live in a Django/DRF project — model, serializer, or view?**
A: None of them exclusively — simple, data-derived logic with no side effects can live on the
model; input shaping/validation lives on the serializer; orchestration (calling a service, mapping
result to a response) lives on the view. Anything with real business logic or side effects
(external API calls, multi-step operations, things that need to be reused outside the HTTP layer)
belongs in an explicit service function, called by a thin view.

**Q2: What's wrong with a 150-line view method that does validation, three DB writes, and two
external API calls inline?**
A: It's hard to test without spinning up the full HTTP stack, hard to reuse from a different entry
point (a management command, a Celery task), and hard to read since HTTP concerns and business
logic are tangled. Extracting the business logic into a service function fixes all three — the view
becomes "validate, call, respond."

**Q3: When would you introduce an abstract base class or interface for a service integration, and
when is that premature?**
A: Introduce it once there are two real concrete implementations sharing a contract (e.g. two OCR
providers actually being swapped between). Building the abstraction for a single implementation
"in case we need to swap providers later" is premature — it adds indirection for a scenario that
may never materialize, and a real second case usually reveals a different abstraction than the
guessed one anyway.

**Q4: How do you decide when a function needs to be split into smaller functions?**
A: If it can't be summarized in one sentence without "and," or it mixes levels of abstraction
(high-level orchestration next to low-level detail like manual string parsing), it's a candidate to
split. The test is readability and testability, not an arbitrary line count — a 40-line function
doing one cohesive thing can be fine; a 15-line function doing three unrelated things isn't.

## Exercises

1. Take a view (real or hypothetical) that does validation + a DB write + an external API call
   inline, and refactor it into a thin view calling a service function, matching the
   `create_order`/`CreateOrderView` split above. Write one unit test for the service function that
   doesn't touch the HTTP layer at all.
2. Pick 5 variable/function names from code you've written recently and rewrite any that restate
   their type, are a vague `data`/`result`/`obj`, or are a non-question boolean name — say out loud
   why each new name is better.
