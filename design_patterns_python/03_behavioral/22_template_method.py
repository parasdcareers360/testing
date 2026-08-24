"""
Design Patterns in Python — #22
Template Method (Behavioral Pattern)

Intent
------
Define the skeleton of an algorithm in a base class, with the fixed, invariant steps written
once, while letting subclasses override specific individual steps without changing the overall
structure of the algorithm. The base class calls the shots on *order* and *when* each step runs;
subclasses only supply *what* an individual step does.

Problem / Motivation
---------------------
Picture a report-generation pipeline: load data, process it, format it, save it. A CSV-based
report and a JSON-based report both follow that exact same four-step shape — they only differ in
*how* they load and *how* they format. Without Template Method, the natural instinct is to write
`generate_csv_report()` and `generate_json_report()` as two separate top-to-bottom functions.
They end up duplicating the "process" and "save" steps almost verbatim, and if a bug in the
processing step is fixed in one function, it's easy to forget the near-identical code sitting a
few functions away in the other one — the two implementations quietly drift out of sync.

Structure
---------
An abstract base class defines a concrete `template_method()` that calls a fixed sequence of
steps, some of which are abstract (subclasses *must* override them) and some of which are
"hooks" with a sensible default (subclasses *may* override them, but don't have to). Concrete
subclasses only implement the steps that vary; the algorithm's overall shape lives in exactly one
place — the base class — and can never drift between subclasses because it's never duplicated.

When to Use
-----------
- Several classes implement the same algorithm structure but differ in a few specific steps
  (report pipelines, request-handling middleware, build/test/deploy stages, sorting/searching
  variants that share a scaffold but differ in a comparison step).
- You want to enforce that a certain sequence of steps always happens in a certain order, while
  still giving subclasses freedom over the specifics of individual steps.

When NOT to Use
----------------
- If the steps' order or presence genuinely varies between use cases (not just what each step
  does, but which steps run and in what sequence), a rigid template forces awkward
  workarounds — consider Strategy (swap the whole algorithm) or just composing functions freely.
- In Python, prefer passing step functions as parameters over building a subclass per variant
  when the "steps" don't need to share persistent state across calls — subclassing to override
  one method is heavier machinery than a plain function parameter (see Implementation 2).

Related / Commonly Confused Patterns
--------------------------------------
- Strategy: both let you vary part of a behavior, but Template Method varies individual *steps*
  of a fixed-shape algorithm via inheritance (the base class stays in control of the sequence),
  while Strategy swaps out an *entire* algorithm via composition (the client holds a reference to
  a chosen strategy object and the "algorithm" is opaque to the caller).
- Factory Method: often *used inside* a template method as one of its steps (e.g. "create the
  right kind of formatter for this step"), but Factory Method is about object creation
  specifically, not algorithm structure.
"""


# ============================================================
# Anti-pattern: the naive way, and why it hurts
# ============================================================
# Two nearly-identical top-to-bottom functions. "process" and "save" are duplicated almost
# verbatim between them -- fix a bug in one and it's easy to forget the copy sitting in the
# other. Every new report format means copy-pasting the whole pipeline again.
def generate_csv_report_naive(raw_rows: list[dict]) -> str:
    # load
    data = raw_rows
    # process (duplicated in the JSON version below)
    processed = [{k: str(v).strip() for k, v in row.items()} for row in data]
    # format (the one truly different step)
    header = ",".join(processed[0].keys()) if processed else ""
    lines = [header] + [",".join(row.values()) for row in processed]
    formatted = "\n".join(lines)
    # save (duplicated in the JSON version below)
    return f"[saved as report.csv]\n{formatted}"


def generate_json_report_naive(raw_rows: list[dict]) -> str:
    import json

    # load
    data = raw_rows
    # process (copy-pasted from the CSV version -- already slightly diverging: no .strip() here!)
    processed = [{k: v for k, v in row.items()} for row in data]
    # format (the one truly different step)
    formatted = json.dumps(processed)
    # save (copy-pasted from the CSV version)
    return f"[saved as report.json]\n{formatted}"


# ============================================================
# Implementation 1: Classic (OOP / GoF-style, abstract base class + template_method())
# ============================================================
# Idea: the algorithm's shape -- load, then process, then format, then save -- is written
# EXACTLY ONCE, in ReportPipeline.generate(). Subclasses only ever override the individual steps
# that legitimately differ; "process" has a sensible default (a hook), so subclasses that don't
# need custom processing simply don't override it, and can't accidentally skip or reorder steps.
from abc import ABC, abstractmethod


class ReportPipeline(ABC):
    def generate(self, raw_rows: list[dict]) -> str:
        """The template method: fixed algorithm shape, never overridden by subclasses."""
        data = self._load(raw_rows)
        processed = self._process(data)
        formatted = self._format(processed)
        return self._save(formatted)

    def _load(self, raw_rows: list[dict]) -> list[dict]:
        return raw_rows

    def _process(self, data: list[dict]) -> list[dict]:
        # A hook with a sensible default -- subclasses MAY override, but most won't need to.
        return [{k: str(v).strip() for k, v in row.items()} for row in data]

    @abstractmethod
    def _format(self, processed: list[dict]) -> str: ...

    @abstractmethod
    def _save(self, formatted: str) -> str: ...


