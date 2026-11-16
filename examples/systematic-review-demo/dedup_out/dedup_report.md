# Deduplication report

**Records identified:** 11  
**Duplicates removed:** 4  
**Unique records (to screen):** 7  
**Possible duplicates to check by hand:** 0

## Records per source

| Source | Records |
|---|---:|
| Scopus | 4 |
| PubMed | 4 |
| WoS | 3 |

## Removed by rule

| Rule | Removed |
|---|---:|
| doi | 2 |
| fuzzy | 1 |
| title-year | 1 |

## Next steps (JEV, ranked)

1. **#1 recommended:** Screen `deduplicated.csv`; record decisions in `screening_template.csv` (two reviewers) and run `screening_agreement.py`.
2. Merge `prisma_identification.json` with your screening counts and run `prisma_flow.py prisma_identification.json screening_counts.json`.
3. Report the deduplication method (this tool, rules, threshold) in Methods.
