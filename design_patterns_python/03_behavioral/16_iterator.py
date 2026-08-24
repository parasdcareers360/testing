"""
Design Patterns in Python — #16
Iterator (Behavioral Pattern)

Intent
------
Provide a way to access the elements of a collection sequentially without exposing how that
collection is actually stored or laid out internally. The client just asks "give me the next
element" repeatedly; it never needs to know whether the underlying structure is a list, a tree,
paginated API responses, or something more exotic — and multiple independent traversals of the
same collection can be in progress at once, each with its own position.

Problem / Motivation
---------------------
Imagine a paginated API client wrapping a search endpoint: results come back a page at a time,
and the caller wants to loop over *all* matching records as if they were one flat sequence.
Without Iterator, callers end up hand-rolling pagination themselves everywhere they need
results: tracking a `page` variable, calling `fetch_page(page)`, checking whether the page is
empty, flattening `page["items"]` into their own loop, and incrementing `page` — repeated at
every call site, with every caller responsible for getting the "am I done yet" check right. Leak
one off-by-one bug in that logic in one call site and you silently drop or duplicate the last
page's records there while other call sites remain unaffected — no single place owns "how do I
walk this collection correctly."

Structure
---------
An Iterable (the collection) exposes a method that returns an Iterator; the Iterator object
holds the traversal position and exposes a uniform "get next element" / "is there more"
interface. The client drives the Iterator through that uniform interface without ever touching
the collection's internal storage directly. In Python this maps onto the built-in iterator
protocol: an iterable implements `__iter__`, and the iterator it returns implements `__next__`
(raising `StopIteration` when exhausted) — which is exactly what powers every `for` loop.

When to Use
-----------
- You want to traverse a collection without exposing its internal representation, or support
  more than one simultaneous, independent traversal over the same collection.
- The underlying data isn't naturally a flat, already-in-memory sequence (paginated API results,
  a tree walked in a specific order, a stream) and you want callers to loop over it as if it
  were one anyway.

When NOT to Use
----------------
- In Python, don't hand-roll an explicit iterator class for something a generator function can
  express in a few lines — the language gives you the pattern for free via `yield`; reaching for
  a full `__iter__`/`__next__` class by default is fighting the language rather than using it
  (see Implementation 2 below for exactly this contrast).
- If the whole collection already comfortably fits in memory and is only ever traversed once in
  a simple way, plain list iteration needs no pattern at all.

Related / Commonly Confused Patterns
--------------------------------------
- Composite: Iterator is frequently used to traverse a Composite's tree structure uniformly
  (e.g. walking every leaf of a nested structure without the client caring about tree depth).
- Visitor: both let you process elements of a structure without changing the structure's
  classes, but Iterator is about *order of access* (what's next), while Visitor is about
  *what operation* runs on each element once you're there — they compose well together.
"""


# ============================================================
# Anti-pattern: the naive way, and why it hurts
# ============================================================
# Every caller that wants "all results" has to re-implement pagination by hand: track a page
# index, fetch it, flatten it, check for the end. That logic -- and any bug in it -- is
# duplicated at every call site instead of living in exactly one place.
class PaginatedSearchAPI:
    """Pretend this hits a real paginated search endpoint."""

    def __init__(self, all_results: list[str], page_size: int = 3):
        self._all_results = all_results
        self._page_size = page_size

    def fetch_page(self, page: int) -> list[str]:
        start = page * self._page_size
        return self._all_results[start : start + self._page_size]


def print_all_results_naive(api: PaginatedSearchAPI) -> list[str]:
    collected = []
    page = 0
    while True:
        items = api.fetch_page(page)
        if not items:
            break
        collected.extend(items)
        page += 1
    return collected
    # ^ every caller who wants "all results" re-writes this exact loop, with its own chance to
    #   get the empty-page termination check wrong.


