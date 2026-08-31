# NumPy, pandas, scikit-learn — What to Actually Know

> **Type:** Study notes

## Why interviewers ask this

These three libraries are the practical substrate of almost all non-deep-learning ML work, and
they show up in take-home assignments and live-coding data manipulation questions even in
backend-track interviews. The bar for a 3-YOE backend candidate isn't "know every API," it's
"write correct, reasonably efficient pandas/NumPy code without falling into the classic
performance traps," and "know what scikit-learn's `fit`/`transform`/`predict` contract means well
enough to use it correctly in a pipeline."

## NumPy — vectorization is the entire point

The single fact that matters most: **avoid Python-level loops over NumPy arrays** — vectorized
operations run in compiled C, loop-based equivalents run in the interpreter and are often 10-100x
slower for large arrays.

```python
import numpy as np

arr = np.random.rand(1_000_000)

# Slow: Python-level loop
total = 0.0
for x in arr:
    total += x ** 2

# Fast: vectorized — same result, runs in compiled code
total = np.sum(arr ** 2)
```

**Broadcasting** — NumPy's rule for applying operations between arrays of different (but
compatible) shapes without writing explicit loops:

```python
matrix = np.random.rand(100, 3)          # 100 rows, 3 features
means = matrix.mean(axis=0)              # shape (3,)
centered = matrix - means                # (100, 3) - (3,) broadcasts across all 100 rows
```
Know the broadcasting rule well enough to explain it: shapes are compared from the trailing
dimension backward; two dimensions are compatible if they're equal or one of them is 1. This comes
up directly in feature-normalization code (see
[`02_data_preprocessing_and_feature_engineering.md`](02_data_preprocessing_and_feature_engineering.md)).

**Views vs. copies** — a real gotcha: slicing a NumPy array returns a *view* (shares memory with
the original) by default, not a copy; mutating a view mutates the original array, which is a
classic silent-bug source.

```python
arr = np.array([1, 2, 3, 4, 5])
sub = arr[1:3]        # view, not a copy
sub[0] = 999
print(arr)             # [1, 999, 3, 4, 5] — the original changed too
safe_copy = arr[1:3].copy()   # explicit copy when you don't want this
```

## pandas — correctness traps that come up constantly

**`SettingWithCopyWarning` and chained indexing** — the most common real-world pandas bug:

```python
# Ambiguous whether this mutates the original df or a temporary copy — pandas warns
df[df["age"] > 30]["status"] = "senior"     # DON'T — may silently do nothing

# Correct: .loc for a single, unambiguous assignment
df.loc[df["age"] > 30, "status"] = "senior"
```

**`apply()` is a loop in disguise — avoid it when a vectorized alternative exists.**

```python
# Slow: row-wise Python function call for every row
df["total"] = df.apply(lambda row: row["price"] * row["qty"], axis=1)

# Fast: vectorized column arithmetic
df["total"] = df["price"] * df["qty"]
```
Knowing *when* `apply()` is unavoidable (genuinely row-dependent logic with no vectorized
equivalent, e.g. calling an external function per row) versus when it's a lazy habit is a real
signal of pandas fluency.

**`groupby` + `agg`** — the workhorse for the aggregation queries you'll actually be asked to
write:

```python
df.groupby("user_id").agg(
    total_spent=("amount", "sum"),
    num_orders=("order_id", "count"),
    avg_order_value=("amount", "mean"),
).reset_index()
```

**Merge/join types matter the same way SQL join types do** (see
[`../04_sql_and_databases/02_joins.md`](../04_sql_and_databases/02_joins.md) for the SQL-level
version) — `pd.merge(df1, df2, how="left")` vs `how="inner"` changes row counts and introduces
`NaN`s exactly the way SQL joins do; a candidate who's fluent in SQL joins should map that
knowledge directly here rather than treating it as a new concept.

## scikit-learn — the `fit`/`transform`/`predict` contract

This is the one conceptual thing worth understanding cold, because it's the shape every
preprocessing and modeling object in the library follows:

- **`.fit(X, y=None)`**: learns parameters from data (e.g. `StandardScaler.fit` computes and
  stores the mean/std; `LogisticRegression.fit` learns weights) — mutates the object, returns
  nothing useful.
- **`.transform(X)`**: applies the already-learned transformation to (possibly new) data — for
  preprocessors, not estimators.
- **`.fit_transform(X)`**: convenience for `fit` then `transform` on the *same* data — **never use
  `fit_transform` on validation/test/production data**, only on training data, or you leak
  information (e.g. the test set's own mean/std) into the transformation. This exact mistake is a
  real, common interview trap.
- **`.predict(X)`**: for estimators — applies the learned model to produce predictions, analogous
  to `transform` for preprocessors.

```python
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)     # learn mean/std from train, apply to train
X_test_scaled = scaler.transform(X_test)           # apply the SAME learned mean/std to test —
                                                     # NOT scaler.fit_transform(X_test)

model = LogisticRegression()
model.fit(X_train_scaled, y_train)
predictions = model.predict(X_test_scaled)
```
The `Pipeline` + `ColumnTransformer` pattern shown in
[`02_data_preprocessing_and_feature_engineering.md`](02_data_preprocessing_and_feature_engineering.md#the-most-important-production-gotcha-traininference-skew)
exists specifically to make this fit/transform discipline hard to get wrong, and to serialize the
whole thing as one artifact for production use.

## Interview questions

**Q: Why is a Python `for` loop over a large NumPy array or pandas DataFrame slow, and what's the
fix?**
A: Python-level loops execute each iteration through the interpreter; vectorized NumPy/pandas
operations dispatch to compiled C/Cython code operating on the whole array at once. Fix: express
the operation as array/column arithmetic, `groupby`/`agg`, or a NumPy ufunc instead of manually
iterating rows.

**Q: What's wrong with calling `scaler.fit_transform(X_test)` instead of `scaler.transform(X_test)`?**
A: `fit_transform` re-fits the scaler on the test data itself, meaning the test set's own
statistics (mean/std) leak into its transformation — this is data leakage, and it makes offline
evaluation metrics unrealistically optimistic since the "unseen" test data influenced the
preprocessing.

**Q: What's the difference between a NumPy view and a copy, and why does it matter?**
A: A view shares underlying memory with the original array (common with basic slicing); a copy is
independent. Mutating a view mutates the original array too, which is a common silent-bug source —
use `.copy()` explicitly when independence is required.

## Exercises

1. Given a DataFrame of orders (`user_id`, `amount`, `created_at`), write a `groupby` that produces
   each user's total spend, order count, and days since their first order — without using `apply()`.
2. Take the `StandardScaler` example above and deliberately introduce the `fit_transform(X_test)`
   leakage bug, then explain (in comments) exactly what number would be wrong and why.
