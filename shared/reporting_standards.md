# Reporting Standards (Shared Core)

Most review genres have a reporting standard: a checklist that makes the review transparent and reproducible. masteracademicreview treats these as **gates**: a review that skips a checklist item is flagged before it is considered done. Two genres (critical review, book review) have **no EQUATOR-registered checklist**; they use an explicit internal contract instead, and the suite says so rather than borrowing a standard that does not fit.

The full citation for every standard, with a Crossref-verified DOI, is in [`method_sources.md`](method_sources.md).

## Standards By Genre

| Genre | Standard | What It Mandates |
|---|---|---|
| Systematic review | **PRISMA 2020** + **PRISMA-S** | 27 items + flow diagram + search reporting |
| Meta-analysis | **PRISMA 2020** + **MOOSE** + **GRADE** | search, pooling method, heterogeneity, bias, certainty |
| Scoping review | **PRISMA-ScR** | 22 items, breadth mapping, optional appraisal |
| Rapid review | **Cochrane rapid-review guidance** + adapted PRISMA | streamlined conduct, every shortcut declared |
| Narrative review | **SANRA** | 6-item scale (justification, aims, search, sources, evidence, synthesis) |
| Meta-synthesis | **ENTREQ** | 21 items on transparency of qualitative synthesis |
| Umbrella review | **PRIOR** | reporting of overviews of reviews; AMSTAR-2 + overlap |
| Realist review | **RAMESES** | theory-driven explanation, CMO reporting |
| Integrative review | **Whittemore & Knafl (2005)** | 5 stages; no EQUATOR checklist exists |
| Mapping review | **ROSES** | pro forma, flow diagram, descriptive summary |
| Bibliometric review | **PRISMA 2020** (search) + bibliometric method guidance | corpus retrieval, document-type filter, reproducible analysis |
| Critical review | *No formal checklist* | thesis + argument discipline (internal contract) |
| Book review | *No formal checklist* | faithful representation + evidence-cited verdict (internal contract) |

## PRISMA 2020 (The 27 Items, Grouped)

1. **Title:** identifies as systematic review/meta-analysis.
2. **Abstract:** structured summary.
3. **Rationale:** why the review is needed.
4. **Objectives:** explicit question(s) with PICO.
5. **Eligibility criteria:** inclusion/exclusion with rationale.
6. **Information sources:** databases, registers, other sources, last search date.
7. **Search strategy:** full strategy for ≥1 database, reproducible.
8. **Selection process:** who screened, how, independent/dual?
9. **Data collection:** how extracted, forms piloted?
10. **Data items:** outcomes and variables sought.
11. **Risk of bias:** tool(s) used per outcome.
12. **Effect measures:** e.g. RR, mean difference, SMD.
13. **Synthesis methods:** criteria for pooling, heterogeneity, sensitivity.
14. **Reporting bias:** how assessed (funnel, Egger).
15. **Certainty:** GRADE or similar.
16. **Study selection:** numbers screened/assessed/included (flow diagram).
17. **Study characteristics:** table of included studies.
18. **Risk of bias in studies:** per-study results.
19. **Results of individual studies:** summary statistics + CIs.
20. **Results of syntheses:** pooled estimates, heterogeneity.
21. **Reporting biases:** results of bias assessment.
22. **Certainty of evidence:** GRADE summary.
23. **Discussion (a):** interpretation in context.
24. **Discussion (b):** limitations of evidence.
25. **Discussion (c):** limitations of review process.
26. **Discussion (d):** implications.
27. **Other:** registration, protocol, funding, conflicts, data availability.

## PRISMA-S (Search Reporting)

Five domains, applied whenever a search is part of the method:

- **Information sources:** every database named; multi-database searching; registries; online resources/browsing; citation searching; contacts; other methods.
- **Search strategies:** the full strategy for each database (not just keywords); limits and restrictions; date of the last search; peer review of the strategy.
- **Strategy development:** who developed it and how it was validated.
- **Deduplication:** the method used and the number removed.
- **Documentation:** enough detail for another reviewer to rerun the search exactly.

## PRISMA-ScR (20 Essential + 2 Optional = 22 Items)

1. Title · 2. Structured summary · 3. Rationale · 4. Objectives · 5. Protocol and registration · 6. Eligibility criteria · 7. Information sources · 8. Search · 9. Selection of sources of evidence · 10. Data charting · 11. Data items · **12. Critical appraisal of individual sources (optional)** · 13. Synthesis of results · 14. Selection of sources of evidence (results) · 15. Characteristics of sources of evidence · **16. Critical appraisal within sources (optional)** · 17. Results of individual sources of evidence · 18. Synthesis of results · 19. Summary of evidence · 20. Limitations · 21. Conclusions · 22. Funding.

Items 12 and 16 are optional: a scoping review may skip appraisal, but if it is done, the rationale, method, and results must be reported. Five original PRISMA items were dropped as not applicable: summary measures (13), risk of bias across studies (15) and within results (22), and additional analyses (16) with their results (23).

