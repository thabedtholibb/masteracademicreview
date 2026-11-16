"""Meta-analysis pooling: fixed/random effects and heterogeneity."""

import math

from scipy.stats import chi2, norm


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


def random_effects(effects, variances, method="dl"):
    """Random-effects pooling (DerSimonian–Laird).

    Returns a dict with pooled effect, variance, tau2, weights, and the
    heterogeneity stats.
    """
    fe, fe_var, w = inverse_variance(effects, variances)
    het = heterogeneity(effects, variances, w)
    if method != "dl":
        raise NotImplementedError("only DerSimonian-Laird is implemented")
    total_w = sum(w)
    c = total_w - sum(x ** 2 for x in w) / total_w
    tau2 = max(0.0, (het["Q"] - het["df"]) / c) if c > 0 else 0.0
    w2 = [1 / (v + tau2) for v in variances]
    total_w2 = sum(w2)
    re = sum(wi * yi for wi, yi in zip(w2, effects)) / total_w2
    re_var = 1 / total_w2
    return {
        "effect": re,
        "variance": re_var,
        "tau2": tau2,
        "weights": w2,
        "heterogeneity": het,
    }


def confidence_interval(pooled, variance, level=0.95):
    """Symmetric Wald confidence interval for a pooled estimate."""
    z = norm.ppf(1 - (1 - level) / 2)
    se = math.sqrt(variance)
    return (float(pooled - z * se), float(pooled + z * se))


if __name__ == "__main__":
    # Synthetic demo: three studies, mean difference (continuous outcome).
    effects = [0.20, 0.45, -0.10]
    variances = [0.05, 0.08, 0.06]
    fe, fe_var, _ = inverse_variance(effects, variances)
    re = random_effects(effects, variances)
    print("Fixed effect:", round(fe, 3), "95% CI",
          tuple(round(x, 3) for x in confidence_interval(fe, fe_var)))
    print("Random effect:", round(re["effect"], 3), "95% CI",
          tuple(round(x, 3) for x in confidence_interval(re["effect"], re["variance"])))
    print("tau2:", round(re["tau2"], 4),
          "I2:", round(re["heterogeneity"]["I2"], 1), "%",
          "Q:", round(re["heterogeneity"]["Q"], 2),
          "p:", round(re["heterogeneity"]["p"], 3))
