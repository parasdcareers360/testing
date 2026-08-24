"""
Design Patterns in Python — #11
Flyweight (Structural Pattern)

Intent
------
Support huge numbers of fine-grained objects efficiently by sharing whatever state is identical
across many of them (the "intrinsic" state) and keeping only what genuinely varies per-object
(the "extrinsic" state) outside the shared part. Instead of one fat object per logical entity,
you get one shared lightweight object per *distinct combination of shared data*, referenced by
many cheap per-entity records that carry just the varying bits.

Problem / Motivation
---------------------
A forest-rendering scene needs to draw 100,000 trees. Each tree has a species-specific mesh and
texture (a few megabytes of geometry/pixel data) and its own position and scale in the world. If
every Tree object stores its own copy of the mesh and texture, you're paying for the same few
megabytes of oak-tree geometry 40,000 times over just because there are 40,000 oak trees at
different spots — the mesh and texture never actually differ between two oaks, only the position
does. That's not "the price of realism," it's pure waste: the same bytes, held redundantly,
purely because nothing separated "data every oak shares" from "data unique to this one oak."

Structure
---------
Intrinsic state (mesh, texture — identical for every tree of a species, context-independent) is
held once inside a shared, immutable `TreeType` (Flyweight) object. Extrinsic state (x, y,
scale — different per tree, supplied by the caller at the point of use) lives in a separate,
lightweight `Tree` record that references its shared `TreeType` instead of duplicating it. A
`TreeFactory` pool guarantees that requesting the same species twice returns the *same*
`TreeType` object rather than building a new one — the object-count savings come entirely from
that pool's deduplication.

When to Use
-----------
- You need a very large number of objects, and profiling (or straightforward accounting) shows
  most of their per-object memory is data that's actually identical across large groups of them.
- The shared data is naturally immutable (or can be made so) — flyweights being mutated by one
  holder and silently affecting every other holder is the classic way this pattern goes wrong.
- The varying (extrinsic) part is small and cheap to pass around or store separately.

When NOT to Use
----------------
- Don't reach for it prematurely — it trades simplicity for memory savings, and that trade only
  pays off at real scale (thousands+ of near-duplicate objects). At small counts, the pool and
  intrinsic/extrinsic split are just extra machinery for no measurable benefit.
- Don't use it when "shared" state isn't actually safe to share — if two logical entities need
  independent mutable copies of what looks like the same data, sharing it is a correctness bug,
  not an optimization.

Related / Commonly Confused Patterns
--------------------------------------
- Singleton: Singleton caps a *class* at one instance total; Flyweight caps the number of
  *distinct combinations of shared state* to one instance each, while still allowing many of
  them (one per species here, not one tree total) plus many separate lightweight referencers.
- Object Pool: superficially similar (both hand out cached objects instead of constructing new
  ones), but Object Pool recycles *mutable* objects for reuse one-at-a-time (e.g. checked in/out
  by a caller); Flyweight shares *immutable* objects concurrently among many holders at once.
"""

from dataclasses import dataclass


# ============================================================
# Anti-pattern: the naive way, and why it hurts
# ============================================================
# Every Tree carries its own full copy of mesh_data and texture_data, even though every oak in
# the forest has byte-for-byte identical mesh/texture. Planting 100,000 trees means allocating
# 100,000 independent copies of that "heavy" data — most of it pure duplication.
class TreeNaive:
    def __init__(self, x: float, y: float, species: str, mesh_data: str, texture_data: str):
        self.x = x
        self.y = y
        self.species = species
        self.mesh_data = mesh_data  # pretend this is a multi-MB mesh, duplicated every time
        self.texture_data = texture_data  # pretend this is a multi-MB texture, duplicated too


