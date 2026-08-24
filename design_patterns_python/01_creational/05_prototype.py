"""
Design Patterns in Python — #5
Prototype (Creational Pattern)

Intent
------
Specify the kinds of objects to create using a pre-configured prototypical instance, and create
new objects by *copying* that prototype rather than by re-running its (possibly expensive or
complex) construction process from scratch. In Python specifically, this pattern lives and dies
on getting the copy semantics right — a naive copy of an object with nested mutable state (a
list, a dict, a nested object) doesn't actually give you an independent object at all.

Problem / Motivation
---------------------
Say a reporting system builds a "quarterly report" template: a title, a list of section headers,
a dict of default formatting options, and a nested `Header`/`Footer` config object. Building one
from scratch means re-running several steps of setup. It's much cheaper to build one canonical
template once and hand out copies for each new report that starts "like the template, with a few
tweaks." The trap: if you copy that template with plain assignment, or even with a shallow
`copy.copy`, the new "copy" still shares the *same* underlying `sections` list and `options`
dict objects as the original — mutating one report's sections silently corrupts every other
report that came from the same template, because there's really only one list, referenced twice.

Structure
---------
A Prototype declares a `clone()` method that returns a new, independent instance with the same
state as `self`. ConcretePrototypes implement it (typically via `copy.deepcopy`, sometimes via a
custom `clone()` that only deep-copies the fields that actually need it). Client code asks an
existing, already-configured prototype instance to clone itself, rather than calling that
class's constructor and re-supplying all the configuration again.

When to Use
-----------
- Building an object from scratch is expensive (heavy computation, I/O, deeply nested default
  configuration) compared to copying an already-built one.
- You want to hand out variations of a canonical "template" object without mutating the
  template itself or re-running its setup for every variation.
- The concrete class of the object to copy is only known at runtime (you have an instance, not
  necessarily easy access to reconstruct its exact type and constructor arguments).

When NOT to Use
----------------
- If construction is cheap and state is simple (a few immutable fields, no nested mutable
  containers), cloning buys nothing over just calling the constructor again — it's an extra
  concept for no benefit.
- Don't reach for a custom hand-rolled `clone()` before checking whether `copy.deepcopy` already
  does exactly what you need; only write custom clone logic when some fields genuinely shouldn't
  be deep-copied (e.g. a shared read-only resource handle that *should* stay shared across
  clones).

Related / Commonly Confused Patterns
--------------------------------------
- Builder (#4): an alternative way to avoid repeating expensive construction — Builder
  re-*runs* a construction recipe with different parameters; Prototype skips construction
  entirely and copies an already-finished object.
- Memento (behavioral, #18): both involve copying object state, but Memento's copy is for
  *restoring* a previous state of the same object (undo), not for producing a new, independent
  object to hand to a different client.
"""

import copy
from dataclasses import dataclass, field


# ============================================================
# Anti-pattern: the naive way, and why it hurts
# ============================================================
# `report_b = report_a` is obviously just an alias, not a copy -- nobody writes that on purpose.
# The real trap is `copy.copy` (shallow copy): it DOES create a new ReportTemplate object, so it
# *looks* like an independent copy. But shallow copy only copies the top-level attributes -- the
# `sections` list and `options` dict inside are still the exact same list/dict objects, shared
# between "original" and "copy". Mutating the copy's sections corrupts the original's too.
class ReportTemplateNaive:
    def __init__(self, title, sections, options):
        self.title = title
        self.sections = sections
        self.options = options

    def __repr__(self):
        return f"ReportTemplateNaive({self.title!r}, sections={self.sections}, options={self.options})"


# ============================================================
# Implementation 1: Classic (explicit clone() method + shallow-vs-deep copy in practice)
# ============================================================
# Idea: ReportTemplate owns an explicit clone() method, so callers never have to remember to
# reach for copy.deepcopy themselves -- correctness of the copy is the prototype's own
# responsibility. Internally it uses copy.deepcopy specifically because sections/options/header
# are nested mutable containers; deepcopy walks the whole object graph and rebuilds every nested
# container too, so the clone shares NO mutable state with the original.
@dataclass
class HeaderConfig:
    logo_path: str
    color_scheme: list[str]


@dataclass
class ReportTemplate:
    title: str
    sections: list[str]
    options: dict
    header: HeaderConfig

    def clone(self) -> "ReportTemplate":
        return copy.deepcopy(self)


def build_quarterly_template() -> ReportTemplate:
    # Pretend this setup is expensive: pulling default section names and formatting options
    # from a database, validating them, etc. We do this once and clone the result afterward.
    print("  [classic] building canonical quarterly report template (expensive)...")
    return ReportTemplate(
        title="Quarterly Report",
        sections=["Summary", "Financials", "Outlook"],
        options={"font": "Helvetica", "color": "black"},
        header=HeaderConfig(logo_path="/assets/logo.png", color_scheme=["#000", "#fff"]),
    )


