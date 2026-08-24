"""
Design Patterns in Python — #1
Singleton (Creational Pattern)

Intent
------
Ensure a class has exactly one instance, and provide a single well-known access point to it.
Singleton exists for cases where having a *second* instance would be actively wrong — not just
wasteful, but a source of bugs — because the object represents something that is inherently
singular in the running program: one connection pool, one in-memory config, one hardware
handle.

Problem / Motivation
---------------------
Say an application loads its configuration from a file once, then reads settings from it all
over the codebase — in the request handler, in a background job, in a CLI entry point. If each
of those places just does `AppConfig()` to get a fresh instance, you get three independent
copies of "the config" that can silently drift out of sync (one place re-reads the file with
stale disk contents, another still has the version from process start). Worse, if loading the
config is expensive (parsing a large file, hitting a secrets manager over the network), doing
it three times instead of once is a real performance and correctness problem, not just an
aesthetic one.

Structure
---------
A single class controls its own instantiation: instead of the client calling the constructor
directly and getting a brand-new object every time, the class intercepts instance creation
(via `__new__`, a metaclass, or a wrapping decorator) and returns the *same* previously-created
instance on every subsequent call. The client code doesn't need to know this is happening — it
just keeps writing `AppConfig()` as if it were a normal constructor call.

When to Use
-----------
- Exactly one instance of something must exist for the lifetime of the program (a config store,
  a connection pool, a hardware/resource handle, a logging registry).
- That single instance needs to be reachable from many unrelated parts of the codebase without
  threading it through every function signature as an explicit parameter.

When NOT to Use
----------------
- As a lazy substitute for proper dependency injection — Singletons make unit testing harder
  (global, shared, hard-to-reset state) and hide a class's dependencies. If you can pass the
  instance in explicitly instead, that's usually the better design.
- For anything that might legitimately need multiple instances later (e.g. "the database
  connection" often needs to become "one connection per tenant" — a Singleton bakes in an
  assumption that's easy to regret).

Related / Commonly Confused Patterns
--------------------------------------
- Borg / Monostate pattern: a lesser-known Python alternative that allows multiple instances
  but forces them all to share the same `__dict__` — same shared-state effect as Singleton,
  without funneling every call through one object identity. Shown below as part of the
  Pythonic implementation's sibling techniques.
- Facade: often implemented as a Singleton in practice (one facade object), but the two
  patterns solve different problems — Facade is about simplifying an interface, Singleton is
  about instance cardinality.
"""


# ============================================================
# Anti-pattern: the naive way, and why it hurts
# ============================================================
# Every call to AppConfigNaive() re-reads and re-parses "the file" from scratch, and each
# caller ends up holding its own independent copy. Two calls produce two different objects
# with (at first) equal contents — but nothing stops them from drifting apart, and the
# "expensive load" work happens every single time instead of once.
class AppConfigNaive:
    def __init__(self, source: dict):
        print("  [naive] loading config from source (expensive!)...")
        self._settings = dict(source)  # pretend this parsed a file / called a secrets API

    def get(self, key: str):
        return self._settings.get(key)

    def set(self, key: str, value) -> None:
        self._settings[key] = value


# ============================================================
# Implementation 1: Classic (OOP / GoF-style, via __new__ override)
# ============================================================
# Idea: intercept object creation at the lowest level Python offers — __new__ — rather than
# __init__. __new__ is what actually allocates the instance; by checking a class-level cache
# there first, we can return an already-built instance and skip allocation entirely for every
# call after the first. __init__ still runs on every call (that's how Python works), so we
# guard the expensive setup work with an `_initialized` flag to avoid redoing it.
class AppConfigSingleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, source: dict | None = None):
        if self._initialized:
            return
        print("  [classic] loading config from source (expensive!)...")
        self._settings = dict(source or {})
        self._initialized = True

    def get(self, key: str):
        return self._settings.get(key)

    def set(self, key: str, value) -> None:
        self._settings[key] = value


