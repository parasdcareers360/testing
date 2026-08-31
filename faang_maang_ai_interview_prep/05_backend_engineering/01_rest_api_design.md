# REST API Design

> **Type:** Study notes

## Why interviewers ask this

Almost every backend/system-design round eventually asks you to sketch an API. Interviewers use
this to check whether you think in terms of **resources and state**, not just "write a function
that does X" — sloppy REST design (verbs in URLs, wrong status codes, inconsistent nesting) is a
fast, cheap signal that someone hasn't designed APIs that other teams actually had to consume.

## What makes an API "RESTful" vs just "an HTTP API"

Slapping JSON over HTTP endpoints isn't REST. Roy Fielding's constraints that actually matter in
interviews:

- **Resource-oriented URLs.** A URL identifies a *thing* (`/orders/42`), not an action
  (`/getOrder?id=42` or `/createOrder`). The HTTP verb carries the action.
- **Uniform interface.** The same verb means the same thing everywhere — `GET` never mutates,
  `DELETE` always removes, `PUT` always replaces.
- **Statelessness.** Each request carries everything needed to process it (auth token, pagination
  cursor, etc.) — the server holds no per-client session state between requests. This is why JWTs
  fit REST better than server-side sessions at scale (see
  [Auth: JWT, OAuth, RBAC](03_auth_jwt_oauth_rbac.md)).
- **HATEOAS** (hypermedia as the engine of application state) — technically part of "true" REST
  (responses include links to related actions/resources) but almost nobody implements this in
  practice. Know the term, mention that most production "REST" APIs are pragmatically RPC-over-HTTP
  with resource URLs, not full HATEOAS. Saying this out loud signals real experience.

In practice, "RESTful" in an interview means: resource nouns in the URL, correct verb semantics,
correct status codes, and statelessness. That's the bar graders actually check.

## Resource-oriented URLs and HTTP verbs

| Verb | Semantics | Idempotent? | Safe (no side effects)? |
|---|---|---|---|
| `GET` | Read a resource or collection | Yes | Yes |
| `POST` | Create a resource / non-idempotent action | No | No |
| `PUT` | Replace a resource entirely | Yes | No |
| `PATCH` | Partially update a resource | No (usually treated as idempotent in practice) | No |
| `DELETE` | Remove a resource | Yes | No |

"Idempotent" means calling it N times has the same effect as calling it once — `DELETE /orders/42`
twice still leaves the order deleted (the second call just 404s or no-ops). `POST /orders` twice
creates two orders — that's why idempotency keys matter for payment/order creation (see
[Idempotency and Retries](09_idempotency_and_retries.md)).

```
GET    /orders              # list
POST   /orders               # create
GET    /orders/{id}          # retrieve
PUT    /orders/{id}          # full replace
PATCH  /orders/{id}          # partial update
DELETE /orders/{id}          # delete
GET    /orders/{id}/items    # nested collection under a resource
```

## Status codes that actually matter

| Code | Use it for |
|---|---|
| 200 | Successful `GET`/`PUT`/`PATCH`, or `POST` that doesn't create a resource (e.g. an action endpoint) |
| 201 | Successful `POST` that created a resource — return the resource + `Location` header |
| 204 | Successful `DELETE`, or any response with no body |
| 400 | Malformed request (bad JSON, failed validation) |
| 401 | Not authenticated (missing/invalid credentials) |
| 403 | Authenticated, but not authorized for this resource |
| 404 | Resource doesn't exist |
| 409 | Conflict (e.g. unique constraint violation, optimistic-lock version mismatch) |
| 422 | Semantically invalid request (well-formed JSON, but business-rule validation failed) — DRF returns this via `ValidationError` |
| 429 | Rate limited (see [Rate Limiting](05_rate_limiting.md)) |
| 500 | Unhandled server error |

Interviewers specifically probe **401 vs 403** — 401 means "I don't know who you are," 403 means
"I know who you are, and you can't do that." Mixing these up is a common tell of someone who's
copy-pasted status codes without understanding them.

## DRF example: ViewSet + Serializer

