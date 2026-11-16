# Data Extraction (shared core)

Use for `systematic-review` and `meta-analysis`. Extraction turns included full texts into structured data — a characteristics table for any review, plus an effect-size dataset for meta-analysis.

## 1. Design the extraction form first

Define exactly which fields you will extract, before touching the studies. Typical fields:

- **Study identity**: first author, year, country, design, sample size, setting.
- **PICO fields**: population details, intervention/exposure, comparator, outcome (definition + how measured).
- **Results**: for each outcome, the summary statistic and its precision (mean/SD/n, events/n, OR/RR/HR with CI, correlation r with n).
- **Quality signals**: anything needed for risk-of-bias (allocation concealment, blinding, follow-up, etc.).

Use a spreadsheet/CSV; one row per study (or per study–outcome pair for meta-analysis).

## 2. Extract, don't interpret

Record what the study reports. If a value is missing, record `missing` — never impute without a stated, defensible rule.

## 3. Effect-size data for meta-analysis

For `meta-analysis`, extraction must yield, per outcome:

- **Continuous**: n, mean, SD for each arm (or mean difference + its SD/CI).
- **Dichotomous**: 2×2 table (events/non-events per arm), or OR/RR with CI.
- **Correlation**: r and n.

Handle the common conversion cases explicitly (the `meta/effect_sizes.py` module does the arithmetic):

- SD missing but SE/CI given → derive SD.
- Median/IQR reported → do **not** silently treat as mean/SD; flag and use an established approximation (Wan et al.) or exclude, per author's call.
- Continuity correction (0.5) for zero cells in 2×2 tables.

## 4. Missing data & contact

Track what is missing and, where feasible, note that authors were contacted. Do not fabricate values to complete a table.

## 5. Output

- `characteristics.csv` — the study characteristics table (feeds the review's Table 1).
- `effects.csv` — the effect-size dataset (feeds `meta/pooling.py`).

Validate both before synthesis:

```
python shared/scripts/validate_extraction.py effects.csv --profile meta --out extraction_check.md
python shared/scripts/validate_extraction.py characteristics.csv --profile generic --required study,year,design --key study
```

`effects.csv` must have one row per study–outcome, finite effects, and variance > 0. The validator errors on impossible values and warns when k < 10 (Egger's test is underpowered below 10 studies). `--strict` turns warnings into failures when the protocol requires it.

## Guardrails

- Extraction is transcription of reported values, not your judgement about whether the study was "good" — that is risk-of-bias's job, kept separate.
- One row per study–outcome in `effects.csv`, so a study contributing two outcomes is not double-counted as two studies in the analysis.
