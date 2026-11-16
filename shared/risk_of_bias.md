# Risk Of Bias & Certainty Of Evidence (Shared Core)

Use for `systematic-review` and `meta-analysis`. Assess the *internal validity* of each included study (risk of bias) and then, if synthesizing, the *certainty* of the body of evidence (GRADE). This is separate from data extraction: extraction records what the study reports; risk-of-bias judges how trustworthy that is.

## 1. Pick The Right Tool By Study Design

| Design | Tool |
|---|---|
| Randomized trials | **RoB 2** (Cochrane) |
| Non-randomized interventions | **ROBINS-I** |
| Cohort / case-control | **Newcastle–Ottawa Scale (NOS)** |
| Diagnostic accuracy | **QUADAS-2** |
| Cross-sectional / prevalence | **JBI checklist** or adapted NOS |
| Qualitative | **CASP Qualitative** checklist |
| Overview of reviews (umbrella) | **AMSTAR-2** |

**Recommendation-first:** when the design is clear, state the tool and proceed; when it is ambiguous, recommend the closest tool as **#1** and name the runner-up: do not hand the author the whole table as an open question. Never apply a tool meant for RCTs to an observational study.

## 2. Judge Per-Domain, Not A Single Score

Rate each domain (e.g. RoB 2: randomization, deviations, missing outcome data, measurement, selective reporting) as **low / some concerns / high** (or equivalent). Summarize per study and across studies (e.g. a traffic-light table). Do **not** collapse to a single numeric score unless the chosen tool does so explicitly (NOS does; RoB 2 does not).

## 3. Certainty Of Evidence (GRADE)

When the review makes summary judgements, rate certainty per outcome across five domains:

- Risk of bias (from step 2)
- Inconsistency (heterogeneity, I²)
- Imprecision (wide CIs, small samples)
- Indirectness (PICO mismatch)
- Publication bias (funnel asymmetry, Egger's test: see `meta/plots.py`)

Rate as **high / moderate / low / very low**, and downgrade with a stated reason. GRADE is for the *body* of evidence, not individual studies.

## 4. Report, Don't Editorialize

Present the risk-of-bias table and GRADE ratings transparently. A high-risk-of-bias result constrains interpretation ("evidence is low certainty"), it does not license overclaiming.

## Guardrails

- Risk-of-bias judgements require reading the methods: do not guess from the abstract alone.
- Keep risk-of-bias separate from statistical significance: a large effect in a high-risk study is still high risk.
- GRADE downgrades are cumulative and each needs a written justification.
