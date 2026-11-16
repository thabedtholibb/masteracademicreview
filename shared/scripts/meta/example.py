"""End-to-end demo of the meta-analysis engine on a synthetic dataset.

Run with:  python shared/scripts/meta/example.py
"""

import os

from effect_sizes import hedges_g
from pooling import random_effects, confidence_interval
from plots import forest_plot, funnel_plot, egger_test

# Synthetic continuous-outcome dataset: treatment vs control means/SDs per study.
# (study, m_treat, sd_treat, n_treat, m_ctrl, sd_ctrl, n_ctrl)
STUDIES = [
    ("Ade 2021", 12.4, 3.1, 40, 10.9, 3.0, 41),
    ("Budi 2022", 9.8, 2.6, 35, 8.9, 2.7, 36),
    ("Citra 2023", 15.1, 4.0, 50, 13.6, 3.8, 48),
    ("Dewi 2024", 7.7, 2.1, 30, 7.1, 2.0, 31),
    ("Eka 2025", 11.2, 3.3, 45, 10.0, 3.4, 44),
]

names, effects, variances = [], [], []
for study, m1, sd1, n1, m2, sd2, n2 in STUDIES:
    g, v = hedges_g(m1, m2, sd1, sd2, n1, n2)
    names.append(study)
    effects.append(g)
    variances.append(v)

out_dir = os.path.join(os.path.dirname(__file__), "out")
os.makedirs(out_dir, exist_ok=True)

re = random_effects(effects, variances)
ci = confidence_interval(re["effect"], re["variance"])
egg = egger_test(effects, variances)

print("Random-effects pooled Hedges' g: %.3f (95%% CI %.3f to %.3f)"
      % (re["effect"], ci[0], ci[1]))
print("tau^2 = %.4f | I^2 = %.1f%% | Q = %.2f (p = %.3f)"
      % (re["tau2"], re["heterogeneity"]["I2"],
         re["heterogeneity"]["Q"], re["heterogeneity"]["p"]))
print("Egger's test: intercept = %.3f (p = %.3f)" % (egg["intercept"], egg["p"]))

forest_plot(names, effects, variances, re["effect"], re["variance"],
            filename=os.path.join(out_dir, "forest.png"))
funnel_plot(effects, variances, re["effect"],
            filename=os.path.join(out_dir, "funnel.png"))
print("wrote %s" % out_dir)
