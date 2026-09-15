#!/usr/bin/env python3
"""Regenerate docs/img/*.png from data/state.json.

Usage: python3 tools/charts.py
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

EXP = Path(__file__).resolve().parent.parent
DATA = EXP / "data" / "state.json"
IMG = EXP / "docs" / "img"

# FE tokens (millions) and effectiveness, from docs/TOKEN-COMPARISON.md /
# the frozen Token Usage Comparison artifact. Not derivable from
# state.json's raw total_tokens (mixed-model runs need per-model FE
# weighting; Codex runs need quota normalization) — kept here as the
# reviewed, citable numbers until a script computes FE from raw usage.
FE = {
    "07-sonnet-low": ("Sonnet, low", 0.91, 5.0, False),
    "01-control": ("Fable 5, high", 6.72, 4.5, False),
    "04-fable51-oob": ("Fable 5.1, high", 5.84, 4.5, True),
    "08-fable51-low": ("Fable 5.1, low", 2.88, 5.0, True),
    "02-orchestrate": ("Cloud Routines", 6.67, 2.0, True),
    "05-orchestrate-v2": ("Workflows", 4.98, 2.0, True),
    "03-new-orchestrate": ("Meta-orch (3 layers)", 6.47, 3.5, False),
    "06-codex": ("Codex Sol, low", 1.80, 3.0, True),
    "09-astra": ("Codex Astra, high", 5.53, 4.5, True),
    "10-qwen-claude": ("Local Qwen (Claude Code)", 0.0, 0.0, True),
    "11-qwen-opencode": ("Local Qwen (OpenCode)", 0.0, 0.0, True),
}

PER_MODEL_FE = {
    # run_id: {model: FE_millions} for the mixed-model runs (03/04/05).
    "03-new-orchestrate": {"fable": 0.34, "opus": 3.31, "sonnet": 2.82},
    "04-fable51-oob": {"fable-5-1": 5.75, "sonnet": 0.09},
    "05-orchestrate-v2": {"fable-5-1": 4.08, "sonnet": 0.90},
}


def load_state():
    return json.loads(DATA.read_text())


def chart_fe_by_run():
    order = list(FE.keys())
    labels = [FE[k][0] for k in order]
    values = [FE[k][1] for k in order]
    eff = [FE[k][2] for k in order]
    uncertain = [FE[k][3] for k in order]

    fig, ax = plt.subplots(figsize=(9, 6))
    colors = ["#c2703d" if u else "#3f5d3a" for u in uncertain]
    hatches = ["//" if u else None for u in uncertain]
    bars = ax.barh(labels, values, color=colors)
    for bar, h in zip(bars, hatches):
        if h:
            bar.set_hatch(h)
            bar.set_edgecolor("#1a1a17")
    for bar, v, e in zip(bars, values, eff):
        ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
                 f"{v:.2f}M FE, {e}/5", va="center", fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("Fable-equivalent (FE) tokens, millions")
    ax.set_title("FE tokens by run (hatched = polluted/predicted/normalized)")
    fig.tight_layout()
    fig.savefig(IMG / "fe-by-run.png", dpi=150)
    plt.close(fig)


def chart_effectiveness_vs_fe():
    fig, ax = plt.subplots(figsize=(7, 6))
    for k, (label, fe, eff, uncertain) in FE.items():
        if fe == 0 and eff == 0:
            continue
        ax.scatter(fe, eff, s=60,
                    facecolors="none" if uncertain else "#3f5d3a",
                    edgecolors="#3f5d3a")
        ax.annotate(label, (fe, eff), textcoords="offset points",
                     xytext=(6, 4), fontsize=8)
    ax.set_xlabel("FE tokens (millions)")
    ax.set_ylabel("Effectiveness / 5")
    ax.set_ylim(0, 5.5)
    ax.set_title("Effectiveness vs. FE tokens")
    fig.tight_layout()
    fig.savefig(IMG / "effectiveness-vs-fe.png", dpi=150)
    plt.close(fig)


def chart_per_model_split():
    runs = list(PER_MODEL_FE.keys())
    models = sorted({m for v in PER_MODEL_FE.values() for m in v})
    fig, ax = plt.subplots(figsize=(7, 5))
    bottoms = [0] * len(runs)
    palette = ["#4f83cc", "#6a4fb0", "#1f8a86", "#b0507a"]
    for i, m in enumerate(models):
        vals = [PER_MODEL_FE[r].get(m, 0) for r in runs]
        ax.bar(runs, vals, bottom=bottoms, label=m, color=palette[i % len(palette)])
        bottoms = [b + v for b, v in zip(bottoms, vals)]
    ax.set_ylabel("FE tokens (millions)")
    ax.set_title("Per-model FE split, mixed-model runs")
    ax.legend()
    fig.tight_layout()
    fig.savefig(IMG / "per-model-fe-split.png", dpi=150)
    plt.close(fig)


def main():
    IMG.mkdir(parents=True, exist_ok=True)
    chart_fe_by_run()
    chart_effectiveness_vs_fe()
    chart_per_model_split()
    print(f"wrote charts to {IMG}")


if __name__ == "__main__":
    main()