# ============================================================
# Implementation 2: Pythonic idiom (copy.copy vs copy.deepcopy, and __deepcopy__ hook)
# ============================================================
# Python's stdlib `copy` module IS the idiomatic way to implement Prototype -- there's no need
# for a from-scratch clone algorithm. The two functions it gives you make the shallow/deep
# distinction explicit rather than hidden inside a clone() method, which is worth seeing
# directly at least once. `copy.copy(obj)` copies one level deep (new outer object, same inner
# references). `copy.deepcopy(obj)` recursively copies everything reachable from obj. A class
# can also customize deep-copy behavior via `__deepcopy__`, e.g. to deliberately keep one field
# shared (a read-only shared resource) while everything else is deep-copied -- shown here with
# the logo asset, which is genuinely fine to share across clones since nothing ever mutates it.
class SharedAsset:
    """Represents something intentionally safe to share unchanged across clones."""
    def __init__(self, path: str):
        self.path = path

    def __repr__(self):
        return f"SharedAsset({self.path!r})"


@dataclass
class ReportTemplateV2:
    title: str
    sections: list[str]
    options: dict
    logo: SharedAsset

    def __deepcopy__(self, memo) -> "ReportTemplateV2":
        # Deep-copy the mutable, per-report fields; deliberately keep `logo` shared -- it's an
        # immutable-in-practice shared resource, so copying it would just waste memory.
        return ReportTemplateV2(
            title=self.title,
            sections=copy.deepcopy(self.sections, memo),
            options=copy.deepcopy(self.options, memo),
            logo=self.logo,  # intentionally NOT deep-copied
        )

    def clone(self) -> "ReportTemplateV2":
        return copy.deepcopy(self)


# ============================================================
# Key Takeaways
# ============================================================
# - Prototype in Python is really a lesson about shallow vs. deep copy: `obj_b = obj_a` aliases,
#   `copy.copy(obj_a)` copies the container but shares nested mutable state, and only
#   `copy.deepcopy(obj_a)` produces a genuinely independent object graph. Reach for deepcopy by
#   default whenever the object holds nested lists/dicts/objects that clones must be free to
#   mutate independently.
# - A `clone()` method isn't strictly required in Python (you could always call
#   `copy.deepcopy(x)` directly) -- but wrapping it as a method keeps the "how do I correctly
#   copy this" decision inside the class that owns the state, instead of every call site having
#   to remember whether shallow or deep copy is safe for this particular type.
# - Common misuse/misconception: assuming `copy.copy` is "good enough" because it does produce a
#   new object -- it silently fails the moment there's a nested mutable field, which is exactly
#   the anti-pattern demonstrated above.
# - Related pattern to compare: Builder (#4) -- re-runs a construction recipe; Prototype skips
#   construction and copies a finished object instead. Use Prototype when copying is cheaper
#   than rebuilding; use Builder when each object genuinely needs fresh, recipe-driven setup.


if __name__ == "__main__":
    print("--- Anti-pattern: shallow copy.copy() shares nested mutable state ---")
    original = ReportTemplateNaive(
        title="Quarterly Report",
        sections=["Summary", "Financials", "Outlook"],
        options={"font": "Helvetica"},
    )
    shallow_copy = copy.copy(original)
    print(f"original is shallow_copy: {original is shallow_copy}  <- different objects, looks safe")
    shallow_copy.sections.append("LEAKED SECTION")  # mutating the "copy"...
    print(f"original.sections: {original.sections}  <- ...corrupted the original too!")
    assert original.sections is shallow_copy.sections  # same underlying list object
    assert "LEAKED SECTION" in original.sections

    print("\n--- Classic: clone() via copy.deepcopy(), no shared nested state ---")
    template = build_quarterly_template()
    annual_report = template.clone()
    annual_report.title = "Annual Report"
    annual_report.sections.append("Five-Year Outlook")
    annual_report.header.color_scheme.append("#f00")
    print(f"template:       {template}")
    print(f"annual_report:  {annual_report}")
    assert template.sections == ["Summary", "Financials", "Outlook"]  # untouched
    assert "Five-Year Outlook" not in template.sections
    assert template.header.color_scheme == ["#000", "#fff"]  # nested object untouched too
    assert template is not annual_report
    assert template.sections is not annual_report.sections

    print("\n--- Pythonic: custom __deepcopy__, deliberately sharing one safe field ---")
    v2_template = ReportTemplateV2(
        title="Quarterly Report",
        sections=["Summary", "Financials"],
        options={"font": "Helvetica"},
        logo=SharedAsset("/assets/logo.png"),
    )
    v2_clone = v2_template.clone()
    v2_clone.sections.append("Appendix")
    print(f"v2_template.sections: {v2_template.sections}  <- unaffected by clone's mutation")
    print(f"v2_clone.sections:    {v2_clone.sections}")
    print(f"v2_template.logo is v2_clone.logo: {v2_template.logo is v2_clone.logo}  <- shared on purpose")
    assert v2_template.sections == ["Summary", "Financials"]
    assert v2_clone.logo is v2_template.logo  # deliberately shared, not copied
    assert v2_clone.sections is not v2_template.sections  # independently copied

    print("\nPrototype confirmed: clones are independent where it matters, shared where it's safe.")