```python
# serializers.py
from rest_framework import serializers
from .models import Order

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id", "customer", "status", "total_cents", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_total_cents(self, value):
        if value < 0:
            raise serializers.ValidationError("total_cents cannot be negative.")
        return value


# views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Order
from .serializers import OrderSerializer

class OrderViewSet(viewsets.ModelViewSet):
    """
    Maps to:
      GET/POST      /orders/
      GET/PUT/PATCH/DELETE /orders/{pk}/
      POST          /orders/{pk}/cancel/   (custom action below)
    """
    queryset = Order.objects.select_related("customer").all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # scope to the requesting user unless staff — never trust a client-supplied filter for this
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(customer=self.request.user)
        return qs

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status == "shipped":
            return Response(
                {"detail": "Cannot cancel an order that has already shipped."},
                status=status.HTTP_409_CONFLICT,
            )
        order.status = "cancelled"
        order.save(update_fields=["status"])
        return Response(OrderSerializer(order).data)
```

`@action(detail=True, methods=["post"])` is the DRF-idiomatic escape hatch for actions that don't
map cleanly to CRUD (`cancel`, `resend-invoice`, `approve`) — it's a `POST` on a sub-resource path
(`/orders/42/cancel/`), not a verb in the base URL.

## Common design mistakes

1. **Verbs in URLs**: `/getUserOrders`, `/createOrder` instead of `GET /users/{id}/orders`,
   `POST /orders`. The verb belongs to HTTP, not the path.
2. **Wrong status codes**: returning `200` for every response (including errors, with the error
   stuffed in the body) — clients can't distinguish success from failure without parsing the body,
   which breaks caching, retries, and monitoring/alerting that key off status code.
3. **Over-nesting resources**: `/customers/1/orders/42/items/7/discounts/3` — beyond 2 levels,
   nesting becomes unmaintainable and every level requires re-validating the parent chain. Prefer
   flattening: `GET /order-items/7/discounts` or give sub-resources their own top-level collection
   with a filter (`GET /discounts?order_item=7`).
4. **Leaking DB implementation** in the URL/response shape (auto-increment IDs that reveal row
   counts, internal foreign key names) — use UUIDs or slugs for public-facing resources when this
   matters.
5. **Inconsistent envelope**: some endpoints return a bare list, others wrap in `{"data": [...]}`,
   others `{"results": [...]}`. Pick one convention (DRF's paginated response format is a reasonable
   default) and apply it everywhere.
6. **Ignoring idempotency on `POST`**: retried requests (client timeout + retry, mobile app on flaky
   network) create duplicate resources. See [Idempotency and Retries](09_idempotency_and_retries.md).

## Interview questions

**Q: What's the difference between `PUT` and `PATCH`?**
`PUT` replaces the entire resource — fields you omit are treated as unset/reset to default.
`PATCH` updates only the fields provided. In DRF, `ModelViewSet` gives you both for free; the
serializer's `partial=True` flag (set automatically for `PATCH`) makes all fields optional for that
request.

**Q: Why is `GET` required to be safe and idempotent — what breaks if it isn't?**
Browsers, proxies, and CDNs assume `GET` has no side effects and will prefetch, retry, or cache it
silently. A `GET` that deletes a record (yes, this happens with careless "delete via link" designs)
can get triggered by a crawler or browser prefetch, deleting data nobody intended to delete.

**Q: How would you version this API without breaking existing mobile clients?**
See [API Versioning](02_api_versioning.md) — short answer: URL path versioning (`/api/v1/orders/`)
is the most explicit and easiest for clients to reason about, at the cost of some code duplication.

**Q: A `POST /orders/{id}/cancel` vs `PATCH /orders/{id}` with `{"status": "cancelled"}` — which is
more RESTful, and does it matter?**
`PATCH` with a status field is more "pure REST" (state transition via resource update), but a
custom action endpoint is often more practical when the transition has side effects (refund
processing, inventory release) that don't map cleanly to "just changing a field." In interviews,
either answer is fine if you can justify the side-effect handling — pick the custom action when the
transition needs its own validation/side effects, and say so.

## Exercise

1. Design the resource URLs, verbs, and status codes for a simplified GitHub-issues API: creating
   an issue, listing issues with a status filter, closing an issue, and adding a comment to an
   issue. Then write the DRF `ViewSet` + `@action` for "close issue" following the pattern above.
