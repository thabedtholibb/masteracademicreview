# A Concrete Session, End to End

This walks through one real usage so you can see *exactly* what happens. The example uses meta-analysis (the most involved path); the other genres follow the same shape, just with fewer scripts.

**How you start (pick one):** describe what you want in plain words (auto), type `@meta-analysis` / `@brainstorm` (OpenCode), or `/meta-analysis` / `/brainstorm` (Claude Code, after copying `commands/` per [INSTALL.md](INSTALL.md)).

Assumptions: skills installed (see [INSTALL.md](INSTALL.md)), Python deps present, and you have a few studies with extractable data.

---

## Step 0 — You open the harness in your project

```
$ claude        # Claude Code, or `opencode`
```

## Step 1 — You describe what you want

> Saya mau meta-analysis efektivitas CBT untuk insomnia. Saya punya 5 studi RCT.

The agent reads your request, notices "meta-analysis", and **loads the `meta-analysis` skill** (its `description` contains that trigger). From here the skill's instructions take over — the agent stops improvising and follows the protocol.

## Step 2 — The skill checks pre-requisites

```
Agent: Oke — meta-analysis. Sebelum menghitung, saya perlu:
  1. ≥2 studi dengan effect size pada outcome yang sama.
  2. Data tiap studi: n, mean, SD per kelompok (atau tabel 2×2, atau r).
  3. Python (numpy/scipy/matplotlib) — sudah terpasang?
  Kalau <2 studi, pooling tidak mungkin; kita turun ke systematic review.
```

This fail-closed check comes from the skill, not improvisation.

## Step 3 — You provide the data

```
> 5 studi RCT, outcome = keparahan insomnia (makin rendah makin baik), treatment vs control:

>  Study     m_t  sd_t  n_t   m_c  sd_c  n_c
>  Ade2021   12.4  3.1   40  10.9  3.0   41
>  Budi2022   9.8  2.6   35   8.9  2.7   36
>  Citra2023 15.1  4.0   50  13.6  3.8   48
>  Dewi2024   7.7  2.1   30   7.1  2.0   31
>  Eka2025   11.2  3.3   45  10.0  3.4   44
```

## Step 4 — The agent runs the Python engine

The skill tells the agent where the scripts are and what to run. The agent executes them through its shell:

```bash
python - <<'PY'
import sys; sys.path.insert(0, "shared/scripts/meta")
from effect_sizes import hedges_g
from pooling import random_effects, confidence_interval
from plots import forest_plot, funnel_plot, egger_test

studies = [("Ade2021",12.4,3.1,40,10.9,3.0,41),
           ("Budi2022",9.8,2.6,35,8.9,2.7,36),
           ("Citra2023",15.1,4.0,50,13.6,3.8,48),
           ("Dewi2024",7.7,2.1,30,7.1,2.0,31),
           ("Eka2025",11.2,3.3,45,10.0,3.4,44)]
names, eff, var = [], [], []
for s,m1,sd1,n1,m2,sd2,n2 in studies:
    g,v = hedges_g(m1,m2,sd1,sd2,n1,n2)
    names.append(s); eff.append(g); var.append(v)

re = random_effects(eff, var)
ci = confidence_interval(re["effect"], re["variance"])
print("pooled g = %.3f (95%% CI %.3f to %.3f)" % (re["effect"], ci[0], ci[1]))
print("I2 = %.1f%%  Q = %.2f (p=%.3f)  tau2 = %.4f" % (
    re["heterogeneity"]["I2"], re["heterogeneity"]["Q"],
    re["heterogeneity"]["p"], re["tau2"]))
print("Egger:", egger_test(eff, var))
forest_plot(names, eff, var, re["effect"], re["variance"], filename="forest.png")
funnel_plot(eff, var, re["effect"], filename="funnel.png")
PY
```

Output:

```
pooled g = 0.374 (95% CI 0.178 to 0.570)
I2 = 0.0%  Q = 0.40 (p=0.982)  tau2 = 0.0000
Egger: {'intercept': -1.532, 'se': ..., 't': ..., 'p': 0.472}
```

The key point: **the model did not guess these numbers.** The code computed them from your data. That is the whole reason the engine exists.

## Step 5 — The agent writes the report

The skill then drafts a PRISMA/MOOSE-structured write-up in Markdown, embedding the numbers and the two plots, plus a GRADE certainty rating (using I², the CI width, risk of bias, and the Egger result).

## Step 6 — You get the deliverables

```
forest.png        # forest plot (editable)
funnel.png        # funnel plot
effects.csv       # your data + computed effect sizes (auditable)
meta-analysis.md  # the report draft
```

You review, edit, and format for your venue (Word/LaTeX) yourself.

---

## The same shape, lighter genres

| Genre | You provide | Agent does | Scripts? |
|---|---|---|---|
| `brainstorm` | a vague topic | research question + keywords (PICO/PICo/PCC/SPIDER) | none |
| `book-review` | the book + its thesis | summary → critique → verdict | none |
| `narrative-review` | a topic + search terms | thematic synthesis (SANRA) | none |
| `critical-review` | your thesis | argument → contribution | none |
| `systematic-review` | PICO + protocol + screening counts | PRISMA report + `prisma_flow.svg` | `prisma_flow.py` |
| `meta-analysis` | effect-size data | pooling + plots + report | `meta/*.py` |
| `scoping-review` | PCC + a broad question | evidence map + gaps | `prisma_flow.py` |
| `umbrella-review` | existing reviews | AMSTAR-2 + PRIOR synthesis | none |
| `meta-synthesis` | qualitative studies | thematic synthesis (ENTREQ) | none |
| `rapid-review` | deadline + focused question | streamlined SR with declared shortcuts | `prisma_flow.py` (opt.) |
| `integrative-review` | diverse designs | integrated synthesis (Whittemore & Knafl) | none |
| `mapping-review` | a framework + studies | evidence & gap map | `prisma_flow.py` |
| `bibliometric-review` | a bibliographic corpus | citation/co-word map | bundled engine |
| `realist-review` | a programme theory | CMO configurations | none |

## When you don't know which genre

Type "help me write a review". `review-router` interviews you (object, purpose, rigor, data), classifies, and hands off. The rest is the same.
