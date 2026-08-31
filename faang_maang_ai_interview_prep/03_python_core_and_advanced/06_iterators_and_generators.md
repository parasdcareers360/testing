# Iterators and Generators

> **Type:** Study notes

## Why interviewers ask this

Generators are the difference between a script that loads a 10GB file/queryset into memory and
crashes, and one that streams it — directly relevant for a candidate with OCR/PDF batch-processing
experience, where "process 50,000 scanned pages" absolutely cannot mean "load 50,000 images into a
list first." Interviewers use this topic to check whether you understand the iterator protocol
well enough to explain *why* a generator saves memory (not just that it does), and whether you
default to streaming idioms when processing large or unbounded data — a strong signal of real
production experience vs. tutorial-level knowledge.

## The iterator protocol

An **iterable** is anything with `__iter__` (returns an iterator). An **iterator** is anything
with both `__iter__` (returns itself) and `__next__` (returns the next value or raises
`StopIteration` when exhausted). `for` loops are sugar over this protocol.

```python
class CountUp:
    """Iterator yielding 0..limit-1, implemented manually."""
    def __init__(self, limit):
        self.limit = limit
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= self.limit:
            raise StopIteration
        value = self.current
        self.current += 1
        return value

for n in CountUp(3):
    print(n)          # 0 1 2

# what `for` actually does under the hood:
it = iter(CountUp(3))
while True:
    try:
        print(next(it))
    except StopIteration:
        break
```
Writing this by hand is tedious — which is exactly the problem generator functions solve.

## Generator functions (`yield`)

Any function containing `yield` becomes a **generator function**: calling it doesn't run the body
— it returns a generator object (which implements the iterator protocol automatically). Execution
pauses at each `yield` and resumes right there on the next `next()` call, preserving all local
state between calls for free — no manual `self.current` bookkeeping needed.

```python
def count_up(limit):
    current = 0
    while current < limit:
        yield current
        current += 1

for n in count_up(3):
    print(n)          # 0 1 2 — same result as CountUp, far less code
```

## Generator expressions vs list comprehensions

Same syntax as a list comprehension but with `()` instead of `[]` — builds values **lazily, one
at a time**, instead of materializing the whole list in memory up front.

```python
nums = range(1_000_000)

squares_list = [x * x for x in nums]     # builds a full list of 1M ints in memory NOW
squares_gen  = (x * x for x in nums)     # builds nothing yet — just an iterator object

print(sum(squares_list))   # works, but held the whole list in memory to build it
print(sum(squares_gen))    # same result, only ever holds ONE value in memory at a time
```
**Memory trade-off to state explicitly in an interview:** a list comprehension is O(n) memory
because every element exists simultaneously; a generator expression is O(1) memory regardless of
`n`, because only the current value (plus minimal loop state) exists at any moment. The trade-off
is that a generator can only be iterated **once** — a list can be re-iterated, sliced, indexed,
and its `len()` taken; a generator supports none of that.

## `yield from`

Delegates iteration to a sub-iterable, flattening one level of nested generator calls without a
manual inner loop.

```python
def flatten_pages(documents):
    for doc in documents:
        yield from doc["pages"]     # equivalent to: for page in doc["pages"]: yield page

docs = [{"pages": ["p1", "p2"]}, {"pages": ["p3"]}]
print(list(flatten_pages(docs)))    # ['p1', 'p2', 'p3']
```
`yield from` also correctly forwards `.send()`, `.throw()`, and the sub-generator's return value —
details that matter if you're building coroutine-style generator pipelines, though for most
interview-level answers "it delegates iteration to a nested generator/iterable, cleaner than a
manual loop" is the expected depth.

## When to prefer a generator over a full list

Prefer a generator whenever:
- The data source is **large or unbounded** relative to available memory (a multi-GB log file, a
  paginated API you're crawling, a directory of thousands of scanned PDF pages).
- You're building a **pipeline** where each stage only needs one item at a time (read page → OCR
  → extract text → write to index) — each stage can be a generator, and items flow through the
  whole pipeline one at a time instead of materializing a full intermediate list at every stage.
