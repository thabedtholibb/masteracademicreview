"""Forest plot, funnel plot, and Egger's regression test."""

import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import t as tdist


def forest_plot(studies, effects, variances, pooled, pooled_variance,
                pooled_label="Pooled (random effects)",
                effect_name="Effect size", title="", filename="forest.png"):
    """Draw a forest plot and save to file. Returns the filename."""
    k = len(studies)
    if k == 0:
        raise ValueError("forest_plot: no studies")
    ses = [math.sqrt(v) for v in variances]
    order = sorted(range(k), key=lambda i: effects[i])

    fig, ax = plt.subplots(figsize=(9, max(3.0, 1.4 + 0.55 * k)))
    yticks, ylabels = [], []
    y = 0
    for i in order:
        lo = effects[i] - 1.96 * ses[i]
        hi = effects[i] + 1.96 * ses[i]
        ax.plot([lo, hi], [y, y], color="0.2", lw=1.2, solid_capstyle="butt")
        ax.plot(effects[i], y, marker="s", ms=7, color="0.1")
        yticks.append(y)
        ylabels.append(studies[i])
        y += 1

    y += 0.6
    se_p = math.sqrt(pooled_variance)
    lo_p = pooled - 1.96 * se_p
    hi_p = pooled + 1.96 * se_p
    diamond_x = [pooled, hi_p, pooled, lo_p, pooled]
    diamond_y = [y, y + 0.35, y + 0.7, y + 0.35, y]
    ax.fill(diamond_x, diamond_y, color="0.2", alpha=0.5)
    yticks.append(y + 0.35)
    ylabels.append(pooled_label)

    ax.axvline(0, color="0.5", ls="--", lw=1)
    ax.set_yticks(yticks)
    ax.set_yticklabels(ylabels, fontsize=8)
    ax.set_xlabel(effect_name)
    if title:
        ax.set_title(title)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(filename, dpi=150)
    plt.close(fig)
    return filename


def funnel_plot(effects, variances, pooled, filename="funnel.png",
                effect_name="Effect size"):
    """Draw a funnel plot (SE vs effect, with pseudo-95% limits)."""
    ses = [math.sqrt(v) for v in variances]
    fig, ax = plt.subplots(figsize=(6.5, 5))
    ax.scatter(effects, ses, s=30, edgecolor="0.1", facecolor="0.7")
    max_se = max(ses) if ses else 1.0
    grid = np.linspace(0, max_se * 1.15, 200)
    ax.plot([pooled] * len(grid), grid, color="0.3", lw=1)
    ax.plot(pooled + 1.96 * grid, grid, color="0.3", ls="--", lw=1)
    ax.plot(pooled - 1.96 * grid, grid, color="0.3", ls="--", lw=1)
    ax.set_ylim(max_se * 1.15, 0)
    ax.set_xlabel(effect_name)
    ax.set_ylabel("Standard error")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(filename, dpi=150)
    plt.close(fig)
    return filename


LFK_CAVEAT = ("Schwarzer, Rücker & Semaca (2024) found that the LFK index does not reliably "
              "detect small-study effects; report it only next to a funnel plot (and Egger's "
              "test when k >= 10), never as the sole evidence about publication bias.")


