# Reference LFK values from R metasens::lfkindex (Rücker & Schwarzer) for the
# datasets in tests/fixtures/lfk_crosscheck.csv. CI compares them with the
# Python implementation (tests/lfk_crosscheck.py). The first dataset is the
# worked example of Furuya-Kanamori et al. (2018), as used in metasens.
library(metasens)
d <- read.csv("tests/fixtures/lfk_crosscheck.csv", stringsAsFactors = FALSE)
groups <- split(d, factor(d$dataset, levels = unique(d$dataset)))
out <- do.call(rbind, lapply(groups, function(x)
  data.frame(dataset = x$dataset[1], lfk = lfkindex(x$te, sqrt(x$var))$lfkindex)))
write.csv(out, "r_lfk.csv", row.names = FALSE)
print(out, digits = 12)
