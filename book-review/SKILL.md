---
name: book-review
description: "Write a critical book review / resensi buku — an assessment of a single book or monograph. Use when the object being reviewed is one book (not a body of literature). Covers scholarly book reviews, general-interest reviews, and Indonesian resensi conventions. Trigger terms: book review, resensi buku, review this book, resensi, ulasan buku, menilai buku, bedah buku."
metadata:
  version: "0.1.0"
  genre: book-review
  reporting_standard: "genre conventions (no formal checklist)"
---

# Book Review (Resensi Buku)

You write a critical assessment of **one book**. Your job is judgement, not summary: what the book argues, whether it succeeds, and who should read it.

## Scope

- **In scope:** a single authored or edited book, monograph, or edited volume.
- **Out of scope:** a body of literature (→ `narrative-review`/`systematic-review`), a conceptual debate (→ `critical-review`), or statistical pooling (→ `meta-analysis`). If the object is not a single book, hand back to `review-router`.

## What you need before writing

Ask the author for, or gather:

1. **Bibliographic facts** — author, full title, publisher, year, edition, page count, ISBN.
2. **The book's own thesis** — what it claims to contribute.
3. **Context** — the field, the author's other work, comparable books.
4. **The review's audience & length** — scholarly journal, newspaper, or a class assignment (resensi tugas).

## Method

1. **Situate the book.** One paragraph: author, title, what it sets out to do, and where it sits in the field.
2. **Reconstruct the argument fairly.** Summarize the book's thesis and its main evidence *before* criticizing. A review that misrepresents the book is worthless regardless of its prose.
3. **Evaluate on the book's own terms.** Did it achieve what it set out to do? Assess argument quality, evidence, structure, and prose — not whether the author wrote the book you would have written.
4. **Give a verdict.** Recommend it — to whom, and for what. A review may be mixed; "it's fine" is a verdict if you say why.

## Structure

```
1. Bibliographic heading (author, title, publisher, year, pages, ISBN)
2. Overview (1–2 paras) — what the book is and its central claim
3. Summary of the argument (accurate, concise, spoiler-minimal)
4. Critical assessment — strengths first, then weaknesses, each tied to evidence
5. Verdict & audience — who should read it and why
```

## Genre conventions to respect

- **Scholarly review:** engage the argument on its merits; cite the book by page where you quote or contest a point. Tone is professional, not promotional.
- **Resensi (Indonesian):** commonly opens with bibliographic details and a hook, then *ringkasan isi* (summary), *keunggulan dan kelemahan* (strengths/weaknesses), and *rekomendasi* (recommendation). Match the expected style of the outlet or assignment.
- **Length:** match the venue — a newspaper review is ~500–800 words; a scholarly review is 1,500–3,000 words.

## Decision points (recommendation-first)

- **Audience & length** — recommend by venue: scholarly journal (#1, ~1,500–3,000 words) vs newspaper/class resensi (#2, ~500–800 words); don't ask the author to pick a length blind.
- **Verdict** — recommend the strongest honest verdict (#1), including a mixed one, rather than forcing praise.

## Standards & sources

No EQUATOR-registered checklist and no peer-reviewed *method* standard exists for book reviews (EQUATOR registry, checked 2026); the closest genre definitions come from review typologies such as Grant & Booth (2009, doi:10.1111/j.1471-1842.2009.00848.x). Conventions come from the venue's author guidelines (length, tone, audience) and scholarly review practice; the gate below is the genre's internal contract (faithful representation → evidence-tied critique → explicit verdict). This limitation is recorded in `shared/method_sources.md` rather than hidden behind a borrowed checklist.

## Gate (before calling it done)

- [ ] The book's actual argument is represented before it is criticized.
- [ ] Every criticism names evidence (a page, a chapter, an example).
- [ ] A verdict and intended audience are stated.
- [ ] Bibliographic facts are complete and correct.

## Guardrails

- Do not write the review without the book's thesis — if the author hasn't provided it, ask first; do not fabricate the book's content.
- Keep summary subordinate to judgement; a book review that is only summary fails its purpose.
- You are reviewing the book, not the author's biography or reputation.
