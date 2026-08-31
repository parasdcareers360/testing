# FAANG/MAANG Resume Template

> **Type:** Template — copy or fill in directly

## Format rules that actually matter

- **One page.** At 3 YOE, a two-page resume reads as an inability to prioritize, not as more
  experience.
- **No photo, no objective statement, no skills-bar graphics.** ATS parsers and human reviewers
  both hate them.
- **Reverse chronological.** Most recent role first.
- **Every bullet: action verb → what you built/fixed → measurable impact.** Never "responsible
  for X" — that's a job description, not an accomplishment.
- **Bullets you can defend under questioning only.** If you can't explain the number in the
  bullet in 30 seconds when a bar raiser pushes on it, cut the number or the bullet.

## Bullet formula

```
<Action verb> <what you built/changed> <using which real tech> <resulting in measurable impact>
```

**Example — replace with your own numbers:**
> Redesigned the pagination layer of a DRF-based search API (Elasticsearch backend) using
> cursor-based pagination instead of offset, cutting p95 latency on page 50+ from 1.8s to 220ms
> for ~40k daily active users.

Weak version of the same bullet (what NOT to do):
> Responsible for improving API performance and search functionality.

## Structure

```markdown
# Your Name
your.email@example.com | +91-XXXXXXXXXX | linkedin.com/in/yourhandle | github.com/yourhandle

## Experience

### <Job Title> — <Company>                                              <Start> – <End>
- <Bullet 1: biggest/most quantifiable win>
- <Bullet 2>
- <Bullet 3>
- <Bullet 4 — optional, only if it's genuinely strong>

### <Previous role, same format>

## Projects (if you have < 3 YOE at a single company, or a standout side project)

### <Project Name> — <one-line what it is>                                <dates>
- <Bullet: what you built, stack, and a concrete result — see
  `project_architecture_explanation_template.md` for the deep-dive version>

## Skills

**Languages:** Python, SQL, ...
**Backend:** Django, DRF, FastAPI, ...
**Data:** PostgreSQL, Elasticsearch, Redis, ...
**Infra:** Docker, ...
**Other:** ...

## Education
<Degree>, <Institution>                                                    <Grad year>
```

Do not add a "Certifications" section unless the certification is directly relevant and
recent (cloud certs are fine; generic online-course certificates are not — they read as filler).

## Quantifying when you don't have exact numbers

You often don't have a dashboard with the exact percentage improvement. It's fine to reason to a
defensible estimate out loud in the interview — just don't print a number on the resume you can't
justify:
- "Reduced query time from ~2s to ~300ms" (measured locally/staging) is fine even without
  production telemetry, as long as you say "measured in staging" if asked.
- "Handled X requests/day" — derive from known DAU × known requests-per-user if you don't have a
  direct counter, and be ready to show that derivation.
- If you truly have no number, describe the *qualitative* before/after and let the interviewer
  ask for scale — don't fabricate a metric.

## Pre-submit checklist

- [ ] Every bullet has a verb + a number or a concrete outcome
- [ ] No bullet you can't defend for 2 minutes of follow-up questions
- [ ] Fits one page at 10-11pt font, reasonable margins
- [ ] No typos, no inconsistent date formats, no "team player" / "hard worker" adjectives
- [ ] Tailored skills section matches the job posting's stack where truthful
- [ ] PDF export (not .docx) unless the application system requires otherwise

See also [`ai_backend_resume_template.md`](ai_backend_resume_template.md) if you're targeting AI
Backend / ML Platform roles specifically, and
[`star_format_project_stories.md`](star_format_project_stories.md) to build the stories behind
each bullet.
