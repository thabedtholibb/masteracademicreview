#!/usr/bin/env python3
"""Protocol generator: protocol.md per review genre (PROSPERO / OSF fields).

Turns a small JSON of decisions into a registration-ready protocol document,
following PRISMA-P (Moher et al. 2015) and the genre's own standard. Anything
you have not decided is written as ``[TO COMPLETE: field]`` and listed at the
end, so a protocol can never look finished when it is not.

    python protocol.py --template systematic-review > protocol.json
    python protocol.py protocol.json --out protocol.md
    python protocol.py protocol.json --strict      # exit 1 while fields are open
    python protocol.py --selftest

Stdlib only. The generator writes what you decided; it does not invent
eligibility criteria, search strings or analysis plans.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _textio import read_text
import contextlib

PICO = [("population", "Population"), ("intervention", "Intervention / exposure"),
        ("comparator", "Comparator"), ("outcomes", "Outcomes (primary / secondary)")]
PCC = [("population", "Population"), ("concept", "Concept"), ("context", "Context")]
SPIDER = [("sample", "Sample"), ("phenomenon", "Phenomenon of interest"),
          ("design", "Design"), ("evaluation", "Evaluation"),
          ("research_type", "Research type")]
OPEN = [("population", "Population / setting"), ("concept", "Concept / phenomenon")]

# genre -> registry, reporting standard, eligibility framework, extra fields
GENRES = {
    "systematic-review": {
        "registry": "PROSPERO (or OSF Registries)", "standard": "PRISMA-P 2015 / PRISMA 2020",
        "framework": PICO, "extra": [
            ("rob_tool", "Risk-of-bias tool (e.g. RoB 2, ROBINS-I, JBI)")]},
    "meta-analysis": {
        "registry": "PROSPERO (or OSF Registries)", "standard": "PRISMA-P 2015 / PRISMA 2020 + MOOSE",
        "framework": PICO, "extra": [
            ("rob_tool", "Risk-of-bias tool"),
            ("effect_measure", "Effect measure (SMD/Hedges g, log OR, log RR, Fisher z)"),
            ("model", "Pooling model and tau-squared estimator (e.g. REML + Hartung-Knapp)"),
            ("heterogeneity_plan", "Heterogeneity assessment (I2, Q, tau2, prediction interval)"),
            ("sensitivity_plan", "Sensitivity analyses (leave-one-out, RoB exclusion)"),
            ("subgroup_plan", "Pre-specified subgroup / meta-regression moderators"),
            ("bias_plan", "Small-study / publication bias plan (Egger only if k >= 10)")]},
    "scoping-review": {
        "registry": "OSF Registries (PROSPERO does not accept scoping reviews)",
        "standard": "PRISMA-ScR + JBI scoping guidance", "framework": PCC, "extra": [
            ("charting_form", "Data-charting form and variables"),
            ("consultation", "Stakeholder consultation (optional)")]},
    "mapping-review": {
        "registry": "OSF Registries", "standard": "PRISMA 2020 (adapted) / ROSES",
        "framework": PCC, "extra": [("coding_framework", "Coding framework / map dimensions")]},
    "umbrella-review": {
        "registry": "PROSPERO (or OSF Registries)", "standard": "PRIOR + AMSTAR-2",
        "framework": PICO, "extra": [
            ("appraisal_tool", "Quality appraisal of included reviews (AMSTAR-2)"),
            ("overlap_method", "Overlap of primary studies (corrected covered area)")]},
    "rapid-review": {
        "registry": "PROSPERO (rapid reviews with health outcomes) or OSF",
        "standard": "PRISMA 2020 + Cochrane Rapid Reviews guidance", "framework": PICO, "extra": [
            ("shortcuts", "Streamlining steps taken (each one named explicitly)"),
            ("time_limit", "Time limit / resource constraint"),
            ("rob_tool", "Risk-of-bias approach (single reviewer? verified?)")]},
    "realist-review": {
        "registry": "PROSPERO (accepts realist reviews) or OSF", "standard": "RAMESES",
        "framework": OPEN, "extra": [
            ("initial_theory", "Initial programme theory"),
            ("iterative_search", "Iterative search plan"),
            ("appraisal_plan", "Relevance and rigour appraisal"),
            ("cmo_plan", "Context-mechanism-outcome extraction and refinement")]},
    "meta-synthesis": {
        "registry": "PROSPERO (qualitative syntheses) or OSF", "standard": "ENTREQ + PRISMA 2020",
        "framework": SPIDER, "extra": [
            ("appraisal_tool", "Appraisal (e.g. CASP qualitative)"),
            ("synthesis_method", "Synthesis method (thematic synthesis, meta-ethnography)")]},
    "integrative-review": {
        "registry": "OSF Registries (no dedicated registry)",
        "standard": "Whittemore & Knafl 2005 (no EQUATOR checklist)", "framework": OPEN,
        "extra": [("appraisal_plan", "Quality appraisal across diverse designs"),
                  ("integration_method", "Data reduction, display and comparison method")]},
}

COMMON = [
    ("authors", "Authors and affiliations"), ("contact", "Corresponding contact"),
    ("funding", "Funding / support"), ("coi", "Conflicts of interest"),
    ("rationale", "Rationale"), ("question", "Review question / objectives"),
    ("study_designs", "Eligible study designs / source types"),
    ("language", "Language limits"), ("date_range", "Date range"),
    ("databases", "Information sources (databases, registers)"),
    ("grey_literature", "Grey literature / citation searching"),
    ("search_string", "Draft search string for one database"),
    ("screening_reviewers", "Screening: number of independent reviewers, pilot, tool"),
    ("disagreement", "Resolving disagreements (third reviewer / consensus)"),
    ("extraction_items", "Data items to extract; who extracts; piloting"),
    ("missing_data", "Handling missing data / contacting authors"),
    ("synthesis_plan", "Synthesis plan"),
    ("certainty_plan", "Certainty of evidence (e.g. GRADE) or appraisal summary"),
    ("timeline", "Timeline"),
]


def template(genre: str) -> dict:
    spec = GENRES[genre]
    keys = ["title", "registration_id"]
    keys += [k for k, _ in COMMON] + [k for k, _ in spec["framework"]] + [k for k, _ in spec["extra"]]
    data = {k: "" for k in dict.fromkeys(keys)}
    data["genre"] = genre
    data["databases"] = []
    return data


def _val(data: dict, key: str, missing: list[str]) -> str:
    v = data.get(key, "")
    if isinstance(v, list):
        v = "; ".join(str(x) for x in v if str(x).strip())
    v = str(v).strip()
    if not v:
        missing.append(key)
        return f"[TO COMPLETE: {key}]"
    return v


def render(data: dict) -> tuple[str, list[str]]:
    genre = data.get("genre", "")
    if genre not in GENRES:
        raise ValueError("unknown or non-registrable genre {!r}; choose from: {}".format(genre, ", ".join(GENRES)))
    spec = GENRES[genre]
    missing: list[str] = []
    labels = dict(COMMON)
    labels.update(dict(spec["framework"]))
    labels.update(dict(spec["extra"]))

    def row(key: str) -> str:
        return f"**{labels[key]}:** {_val(data, key, missing)}  "

    title = _val(data, "title", missing)
    reg = str(data.get("registration_id", "")).strip() or "[not yet registered]"
    out = [
        f"# Protocol: {title}", "",
        "**Review type:** {} protocol  ".format(genre.replace("-", " ")),
        "**Reporting standard:** {}  ".format(spec["standard"]),
        "**Planned registry:** {}  ".format(spec["registry"]),
        f"**Registration ID:** {reg}  ",
        f"**Protocol date:** {date.today().isoformat()}", "",
        "---", "",
        "## 1. Administrative Information", "",
        row("authors"), row("contact"), row("funding"), row("coi"), "",
        "## 2. Introduction", "", row("rationale"), "", row("question"), "",
        "## 3. Eligibility Criteria", "",
    ]
    out += [row(k) for k, _ in spec["framework"]]
    out += ["", row("study_designs"), row("language"), row("date_range"), "",
            "## 4. Information Sources And Search", "",
            row("databases"), row("grey_literature"), "",
            "Search string (one database; peer-review it, e.g. PRESS):", "",
            "```", _val(data, "search_string", missing), "```", "",
            "## 5. Study Selection", "", row("screening_reviewers"), row("disagreement"), "",
            "Agreement will be reported with `shared/scripts/screening_agreement.py` (Cohen's kappa / PABAK).", "",
            "## 6. Data Collection", "", row("extraction_items"), row("missing_data"), "",
            "Extraction tables will be checked with `shared/scripts/validate_extraction.py`.", "",
            "## 7. Appraisal And Synthesis", ""]
    out += [row(k) for k, _ in spec["extra"]]
    out += ["", row("synthesis_plan"), row("certainty_plan"), "",
            "## 8. Timeline", "", row("timeline"), "",
            "## 9. Amendments Log", "",
            "Any change after registration is recorded here with its date and reason, "
            "and reported in the final review.", "",
            "| Date | Section | Change | Reason |", "|---|---|---|---|",
            "| | | | |", "",
            "## References", "",
            "1. Moher D, Shamseer L, Clarke M, et al. Preferred reporting items for systematic "
            "review and meta-analysis protocols (PRISMA-P) 2015 statement. *Syst Rev*. 2015;4:1. "
            "doi:10.1186/2046-4053-4-1", ""]
    if missing:
        out += ["---", "", f'**Open fields ({len(set(missing)):d}):** {", ".join(dict.fromkeys(missing))}', ""]
    return "\n".join(out), list(dict.fromkeys(missing))


def selftest() -> None:
    for g in GENRES:
        t = template(g)
        text, miss = render(t)
        assert "[TO COMPLETE: title]" in text and "title" in miss, g
        assert "Open fields" in text
        assert "**Review type:**" in text and "## 9. Amendments Log" in text
    t = template("meta-analysis")
    assert "effect_measure" in t and "model" in t
    t.update({"title": "X", "question": "Does A improve B?", "databases": ["Scopus", "PubMed"]})
    text, miss = render(t)
    assert "Scopus; PubMed" in text and "question" not in miss
    try:
        render({"genre": "book-review"})
    except ValueError:
        pass
    else:
        raise AssertionError("non-registrable genre must be rejected")
    print(f"protocol selftest OK ({len(GENRES):d} genres)")


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        with contextlib.suppress(AttributeError, ValueError):
            stream.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description="Generate protocol.md for a review genre.")
    p.add_argument("input", nargs="?", help="protocol.json")
    p.add_argument("--template", choices=sorted(GENRES), help="print an empty JSON for this genre")
    p.add_argument("--out", type=Path, help="write protocol.md here")
    p.add_argument("--strict", action="store_true", help="exit 1 while fields are still open")
    p.add_argument("--selftest", action="store_true")
    a = p.parse_args(argv)
    if a.selftest:
        selftest()
        return 0
    if a.template:
        print(json.dumps(template(a.template), indent=2, ensure_ascii=False))
        return 0
    if not a.input:
        p.error("provide protocol.json (or --template GENRE / --selftest)")
    try:
        raw = read_text(a.input)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            what = "is empty" if not raw.strip() else f"is not valid JSON (line {exc.lineno}, column {exc.colno}: {exc.msg})"
            raise ValueError(f"{a.input} {what}; create a starting file with: protocol.py --template GENRE") from exc
        if not isinstance(data, dict):
            raise ValueError(f"{a.input} must hold one JSON object (see: protocol.py --template GENRE)")
        text, missing = render(data)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if a.out:
        a.out.write_text(text, encoding="utf-8")
        print(f"wrote {a.out} ({len(missing):d} open fields)")
    else:
        print(text)
    return 1 if (a.strict and missing) else 0


if __name__ == "__main__":
    raise SystemExit(main())