def plant_forest_naive(count: int) -> list[TreeNaive]:
    trees = []
    for i in range(count):
        # Same "heavy" mesh/texture string rebuilt and attached to every single tree.
        trees.append(TreeNaive(
            x=float(i % 100), y=float(i // 100), species="oak",
            mesh_data="OAK_MESH_BYTES" * 1000, texture_data="OAK_BARK_TEXTURE" * 1000,
        ))
    return trees


# ============================================================
# Implementation 1: Classic (OOP / GoF-style — Flyweight + Factory pool)
# ============================================================
# TreeType holds only intrinsic (shared, immutable) state: species, mesh, texture. TreeFactory
# is the pool — it hands out the SAME TreeType instance for a given species every time, building
# a new one only the first time that species is requested. Tree (the "context" object) is cheap:
# it holds just extrinsic state (x, y, scale) plus a reference to its shared TreeType.
@dataclass(frozen=True)
class TreeType:
    """Intrinsic state: identical for every tree of this species. Immutable and shared."""
    species: str
    mesh_data: str
    texture_data: str


class TreeFactory:
    _pool: dict[str, TreeType] = {}

    @classmethod
    def get_tree_type(cls, species: str) -> TreeType:
        if species not in cls._pool:
            print(f"  [factory] building NEW TreeType for species={species!r} (cache miss)")
            cls._pool[species] = TreeType(
                species=species,
                mesh_data=f"{species.upper()}_MESH_BYTES" * 1000,
                texture_data=f"{species.upper()}_TEXTURE_BYTES" * 1000,
            )
        return cls._pool[species]

    @classmethod
    def distinct_type_count(cls) -> int:
        return len(cls._pool)


class Tree:
    """Extrinsic state only: position and scale differ per tree; the type is shared."""

    __slots__ = ("x", "y", "scale", "tree_type")

    def __init__(self, x: float, y: float, scale: float, tree_type: TreeType):
        self.x = x
        self.y = y
        self.scale = scale
        self.tree_type = tree_type  # reference to a SHARED TreeType, not a private copy

    def render(self) -> str:
        t = self.tree_type
        return f"{t.species} @ ({self.x:.0f},{self.y:.0f}) scale={self.scale} [{id(t)}]"


def plant_forest_flyweight(count: int, species_cycle: list[str]) -> list[Tree]:
    trees = []
    for i in range(count):
        species = species_cycle[i % len(species_cycle)]
        tree_type = TreeFactory.get_tree_type(species)  # shared, deduplicated by the pool
        trees.append(Tree(x=float(i % 100), y=float(i // 100), scale=1.0, tree_type=tree_type))
    return trees


# ============================================================
# Implementation 2: Pythonic idiom (functools.lru_cache as the flyweight pool)
# ============================================================
# The GoF factory pool is just memoization: "give me the shared object for this key, building it
# only once." Python's stdlib already has a decorator for exactly that. lru_cache keyed on the
# species name replaces TreeFactory's manual dict + if-not-in-pool check with one line — same
# sharing guarantee (same arguments -> same returned object), far less boilerplate.
from functools import lru_cache


@lru_cache(maxsize=None)
def get_tree_type_cached(species: str) -> TreeType:
    print(f"  [lru_cache] building NEW TreeType for species={species!r} (cache miss)")
    return TreeType(
        species=species,
        mesh_data=f"{species.upper()}_MESH_BYTES" * 1000,
        texture_data=f"{species.upper()}_TEXTURE_BYTES" * 1000,
    )


def plant_forest_pythonic(count: int, species_cycle: list[str]) -> list[Tree]:
    trees = []
    for i in range(count):
        species = species_cycle[i % len(species_cycle)]
        tree_type = get_tree_type_cached(species)
        trees.append(Tree(x=float(i % 100), y=float(i // 100), scale=1.0, tree_type=tree_type))
    return trees


# ============================================================
# Key Takeaways
# ============================================================
# - Flyweight only pays off once you correctly separate intrinsic (shared, immutable, factored
#   out) from extrinsic (per-instance, kept small) state — get that split wrong and you either
#   lose the memory savings or accidentally share data that shouldn't be shared.
# - The savings are structural, not incidental: N tree instances but only as many TreeType
#   objects as there are distinct species, no matter how large N grows.
# - functools.lru_cache turns "build a factory pool class" into "decorate a builder function" —
#   a good example of a GoF pattern collapsing into a one-line stdlib idiom in Python.
# - Common misuse: applying Flyweight to state that only *looks* identical today but is actually
#   expected to vary per-instance later — that's a correctness bug waiting to happen, not an
#   optimization. Compare against Object Pool, which recycles mutable objects instead.


if __name__ == "__main__":
    N = 10_000

    print("--- Anti-pattern: every tree duplicates its mesh/texture data ---")
    naive_trees = plant_forest_naive(N)
    naive_object_count = sum(1 for _ in naive_trees)
    naive_heavy_copies = len(naive_trees)  # one mesh/texture copy PER TREE
    print(f"  planted {naive_object_count} trees")
    print(f"  distinct mesh/texture copies in memory: {naive_heavy_copies}  <- one per tree!")

    print("\n--- Classic: TreeFactory pool shares TreeType across all trees of a species ---")
    species_mix = ["oak", "pine", "birch"]
    flyweight_trees = plant_forest_flyweight(N, species_mix)
    print(f"  planted {len(flyweight_trees)} trees")
    print(f"  distinct TreeType objects created: {TreeFactory.distinct_type_count()}")
    assert len(flyweight_trees) == N
    assert TreeFactory.distinct_type_count() == len(species_mix)
    # Every oak tree really does point at the exact same TreeType instance.
    oaks = [t for t in flyweight_trees if t.tree_type.species == "oak"]
    assert all(t.tree_type is oaks[0].tree_type for t in oaks)
    print(f"  all {len(oaks)} oak trees share one TreeType instance (id={id(oaks[0].tree_type)})")

    print("\n--- Pythonic: same guarantee via functools.lru_cache ---")
    get_tree_type_cached.cache_clear()
    pythonic_trees = plant_forest_pythonic(N, species_mix)
    cache_info = get_tree_type_cached.cache_info()
    print(f"  planted {len(pythonic_trees)} trees")
    print(f"  distinct TreeType objects created (cache misses): {cache_info.misses}")
    print(f"  TreeType lookups served from cache (hits): {cache_info.hits}")
    assert cache_info.misses == len(species_mix)
    assert cache_info.hits == N - len(species_mix)

    print(f"\n{N} trees planted; only {len(species_mix)} heavy TreeType objects ever built.")
