# GitHub Project README Template

> **Type:** Template — copy or fill in directly

A reviewer decides whether to keep reading in about 30 seconds. Front-load what it does and why
it's interesting — don't make them scroll to find out.

## Structure

```markdown
# Project Name

One-sentence description of what it does and for whom.

[Optional: badge row — build status, license, Python version]

## Why this exists / what problem it solves

2-4 sentences. What's the real-world use case? What would break or be annoying without this?

## Architecture

<A short paragraph or a Mermaid diagram — see
06_system_design fundamentals for diagram conventions>

\`\`\`mermaid
flowchart LR
    Client --> API[DRF API]
    API --> DB[(PostgreSQL)]
    API --> Search[(Elasticsearch)]
    API --> Queue[Celery + Redis]
\`\`\`

## Key technical decisions

- **<Decision, e.g. "Cursor pagination instead of offset">**: <why, in 1-2 sentences — this is
  what shows engineering judgment to a reviewer, not just tech-stack listing>
- **<Decision 2>**: <why>

## Tech stack

Python, Django, DRF, PostgreSQL, Elasticsearch, Docker, Celery, Redis — list what's actually
used, not aspirational tech.

## Setup

\`\`\`bash
git clone <repo>
cd <repo>
docker-compose up --build
\`\`\`

(Whatever actually gets someone from clone to running in under 5 minutes — a reviewer who has to
debug your setup instructions stops reading.)

## What I'd do differently / known limitations

Honest section. Shows self-awareness and seniority — better than pretending it's perfect.

## License
```

## Rules

- **Never claim scale you didn't test.** "Designed to handle 10k req/s" without a load test
  result is a red flag if a reviewer asks "did you actually test that?" — say "load-tested
  locally to X" or "designed for, not yet load-tested at scale" instead.
- **Screenshots/GIFs for anything with a UI.** Reviewers skim; a picture stops the scroll.
- **Keep the README shorter than the code.** If the README is longer than what a candidate would
  actually say out loud in 2 minutes, cut it.
- Link this README from your resume project bullet and be ready to open it on screen-share during
  a deep-dive round.

See [`project_architecture_explanation_template.md`](project_architecture_explanation_template.md)
for the spoken version of this same content.
