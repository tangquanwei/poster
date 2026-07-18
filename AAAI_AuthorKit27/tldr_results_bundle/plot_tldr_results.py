from __future__ import annotations

import argparse
import math
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET

try:
    import matplotlib.pyplot as plt
    from matplotlib import colors as mcolors
    from matplotlib.ticker import MultipleLocator
except ModuleNotFoundError as exc:  # pragma: no cover - user environment guard
    raise SystemExit(
        "Missing plotting dependency. Install matplotlib, for example:\n"
        "  python -m pip install matplotlib\n"
        "or run with uv:\n"
        "  uv run --with matplotlib plot_tldr_results.py"
    ) from exc


DATASETS = ["AISHELL1-NE", "ContextASR-ZH", "ContextASR-EN", "AISpeech-Meeting"]
DATASET_LABELS = {
    "AISHELL1-NE": "AISHELL1-NE",
    "ContextASR-ZH": "ContextASR-ZH",
    "ContextASR-EN": "ContextASR-EN",
    "AISpeech-Meeting": "Meeting",
}
DATASET_SHORT = {
    "AISHELL1-NE": "AISHELL",
    "ContextASR-ZH": "Ctx-ZH",
    "ContextASR-EN": "Ctx-EN",
    "AISpeech-Meeting": "Meeting",
}
TRAINING_REGIMES = ["ZH+EN", "ZH only"]
MODELS = ["GLCLAP", "CLAR", "TLDR"]
BASELINE_MODELS = ["GLCLAP", "CLAR"]
METRIC_COLUMNS = ["F1", "Precision", "Recall", "R@1", "R@5", "R@10"]

METHOD_COLORS = {
    "GLCLAP": "#0072B2",
    "CLAR": "#E69F00",
    "TLDR": "#009E73",
}
TRAINING_COLORS = {
    "ZH+EN": "#0072B2",
    "ZH only": "#D55E00",
}
TRAINING_MARKERS = {
    "ZH+EN": "o",
    "ZH only": "s",
}

NS = {
    "m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}


def configure_matplotlib() -> None:
    """Publication-oriented defaults for compact AAAI two-column figures."""
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
            "mathtext.fontset": "stix",
            "font.size": 8.5,
            "axes.labelsize": 8.5,
            "xtick.labelsize": 7.5,
            "ytick.labelsize": 7.5,
            "legend.fontsize": 7.5,
            "figure.dpi": 180,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.035,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "axes.linewidth": 0.75,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": False,
            "grid.linewidth": 0.45,
            "grid.alpha": 0.28,
            "lines.linewidth": 1.45,
            "lines.markersize": 4.2,
            "patch.linewidth": 0.5,
            "legend.frameon": False,
        }
    )


def _column_index(cell_ref: str) -> int:
    letters = "".join(ch for ch in cell_ref if ch.isalpha())
    value = 0
    for char in letters:
        value = value * 26 + ord(char.upper()) - ord("A") + 1
    return value - 1


def _sheet_path_from_name(zf: ZipFile, sheet_name: str) -> str:
    workbook = ET.fromstring(zf.read("xl/workbook.xml"))
    rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
    rel_targets = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels}

    for sheet in workbook.findall("m:sheets/m:sheet", NS):
        if sheet.attrib["name"] == sheet_name:
            rel_id = sheet.attrib[f"{{{NS['r']}}}id"]
            target = rel_targets[rel_id].replace("\\", "/").lstrip("/")
            return target if target.startswith("xl/") else f"xl/{target}"

    names = [sheet.attrib["name"] for sheet in workbook.findall("m:sheets/m:sheet", NS)]
    raise ValueError(f"Sheet {sheet_name!r} not found. Available sheets: {names}")


