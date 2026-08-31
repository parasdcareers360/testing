# Testing: pytest, Mocking, and Fixtures

> **Type:** Study notes

## Why interviewers ask this

Take-home assignments and live-coding rounds are frequently graded partly on whether you write
tests unprompted, and system-design/backend rounds ask "how would you test this" for any service
that calls external dependencies. For this candidate's background specifically — DRF views that
call OCR services, payment gateways, or other microservices — knowing *what* to mock (the external
call) versus what *not* to mock (the DB, in most cases — prefer a real test DB/transaction rollback
over mocking the ORM) is a direct signal of production testing experience versus toy-project
testing.

## pytest basics

pytest auto-discovers files named `test_*.py` or `*_test.py`, functions named `test_*`, and classes
named `Test*` (no `__init__`, no need to subclass `unittest.TestCase`). Assertions are plain
`assert` statements — pytest rewrites them at import time to give rich failure output (showing
actual values on both sides) without needing `self.assertEqual`, `self.assertTrue`, etc.

```python
# test_math_utils.py
def add(a, b):
    return a + b

def test_add_positive_numbers():
    assert add(2, 3) == 5

def test_add_handles_negative():
    assert add(-1, 1) == 0
```
Run with `pytest` (whole repo), `pytest test_math_utils.py::test_add_positive_numbers` (single
test), `pytest -k "positive"` (name substring match), `pytest -v` (verbose), `pytest -x` (stop at
first failure). A failed `assert add(2, 3) == 6` prints `assert 5 == 6` automatically — no manual
message needed, unlike `unittest`'s `self.assertEqual(add(2,3), 6, "message")` boilerplate.

## Fixtures: `@pytest.fixture` and scope

A fixture is a function that provides setup (and optional teardown) for tests that request it by
parameter name — dependency injection instead of `setUp`/`tearDown` methods.

```python
import pytest

@pytest.fixture
def sample_user():
    return {"id": 1, "email": "test@example.com", "is_active": True}

def test_user_is_active(sample_user):
    assert sample_user["is_active"] is True
```
`scope` controls how often the fixture re-runs: `function` (default — fresh per test), `class`,
`module` (once per test file), `session` (once for the whole test run) — use a broader scope for
expensive setup (spinning up a test DB connection, loading a large fixture file) that's safe to
share across tests, and keep `function` scope for anything mutable that tests shouldn't leak state
through.

```python
@pytest.fixture(scope="module")
def db_connection():
    conn = create_test_db_connection()
    yield conn          # everything before yield = setup, after = teardown
    conn.close()
```
The `yield` pattern is the standard way to express teardown — it's a generator-based context
manager under the hood (see [Context Managers](07_context_managers.md)); code after `yield` runs
even if the test raises, similar to a `finally` block.

## `@pytest.mark.parametrize`: one test, many cases

Instead of copy-pasting near-identical test functions for each input/output pair, parametrize runs
the same test body once per row — each row shows up as a separate result in test output, so a
single bad case doesn't hide among passes.

```python
import pytest

@pytest.mark.parametrize("a, b, expected", [
    (2, 3, 5),
    (-1, 1, 0),
    (0, 0, 0),
    (100, -100, 0),
])
def test_add(a, b, expected):
    assert add(a, b) == expected
```
This is the pytest idiom interviewers expect over four separate `test_add_case1`, `test_add_case2`
functions — mention it explicitly if asked "how would you test multiple edge cases for this
function."

## Mocking with `unittest.mock` / `pytest-mock`

`Mock`/`MagicMock` create fake objects that record how they were called; `patch` replaces a real
object with a mock for the duration of a test. `pytest-mock`'s `mocker` fixture is the same
machinery with automatic cleanup (no need for `with patch(...)` context managers or
`@patch` decorators — the mock is undone automatically at test end).

```python
from unittest.mock import Mock, patch

def test_mock_records_calls():
    fake_service = Mock()
    fake_service.get_status.return_value = "ok"

    result = fake_service.get_status()

    assert result == "ok"
    fake_service.get_status.assert_called_once()

# Patching a function where it's *used*, not where it's defined
@patch("myapp.services.ocr_client.extract_text")
def test_process_document_handles_ocr_failure(mock_extract):
    mock_extract.side_effect = TimeoutError("OCR service timed out")
    with pytest.raises(TimeoutError):
        process_document(doc_id=1)
```
**Key rule interviewers check for:** patch the name **where it's looked up**, not where it's
defined — `@patch("myapp.services.ocr_client.extract_text")` patches the reference inside the
module that *calls* it (`myapp.views` does `from myapp.services import ocr_client` then calls
`ocr_client.extract_text`), so patch the attribute on the module object that holds the reference at
call time. Patching the wrong path is the single most common mocking bug — the test passes locally
in isolation but the "mock" never actually intercepts the real call.

