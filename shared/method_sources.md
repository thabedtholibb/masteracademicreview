# Method Sources & Provenance

This file answers one question: **why should a reviewer trust the method this suite encodes?**

Every genre skill is built on a published methodological standard plus the peer-reviewed literature that defines how that standard is applied. The **governing standard** is the checklist used as a gate; the **method sources** are the papers/books the workflow steps come from. Nothing here is invented for the suite.

> **On "Q1".** Q1 is a *venue metric* (a CiteScore/SJR/JIF quartile), not a certificate that a method is correct. What this suite can guarantee is that each genre follows the **methodological and reporting bar Q1 reviewers apply** in that field — a reproducible search, a declared protocol where the genre requires one, design-matched risk-of-bias appraisal, an appropriate synthesis, a certainty judgement, and the reporting checklist attached. Journal quartiles are handled separately by the `journal-match` skill, with every metric verified and date-stamped.

**Verification.** All journal citations below were resolved against **Crossref on 2026-11-16** (DOI, journal, year, volume, pages checked). Books, handbooks and reporting-guideline websites that have no DOI are listed separately with their publisher or canonical URL. Re-verify a DOI before quoting it in a manuscript; publishers occasionally re-register metadata.

---

## 1. Standards map — all 13 genres

| Genre | Governing standard | Primary publication | DOI | Gate |
|---|---|---|---|---|
| Systematic review | **PRISMA 2020** + **PRISMA-S** (search) | Page et al. 2021; Rethlefsen et al. 2021 | `10.1136/bmj.n71`; `10.1186/s13643-020-01542-z` | 27 items + flow diagram |
| Meta-analysis | **PRISMA 2020** + **MOOSE** + **GRADE** | Page et al. 2021; Stroup et al. 2000; Guyatt et al. 2008 | `10.1136/bmj.n71`; `10.1001/jama.283.15.2008`; `10.1136/bmj.39489.470347.AD` | PRISMA/MOOSE + pooled estimate + GRADE |
| Scoping review | **PRISMA-ScR** | Tricco et al. 2018 | `10.7326/M18-0850` | 22 items + flow diagram |
| Rapid review | **Cochrane rapid-review guidance** + adapted PRISMA | Garritty et al. 2021; Garritty et al. 2024 | `10.1016/j.jclinepi.2020.10.007`; `10.1136/bmj-2023-076335` | declared shortcuts |
| Narrative review | **SANRA** | Baethge et al. 2019 | `10.1186/s41073-019-0064-8` | 6 items |
| Meta-synthesis | **ENTREQ** | Tong et al. 2012 | `10.1186/1471-2288-12-181` | 21 items |
| Umbrella review | **PRIOR** | Gates et al. 2022 | `10.1136/bmj-2022-070849` | PRIOR + AMSTAR-2 + CCA |
| Realist review | **RAMESES** | Wong et al. 2013 | `10.1186/1741-7015-11-21` | RAMESES |
| Integrative review | **Whittemore & Knafl** (no EQUATOR checklist) | Whittemore & Knafl 2005; Torraco 2005 | `10.1111/j.1365-2648.2005.03621.x`; `10.1177/1534484305278283` | 5 stages + integrated synthesis |
| Mapping review | **ROSES** | Haddaway et al. 2018 | `10.1186/s13750-018-0121-7` | pro forma + flow + map |
| Bibliometric review | **PRISMA 2020** (search) + bibliometric method guidance | Page et al. 2021; Donthu et al. 2021 | `10.1136/bmj.n71`; `10.1016/j.jbusres.2021.04.070` | documented corpus + reproducible analysis |
| Critical review | *No formal checklist*; review typology + argument method | Grant & Booth 2009; Paré et al. 2015; Snyder 2019 | `10.1111/j.1471-1842.2009.00848.x`; `10.1016/j.im.2014.08.008`; `10.1016/j.jbusres.2019.07.039` | thesis + argument discipline |
| Book review | *No formal checklist*; venue conventions | See §4 — no EQUATOR standard exists | — | genre contract |

