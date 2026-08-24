"""
Design Patterns in Python — #2
Factory Method (Creational Pattern)

Intent
------
Define an interface for creating an object, but let subclasses (or, in the Pythonic variant,
registered callables) decide which concrete class gets instantiated. Factory Method lets a
class defer instantiation to a method that can be overridden or swapped, so the code that *uses*
an object never has to hard-code the concrete class it's building.

Problem / Motivation
---------------------
Say a report exporter needs to produce output in several formats: CSV, JSON, and PDF. The
obvious first pass is a function that branches on a format string and constructs the right
exporter class directly. That works for three formats. Then someone adds XML support, then a
plugin-style "custom" format for one client, then a compressed CSV variant — and every addition
means opening the same function and adding another `elif`, in every place that function is
duplicated. The construction logic (which concrete class to build) is tangled up with the
business logic (export the report), and the two grow at different rates for different reasons.

Structure
---------
A Creator declares a factory method that returns a Product; ConcreteCreator subclasses override
that method to return a specific ConcreteProduct. Client code talks to the Creator's interface
and the abstract Product interface only — it calls `creator.create_exporter()` and gets back
something that satisfies the Exporter contract, without ever naming the concrete class. Adding a
new product means adding a new ConcreteCreator/ConcreteProduct pair, not editing existing code.

When to Use
-----------
- A class can't anticipate which concrete class of object it needs to create ahead of time (a
  plugin system, a format-driven exporter, a driver registry).
- You want to localize "which concrete class to build" logic in one place instead of scattering
  `if format == "csv": ... elif format == "json": ...` chains across the codebase.
- You want new product types to be addable without modifying the code that already works
  (open/closed principle).

When NOT to Use
----------------
- If there's only ever going to be one or two concrete products and that's genuinely not going
  to change, a factory method is ceremony for its own sake — a direct constructor call is
  clearer.
- Don't reach for a full subclass-per-product hierarchy in Python by default; a dict-based
  registry (Implementation 2 below) gets the same open/closed benefit with far less boilerplate
  for the common case of "many small, stateless product classes."

Related / Commonly Confused Patterns
--------------------------------------
- Abstract Factory: often built out of several Factory Methods, one per product in a *family* of
  related products (see pattern #3) — Factory Method makes one product, Abstract Factory makes a
  matched set.
- Template Method: Factory Method is a special case of Template Method where the "step" being
  overridden happens to be object creation.
"""


# ============================================================
# Anti-pattern: the naive way, and why it hurts
# ============================================================
# The export logic and the "which class to instantiate" logic are welded together in one
# function. Every new format means editing this function (and every other copy of this same
# if/elif chain elsewhere in the codebase that also needs to build exporters).
class CsvExporter:
    def export(self, rows: list[dict]) -> str:
        if not rows:
            return ""
        header = ",".join(rows[0].keys())
        body = "\n".join(",".join(str(v) for v in row.values()) for row in rows)
        return f"{header}\n{body}"


class JsonExporter:
    def export(self, rows: list[dict]) -> str:
        import json
        return json.dumps(rows)


def export_report_naive(fmt: str, rows: list[dict]) -> str:
    if fmt == "csv":
        exporter = CsvExporter()
    elif fmt == "json":
        exporter = JsonExporter()
    # ...adding "xml" means another elif here, and in every other function like this one.
    else:
        raise ValueError(f"unsupported format: {fmt}")
    return exporter.export(rows)


# ============================================================
# Implementation 1: Classic (OOP / GoF-style, subclass overrides the factory method)
# ============================================================
# Idea: each concrete Creator owns the decision of which concrete Product to build. Client code
# is written entirely against the abstract ReportJob / Exporter interfaces — it calls
# job.run(rows), and job.make_exporter() (overridden per subclass) supplies the concrete piece.
from abc import ABC, abstractmethod


class Exporter(ABC):
    @abstractmethod
    def export(self, rows: list[dict]) -> str:
        ...


class ClassicCsvExporter(Exporter):
    def export(self, rows: list[dict]) -> str:
        if not rows:
            return ""
        header = ",".join(rows[0].keys())
        body = "\n".join(",".join(str(v) for v in row.values()) for row in rows)
        return f"{header}\n{body}"


class ClassicJsonExporter(Exporter):
    def export(self, rows: list[dict]) -> str:
        import json
        return json.dumps(rows)


class ClassicXmlExporter(Exporter):
    def export(self, rows: list[dict]) -> str:
        items = "".join(
            "<row>" + "".join(f"<{k}>{v}</{k}>" for k, v in row.items()) + "</row>"
            for row in rows
        )
        return f"<rows>{items}</rows>"