def _read_shared_strings(zf: ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in zf.namelist():
        return []
    root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
    strings = []
    for item in root.findall("m:si", NS):
        strings.append("".join(text.text or "" for text in item.findall(".//m:t", NS)))
    return strings


def _coerce_number(value: str) -> float | int | str:
    try:
        number = float(value)
    except ValueError:
        return value
    return int(number) if number.is_integer() else number


def read_xlsx_sheet(path: Path, sheet_name: str) -> list[list[object]]:
    """Read a simple worksheet using only the Python standard library."""
    with ZipFile(path) as zf:
        shared_strings = _read_shared_strings(zf)
        sheet_path = _sheet_path_from_name(zf, sheet_name)
        root = ET.fromstring(zf.read(sheet_path))

        rows: list[list[object]] = []
        for xml_row in root.findall("m:sheetData/m:row", NS):
            row: list[object] = []
            for cell in xml_row.findall("m:c", NS):
                cell_ref = cell.attrib.get("r", "A1")
                col_idx = _column_index(cell_ref)
                while len(row) < col_idx:
                    row.append("")

                cell_type = cell.attrib.get("t")
                value_node = cell.find("m:v", NS)
                if cell_type == "s" and value_node is not None:
                    value: object = shared_strings[int(value_node.text or 0)]
                elif cell_type == "inlineStr":
                    value = "".join(text.text or "" for text in cell.findall(".//m:t", NS))
                elif value_node is not None:
                    value = _coerce_number(value_node.text or "")
                else:
                    value = ""

                row.append(value)
            rows.append(row)

    return rows


def load_results(excel_path: Path) -> list[dict[str, object]]:
    rows = read_xlsx_sheet(excel_path, "Results_Long")
    if not rows:
        raise ValueError("Results_Long is empty.")

    headers = [str(cell).strip() for cell in rows[0]]
    required = {"Training Regime", "Model", "Dataset", *METRIC_COLUMNS}
    missing = required.difference(headers)
    if missing:
        raise ValueError(f"Missing columns in Results_Long: {sorted(missing)}")

    records: list[dict[str, object]] = []
    for raw in rows[1:]:
        if not any(cell not in ("", None) for cell in raw):
            continue
        padded = list(raw) + [""] * (len(headers) - len(raw))
        record = dict(zip(headers, padded))
        if record.get("Model") not in MODELS:
            continue
        for metric in METRIC_COLUMNS:
            record[metric] = float(record[metric])
        records.append(record)

    expected = len(TRAINING_REGIMES) * len(DATASETS) * len(MODELS)
    if len(records) != expected:
        raise ValueError(f"Expected {expected} result rows, found {len(records)}.")

    return records


def make_index(records: list[dict[str, object]]) -> dict[tuple[str, str, str], dict[str, object]]:
    return {
        (str(row["Training Regime"]), str(row["Dataset"]), str(row["Model"])): row
        for row in records
    }


def value_at(
    index: dict[tuple[str, str, str], dict[str, object]],
    training: str,
    dataset: str,
    model: str,
    metric: str,
) -> float:
    return float(index[(training, dataset, model)][metric])


def best_baseline_f1(
    index: dict[tuple[str, str, str], dict[str, object]], training: str, dataset: str
) -> tuple[str, float]:
    scored = [
        (model, value_at(index, training, dataset, model, "F1"))
        for model in BASELINE_MODELS
    ]
    return max(scored, key=lambda item: item[1])


def macro_f1(index: dict[tuple[str, str, str], dict[str, object]], training: str, model: str) -> float:
    return sum(value_at(index, training, dataset, model, "F1") for dataset in DATASETS) / len(DATASETS)


def tldr_gain_rows(records: list[dict[str, object]]) -> list[dict[str, object]]:
    index = make_index(records)
    gains: list[dict[str, object]] = []
    for training in TRAINING_REGIMES:
        for dataset in DATASETS:
            best_model, baseline = best_baseline_f1(index, training, dataset)
            tldr = value_at(index, training, dataset, "TLDR", "F1")
            gains.append(
                {
                    "Training Regime": training,
                    "Dataset": dataset,
                    "Best Baseline": best_model,
                    "Best Baseline F1": baseline,
                    "TLDR F1": tldr,
                    "F1 Gain": tldr - baseline,
                }
            )

        baseline_macro = max(macro_f1(index, training, model) for model in BASELINE_MODELS)
        tldr_macro = macro_f1(index, training, "TLDR")
        gains.append(
            {
                "Training Regime": training,
                "Dataset": "Macro",
                "Best Baseline": "Macro best",
                "Best Baseline F1": baseline_macro,
                "TLDR F1": tldr_macro,
                "F1 Gain": tldr_macro - baseline_macro,
            }
        )
    return gains


def save_figure(fig, output_dir: Path, stem: str, formats: list[str]) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for fmt in formats:
        path = output_dir / f"{stem}.{fmt}"
        fig.savefig(path, format=fmt)
        paths.append(path)
    plt.close(fig)
    return paths


def format_signed(value: float) -> str:
    if abs(value) < 0.05:
        value = 0.0
    adjusted = value + (1e-9 if value >= 0 else -1e-9)
    rounded = Decimal(str(adjusted)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    if rounded == Decimal("-0.0"):
        rounded = Decimal("0.0")
    return f"{rounded:+.1f}"


def plot_gain_heatmap(records: list[dict[str, object]], output_dir: Path, formats: list[str]) -> list[Path]:
    gains = tldr_gain_rows(records)
    columns = DATASETS + ["Macro"]
    matrix = []
    for training in TRAINING_REGIMES:
        row = []
        for dataset in columns:
            match = next(
                item for item in gains
                if item["Training Regime"] == training and item["Dataset"] == dataset
            )
            row.append(float(match["F1 Gain"]))
        matrix.append(row)

    max_abs = max(abs(value) for row in matrix for value in row)
    norm = mcolors.TwoSlopeNorm(vmin=-max(2.0, max_abs), vcenter=0.0, vmax=max(2.0, max_abs))

    fig, ax = plt.subplots(figsize=(7.05, 1.95))
    image = ax.imshow(matrix, cmap="RdBu_r", norm=norm, aspect="auto")

    ax.set_yticks(range(len(TRAINING_REGIMES)), TRAINING_REGIMES)
    ax.set_xticks(
        range(len(columns)),
        ["AISHELL1-NE", "Context-ZH", "Context-EN", "Meeting", "Macro"],
    )
    ax.tick_params(length=0)
    ax.set_xticks([i - 0.5 for i in range(1, len(columns))], minor=True)
    ax.set_yticks([0.5], minor=True)
    ax.grid(which="minor", color="white", linewidth=1.0)
    ax.tick_params(which="minor", bottom=False, left=False)

    for row_idx, row in enumerate(matrix):
        for col_idx, value in enumerate(row):
            weight = "bold" if abs(value) >= 6.0 or columns[col_idx] == "Macro" else "normal"
            ax.text(
                col_idx,
                row_idx,
                format_signed(value),
                ha="center",
                va="center",
                fontsize=8,
                fontweight=weight,
                color="black",
            )

    cbar = fig.colorbar(image, ax=ax, fraction=0.035, pad=0.018)
    cbar.set_label("F1 gain", labelpad=2)
    cbar.ax.tick_params(length=2, width=0.6)
    fig.tight_layout(pad=0.2)
    return save_figure(fig, output_dir, "fig1_tldr_gain_heatmap", formats)


def plot_difficulty_gain(records: list[dict[str, object]], output_dir: Path, formats: list[str]) -> list[Path]:
    gains = [row for row in tldr_gain_rows(records) if row["Dataset"] != "Macro"]
    xs = [float(row["Best Baseline F1"]) for row in gains]
    ys = [float(row["F1 Gain"]) for row in gains]
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    denom = sum((x - mean_x) ** 2 for x in xs)
    slope = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)) / denom
    intercept = mean_y - slope * mean_x
    x_line = [min(xs) - 3.0, max(xs) + 3.0]
    y_line = [slope * x + intercept for x in x_line]

    fig, ax = plt.subplots(figsize=(3.35, 2.45))
    ax.plot(x_line, y_line, color="#666666", linestyle="--", linewidth=0.85, label="Trend")
    ax.axhline(0, color="#333333", linewidth=0.65)

    offsets = {
        ("ZH+EN", "ContextASR-ZH"): (5, 6),
        ("ZH+EN", "ContextASR-EN"): (5, 6),
        ("ZH+EN", "AISpeech-Meeting"): (5, -12),
        ("ZH only", "ContextASR-ZH"): (5, 6),
        ("ZH only", "ContextASR-EN"): (6, 2),
        ("ZH only", "AISpeech-Meeting"): (5, 6),
    }

    for training in TRAINING_REGIMES:
        training_rows = [row for row in gains if row["Training Regime"] == training]
        ax.scatter(
            [float(row["Best Baseline F1"]) for row in training_rows],
            [float(row["F1 Gain"]) for row in training_rows],
            color=TRAINING_COLORS[training],
            marker=TRAINING_MARKERS[training],
            s=28,
            edgecolor="white",
            linewidth=0.5,
            label=training,
            zorder=3,
        )
        for row in training_rows:
            dataset = str(row["Dataset"])
            if dataset == "AISHELL1-NE":
                continue
            dx, dy = offsets[(training, dataset)]
            ax.annotate(
                DATASET_SHORT[dataset],
                (float(row["Best Baseline F1"]), float(row["F1 Gain"])),
                xytext=(dx, dy),
                textcoords="offset points",
                fontsize=6.5,
            )

    ax.set_xlabel("Best baseline F1 (%)")
    ax.set_ylabel("TLDR F1 gain")
    ax.set_xlim(0, 102)
    ax.set_ylim(-2.0, 18.5)
    ax.yaxis.set_major_locator(MultipleLocator(5))
    ax.grid(axis="y")
    ax.legend(loc="upper right", handletextpad=0.4, borderaxespad=0.2)
    fig.tight_layout(pad=0.15)
    return save_figure(fig, output_dir, "fig2_difficulty_vs_gain", formats)