class CsvReportPipeline(ReportPipeline):
    def _format(self, processed: list[dict]) -> str:
        if not processed:
            return ""
        header = ",".join(processed[0].keys())
        lines = [header] + [",".join(row.values()) for row in processed]
        return "\n".join(lines)

    def _save(self, formatted: str) -> str:
        return f"[saved as report.csv]\n{formatted}"


class JsonReportPipeline(ReportPipeline):
    def _format(self, processed: list[dict]) -> str:
        import json

        return json.dumps(processed)

    def _save(self, formatted: str) -> str:
        return f"[saved as report.json]\n{formatted}"


class AuditedCsvReportPipeline(CsvReportPipeline):
    """Demonstrates overriding the hook step: adds a row-count column no other pipeline has,
    without touching (or duplicating) the load/format/save steps it inherits unchanged."""

    def _process(self, data: list[dict]) -> list[dict]:
        cleaned = super()._process(data)
        for i, row in enumerate(cleaned, start=1):
            row["row_num"] = str(i)
        return cleaned


# ============================================================
# Implementation 2: Pythonic idiom (a single function taking step functions as parameters)
# ============================================================
# Idea: when the "steps" are stateless and don't need to share data across calls, a whole
# subclass per variant is more machinery than the problem needs -- the fixed algorithm shape can
# just be a function that accepts the varying steps as callables. No class hierarchy, no `self`,
# no ABC: swapping behavior is passing a different function, not defining a different class.
def run_report_pipeline(raw_rows: list[dict], format_step, save_step, process_step=None) -> str:
    data = raw_rows
    processed = (process_step or _default_process)(data)
    formatted = format_step(processed)
    return save_step(formatted)


def _default_process(data: list[dict]) -> list[dict]:
    return [{k: str(v).strip() for k, v in row.items()} for row in data]


def format_as_csv(processed: list[dict]) -> str:
    if not processed:
        return ""
    header = ",".join(processed[0].keys())
    lines = [header] + [",".join(row.values()) for row in processed]
    return "\n".join(lines)


def format_as_json(processed: list[dict]) -> str:
    import json

    return json.dumps(processed)


def save_as(extension: str):
    """Returns a save-step closure -- shows steps can themselves be parameterized factories."""

    def save(formatted: str) -> str:
        return f"[saved as report.{extension}]\n{formatted}"

    return save


# ============================================================
# Key Takeaways
# ============================================================
# - The algorithm's *shape* (order of steps) lives in exactly one place -- the template method,
#   or the one pipeline function -- so it can never drift between variants the way copy-pasted
#   top-to-bottom functions inevitably do.
# - A "hook" (a step with a default implementation, like _process here) is different from an
#   abstract step subclasses MUST override -- mixing the two lets common cases skip boilerplate
#   while still allowing full customization where it's actually needed.
# - Common misuse: reaching for a subclass-per-variant hierarchy in Python when the steps are
#   plain stateless functions -- passing step functions as parameters (Implementation 2) gets
#   the same "fixed shape, swappable steps" guarantee with far less ceremony.
# - Related pattern to compare: Strategy -- Template Method varies individual steps of one fixed
#   algorithm (inheritance-driven), Strategy swaps the entire algorithm as one unit (composition-
#   driven); they're easy to confuse because both are about varying behavior.


if __name__ == "__main__":
    rows = [
        {"name": " Alice ", "amount": 100},
        {"name": "Bob", "amount": 250},
    ]

    print("--- Anti-pattern: two hand-duplicated top-to-bottom functions ---")
    print(generate_csv_report_naive(rows))
    print(generate_json_report_naive(rows))
    print("  (note: JSON version's copy-pasted 'process' step already forgot the .strip() call)")

    print("\n--- Classic: ReportPipeline template method, steps overridden per subclass ---")
    csv_report = CsvReportPipeline().generate(rows)
    json_report = JsonReportPipeline().generate(rows)
    print(csv_report)
    print(json_report)
    assert "Alice" in csv_report and "report.csv" in csv_report
    assert '"amount": "100"' in json_report and "report.json" in json_report

    audited = AuditedCsvReportPipeline().generate(rows)
    print(audited)
    assert "row_num" in audited  # hook override changed only _process, nothing else
    assert "report.csv" in audited  # _save/_format still inherited unchanged from CsvReportPipeline

    print("\n--- Pythonic: run_report_pipeline() with step functions passed in ---")
    csv_fn_report = run_report_pipeline(rows, format_step=format_as_csv, save_step=save_as("csv"))
    json_fn_report = run_report_pipeline(
        rows, format_step=format_as_json, save_step=save_as("json")
    )
    print(csv_fn_report)
    print(json_fn_report)
    assert csv_fn_report == csv_report  # identical output to the class-based version
    assert json_fn_report == json_report

    print("\nSame fixed algorithm shape (load -> process -> format -> save), expressed once via")
    print("a class hierarchy and once via function parameters -- both keep 'process'/'save'")
    print("from ever being copy-pasted the way the anti-pattern's two functions were.")
