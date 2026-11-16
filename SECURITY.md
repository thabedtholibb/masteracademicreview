# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| 0.1.x | yes |
| < 0.1 | no |

## What The Tools Do With Your Data

- Every tool runs **locally** and reads the files you pass it (CSV, RIS,
  BibTeX, Markdown, JSON). Nothing is uploaded, and there is no telemetry.
- The only network access is `verify_refs.py --online`, which sends the DOI
  or the title and year of each reference to `api.crossref.org`. Do not run it
  on references you are not allowed to disclose. `--mailto` is optional and is
  sent only if you pass it.
- No tool needs or stores credentials. The PyPI publish workflow uses trusted
  publishing; no token is kept in the repository.

## Reporting A Vulnerability

Please **do not** open a public issue for a security problem. Use GitHub's
private reporting instead: **Security → Report a vulnerability** on the
repository page. Include the tool, the version (`mar --version`), a minimal
input that reproduces the problem, and what you expected.

You can expect an acknowledgement within 7 days and a fix or a decision within
30 days for confirmed issues. Credit is given in the changelog unless you ask
otherwise.

## In Scope

- A crafted input file (CSV, RIS, BibTeX, Markdown, JSON) that makes a tool
  write outside the output directory, execute code, or hang indefinitely.
- Leaking data to any host other than `api.crossref.org` (online reference check).
- Problems in the GitHub workflows of this repository.

## Out Of Scope

- Wrong scientific output on valid input: please open a normal bug report
  with a reproducible example; those matter just as much, but they are not
  security issues.
- Vulnerabilities in third-party packages (numpy, scipy, matplotlib,
  python-docx, reportlab, Pandoc); report those upstream.
