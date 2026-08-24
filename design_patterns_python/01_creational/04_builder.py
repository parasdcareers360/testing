"""
Design Patterns in Python — #4
Builder (Creational Pattern)

Intent
------
Separate the construction of a complex object from its representation, so the same
step-by-step construction process can produce different configurations of that object — without
the constructor itself turning into an unreadable pile of positional parameters.

Problem / Motivation
---------------------
Say a game needs to spawn enemy characters that vary along many independent axes: base stats,
equipped weapon, armor, resistances, AI behavior, loot table, optional aura effects. A single
constructor that takes all of this ends up with a dozen-plus parameters, most of them optional,
and callers either pass a long wall of positional args (easy to mix up two adjacent `int`
parameters) or a long wall of keyword args repeated at every call site. Worse, some combinations
are only valid if built in the right order or with the right defaults filled in consistently
(e.g. "elite" enemies always get a resistance bonus applied after their base stats are set) —
logic that has nowhere good to live in a plain constructor.

Structure
---------
A Builder declares step methods for setting each part of the product (`set_weapon`,
`add_resistance`, ...) and a final `build()` that returns the assembled product. A Director
(optional) encodes specific, reusable *recipes* — fixed sequences of builder calls that produce
a named configuration (e.g. "build a standard elite orc"). Client code either drives the builder
directly for one-off custom objects, or hands the builder to a Director for a canned recipe.

When to Use
-----------
- An object has many optional parts or configuration axes, and most call sites only need to set
  a handful of them.
- Construction has an inherent multi-step process, order-dependent logic, or validation that
  doesn't fit cleanly in `__init__`.
- You want to reuse the *same* construction recipe to produce several similarly-configured
  objects (that's what the Director is for).

When NOT to Use
----------------
- If an object has few enough parameters that Python's own keyword arguments (or a `@dataclass`
  with sensible defaults) already read clearly at the call site, a full Builder class is
  ceremony you don't need — see the contrast drawn in Implementation 2 below.
- Don't reach for a Director unless you actually have more than one reusable recipe; a Director
  wrapping a single call sequence used in exactly one place is indirection with no payoff.

Related / Commonly Confused Patterns
--------------------------------------
- Abstract Factory (#3): both hide "how is this object put together" from the client, but
  Abstract Factory hands back one of several *complete, ready-made* families of simple objects
  in a single call; Builder assembles *one* complex object incrementally, step by step.
- Prototype (#5): an alternative way to avoid repeating expensive/complex construction — clone
  an existing configured object instead of building a new one from scratch.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


# ============================================================
# Anti-pattern: the naive way, and why it hurts
# ============================================================
# One constructor, a dozen parameters, most of them optional. Call sites become either an
# error-prone wall of positional args or a repeated wall of keywords, and there's no good place
# to put "elites always get +resistance" logic short of duplicating it at every call site.
class EnemyNaive:
    def __init__(
        self, name, hp, attack, defense, weapon, armor, resistances,
        ai_behavior, loot_table, is_elite, aura,
    ):
        self.name = name
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.weapon = weapon
        self.armor = armor
        self.resistances = resistances
        self.ai_behavior = ai_behavior
        self.loot_table = loot_table
        self.is_elite = is_elite
        self.aura = aura

    def __repr__(self):
        return f"Enemy({self.name}, hp={self.hp}, elite={self.is_elite}, aura={self.aura})"


def spawn_elite_orc_naive() -> EnemyNaive:
    # Every "elite orc" spawn site has to remember to replicate this exact combination by hand.
    return EnemyNaive(
        "Orc", 80, 12, 8, "Greataxe", "Plate", ["fire"], "aggressive", "orc_loot", True, "rage",
    )


# ============================================================
# Implementation 1: Classic (OOP / GoF-style, explicit Builder class + Director)
# ============================================================
# Idea: each step method configures one part of the product and returns nothing (the classic
# GoF form) — the builder accumulates state internally, and only build() hands back the finished
# object. A Director encodes named, reusable recipes ("elite orc", "trash goblin") as fixed
# sequences of builder calls, so that recipe only has to be written once.
@dataclass
class Enemy:
    name: str
    hp: int = 10
    attack: int = 1
    defense: int = 0
    weapon: str = "fists"
    armor: str = "none"
    resistances: list = field(default_factory=list)
    ai_behavior: str = "passive"
    loot_table: str = "common"
    is_elite: bool = False
    aura: str | None = None


class EnemyBuilder(ABC):
    @abstractmethod
    def set_base_stats(self, hp: int, attack: int, defense: int) -> None: ...

    @abstractmethod
    def set_equipment(self, weapon: str, armor: str) -> None: ...

    @abstractmethod
    def set_behavior(self, ai_behavior: str, loot_table: str) -> None: ...

    @abstractmethod
    def make_elite(self, aura: str) -> None: ...

    @abstractmethod
    def build(self) -> Enemy: ...


class ClassicEnemyBuilder(EnemyBuilder):
    def __init__(self, name: str):
        self._enemy = Enemy(name=name)

    def set_base_stats(self, hp: int, attack: int, defense: int) -> None:
        self._enemy.hp = hp
        self._enemy.attack = attack
        self._enemy.defense = defense

    def set_equipment(self, weapon: str, armor: str) -> None:
        self._enemy.weapon = weapon
        self._enemy.armor = armor

    def set_behavior(self, ai_behavior: str, loot_table: str) -> None:
        self._enemy.ai_behavior = ai_behavior
        self._enemy.loot_table = loot_table

    def make_elite(self, aura: str) -> None:
        # Order-dependent business rule that has nowhere clean to live in a plain constructor:
        # elites get their defense boosted, gain a resistance, and get an aura.
        self._enemy.is_elite = True
        self._enemy.defense += 4
        self._enemy.resistances.append("fire")
        self._enemy.aura = aura

    def build(self) -> Enemy:
        return self._enemy


class EnemyDirector:
    """Encodes reusable spawn recipes as fixed sequences of builder calls."""

    @staticmethod
    def build_elite_orc(builder: EnemyBuilder) -> Enemy:
        builder.set_base_stats(hp=80, attack=12, defense=8)
        builder.set_equipment(weapon="Greataxe", armor="Plate")
        builder.set_behavior(ai_behavior="aggressive", loot_table="orc_loot")
        builder.make_elite(aura="rage")
        return builder.build()

    @staticmethod
    def build_trash_goblin(builder: EnemyBuilder) -> Enemy:
        builder.set_base_stats(hp=15, attack=3, defense=1)
        builder.set_equipment(weapon="Dagger", armor="Rags")
        builder.set_behavior(ai_behavior="skittish", loot_table="goblin_loot")
        return builder.build()


# ============================================================
# Implementation 2: Pythonic idiom (fluent/chainable builder)
# ============================================================
# Idea: the same step-by-step assembly, but each step method returns `self`, so calls chain
# into one readable expression at the call site instead of a sequence of separate statements.
# This is a genuinely more Pythonic *feel* (mirrors stdlib/3rd-party fluent APIs like
# `pathlib.Path` chaining or query builders) even though the structure underneath is the same
# idea as the classic form. For enemies with only a few commonly-set fields and no order-
# dependent rules, a plain @dataclass with keyword defaults (shown in __main__) is honestly
# simpler than reaching for either Builder form — Builder earns its keep when there's real
# multi-step logic (like make_elite's stat-boost rule) to encapsulate.
class FluentEnemyBuilder:
    def __init__(self, name: str):
        self._enemy = Enemy(name=name)

    def with_base_stats(self, hp: int, attack: int, defense: int) -> "FluentEnemyBuilder":
        self._enemy.hp = hp
        self._enemy.attack = attack
        self._enemy.defense = defense
        return self

    def with_equipment(self, weapon: str, armor: str) -> "FluentEnemyBuilder":
        self._enemy.weapon = weapon
        self._enemy.armor = armor
        return self

    def with_behavior(self, ai_behavior: str, loot_table: str) -> "FluentEnemyBuilder":
        self._enemy.ai_behavior = ai_behavior
        self._enemy.loot_table = loot_table
        return self

    def as_elite(self, aura: str) -> "FluentEnemyBuilder":
        self._enemy.is_elite = True
        self._enemy.defense += 4
        self._enemy.resistances.append("fire")
        self._enemy.aura = aura
        return self

    def build(self) -> Enemy:
        return self._enemy


# ============================================================
# Key Takeaways
# ============================================================
# - Builder's real value is encapsulating multi-step, order-dependent construction logic (like
#   "elites get +defense, a resistance, and an aura, in that order") in one place, instead of
#   duplicating it at every call site that needs an elite enemy.
# - The Director is only worth having when there's more than one reusable recipe; for a single
#   one-off configuration, drive the builder directly.
# - Common misuse: reaching for a full Builder (classic or fluent) when a `@dataclass` with
#   keyword-argument defaults would read just as clearly and needs no extra class — Python's
#   native keyword args already solve "too many constructor parameters" for the simple case.
#   Builder earns the extra machinery specifically when steps have order or validation rules.
# - Related pattern to compare: Prototype (#5) — instead of re-running an expensive build
#   recipe, clone an already-built object and tweak the copy.


if __name__ == "__main__":
    print("--- Anti-pattern: wall of positional args, elite logic duplicated by hand ---")
    naive_orc = spawn_elite_orc_naive()
    print(naive_orc)

    print("\n--- Classic: explicit Builder + Director recipes ---")
    orc = EnemyDirector.build_elite_orc(ClassicEnemyBuilder("Orc"))
    goblin = EnemyDirector.build_trash_goblin(ClassicEnemyBuilder("Goblin"))
    print(orc)
    print(goblin)
    assert orc.is_elite and orc.defense == 12  # 8 base + 4 elite bonus
    assert orc.aura == "rage" and "fire" in orc.resistances
    assert not goblin.is_elite and goblin.aura is None

    print("\n--- Pythonic: fluent chainable builder ---")
    elite_troll = (
        FluentEnemyBuilder("Troll")
        .with_base_stats(hp=120, attack=18, defense=10)
        .with_equipment(weapon="Club", armor="Hide")
        .with_behavior(ai_behavior="berserk", loot_table="troll_loot")
        .as_elite(aura="regeneration")
        .build()
    )
    print(elite_troll)
    assert elite_troll.is_elite and elite_troll.defense == 14  # 10 base + 4 elite bonus
    assert elite_troll.aura == "regeneration"

    print("\n--- When Builder is overkill: a plain dataclass with keyword defaults ---")
    simple_rat = Enemy(name="Rat", hp=5, attack=1)  # no multi-step logic needed, kwargs suffice
    print(simple_rat)
    assert simple_rat.hp == 5 and not simple_rat.is_elite

    print("\nBoth Builder variants confirmed: complex, order-dependent construction encapsulated.")