**Honest gaps.** Critical reviews and book reviews have **no EQUATOR-registered reporting guideline**. The suite says so rather than borrowing a checklist that does not fit, and substitutes an explicit internal contract (thesis/argument for critical; argument-faithfulness/verdict for book). Integrative reviews likewise have a canonical *method* paper but no EQUATOR checklist; ROSES covers systematic maps, which is the closest fit for mapping reviews.

---

## 2. Method sources by genre

### Systematic review
- Page MJ, McKenzie JE, Bossuyt PM, et al. The PRISMA 2020 statement: an updated guideline for reporting systematic reviews. *BMJ*. 2021;372:n71. doi:10.1136/bmj.n71
- Page MJ, Moher D, Bossuyt PM, et al. PRISMA 2020 explanation and elaboration: updated guidance and exemplars for reporting systematic reviews. *BMJ*. 2021;372:n160. doi:10.1136/bmj.n160
- Rethlefsen ML, Kirtley S, Waffenschmidt S, et al. PRISMA-S: an extension to the PRISMA statement for reporting literature searches in systematic reviews. *Syst Rev*. 2021;10:39. doi:10.1186/s13643-020-01542-z
- Sterne JAC, Savović J, Page MJ, et al. RoB 2: a revised tool for assessing risk of bias in randomised trials. *BMJ*. 2019;366:l4898. doi:10.1136/bmj.l4898
- Sterne JA, Hernán MA, Reeves BC, et al. ROBINS-I: a tool for assessing risk of bias in non-randomised studies of interventions. *BMJ*. 2016;355:i4919. doi:10.1136/bmj.i4919
- Guyatt GH, Oxman AD, Vist GE, et al. GRADE: an emerging consensus on rating quality of evidence and strength of recommendations. *BMJ*. 2008;336(7650):924-926. doi:10.1136/bmj.39489.470347.AD
- *Cochrane Handbook for Systematic Reviews of Interventions*, version 6.4. Cochrane; 2023. https://training.cochrane.org/handbook

### Meta-analysis
- Stroup DF, Berlin JA, Morton SC, et al. Meta-analysis of observational studies in epidemiology: a proposal for reporting. *JAMA*. 2000;283(15):2008-2012. doi:10.1001/jama.283.15.2008
- Higgins JPT, Thompson SG. Quantifying heterogeneity in a meta-analysis. *Stat Med*. 2002;21(11):1539-1558. doi:10.1002/sim.1186
- DerSimonian R, Laird N. Meta-analysis in clinical trials. *Control Clin Trials*. 1986;7(3):177-188. doi:10.1016/0197-2456(86)90046-2
- Hartung J, Knapp G. On tests of the overall treatment effect in meta-analysis with normally distributed responses. *Stat Med*. 2001;20(12):1771-1782. doi:10.1002/sim.791
- Sidik K, Jonkman JN. A simple confidence interval for meta-analysis. *Stat Med*. 2002;21(21):3153-3159. doi:10.1002/sim.1262
- IntHout J, Ioannidis JPA, Borm GF. The Hartung-Knapp-Sidik-Jonkman method for random effects meta-analysis is straightforward and considerably outperforms the standard DerSimonian-Laird method. *BMC Med Res Methodol*. 2014;14:25. doi:10.1186/1471-2288-14-25
- Higgins JPT, Thompson SG, Spiegelhalter DJ. A re-evaluation of random-effects meta-analysis. *J R Stat Soc A*. 2009;172(1):137-159. doi:10.1111/j.1467-985X.2008.00552.x
- Paule RC, Mandel J. Consensus values and weighting factors. *J Res Natl Bur Stand*. 1982;87(5):377-385. doi:10.6028/jres.087.022
- Viechtbauer W. Bias and efficiency of meta-analytic variance estimators in the random-effects model. *J Educ Behav Stat*. 2005;30(3):261-293. doi:10.3102/10769986030003261
- Sterne JAC, Sutton AJ, Ioannidis JPA, et al. Recommendations for examining and interpreting funnel plot asymmetry in meta-analyses of randomised controlled trials. *BMJ*. 2011;343:d4002. doi:10.1136/bmj.d4002
- Furuya-Kanamori L, Barendregt JJ, Doi SAR. A new improved graphical and quantitative method for detecting bias in meta-analysis. *Int J Evid Based Healthc*. 2018;16(4):195-203. doi:10.1097/XEB.0000000000000141
- Schwarzer G, Rücker G, Semaca C. LFK index does not reliably detect small-study effects in meta-analysis: a simulation study. *Res Synth Methods*. 2024;15(4):603-615. doi:10.1002/jrsm.1714
- Egger M, Davey Smith G, Schneider M, Minder C. Bias in meta-analysis detected by a simple, graphical test. *BMJ*. 1997;315(7109):629-634. doi:10.1136/bmj.315.7109.629
- Duval S, Tweedie R. Trim and fill: a simple funnel-plot-based method of testing and adjusting for publication bias in meta-analysis. *Biometrics*. 2000;56(2):455-463. doi:10.1111/j.0006-341X.2000.00455.x
- Viechtbauer W. Conducting meta-analyses in R with the metafor package. *J Stat Softw*. 2010;36(3):1-48. doi:10.18637/jss.v036.i03
- Borenstein M, Hedges LV, Higgins JPT, Rothstein HR. *Introduction to Meta-Analysis*. 2nd ed. Wiley; 2021.

