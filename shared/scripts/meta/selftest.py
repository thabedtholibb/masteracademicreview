"""Self-test for the pooling extensions (needs numpy + scipy).

Run:  python shared/scripts/meta/selftest.py
Checks estimators against independent computations, not hard-coded output.
"""

import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from scipy.optimize import minimize_scalar  # noqa: E402
from scipy.stats import t as tdist  # noqa: E402

from meta import (  # noqa: E402
    egger_test, leave_one_out, meta_regression, prediction_interval,
    random_effects, subgroup_analysis,
)
from meta.pooling import _q_gen  # noqa: E402

Y = [-0.5, 0.1, 0.8, 1.2, 0.3, -0.2, 0.9]
V = [0.04, 0.06, 0.05, 0.09, 0.03, 0.07, 0.08]
FAILS = []


def check(name, cond):
    print("[%s] %s" % ("PASS" if cond else "FAIL", name))
    if not cond:
        FAILS.append(name)


def reml_nll(t):
    w = [1 / (a + t) for a in V]
    mu = sum(a * b for a, b in zip(w, Y)) / sum(w)
    return 0.5 * (sum(math.log(a + t) for a in V) + math.log(sum(w))
                  + sum(a * (b - mu) ** 2 for a, b in zip(w, Y)))


def main():
    dl = random_effects(Y, V)
    check("DL default (tau2 > 0, no HKSJ)", dl["tau2"] > 0 and not dl["hksj"])

    ref = minimize_scalar(reml_nll, bounds=(0, 5), method="bounded",
                          options={"xatol": 1e-10}).x
    reml = random_effects(Y, V, "reml")
    check("REML tau2 matches independent likelihood optimum",
          abs(reml["tau2"] - ref) < 1e-5)

    pm = random_effects(Y, V, "pm")
    check("Paule-Mandel: generalized Q == k-1",
          abs(_q_gen(pm["tau2"], Y, V) - (len(Y) - 1)) < 1e-6)

    h = random_effects(Y, V, "reml", hksj=True)
    se = math.sqrt(h["variance"])
    crit = tdist.ppf(0.975, len(Y) - 1)
    check("HKSJ uses t(k-1) interval",
          abs((h["ci"][1] - h["ci"][0]) / 2 - crit * se) < 1e-9)
    check("HKSJ interval not narrower than unadjusted",
          (h["ci"][1] - h["ci"][0]) >= (reml["ci"][1] - reml["ci"][0]) - 1e-12)

    lo, hi = prediction_interval(h)
    check("prediction interval wider than CI",
          lo < h["ci"][0] and hi > h["ci"][1])
    check("prediction interval undefined for k < 3",
          math.isnan(prediction_interval(random_effects(Y[:2], V[:2]))[0]))

    check("leave-one-out: one result per study",
          len(leave_one_out(Y, V)) == len(Y))

    sg = subgroup_analysis(Y, V, list("aaabbbb"))
    check("subgroup: two groups, df=1, warning for k<10",
          sg["between"]["df"] == 1 and sg["warning"] is not None)

    m0 = meta_regression(Y, V, [], hksj=False)
    check("intercept-only meta-regression == DL random effects",
          abs(m0["coef"][0] - dl["effect"]) < 1e-9
          and abs(m0["tau2"] - dl["tau2"]) < 1e-9)
    mr = meta_regression(Y, V, [list(range(len(Y)))])
    check("meta-regression: 2 coefficients + k<10 warning",
          len(mr["coef"]) == 2 and mr["warning"] is not None)

    eg = egger_test(Y, V)
    check("Egger flagged inadequate when k < 10",
          eg["adequate"] is False and bool(eg["warning"]))
    big_v = [x * (1 + 0.1 * i) for i, x in enumerate(V * 2)]
    check("Egger adequate when k >= 10", egger_test(Y * 2, big_v)["adequate"])

    if FAILS:
        print("%d failed" % len(FAILS))
        return 1
    print("meta selftest OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
