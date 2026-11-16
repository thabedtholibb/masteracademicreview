---
name: meta-analysis
description: "Conduct a meta-analysis — a systematic review plus real statistical pooling of effect sizes, with heterogeneity (I²/Q), forest plot, funnel plot, and Egger's test computed in Python. Use when the author wants to statistically combine results across studies (≥2 studies with extractable effect sizes). Trigger terms: meta-analysis, meta analisis, pooled estimate, effect size pooling, forest plot, heterogeneity, I-squared, random effects, fixed effects."
metadata:
  version: "0.1.0"
  genre: meta-analysis
  reporting_standard: "PRISMA 2020 + MOOSE + GRADE"
  requires_python: true
---

# Meta-Analysis

You do everything a `systematic-review` does, **plus** you statistically combine effect sizes. The statistics are computed by code (`shared/scripts/meta/`), never guessed by the model. This is the one genre where the arithmetic is a hard, deterministic deliverable.

## Scope

- **In scope:** ≥2 studies with extractable effect sizes on a common outcome; the author wants a pooled estimate.
- **Out of scope:** <2 studies or no numeric data (→ `systematic-review`); no protocol (→ `narrative-review`).

## Pre-requisites (fail-closed)

1. Everything required by `systematic-review` (protocol, search, screening, RoB).
2. **≥2 studies** with extractable effect sizes for the target outcome.
3. Python 3.10+ with `numpy`, `scipy`, `pandas`, `matplotlib`.

If there are fewer than 2 studies, pooling is mathematically meaningless — stop and route to `systematic-review`.

## Choosing your inputs (recommendation-first)

- **Effect-size measure** — continuous → **Hedges' g (#1)**; dichotomous → **log odds ratio (#1)** or log risk ratio; correlation → **Fisher z (#1)**. Recommend by data type; don't ask the author to pick blindly.
- **Pooling model** — **random effects (#1, default)**, because studies are rarely identical; use fixed effects only when heterogeneity is trivially low *and* the studies are near-identical.

## Method

1. **Run the full systematic-review protocol** (steps 1–5 of `systematic-review/SKILL.md`).
2. **Extract effect sizes** — follow `shared/data_extraction.md`, then convert each study's result to a common effect size with `shared/scripts/meta/effect_sizes.py`:
   - continuous → `hedges_g(m1, m2, sd1, sd2, n1, n2)`
   - dichotomous → `log_odds_ratio(a, b, c, d)` or `log_risk_ratio(...)`
   - correlation → `fisher_z(r)` + `fisher_z_variance(n)`
3. **Pool** — fixed and random effects with `shared/scripts/meta/pooling.py`:
   ```python
   from pooling import inverse_variance, random_effects, confidence_interval
   re = random_effects(effects, variances)        # random effects (DerSimonian–Laird)
   ci = confidence_interval(re["effect"], re["variance"])
   # re["heterogeneity"] -> {Q, df, p, I2}
   ```
4. **Assess heterogeneity & bias** — report I² and Q; draw forest and funnel plots, and run Egger's test with `shared/scripts/meta/plots.py`:
   ```python
   from plots import forest_plot, funnel_plot, egger_test
   forest_plot(studies, effects, variances, re["effect"], re["variance"], ...)
   funnel_plot(effects, variances, re["effect"], ...)
   egger = egger_test(effects, variances)          # {intercept, se, t, p}
   ```
5. **Rate certainty** — apply GRADE (`shared/risk_of_bias.md`) using I² (inconsistency), CIs (imprecision), RoB, indirectness, and Egger's result (publication bias).
6. **Report** — PRISMA 2020 + MOOSE; include the forest plot, funnel plot, pooled estimate with CI, I², tau², and Egger's test.

An end-to-end runnable demo exists: `shared/scripts/meta/example.py`.

## What the code does (do not re-derive by hand)

| Quantity | Function |
|---|---|
| Hedges' g + variance | `hedges_g` |
| Log OR / log RR | `log_odds_ratio` / `log_risk_ratio` |
| Fixed-effect pooled estimate | `inverse_variance` |
| Random-effects (DL) + tau² | `random_effects` |
| I² and Cochran's Q | `heterogeneity` |
| Forest / funnel plot | `forest_plot` / `funnel_plot` |
| Egger's test | `egger_test` |

## Gate (before calling it done)

- [ ] ≥2 studies pooled; each study's effect size is traceable to extracted data.
- [ ] Fixed *and* random effects reported (report random-effects as primary).
- [ ] I², Q (with p), and tau² reported and interpreted.
- [ ] Forest plot and funnel plot produced from the code, with Egger's result stated.
- [ ] Publication-bias and heterogeneity limitations are discussed (high I² → cautious interpretation).
- [ ] GRADE certainty rating per outcome.

## Guardrails

- **Never fabricate effect sizes, SDs, or sample sizes.** If a study reports medians/IQR, do not silently treat them as mean/SD — flag it and use an established approximation or exclude, per the author.
- The model reasons and interprets; the **code** computes. If a number cannot be produced by the code from real inputs, it does not go in the paper.
- A large I² or significant Egger's test must be reported honestly, not papered over.
