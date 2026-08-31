# Style Guide — faang_maang_ai_interview_prep

Conventions for every file in this workspace. Read this before writing or editing anything here.

## Who this is for

A **Python backend developer with 3 years of experience** (Django, DRF, PostgreSQL, Elasticsearch,
Docker, microservices, API gateways, auth, background jobs, OCR/PDF processing) preparing for
Software Engineer / Backend Engineer / Python Developer / Platform Engineer / AI Backend Engineer /
ML Platform roles at FAANG/MAANG companies and AI-focused companies (OpenAI, Anthropic, Google
DeepMind, Microsoft AI, and similar). Write at that level: not a beginner tutorial, not a research
paper — practical, interview-focused, assumes real production experience.

## Two kinds of file — mark clearly which one you're writing

1. **Study material** — concept explanations, interview Q&A, worked examples. Dense with real
   content. Header should read `> **Type:** Study notes`.
2. **Templates / trackers** — meant to be copied, filled in, or updated repeatedly (checklists,
   resume templates, trackers, mock-interview sheets). Header should read `> **Type:** Template —
   copy or fill in directly` and should contain mostly structure (headings, tables, checkboxes)
   with a *little* worked example so it's clear how to use it, not a wall of prose.

Every file starts with:
```markdown
# <Title>

> **Type:** Study notes | Template — copy or fill in directly
```

## Hard rules

1. **No generic filler.** Every bullet must say something a candidate can actually use — a real
   gotcha, a real trade-off, a real phrase to say out loud, a real number. Delete any sentence that
   would still be true if you deleted the specific noun in it.
2. **Python-first.** All code examples are Python (Django/DRF-flavored where relevant to this
   candidate's background), never Java/C++, unless the topic is language-agnostic (SQL, system
   design) — even then, prefer Python for any client-code snippets.
3. **Interview-oriented.** Every concept file includes: a short "why interviewers ask this,"
   2-5 realistic interview questions with concise model answers, at least one runnable-looking code
   example, and where relevant, 1-2 hands-on exercises the reader can actually do.
4. **Tables and checkboxes for anything tracked over time.** Progress trackers, checklists, and
   scorecards must be Markdown tables or `- [ ]` checklists that are trivial to hand-edit — never
   prose describing what to track.
5. **Mermaid where a diagram earns its place** — system design, LLD class diagrams, architecture
   flows. Use ` ```mermaid ` fenced blocks. Don't diagram things that are clearer as a bullet list.
6. **Explicit "varies" caveat on anything company-specific.** Interview processes, bar, and
   question style vary by role, team, level, location, and hiring cycle/year. Every
   company-specific file states this once, clearly, near the top — don't present a single process
   as gospel.
7. **No invented specifics you can't back up.** Don't fabricate a named interviewer, a specific
   leaked question, a specific comp number, or a specific process detail presented as fact if it's
   not well-established public knowledge. General, well-known patterns (e.g. "Amazon interviews
   are Leadership-Principle-heavy," "Google has a bar raiser") are fine; fabricated specifics
   (e.g. "Google's third round is always X problem") are not.
8. **Cross-link related files** with relative Markdown links (e.g.
   `[SOLID principles](../07_low_level_design/fundamentals/solid_principles.md)`) instead of
   repeating content — this is one workspace, not isolated documents.
9. **Every DSA pattern's `template.py` must be real, correct, syntactically valid Python** —
   runnable skeleton code (helper functions, common patterns like sliding-window boilerplate,
   Union-Find class, etc.), not pseudocode in a code fence.
10. **Problem-practice trackers use this exact table shape** (fill with real, correctly-named
    LeetCode-style problems appropriate to the pattern — a mix the candidate would realistically
    meet at FAANG/MAANG, spread Easy/Medium/Hard, weighted toward Medium):

    ```markdown
    | # | Problem | Difficulty | Status | Notes |
    |---|---------|------------|--------|-------|
    | 1 | Two Sum | Easy | [ ] | |
    ```
    Aim for roughly 8-12 problems per pattern (2-3 Easy, 5-7 Medium, 1-3 Hard).

## Directory-specific notes

- **`02_dsa_and_coding/patterns/<topic>/`**: exactly 5 files + `solutions/` (empty except
  `.gitkeep`): `concept.md`, `template.py`, `common_mistakes.md`, `communication_tips.md`,
  `problem_tracker.md`. Don't add extra files here — the tracker + concept file are where content
  lives.
- **`06_system_design/exercises/*.md`** and **`07_low_level_design/exercises/*.md`**: each is a
  *complete* worked design exercise (requirements → capacity/estimation or class model →
  design → trade-offs → what a 3-YOE candidate is expected to cover vs. what's out of scope), not
  just a prompt. Include at least one Mermaid diagram.
- **`09_ai_backend_and_llm_systems/mini_projects/*.md`**: each is a project brief a candidate could
  actually build in a few weekends — problem statement, suggested stack (favor
  Python/Django/DRF/PostgreSQL/pgvector/Elasticsearch consistent with this candidate's background),
  rough architecture, and what it demonstrates to an interviewer.
- **Trackers in `12_mock_interviews/`, `13_job_application_tracking/`, `15_progress_tracking/`,
  `11_behavioral_and_leadership/story_bank_tracker.md`**: pure Markdown tables, one small worked
  example row, ready to be duplicated/extended by hand.

## Filenames

Fixed by `MANIFEST.md` — do not rename, skip, reorder, or invent extra files beyond what it lists.
