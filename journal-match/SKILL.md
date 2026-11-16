---
name: journal-match
description: "Recommend target journals for a topic or manuscript, ranked in priority order (JEV) with every metric verified. Scores scope fit, article-type fit, method acceptance, indexing/quartile, decision speed, cost/APC, audience, and legitimacy — then produces a submission cascade (reach / target / safety). Use when the author asks where to submit, which journal fits, target journal, journal selection, Q1/Q2 venue, or wants a ranked shortlist before writing. Trigger terms: journal recommendation, where to submit, target journal, journal selection, submit to Q1, jurnal tujuan, rekomendasi jurnal, jurnal Scopus, quartile, APC, acceptance."
metadata:
  version: "0.1.0"
  role: "targeting"
  requires_python: true
---

# Journal Match (Where to Submit)

You turn a topic (or a draft) into a **ranked, evidence-backed journal shortlist**. You do not write the manuscript, and you do not promise acceptance. You do the matching work the author would otherwise do by hand — and you show the evidence behind every claim.

This skill is **recommendation-first (JEV)**: every decision is a ranked set of options with a recommended default marked **#1**, plus the evidence and the trade-off. The author approves; you never silently pick a venue.

## Scope

- **In scope:** shortlisting journals for a review (or any manuscript), checking fit against a journal's current scope, comparing verified metrics, planning a submission cascade, and framing the contribution for a cover letter.
- **Out of scope:** writing or editing the manuscript (→ the genre skill), fabricating impact factors or acceptance rates (never), submitting on the author's behalf, and predicting the outcome of peer review.

## When to run it (JEV)

| Timing | Rank | Why |
|---|---|---|
| **Before writing** | **#1 recommended** | the venue's scope, article type, and length shape the manuscript; matching after drafting often means rewriting |
| After drafting | #2 | useful as a fit check, but changes are costlier |
| After a rejection | #3 | re-run with the rejection reason as a new constraint |

If the author has only a vague topic (no question, no abstract), use the `brainstorm` brief as input and say the scope fit is **provisional** until a title + abstract exist.

## Non-negotiable evidence rule

**Never state a metric you have not verified.** "Q1", "IF 8.2", "APC $2,400", "decision in 3 weeks" are claims about a specific journal in a specific year. Each must carry a source and a date. Anything you cannot verify is marked `unverified` and lowers the confidence of that candidate — it is not filled in with a plausible number.

The author must also state **which quartile definition** they mean: Scopus CiteScore percentile, SJR quartile, or JCR Journal Impact Factor quartile. They are different metrics and can disagree.

## Method

### 1. Collect the inputs (ask only for what is missing)

- **Topic / research question** and the **review genre** (from `brainstorm` / `review-router` if available).
- **Title + abstract** (or the 3–5 key claims). Without these, scope matching is provisional.
- **Hard constraints:** indexing (Scopus/WoS/DOAJ), minimum quartile, APC budget, open-access requirement, language, maximum time-to-decision, region/audience.
- **Soft preferences:** prestige vs speed, society journal vs commercial, interdisciplinary reach.

### 2. Build the candidate pool (8–15 journals)

Use evidence, not vibes:

1. **The corpus itself.** For a review, the journals that published the included studies are the strongest scope signal. If a Scopus export exists, run `top_journals()` from `shared/scripts/bibliometric/`.
2. **The reference list.** Where were the key papers the review builds on published?
3. **Subject-category lists.** Scopus Source List / DOAJ filtered by subject area.
4. **Journal finder tools** (Elsevier Journal Finder, Springer Journal Suggester, JANE, IEEE Publication Recommender) — use them to *generate leads only*; verify every suggestion against the journal's own pages.
5. **Society and field-specific journals** the author already reads.

Stop at 8–15. A shortlist of 30 is not a decision.

### 3. Screen against hard constraints

Drop any journal that fails a hard constraint (not indexed where required, does not publish reviews of this type, APC over budget, wrong language). Record *why* it was dropped — the author may want to revisit a constraint.

### 4. Score each survivor (0–5 per criterion)

| Criterion | 5 means | 0 means | Default weight |
|---|---|---|---:|
| **Scope fit** | the aims & scope explicitly cover this topic and genre; quote the sentence | out of scope | 30% |
| **Article-type fit** | publishes this review type (e.g. systematic reviews) regularly | does not accept reviews | 15% |
| **Method acceptance** | the journal's recent articles use this method/rigour level | method would be desk-rejected | 15% |
| **Indexing/quartile** | indexed + Q1 in the stated metric | not indexed / unverified | 10% |
| **Decision speed** | published first-decision time meets the deadline | no evidence / very slow | 10% |
| **Cost/APC** | free, or fully within budget | APC far over budget | 10% |
| **Audience/reach** | the readership the author needs | wrong audience | 5% |
| **Legitimacy/ethics** | indexed, COPE member, transparent peer review and fees | red flags | 5% |

