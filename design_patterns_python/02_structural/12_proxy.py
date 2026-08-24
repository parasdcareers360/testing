"""
Design Patterns in Python — #12
Proxy (Structural Pattern)

Intent
------
Provide a stand-in object that controls access to another (usually more expensive, more
sensitive, or remote) object, implementing the same interface so client code can't tell the
difference. The proxy sits in the exact place the real object would sit and decides, on each
call, whether and how to actually involve the real object — deferring its creation, checking
permissions, adding logging, or forwarding a call across a network — all invisibly to the caller.

Problem / Motivation
---------------------
A desktop image-gallery app shows a scrolling grid of thousands of thumbnails. If opening the
gallery eagerly decodes every full-resolution image up front so each `Image` object is "ready"
before the grid even renders, the app pays the full decode cost (disk I/O + memory) for every
photo the user might *never* scroll to — startup stalls for seconds loading images nobody looks
at this session. What's actually needed is an object that *behaves* like a fully-loaded image
from the caller's point of view (the grid code shouldn't need special-case logic for "not loaded
yet") but only pays the real loading cost the first time someone actually asks to render it.

Structure
---------
Subject defines the common interface (`render()`) that both RealSubject and Proxy implement.
RealImage (RealSubject) does the expensive work (decoding the file) — normally in its
constructor. ImageProxy (Proxy) holds just the lightweight info needed to create the real thing
later (a file path) and implements the same interface; on first `render()` call it constructs
the RealImage and delegates to it, caching the result so every later call reuses it. The gallery
grid code holds a list of Subject references and never needs to know which ones are proxies.

When to Use
-----------
- Virtual Proxy: defer creating an expensive object until it's actually used (this file's focus)
  — expensive images, large documents, heavy report generators, cold database connections.
- Protection Proxy: check permissions/roles before allowing a call to reach the real object,
  without scattering access-control checks through the real object's own methods.
- Remote Proxy: present a local stand-in for an object that actually lives across a network
  (this is what RPC/gRPC client stubs are, structurally) — the caller writes normal method
  calls; the proxy handles the serialization and the trip over the wire.
- Logging/caching proxy: transparently record or memoize calls without touching the real class.

When NOT to Use
----------------
- Don't add a proxy "just in case" — if the real object is cheap to create and there's no access
  control, remoteness, or caching need, a proxy is pure indirection with no payoff.
- Don't let a proxy silently swallow or reinterpret errors from the real subject in ways that
  make debugging harder — the whole point is that it should be behaviorally transparent except
  for the one thing it's deliberately adding (deferral, access-check, logging, etc).

Related / Commonly Confused Patterns
--------------------------------------
- Decorator: structurally almost identical (both wrap an object behind the same interface), but
  intent differs — Decorator *adds new behavior/responsibilities* to an object the caller
  already has full access to; Proxy *controls access* to an object the caller might not get to
  touch directly at all (it might not even exist yet).
- Facade: Facade simplifies a *set* of different subsystem interfaces into one new, simpler one;
  Proxy implements the *same* single interface as the one real object it stands in for.
- Adapter: Adapter changes an interface to match what the caller expects; Proxy keeps the
  interface identical and changes *when/how/whether* the underlying call actually happens.
"""

from abc import ABC, abstractmethod


# ============================================================
# Anti-pattern: the naive way, and why it hurts
# ============================================================
# Building the gallery eagerly constructs every Image, and every Image decodes its full file in
# __init__. All 5,000 "expensive" decodes happen at startup, even though this run only ever
# renders 2 of them — the other 4,998 decodes were pure wasted work and wasted memory.
class ImageNaive:
    def __init__(self, filename: str):
        self.filename = filename
        print(f"  [naive] decoding full-res image from disk: {filename} (expensive!)")
        self.pixel_data = f"<decoded pixels of {filename}>"  # pretend: real, heavy decode work

    def render(self) -> str:
        return f"rendering {self.filename}: {self.pixel_data}"


def build_gallery_naive(filenames: list[str]) -> list[ImageNaive]:
    return [ImageNaive(f) for f in filenames]  # every single one decoded right now


# ============================================================
# Implementation 1: Classic (OOP / GoF-style — Virtual Proxy)
# ============================================================
# Image is the Subject interface. RealImage is the expensive RealSubject — decoding happens in
# its constructor, same as before. ImageProxy implements the SAME Image interface but only holds
# a filename until render() is actually called; it builds (and then caches) the RealImage lazily,
# so gallery code written against `Image` can't tell a proxy from the real thing except by timing.
class Image(ABC):
    @abstractmethod
    def render(self) -> str: ...


