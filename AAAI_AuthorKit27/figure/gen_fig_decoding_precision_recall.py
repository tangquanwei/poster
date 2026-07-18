import json

import matplotlib.pyplot as plt

from paper_plot_style import (
    COLORS,
    DATA_PATH,
    DATASETS,
    DECODING_METHODS,
    MARKERS,
    format_percent_axis,
    local_limits,
    save_pdf,
)


with open(DATA_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)["decoding"]

fig, axes = plt.subplots(1, 4, figsize=(7.25, 2.25))

for col, dataset in enumerate(DATASETS):
    ax = axes[col]
    subset = [item for item in data if item["dataset"] == dataset]
    vals = []
    for method in DECODING_METHODS:
        item = next(x for x in subset if x["method"] == method)
        vals.extend([item["precision"], item["recall"]])
        scatter_kwargs = {
            "s": 28,
            "color": COLORS[method],
            "marker": MARKERS[method],
            "zorder": 3,
            "label": method,
        }
        if MARKERS[method] != "x":
            scatter_kwargs.update({"edgecolor": "white", "linewidth": 0.45})
        ax.scatter(item["precision"], item["recall"], **scatter_kwargs)

    lo, hi = local_limits(vals, pad=5.0)
    ax.plot([lo, hi], [lo, hi], color="#BDBDBD", linewidth=0.65, zorder=1)
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_xlabel("Precision (%)")
    if col == 0:
        ax.set_ylabel("Recall (%)")
    format_percent_axis(ax)
    ax.text(
        0.5,
        1.10,
        dataset,
        transform=ax.transAxes,
        ha="center",
        va="bottom",
        fontsize=8.2,
        fontweight="bold",
    )

handles, labels = axes[0].get_legend_handles_labels()
fig.legend(
    handles,
    labels,
    loc="lower center",
    ncol=5,
    frameon=False,
    bbox_to_anchor=(0.53, -0.02),
    handletextpad=0.25,
    columnspacing=0.9,
)
fig.subplots_adjust(left=0.075, right=0.995, bottom=0.28, top=0.83, wspace=0.35)
save_pdf(fig, "fig_decoding_precision_recall")
