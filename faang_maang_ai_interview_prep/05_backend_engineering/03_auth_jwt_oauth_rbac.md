# Auth: Sessions, JWT, OAuth2, RBAC

> **Type:** Study notes

## Why interviewers ask this

Auth is where "I can build CRUD endpoints" becomes "I understand what happens when someone
malicious hits my API." It's one of the highest-signal system-design/backend topics because it
touches security, statelessness, and distributed-systems trade-offs (do multiple services trust one
token, or does each check a shared session store?) all at once — and it's an area where 3 YOE
candidates are expected to have real opinions, not just definitions.

## Session auth vs token auth vs JWT

| | Session auth | Opaque token auth | JWT |
|---|---|---|---|
| Where state lives | Server (session store, e.g. Redis/DB) | Server (token → user mapping in DB/cache) | Encoded *in* the token itself |
| Revocation | Instant (delete session server-side) | Instant (delete token record) | Hard — token is valid until expiry unless you maintain a blocklist (defeats the point) |
| Scales across services? | Needs shared session store | Needs shared token store | Yes — any service with the public key/secret can verify independently, no shared store needed |
| Payload readable by client? | No (opaque cookie/ID) | No (opaque string) | Yes — base64, **not encrypted**, just encoded |
| Typical transport | Cookie | Header (`Authorization: Token ...`) | Header (`Authorization: Bearer ...`) |

The core trade-off: session/opaque-token auth gives you instant revocation at the cost of a
stateful lookup on every request (shared store = coupling between services). JWT gives you
stateless, horizontally-scalable verification (any microservice can verify a JWT locally with just
the public key — no round trip to an auth service) at the cost of hard revocation — this is exactly
why JWTs use **short expiry + refresh tokens** instead of long-lived tokens (below).

## JWT structure — and why the payload isn't trustworthy on its own

A JWT is three base64url-encoded segments joined by dots: `header.payload.signature`.

```
eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo0MiwiZXhwIjoxNzI5...  .   4f8a2b1c9d...
     header                    payload                       signature
```

- **Header**: algorithm + token type, e.g. `{"alg": "HS256", "typ": "JWT"}`.
- **Payload**: claims — `user_id`, `exp` (expiry), `iat` (issued-at), custom claims like `role`.
  **This is just base64, not encryption.** Anyone can decode it and read it (`base64 -d` on the
  middle segment) — never put secrets (passwords, raw PII beyond what's needed) in a JWT payload.
- **Signature**: `HMACSHA256(base64(header) + "." + base64(payload), secret)` for symmetric
  algorithms (HS256), or an RSA/ECDSA private-key signature for asymmetric (RS256/ES256).

**Why you can't "just trust" the payload without verifying the signature**: decoding the payload
tells you what the token *claims*, not whether it's genuine. An attacker can hand-craft a JWT with
`{"user_id": 1, "role": "admin"}` in the payload trivially — the signature is the only thing proving
the payload wasn't tampered with since a trusted party issued it. **Always verify the signature
(and `exp`, and `alg` matches what you expect — the classic `alg: none` attack tricks a naive
verifier into skipping signature checks entirely) before trusting any claim in the payload.**
Libraries like `PyJWT` / DRF SimpleJWT do this for you — the danger is code that manually
`base64.decode()`s a token to "read the user id" without calling `jwt.decode(..., verify=True)`.

```python
import jwt
from django.conf import settings

# WRONG — decodes without verifying signature, trusts attacker-controlled data
payload = jwt.decode(token, options={"verify_signature": False})  # never do this in an auth path

# RIGHT — verifies signature + expiry before trusting any claim
try:
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
except jwt.ExpiredSignatureError:
    raise AuthenticationFailed("Token expired.")
except jwt.InvalidTokenError:
    raise AuthenticationFailed("Invalid token.")
user_id = payload["user_id"]  # only trustworthy after verification above
```

## Access token vs refresh token pattern

- **Access token**: short-lived (minutes to ~1 hour), sent on every API request, JWT (stateless,
  fast to verify). Short lifetime limits the blast radius if it's stolen (XSS, log leak).
- **Refresh token**: long-lived (days to weeks), used *only* to obtain a new access token, stored
  more carefully (httpOnly cookie or secure storage, not `localStorage`), and — critically — **is
  checked against a server-side store**, so it *can* be revoked (logout, compromised-account
  response) even though the access tokens it minted can't be individually revoked before they
  expire.
- Rotating refresh tokens (issue a new refresh token on every use, invalidate the old one) limits
  damage if a refresh token is stolen and replayed — a reused old refresh token signals theft and
  can trigger revoking the whole token family.

```python
# DRF SimpleJWT-style flow (conceptually — the library handles the mechanics)
# POST /api/token/            {username, password} -> {access, refresh}
# POST /api/token/refresh/    {refresh}             -> {access}
# access: 5-15 min TTL, refresh: 7-30 day TTL, refresh rotation + blocklist enabled
```

## OAuth2 grant types (conceptual)

OAuth2 solves a different problem than "log a user into my app": **delegated authorization** — how
does app A get limited access to a resource on behalf of a user, without ever seeing the user's
password for the resource owner (e.g. "let this app read your Google Calendar").

- **Authorization Code flow** (the standard for anything with a backend): user is redirected to the
  provider (Google/GitHub), logs in there, provider redirects back with a short-lived `code`, your
  **backend** (never the browser) exchanges that code + a client secret for tokens via a
  server-to-server call. The client secret never touches the browser, so a stolen redirect URL alone
  isn't enough to get tokens.
- **Authorization Code + PKCE**: same flow, but for clients that *can't* keep a secret (mobile apps,
  SPAs) — a dynamically generated `code_verifier`/`code_challenge` pair replaces the static client
  secret as proof that the app exchanging the code is the same one that started the flow. This is
  now the recommended flow for public clients.