class RealImage(Image):
    def __init__(self, filename: str):
        self.filename = filename
        print(f"  [real] decoding full-res image from disk: {filename} (expensive!)")
        self.pixel_data = f"<decoded pixels of {filename}>"

    def render(self) -> str:
        return f"rendering {self.filename}: {self.pixel_data}"


class ImageProxy(Image):
    def __init__(self, filename: str):
        self.filename = filename
        self._real_image: RealImage | None = None  # not built yet — that's the whole point

    def render(self) -> str:
        if self._real_image is None:
            print(f"  [proxy] first render() of {self.filename} — building RealImage now")
            self._real_image = RealImage(self.filename)
        else:
            print(f"  [proxy] {self.filename} already loaded — reusing cached RealImage")
        return self._real_image.render()


def build_gallery_classic(filenames: list[str]) -> list[Image]:
    return [ImageProxy(f) for f in filenames]  # cheap — no decoding happens here at all


# ============================================================
# Implementation 2: Pythonic idiom (lazy loading via a property/descriptor)
# ============================================================
# The same "defer the expensive work, cache it, expose it as if it were always there" idea is
# also exactly what Python's `property` (or `functools.cached_property`) is for. Wrapping the
# lazy-build in a property is less code than a full parallel Proxy class implementing an ABC,
# and reads very naturally as "this attribute happens to be expensive the first time." The
# trade-off vs the classic version: this ISN'T interchangeable with RealImage through a shared
# abstract interface — callers must know to access `.pixels` (a property), not call an
# ABC-declared `render()` — so it fits best when you control both ends and don't need Image/
# ImageProxy to be swappable as two implementations of one formal Subject type.
from functools import cached_property


class LazyImage:
    def __init__(self, filename: str):
        self.filename = filename  # cheap: no decode happens here

    @cached_property
    def pixels(self) -> str:
        print(f"  [cached_property] first access of {self.filename} — decoding now")
        return f"<decoded pixels of {self.filename}>"

    def render(self) -> str:
        return f"rendering {self.filename}: {self.pixels}"  # triggers decode on first use only


def build_gallery_pythonic(filenames: list[str]) -> list[LazyImage]:
    return [LazyImage(f) for f in filenames]


# ============================================================
# Key Takeaways
# ============================================================
# - A proxy's defining trait is interface fidelity: it stands in for the real object well enough
#   that callers don't need to special-case "is this a proxy?" — that's what separates it from
#   just writing an `if not loaded: load()` check inline everywhere the object is used.
# - Virtual Proxy defers cost; Protection Proxy gates access; Remote Proxy hides network calls —
#   same structural shape (wrap Subject, forward to RealSubject), different reason to intercept.
# - `functools.cached_property` gives you lazy-build-once-and-cache for free on a single
#   attribute — genuinely simpler than a full Proxy class, at the cost of not being a swappable
#   implementation of a shared abstract interface with the real object.
# - Common confusion: Proxy vs Decorator look identical in code (wrap + delegate) — the tell is
#   intent: are you adding behavior to something the caller already fully has (Decorator), or
#   controlling/deferring access to something the caller shouldn't touch directly yet (Proxy)?


if __name__ == "__main__":
    files = [f"photo_{i:04d}.raw" for i in range(5000)]

    print("--- Anti-pattern: building the gallery decodes ALL 5000 images immediately ---")
    gallery_naive = build_gallery_naive(files[:5])  # trimmed to 5 just to keep output readable
    print(f"  gallery built; {len(gallery_naive)} images were decoded whether viewed or not")

    print("\n--- Classic: ImageProxy — building the gallery decodes NOTHING ---")
    gallery = build_gallery_classic(files)
    print(f"  gallery of {len(gallery)} images built — zero RealImage objects created yet")
    assert all(isinstance(img, Image) for img in gallery)

    print("  user scrolls to photo #42 and #7, and only those two get decoded:")
    gallery[42].render()
    gallery[7].render()
    gallery[42].render()  # second view — should reuse the cached RealImage, not redecode
    assert gallery[42]._real_image is not None
    assert gallery[100]._real_image is None  # never viewed -> never decoded
    print(f"  photo #100 (never viewed) still has no RealImage: "
          f"{gallery[100]._real_image is None}")

    print("\n--- Pythonic: cached_property-based lazy image ---")
    lazy_gallery = build_gallery_pythonic(files)
    print(f"  gallery of {len(lazy_gallery)} images built — no pixels decoded yet")
    lazy_gallery[42].render()
    lazy_gallery[42].render()  # cached_property: second access reuses the cached value
    assert "pixels" in lazy_gallery[42].__dict__  # cached_property stores the value on the instance
    assert "pixels" not in lazy_gallery[100].__dict__  # never accessed -> never decoded

    print("\nBoth proxies made a 5000-photo gallery instant to open by deferring real work.")
