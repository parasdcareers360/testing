# Sample Storytelling — Django REST APIs

> **Type:** Study notes

An illustrative worked example — replace the specifics with your own real project.

## The story (spoken, ~2 min)

> "I built and maintained a DRF-based API serving a document management product — roughly 40
> endpoints across auth, document CRUD, sharing/permissions, and search. The interesting part was
> permissions: we needed row-level access control (a document could be shared with specific users
> or teams, with view/edit/admin tiers) on top of Django's default model-level permissions, which
> don't handle that.
>
> I implemented it with a custom DRF permission class plus a `django-guardian`-style object
> permission table, and added a queryset-filtering mixin so every viewset automatically excluded
> documents the requesting user couldn't see — rather than relying on each view to remember to
> check. That mattered because a missed check in even one endpoint would have been a real data
> leak, not just a bug.
>
> The trade-off was query complexity — permission-filtered querysets needed a join against the
> permissions table on every list endpoint, which I mitigated with a covering index on
> `(user_id, document_id, permission_level)` and by paginating aggressively by default."

## Why this works as an answer

- Names a **real DRF-specific mechanism** (permission classes, querysets, viewset mixins) — not
  generic "I built APIs."
- States the **actual technical problem** (row-level permissions Django doesn't give you by
  default) instead of a vague "it was complex."
- Includes **one concrete trade-off and mitigation** (join cost → covering index), which is what
  separates a mid-level answer from a senior one.
- Names the **risk if done wrong** (data leak) — shows you understood why the design mattered,
  not just what you built.

## Likely follow-ups and what they're probing

| Follow-up | What to have ready |
|---|---|
| "How did you test the permission logic?" | Specific test cases: cross-user access denial, team-share edge cases |
| "What if a user's team membership changed after a document was shared?" | Whether you thought about permission staleness/caching |
| "How would this scale to 10M documents?" | Index strategy, maybe denormalizing an ACL table |

See [`../../05_backend_engineering/03_auth_jwt_oauth_rbac.md`](../../05_backend_engineering/03_auth_jwt_oauth_rbac.md)
and [`../../05_backend_engineering/17_django_and_drf_patterns.md`](../../05_backend_engineering/17_django_and_drf_patterns.md)
for the underlying concepts this story draws on.
