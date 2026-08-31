# Sample Storytelling — API Gateway Design

> **Type:** Study notes

An illustrative worked example — replace the specifics with your own real project.

## The story (spoken, ~2 min)

> "As we split out services (notifications, search, the core app), each one started reimplementing
> auth-token validation, rate limiting, and request logging separately — which meant three
> slightly different bugs in three places. I introduced a lightweight API gateway (nginx +
> a small custom auth-validation service, not a full managed gateway product, since our scale
> didn't justify that cost yet) in front of all of them.
>
> The gateway did three things: validated the JWT and forwarded a verified user-id header
> downstream (so individual services trusted the header instead of re-validating tokens
> themselves), applied a per-user rate limit using Redis-backed sliding-window counters, and
> logged every request with a correlation ID that got propagated through all downstream service
> calls for tracing.
>
> The trade-off I had to explicitly decide on was: should downstream services still validate the
> user-id header themselves, or fully trust the gateway? I went with 'trust but verify at the
> network level' — the services only accept traffic from the gateway's IP range, not from the
> public internet directly, so the header can't be spoofed by an external caller."

## Why this works as an answer

- Starts from the **real duplication problem**, same honesty pattern as good stories in this
  folder — not "gateways are a best practice."
- Names the **three concrete responsibilities** (auth forwarding, rate limiting, correlation IDs)
  instead of a vague "handles cross-cutting concerns."
- The **trust-boundary trade-off** at the end is the strongest part — it shows security thinking
  a mid-level answer would skip entirely.

## Likely follow-ups and what they're probing

| Follow-up | What to have ready |
|---|---|
| "What happens if the gateway itself goes down?" | Single point of failure awareness — redundant gateway instances behind a load balancer |
| "How do you rate-limit per-user vs. per-IP, and why does it matter?" | Understanding NAT'd users behind one IP, and API keys vs. IP-based limiting trade-offs |
| "Why not a managed API gateway (Kong, AWS API Gateway)?" | Honest cost/complexity trade-off reasoning for your team's actual scale at the time |

See [`../../06_system_design/exercises/api_gateway.md`](../../06_system_design/exercises/api_gateway.md)
and [`../../05_backend_engineering/11_api_gateways.md`](../../05_backend_engineering/11_api_gateways.md)
for the underlying concepts.
