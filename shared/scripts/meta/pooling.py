"""Meta-analysis pooling: fixed/random effects, heterogeneity, sensitivity.

Estimators: DerSimonian-Laird (default), REML, Paule-Mandel; optional
Hartung-Knapp-Sidik-Jonkman (HKSJ) adjustment; prediction interval;
leave-one-out; subgroup analysis; meta-regression.
"""

import math

import numpy as np
from scipy.optimize import brentq
from scipy.stats import chi2, norm, t as tdist


def inverse_variance(effects, variances):
    """Fixed-effect (inverse-variance) pooling.

    Returns ``(pooled_effect, pooled_variance, weights)``.
    """
    weights = [1 / v for v in variances]
    total = sum(weights)
    pooled = sum(w * y for w, y in zip(weights, effects)) / total
    var = 1 / total
    return pooled, var, weights


def heterogeneity(effects, variances, weights=None):
    """Cochran's Q and I^2.

    Returns a dict with keys Q, df, p, I2 (percent).
    """
    if weights is None:
        weights = [1 / v for v in variances]
    k = len(effects)
    if k < 2:
        return {"Q": 0.0, "df": 0, "p": 1.0, "I2": 0.0}
    total = sum(weights)
    fe = sum(w * y for w, y in zip(weights, effects)) / total
    q = sum(w * (y - fe) ** 2 for w, y in zip(weights, effects))
    df = k - 1
    p = chi2.sf(q, df)
    i2 = max(0.0, (q - df) / q) * 100 if q > 0 else 0.0
    return {"Q": q, "df": df, "p": p, "I2": i2}


def _tau2_dl(effects, variances):
    w = [1 / v for v in variances]
    het = heterogeneity(effects, variances, w)
    total_w = sum(w)
    c = total_w - sum(x ** 2 for x in w) / total_w
    return max(0.0, (het["Q"] - het["df"]) / c) if c > 0 else 0.0


def _q_gen(tau2, effects, variances):
    w = [1 / (v + tau2) for v in variances]
    mu = sum(wi * y for wi, y in zip(w, effects)) / sum(w)
    return sum(wi * (y - mu) ** 2 for wi, y in zip(w, effects))


def _tau2_pm(effects, variances):
    """Paule-Mandel: tau2 such that generalized Q equals k-1."""
    k = len(effects)
    if k < 2 or _q_gen(0.0, effects, variances) <= k - 1:
        return 0.0
    hi = max(1.0, 10 * (max(effects) - min(effects)) ** 2)
    return float(brentq(lambda t: _q_gen(t, effects, variances) - (k - 1),
                        0.0, hi))


def _tau2_reml(effects, variances, tol=1e-10, max_iter=1000):
    """REML via fixed-point iteration, started from DL."""
    tau2 = _tau2_dl(effects, variances)
    for _ in range(max_iter):
        w = [1 / (v + tau2) for v in variances]
        sw = sum(w)
        mu = sum(wi * y for wi, y in zip(w, effects)) / sw
        num = sum(wi ** 2 * ((y - mu) ** 2 - v)
                  for wi, y, v in zip(w, effects, variances))
        num += sum(wi ** 2 for wi in w) / sw  # REML correction
        new = max(0.0, num / sum(wi ** 2 for wi in w))
        if abs(new - tau2) < tol:
            return new
        tau2 = new
    return tau2


TAU2_METHODS = {"dl": _tau2_dl, "pm": _tau2_pm, "reml": _tau2_reml}


def random_effects(effects, variances, method="dl", hksj=False,
                   level=0.95):
    """Random-effects pooling.

    ``method``: tau^2 estimator, "dl" (DerSimonian-Laird, default),
    "reml" or "pm" (Paule-Mandel). ``hksj=True`` applies the
    Hartung-Knapp-Sidik-Jonkman adjustment (variance rescaled by the
    residual q, truncated at 1, and a t(k-1) interval), recommended
    when k is small or heterogeneity is present.

    Returns a dict with pooled effect, variance, tau2, weights, the
    heterogeneity stats and ``ci`` (low, high) for the requested level.
    """
    if method not in TAU2_METHODS:
        raise ValueError("method must be one of %s" % sorted(TAU2_METHODS))
    k = len(effects)
    het = heterogeneity(effects, variances)
    tau2 = TAU2_METHODS[method](effects, variances)
    w2 = [1 / (v + tau2) for v in variances]
    total_w2 = sum(w2)
    re = sum(wi * yi for wi, yi in zip(w2, effects)) / total_w2
    re_var = 1 / total_w2
    if hksj and k > 1:
        q = sum(wi * (y - re) ** 2 for wi, y in zip(w2, effects)) / (k - 1)
        re_var = max(1.0, q) * re_var
        crit = tdist.ppf(1 - (1 - level) / 2, k - 1)
    else:
        crit = norm.ppf(1 - (1 - level) / 2)
    half = crit * math.sqrt(re_var)
    return {
        "effect": re,
        "variance": re_var,
        "tau2": tau2,
        "tau2_method": method,
        "hksj": bool(hksj),
        "weights": w2,
        "heterogeneity": het,
        "ci": (float(re - half), float(re + half)),
        "k": k,
    }