def _spread_label_positions(values: list[float], min_gap: float = 5.0) -> list[float]:
    ordered = sorted(enumerate(values), key=lambda item: item[1])
    adjusted = [0.0] * len(values)
    last = -math.inf
    for idx, value in ordered:
        adjusted_value = max(value, last + min_gap)
        adjusted[idx] = adjusted_value
        last = adjusted_value
    overflow = max(adjusted) - 100.0
    if overflow > 0:
        adjusted = [value - overflow for value in adjusted]
    return adjusted


def plot_training_degradation(
    records: list[dict[str, object]], output_dir: Path, formats: list[str]
) -> list[Path]:
    index = make_index(records)
    selected = ["ContextASR-ZH", "AISpeech-Meeting"]
    fig, axes = plt.subplots(1, 2, figsize=(7.05, 2.45), sharey=True)

    for panel_idx, (ax, dataset) in enumerate(zip(axes, selected)):
        right_values = []
        label_texts = []
        label_colors = []
        for model in MODELS:
            values = [value_at(index, training, dataset, model, "F1") for training in TRAINING_REGIMES]
            drop = values[1] - values[0]
            ax.plot(
                [0, 1],
                values,
                marker="o",
                color=METHOD_COLORS[model],
                label=model if panel_idx == 0 else None,
            )
            right_values.append(values[1])
            label_texts.append(f"{model} ({drop:+.1f})")
            label_colors.append(METHOD_COLORS[model])

        label_positions = _spread_label_positions(right_values, min_gap=5.5)
        for original_y, label_y, text, color in zip(
            right_values, label_positions, label_texts, label_colors
        ):
            ax.annotate(
                text,
                xy=(1.0, original_y),
                xytext=(1.08, label_y),
                textcoords="data",
                color=color,
                fontsize=7,
                va="center",
                arrowprops=None if abs(label_y - original_y) < 0.1 else {
                    "arrowstyle": "-",
                    "color": color,
                    "lw": 0.5,
                    "shrinkA": 0,
                    "shrinkB": 2,
                },
            )

        ax.text(
            0.03,
            0.08,
            f"({chr(ord('a') + panel_idx)}) {DATASET_LABELS[dataset]}",
            transform=ax.transAxes,
            ha="left",
            va="bottom",
            fontsize=8,
            fontweight="bold",
        )
        ax.set_xlim(-0.08, 1.62)
        ax.set_ylim(35, 101)
        ax.set_xticks([0, 1], TRAINING_REGIMES)
        ax.grid(axis="y")
        if panel_idx == 0:
            ax.set_ylabel("F1 (%)")

    axes[0].legend(loc="lower left", bbox_to_anchor=(0.0, 1.02), ncol=3)
    fig.tight_layout(w_pad=1.0, pad=0.15)
    return save_figure(fig, output_dir, "fig3_restricted_training_degradation", formats)