### Scoping review
- Moher D, Shamseer L, Clarke M, et al. Preferred reporting items for systematic review and meta-analysis protocols (PRISMA-P) 2015 statement. *Syst Rev*. 2015;4:1. doi:10.1186/2046-4053-4-1
- Tricco AC, Lillie E, Zarin W, et al. PRISMA Extension for Scoping Reviews (PRISMA-ScR): checklist and explanation. *Ann Intern Med*. 2018;169(7):467-473. doi:10.7326/M18-0850
- Arksey H, O'Malley L. Scoping studies: towards a methodological framework. *Int J Soc Res Methodol*. 2005;8(1):19-32. doi:10.1080/1364557032000119616
- Levac D, Colquhoun H, O'Brien KK. Scoping studies: advancing the methodology. *Implement Sci*. 2010;5:69. doi:10.1186/1748-5908-5-69
- Peters MDJ, Marnie C, Tricco AC, et al. Updated methodological guidance for the conduct of scoping reviews. *JBI Evid Synth*. 2020;18(10):2119-2126. doi:10.11124/JBIES-20-00167

### Rapid review
- Garritty C, Gartlehner G, Nussbaumer-Streit B, et al. Cochrane Rapid Reviews Methods Group offers evidence-informed guidance to conduct rapid reviews. *J Clin Epidemiol*. 2021;130:13-22. doi:10.1016/j.jclinepi.2020.10.007
- Garritty C, Gartlehner G, Nussbaumer-Streit B, et al. Updated recommendations for the Cochrane rapid review methods guidance for rapid reviews of effectiveness. *BMJ*. 2024;384:e076335. doi:10.1136/bmj-2023-076335
- Tricco AC, Antony J, Zarin W, et al. A scoping review of rapid review methods. *BMC Med*. 2015;13:224. doi:10.1186/s12916-015-0465-6
- Khangura S, Konnyu K, Cushman R, Grimshaw J, Moher D. Evidence summaries: the evolution of a rapid review approach. *Syst Rev*. 2012;1:10. doi:10.1186/2046-4053-1-10

### Narrative review
- Baethge C, Goldbeck-Wood S, Mertens S. SANRA—a scale for the quality assessment of narrative review articles. *Res Integr Peer Rev*. 2019;4:5. doi:10.1186/s41073-019-0064-8
- Greenhalgh T, Thorne S, Malterud K. Time to challenge the spurious hierarchy of systematic over narrative reviews? *Eur J Clin Invest*. 2018;48(6):e12931. doi:10.1111/eci.12931

