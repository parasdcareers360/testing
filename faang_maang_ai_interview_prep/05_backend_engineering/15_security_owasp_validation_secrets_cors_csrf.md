# Security: OWASP, Validation, Secrets, CORS, CSRF

> **Type:** Study notes

## Why interviewers ask this

Security questions at 3 YOE aren't asking you to be a pentester — they're checking that you build
defensively by default: that you know *why* the ORM protects you from SQL injection instead of
just trusting it blindly, that you can explain CORS/CSRF instead of cargo-culting
`CORS_ALLOW_ALL_ORIGINS = True` to make an error go away, and that secrets never end up in git.
These are exactly the mistakes that turn into real incidents.

## OWASP Top 10 — the practical subset

You won't be asked to recite all 10. Know these cold, with a concrete mechanism for each:

- **Injection (SQL injection)** — happens when untrusted input is concatenated directly into a
  query string. The Django ORM parameterizes queries by default, so `Model.objects.filter(name=user_input)`
  is safe — the value is bound as a parameter, never interpolated into SQL text. The danger zone
  is `.raw()` and `.extra()` with string formatting, or raw `cursor.execute()` calls:

```python
# Vulnerable — string-formats untrusted input directly into SQL
cursor.execute(f"SELECT * FROM documents WHERE title = '{title}'")

# Safe — parameterized, the DB driver handles escaping
cursor.execute("SELECT * FROM documents WHERE title = %s", [title])
```

- **Broken authentication** — weak session/token handling: tokens that don't expire, passwords
  compared with `==` instead of a constant-time check, no rate limiting on login (enables
  brute-force). Django's `django.contrib.auth` and DRF's token/JWT auth handle the hard parts
  correctly by default — the mistake is usually rolling your own auth and skipping a detail like
  password hashing or token expiry.
- **Sensitive data exposure** — logging full request bodies (including passwords, card numbers),
  returning stack traces with `DEBUG=True` in production, storing passwords in plaintext instead
  of hashed (Django hashes by default via `AbstractUser` — don't override that casually).
- **Broken access control** — checking "is this user authenticated" but not "is this user allowed
  to access *this specific* object" (IDOR — Insecure Direct Object Reference). `GET
  /documents/42` must check `request.user == document.owner`, not just that *some* valid user is
  logged in.

## Input validation — DRF serializers as the mechanism

Validation is your first line of defense against injection, broken business invariants, and
malformed data reaching your models. DRF serializers are the concrete tool:

```python
class DocumentUploadSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255, trim_whitespace=True)
    file = serializers.FileField(max_length=None, allow_empty_file=False)
    category = serializers.ChoiceField(choices=["invoice", "contract", "receipt"])

    def validate_file(self, value):
        if value.size > 50 * 1024 * 1024:
            raise serializers.ValidationError("File exceeds 50MB limit.")
        if not value.name.lower().endswith((".pdf", ".png", ".jpg")):
            raise serializers.ValidationError("Unsupported file type.")
        return value

    def validate(self, attrs):
        # cross-field validation goes here
        return attrs
```

Field-level validators (`validate_<field>`) catch per-field issues; `validate()` catches
cross-field invariants. Never trust client-supplied data past the serializer boundary — that
includes query params and headers, not just the request body. Whitelisting (`ChoiceField`,
explicit `max_length`) beats blacklisting attempted-bad-input patterns.

## Secrets management

Never in code or git — this is non-negotiable, not a style preference. A secret committed once
lives in git history forever unless you rewrite history (and even then, assume it's compromised
and rotate it).

```python
# Bad
STRIPE_SECRET_KEY = "sk_live_abc123..."

# Better — environment variable, .env kept out of git via .gitignore
STRIPE_SECRET_KEY = os.environ["STRIPE_SECRET_KEY"]

# Production-grade — a secrets manager (AWS Secrets Manager, Vault, GCP Secret Manager)
# injects the value at runtime/deploy time, with access-controlled retrieval and rotation support
STRIPE_SECRET_KEY = get_secret("prod/stripe/secret_key")
```

Env vars are fine for most 3-YOE-scale projects; a real secrets manager adds access auditing,
rotation, and the ability to revoke without a redeploy. Either way: `.env` files stay in
`.gitignore`, CI secrets live in the CI platform's encrypted secret store (GitHub Actions
secrets, etc.), and a leaked secret gets rotated immediately, not just removed from the latest
commit.

## CORS — what it actually protects against

CORS (Cross-Origin Resource Sharing) is a **browser-enforced** rule: by default, JavaScript
running on `https://evil.com` cannot read the response of a fetch to `https://yourapi.com` unless
your API's response explicitly allows that origin via `Access-Control-Allow-Origin`. It does
**not** stop the request from being sent (the request often still hits your server) — it stops
the *browser* from letting the malicious page's JS *read the response*. This matters specifically
for cookie-authenticated APIs: without CORS, `evil.com` could run JS that fetches
`https://yourapi.com/api/account` using the victim's logged-in session cookie and read back
private data.