def plot_zero_shot_ranking(
    records: list[dict[str, object]], output_dir: Path, formats: list[str]
) -> list[Path]:
    index = make_index(records)
    ks = [1, 5, 10]
    metrics = ["R@1", "R@5", "R@10"]

    fig, ax = plt.subplots(figsize=(3.35, 2.38))
    for model in MODELS:
        values = [
            value_at(index, "ZH only", "ContextASR-EN", model, metric)
            for metric in metrics
        ]
        ax.plot(ks, values, marker="o", color=METHOD_COLORS[model])
        ax.annotate(
            f"{model} {values[-1]:.1f}",
            (ks[-1], values[-1]),
            xytext=(5, 0),
            textcoords="offset points",
            va="center",
            fontsize=7,
            color=METHOD_COLORS[model],
        )

    ax.set_xlabel("K")
    ax.set_ylabel("Recall@K (%)")
    ax.set_xticks(ks)
    ax.set_xlim(0.6, 12.4)
    ax.set_ylim(0, 60)
    ax.yaxis.set_major_locator(MultipleLocator(10))
    ax.grid(axis="y")
    fig.tight_layout(pad=0.15)
    return save_figure(fig, output_dir, "fig4_zh_only_contextasr_en_ranking", formats)


def plot_detection_f1_overview(
    records: list[dict[str, object]], output_dir: Path, formats: list[str]
) -> list[Path]:
    index = make_index(records)
    fig, axes = plt.subplots(1, 2, figsize=(7.05, 2.55), sharey=True)
    x = list(range(len(DATASETS)))
    width = 0.23

    for panel_idx, (ax, training) in enumerate(zip(axes, TRAINING_REGIMES)):
        for model_idx, model in enumerate(MODELS):
            positions = [pos + (model_idx - 1) * width for pos in x]
            values = [value_at(index, training, dataset, model, "F1") for dataset in DATASETS]
            bars = ax.bar(
                positions,
                values,
                width=width,
                color=METHOD_COLORS[model],
                label=model if panel_idx == 0 else None,
            )
            if model == "TLDR":
                for bar, value in zip(bars, values):
                    ax.text(
                        bar.get_x() + bar.get_width() / 2,
                        value + 1.0,
                        f"{value:.1f}",
                        ha="center",
                        va="bottom",
                        fontsize=6.5,
                        color=METHOD_COLORS[model],
                    )

        ax.set_title(
            f"({chr(ord('a') + panel_idx)}) {training}",
            loc="left",
            fontsize=8,
            fontweight="bold",
            pad=2,
        )
        ax.set_xticks(x, [DATASET_LABELS[dataset] for dataset in DATASETS], rotation=18, ha="right")
        ax.set_ylim(0, 112)
        ax.yaxis.set_major_locator(MultipleLocator(20))
        ax.grid(axis="y")
        if panel_idx == 0:
            ax.set_ylabel("F1 (%)")

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 1.0), ncol=3)
    fig.tight_layout(rect=(0, 0, 1, 0.88), w_pad=0.8, pad=0.15)
    return save_figure(fig, output_dir, "figS1_detection_f1_overview", formats)