### Critical review
- Grant MJ, Booth A. A typology of reviews: an analysis of 14 review types and associated methodologies. *Health Info Libr J*. 2009;26(2):91-108. doi:10.1111/j.1471-1842.2009.00848.x
- Paré G, Trudel MC, Jaana M, Kitsiou S. Synthesizing information systems knowledge: a typology of literature reviews. *Inf Manage*. 2015;52(2):183-199. doi:10.1016/j.im.2014.08.008
- Snyder H. Literature review as a research methodology: an overview and guidelines. *J Bus Res*. 2019;104:333-339. doi:10.1016/j.jbusres.2019.07.039

### Integrative review
- Whittemore R, Knafl K. The integrative review: updated methodology. *J Adv Nurs*. 2005;52(5):546-553. doi:10.1111/j.1365-2648.2005.03621.x
- Torraco RJ. Writing integrative literature reviews: guidelines and examples. *Hum Resour Dev Rev*. 2005;4(3):356-367. doi:10.1177/1534484305278283
- Hopia H, Latvala E, Liimatainen L. Reviewing the methodology of an integrative review. *Scand J Caring Sci*. 2016;30(4):662-669. doi:10.1111/scs.12327

### Mapping review
- Haddaway NR, Macura B, Whaley P, Pullin AS. ROSES RepOrting standards for Systematic Evidence Syntheses: pro forma, flow-diagram and descriptive summary of the plan and conduct of environmental systematic reviews and systematic maps. *Environ Evid*. 2018;7:7. doi:10.1186/s13750-018-0121-7
- Saran A, White H. Evidence and gap maps: a comparison of different approaches. *Campbell Syst Rev*. 2018;14(1):1-38. doi:10.4073/cmdp.2018.2

### Bibliometric review
- Donthu N, Kumar S, Mukherjee D, Pandey N, Lim WM. How to conduct a bibliometric analysis: an overview and guidelines. *J Bus Res*. 2021;133:285-296. doi:10.1016/j.jbusres.2021.04.070
- Zupic I, Čater T. Bibliometric methods in management and organization. *Organ Res Methods*. 2015;18(3):429-472. doi:10.1177/1094428114562629
- van Eck NJ, Waltman L. Software survey: VOSviewer, a computer program for bibliometric mapping. *Scientometrics*. 2010;84(2):523-538. doi:10.1007/s11192-009-0146-3
- Aria M, Cuccurullo C. bibliometrix: an R-tool for comprehensive science mapping analysis. *J Informetr*. 2017;11(4):959-975. doi:10.1016/j.joi.2017.08.007

### Umbrella review
- Gates M, Gates A, Pieper D, et al. Reporting guideline for overviews of reviews of healthcare interventions: development of the PRIOR statement. *BMJ*. 2022;378:e070849. doi:10.1136/bmj-2022-070849
- Aromataris E, Fernandez R, Godfrey CM, Holly C, Khalil H, Tungpunkom P. Summarizing systematic reviews: methodological development, conduct and reporting of an umbrella review approach. *Int J Evid Based Healthc*. 2015;13(3):132-140. doi:10.1097/XEB.0000000000000055
- Shea BJ, Reeves BC, Wells G, et al. AMSTAR 2: a critical appraisal tool for systematic reviews that include randomised or non-randomised studies of healthcare interventions, or both. *BMJ*. 2017;358:j4008. doi:10.1136/bmj.j4008
- Pieper D, Buechter RB, Li L, Prediger B, Eikermann M. Systematic review found AMSTAR, but not R(evised)-AMSTAR, to have good measurement properties. *J Clin Epidemiol*. 2015;68(5):574-583. doi:10.1016/j.jclinepi.2014.12.009

