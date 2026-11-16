"""End-to-end demo of the bibliometric engine on a synthetic corpus.

Run with:  python shared/scripts/bibliometric/example.py
"""

import os

from parsers import load_csv
from performance import summary, publications_per_year, top_authors, top_journals, top_keywords
from mapping import co_occurrence
from plots import plot_pubs_per_year, plot_top, plot_heatmap

# Build a small synthetic corpus (fields: title, authors, year, journal, keywords, citations)
CSV = os.path.join(os.path.dirname(__file__), "sample.csv")
with open(CSV, "w", encoding="utf-8") as f:
    f.write("title,authors,year,journal,keywords,citations\n")
    rows = [
        ("Diffusion models for images", "Andi; Budi", 2020, "NeurIPS", "diffusion; generative; images", 120),
        ("GANs for low-dim data", "Budi; Citra", 2021, "ICML", "gan; generative; low-dim", 45),
        ("Diffusion for audio", "Andi; Citra", 2021, "ICASSP", "diffusion; generative; audio", 30),
        ("Score-based generative models", "Andi", 2022, "Nature MI", "diffusion; score-based; generative", 200),
        ("GAN stability", "Budi; Dewi", 2022, "ICLR", "gan; stability; training", 15),
        ("Audio diffusion survey", "Citra; Dewi", 2023, "IEEE TASLP", "diffusion; audio; survey", 10),
    ]
    for r in rows:
        f.write(",".join(str(x) for x in r) + "\n")

out_dir = os.path.join(os.path.dirname(__file__), "out")
os.makedirs(out_dir, exist_ok=True)

records = load_csv(CSV)
s = summary(records)

print("Records:", s["n_records"], "| Years:", s["year_range"],
      "| Authors:", s["n_authors"], "| Journals:", s["n_journals"])
print("Total citations:", s["total_citations"], "| corpus h-index:", s["h_index_corpus"])
print("Top authors:", s["top_authors"])
print("Top journals:", s["top_journals"])
print("Top keywords:", s["top_keywords"])

labels, m = co_occurrence(records, field="keywords", top_n=6)
print("Co-occurrence matrix over:", labels)

plot_pubs_per_year(publications_per_year(records),
                   filename=os.path.join(out_dir, "pubs_per_year.png"))
plot_top(top_authors(records, 10), filename=os.path.join(out_dir, "top_authors.png"),
         xlabel="Papers", title="Top authors")
plot_top(top_journals(records, 10), filename=os.path.join(out_dir, "top_journals.png"),
         xlabel="Papers", title="Top journals")
plot_heatmap(labels, m, filename=os.path.join(out_dir, "cooccurrence.png"),
             title="Keyword co-occurrence")
print("wrote %s" % out_dir)
