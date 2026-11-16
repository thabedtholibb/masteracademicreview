"""Meta-analysis statistics engine (masteracademicreview).

Public API re-exported here so callers can do:

    from meta import hedges_g, inverse_variance, random_effects, forest_plot
"""

from .effect_sizes import (
    cohens_d,
    hedges_g,
    log_odds_ratio,
    log_risk_ratio,
    fisher_z,
    fisher_z_variance,
)
from .pooling import (
    inverse_variance,
    random_effects,
    heterogeneity,
    confidence_interval,
    prediction_interval,
    leave_one_out,
    subgroup_analysis,
    meta_regression,
)
from .plots import (
    forest_plot,
    funnel_plot,
    egger_test,
    lfk_index,
    doi_plot,
)

__all__ = [
    "cohens_d",
    "confidence_interval",
    "doi_plot",
    "egger_test",
    "fisher_z",
    "fisher_z_variance",
    "forest_plot",
    "funnel_plot",
    "hedges_g",
    "heterogeneity",
    "inverse_variance",
    "leave_one_out",
    "lfk_index",
    "log_odds_ratio",
    "log_risk_ratio",
    "meta_regression",
    "prediction_interval",
    "random_effects",
    "subgroup_analysis",
]
