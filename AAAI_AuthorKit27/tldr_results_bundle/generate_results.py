"""Generate all main and supplementary result artifacts from tldr_results.json."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


REGIMES = ("ZH+EN", "ZH-only")
DATASETS = ("AISHELL1-NE", "ContextASR-ZH", "ContextASR-EN", "AISpeechMeeting")
RETRIEVERS = ("GLCLAP", "CLAR", "TLDR")
DECODERS = ("Raw", "Oracle hotwords", "+GLCLAP", "+CLAR", "+TLDR")


def _index_unique(rows, fields, label):
    index = {}
    for row in rows:
        key = tuple(row[field] for field in fields)
        if key in index:
            raise ValueError(f"duplicate {label} combination: {key}")
        index[key] = row
    return index


def _validate(data):
    retrieval = _index_unique(data["retrieval"], ("regime", "dataset", "method"), "retrieval")
    decoding = _index_unique(data["decoding"], ("dataset", "method"), "decoding")
    expected_retrieval = {(r, d, m) for r in REGIMES for d in DATASETS for m in RETRIEVERS}
    expected_decoding = {(d, m) for d in DATASETS for m in DECODERS}
    if set(retrieval) != expected_retrieval:
        raise ValueError("retrieval combinations are incomplete or unexpected")
    if set(decoding) != expected_decoding:
        raise ValueError("decoding combinations are incomplete or unexpected")
    for row in data["retrieval"]:
        for metric in ("f1", "precision", "recall", "r1", "r5", "r10"):
            if not 0 <= row[metric] <= 100:
                raise ValueError(f"{metric} outside [0,100]")
    for row in data["decoding"]:
        for metric in ("f1", "precision", "recall"):
            if not 0 <= row[metric] <= 100:
                raise ValueError(f"{metric} outside [0,100]")
        if row["wer"] <= 0:
            raise ValueError("WER must be positive")
    return retrieval, decoding


def build_summary(data):
    retrieval, decoding = _validate(data)
    retrieval_summary = []
    macro_gain = {}
    for regime in REGIMES:
        gains = []
        for dataset in DATASETS:
            baselines = [retrieval[(regime, dataset, method)] for method in RETRIEVERS[:-1]]
            prior = max(baselines, key=lambda row: row["f1"])
            tldr = retrieval[(regime, dataset, "TLDR")]
            gain = tldr["f1"] - prior["f1"]
            gains.append(gain)
            retrieval_summary.append({"regime": regime, "dataset": dataset,
                                      "prior": prior["method"], "prior_f1": prior["f1"],
                                      "tldr_f1": tldr["f1"], "gain": gain})
        macro_gain[regime] = sum(gains) / len(gains)

    decoding_summary = []
    for dataset in DATASETS:
        raw = decoding[(dataset, "Raw")]
        oracle = decoding[(dataset, "Oracle hotwords")]
        priors = [decoding[(dataset, method)] for method in ("+GLCLAP", "+CLAR")]
        prior = min(priors, key=lambda row: row["wer"])
        tldr = decoding[(dataset, "+TLDR")]
        decoding_summary.append({
            "dataset": dataset, "raw_wer": raw["wer"], "prior": prior["method"].lstrip("+"),
            "prior_wer": prior["wer"], "tldr_wer": tldr["wer"], "oracle_wer": oracle["wer"],
            "vs_raw_reduction": 100 * (raw["wer"] - tldr["wer"]) / raw["wer"],
            "vs_prior_reduction": 100 * (prior["wer"] - tldr["wer"]) / prior["wer"],
        })
    return {"retrieval": retrieval_summary, "decoding": decoding_summary,
            "macro_gain": macro_gain, "retrieval_index": retrieval, "decoding_index": decoding}


def _main_table(summary):
    lines = [r"\begin{table*}[!t]", r"\definecolor{resultblue}{HTML}{0072B2}", r"\definecolor{resultorange}{HTML}{D55E00}", r"\centering", r"\caption{Main retrieval and downstream ASR results, averaged over three random seeds. Best prior denotes the stronger of GLCLAP and CLAR. F1 gains are absolute; WER reductions are relative.}",
             r"\label{tab:main_results}", r"\begin{minipage}[t]{0.52\textwidth}", r"\vspace{0pt}", r"\centering",
             r"\colorbox{resultblue!10}{\parbox{\dimexpr\linewidth-2\fboxsep\relax}{\centering\color{resultblue}\textbf{(a) Hotword retrieval F1 (\%)}}}\par\smallskip", r"\resizebox{\linewidth}{!}{%",
             r"\begin{tabular}{llrrrr}", r"\toprule",
             r"Training & Dataset & Strongest prior & Prior F1 & TLDR & $\Delta$F1 \\", r"\midrule"]
    for i, row in enumerate(summary["retrieval"]):
        if i == 4:
            lines.append(r"\midrule")
        tldr = f"\\textcolor{{resultblue}}{{\\textbf{{{row['tldr_f1']:.1f}}}}}" if row["gain"] > 0 else f"{row['tldr_f1']:.1f}"
        prior = f"{row['prior']}" + (f" / \\textbf{{{row['prior_f1']:.1f}}}" if row["gain"] <= 0 else f" / {row['prior_f1']:.1f}")
        regime = row["regime"] if i in (0, 4) else ""
        gain = f"\\textcolor{{resultblue}}{{{row['gain']:+.1f}}}" if row["gain"] > 0 else f"{row['gain']:+.1f}"
        lines.append(f"{regime} & {row['dataset']} & {prior.split(' / ')[0]} & {prior.split(' / ')[1]} & {tldr} & {gain}" + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}", r"}", r"\end{minipage}\hfill",
              r"\begin{minipage}[t]{0.46\textwidth}", r"\vspace{0pt}", r"\centering",
              r"\colorbox{resultorange!10}{\parbox{\dimexpr\linewidth-2\fboxsep\relax}{\centering\color{resultorange}\textbf{(b) Downstream WER}}}\par\smallskip", r"\resizebox{\linewidth}{!}{%",
              r"\begin{tabular}{lrrrrrr}", r"\toprule",
              r"Dataset & Raw & Strongest prior & TLDR & Oracle & vs. Raw & vs. prior \\", r"\midrule"]
    for row in summary["decoding"]:
        lines.append(f"{row['dataset']} & {row['raw_wer']:.2f} & {row['prior']} / {row['prior_wer']:.2f} & \\textcolor{{resultorange}}{{\\textbf{{{row['tldr_wer']:.2f}}}}} & \\textit{{{row['oracle_wer']:.2f}}} & {row['vs_raw_reduction']:.1f}\\% & \\textcolor{{resultorange}}{{{row['vs_prior_reduction']:.1f}\\%}}" + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}", r"}", r"\end{minipage}", r"\end{table*}", ""]
    return "\n".join(lines)


def _supplement(summary):
    ri, di = summary["retrieval_index"], summary["decoding_index"]
    lines = [r"% Complete secondary metrics; include this file in the supplementary material.",
             r"\section{Complete Experimental Results}", r"\begin{table*}[t]", r"\centering",
             r"\caption{Complete retrieval results (\%).}", r"\label{tab:supp_retrieval}", r"\small", r"\setlength{\tabcolsep}{3.5pt}",
             r"\begin{tabular}{lllrrrrrr}", r"\toprule", r"Training & Dataset & Method & F1 & P & R & R@1 & R@5 & R@10 \\", r"\midrule"]
    for regime in REGIMES:
        for dataset in DATASETS:
            for method in RETRIEVERS:
                row = ri[(regime, dataset, method)]
                lines.append(f"{regime} & {dataset} & {method} & " + " & ".join(f"{row[m]:.1f}" for m in ("f1", "precision", "recall", "r1", "r5", "r10")) + r" \\")
        if regime != REGIMES[-1]:
            lines.append(r"\midrule")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table*}", r"\begin{table*}[t]", r"\centering",
              r"\caption{Complete downstream decoding results.}", r"\label{tab:supp_decoding}", r"\small",
              r"\begin{tabular}{llrrrr}", r"\toprule", r"Dataset & Method & F1 & P & R & WER \\", r"\midrule"]
    for dataset in DATASETS:
        for method in DECODERS:
            row = di[(dataset, method)]
            lines.append(f"{dataset} & {method} & {row['f1']:.1f} & {row['precision']:.1f} & {row['recall']:.1f} & {row['wer']:.2f}" + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table*}",
              r"\input{tldr_results_bundle/figure_secondary_metrics}", ""]
    return "\n".join(lines)


def _plot(summary, path):
    matplotlib.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42, "font.size": 8,
                                "axes.titlesize": 9, "axes.labelsize": 8})
    fig, (left, right) = plt.subplots(1, 2, figsize=(7.0, 3.35),
                                     gridspec_kw={"wspace": 0.62, "width_ratios": (1.08, 1)})
    colors = {"ZH+EN": "#0072B2", "ZH-only": "#D55E00"}
    rows = summary["retrieval"]
    y = list(range(len(rows)))[::-1]
    left.axvline(0, color="0.45", lw=0.8)
    for pos, row in zip(y, rows):
        left.plot(row["gain"], pos, "o", color=colors[row["regime"]], ms=5)
        offset = 0.35 if row["gain"] >= 0 else -0.35
        left.text(row["gain"] + offset, pos, f"{row['gain']:+.1f}", va="center",
                  ha="left" if offset > 0 else "right", fontsize=7)
    left.set_yticks(y, [row["dataset"] for row in rows])
    left.set_xlim(-2, 20)
    left.set_xlabel("TLDR $-$ strongest prior (F1 points)")
    left.set_title("(a) Retrieval gain")
    left.text(19.7, 6.55, "ZH+EN", color=colors["ZH+EN"], ha="right", weight="bold")
    left.text(19.7, 2.55, "ZH-only", color=colors["ZH-only"], ha="right", weight="bold")
    left.grid(axis="x", color="0.9", lw=0.6)

    drows = summary["decoding"]
    yd = list(range(len(drows)))[::-1]
    for pos, row in zip(yd, drows):
        right.plot([row["oracle_wer"], row["raw_wer"]], [pos, pos], color="0.82", lw=2, zorder=1)
        right.plot(row["raw_wer"], pos, marker="x", color="0.45", ms=5, linestyle="None", label="Raw" if pos == 3 else None)
        right.plot(row["prior_wer"], pos, marker="s", color="0.35", ms=4, linestyle="None", label="Best prior" if pos == 3 else None)
        right.plot(row["oracle_wer"], pos, marker="|", color="0.6", ms=8, linestyle="None", label="Oracle" if pos == 3 else None)
        right.plot(row["tldr_wer"], pos, marker="o", color="#D55E00", ms=5, linestyle="None", label="TLDR" if pos == 3 else None)
    right.set_yticks(yd, [row["dataset"] for row in drows], fontsize=7)
    right.set_xlim(0, 20)
    right.set_xlabel("WER (lower is better)")
    right.set_title("(b) Downstream ASR")
    right.grid(axis="x", color="0.9", lw=0.6)
    right.legend(frameon=False, ncol=2, loc="upper right", fontsize=6.5,
                 columnspacing=0.7, handletextpad=0.4)
    for ax in (left, right):
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.tick_params(axis="y", length=0)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def generate_all(data_path, output_dir):
    data = json.loads(data_path.read_text(encoding="utf-8"))
    summary = build_summary(data)
    output_dir.mkdir(parents=True, exist_ok=True)
    table = output_dir / "table_main_results.tex"
    supplement = output_dir / "supplementary_results.tex"
    figure = output_dir / "main_results.pdf"
    table.write_text(_main_table(summary), encoding="utf-8")
    supplement.write_text(_supplement(summary), encoding="utf-8")
    _plot(summary, figure)
    return [table, supplement, figure]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path(__file__).with_name("tldr_results.json"))
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parent)
    args = parser.parse_args()
    for path in generate_all(args.data, args.output_dir):
        print(path)


if __name__ == "__main__":
    main()