# ============================================================
# Implementation 2: Pythonic idiom (module-level instance + a decorator variant)
# ============================================================
# Idea: Python modules are only imported (and therefore only executed) once per process, and
# the module object itself is cached by the interpreter — so a plain module-level object IS a
# singleton, for free, with none of the __new__/metaclass machinery. This is the most
# "Pythonic" answer to Singleton: don't fight the language, use the guarantee it already gives
# you. A second common idiom is a `@singleton` class decorator, shown here too, which is handy
# when you want singleton *behavior* attached to a class definition without changing what the
# class itself looks like internally (no __new__ override needed inside the class body).
def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


@singleton
class AppConfigDecorated:
    def __init__(self, source: dict | None = None):
        print("  [decorated] loading config from source (expensive!)...")
        self._settings = dict(source or {})

    def get(self, key: str):
        return self._settings.get(key)

    def set(self, key: str, value) -> None:
        self._settings[key] = value


# The "just use the module" version — see how AppConfig-as-a-plain-object further down in
# __main__ uses this by importing the same module twice conceptually (simulated with a plain
# global object here, since we're in one file):
_module_level_config = {"loaded": False, "settings": {}}


def get_module_config(source: dict | None = None) -> dict:
    if not _module_level_config["loaded"]:
        print("  [module-level] loading config from source (expensive!)...")
        _module_level_config["settings"] = dict(source or {})
        _module_level_config["loaded"] = True
    return _module_level_config["settings"]


# ============================================================
# Key Takeaways
# ============================================================
# - Singleton is fundamentally about controlling *identity* (there is exactly one object), not
#   just about sharing data — that's why it's implemented by intercepting construction
#   (__new__, a metaclass, or a decorator), not by adding a "shared" flag to a normal class.
# - In Python, a module-level object is very often the simplest correct Singleton: modules are
#   cached by the import system, so `import app_config; app_config.SETTINGS` already gives you
#   "load once, share everywhere" without any special-case code.
# - Common misuse: reaching for Singleton to avoid passing an object around explicitly. That
#   convenience comes at the cost of hidden global state, which makes tests fragile (state
#   leaks between test cases unless you remember to reset the singleton) and makes a class's
#   real dependencies invisible from its constructor signature.
# - Related pattern to compare: Borg/Monostate — multiple instances, shared __dict__ — solves
#   the "shared state" half of Singleton's job without forcing single identity.


if __name__ == "__main__":
    print("--- Anti-pattern: two calls, two independent (and now diverging) objects ---")
    cfg_a = AppConfigNaive({"env": "prod"})
    cfg_b = AppConfigNaive({"env": "prod"})  # reloads "expensively" a second time
    cfg_a.set("feature_x_enabled", True)
    print(f"cfg_a is cfg_b: {cfg_a is cfg_b}")
    print(f"cfg_a sees feature_x_enabled: {cfg_a.get('feature_x_enabled')}")
    print(f"cfg_b sees feature_x_enabled: {cfg_b.get('feature_x_enabled')}  <- drifted!")
    assert cfg_a is not cfg_b
    assert cfg_a.get("feature_x_enabled") != cfg_b.get("feature_x_enabled")

    print("\n--- Classic (__new__ override): one real instance, load runs once ---")
    s1 = AppConfigSingleton({"env": "prod"})
    s2 = AppConfigSingleton({"env": "this argument is ignored, s1 already exists"})
    s1.set("feature_x_enabled", True)
    print(f"s1 is s2: {s1 is s2}")
    print(f"s2 sees feature_x_enabled: {s2.get('feature_x_enabled')}  <- shared, no drift")
    assert s1 is s2
    assert s2.get("feature_x_enabled") is True

    print("\n--- Pythonic: @singleton decorator ---")
    d1 = AppConfigDecorated({"env": "prod"})
    d2 = AppConfigDecorated({"env": "ignored"})
    print(f"d1 is d2: {d1 is d2}")
    assert d1 is d2

    print("\n--- Pythonic: plain module-level cache (no class machinery at all) ---")
    m1 = get_module_config({"env": "prod"})
    m2 = get_module_config({"env": "ignored"})
    print(f"m1 is m2: {m1 is m2}")
    assert m1 is m2

    print("\nAll Singleton variants confirmed: one shared instance, load-once semantics.")