- **Implicit flow** (deprecated/discouraged): tokens were returned directly in the redirect URL
  fragment, with no backend exchange step — meant for pure-JS SPAs before PKCE existed. Discouraged
  now because the access token is exposed in browser history/referrer headers/logs, there's no
  refresh-token support, and PKCE gives SPAs a strictly safer path to the same result. If asked
  "why not implicit flow," this is the answer.
- **Client Credentials flow**: service-to-service auth, no user involved — a service authenticates
  with its own client ID/secret to get a token representing itself, not a user.

## RBAC vs ABAC

- **RBAC (Role-Based Access Control)**: users are assigned roles (`admin`, `editor`, `viewer`),
  roles map to a fixed set of permissions. Simple, auditable, and covers most CRUD apps — "can
  editors delete posts?" is a static yes/no lookup.
- **ABAC (Attribute-Based Access Control)**: decisions depend on *attributes* of the user, resource,
  and context at request time — "can this user edit *this specific* document?" might depend on
  `document.owner_id == request.user.id`, or `request.user.department == document.department`, or
  time-of-day/IP restrictions. More flexible, harder to audit ("what can Alice access?" requires
  evaluating rules, not reading a table).
- In practice most production systems are RBAC for coarse permissions (can this role hit this
  endpoint at all) layered with **object-level checks** (does this specific object belong to this
  user) that are effectively lightweight ABAC — DRF's `has_object_permission` is exactly this
  layering.

## DRF permission classes — concrete implementation

```python
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """RBAC-ish coarse gate (must be authenticated) + ABAC-ish object check (must own it)."""

    def has_permission(self, request, view):
        # coarse gate: anyone authenticated can attempt; unauthenticated can only read (if allowed)
        return request.method in permissions.SAFE_METHODS or request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner_id == request.user.id


class IsEditorRole(permissions.BasePermission):
    """Classic RBAC: role -> permission, no object inspection needed."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ("editor", "admin")


# views.py
class PostViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
```

`has_permission` runs before the object is fetched (view-level/RBAC-style gate); `has_object_permission`
runs per-object after `get_object()` (ABAC-style, needs the actual instance) — DRF calls the latter
automatically for detail routes when you use `get_object()`, but **you must call
`check_object_permissions` yourself in any view logic that bypasses the generic `get_object()`**, a
common source of "permission class exists but doesn't actually get enforced" bugs.

## Interview questions

**Q: Why use short-lived access tokens plus a refresh token instead of one long-lived JWT?**
A stolen long-lived JWT is valid until it naturally expires — with JWTs you can't cheaply revoke a
single token early (no server-side lookup, that's the whole point of statelessness). Short access
tokens limit exposure window; the refresh token *is* checked server-side, so it's the one lever you
have to force logout/revoke a compromised session.

**Q: How do you invalidate a single JWT before its expiry, given they're stateless by design?**
Practical answers, in order of how commonly they're used: (1) keep access token TTL short enough
that "wait it out" is an acceptable window, (2) maintain a small revocation blocklist (JWT ID /
`jti` claim in Redis with TTL = remaining token life) checked on verification for genuinely
sensitive actions, (3) revoke the associated refresh token so no new access tokens get minted, which
bounds the damage without full statelessness.

**Q: Session cookies vs JWT in an `Authorization` header — which are you more exposed to, CSRF or
XSS?**
Cookie-based session auth is sent automatically by the browser, so it's CSRF-prone (a malicious
site can trigger a request that includes the cookie) unless you add CSRF tokens/`SameSite`. JWTs in
a header must be attached explicitly by your JS, so they're not CSRF-prone the same way, but if
stored in `localStorage` they're readable by any injected script — so XSS-prone. httpOnly cookies
for refresh tokens combined with in-memory (not localStorage) access tokens is a common way to get
the best of both.

**Q: What's the practical difference between 401 and 403 in a permission-class failure?**
`has_permission`/authentication failure (not logged in, invalid token) → 401. `has_object_permission`
failure (logged in, but don't own this resource / wrong role) → 403. Mixing these up is a common
interview tell — see [REST API Design](01_rest_api_design.md).

## Exercise

1. Implement `IsOwnerOrReadOnly` above, then write a DRF test that asserts: an anonymous `GET`
   succeeds (200), an authenticated non-owner `PATCH` fails (403), and the owner's `PATCH` succeeds
   (200). This is a realistic "write the permission class and test it" interview task.