**When to mock an external API call vs a DB call:**
- **External API/service calls (OCR service, payment gateway, another microservice): always mock.**
  These are slow, flaky, cost money per call, or have side effects you don't want in a test run —
  and you don't control their uptime/behavior in CI. Mock at the client boundary (`extract_text`,
  `charge_card`) and assert your code handles both success and failure/timeout responses correctly.
- **DB calls: prefer a real test database over mocking the ORM**, using Django's `TestCase` (wraps
  each test in a transaction that's rolled back after) or a dedicated test DB/schema. Mocking
  `queryset.filter()` chains is brittle — you end up re-encoding the ORM's behavior in the mock
  instead of testing your actual query logic, and you can silently miss real query bugs (wrong
  filter, missing `select_related`) that only a real DB round-trip would catch.

## DRF-relevant example: testing a view with a mocked external service call

```python
# services.py
class OCRServiceError(Exception):
    pass

def extract_text_from_document(document_id: int) -> str:
    """Calls an external OCR microservice."""
    response = requests.post(
        "https://ocr-service.internal/extract",
        json={"document_id": document_id},
        timeout=10,
    )
    if response.status_code != 200:
        raise OCRServiceError(f"OCR service returned {response.status_code}")
    return response.json()["text"]

# views.py
class DocumentExtractView(APIView):
    def post(self, request, document_id):
        try:
            text = extract_text_from_document(document_id)
        except OCRServiceError:
            return Response({"error": "extraction failed"}, status=502)
        return Response({"text": text}, status=200)

# test_views.py
import pytest
from rest_framework.test import APIClient

@pytest.fixture
def api_client():
    return APIClient()

def test_extract_view_returns_text_on_success(api_client, mocker):
    mocker.patch(
        "myapp.views.extract_text_from_document",
        return_value="extracted invoice text",
    )
    response = api_client.post("/documents/1/extract/")
    assert response.status_code == 200
    assert response.data["text"] == "extracted invoice text"

def test_extract_view_returns_502_on_ocr_failure(api_client, mocker):
    mocker.patch(
        "myapp.views.extract_text_from_document",
        side_effect=OCRServiceError("timeout"),
    )
    response = api_client.post("/documents/1/extract/")
    assert response.status_code == 502
```
Note the patch target is `myapp.views.extract_text_from_document` (where the view imports and calls
it) — this test never makes a real network call, runs in milliseconds, and explicitly covers the
failure path, which is exactly what an interviewer wants to see for an integration point like this.

## Interview questions

**Q1: How do pytest fixtures differ from `unittest`'s `setUp`/`tearDown`?**
A: Fixtures are explicit dependencies requested by parameter name rather than implicit methods run
before every test — a test only pays for the setup it actually needs, fixtures can depend on other
fixtures, and `scope` lets expensive setup be shared across many tests instead of re-running per
test.

**Q2: You're testing a DRF view that calls a third-party payment API. Would you mock the API call
or hit the real sandbox endpoint in your test suite?**
A: Mock it. Real network calls make the suite slow, flaky (network/service downtime fails
unrelated tests), and in a payment case potentially costly or side-effect-having. Mock at the
client function boundary and write explicit test cases for both success and failure/timeout
responses from that boundary — the goal is to test *your* error handling, not re-test the third
party's API.

**Q3: `@patch("mymodule.some_function")` in your test doesn't seem to intercept the call — the real
function still runs. What's the likely bug?**
A: Patching the wrong path — you must patch the name where it's looked up (the importing module's
namespace), not where it's defined. If `views.py` does `from services import extract_text` and
calls `extract_text(...)`, patch `"views.extract_text"`, not `"services.extract_text"`.

**Q4: Would you mock the Django ORM in a unit test for a view that queries the database?**
A: Generally no — use a real test database with Django's `TestCase` (transaction rollback per
test) instead. Mocking queryset chains is brittle and tends to just re-assert your own mock setup
rather than catching real query bugs; a real (test) DB call is fast enough at unit-test scale and
gives genuine confidence.

## Exercises

1. Write `extract_text_from_document` and its two tests above from scratch (using `pytest-mock`'s
   `mocker.patch`), verifying both the success and `OCRServiceError` failure paths return the
   correct status codes.
2. Take a function with 4+ edge cases you'd normally test with separate functions, and rewrite it
   as one `@pytest.mark.parametrize`-driven test with all cases in a single table.
