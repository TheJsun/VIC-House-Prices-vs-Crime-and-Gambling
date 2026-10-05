"""Shared evaluation helpers, so the three analysis notebooks cannot diverge.

The original project evaluated models three different ways in three different
notebooks, which is how it ended up reporting six accuracies between 0.48 and
0.74 for what was nominally the same model. Centralising the protocols here
means a number means the same thing wherever it appears.

Three evaluation protocols are offered, and the difference between them is the
single most important methodological point in this project:

``resample_scores``
    What the original did: repeatedly split *rows* at random, train, score,
    average. Reproduced here, now seeded.

``repeated_stratified_cv``
    The standard version of the same idea: repeated stratified k-fold, which
    guarantees every row is tested exactly once per repeat and keeps the class
    balance in every fold.

``grouped_cv``
    The honest one. Every LGA contributes five rows -- one per year -- whose
    features barely move and whose label is usually identical across all five.
    A row-wise split therefore puts four near-duplicates of each test row into
    the training set, so the model can score well by recognising the council
    rather than by learning the relationship. Grouping the folds by LGA means
    a council appears in training or in testing, never both.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.base import BaseEstimator, clone
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error
from sklearn.model_selection import (
    GroupKFold,
    RepeatedStratifiedKFold,
    StratifiedGroupKFold,
    cross_val_predict,
    cross_val_score,
    train_test_split,
)
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .config import CV_REPEATS, CV_SPLITS, N_RESAMPLES, SEED, TEST_FRACTION


# --------------------------------------------------------------------------
# estimators
# --------------------------------------------------------------------------
def knn(k: int, *, scale: bool) -> BaseEstimator:
    """A k-nearest-neighbours classifier, with or without feature scaling.

    Scaling is not cosmetic here. The two features are an offence rate per
    100,000 residents (roughly 5,000-15,000) and gambling loss per head
    (roughly 100-600), so without scaling the Euclidean distance that k-NN
    depends on is almost entirely the offence rate and the gambling feature is
    effectively ignored. Both variants are kept so the effect is measurable
    rather than asserted.
    """
    model = KNeighborsClassifier(n_neighbors=k)
    if not scale:
        return model
    return Pipeline([("scale", StandardScaler()), ("knn", model)])


# --------------------------------------------------------------------------
# baselines
# --------------------------------------------------------------------------
def classification_baselines(X, y) -> dict[str, float]:
    """Accuracy of the trivial classifiers, under grouped CV where possible.

    The original project never computed these, which left its headline 0.66
    with nothing to be compared against.
    """
    out = {}
    for name, strategy in [
        ("majority class", "most_frequent"),
        ("stratified random", "stratified"),
        ("uniform random", "uniform"),
    ]:
        model = DummyClassifier(strategy=strategy, random_state=SEED)
        scores = cross_val_score(
            model,
            X,
            y,
            cv=RepeatedStratifiedKFold(
                n_splits=CV_SPLITS, n_repeats=CV_REPEATS, random_state=SEED
            ),
        )
        out[name] = float(np.mean(scores))
    return out


def regression_baseline_rmse(y) -> float:
    """RMSE of always predicting the mean.

    Equal to the standard deviation of y, and the number any regression here
    has to beat to be doing anything at all.
    """
    y = np.asarray(y, dtype=float)
    return float(np.sqrt(np.mean((y - y.mean()) ** 2)))


# --------------------------------------------------------------------------
# evaluation protocols
# --------------------------------------------------------------------------
def resample_scores(
    estimator: BaseEstimator,
    X,
    y,
    *,
    n_resamples: int = N_RESAMPLES,
    test_fraction: float = TEST_FRACTION,
    seed: int = SEED,
    stratify: bool = True,
) -> np.ndarray:
    """The original project's protocol: repeated random row-wise splits.

    Reproduced with a seed so the result is stable. Note that this protocol
    leaks by LGA -- see the module docstring -- and is reported for
    comparability with the submitted report, not as the headline.
    """
    scores = []
    for i in range(n_resamples):
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=test_fraction,
            random_state=seed + i,
            stratify=y if stratify else None,
        )
        model = clone(estimator).fit(X_train, y_train)
        scores.append(accuracy_score(y_test, model.predict(X_test)))
    return np.asarray(scores)


def repeated_stratified_cv(estimator: BaseEstimator, X, y) -> np.ndarray:
    """Repeated stratified k-fold accuracy. Still row-wise, so still leaky."""
    cv = RepeatedStratifiedKFold(
        n_splits=CV_SPLITS, n_repeats=CV_REPEATS, random_state=SEED
    )
    return cross_val_score(estimator, X, y, cv=cv, scoring="accuracy")


def grouped_cv(
    estimator: BaseEstimator, X, y, groups, *, scoring: str = "accuracy"
) -> np.ndarray:
    """Accuracy with folds grouped by LGA, so no council spans the split."""
    cv = StratifiedGroupKFold(n_splits=CV_SPLITS, shuffle=True, random_state=SEED)
    return cross_val_score(
        estimator, X, y, groups=groups, cv=cv, scoring=scoring
    )


def grouped_predictions(estimator: BaseEstimator, X, y, groups) -> np.ndarray:
    """Out-of-fold predictions under LGA-grouped folds.

    Used for the confusion matrix and classification report, so those describe
    held-out performance rather than performance on the training data.
    """
    cv = StratifiedGroupKFold(n_splits=CV_SPLITS, shuffle=True, random_state=SEED)
    return cross_val_predict(estimator, X, y, groups=groups, cv=cv)


def grouped_regression_predictions(estimator: BaseEstimator, X, y, groups):
    """Out-of-fold predictions for a regressor, folds grouped by LGA."""
    cv = GroupKFold(n_splits=CV_SPLITS)
    return cross_val_predict(estimator, X, y, groups=groups, cv=cv)


def year_split(df: pd.DataFrame, train_years, test_years):
    """Split by year, the way two of the original notebooks did.

    Worth keeping because the report quotes results from it, and worth
    labelling clearly: splitting by year does *not* remove the LGA leak, since
    every council still appears on both sides.
    """
    train = df[df["Year"].isin(train_years)]
    test = df[df["Year"].isin(test_years)]
    return train, test


# --------------------------------------------------------------------------
# metrics
# --------------------------------------------------------------------------
@dataclass
class RegressionMetrics:
    """Everything the original reported, plus what it was missing."""

    n: int
    n_features: int
    rmse: float
    mae: float
    r2: float
    adjusted_r2: float
    pearson_r: float
    pearson_p: float
    coefficients: list[float] = field(default_factory=list)
    intercept: float = float("nan")

    def as_row(self) -> dict:
        row = {
            "n": self.n,
            "Intercept": self.intercept,
            "RMSE": self.rmse,
            "MAE": self.mae,
            "R2": self.r2,
            "Adjusted R2": self.adjusted_r2,
            "Pearson r": self.pearson_r,
            "Pearson p": self.pearson_p,
        }
        for i, coefficient in enumerate(self.coefficients, start=1):
            row["Coefficient " + str(i)] = coefficient
        return row


def regression_metrics(
    y_true,
    y_pred,
    *,
    n_features: int,
    coefficients=None,
    intercept: float = float("nan"),
) -> RegressionMetrics:
    """Compute RMSE, MAE, R squared, adjusted R squared and Pearson r.

    The original reported RMSE and ``pearsonr(y_true, y_pred)``. The latter is
    a correlation, and reporting it alongside R squared matters: a correlation
    of 0.48 sounds respectable, while the R squared it implies -- 0.23 -- says
    plainly that three quarters of the variation is unexplained.
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    n = len(y_true)

    residuals = y_true - y_pred
    rmse = float(np.sqrt(np.mean(residuals**2)))
    mae = float(mean_absolute_error(y_true, y_pred))

    total_ss = float(np.sum((y_true - y_true.mean()) ** 2))
    residual_ss = float(np.sum(residuals**2))
    r2 = 1.0 - residual_ss / total_ss if total_ss > 0 else float("nan")

    denominator = n - n_features - 1
    adjusted = (
        1.0 - (1.0 - r2) * (n - 1) / denominator if denominator > 0 else float("nan")
    )

    r, p = stats.pearsonr(y_true, y_pred)

    return RegressionMetrics(
        n=n,
        n_features=n_features,
        rmse=rmse,
        mae=mae,
        r2=r2,
        adjusted_r2=float(adjusted),
        pearson_r=float(r),
        pearson_p=float(p),
        coefficients=list(coefficients) if coefficients is not None else [],
        intercept=float(intercept),
    )


