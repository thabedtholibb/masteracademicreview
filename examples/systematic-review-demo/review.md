# Physical Activity Interventions For Depressive Symptoms In Older Adults: A Systematic Review (DEMO)

**Review type:** systematic review  
**Reporting standard:** PRISMA 2020  
**Sources:** Scopus, PubMed, Web of Science (synthetic demo exports)  
**Search date:** 2026-11-16  
**Gate:** ⚠ partial (PRISMA 24/27)

---

> **Demo only.** Every study, author, journal and DOI in this example is
> fictional. The file exists to show how the tools fit together; it is not
> evidence about exercise or depression.

## Abstract

**Background.** Depressive symptoms are common in later life. **Methods.** We
searched three databases, removed duplicates with `dedup.py`, screened records
in duplicate and synthesised trials narratively. **Results.** Of 11 records,
7 were unique and screened; 3 trials (n = 270) were included. **Conclusions.**
All three trials favoured the intervention; certainty is limited by small samples.

## 1. Introduction

Physical activity is a low-cost option for depressive symptoms in older adults,
but trials differ in the type of activity and in the comparator. This review
asks whether structured physical activity reduces depressive symptoms compared
with usual care or attention control. Reporting follows PRISMA 2020 (Page et al., 2021).

## 2. Methods

The protocol (`protocol.md`) was written before screening. Exports from three
databases were deduplicated with `dedup.py` (DOI, then title and year; one
fuzzy match was checked by hand and merged). Two reviewers screened titles and
abstracts and then full texts; agreement is reported in `agreement.md`. Study
characteristics were extracted into `characteristics.csv` and checked with
`validate_extraction.py`.

## 3. Results

The flow of records is shown in `prisma_flow.svg`. Three randomised trials met
the criteria (Rahman & Wijaya, 2021; Santoso & Lee, 2022; Okafor, 2018). Two
used the GDS-15 and one the PHQ-9.

| Study | Design | N | Intervention | Comparator |
|---|---|---:|---|---|
| Rahman 2021 | RCT | 120 | Walking programme | Usual care |
| Santoso 2022 | RCT | 86 | App-based exercise coaching | Waitlist |
| Okafor 2018 | Cluster RCT | 64 | Resistance training | Social visits |

## 4. Discussion

All included trials reported lower depressive symptoms in the intervention
group, but the samples were small and outcome measures differed, so no pooled
estimate is given. Missing gate items: protocol registration (item 24a),
funding statement (25) and competing interests (26) are not met in this demo.

## References

1. Okafor C. Resistance training and mood in nursing-home residents. *Fictional Geriatric Care*. 2018. doi:10.5555/fict.005
2. Page MJ, McKenzie JE, Bossuyt PM, et al. The PRISMA 2020 statement: an updated guideline for reporting systematic reviews. *BMJ*. 2021;372:n71. doi:10.1136/bmj.n71
3. Rahman A, Wijaya S. Walking programmes and depressive symptoms in older adults: a randomised trial. *Journal of Fictional Ageing*. 2021. doi:10.5555/fict.001
4. Santoso B, Lee M. Digital exercise coaching for older adults with low mood. *Journal of Fictional Ageing*. 2022. doi:10.5555/fict.004