```python
# settings.py — misconfiguration to avoid
CORS_ALLOW_ALL_ORIGINS = True  # danger: any website's JS can read authenticated responses

# Correct — explicit allowlist
CORS_ALLOWED_ORIGINS = [
    "https://app.mycompany.com",
    "https://staging.mycompany.com",
]
```

`CORS_ALLOW_ALL_ORIGINS = True` combined with `CORS_ALLOW_CREDENTIALS = True` (cookies sent
cross-origin) is a real vulnerability, not a convenience — it lets any website's script read
authenticated responses on behalf of a logged-in victim. Note CORS is irrelevant for
server-to-server calls or non-browser clients (curl, mobile apps) — it's purely a browser
protection.

## CSRF — why it matters for cookies, not for header tokens

CSRF (Cross-Site Request Forgery) exploits the fact that browsers **automatically attach cookies**
to any request to a domain, even one triggered by a form/script on a different malicious site.
If your auth is cookie-based (Django's default session auth), a malicious page can submit a form
to `https://yourapi.com/account/delete` and the browser will happily attach the victim's session
cookie — the request looks authenticated even though the user never intended it. Django's CSRF
middleware defends against this by requiring a token (not stored in a cookie the attacker's page
can silently reuse without knowing it, or protected via `SameSite` cookie attributes) alongside
the cookie for state-changing requests.

**Why token/JWT-in-header auth is typically exempt**: if your auth token is sent via an
`Authorization: Bearer <token>` header, it is not automatically attached by the browser — the
attacker's page has no way to read your token (it's not in a cookie, and same-origin policy
blocks reading it from `localStorage`/JS memory on your domain from their origin) and no way to
make the browser attach it to a forged request. The attacker can *send* a request, but it won't
carry your credentials. That's why DRF's `TokenAuthentication`/JWT setups commonly disable CSRF
checks — the attack CSRF protection exists for doesn't apply to header-based auth. The trade-off:
header tokens push you to worry about XSS (if an attacker's script *does* run on your own page and
can read `localStorage`, they get the token) instead of CSRF — different vulnerability, not "no
vulnerability."

## Interview Q&A

**Q: Why doesn't the Django ORM need manual SQL escaping?**
A: Every ORM query is built with parameterized SQL under the hood — values are bound separately
from the query structure and sent to the DB driver, not string-interpolated into the SQL text, so
there's no injection surface as long as you stay off `.raw()`/`.extra()` with unsanitized string
formatting.

**Q: A teammate wants to set `CORS_ALLOW_ALL_ORIGINS = True` to fix a local dev CORS error. What's
your concern?**
A: Fine for local dev, dangerous in production if it ships that way — combined with credentialed
requests it lets any origin's JS read authenticated API responses on behalf of a logged-in user.
I'd scope it to an explicit allowlist per environment, or at minimum ensure it's gated behind
`DEBUG`/environment config so it can't accidentally reach prod.

**Q: Why is CSRF protection usually disabled for a JWT-based API but required for a
session-cookie-based one?**
A: CSRF relies on the browser auto-attaching credentials (cookies) to cross-site requests without
the attacker needing to know them. A JWT sent via an `Authorization` header isn't auto-attached by
the browser — the attacker's forged request just won't carry it. Session cookies are auto-attached,
so CSRF tokens are the mitigation there.

**Q: You found an API secret committed to the repo six months ago. What do you do?**
A: Rotate the secret immediately — assume it's compromised regardless of whether the repo is
private, since it's been in history for months. Then remove it from the codebase (env var/secrets
manager), and only bother rewriting git history if there's a specific reason to (e.g. compliance
requirement) — rotation is the actual fix, history-scrubbing alone is not.

## Hands-on exercise

1. Write a DRF serializer for a "change password" endpoint with proper validation: current
   password check, new password strength rules, and confirmation match — and explain which checks
   belong in `validate_<field>` vs. `validate()`.
2. Given a Django settings file with `CORS_ALLOW_ALL_ORIGINS = True` and
   `CORS_ALLOW_CREDENTIALS = True`, describe the exact attack a malicious site could run against a
   logged-in user, and rewrite the settings to fix it.