### Meta-synthesis
- Tong A, Flemming K, McInnes E, Oliver S, Craig J. Enhancing transparency in reporting the synthesis of qualitative research: ENTREQ. *BMC Med Res Methodol*. 2012;12:181. doi:10.1186/1471-2288-12-181
- Thomas J, Harden A. Methods for the thematic synthesis of qualitative research in systematic reviews. *BMC Med Res Methodol*. 2008;8:45. doi:10.1186/1471-2288-8-45
- Lockwood C, Munn Z, Porritt K. Qualitative research synthesis: methodological guidance for systematic reviewers utilizing meta-aggregation. *Int J Evid Based Healthc*. 2015;13(3):179-187. doi:10.1097/XEB.0000000000000062
- Flemming K, Booth A, Hannes K, Cargo M, Noyes J. Cochrane Qualitative and Implementation Methods Group guidance series—paper 6: reporting guidelines for qualitative, implementation, and process evaluation evidence syntheses. *J Clin Epidemiol*. 2018;97:79-85. doi:10.1016/j.jclinepi.2017.10.022
- Noblit GW, Hare RD. *Meta-Ethnography: Synthesizing Qualitative Studies*. Sage; 1988.
- Sandelowski M, Barroso J. *Handbook for Synthesizing Qualitative Research*. Springer; 2007.

### Realist review
- Pawson R, Greenhalgh T, Harvey G, Walshe K. Realist review—a new method of systematic review designed for complex policy interventions. *J Health Serv Res Policy*. 2005;10(Suppl 1):21-34. doi:10.1258/1355819054308530
- Wong G, Greenhalgh T, Westhorp G, Buckingham J, Pawson R. RAMESES publication standards: realist syntheses. *BMC Med*. 2013;11:21. doi:10.1186/1741-7015-11-21

### Book review
- No EQUATOR-registered reporting guideline and no peer-reviewed *method* standard exists for book reviews. Conventions come from the **review venue's author guidelines** (length, tone, audience) and from scholarly review practice. The skill's gate is therefore an internal contract, not an external checklist: represent the book's argument faithfully → tie every criticism to evidence (page/chapter) → state a verdict and audience.
- Bibliographic style: the venue's required style manual (e.g. Chicago, APA), not a method source.

---

## 3. Shared method components

| Component | Source | What the suite takes |
|---|---|---|
| Structured question | PICO for effectiveness, PICo/SPIDER for qualitative, PCC for mapping | framing is chosen by question type, not habit |
| Search reporting | PRISMA-S (Rethlefsen et al. 2021) | databases, full strategies, limits, dates, deduplication |
| Risk of bias (RCT) | RoB 2 (Sterne et al. 2019) | five domains + overall judgement |
| Risk of bias (non-randomised) | ROBINS-I (Sterne et al. 2016) | seven domains, target-trial logic |
| Risk of bias (reviews) | AMSTAR 2 (Shea et al. 2017) | 16 items + confidence rating |
| Risk of bias (mixed methods) | MMAT 2018 (Hong et al. 2018, doi:10.3233/EFI-180221) | five criteria per design |
| Qualitative appraisal | CASP Qualitative Checklist | trustworthiness, not exclusion |
| Certainty of evidence | GRADE (Guyatt et al. 2008) | risk of bias, inconsistency, indirectness, imprecision, publication bias |
| Inter-rater agreement | Cohen 1960; Landis & Koch 1977 | κ and its interpretation bands |
| Agreement with skewed prevalence | Byrt et al. 1993 | PABAK, prevalence and bias indices |
| Heterogeneity | Higgins & Thompson 2002 | I², Cochran's Q |
| Random-effects pooling | DerSimonian & Laird 1986 | tau², pooled estimate |
| tau² estimators | Paule & Mandel 1982; Viechtbauer 2005 | PM and REML options in `random_effects` |
| Small-k interval adjustment | Hartung & Knapp 2001; Sidik & Jonkman 2002; IntHout et al. 2014 | `hksj=True` |
| Prediction interval | Higgins et al. 2009 | `prediction_interval` |
| Small-study test adequacy | Sterne et al. 2011 | Egger guard (k ≥ 10) |
| Doi plot / LFK index | Furuya-Kanamori et al. 2018; limitation: Schwarzer et al. 2024 | `doi_plot`, `lfk_index` (supplementary only) |
| Small-study effects | Egger et al. 1997; Duval & Tweedie 2000 | Egger's test, trim-and-fill |
| Mixed-methods reviews | Pluye & Hong 2014 (doi:10.1146/annurev-publhealth-032013-182440) | integrating qualitative + quantitative evidence |
| Scoping/mapping conduct | JBI Manual for Evidence Synthesis (2024) | PCC, charting, optional appraisal |