def lfk_index(effects, variances):
    """LFK index and Doi-plot coordinates (Furuya-Kanamori et al. 2018).

    Same algorithm as ``metasens::lfkindex`` (Rücker & Schwarzer): studies
    are ordered by effect; each gets a weight N = 100 * max(var) / var; the
    mid-rank percentile of the cumulative weights is turned into a normal
    quantile z; the study with the smallest |z| is the reference; then
    LFK = 5 / (2k) * sum(z_i + (range(z) / range(d)) * d_i), d_i = effect_i -
    effect_ref. Interpretation: |LFK| <= 1 no asymmetry, <= 2 minor, > 2 major.

    Returns a dict with ``lfk``, ``interpretation``, ``effects`` (sorted),
    ``abs_z`` (Doi-plot y values), ``z`` and ``caveat``. CI cross-checks
    the value against the R implementation.
    """
    from statistics import NormalDist

    pairs = sorted(zip(effects, variances), key=lambda p: p[0])   # stable, like R order()
    te = [float(e) for e, _ in pairs]
    var = [float(v) for _, v in pairs]
    k = len(te)
    if k < 2 or any(v <= 0 for v in var):
        raise ValueError("lfk_index needs >= 2 studies with positive variances")
    weight = [100.0 * max(var) / v for v in var]
    mid = [weight[0] / 2.0]
    for i in range(1, k):
        mid.append(mid[i - 1] + (weight[i - 1] + weight[i]) / 2.0)
    total = sum(weight)
    z = [NormalDist().inv_cdf((m - 0.5) / total) for m in mid]
    abs_z = [abs(v) for v in z]
    ref = min(range(k), key=abs_z.__getitem__)                  # first minimum, like which.min
    d = [t - te[ref] for t in te]
    span_z, span_d = max(z) - min(z), max(d) - min(d)
    if span_d == 0:
        lfk, label = float("nan"), "unclear (all effects equal)"
    else:
        lfk = 5.0 / (2.0 * k) * sum(zi + span_z / span_d * di for zi, di in zip(z, d))
        label = ("no asymmetry" if abs(lfk) <= 1 else
                 "minor asymmetry" if abs(lfk) <= 2 else "major asymmetry")
    return {"lfk": lfk, "interpretation": label, "effects": te, "abs_z": abs_z,
            "z": z, "k": k, "caveat": LFK_CAVEAT}


def doi_plot(effects, variances, filename="doi.png", effect_name="Effect size"):
    """Doi plot: effect size vs |z| (most precise studies at the top), with the LFK index."""
    res = lfk_index(effects, variances)
    fig, ax = plt.subplots(figsize=(6.5, 5))
    ax.plot(res["effects"], res["abs_z"], marker="o", color="0.2", lw=1,
            markerfacecolor="0.7", markeredgecolor="0.1")
    ax.set_ylim(max(res["abs_z"]) * 1.1 + 0.05, 0)
    ax.set_xlabel(effect_name)
    ax.set_ylabel("|Z-score|")
    ax.set_title("LFK index %.2f (%s)" % (res["lfk"], res["interpretation"]), fontsize=10)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(filename, dpi=150)
    plt.close(fig)
    return filename


def egger_test(effects, variances, min_k=10):
    """Egger's regression test for small-study / publication bias.

    Regresses the standardized effect (effect/SE) on precision (1/SE);
    a nonzero intercept suggests asymmetry. Returns a dict with
    intercept, se, t, two-sided p, and ``adequate`` (False with a
    ``warning`` when k < ``min_k``: low power, do not interpret;
    Sterne et al. 2011).
    """
    effects = np.asarray(effects, dtype=float)
    variances = np.asarray(variances, dtype=float)
    ses = np.sqrt(variances)
    precision = 1 / ses
    snd = effects / ses
    n = len(effects)
    if n < 3:
        return {"intercept": float("nan"), "se": float("nan"),
                "t": float("nan"), "p": float("nan"), "adequate": False,
                "warning": "k < 3: Egger test not computable"}
    x = np.column_stack([np.ones(n), precision])
    beta, *_ = np.linalg.lstsq(x, snd, rcond=None)
    resid = snd - x @ beta
    dof = n - 2
    sigma2 = float(resid @ resid) / dof
    cov = sigma2 * np.linalg.inv(x.T @ x)
    se_intercept = math.sqrt(cov[0, 0])
    t_stat = beta[0] / se_intercept
    p = 2 * tdist.sf(abs(t_stat), dof)
    ok = n >= min_k
    return {"intercept": float(beta[0]), "se": se_intercept,
            "t": float(t_stat), "p": float(p), "adequate": ok,
            "warning": None if ok else
            "k < %d: low power; do not interpret as evidence for or "
            "against publication bias" % min_k}
