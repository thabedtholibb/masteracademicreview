---
name: meta-analysis
description: "Conduct a meta-analysis: a systematic review plus real statistical pooling of effect sizes, with heterogeneity (I²/Q), forest plot, funnel plot, and Egger's test computed in Python. Use when the author wants to statistically combine results across studies (≥2 studies with extractable effect sizes). Trigger terms: meta-analysis, meta analisis, pooled estimate, effect size pooling, forest plot, heterogeneity, I-squared, random effects, fixed effects."
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

## Pre-Requisites (Fail-Closed)

1. Everything required by `systematic-review` (protocol, search, screening, RoB).
2. **≥2 studies** with extractable effect sizes for the target outcome.
3. Python 3.10+ with `numpy`, `scipy`, `pandas`, `matplotlib`.

If there are fewer than 2 studies, pooling is mathematically meaningless: stop and route to `systematic-review`.

## Choosing Your Inputs (JEV)

- **Effect-size measure:** continuous → **Hedges' g (#1)**; dichotomous → **log odds ratio (#1)** or log risk ratio; correlation → **Fisher z (#1)**. Recommend by data type; don't ask the author to pick blindly.
- **Pooling model:** **random effects (#1, default)**, because studies are rarely identical; use fixed effects only when heterogeneity is trivially low *and* the studies are near-identical.

## Method

1. **Run the full systematic-review protocol** (steps 1–5 of `systematic-review/SKILL.md`). Deduplicate the database exports with `mar dedup --source <Name>=<file> ...`: certain duplicates are removed, near-matches are listed for you to decide (JEV), and the PRISMA identification counts are written for you.
2. **Extract effect sizes:** follow `shared/data_extraction.md`, then convert each study's result to a common effect size with `shared/scripts/meta/effect_sizes.py`:
   - continuous → `hedges_g(m1, m2, sd1, sd2, n1, n2)`
   - dichotomous → `log_odds_ratio(a, b, c, d)` or `log_risk_ratio(...)`
   - correlation → `fisher_z(r)` + `fisher_z_variance(n)`
3. **Pool:** fixed and random effects with `shared/scripts/meta/pooling.py`:
   ```python
   from pooling import inverse_variance, random_effects, confidence_interval
   re = random_effects(effects, variances, method="reml", hksj=True)
   # method: "dl" (default) | "reml" | "pm"; hksj=True -> Hartung-Knapp-Sidik-Jonkman
   re["ci"]                                        # CI (t with k-1 df when hksj)
   # re["heterogeneity"] -> {Q, df, p, I2}; re["tau2"]
   ```
   Default to **REML + HKSJ** when k is small or heterogeneity is present; state the estimator in Methods and report DL as a sensitivity analysis when the field expects it.
4. **Assess heterogeneity & bias:** report I² and Q; draw forest and funnel plots, and run Egger's test with `shared/scripts/meta/plots.py`:
   ```python
   from plots import forest_plot, funnel_plot, egger_test
   forest_plot(studies, effects, variances, re["effect"], re["variance"], ...)
   funnel_plot(effects, variances, re["effect"], ...)
   egger = egger_test(effects, variances)          # {intercept, se, t, p, adequate, warning}
   ```
   Egger is flagged `adequate=False` when k < 10: do not interpret it (state this, do not claim "no publication bias").
4b. **Heterogeneity and sensitivity**: report a 95% **prediction interval** (`prediction_interval(re)`, k ≥ 3), run **leave-one-out** (`leave_one_out`), and, only with enough studies, `subgroup_analysis` / `meta_regression` (pre-specified moderators; < 10 studies per moderator is exploratory and returns a `warning`).
5. **Rate certainty:** apply GRADE (`shared/risk_of_bias.md`) using I² (inconsistency), CIs (imprecision), RoB, indirectness, and Egger's result (publication bias).
6. **Report:** PRISMA 2020 + MOOSE; include the forest plot, funnel plot, pooled estimate with CI, I², tau², and Egger's test.

An end-to-end runnable demo exists: `shared/scripts/meta/example.py`.

## What The Code Does (Do Not Re-Derive By Hand)

| Quantity | Function |
|---|---|
| Hedges' g + variance | `hedges_g` |
| Log OR / log RR | `log_odds_ratio` / `log_risk_ratio` |
| Fixed-effect pooled estimate | `inverse_variance` |
| Random-effects (DL/REML/PM, optional HKSJ) + tau² | `random_effects` |
| Prediction interval | `prediction_interval` |
| Leave-one-out sensitivity | `leave_one_out` |
| Subgroup test / meta-regression | `subgroup_analysis` / `meta_regression` |
| I² and Cochran's Q | `heterogeneity` |
| Forest / funnel plot | `forest_plot` / `funnel_plot` |
| Egger's test | `egger_test` |
| Doi plot + LFK index (supplementary; same algorithm as R `metasens::lfkindex`, cross-checked in CI) | `doi_plot` / `lfk_index` |

## Decision Points (JEV)

Every decision here follows the JEV protocol (`../shared/jev.md`): ranked options, **#1 recommended**, one line of evidence each, what would change the ranking, and the author approves. Approved choices go into `decisions.md`.

- **Model.** **#1 recommended:** random effects with REML and the Hartung-Knapp-Sidik-Jonkman adjustment (`random_effects(method="reml", hksj=True)`). #2: DerSimonian-Laird, as a sensitivity analysis or where the field expects it. #3: fixed effect, only if the studies are functionally identical (justify it).
- **Effect measure.** **#1 recommended:** SMD (Hedges' g) when scales differ, MD when all studies share one scale; for binary outcomes the risk ratio (easier to read), or the odds ratio for case-control data.
- **Heterogeneity.** **#1 recommended:** report tau², I² and the 95% prediction interval together. Subgroups and meta-regression only for pre-specified moderators, with at least 10 studies per moderator.
- **Small-study effects.** **#1 recommended:** funnel plot and Egger's test only when k >= 10; with fewer studies, state that it is not assessable (the engine returns `adequate=False`). #2: Doi plot + LFK index (`doi_plot`, `lfk_index`) as a *supplementary* display only: a simulation study found the LFK index does not reliably detect small-study effects (Schwarzer et al. 2024), so never report it alone.
- **Sensitivity.** **#1 recommended:** leave-one-out (`leave_one_out`) plus excluding high risk-of-bias studies.
- *What changes the ranking:* very few studies with high heterogeneity: present the studies without pooling (systematic-review synthesis #2).

## Structure

```
Title (identifies as a meta-analysis)
Abstract (structured)
1. Introduction: rationale, objectives, PICO
2. Methods: protocol, eligibility, search, selection, extraction, effect measure, model and estimator, heterogeneity, small-study effects, certainty
3. Results: study selection (flow diagram), characteristics, pooled estimate (forest plot), heterogeneity and prediction interval, sensitivity analyses, small-study effects (funnel plot), certainty
4. Discussion: interpretation, limitations of the evidence and of the process, implications
References
```

## Standards & Sources

Governing standards: **PRISMA 2020** (Page et al., 2021, doi:10.1136/bmj.n71), **MOOSE** for observational data (Stroup et al., 2000, doi:10.1001/jama.283.15.2008), **GRADE** for certainty (Guyatt et al., 2008, doi:10.1136/bmj.39489.470347.AD). Method sources: Higgins & Thompson 2002 for I²/Q (doi:10.1002/sim.1186), DerSimonian & Laird 1986 for random effects (doi:10.1016/0197-2456(86)90046-2), Egger et al. 1997 (doi:10.1136/bmj.315.7109.629), Duval & Tweedie 2000 (doi:10.1111/j.0006-341X.2000.00455.x), Borenstein et al. 2021. Full citations: `shared/method_sources.md`.

## Gate (Before Calling It Done)

- [ ] ≥2 studies pooled; each study's effect size is traceable to extracted data.
- [ ] `effects.csv` validated (finite effects, variance > 0, one row per study–outcome): `python shared/scripts/validate_extraction.py effects.csv`.
- [ ] Fixed *and* random effects reported (report random-effects as primary).
- [ ] I², Q (with p), and tau² reported and interpreted.
- [ ] Forest plot and funnel plot produced from the code, with Egger's result stated; k < 10 is acknowledged as underpowered for Egger.
- [ ] Publication-bias and heterogeneity limitations are discussed (high I² → cautious interpretation).
- [ ] Dual screening agreement reported (`screening_agreement.py`) or the single-reviewer limitation stated.
- [ ] References checked: `python shared/scripts/verify_refs.py review.md`.
- [ ] GRADE certainty rating per outcome.

**Automated Gate:** run these before you call the review done. Both are offline; `pip install masteracademicreview` provides `mar`.

- [ ] `mar check-review review.md` reports **0 errors**: header fields, the sections this genre needs, citations matched to references, referenced and required artifacts present, no placeholders, and a gate line that matches the checklist. It ranks what to fix first.
- [ ] `mar verify-refs review.md` finds no unresolved citation or duplicate DOI; add `--online` before submission to check every reference against Crossref.

## Guardrails

- **Never fabricate effect sizes, SDs, or sample sizes.** If a study reports medians/IQR, do not silently treat them as mean/SD: flag it and use an established approximation or exclude, per the author.
- The model reasons and interprets; the **code** computes. If a number cannot be produced by the code from real inputs, it does not go in the paper.
- A large I² or significant Egger's test must be reported honestly, not papered over.
