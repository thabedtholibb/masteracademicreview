"""Effect-size computation and conversion for meta-analysis.

Each function returns ``(effect, variance)`` so results feed directly into
``pooling.py``. Variances use the standard large-sample approximations.
"""

import math


def cohens_d(m1, m2, sd1, sd2, n1, n2):
    """Cohen's d from two-arm means/SDs (uncorrected)."""
    sp = math.sqrt(((n1 - 1) * sd1 ** 2 + (n2 - 1) * sd2 ** 2) / (n1 + n2 - 2))
    return (m1 - m2) / sp


def hedges_g(m1, m2, sd1, sd2, n1, n2):
    """Hedges' g (bias-corrected Cohen's d) with variance.

    Preferred over Cohen's d for small samples.
    """
    d = cohens_d(m1, m2, sd1, sd2, n1, n2)
    df = n1 + n2 - 2
    j = 1 - 3 / (4 * df - 1)
    g = j * d
    var = j ** 2 * ((n1 + n2) / (n1 * n2) + d ** 2 / (2 * (n1 + n2)))
    return g, var


def log_odds_ratio(a, b, c, d, cc=0.5):
    """Log odds ratio from a 2x2 table.

    a = events treatment, b = non-events treatment,
    c = events control,   d = non-events control.
    Applies a continuity correction if any cell is zero.
    """
    if any(x == 0 for x in (a, b, c, d)):
        a, b, c, d = a + cc, b + cc, c + cc, d + cc
    lor = math.log((a * d) / (b * c))
    var = 1 / a + 1 / b + 1 / c + 1 / d
    return lor, var


def log_risk_ratio(a, b, c, d, cc=0.5):
    """Log risk ratio from a 2x2 table (events/non-events per arm)."""
    if any(x == 0 for x in (a, b, c, d)):
        a, b, c, d = a + cc, b + cc, c + cc, d + cc
    n1 = a + b
    n2 = c + d
    lrr = math.log((a / n1) / (c / n2))
    var = 1 / a - 1 / n1 + 1 / c - 1 / n2
    return lrr, var


def fisher_z(r):
    """Fisher z-transform of a correlation."""
    return 0.5 * math.log((1 + r) / (1 - r))


def fisher_z_variance(n):
    """Variance of Fisher-z for a correlation based on n observations."""
    return 1 / (n - 3)
