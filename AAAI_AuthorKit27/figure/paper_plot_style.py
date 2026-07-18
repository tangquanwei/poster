from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "figure"
DATA_PATH = ROOT / "tldr_results_bundle" / "tldr_results.json"

DATASETS = ["AISHELL1-NE", "ContextASR-ZH", "ContextASR-EN", "AISpeechMeeting"]
REGIMES = ["ZH+EN", "ZH-only"]
RETRIEVAL_METHODS = ["GLCLAP", "CLAR", "TLDR"]
DECODING_METHODS = ["Raw", "Oracle hotwords", "+GLCLAP", "+CLAR", "+TLDR"]

COLORS = {
    "Raw": "#000000",
    "Oracle hotwords": "#7A7A7A",
    "GLCLAP": "#D55E00",
    "CLAR": "#0072B2",
    "TLDR": "#009E73",
    "+GLCLAP": "#D55E00",
    "+CLAR": "#0072B2",
    "+TLDR": "#009E73",
}

MARKERS = {
    "Raw": "x",
    "Oracle hotwords": "P",
    "GLCLAP": "o",
    "CLAR": "s",
    "TLDR": "D",
    "+GLCLAP": "o",
    "+CLAR": "s",
    "+TLDR": "D",
}

LINESTYLES = {
    "GLCLAP": (0, (1.0, 1.2)),
    "CLAR": (0, (4.0, 1.7)),
    "TLDR": "solid",
}

mpl.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
    "font.size": 8.5,
    "axes.labelsize": 8.5,
    "xtick.labelsize": 7.5,
    "ytick.labelsize": 7.5,
    "legend.fontsize": 7.5,
    "axes.linewidth": 0.75,
    "lines.linewidth": 1.25,
    "lines.markersize": 4.2,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.03,
})


def save_pdf(fig, name):
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    path = FIG_DIR / f"{name}.pdf"
    fig.savefig(path)
    print(f"Saved {path}")


def format_percent_axis(ax):
    ax.tick_params(direction="out", length=2.5, width=0.7, pad=1.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="#E8E8E8", linewidth=0.45)


def local_limits(values, floor=0.0, ceil=100.0, pad=4.0):
    lo = max(floor, min(values) - pad)
    hi = min(ceil, max(values) + pad)
    if hi - lo < 8:
        mid = (hi + lo) / 2.0
        lo = max(floor, mid - 4)
        hi = min(ceil, mid + 4)
    return lo, hi