class ReportJob(ABC):
    """Creator: defines the workflow, defers the 'which exporter' decision to a subclass."""

    @abstractmethod
    def make_exporter(self) -> Exporter:
        """The factory method — overridden by each ConcreteCreator."""
        ...

    def run(self, rows: list[dict]) -> str:
        exporter = self.make_exporter()  # never names a concrete class directly
        print(f"  [classic] running report job via {type(exporter).__name__}")
        return exporter.export(rows)


class CsvReportJob(ReportJob):
    def make_exporter(self) -> Exporter:
        return ClassicCsvExporter()


class JsonReportJob(ReportJob):
    def make_exporter(self) -> Exporter:
        return ClassicJsonExporter()


class XmlReportJob(ReportJob):
    def make_exporter(self) -> Exporter:
        return ClassicXmlExporter()


# ============================================================
# Implementation 2: Pythonic idiom (dict-based registry of constructors)
# ============================================================
# Idea: in Python, classes and functions are first-class objects, so "which concrete class to
# build" can just be a lookup in a dict instead of a whole subclass hierarchy. A registration
# decorator lets each exporter register itself under a name at import time — adding a new format
# means adding one small class with one decorator line, no new ReportJob subclass required. This
# is by far the more common way this pattern shows up in real Python codebases (plugin systems,
# serializer registries, CLI subcommand dispatch all use this shape).
_EXPORTER_REGISTRY: dict[str, type[Exporter]] = {}


def register(name: str):
    def decorator(cls: type[Exporter]) -> type[Exporter]:
        _EXPORTER_REGISTRY[name] = cls
        return cls
    return decorator


@register("csv")
class RegistryCsvExporter(Exporter):
    def export(self, rows: list[dict]) -> str:
        if not rows:
            return ""
        header = ",".join(rows[0].keys())
        body = "\n".join(",".join(str(v) for v in row.values()) for row in rows)
        return f"{header}\n{body}"


@register("json")
class RegistryJsonExporter(Exporter):
    def export(self, rows: list[dict]) -> str:
        import json
        return json.dumps(rows)


def create_exporter(fmt: str) -> Exporter:
    """The 'factory method', reduced to a single dict lookup."""
    try:
        exporter_cls = _EXPORTER_REGISTRY[fmt]
    except KeyError:
        raise ValueError(f"unsupported format: {fmt}") from None
    return exporter_cls()


def export_report(fmt: str, rows: list[dict]) -> str:
    exporter = create_exporter(fmt)
    print(f"  [registry] running report job via {type(exporter).__name__}")
    return exporter.export(rows)


# ============================================================
# Key Takeaways
# ============================================================
# - Factory Method's real job is decoupling "what gets built" from "how it gets used" — client
#   code should only ever depend on the abstract Product interface, never on concrete classes.
# - The classic subclass-per-product form earns its keep when each ConcreteCreator also carries
#   real *workflow* differences (not just a different product), because that's what the Template
#   Method-style `run()` is for. If creators differ only in which product they hand back, that's
#   a strong signal to reach for the dict-registry version instead.
# - Common misuse: building a deep Creator/Product class hierarchy for a handful of stateless
#   product types that would be perfectly served by `{"name": ClassOrFunction}` and a decorator.
# - Related pattern to compare: Abstract Factory (#3) — a step up from Factory Method for when
#   you need a whole *family* of related products built consistently together.


if __name__ == "__main__":
    rows = [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Grace"}]

    print("--- Anti-pattern: if/elif chain hard-codes every format in one place ---")
    print(export_report_naive("csv", rows))
    try:
        export_report_naive("xml", rows)
    except ValueError as e:
        print(f"expected failure: {e}  <- xml was never wired into the chain")

    print("\n--- Classic: one ReportJob subclass per format, each owns its factory method ---")
    for job in (CsvReportJob(), JsonReportJob(), XmlReportJob()):
        result = job.run(rows)
        print(f"  -> {result}")
    assert isinstance(CsvReportJob().make_exporter(), ClassicCsvExporter)
    assert isinstance(XmlReportJob().make_exporter(), ClassicXmlExporter)

    print("\n--- Pythonic: dict registry, new formats register themselves via @register ---")
    print(export_report("csv", rows))
    print(export_report("json", rows))

    @register("xml")
    class AdHocXmlExporter(Exporter):
        def export(self, rows: list[dict]) -> str:
            items = "".join(
                "<row>" + "".join(f"<{k}>{v}</{k}>" for k, v in row.items()) + "</row>"
                for row in rows
            )
            return f"<rows>{items}</rows>"

    print(export_report("xml", rows))  # works immediately, no ReportJob subclass needed
    assert set(_EXPORTER_REGISTRY) == {"csv", "json", "xml"}

    try:
        export_report("yaml", rows)
    except ValueError as e:
        print(f"expected failure: {e}  <- yaml was never registered")

    print("\nBoth Factory Method variants confirmed: construction decoupled from use.")
