#!/usr/bin/env python3
"""Submission documents wired to journal-match and the gate.

Two subcommands:

  cover-letter  review.md + the journal_rank.py JSON shortlist (+ the
                check_review.py report) -> cover_letter.md for the #1
                recommended journal (JEV; --rank N to pick another).
  response      reviewer comments (plain text) -> a ranked revision plan
                and a point-by-point response skeleton.

    python submission.py cover-letter review.md --shortlist journal_shortlist.json \\
        --gate-report review_check.md --out cover_letter.md
    python submission.py response reviewer_comments.txt --review review.md \\
        --out response_to_reviewers.md
    python submission.py cover-letter ... --lang id      # Indonesian letter
    python submission.py --selftest

Guards (fail-closed):
  - no cover letter while the gate is "failed" or the gate report has errors;
    "partial" needs --allow-partial-gate (and stays visible in the checklist);
  - no cover letter for a journal flagged LEGITIMACY RISK or SCOPE MISMATCH;
    the tool names the next clean candidate instead.
Everything the tool cannot know is written as [TO COMPLETE: ...]; it never
invents a contribution, a funding statement or a registration number.

Stdlib only. Exit codes: 0 = written, 1 = refused by a guard, 2 = bad input.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _textio import read_text
import contextlib

HERE = Path(__file__).resolve().parent
BLOCKING_FLAGS = ("LEGITIMACY RISK", "SCOPE MISMATCH")
REGISTRABLE = {"systematic-review", "meta-analysis", "scoping-review", "umbrella-review",
               "rapid-review", "realist-review", "meta-synthesis", "mapping-review"}


class SubmissionError(Exception):
    pass


class Refused(Exception):
    pass


def _check_review():
    spec = importlib.util.spec_from_file_location("_mar_check_review", HERE / "check_review.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["_mar_check_review"] = module
    spec.loader.exec_module(module)
    return module


def read_review(path: Path) -> dict:
    if not path.is_file():
        raise SubmissionError(f"file not found: {path}")
    text = read_text(path)
    cr = _check_review()
    meta, _ = cr.parse_metadata(text.splitlines())
    title = ""
    for line in text.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break
    gate = meta.get("gate", "")
    m = cr.GATE_STATUS_RE.search(gate)
    return {
        "title": title or "[TO COMPLETE: title]",
        "review_type": meta.get("review type", ""),
        "genre": cr.detect_genre(meta.get("review type", ""), None),
        "standard": meta.get("reporting standard", ""),
        "sources": meta.get("sources", ""),
        "search_date": meta.get("search date", ""),
        "registration": meta.get("registration", "") or meta.get("registration id", ""),
        "gate_line": gate,
        "gate_status": cr.GATE_CANON[m.group(1).lower()] if m else "missing",
    }


def read_gate_report(path: Path | None) -> int | None:
    if path is None:
        return None
    if not path.is_file():
        raise SubmissionError(f"gate report not found: {path} (run check_review.py --out first)")
    m = re.search(r"\*\*Errors:\*\*\s*(\d+)", read_text(path))
    if not m:
        raise SubmissionError(f"{path} is not a check_review.py report")
    return int(m.group(1))


def read_shortlist(path: Path) -> list[dict]:
    if not path.is_file():
        raise SubmissionError(f"shortlist not found: {path} (run journal_rank.py --json)")
    data = json.loads(read_text(path))
    cands = data.get("candidates") if isinstance(data, dict) else data
    if not cands:
        raise SubmissionError(f"{path} has no candidates")
    return cands


# --------------------------------------------------------------------------- #
# Cover letter
# --------------------------------------------------------------------------- #

TEXT = {
    "en": {
        "salutation": "Dear Editor,",
        "re": 'Re: Submission of a {atype}, "{title}"',
        "intro": 'Please consider the enclosed manuscript, "{title}", for publication in '
                 "*{journal}* as a {atype}.",
        "why": "**Why {journal}.** Your aims and scope state: “{quote}” "
               "[TO COMPLETE: one sentence linking this scope to the review question.]",
        "adds": "**What the review adds.** [TO COMPLETE: the gap, in two sentences.] "
                "[TO COMPLETE: the main finding and why it matters to your readers.]",
        "how": "**How it was done.** The review is reported according to {standard}{reg}. "
               "Sources searched: {sources}; last search: {search_date}.",
        "reg_yes": " and its protocol was registered ({reg})",
        "reg_todo": " [TO COMPLETE: protocol registration ID, or state that it was not registered and why]",
        "decl": "**Declarations.** This manuscript is original, has not been published and "
                "is not under consideration elsewhere. All authors approved the submission. "
                "[TO COMPLETE: competing interests.] [TO COMPLETE: funding.] "
                "[TO COMPLETE: data availability.] [TO COMPLETE: AI-use statement as the "
                "journal requires.]",
        "close": "Thank you for considering our work.",
        "sign": "Sincerely,\n\n[TO COMPLETE: corresponding author, affiliation, email, ORCID]",
        "check_title": "Pre-Submission Checklist (Not Part Of The Letter): JEV",
    },
    "id": {
        "salutation": "Yth. Editor,",
        "re": 'Perihal: Pengajuan naskah {atype}, "{title}"',
        "intro": 'Bersama ini kami mengajukan naskah berjudul "{title}" untuk dipertimbangkan '
                 "terbit di *{journal}* sebagai artikel {atype}.",
        "why": "**Mengapa {journal}.** Ruang lingkup jurnal menyebutkan: “{quote}” "
               "[LENGKAPI: satu kalimat yang menghubungkan ruang lingkup ini dengan pertanyaan review.]",
        "adds": "**Kontribusi review.** [LENGKAPI: celah penelitian dalam dua kalimat.] "
                "[LENGKAPI: temuan utama dan manfaatnya bagi pembaca jurnal.]",
        "how": "**Metode.** Review ini dilaporkan mengikuti {standard}{reg}. "
               "Sumber yang dicari: {sources}; pencarian terakhir: {search_date}.",
        "reg_yes": " dan protokolnya telah diregistrasi ({reg})",
        "reg_todo": " [LENGKAPI: nomor registrasi protokol, atau jelaskan alasan tidak diregistrasi]",
        "decl": "**Pernyataan.** Naskah ini orisinal, belum pernah diterbitkan, dan tidak sedang "
                "diajukan ke jurnal lain. Seluruh penulis telah menyetujui pengajuan ini. "
                "[LENGKAPI: konflik kepentingan.] [LENGKAPI: pendanaan.] "
                "[LENGKAPI: ketersediaan data.] [LENGKAPI: pernyataan penggunaan AI sesuai "
                "kebijakan jurnal.]",
        "close": "Atas perhatian dan pertimbangan Bapak/Ibu, kami ucapkan terima kasih.",
        "sign": "Hormat kami,\n\n[LENGKAPI: penulis korespondensi, afiliasi, email, ORCID]",
        "check_title": "Daftar Periksa Sebelum Submit (Bukan Bagian Surat): JEV",
    },
}


def pick_journal(cands: list[dict], rank: int) -> tuple[dict, list[str]]:
    """Return the chosen candidate (1-based rank) or raise Refused with a JEV suggestion."""
    if not 1 <= rank <= len(cands):
        raise SubmissionError(f"--rank must be between 1 and {len(cands)}")
    chosen = cands[rank - 1]
    blocking = [f for f in chosen.get("flags", []) if f in BLOCKING_FLAGS]
    if blocking:
        clean = [(i, c) for i, c in enumerate(cands, 1)
                 if not any(f in BLOCKING_FLAGS for f in c.get("flags", []))]
        hint = (f"#1 recommended instead: rank {clean[0][0]} {clean[0][1]['journal']} "
                f"(--rank {clean[0][0]})") if clean else "no clean candidate: rebuild the shortlist"
        raise Refused(f"{chosen['journal']} is flagged {', '.join(blocking)}. {hint}.")
    cascade = [c["journal"] for c in cands
               if c is not chosen and not any(f in BLOCKING_FLAGS for f in c.get("flags", []))]
    return chosen, cascade[:2]


def cover_letter(review: dict, cands: list[dict], rank: int = 1, gate_errors: int | None = None,
                 allow_partial: bool = False, lang: str = "en") -> str:
    status = review["gate_status"]
    if status in ("failed", "missing"):
        raise Refused(f"gate is '{status}': finish the review and run check_review.py first.")
    if gate_errors:
        raise Refused(f"the gate report lists {gate_errors} error(s): fix them before submitting.")
    if status == "partial" and not allow_partial:
        raise Refused("gate is 'partial'. #1 recommended: close the missing items. "
                      "#2: submit anyway with --allow-partial-gate and disclose them.")
    journal, cascade = pick_journal(cands, rank)
    t = TEXT[lang]
    todo = "LENGKAPI" if lang == "id" else "TO COMPLETE"
    atype = (review["review_type"] or f"[{todo}: article type]").strip()
    quote = journal.get("scope_quote") or f"[{todo}: quote the aims & scope sentence]"
    if review["registration"]:
        reg = t["reg_yes"].format(reg=review["registration"])
    elif review["genre"] in REGISTRABLE:
        reg = t["reg_todo"]
    else:
        reg = ""
    fmt = dict(atype=atype, title=review["title"], journal=journal["journal"], quote=quote,
               standard=review["standard"] or f"[{todo}: reporting standard]",
               sources=review["sources"] or f"[{todo}: sources]",
               search_date=review["search_date"] or f"[{todo}: search date]", reg=reg)
    letter = [
        date.today().isoformat(), "",
        t["salutation"], "",
        t["re"].format(**fmt), "",
        t["intro"].format(**fmt), "",
        t["why"].format(**fmt), "",
        t["adds"], "",
        t["how"].format(**fmt), "",
        t["decl"], "",
        t["close"], "",
        t["sign"], "",
    ]
    gate_ok = status == "passed" and not gate_errors
    c = CHECKLIST[lang]
    gaps = ", ".join(journal.get("gaps", [])) or c["none"]
    checklist = [
        "---", "",
        f"## {t['check_title']}", "",
        f"**{c['target']} (#{rank}):** {journal['journal']} (tier {journal.get('tier') or 'n/a'}, "
        f"fit {journal.get('fit', 'n/a')}, confidence {journal.get('confidence', 'n/a')}%)  ",
        f"**{c['cascade']}:** " + (" → ".join(cascade) or c["none"]), "",
        f"- [{'x' if gate_ok else ' '}] Gate: {review['gate_line'] or 'missing'}"
        + ("" if gate_errors is None else f" ({c['errors']}: {gate_errors})"),
        f"- [ ] {c['gaps']}: {gaps}",
        f"- [ ] {c['guide']}",
        f"- [ ] {c['replace']} [{todo}: ...]",
        f"- [ ] {c['rerun']}",
        f"- [ ] {c['one']}", "",
    ]
    if status == "partial":
        checklist.insert(8, f"- [ ] {c['partial']}")
    return "\n".join(letter + checklist)


CHECKLIST = {
    "en": {
        "target": "Target", "cascade": "Cascade if rejected (clean candidates only)", "none": "none",
        "errors": "report errors", "gaps": "Unverified journal facts to check before submitting",
        "guide": "Article type, word limit and required checklist from the journal's guide for authors",
        "replace": "Replace every", "one": "Submit to one journal at a time (no simultaneous submissions)",
        "rerun": "Re-run `check_review.py` and `verify_refs.py --online` after the last edit",
        "partial": "**Gate is partial**: disclose the missing items to the editor or close them first",
    },
    "id": {
        "target": "Target", "cascade": "Urutan cadangan bila ditolak (hanya kandidat bersih)",
        "none": "tidak ada", "errors": "error di laporan",
        "gaps": "Fakta jurnal yang belum diverifikasi, cek sebelum submit",
        "guide": "Jenis artikel, batas kata, dan checklist wajib dari pedoman penulis jurnal",
        "replace": "Ganti setiap", "one": "Ajukan ke satu jurnal saja pada satu waktu",
        "rerun": "Jalankan ulang `check_review.py` dan `verify_refs.py --online` setelah suntingan terakhir",
        "partial": "**Gate masih partial**: sampaikan item yang kurang kepada editor, atau lengkapi dulu",
    },
}


# --------------------------------------------------------------------------- #
# Response to reviewers
# --------------------------------------------------------------------------- #

HEADER_RE = re.compile(r"^\s*(?:#+\s*)?(editor|associate editor|academic editor|"
                       r"(?:reviewer|referee)\s*#?\s*(\d+))\b[^\n]*$", re.I)
ITEM_RE = re.compile(r"^\s*(?:(?:comment|point|item)\s*)?(\d+)\s*[.):]\s+(.*)$", re.I)
MAJOR_RE = re.compile(r"\b(major|must|essential|critical|incorrect|error|not reported|missing|"
                      r"overstat\w*|justify|invalid|bias(?:ed)?|unclear method|wrong)\b", re.I)
MINOR_RE = re.compile(r"\b(minor|typo\w*|grammar|spelling|format\w*|wording|language|"
                      r"punctuation|reference style)\b", re.I)
PRIORITY_ORDER = {"major": 0, "moderate": 1, "minor": 2}


def classify(text: str) -> str:
    head = text.strip().lower()
    if head.startswith("minor"):
        return "minor"
    if head.startswith("major") or MAJOR_RE.search(text):
        return "major"
    if MINOR_RE.search(text):
        return "minor"
    return "moderate"


def parse_comments(text: str) -> list[dict]:
    """Split reviewer text into comments: [{who, n, text}] in document order."""
    blocks: list[tuple[str, list[str]]] = []
    who, lines = "Reviewer 1", []
    for line in text.splitlines():
        m = HEADER_RE.match(line)
        if m and len(line.strip()) < 60:
            if any(x.strip() for x in lines):
                blocks.append((who, lines))
            label = m.group(1).strip()
            who = "Editor" if "editor" in label.lower() else f"Reviewer {m.group(2)}"
            lines = []
        else:
            lines.append(line)
    if any(x.strip() for x in lines):
        blocks.append((who, lines))

    comments = []
    for who, body in blocks:
        items: list[str] = []
        cur: list[str] = []
        numbered = any(ITEM_RE.match(line) for line in body)
        for line in body:
            m = ITEM_RE.match(line) if numbered else None
            if m:
                if cur:
                    items.append(" ".join(cur))
                cur = [m.group(2).strip()]
            elif not line.strip():
                if cur and not numbered:
                    items.append(" ".join(cur))
                    cur = []
            else:
                cur.append(line.strip())
        if cur:
            items.append(" ".join(cur))
        for n, item in enumerate((i for i in items if i.strip()), 1):
            comments.append({"who": who, "n": n, "text": item.strip()})
    return comments


def comment_id(c: dict) -> str:
    return (f'E.{c["n"]:d}') if c["who"] == "Editor" else f'R{c["who"].split()[-1]}.{c["n"]:d}'


def response(comments: list[dict], review: dict | None, lang: str = "en") -> str:
    if not comments:
        raise SubmissionError("no reviewer comments found")
    todo = "LENGKAPI" if lang == "id" else "TO COMPLETE"
    for pos, c in enumerate(comments):
        c["priority"] = classify(c["text"])
        c["id"] = comment_id(c)
        c["pos"] = pos
    ranked = sorted(comments, key=lambda c: (PRIORITY_ORDER[c["priority"]], c["pos"]))
    title = review["title"] if review else f"[{todo}: manuscript title]"
    gate = review["gate_line"] if review else "not checked"
    if lang == "id":
        intro = (f"Yth. Editor,\n\nTerima kasih atas kesempatan merevisi naskah \"{title}\". Kami berterima "
                 "kasih kepada para reviewer atas masukan yang membangun. Tanggapan kami untuk setiap "
                 "komentar disajikan di bawah ini, beserta lokasi perubahannya di naskah.")
        h_plan, h_points, h_before = ("Rencana Revisi (JEV, Berurutan Prioritas)",
                                      "Tanggapan Per Poin", "Sebelum Submit Ulang")
        resp, chg = "Tanggapan", "Perubahan di naskah"
        advice = ("Komentar mayor didahulukan karena menentukan keputusan editor. Jawab setiap "
                  "komentar, termasuk yang tidak Anda setujui; bantah dengan bukti, bukan nada.")
    else:
        intro = (f"Dear Editor,\n\nThank you for the opportunity to revise \"{title}\". We thank the "
                 "reviewers for their constructive comments. Our point-by-point responses follow, "
                 "with the location of every change in the manuscript.")
        h_plan, h_points, h_before = ("Revision Plan (JEV, Ranked By Priority)",
                                      "Point-By-Point Responses", "Before Resubmission")
        resp, chg = "Response", "Changes in the manuscript"
        advice = ("Major comments first: they decide the editor's verdict. Answer every comment, "
                  "even when you disagree; disagree with evidence, not tone.")
    out = [f"# Response To Reviewers: {title}", "",
           f"**Gate status of the current draft:** {gate}", "",
           intro, "", f"## {h_plan}", "",
           "| Rank | ID | Priority | Comment (Start) | Status |", "|---:|---|---|---|---|"]
    for rank, c in enumerate(ranked, 1):
        short = c["text"][:90].replace("|", "\\|") + ("..." if len(c["text"]) > 90 else "")
        label = f"**#{rank}**" if rank == 1 else f"#{rank}"
        out.append(f"| {label} | {c['id']} | {c['priority']} | {short} | open |")
    out += ["", advice, "", f"## {h_points}", ""]
    current = None
    for c in comments:
        if c["who"] != current:
            current = c["who"]
            out += [f"### {current}", ""]
        out += [f"**{c['id']} ({c['priority']})**", "", "> " + c["text"], "",
                f"**{resp}:** [{todo}: thank, answer, and give the evidence or reason]  ",
                f"**{chg}:** [{todo}: section / page / line, or 'no change' with the reason]", ""]
    out += [f"## {h_before}", "",
            "- [ ] Every comment has a response and a location (or a reasoned 'no change')",
            "- [ ] Changes are tracked/highlighted in the revised manuscript as the journal asks",
            "- [ ] `check_review.py review.md` passes after the revision",
            "- [ ] `verify_refs.py review.md --online` passes (new references included)",
            "- [ ] The cover letter for the resubmission summarises the major changes", ""]
    return "\n".join(out)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def selftest() -> None:
    review = {"title": "T", "review_type": "systematic review", "genre": "systematic-review",
              "standard": "PRISMA 2020", "sources": "Scopus", "search_date": "2026-01-01",
              "registration": "", "gate_line": "✓ passed (PRISMA 27/27)", "gate_status": "passed"}
    cands = [
        {"journal": "Risky J", "flags": ["LEGITIMACY RISK"], "gaps": [], "scope_quote": "q"},
        {"journal": "Good J", "flags": [], "gaps": ["speed"], "scope_quote": "Reviews of X",
         "tier": "target", "fit": 90.0, "confidence": 75.0},
        {"journal": "Other J", "flags": [], "gaps": [], "scope_quote": "y"},
    ]
    try:
        cover_letter(review, cands, 1)
    except Refused as exc:
        assert "--rank 2" in str(exc), exc
    else:
        raise AssertionError("flagged journal must be refused")
    letter = cover_letter(review, cands, 2)
    assert "*Good J*" in letter and "Reviews of X" in letter and "TO COMPLETE: protocol" in letter
    assert "Risky J" not in letter, "flagged journals never enter the cascade"
    for bad in ({"gate_status": "failed"}, {"gate_status": "partial"}):
        try:
            cover_letter(dict(review, **bad), cands, 2)
        except Refused:
            pass
        else:
            raise AssertionError(f"gate {bad} must be refused")
    assert "Gate is partial" in cover_letter(dict(review, gate_status="partial"), cands, 2,
                                             allow_partial=True)
    try:
        cover_letter(review, cands, 2, gate_errors=2)
    except Refused:
        pass
    else:
        raise AssertionError("gate report errors must be refused")
    assert "Yth. Editor" in cover_letter(review, cands, 2, lang="id")

    text = ("Editor\nPlease address all comments.\n\nReviewer 1\n1. Minor: typo in Table 1.\n"
            "2. The risk of bias is not reported.\ncontinued line.\n\nReviewer #2\n"
            "1) Please clarify the search dates.\n")
    cs = parse_comments(text)
    assert [comment_id(c) for c in cs] == ["E.1", "R1.1", "R1.2", "R2.1"], [comment_id(c) for c in cs]
    assert cs[2]["text"].endswith("continued line.")
    md = response(cs, review)
    assert md.index("| **#1** | R1.2 | major |") > 0, "major comment must rank first"
    assert "Tanggapan Per Poin" in response(parse_comments(text), review, "id")
    print("submission selftest OK (journal pick, flags, gate guards, languages, comment parsing, ranking)")


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        with contextlib.suppress(AttributeError, ValueError):
            stream.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description="Cover letter and response-to-reviewers documents.")
    p.add_argument("--selftest", action="store_true")
    sub = p.add_subparsers(dest="cmd")
    c = sub.add_parser("cover-letter", help="cover letter for the #1 (or --rank N) journal")
    c.add_argument("review", type=Path)
    c.add_argument("--shortlist", type=Path, required=True, help="journal_rank.py --json output")
    c.add_argument("--rank", type=int, default=1, help="journal rank to address (default 1 = #1)")
    c.add_argument("--gate-report", type=Path, help="check_review.py --out report")
    c.add_argument("--allow-partial-gate", action="store_true")
    c.add_argument("--lang", choices=("en", "id"), default="en")
    c.add_argument("--out", type=Path)
    r = sub.add_parser("response", help="point-by-point response skeleton")
    r.add_argument("comments", type=Path, help="reviewer comments as plain text")
    r.add_argument("--review", type=Path, help="review.md (title and gate status)")
    r.add_argument("--lang", choices=("en", "id"), default="en")
    r.add_argument("--out", type=Path)
    a = p.parse_args(argv)
    if a.selftest:
        selftest()
        return 0
    if not a.cmd:
        p.error("choose a subcommand: cover-letter or response (or --selftest)")
    try:
        if a.cmd == "cover-letter":
            text = cover_letter(read_review(a.review), read_shortlist(a.shortlist), a.rank,
                                read_gate_report(a.gate_report), a.allow_partial_gate, a.lang)
        else:
            if not a.comments.is_file():
                raise SubmissionError(f"file not found: {a.comments}")
            review = read_review(a.review) if a.review else None
            text = response(parse_comments(read_text(a.comments)), review, a.lang)
    except Refused as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 1
    except (SubmissionError, json.JSONDecodeError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if a.out:
        a.out.write_text(text, encoding="utf-8")
        print(f"wrote {a.out}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
