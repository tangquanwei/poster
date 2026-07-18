import json

import matplotlib.pyplot as plt

from paper_plot_style import (
    COLORS,
    DATA_PATH,
    DATASETS,
    LINESTYLES,
    MARKERS,
    REGIMES,
    RETRIEVAL_METHODS,
    format_percent_axis,
    local_limits,
    save_pdf,
)


with open(DATA_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)["retrieval"]

ks = [1, 5, 10]
keys = ["r1", "r5", "r10"]
fig, axes = plt.subplots(2, 4, figsize=(7.25, 4.05))

for row, regime in enumerate(REGIMES):
    for col, dataset in enumerate(DATASETS):
        ax = axes[row, col]
        subset = [
            item for item in data
            if item["regime"] == regime and item["dataset"] == dataset
        ]
        vals = []
        for method in RETRIEVAL_METHODS:
            item = next(x for x in subset if x["method"] == method)
            y = [item[key] for key in keys]
            vals.extend(y)
            ax.plot(
                ks,
                y,
                color=COLORS[method],
                marker=MARKERS[method],
                linestyle=LINESTYLES[method],
                label=method,
            )

        lo, hi = local_limits(vals, pad=5.0)
        ax.set_xlim(0.5, 10.5)
        ax.set_ylim(lo, hi)
        ax.set_xticks(ks, ["1", "5", "10"])
        format_percent_axis(ax)

        if row == 1:
            ax.set_xlabel("Retrieved candidates (K)")
        if col == 0:
            ax.set_ylabel("Recall@K (%)")
            ax.text(
                -0.50,
                0.5,
                regime,
                transform=ax.transAxes,
                rotation=90,
                ha="center",
                va="center",
                fontsize=8.5,
                fontweight="bold",
            )
        if row == 0:
            ax.text(
                0.5,
                1.12,
                dataset,
                transform=ax.transAxes,
                ha="center",
                va="bottom",
                fontsize=8.2,
                fontweight="bold",
            )

handles, labels = axes[0, 0].get_legend_handles_labels()
fig.legend(
    handles,
    labels,
    loc="lower center",
    ncol=3,
    frameon=False,
    bbox_to_anchor=(0.54, 0.0),
    handletextpad=0.35,
    columnspacing=1.2,
)
fig.subplots_adjust(left=0.10, right=0.995, bottom=0.15, top=0.88, wspace=0.34, hspace=0.42)
save_pdf(fig, "fig_retrieval_recall_at_k")
