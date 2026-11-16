# Journal Evidence Worksheet

One block per candidate journal. Fill it **from the journal's own pages**, then
copy the scores into `journals.csv`. Score only against the anchors
(`python shared/scripts/journal_rank.py --rubric`): 5 / 3 / 1 / 0.
Do not scrape Scopus or any source whose terms forbid it; look the value
up manually and record where and when.

**Journal:** ______________________  **ISSN:** __________  **Publisher:** __________
**Checked on (date):** __________  **Checked by:** __________
**Quartile definition used:** CiteScore percentile / SJR / JIF (circle one), year ____

| Criterion | Score (0/1/3/5) | Evidence (What You Saw) | Source URL | Verified? |
|---|---|---|---|---|
| Scope fit | | **scope_quote** (verbatim sentence from Aims & Scope; required if score >= 3): | | |
| Article-type fit | | recent reviews of this type (titles + years): | | |
| Method acceptance | | recent articles using this method (titles): | | |
| Indexing / quartile | | indexed in ____; quartile ____ (metric, year) | | |
| Decision speed | | published first-decision time: ____ days | | |
| Cost / APC | | APC ____ ; OA model ____ ; waiver policy ____ | | |
| Audience / reach | | who reads it; fit with target readers | | |
| Legitimacy / ethics | | COPE / Think.Check.Submit / board / fees transparent? | | |

**Hard-constraint check:** indexing [ ]  quartile [ ]  APC budget [ ]  language [ ]  time [ ]
**Dropped?** yes / no. Reason: ______________________
**Conflicts of interest with this journal:** ______________________

**CSV columns (copy the row into journals.csv):**

```
journal,issn,publisher,tier,scope_fit,article_fit,method_fit,indexing,speed,cost,audience,risk,verified,scope_quote,evidence_url,notes
```

`verified` = semicolon list of criteria whose value you checked at the source
(e.g. `scope_fit;indexing;cost`). Leave a criterion out if you did not check it.