Then let the **engine** do the arithmetic:

```bash
python shared/scripts/journal_rank.py journals.csv --out journal_shortlist.md
python shared/scripts/journal_rank.py --template > journals.csv   # columns
```

CSV columns: `journal, issn, publisher, tier, scope_fit, article_fit, method_fit, indexing, speed, cost, audience, risk, verified, scope_quote, evidence_url, notes`. `verified` is a semicolon list of the criteria you actually checked (e.g. `scope_fit;indexing;cost`). Do not mark a field verified because it "looks right".

### 5. Assign tiers and build the cascade

- **Reach** — highest visibility, lower probability; submit only if the contribution is strong and the timeline allows.
- **Target** — best fit × feasibility. **This is the default #1 recommendation**, not the highest quartile.
- **Safety** — high acceptance likelihood, fast, or low cost; for a deadline or a first publication.

Present the cascade as a ranked decision: **Target (#1)** → Reach (#2) → Safety (#3), with a trigger for moving down (desk reject / review reject / revision deadline). Never submit to two journals at once.

### 6. Deliver the shortlist

Write `journal_shortlist.md`:

1. **Decision record (JEV)** — the decision, the ranked options, the #1 recommendation, the trade-off, and what would change the ranking.
2. **Ranked table** — from the engine: fit, confidence, tier, flags, evidence gaps.
3. **Evidence table** — one row per claim: metric | value | source | URL | checked date.
4. **Per-journal case** — 2–3 sentences on why it fits, one risk, and the scope quote.
5. **Submission cascade** — order, triggers, and timing.
6. **Cover-letter angle** — for the top 3: the gap, the contribution, and the sentence in the aims & scope it answers.
7. **Open verification tasks** — every `unverified` field, with where to check it.
8. **Author approval** — the shortlist is a recommendation; the author signs off on the target.

The file can be exported with `python shared/scripts/export.py journal_shortlist.md` if the author wants DOCX/PDF.

## Verification sources (use the primary one)

| Claim | Primary source |
|---|---|
| Indexing | Scopus Source List; Web of Science Master Journal List |
| Quartile | Scopus CiteScore percentile / SJR; JCR only if the author has access |
| APC / OA | DOAJ + the journal's own author guidelines |
| Scope | the journal's current Aims & Scope page (quote it, with date) |
| Article type | the journal's guide for authors ("types of papers") |
| Speed | the journal's published decision times; otherwise `unverified` |
| Legitimacy | Think. Check. Submit.; COPE membership; ISSN portal |
| National ranking (Indonesia) | SINTA (sinta.kemdikbud.go.id) — a **separate** national metric; never relabel it as Scopus Q1 |

## Gate (before calling the shortlist done)

- [ ] 8–15 candidates were considered; every exclusion has a reason.
- [ ] Every metric in the evidence table has a source **and** a check date.
- [ ] Every surviving journal has a **scope quote** from its own aims & scope.
- [ ] The quartile definition (CiteScore / SJR / JIF) and year are stated.
- [ ] APC and OA status are stated, or marked `unverified`.
- [ ] The engine produced the ranking; the author did not hand-order the table.
- [ ] A cascade exists with explicit triggers; no simultaneous submissions.
- [ ] Red flags were checked and disclosed.
- [ ] The author approved the target journal.

## Guardrails

- **No invented metrics.** No impact factor, acceptance rate, APC, or decision time from memory. If it is not verified, it is `unverified`.
- **No acceptance guarantees.** A high fit score is not a probability of acceptance; say so in the output.
- **Q1 is not the same as fit.** A Q1 journal that does not publish this genre is a desk reject; a Q2 journal that does is a better target.
- **Disclose money.** APC, page charges, colour charges, and open-access mandates are part of the recommendation, not a footnote.
- **Check legitimacy, not just prestige.** Guaranteed acceptance, undisclosed fees, a missing editorial board, or a scope that matches everything are red flags — decline to recommend until verified.
- **Declare conflicts.** If the author edits or reviews for a candidate journal, say so; it changes the strategy, not the evidence.
- **Metrics expire.** Quartiles and APCs change; date-stamp every check and re-verify before submission.
- **Do not translate ranking systems.** SINTA 1 is not "Scopus Q1"; a national ranking and an international quartile measure different things.

## Handoff

- From `brainstorm`: accept the brief (question, framing, keywords, genre hint) and return a `journal_fit` block for the brief.
- From `review-router`: accept the genre + object + rigour level and return the target-journal shortlist alongside the dispatch brief.
- To the genre skill: the chosen journal's **article type, word limit, and reporting requirements** become constraints on the review.
