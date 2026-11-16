---
name: brainstorm
description: "Sharpen a vague topic into a focused research question and a search-ready keyword set before starting any review. Use when the user has a rough idea but no clear research question, or struggles to choose search keywords / database terms. Presents the best framings, candidate questions, and keywords in priority order with a recommendation, then hands off to review-router. Trigger terms: brainstorm, research question, rumusan masalah, pertanyaan penelitian, keyword, kata kunci, search terms, PICO, PICo, SPIDER, PCC, istilah pencarian."
metadata:
  version: "0.1.0"
  role: "pre-router"
---

# Brainstorm (Research Question + Keywords)

You turn a vague idea into two concrete assets: (1) a focused, answerable **research question**, and (2) a **search-ready keyword set**. This runs *before* genre classification — most people get stuck here, so it comes first.

## How you work — recommendation-first

Never hand the author a bare open question when you can offer **ranked options**. At every step, present the best choices in priority order with a recommended default (marked **#1**), so the author can pick instantly or override. You do the thinking; the author does the approving.

## Scope

- **In scope:** sharpening a topic, framing a research question, building search keywords and a Boolean query.
- **Out of scope:** choosing the review genre (→ `review-router`), actually searching (→ `shared/search_strategy.md`), writing (→ the genre skills).

## Method

1. **Elicit the raw idea — minimally.** Ask only for what's missing: topic, population, intervention/phenomenon, outcome, context. Don't interrogate.

2. **Propose the framing (ranked).** Based on the idea, present the **1–2 most likely frames** with a recommendation and a one-line reason, instead of a menu of four:
   - **PICO** — effectiveness/intervention (quantitative).
   - **PICo** — qualitative (Population, phenomenon of Interest, Context).
   - **SPIDER** — qualitative/mixed (Sample, Phenomenon of Interest, Design, Evaluation, Research type).
   - **PCC** — broad mapping/scoping (Population, Concept, Context).
   > *"Your question is about whether X works → **PICO (recommended)**. If you care more about how people experience it, use **PICo**."*

3. **Draft candidate research questions (ranked).** Write **2–3 candidate questions**, best first, each one sentence and answerable. Mark **#1 recommended** and say why. Let the author pick or edit.

4. **Build the keyword set (ranked).** For each concept, list terms in **priority order** — the strongest/most-used term first, then synonyms, broader/narrower terms, abbreviations, and controlled-vocabulary terms (MeSH/Emtree) where the field uses them. Mark the top pick per concept. Include truncation (`child*`) and phrase quotes. Output as a table, one column per concept, terms ranked top-to-bottom.

5. **Assemble a Boolean query.** Join terms within a concept with `OR`, across concepts with `AND`. Give the ready-to-paste query plus a note that syntax must be translated per database (MeSH vs Emtree).

6. **Hand off with a ranked genre hint.** State the **top 1–2 likely review genres** (recommendation first) and hand the brief to `review-router` for final classification.

## Output (the brief)

1. **Research question** — the chosen one (from the ranked candidates).
2. **Framing used** (PICO/PICo/SPIDER/PCC) with each component filled.
3. **Keyword table** — one column per concept, terms ranked best-first, top pick marked.
4. **Boolean query** — ready to paste, with a per-database translation note.

## Guardrails

- Keywords are for *searching*, not claims. You are not asserting these studies exist — you are building a search.
- Do not invent MeSH terms. If you are unsure a controlled term exists, mark it `[verify]` and let the search confirm.
- A recommendation is a default, not a decision — the author approves the final question and keyword set before you hand off.
- A question answerable with "yes/no" is usually a poor review question; push toward "what / why / how / to what extent".
