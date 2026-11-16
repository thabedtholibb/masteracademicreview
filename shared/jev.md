# JEV: the decision protocol of this suite

**JEV** is how every skill in this suite makes a decision with the author:
**rank the options, recommend #1, show the evidence, let the author decide.**
It applies to choices of method (which database, which model, which journal)
and to priorities of work (which gate item, which reviewer comment first).

A skill never silently picks for the author, and never dumps an unranked menu
on them either.

## The five rules

1. **Rank.** Present 2–4 realistic options in priority order. Mark the first
   **#1 recommended**. More than four options is a list, not a decision.
2. **Justify.** Each option gets one line: why it ranks there, and its main
   trade-off. The #1 reason should cite the standard, a method source
   (`shared/method_sources.md`) or the author's own constraint.
3. **Say what would change the ranking.** One sentence: "If you have no
   effect sizes, #2 becomes #1." This is what makes the recommendation honest.
4. **The author decides.** Wait for approval on decisions that change the
   review (genre, protocol, eligibility, model, journal). If the author says
   "you choose", take #1 and record that.
5. **Record it.** Every approved decision goes into the decision log (below),
   so the Methods section and the response to reviewers can cite it.

## Priority of work (when several things are open)

Rank open work by how much it blocks the verdict, highest first:

| Priority | What | Why first |
|---:|---|---|
| **#1** | Integrity errors: unresolved citations, invented or wrong references, numbers that do not add up | an editor rejects for these, and they are the hardest to defend |
| #2 | Missing required artifacts and genre sections (flow diagram, RoB table, protocol) | the reporting standard cannot be met without them |
| #3 | Method choices that are not justified in the text | reviewers ask for them first |
| #4 | Placeholders, header fields, formatting | quick, but still blockers |
| #5 | Warnings and polish | improve the review, rarely decide it |

`check_review.py` prints its findings in this order ("Next steps (JEV, ranked)"),
and `submission.py response` ranks reviewer comments the same way: major first.

## Template for one decision

```markdown
**Decision: <what is being decided>**

1. **#1 recommended — <option>.** <why; source or constraint> Trade-off: <...>
2. #2 — <option>. <why it is second> Trade-off: <...>
3. #3 — <option>. <when it would be right>

What would change the ranking: <one sentence>.
Your call: approve #1, or pick another.
```

## Decision log

Keep `decisions.md` next to `review.md`:

| Date | Decision | Options (ranked) | Chosen | Evidence / reason | Approved by |
|---|---|---|---|---|---|
| 2026-01-10 | Pooling model | #1 REML + HKSJ · #2 DL · #3 fixed effect | #1 | k = 7, I² = 62%; IntHout et al. 2014 | author |

## Where JEV is built into the tools

| Tool | JEV behaviour |
|---|---|
| `dedup.py` | certain duplicates removed; uncertain ones only *recommended* (`possible_duplicates.csv`); the kept copy is chosen by a ranked rule |
| `journal_rank.py` | ranked shortlist, **#1 recommended**, anchored scores, `--explain` |
| `submission.py` | cover letter for the **#1** clean journal; a flagged #1 is refused with the next clean rank named; reviewer comments ranked major → minor |
| `check_review.py` | findings printed as ranked next steps (integrity first) |
| `protocol.py` | registries listed in order of preference per genre |
| `review-router` skill | top 2–3 genres, #1 recommended |
