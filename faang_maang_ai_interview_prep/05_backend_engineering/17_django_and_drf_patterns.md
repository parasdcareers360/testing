# Django & DRF Patterns

> **Type:** Study notes

## Why interviewers ask this

Django-specific questions at 3 YOE aren't testing whether you know the framework exists — they're
testing whether your code stays maintainable as an app grows. Fat-model-vs-service-layer, signal
overuse, and permission design are exactly the decisions that separate a Django app that's
pleasant to work in after 2 years from one nobody wants to touch. Expect interviewers (especially
at companies that use Django/DRF themselves) to probe for real opinions here, not textbook
definitions.

## Fat-model-thin-view vs. service layer

**Fat models** ("fat model, thin view/serializer"): business logic lives as methods on the model
itself. Good for logic that's genuinely intrinsic to the entity's own state.

```python
class Document(models.Model):
    status = models.CharField(max_length=20, default="uploaded")

    def mark_processing_failed(self, reason: str):
        if self.status not in ("processing",):
            raise InvalidStateTransition(f"Cannot fail from status={self.status}")
        self.status = "failed"
        self.failure_reason = reason
        self.save(update_fields=["status", "failure_reason"])
```

**Service layer**: business logic that spans multiple models, calls external systems, or
orchestrates a multi-step process lives in a plain function/class outside any single model —
often in a `services.py` per app.

```python
# documents/services.py
def submit_document_for_processing(*, document: Document, user: User) -> None:
    if not user.has_perm("documents.process_document", document):
        raise PermissionDenied

    document.status = "processing"
    document.save(update_fields=["status"])

    ProcessingAuditLog.objects.create(document=document, user=user, action="submitted")
    run_ocr_on_document.delay(document.id)
```

**When to use which**: logic that only needs the model's own fields and doesn't reach outside it
→ model method. Logic that touches multiple models, triggers a task, calls an external API, or
needs a permission check → service function, called from a thin view. The failure mode to name if
asked: models that grow 500-line God-object methods because *everything* got jammed into
`save()` overrides and model methods "for consistency" — that's over-applying fat models past the
point it helps. Views should mostly be: deserialize → call a service/model method → serialize the
result.

## DRF serializer validation patterns

```python
class DocumentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["title", "file", "category"]

    def validate_title(self, value):
        if Document.objects.filter(owner=self.context["request"].user, title=value).exists():
            raise serializers.ValidationError("You already have a document with this title.")
        return value

    def validate(self, attrs):
        if attrs["category"] == "invoice" and not attrs["file"].name.endswith(".pdf"):
            raise serializers.ValidationError("Invoices must be PDF files.")
        return attrs

    def create(self, validated_data):
        # keep the actual side effect in a service, not buried in the serializer
        return submit_document_for_processing(
            **validated_data, user=self.context["request"].user
        )
```

Key habits: field-level `validate_<field>` for single-field rules, `validate()` for cross-field
rules, pass `context={"request": request}` from the view so serializers can access the
authenticated user without reaching for a global. Keep `create()`/`update()` thin — delegate to a
service function rather than writing multi-step orchestration logic inline inside the serializer.

## Custom permission classes

```python
class IsDocumentOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner_id == request.user.id

class IsDocumentOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner_id == request.user.id
```

