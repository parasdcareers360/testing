# Data Preprocessing & Feature Engineering

> **Type:** Study notes

## Why interviewers ask this

For a backend engineer, this is often the *actual* job — you're far more likely to own the data
pipeline feeding a model than the model architecture itself. Interviewers probe this to see if you
understand why "garbage in, garbage out" is an engineering problem you're responsible for, not
just an ML researcher's concern, and whether you know the standard techniques well enough to
implement or review a preprocessing pipeline in Django/pandas.

## Missing data

Three real options, each with a real trade-off — naming the trade-off matters more than naming the
technique:

- **Drop rows/columns**: simplest, safe when missingness is rare and random; loses data and can
  bias results if missingness correlates with the outcome (e.g. users who abandon a form are
  systematically different from those who complete it).
- **Impute with a statistic** (mean/median for numeric, mode for categorical): keeps all rows,
  but can understate variance and create artificial "clumps" at the imputed value — median is
  generally preferred over mean for skewed data (outliers distort the mean more).
- **Impute with a model or a flag**: a "missingness indicator" column (`was_missing: bool`)
  alongside an imputed value preserves the signal that a value was missing, which itself can be
  predictive (e.g. "user didn't provide phone number" correlates with churn).

```python
import pandas as pd

df["income_was_missing"] = df["income"].isna()
df["income"] = df["income"].fillna(df["income"].median())
```

## Scaling and normalization — and why it matters for some models but not others

- **Standardization** (`(x - mean) / std`): centers data at 0 with unit variance.
- **Min-max scaling** (`(x - min) / (max - min)`): rescales into `[0, 1]`.
- **Why it matters**: distance-based and gradient-descent-based models (k-NN, SVM, neural nets,
  linear/logistic regression) are sensitive to feature scale — a feature ranging 0-1,000,000
  (income) will dominate one ranging 0-1 (a ratio) in distance calculations or gradient updates
  purely due to magnitude, not actual predictive importance. Tree-based models (decision trees,
  random forest, gradient-boosted trees) are scale-invariant — they split on thresholds, not
  distances — so scaling is wasted effort there. Knowing *which model family cares* is the
  interview-relevant fact, not the formulas themselves.

## Categorical encoding

- **One-hot encoding**: one binary column per category — correct choice when categories have no
  order (color, country) and cardinality is low-to-moderate. High-cardinality categoricals (user
  ID, product SKU with thousands of values) blow up dimensionality — consider target encoding,
  embeddings, or hashing instead.
- **Label/ordinal encoding**: integers per category — only correct when there's a genuine order
  (small/medium/large); using it on an unordered category (like city) falsely implies an order the
  model will pick up on as if it were meaningful.
- **Target/mean encoding**: replace a category with the mean of the target variable for that
  category — powerful for high-cardinality features, but leaks target information if not done
  carefully with cross-validation (fit encoding on a fold the row wasn't part of), otherwise it
  overfits badly.

```python
# One-hot: pandas' get_dummies for prototyping (production pipelines use sklearn's
# OneHotEncoder so the same category set is guaranteed at train and inference time)
pd.get_dummies(df, columns=["country"], drop_first=True)
```
`drop_first=True` avoids the "dummy variable trap" — perfect multicollinearity for linear models,
since the last category's info is fully implied by all the others being 0. Worth mentioning
unprompted; it's a real, specific gotcha.

## Feature engineering — the part interviewers most want a concrete example of

Deriving new, more predictive columns from raw ones — usually the highest-leverage part of a
pipeline, more impactful than model choice for many real problems. Concrete examples relevant to a
backend candidate's likely domain:

- From a `created_at` timestamp: `day_of_week`, `hour_of_day`, `is_weekend`, `days_since_signup` —
  raw timestamps are nearly useless to most models directly.
- From free text (a support ticket, a search query): length, presence of specific keywords,
  sentiment score, or — increasingly the modern default — an embedding vector (see
  [`05_nlp_basics_tokenization_embeddings_transformers_attention.md`](05_nlp_basics_tokenization_embeddings_transformers_attention.md)).
- From a user's event history: aggregates like `num_purchases_last_30_days`, `avg_session_length`
  — this is exactly what a **feature store** exists to compute and serve consistently between
  training and inference (see the next section).

## The most important production gotcha: train/inference skew

If preprocessing logic is written twice — once in an offline training pipeline (pandas/SQL) and
once in the online inference path (a Django view, a Python service) — the two can silently drift
apart (a rounding difference, a different `fillna` default, a timezone bug) and degrade model
performance in a way that's very hard to detect from application logs alone. The standard fix:
**share the exact same preprocessing code/artifact** between training and serving — either the
preprocessing pipeline is a versioned, serialized object (a fitted `sklearn.Pipeline`,
pickled/joblib-saved and loaded by the serving code) or a feature store computes features once and
both training and serving read from it. This is a real production-reliability topic a backend
engineer is expected to own, not a research concern.

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
import joblib

pipeline = Pipeline([
    ("preprocess", ColumnTransformer([
        ("num", StandardScaler(), ["income", "age"]),
        ("cat", OneHotEncoder(handle_unknown="ignore"), ["country"]),
    ])),
])
pipeline.fit(training_df)
joblib.dump(pipeline, "preprocess_pipeline.joblib")   # same artifact loaded by the serving service
```
`handle_unknown="ignore"` on `OneHotEncoder` is another concrete, sayable detail: it prevents
inference-time crashes when a category appears in production that wasn't seen during training.

## Interview questions

**Q: Why does feature scaling matter for some models and not others?**
A: Distance- and gradient-based models (k-NN, SVM, linear/logistic regression, neural nets) treat
raw feature magnitude as meaningful, so an unscaled large-range feature can dominate purely by
scale; tree-based models split on thresholds per feature independently, so scale doesn't affect
their splits.

**Q: How would you handle a categorical feature with 50,000 unique values (e.g. product SKU)?**
A: One-hot encoding is impractical (50,000 new columns). Options: target/mean encoding (with
proper cross-validation to avoid leakage), embeddings (learn a dense low-dimensional
representation, common for recommendation systems), or hashing trick (fixed-size hash buckets,
accepts some collision risk for bounded dimensionality).

**Q: What's train/inference skew and how do you prevent it in a production system?**
A: It's a silent mismatch between how features are computed at training time vs. serving time,
degrading model accuracy without an obvious error. Prevent it by sharing the exact preprocessing
artifact/code between both paths — a serialized fitted pipeline or a feature store — rather than
reimplementing preprocessing logic twice.

## Exercises

1. Given a raw events table (`user_id`, `event_type`, `timestamp`), write pandas code to engineer
   three features: `events_last_7_days`, `hour_of_day` of the most recent event, and
   `days_since_first_event`.
2. Take the `ColumnTransformer` example above and extend it with a missing-value imputer for
   `income` using the missingness-indicator pattern from the "Missing data" section, keeping it as
   one fitted, serializable pipeline.