def classification_summary(y_true, y_pred, labels) -> pd.DataFrame:
    """Per-class precision, recall and F1, plus macro and weighted averages.

    Computed rather than transcribed. The submitted report's equivalent table
    was typed out by hand from a confusion matrix.
    """
    from sklearn.metrics import precision_recall_fscore_support

    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, zero_division=0
    )
    rows = [
        {
            "Class": label,
            "Precision": precision[i],
            "Recall": recall[i],
            "F1": f1[i],
            "Support": int(support[i]),
        }
        for i, label in enumerate(labels)
    ]
    for average in ("macro", "weighted"):
        p, r, f, _ = precision_recall_fscore_support(
            y_true, y_pred, labels=labels, average=average, zero_division=0
        )
        rows.append(
            {
                "Class": average + " average",
                "Precision": p,
                "Recall": r,
                "F1": f,
                "Support": int(sum(support)),
            }
        )
    return pd.DataFrame(rows).round(4)


def summarise(scores: np.ndarray) -> dict[str, float]:
    """Mean, standard deviation and a 95% interval for a set of CV scores.

    The original reported point estimates from a 33-row test set, where a
    single reclassified row moves accuracy by three points. Reporting spread
    is what makes the numbers comparable.
    """
    scores = np.asarray(scores, dtype=float)
    mean = float(scores.mean())
    sd = float(scores.std(ddof=1)) if len(scores) > 1 else 0.0
    half_width = 1.96 * sd / np.sqrt(len(scores)) if len(scores) > 1 else 0.0
    return {
        "mean": mean,
        "sd": sd,
        "ci_low": mean - half_width,
        "ci_high": mean + half_width,
        "n_scores": len(scores),
    }