def prediction_interval(result, level=0.95):
    """Prediction interval for a new study (Higgins 2009; t with k-2 df).

    Needs k >= 3 and a ``random_effects`` result; returns (nan, nan)
    otherwise.
    """
    k = result["k"]
    if k < 3:
        return (float("nan"), float("nan"))
    t = tdist.ppf(1 - (1 - level) / 2, k - 2)
    half = t * math.sqrt(result["tau2"] + result["variance"])
    return (float(result["effect"] - half), float(result["effect"] + half))


def leave_one_out(effects, variances, names=None, **kwargs):
    """Sensitivity analysis: re-pool omitting each study in turn.

    Returns a list of dicts (omitted, effect, ci, tau2, I2).
    """
    effects, variances = list(effects), list(variances)
    k = len(effects)
    names = names or ["study %d" % (i + 1) for i in range(k)]
    out = []
    for i in range(k):
        r = random_effects(effects[:i] + effects[i + 1:],
                           variances[:i] + variances[i + 1:], **kwargs)
        out.append({"omitted": names[i], "effect": r["effect"],
                    "ci": r["ci"], "tau2": r["tau2"],
                    "I2": r["heterogeneity"]["I2"]})
    return out


def subgroup_analysis(effects, variances, groups, **kwargs):
    """Random-effects pooling per subgroup + test for subgroup differences.

    The between-subgroup test is Q_between on the subgroup estimates
    (chi-square, g-1 df). A ``warning`` is returned when k < 10 because
    subgroup tests are then exploratory.
    """
    labels = list(dict.fromkeys(groups))
    res = {}
    for g in labels:
        idx = [i for i, x in enumerate(groups) if x == g]
        r = random_effects([effects[i] for i in idx],
                           [variances[i] for i in idx], **kwargs)
        r["n_studies"] = len(idx)
        res[g] = r
    if len(labels) > 1:
        est = [res[g]["effect"] for g in labels]
        w = [1 / res[g]["variance"] for g in labels]
        mu = sum(a * b for a, b in zip(w, est)) / sum(w)
        qb = sum(a * (b - mu) ** 2 for a, b in zip(w, est))
        df = len(labels) - 1
        between = {"Q": qb, "df": df, "p": float(chi2.sf(qb, df))}
    else:
        between = {"Q": 0.0, "df": 0, "p": 1.0}
    return {"subgroups": res, "between": between,
            "warning": ("fewer than 10 studies: subgroup test is "
                        "exploratory" if len(effects) < 10 else None)}


def meta_regression(effects, variances, moderators, hksj=True):
    """Random-effects meta-regression (method-of-moments tau^2).

    ``moderators``: list of columns (one number per study each); an
    intercept is added. Returns coefficients with SE, statistic and p
    (t with k-p df when ``hksj``, else z) and the residual tau2.
    Rule of thumb: >= 10 studies per moderator; ``warning`` otherwise.
    """
    k = len(effects)
    cols = [[1.0] * k] + [[float(x) for x in c] for c in moderators]
    p = len(cols)
    if k <= p:
        raise ValueError("need more studies than coefficients")
    X = np.array(cols).T
    y = np.asarray(effects, dtype=float)
    v = np.asarray(variances, dtype=float)

    def fit(tau2):
        w = 1 / (v + tau2)
        inv = np.linalg.inv(X.T @ (X * w[:, None]))
        return w, inv, inv @ (X.T @ (w * y))

    w, inv, beta = fit(0.0)
    qres = float(np.sum(w * (y - X @ beta) ** 2))
    c = float(w.sum() - np.trace(inv @ (X.T @ (X * (w ** 2)[:, None]))))
    tau2 = max(0.0, (qres - (k - p)) / c) if c > 0 else 0.0
    w, inv, beta = fit(tau2)
    resid = y - X @ beta
    cov = inv
    if hksj:
        cov = inv * max(1.0, float(np.sum(w * resid ** 2)) / (k - p))
    se = np.sqrt(np.diag(cov))
    stat = beta / se
    pv = (2 * tdist.sf(np.abs(stat), k - p) if hksj
          else 2 * norm.sf(np.abs(stat)))
    return {"coef": [float(b) for b in beta], "se": [float(s) for s in se],
            "stat": [float(s) for s in stat], "p": [float(x) for x in pv],
            "tau2": tau2, "k": k,
            "warning": ("fewer than 10 studies per moderator: exploratory"
                        if k < 10 * (p - 1) else None)}


def confidence_interval(pooled, variance, level=0.95):
    """Symmetric Wald confidence interval for a pooled estimate."""
    z = norm.ppf(1 - (1 - level) / 2)
    se = math.sqrt(variance)
    return (float(pooled - z * se), float(pooled + z * se))


if __name__ == "__main__":
    effects = [0.20, 0.45, -0.10]
    variances = [0.05, 0.08, 0.06]
    fe, fe_var, _ = inverse_variance(effects, variances)
    re = random_effects(effects, variances)
    print("Fixed effect:", round(fe, 3), "95% CI",
          tuple(round(x, 3) for x in confidence_interval(fe, fe_var)))
    print("Random effect:", round(re["effect"], 3), "95% CI",
          tuple(round(x, 3) for x in re["ci"]))
    print("tau2:", round(re["tau2"], 4),
          "I2:", round(re["heterogeneity"]["I2"], 1), "%",
          "Q:", round(re["heterogeneity"]["Q"], 2),
          "p:", round(re["heterogeneity"]["p"], 3))