**Agreement statistics:** Cohen J. A coefficient of agreement for nominal scales. *Educ Psychol Meas*. 1960;20(1):37-46. doi:10.1177/001316446002000104 · Landis JR, Koch GG. The measurement of observer agreement for categorical data. *Biometrics*. 1977;33(1):159-174. doi:10.2307/2529310 · Byrt T, Bishop J, Carlin JB. Bias, prevalence and kappa. *J Clin Epidemiol*. 1993;46(5):423-429. doi:10.1016/0895-4356(93)90018-V.

---

## 4. Venue metrics and journal targeting

These are **not** methodological citations. They are the evidence base the `journal-match` skill requires before a journal can be recommended:

| Claim | Must be verified against | Notes |
|---|---|---|
| Indexing | Scopus Source List; Web of Science Master Journal List | check the ISSN, not just the title |
| Quartile | Scopus CiteScore percentile / SJR quartile; JCR only if the author has access | always state **which metric** and **which year** |
| Open access & APC | DOAJ; the journal's own author guidelines | "hybrid" is not the same as "free" |
| Scope fit | the journal's current Aims & Scope page | quote the sentence that matches, with date |
| Legitimacy | Think. Check. Submit.; COPE membership; ISSN portal | guarantees of acceptance and undisclosed fees are red flags |
| Speed | the journal's published decision times; recent reports | if unknown, mark `unverified` — do not guess |

**Sources:** DOAJ (https://doaj.org) · Scopus Source List (https://www.elsevier.com/solutions/scopus/how-scopus-works/content) · Scimago Journal Rank (https://www.scimagojr.com) · Web of Science Master Journal List (https://mjl.clarivate.com) · Think. Check. Submit. (https://thinkchecksubmit.org) · COPE (https://publicationethics.org).

---

## 5. Q1-readiness checklist (applies to every genre)

A Q1 editor or reviewer will typically check the following. The genre gates cover them; this list is the cross-genre audit.

- [ ] **Gap statement** — the review answers a question the literature has not already answered.
- [ ] **Protocol** — registered (PROSPERO/OSF) where the genre requires it; deviations reported.
- [ ] **Reproducible search** — databases, full strategies, limits, dates, deduplication (PRISMA-S).
- [ ] **Eligibility criteria** — explicit, applied consistently, with ordered exclusion reasons.
- [ ] **Dual processes** — screening and extraction performed independently, with agreement reported (`screening_agreement.py`).
- [ ] **Risk of bias** — design-matched tool, per-study results, not a single aggregate score.
- [ ] **Synthesis** — method matches the data (pooling, thematic, CMO, mapping); heterogeneity handled.
- [ ] **Certainty** — GRADE or the genre's equivalent, with reasons for downgrading.
- [ ] **Reporting checklist** — completed checklist attached as a supplement, not just cited.
- [ ] **Data availability** — extraction sheet, search log, analysis code available.
- [ ] **Reference integrity** — every in-text citation resolves, no duplicate DOIs, DOI-bearing references spot-checked (`verify_refs.py`).
- [ ] **Limitations** — of the evidence *and* of the review process, stated separately.
- [ ] **Funding/COI and AI-use disclosure** — per the venue's policy.

A review that cannot tick these is not ready for a Q1 submission regardless of how well it is written. The gates in each skill are the mechanism; this checklist is the audit.
