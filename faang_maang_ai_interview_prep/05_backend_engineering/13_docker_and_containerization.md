# Docker & Containerization

> **Type:** Study notes

## Why interviewers ask this

Docker questions filter for whether you understand what a container actually is versus treating
`docker run` as magic. At 3 YOE, interviewers expect you to explain image layering/caching (why
your builds are slow or fast), write a reasonable multi-stage Dockerfile, and be honest about
what containers don't solve — because "we use Docker" is table stakes, and the differentiator is
knowing its edges.

## Image vs. container

An **image** is a read-only, layered filesystem snapshot plus metadata (entrypoint, env,
exposed ports) — it's a build artifact, like a compiled binary but for a whole filesystem. A
**container** is a running (or stopped) instance of an image: the image's layers mounted
read-only with a thin writable layer on top, plus an isolated process namespace, network
namespace, and cgroup resource limits. One image, many containers — the same way one class can
have many instances. Deleting a container doesn't touch the image; deleting an image you're not
running from doesn't affect a container already running from it (the container has its own
reference to the layers).

## Dockerfile basics: layers, caching, multi-stage

Each instruction in a Dockerfile (`RUN`, `COPY`, `ADD`) creates a new layer. Docker caches layers
and reuses them if the instruction and its inputs haven't changed — so **ordering matters**:
put things that change rarely (installing system deps) before things that change often (copying
your application code), or every code change invalidates the cache all the way down and forces a
full rebuild.

```dockerfile
# Bad: any code change invalidates the pip install cache below it
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["gunicorn", "myproj.wsgi:application", "--bind", "0.0.0.0:8000"]
```

```dockerfile
# Better: dependency layer only rebuilds when requirements.txt changes
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
# Copy only the installed packages from the builder stage, not its build tools
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
RUN useradd --create-home appuser && chown -R appuser /app
USER appuser
CMD ["gunicorn", "myproj.wsgi:application", "--bind", "0.0.0.0:8000"]
```

**Multi-stage builds**: use one stage (`builder`) with all the compilers/build tools needed to
install dependencies, then copy *only the result* into a clean final stage. This keeps the
shipped image small (no gcc, no build headers, no leftover pip cache) and reduces attack
surface — a smaller image is also a faster pull/deploy. Also note running as a non-root `USER`,
which comes up in security-flavored follow-ups.

## docker-compose for local multi-service dev

A Django app in real use rarely runs alone — it needs Postgres, Redis, Elasticsearch, a Celery
worker. `docker-compose` describes that whole local stack in one file so `docker-compose up`
gives every developer (and CI) the identical set of services, wired together, without each person
hand-installing Postgres/Redis locally.

```yaml
services:
  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    environment:
      - DATABASE_URL=postgres://postgres:postgres@db:5432/myapp

  worker:
    build: .
    command: celery -A myproj worker -l info
    depends_on:
      - db
      - redis

  db:
    image: postgres:16
    environment:
      - POSTGRES_PASSWORD=postgres
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7

volumes:
  pgdata:
```

Note `web` and `worker` share the same image/build — same app code, different `command` — which
mirrors how you'd actually run Celery workers in production: same codebase, different process
type. `depends_on` controls start order, not "wait until actually ready" — a real app should
still handle "Postgres accepted the TCP connection but isn't ready for queries yet" with
retry-on-startup logic.

## Why containers help — and what they don't solve

**What containers solve: environment parity.** "Works on my machine" mostly comes from
differences in installed system libraries, Python versions, or OS-level dependencies between
dev/CI/prod. A container packages the exact runtime environment as an artifact — the same image
that passed CI is the image that runs in production, not "a similar setup rebuilt from a
requirements file on a different base OS."

**What containers don't solve: orchestration.** A single `docker run` doesn't give you: scheduling
containers across a fleet of machines, restarting a crashed container automatically, rolling
deploys with health checks, service discovery between containers on different hosts, or
horizontal autoscaling. That's the layer above containers — **Kubernetes** (or simpler tools like
ECS, Docker Swarm) is what handles "run N replicas of this image, across M machines, restart
failures, roll out updates without downtime." Worth mentioning by name if asked "what comes
next," but a deep Kubernetes dive is out of scope for this file — the point to land is that
Docker packages the unit of deployment; something else has to actually schedule and manage it at
scale.

## Interview Q&A

**Q: Your Docker build takes 4 minutes even for a one-line code change. Why, and how do you fix
it?**
A: Almost certainly layer-cache invalidation — `COPY . .` (or installing deps) happens before the
code copy, so every code change reruns the expensive `pip install`/`apt-get` layers below it.
Reorder the Dockerfile so dependency installation is a separate, earlier layer keyed only on
`requirements.txt`, and use multi-stage builds to keep the final image lean.

**Q: What's the difference between `COPY` and `ADD`?**
A: `COPY` does a plain file copy — use it by default. `ADD` additionally auto-extracts local tar
archives and can fetch remote URLs, which is more "magic" than most Dockerfiles want; prefer
`COPY` unless you specifically need `ADD`'s extra behavior.

**Q: If containers give environment parity, why do people still say "works in Docker, breaks in
prod"?**
A: Usually it's not the container image that differs — it's something outside the image: env
vars/secrets configured differently, a missing volume/network dependency, resource limits
(memory/CPU) that are tighter in prod and OOM-kill the process, or an orchestration-layer
difference (readiness probes, scaling behavior) that Docker itself doesn't control.

## Hands-on exercise

1. Take a Django project and write a multi-stage Dockerfile: a `builder` stage that installs
   dependencies into a virtualenv or `--user` target, and a final slim stage that copies only the
   installed packages + app code, runs as a non-root user.
2. Write a `docker-compose.yml` for that project with `web`, `worker` (Celery), `db` (Postgres),
   and `redis` services, and explain out loud why `web` and `worker` should share the same image.
