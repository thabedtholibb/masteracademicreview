# Deduplication report

**Records identified:** 11  
**Duplicates removed:** 3  
**Unique records (to screen):** 8  
**Possible duplicates to check by hand:** 1

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
| title-year | 1 |

## Next steps (JEV, ranked)

1. **#1 recommended:** Resolve `possible_duplicates.csv` by hand (highest similarity first); re-run with `--merge-possible` only if every pair is a true duplicate.
2. Screen `deduplicated.csv`; record decisions in `screening_template.csv` (two reviewers) and run `screening_agreement.py`.
3. Merge `prisma_identification.json` with your screening counts and run `prisma_flow.py prisma_identification.json screening_counts.json`.
4. Report the deduplication method (this tool, rules, threshold) in Methods.
