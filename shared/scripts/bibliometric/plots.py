"""Visualizations for bibliometric analysis (matplotlib, Agg backend)."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def plot_pubs_per_year(years, filename="pubs_per_year.png", title=""):
    ys = sorted(years)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar([str(y) for y in ys], [years[y] for y in ys], color="0.55")
    ax.set_xlabel("Year")
    ax.set_ylabel("Publications")
    if title:
        ax.set_title(title)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(filename, dpi=150)
    plt.close(fig)
    return filename


def plot_top(items, filename="top.png", xlabel="Documents", title="", n=10):
    """Horizontal bar of a ranked list [(label, count), ...]."""
    items = items[:n][::-1]
    labels = [x[0] for x in items]
    counts = [x[1] for x in items]
    fig, ax = plt.subplots(figsize=(8, max(2.5, 0.45 * len(labels) + 1)))
    ax.barh(labels, counts, color="0.55")
    ax.set_xlabel(xlabel)
    if title:
        ax.set_title(title)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(filename, dpi=150)
    plt.close(fig)
    return filename


def plot_heatmap(labels, matrix, filename="cooccurrence.png", title="", cmap="viridis"):
    """Heatmap of a symmetric co-occurrence matrix."""
    n = len(labels)
    fig, ax = plt.subplots(figsize=(max(6, 0.45 * n + 2), max(5, 0.45 * n + 1)))
    im = ax.imshow(matrix, cmap=cmap, aspect="auto")
    ax.set_xticks(range(n))
    ax.set_xticklabels(labels, rotation=90, fontsize=7)
    ax.set_yticks(range(n))
    ax.set_yticklabels(labels, fontsize=7)
    fig.colorbar(im, ax=ax, label="Co-occurrence")
    if title:
        ax.set_title(title)
    fig.tight_layout()
    fig.savefig(filename, dpi=150)
    plt.close(fig)
    return filename