def write_gain_table(records: list[dict[str, object]], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    gains = tldr_gain_rows(records)
    columns = DATASETS + ["Macro"]
    path = output_dir / "table_tldr_f1_gain.tex"

    lines = [
        r"\begin{table}[t]",
        r"\centering",
        r"\small",
        r"\setlength{\tabcolsep}{4pt}",
        r"\caption{Absolute F1 gain of TLDR over the strongest baseline. Macro is the unweighted average across datasets.}",
        r"\label{tab:tldr-f1-gain}",
        r"\begin{tabular}{lrrrrr}",
        r"\toprule",
        r"Training & AISHELL1-NE & Context-ZH & Context-EN & Meeting & Macro \\",
        r"\midrule",
    ]
    for training in TRAINING_REGIMES:
        row_values = []
        for dataset in columns:
            gain = next(
                item for item in gains
                if item["Training Regime"] == training and item["Dataset"] == dataset
            )
            value = float(gain["F1 Gain"])
            text = format_signed(value)
            if abs(value) >= 6.0 or dataset == "Macro":
                text = rf"\textbf{{{text}}}"
            row_values.append(text)
        lines.append(f"{training} & " + " & ".join(row_values) + r" \\")
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table}", ""])
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_latex_includes(output_dir: Path, primary_format: str) -> Path:
    path = output_dir / "latex_includes.tex"
    entries = [
        (
            "fig1_tldr_gain_heatmap",
            r"\textwidth",
            "Summary of TLDR's absolute F1 gain over the strongest baseline. The gain is small on saturated in-domain settings and grows under restricted or difficult conditions.",
            "fig:tldr-gain-heatmap",
        ),
        (
            "fig2_difficulty_vs_gain",
            r"0.48\textwidth",
            "Relationship between baseline difficulty and TLDR improvement. Each point is one training regime and test dataset; the dashed line is a least-squares guide.",
            "fig:difficulty-gain",
        ),
        (
            "fig3_restricted_training_degradation",
            r"\textwidth",
            "F1 degradation from bilingual training to Chinese-only training on two cross-domain Chinese test sets. Values in parentheses denote the absolute change in F1.",
            "fig:restricted-training",
        ),
        (
            "fig4_zh_only_contextasr_en_ranking",
            r"0.48\textwidth",
            "Zero-shot English candidate ranking under Chinese-only training. TLDR improves Recall@K substantially, while absolute detection performance remains limited.",
            "fig:zh-only-en-ranking",
        ),
        (
            "figS1_detection_f1_overview",
            r"\textwidth",
            "Complete F1 overview across datasets, training regimes, and models. TLDR bar values are annotated for readability.",
            "fig:f1-overview",
        ),
    ]

    lines = [
        "% Generated by plot_tldr_results.py.",
        "% Copy the snippets you need into the paper. Captions are intentionally outside the figures.",
        "",
    ]
    for stem, width, caption, label in entries:
        lines.extend(
            [
                r"\begin{figure}[t]",
                r"    \centering",
                rf"    \includegraphics[width={width}]{{figures/{stem}.{primary_format}}}",
                rf"    \caption{{{caption}}}",
                rf"    \label{{{label}}}",
                r"\end{figure}",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate AAAI-style figures from TLDR hotword retrieval results."
    )
    parser.add_argument(
        "--excel",
        type=Path,
        default=Path(__file__).with_name("tldr_experiment_results.xlsx"),
        help="Input workbook. The Results_Long sheet is treated as canonical.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).with_name("figures"),
        help="Directory for generated figures and LaTeX snippets.",
    )
    parser.add_argument(
        "--formats",
        nargs="+",
        default=["pdf"],
        choices=["pdf", "png", "svg"],
        help="Output formats. PDF is recommended for AAAI LaTeX submissions.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    configure_matplotlib()

    records = load_results(args.excel)
    written: list[Path] = []
    written.extend(plot_gain_heatmap(records, args.output_dir, args.formats))
    written.extend(plot_difficulty_gain(records, args.output_dir, args.formats))
    written.extend(plot_training_degradation(records, args.output_dir, args.formats))
    written.extend(plot_zero_shot_ranking(records, args.output_dir, args.formats))
    written.extend(plot_detection_f1_overview(records, args.output_dir, args.formats))
    written.append(write_gain_table(records, args.output_dir))
    written.append(write_latex_includes(args.output_dir, args.formats[0]))

    print(f"Loaded {len(records)} rows from {args.excel.resolve()}")
    print(f"Saved {len(written)} files to {args.output_dir.resolve()}")
    for path in written:
        print(f"  {path.name}")


if __name__ == "__main__":
    main()