`has_permission` runs before the object is fetched (view-level: "can this user hit this endpoint
at all"); `has_object_permission` runs per-object (only for detail views/`get_object()` calls —
DRF does **not** call it automatically for list views, a common gotcha). This is where you close
the IDOR gap mentioned in
[`15_security_owasp_validation_secrets_cors_csrf.md`](15_security_owasp_validation_secrets_cors_csrf.md) —
authentication alone ("is there a valid user") is not authorization ("is *this* user allowed to
touch *this* object").

## Signals — and why overusing them is a real gotcha

```python
@receiver(post_save, sender=Document)
def notify_on_document_upload(sender, instance, created, **kwargs):
    if created:
        send_upload_notification.delay(instance.id)
```

Signals decouple the sender from the receiver — the `Document` model doesn't need to know
notifications exist. That's the appeal, and it's also the trap: **the side effect becomes
invisible from the call site.** Someone reading `Document.objects.create(...)` in a view or a
data migration has no idea a notification just fired, an audit log got written, and a Celery task
got queued, unless they already know to go search for `post_save` receivers on `Document`
somewhere else in the codebase. This gets worse with chained signals (signal A triggers a save
that fires signal B) — debugging becomes "trace an invisible call graph across files with no
stack-trace-visible connection." A practical rule to state in an interview: use signals for
genuinely cross-cutting, optional concerns (cache invalidation, audit logging that truly must
apply no matter how the save happened, including from Django admin or a data migration) — use an
explicit service-function call for anything that's core business logic and should be visible at
the call site, especially anything another engineer debugging a production issue would need to
find quickly.

## Middleware

Runs on every request/response, before/after the view — the right place for genuinely global,
request-agnostic concerns: authentication token parsing, request ID/trace ID injection (see
[`16_monitoring_logging_metrics_tracing.md`](16_monitoring_logging_metrics_tracing.md)), timing,
CORS headers.

```python
class RequestTimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.monotonic()
        response = self.get_response(request)
        duration = time.monotonic() - start
        response["X-Response-Time-Ms"] = str(int(duration * 1000))
        if duration > 1.0:
            logger.warning("slow_request", extra={"path": request.path, "duration": duration})
        return response
```

Keep middleware cheap and dependency-free — it runs on *every* request including ones that will
404 or fail auth, so an expensive DB query in middleware taxes traffic that shouldn't have reached
your app logic at all.

## `select_related`/`prefetch_related` — the N+1 problem

The most common Django performance interview question. `select_related` (SQL `JOIN`, for
FK/OneToOne) and `prefetch_related` (separate query + Python-side join, for reverse FK/M2M) both
exist to avoid firing one query per related object in a loop:

```python
# N+1: one query for documents, then one more query PER document for .owner
for doc in Document.objects.all():
    print(doc.owner.email)

# Fixed: one query total, owner joined in
for doc in Document.objects.select_related("owner"):
    print(doc.owner.email)
```

Full trade-offs, `Prefetch()` objects, and query-plan-level detail live in
[`../04_sql_and_databases/14_orm_tradeoffs_and_django_orm_optimization.md`](../04_sql_and_databases/14_orm_tradeoffs_and_django_orm_optimization.md) —
worth reading alongside this file since the two overlap heavily in real interviews.

## Interview Q&A

**Q: When do you reach for a service layer instead of putting logic on the model?**
A: When the logic spans multiple models, needs to call something external (queue a task, hit an
API), or needs request context like the acting user for a permission check. Model methods are
great for logic that's purely about that model's own state transitions; anything that
orchestrates multiple things belongs in an explicit service function so it's visible and testable
on its own.

**Q: What's wrong with putting an email-send inside a `post_save` signal on `Order`?**
A: It's invisible at the call site — anyone creating/saving an `Order` anywhere (a view, a
management command, a data migration, Django admin) triggers the email without it being obvious
from reading that code. It also runs synchronously inside the save unless you explicitly hand it
off to a task, and debugging "why did this email send twice" means hunting across the codebase for
receivers instead of reading one function. I'd make this an explicit call in the service function
that actually creates the order, wrapped in `transaction.on_commit()` if it needs to fire after
the DB transaction commits, dispatched as a Celery task either way.

**Q: `has_object_permission` isn't being enforced on your list endpoint — why?**
A: DRF only calls `has_object_permission` when the view actually fetches a single object via
`get_object()` (retrieve/update/destroy). List views return a queryset directly and never call
`get_object()`, so object-level permission checks there have to happen by filtering the queryset
itself (e.g. `Document.objects.filter(owner=request.user)` in `get_queryset()`), not by relying on
the permission class alone.

## Hands-on exercise

1. Refactor a Django view that currently does validation, a multi-step state change across two
   models, and a Celery task dispatch all inline in the view, into: a thin DRF serializer for
   validation, a service function for orchestration, and a thin view that just wires them
   together.
2. Find (or write) a `post_save` signal that does something non-trivial (e.g. sends a
   notification), and rewrite it as an explicit call inside the relevant service function.
   Articulate out loud what became easier to trace.
