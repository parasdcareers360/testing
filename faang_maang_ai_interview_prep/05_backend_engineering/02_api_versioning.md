# API Versioning

> **Type:** Study notes

## Why interviewers ask this

Any API that survives contact with real clients needs to change its contract eventually, and real
clients (mobile apps in app-store review, third-party integrations, other internal services) can't
all upgrade at once. Versioning is where "designing an API" meets "operating an API in production" —
interviewers use it to see if you've actually shipped a breaking change to a live service, not just
built one from scratch.

## The three main strategies

### 1. URL path versioning — `/api/v1/orders/`, `/api/v2/orders/`

- **Pros**: explicit and visible in every request, trivial to route (different URL prefix can even
  hit a different codebase/deployment), easy to grep logs by version, cache-friendly (different URL
  = different cache key automatically).
- **Cons**: "the URL is supposed to identify a resource, not a contract version" (purist REST
  objection — in practice nobody cares), and it encourages whole-endpoint duplication rather than
  granular field-level evolution.
- **Verdict**: the most common in practice (Stripe, GitHub, Twitter/X all do this) because it's the
  easiest for client developers to reason about and debug. Default choice unless you have a reason
  not to.

### 2. Header versioning — `Accept: application/vnd.myapi.v2+json` or a custom `Api-Version: 2` header

- **Pros**: keeps URLs clean/stable (good if URLs are bookmarked, logged, or used as cache keys
  elsewhere), fits HTTP content-negotiation semantics correctly (`Accept` header is literally
  designed for "what representation do you want").
- **Cons**: invisible in browser address bars and casual `curl` testing (you forget the header,
  you silently get a default version), harder to test/debug quickly, some proxies/CDNs don't vary
  cache keys on custom headers by default (must configure `Vary` explicitly).
- **Verdict**: technically "more correct" REST but worse developer ergonomics — GitHub's API
  actually supports this alongside path versioning.

### 3. Query parameter versioning — `/orders?version=2`

- **Pros**: simple, doesn't require header manipulation, easy to test in a browser.
- **Cons**: easy to forget (defaults silently to latest/oldest, unclear which), pollutes query
  params that might already be used for filtering (see
  [Pagination, Filtering, Sorting, Search](04_pagination_filtering_sorting_search.md)), and mixing
  it with caching is messier than path-based (need to vary cache key on query param, which most
  caches do by default — but easy to get wrong with normalization).
- **Verdict**: weakest of the three for anything beyond an internal/prototype API — rarely the right
  default at a company with real external clients.

| Strategy | Visibility | Cache-friendliness | Client ergonomics | Common in practice |
|---|---|---|---|---|
| URL path | High | High (distinct URL) | High | Most common |
| Header | Low | Medium (needs `Vary`) | Medium | Common at scale (GitHub, some internal APIs) |
| Query param | Medium | Medium | Medium | Least common for public APIs |

## DRF's built-in versioning classes

DRF ships versioning as a pluggable `DEFAULT_VERSIONING_CLASS` — the resolved version shows up as
`request.version` in the view.

```python
# settings.py
REST_FRAMEWORK = {
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
    "DEFAULT_VERSION": "v1",
    "ALLOWED_VERSIONS": ["v1", "v2"],
    "VERSION_PARAM": "version",
}

# urls.py
urlpatterns = [
    path("api/<str:version>/orders/", OrderListView.as_view()),
]

# views.py
class OrderListView(APIView):
    def get(self, request, *args, **kwargs):
        if request.version == "v2":
            serializer_class = OrderSerializerV2
        else:
            serializer_class = OrderSerializerV1
        orders = Order.objects.all()
        return Response(serializer_class(orders, many=True).data)
```

Other built-in classes: `AcceptHeaderVersioning` (parses `Accept: application/json; version=2.0`),
`NamespaceVersioning` (uses separate URLconf namespaces per version — cleanest for large divergent
codebases), `HostNameVersioning` (`v2.api.example.com`), `QueryParameterVersioning`. Swapping
strategy is a one-line settings change plus matching URL/header wiring — the view-level
`request.version` API stays the same, which is worth mentioning if asked "how would you migrate
strategies."

In practice, for anything beyond a toy divergence, prefer **separate serializer classes per
version** (as above) or even **separate ViewSets per version module** (`api/v1/views.py`,
`api/v2/views.py`) over branching logic inside one view — branching logic inside a shared view is
where version-migration bugs live.

## Deprecating a version without breaking existing clients

1. **Ship v2 alongside v1** — never mutate v1's contract in place. v1 keeps behaving exactly as
   documented until it's formally sunset.
2. **Announce a deprecation window** with a concrete sunset date, communicated via docs, email to
   registered API consumers, and a response header:
   ```
   Deprecation: true
   Sunset: Sat, 01 Nov 2026 00:00:00 GMT
   Link: <https://api.example.com/docs/migration-v1-to-v2>; rel="deprecation"
   ```
   `Sunset` is an actual (draft) HTTP header standard for exactly this.
3. **Monitor usage of the old version** — log/metric every request by version so you know real
   traffic before killing it, not guessed traffic. Don't sunset a version with nonzero traffic
   without an explicit exception process.
4. **Return `410 Gone`** (not 404) once genuinely retired — tells the client "this used to exist and
   won't come back," distinct from "never existed."
5. **Avoid silent breaking changes within a version** — adding a new required field, renaming a
   field, or changing a field's type in v1 breaks clients without bumping the version number. Only
   *additive, backward-compatible* changes (new optional field, new endpoint) are safe to ship
   in-place; anything else requires a new version.

## Interview questions

**Q: URL path vs header versioning — which would you pick for a public API with third-party
integrators, and why?**
URL path — third-party developers copy-paste `curl` examples and read URLs in logs/dashboards;
requiring a specific header for correct behavior is an easy way to get silently-wrong-version bugs
reported against you. Header versioning is more defensible for an internal API where you control
all clients (e.g. via a shared SDK) and want clean URLs.

**Q: How do you avoid the situation where a client silently breaks because you changed a field type
in place?**
Treat any non-additive change (renamed/removed/retyped field, changed status code, changed error
shape) as a new version, full stop — never mutate an existing version's contract. Contract tests
against the serializer/schema in CI catch this before it ships.

**Q: You have a mobile app in app-store review that can't be forced to upgrade — how does that
constrain your versioning approach?**
It means you must support the old version indefinitely (or for a long tail) since you can't force
an update the way you can with a web client or internal service — this pushes toward URL path
versioning with a long deprecation window and monitoring actual old-version traffic before ever
considering a sunset date.

**Q: What's the risk of `QueryParameterVersioning` combined with caching?**
If a CDN/cache doesn't vary its cache key on that query param (or normalizes/strips unrecognized
params), you can serve a v1 response to a v2 request or vice versa. URL path versioning avoids this
because the version is baked into the cacheable URL itself.

## Exercise

1. Take the `OrderViewSet` from [REST API Design](01_rest_api_design.md) and split it into a v1
   (returns `total_cents` as an integer) and v2 (returns `total` as a formatted decimal string)
   using `URLPathVersioning` — write both serializers and the URL routing for `/api/v1/orders/` and
   `/api/v2/orders/`.
