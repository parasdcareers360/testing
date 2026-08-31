# 03 — Python Core and Advanced

> **Type:** Study notes (index)

Python-specific depth beyond "I know the syntax" — the object model, concurrency model, memory
model, and production-quality habits (testing, logging, structure) that separate a candidate who's
used Python for 3 years from one who deeply understands it. Read roughly in order; later files
(concurrency, memory, testing, logging, structure) build on the object-model foundations in the
first few.

## Topics

| # | Topic | File |
|---|---|---|
| 1 | Data model and object references (`is` vs `==`, identity, `__eq__`/`__hash__`) | [`01_data_model_and_object_references.md`](01_data_model_and_object_references.md) |
| 2 | Mutable vs immutable types and their gotchas | [`02_mutable_vs_immutable.md`](02_mutable_vs_immutable.md) |
| 3 | Shallow vs deep copy | [`03_shallow_vs_deep_copy.md`](03_shallow_vs_deep_copy.md) |
| 4 | Functions, `*args`/`**kwargs`, argument passing | [`04_functions_args_kwargs.md`](04_functions_args_kwargs.md) |
| 5 | Closures and decorators | [`05_closures_and_decorators.md`](05_closures_and_decorators.md) |
| 6 | Iterators and generators | [`06_iterators_and_generators.md`](06_iterators_and_generators.md) |
| 7 | Context managers (`with`, `__enter__`/`__exit__`) | [`07_context_managers.md`](07_context_managers.md) |
| 8 | Exceptions and error handling | [`08_exceptions_and_error_handling.md`](08_exceptions_and_error_handling.md) |
| 9 | Type hints and mypy | [`09_type_hints_and_mypy.md`](09_type_hints_and_mypy.md) |
| 10 | OOP, SOLID, composition vs inheritance | [`10_oop_solid_composition_vs_inheritance.md`](10_oop_solid_composition_vs_inheritance.md) |
| 11 | Dataclasses and Pydantic | [`11_dataclasses_and_pydantic.md`](11_dataclasses_and_pydantic.md) |
| 12 | Performance and profiling (`timeit`, `cProfile`, common traps) | [`12_performance_and_profiling.md`](12_performance_and_profiling.md) |
| 13 | GIL, threading, multiprocessing, asyncio | [`13_gil_threading_multiprocessing_asyncio.md`](13_gil_threading_multiprocessing_asyncio.md) |
| 14 | Memory management and garbage collection | [`14_memory_management_and_gc.md`](14_memory_management_and_gc.md) |
| 15 | Testing: pytest, mocking, fixtures | [`15_testing_pytest_mocking_fixtures.md`](15_testing_pytest_mocking_fixtures.md) |
| 16 | Logging and observability | [`16_logging_and_observability.md`](16_logging_and_observability.md) |
| 17 | Clean code and project structure | [`17_clean_code_and_project_structure.md`](17_clean_code_and_project_structure.md) |

## How to use this section

1. Skim files 1-3 first even if they feel basic — object identity/mutability mistakes are the most
   common source of "gotcha" interview questions and real production bugs alike.
2. Files 12-14 (performance, concurrency, memory) are where senior-leaning follow-up questions
   live — expect "why" pressure-testing beyond the first answer.
3. Files 15-17 are less "trivia," more "how do you actually work" — testing habits, logging
   discipline, and code structure are graded live in take-homes and pairing rounds, not just asked
   about verbally.