- You might **stop early** (e.g. `next(gen for gen in results if matches(gen))`) — a generator
  doesn't do the work for items you never consume; a list comprehension always computes all of
  them upfront.

```python
def ocr_pages(pdf_paths):
    """Streaming pipeline: never holds more than one page's data in memory."""
    for path in pdf_paths:
        for page_image in load_pdf_pages(path):   # assume this is itself a generator
            yield run_ocr(page_image)               # yields extracted text, one page at a time

for text in ocr_pages(batch_of_10000_pdfs):
    save_to_elasticsearch(text)    # process-and-discard, constant memory regardless of batch size
```
Prefer a list when you need random access, multiple passes, `len()`, or the data is small enough
that memory isn't a real concern — a generator adds indirection with no benefit there.

## `itertools` highlights

```python
from itertools import chain, islice, groupby

# chain: flatten several iterables into one, lazily
combined = chain([1, 2], [3, 4], [5])
print(list(combined))                          # [1, 2, 3, 4, 5]

# islice: take a slice of an iterator without consuming it into a list first
first_three = islice(count_up(1_000_000), 3)    # only pulls 3 items, ever
print(list(first_three))                        # [0, 1, 2]

# groupby: group CONSECUTIVE items sharing a key — input must already be sorted/ordered by that key
pages = [{"doc": "a", "n": 1}, {"doc": "a", "n": 2}, {"doc": "b", "n": 1}]
for doc_id, group in groupby(pages, key=lambda p: p["doc"]):
    print(doc_id, [p["n"] for p in group])
# a [1, 2]
# b [1]
```
`groupby`'s "consecutive only" behavior is a common interview trap: `groupby` on unsorted data
silently produces multiple separate groups for the same key — always `sorted(data, key=...)`
first unless you know the data is already grouped/ordered.

## Interview questions

**Q1: What's the difference between an iterable and an iterator?**
A: An iterable implements `__iter__` and can produce a fresh iterator each time (a `list` can be
iterated repeatedly). An iterator implements both `__iter__` (returning itself) and `__next__`,
and is stateful/single-use — once exhausted, it stays exhausted.

**Q2: Why use a generator instead of returning a list?**
A: Constant memory usage regardless of input size (lazy, one value at a time), ability to
short-circuit without computing unconsumed values, and natural fit for streaming pipelines. Trade-
off: single-pass only, no `len()`, no indexing/slicing, no re-iteration.

**Q3: What does `yield from` do?**
A: Delegates iteration to a nested iterable/generator, yielding each of its values in turn —
shorthand for a manual `for item in sub: yield item` loop, and it also correctly forwards
`.send()`/`.throw()`/return values in coroutine-style usage.

**Q4: You're processing 50,000 scanned PDF pages for OCR. Would you build a list of all extracted
text or use a generator? Why?**
A: A generator-based streaming pipeline — loading all pages/images into memory at once for 50,000
pages would likely exceed available memory or cause heavy GC pressure; a generator processes and
discards one page at a time, keeping memory usage constant regardless of batch size, and lets you
write results incrementally (e.g. to Elasticsearch) instead of waiting for the whole batch.

**Q5: What's a common bug with `itertools.groupby`?**
A: It only groups *consecutive* matching items, not all items sharing a key across the whole
iterable — running it on unsorted data produces multiple fragmented groups for the same key
instead of one. Always sort by the same key first.

## Exercises

1. Write a generator function `read_large_file_lines(path)` that yields one stripped, non-empty
   line at a time from a file, then use it with `itertools.islice` to print only the first 5
   matching lines without reading the whole file into memory.
2. Take a list of dicts representing log entries with a `"level"` key (not sorted), sort them by
   `"level"`, then use `itertools.groupby` to print counts per level — first without sorting to
   observe the fragmented-groups bug, then with sorting to see the fix.