## SANRA (6 Items)

1. Justification of the review's importance.
2. Concrete statement of aims.
3. Description of the literature search (sources, terms, limits).
4. Referencing: key statements carry citations.
5. Scientific reasoning: conclusions follow from the cited evidence.
6. Appropriate presentation of data (tables/figures where they help).

## ENTREQ (21 Items)

1. Aim · 2. Synthesis methodology · 3. Approach to searching · 4. Inclusion criteria · 5. Data sources · 6. Electronic search strategy · 7. Study screening methods · 8. Study characteristics · 9. Study selection results · 10. Rationale for appraisal · 11. Appraisal items · 12. Appraisal process · 13. Appraisal results · 14. Data extraction · 15. Software · 16. Number of reviewers · 17. Coding · 18. Study comparison · 19. Derivation of themes · 20. Quotations · 21. Synthesis output.

The items ENTREQ makes hard to fake: **how themes were derived** (item 19: inductive or deductive), **how studies were compared** (item 18), and whether the output **goes beyond a summary** of the primary studies (item 21).

## PRIOR (Overviews Of Reviews)

PRIOR covers: title and abstract; rationale and objectives; eligibility criteria for reviews; information sources and search; selection process; data collection; appraisal of included reviews (e.g. AMSTAR-2); **overlap between reviews** (e.g. corrected covered area); synthesis methods; certainty of evidence; results (including a flow diagram and a characteristics-of-reviews table); discussion; registration, funding, conflicts of interest, and data availability.

Two PRIOR-specific obligations this suite enforces:
- **AMSTAR-2 confidence rating** for every included review.
- **Corrected covered area (CCA)** to quantify primary-study overlap across reviews.

## RAMESES (Realist Syntheses)

RAMESES covers: title; abstract; rationale; objectives; **changes to the protocol**; search strategy; selection and appraisal by relevance and rigour; analysis and synthesis (CMO development); documents and data; funding; conflicts of interest; limitations; implications. It expects the **programme theory** and its refinement to be visible, not just the final CMOs.

## Cochrane Rapid-Review Guidance

The gate is not a fixed checklist but a **declaration contract**, built from the Cochrane Rapid Reviews Methods Group guidance:

- every shortcut is named (databases, screening duplication, extraction, appraisal, synthesis);
- the search and selection remain reproducible from the reported detail;
- the deadline and the reason for each shortcut are stated;
- the review is never presented as a full systematic review.

## ROSES (Systematic Maps)

ROSES has three components: a **pro forma** (rationale, objectives, searches, eligibility, screening, coding, appraisal), a **flow diagram** of the mapping process, and a **descriptive summary** of the plan and conduct. For evidence and gap maps, the matrix/framework and the cell-level gap statement are additional mandatory artifacts.

## MOOSE (Observational Meta-Analysis)

MOOSE covers six domains: background; search strategy; methods (eligibility, data extraction, appraisal, pooling); results (flow, characteristics, estimates, heterogeneity, bias); discussion; conclusion. It is used **alongside** PRISMA 2020, not instead of it.

## AMSTAR-2 (16 Items)

1. PICO in the research question and inclusion criteria · 2. Protocol established a priori, deviations justified · 3. Explanation of study designs selected · 4. Comprehensive literature search · 5. Study selection in duplicate · 6. Data extraction in duplicate · 7. List of excluded studies with reasons · 8. Adequate description of included studies · 9. Satisfactory risk-of-bias technique · 10. Funding sources of included studies reported · 11. Appropriate statistical combination (if meta-analysis) · 12. Impact of risk of bias on the pooled result assessed · 13. Risk of bias accounted for in interpretation · 14. Satisfactory explanation of heterogeneity · 15. Publication-bias investigation (if quantitative synthesis) · 16. Conflicts of interest and funding reported.

Confidence rating: **high / moderate / low / critically low**: a *critically low* review must not carry a strong conclusion in an umbrella review.

## GRADE (5 Downgrade Domains)

Risk of bias · inconsistency · indirectness · imprecision · publication bias. Certainty is rated **high / moderate / low / very low** per outcome, with the reason for each downgrade stated.

## How Gates Work

For each genre, the skill defines a concrete checklist. At completion, the skill:

1. walks the checklist item by item;
2. marks each **present / partial / missing**;
3. **flags** any `missing` item and refuses to call the review "done" until it is either satisfied or explicitly waived by the author with a reason.

A gate is a *check*, not a barrier to honesty: an author can waive an item, but the waiver must be recorded.

## Guardrails

- The checklist is the floor, not the ceiling: satisfying PRISMA does not make a bad review good; it makes it transparent.
- Do not claim a standard was followed if the corresponding artifact (e.g. the PRISMA flow diagram, the AMSTAR-2 table) was not produced.
- Never import a checklist from another genre to look rigorous. A book review with a PRISMA diagram is a category error.
- Report the checklist version and, for search standards, the date of the last search.