# ============================================================
# Implementation 1: Classic (OOP / GoF-style, explicit Iterator class with __iter__/__next__)
# ============================================================
# Idea: pagination logic is written EXACTLY ONCE, inside SearchResultIterator. The API object
# just hands out a fresh iterator; the iterator owns the "current page" state machine and
# implements Python's real iterator protocol, so it plugs directly into `for`/`next()`/`iter()`
# like any built-in sequence would.
class SearchResultIterator:
    def __init__(self, api: PaginatedSearchAPI):
        self._api = api
        self._current_page: list[str] = []
        self._page_index = 0
        self._position_in_page = 0
        self._exhausted = False

    def __iter__(self) -> "SearchResultIterator":
        return self  # an iterator is its own __iter__, per the protocol

    def __next__(self) -> str:
        if self._position_in_page >= len(self._current_page):
            if self._exhausted:
                raise StopIteration
            self._current_page = self._api.fetch_page(self._page_index)
            self._page_index += 1
            self._position_in_page = 0
            if not self._current_page:
                self._exhausted = True
                raise StopIteration
        item = self._current_page[self._position_in_page]
        self._position_in_page += 1
        return item


class IterableSearchResults:
    """The Iterable: knows nothing about traversal state, just hands out fresh iterators."""

    def __init__(self, api: PaginatedSearchAPI):
        self._api = api

    def __iter__(self) -> SearchResultIterator:
        return SearchResultIterator(self._api)  # a NEW iterator each time -> independent walks


# ============================================================
# Implementation 2: Pythonic idiom (a generator function doing the exact same traversal)
# ============================================================
# Idea: the entire state machine above (current page, position in page, exhausted flag) is
# exactly what a generator function tracks FOR you, automatically, via `yield` -- the local
# variables in a normal-looking while-loop become the "traversal state" for free, and
# StopIteration is raised for you when the function returns. Same protocol, same result, far
# less code, and no state to get wrong by hand.
def iter_search_results(api: PaginatedSearchAPI):
    page_index = 0
    while True:
        page = api.fetch_page(page_index)
        if not page:
            return  # a plain `return` inside a generator IS StopIteration -- no manual raise
        yield from page
        page_index += 1


# ============================================================
# Key Takeaways
# ============================================================
# - Both implementations satisfy the exact same protocol -- `for x in thing`, `iter(thing)`, and
#   `next(it)` all work identically on either -- because Python's `for` loop doesn't care HOW
#   __next__ is implemented, only that it follows the protocol.
# - The explicit class makes every piece of traversal state a named field you can see; the
#   generator makes that same state implicit in local variables + the paused stack frame -- same
#   information, radically less ceremony.
# - Common misuse: hand-writing a __iter__/__next__ class in Python when a generator function
#   would do, out of habit from languages (Java, C++) that have no `yield` -- reach for a
#   generator first, and only build an explicit Iterator class when you need extra methods on
#   the iterator itself (e.g. a `has_next()` peek, or resettable/seekable position).
# - Related pattern to compare: Composite -- Iterator is commonly layered on top of a Composite
#   tree to give it flat, uniform traversal.


if __name__ == "__main__":
    results_data = [f"result-{i}" for i in range(1, 8)]  # 7 results, page_size=3 -> 3 pages
    api = PaginatedSearchAPI(results_data, page_size=3)

    print("--- Anti-pattern: hand-rolled pagination loop at the call site ---")
    naive_results = print_all_results_naive(api)
    print(f"  collected {len(naive_results)} results: {naive_results}")
    assert naive_results == results_data

    print("\n--- Classic: explicit Iterator class (__iter__/__next__) ---")
    iterable = IterableSearchResults(api)
    classic_results = list(iterable)  # `list()` drives the protocol via __iter__/__next__
    print(f"  collected via for-loop-compatible class: {classic_results}")
    assert classic_results == results_data

    # Two independent traversals over the same iterable, proving position isn't shared state:
    it_a = iter(iterable)
    it_b = iter(iterable)
    assert next(it_a) == "result-1"
    assert next(it_a) == "result-2"
    assert next(it_b) == "result-1"  # it_b is unaffected by it_a's progress
    print("  two independent iterators over the same collection stay independent: OK")

    print("\n--- Pythonic: generator function doing the identical traversal ---")
    gen_results = list(iter_search_results(api))
    print(f"  collected via generator: {gen_results}")
    assert gen_results == results_data

    gen_a = iter_search_results(api)
    gen_b = iter_search_results(api)
    assert next(gen_a) == "result-1"
    assert next(gen_b) == "result-1"  # fresh generator call -> independent state, same as above
    print("  generator instances are independent too: OK")

    for item in iter_search_results(api):
        pass  # proves it plugs directly into a real `for` loop, not just list()

    print("\nSame protocol, same results, from an explicit state machine and from `yield` --")
    print("that's the whole lesson: `yield` gets you the pattern almost for free in Python.")
