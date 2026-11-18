# Protocol: Physical Activity Interventions For Depressive Symptoms In Older Adults: A Systematic Review (DEMO, Synthetic Data)

**Review type:** systematic review protocol  
**Reporting standard:** PRISMA-P 2015 / PRISMA 2020  
**Planned registry:** PROSPERO (or OSF Registries)  
**Registration ID:** [not yet registered]  
**Protocol date:** 2026-11-18

---

## 1. Administrative Information

**Authors and affiliations:** Demo Author (Example University)  
**Corresponding contact:** demo author, via the repository issue tracker  
**Funding / support:** None  
**Conflicts of interest:** None declared  

## 2. Introduction

**Rationale:** Depressive symptoms are common in later life; physical activity is a low-cost option whose effect across intervention types is unclear.  

**Review question / objectives:** In adults aged 60 or older, do structured physical activity interventions reduce depressive symptoms compared with usual care or attention control?  

## 3. Eligibility Criteria

**Population:** Adults aged 60 or older, community-dwelling or in residential care  
**Intervention / exposure:** Structured physical activity (aerobic, resistance, mind-body, or digitally coached exercise)  
**Comparator:** Usual care, waitlist, or attention control  
**Outcomes (primary / secondary):** Primary: depressive symptoms on a validated scale (GDS, PHQ-9). Secondary: adherence, adverse events  

**Eligible study designs / source types:** Randomised and cluster-randomised controlled trials  
**Language limits:** English and Indonesian  
**Date range:** 2010 to search date  

## 4. Information Sources And Search

**Information sources (databases, registers):** Scopus; PubMed; Web of Science  
**Grey literature / citation searching:** Reference lists of included studies; trial registers  

Search string (one database; peer-review it, e.g. PRESS):

```
("older adult*" OR elderly OR "aged 60") AND (exercise OR "physical activity" OR walking OR "tai chi" OR yoga) AND (depress* OR "low mood")
```

## 5. Study Selection

**Screening: number of independent reviewers, pilot, tool:** Two independent reviewers at title/abstract and full text; pilot on 10% of records  
**Resolving disagreements (third reviewer / consensus):** Discussion, then a third reviewer  

Agreement will be reported with `shared/scripts/screening_agreement.py` (Cohen's kappa / PABAK).

## 6. Data Collection

**Data items to extract; who extracts; piloting:** Design, country, sample size, intervention, comparator, outcome measure; two extractors, piloted form  
**Handling missing data / contacting authors:** Contact corresponding authors once; otherwise report as missing  

Extraction tables will be checked with `shared/scripts/validate_extraction.py`.

## 7. Appraisal And Synthesis

**Risk-of-bias tool (e.g. RoB 2, ROBINS-I, JBI):** RoB 2 (cluster variant for cluster trials)  

**Synthesis plan:** Structured narrative synthesis by intervention type; meta-analysis only if at least 3 trials share an outcome measure  
**Certainty of evidence (e.g. GRADE) or appraisal summary:** GRADE for the primary outcome  

## 8. Timeline

**Timeline:** Search month 1, screening months 2-3, synthesis month 4  

## 9. Amendments Log

Any change after registration is recorded here with its date and reason, and reported in the final review.

| Date | Section | Change | Reason |
|---|---|---|---|
| | | | |

## References

1. Moher D, Shamseer L, Clarke M, et al. Preferred reporting items for systematic review and meta-analysis protocols (PRISMA-P) 2015 statement. *Syst Rev*. 2015;4:1. doi:10.1186/2046-4053-4-1
