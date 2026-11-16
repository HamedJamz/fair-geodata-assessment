#!/usr/bin/env python3
"""Step 4 — summary tables, figures and an auto-generated results summary."""
import json, sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fairgeo.common import RESULTS, ROOT, load_config
from fairgeo.indicators import INDICATORS, PRINCIPLES

INK, MUTED, BLUE = "#1f2933", "#6b7780", "#2f6fb0"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": "#c5ccd3", "text.color": INK,
                     "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": INK,
                     "figure.dpi": 150, "savefig.bbox": "tight", "font.family": "DejaVu Sans"})


def main():
    cfg = load_config()
    labels = {r["client_id"]: r.get("label", r["client_id"]) for r in cfg["repositories"]}
    df = pd.read_csv(RESULTS / "fair_assessment_table.csv")
    df["repo"] = df["client_id"].map(labels)
    order = [labels[c] for c in labels if c in set(df["client_id"])]
    ind = list(INDICATORS)
    score_cols = [f"score_{l}" for l in PRINCIPLES] + ["score_FAIR"]
    fig_dir = RESULTS / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    # ---- tables -----------------------------------------------------------
    by_repo = df.groupby("repo")[score_cols].mean().round(1).reindex(order)
    by_repo.insert(0, "n_datasets", df.groupby("repo").size().reindex(order))
    by_repo["FAIR_min"] = df.groupby("repo")["score_FAIR"].min().reindex(order)
    by_repo["FAIR_max"] = df.groupby("repo")["score_FAIR"].max().reindex(order)
    by_repo.loc["All repositories (pooled sample)"] = ([len(df)] + list(df[score_cols].mean().round(1))
                                                       + [df["score_FAIR"].min(), df["score_FAIR"].max()])
    by_repo.to_csv(RESULTS / "summary_by_repository.csv")

    rates = (df.groupby("repo")[ind].mean() * 100).round(0).reindex(order)
    rates_t = rates.T
    rates_t.insert(0, "label", [INDICATORS[k][1] for k in ind])
    rates_t.insert(0, "principle", [INDICATORS[k][0] for k in ind])
    rates_t["all_pooled"] = (df[ind].mean() * 100).round(0)
    rates_t.to_csv(RESULTS / "indicator_pass_rates.csv", index_label="indicator")

    top = (df.sort_values(["score_FAIR", "citation_count"], ascending=False)
             .groupby("repo", sort=False).head(1).head(10)
           [["doi", "repo", "title", "publication_year", "license", "citation_count"] + score_cols])
    top.to_csv(RESULTS / "success_story_candidates.csv", index=False)

    # ---- figure 1: heatmap repository x indicator -------------------------
    fig, ax = plt.subplots(figsize=(11.5, 0.55 * len(order) + 2.6), constrained_layout=True)
    im = ax.imshow(rates.values, cmap="Blues", vmin=0, vmax=100, aspect="auto")
    ax.set_xticks(range(len(ind)), [INDICATORS[k][1] for k in ind], rotation=40, ha="right")
    ax.set_yticks(range(len(order)), order)
    for i in range(rates.shape[0]):
        for j in range(rates.shape[1]):
            v = rates.values[i, j]
            ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=8,
                    color="white" if v > 55 else INK)
    pos = 0
    for letter, name in PRINCIPLES.items():
        k = sum(1 for m in INDICATORS.values() if m[0] == letter)
        ax.text(pos + k / 2 - 0.5, -0.75, name, ha="center", va="bottom", fontsize=9.5, weight="bold")
        if pos:
            ax.axvline(pos - 0.5, color="white", lw=4)
        pos += k
    ax.set_xticks([x - 0.5 for x in range(1, len(ind))], minor=True)
    ax.set_yticks([y - 0.5 for y in range(1, len(order))], minor=True)
    ax.grid(which="minor", color="white", lw=1.2); ax.tick_params(which="both", length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    cb = fig.colorbar(im, ax=ax, fraction=0.018, pad=0.015); cb.outline.set_visible(False)
    cb.set_label("datasets passing (%)")
    ax.set_title("Share of sampled datasets passing each metadata-level FAIR indicator",
                 loc="left", pad=28, fontsize=11, weight="bold")
    fig.savefig(fig_dir / "fig1_indicator_heatmap.png"); plt.close(fig)

    # ---- figure 2: small multiples, mean score per principle --------------
    fig, axes = plt.subplots(1, 5, figsize=(12, 0.42 * len(order) + 1.3), sharey=True)
    for ax, col in zip(axes, score_cols):
        vals = by_repo.loc[order, col]
        ax.barh(order, vals, color=BLUE, height=0.62)
        for y, v in enumerate(vals):
            ax.text(v + 2, y, f"{v:.0f}", va="center", fontsize=8, color=INK)
        ax.set_xlim(0, 112); ax.set_xticks([0, 50, 100])
        ax.set_title("Overall FAIR" if col == "score_FAIR" else PRINCIPLES[col[-1]],
                     fontsize=9.5, weight="bold", loc="left")
        ax.grid(axis="x", color="#e3e7eb", lw=0.8); ax.set_axisbelow(True)
        for s in ("top", "right", "left"):
            ax.spines[s].set_visible(False)
        ax.tick_params(length=0)
    axes[0].invert_yaxis()
    fig.suptitle("Mean metadata-level FAIR score per repository (0-100)", x=0.01, ha="left",
                 fontsize=11, weight="bold", y=1.06)
    fig.savefig(fig_dir / "fig2_scores_by_repository.png"); plt.close(fig)

    # ---- optional: comparison with F-UJI ----------------------------------
    fuji_note = "F-UJI cross-check: not run (optional step 3)."
    fuji_file = RESULTS / "fuji_scores.csv"
    if fuji_file.exists():
        m = df.merge(pd.read_csv(fuji_file).dropna(subset=["fuji_FAIR"]), on=["doi", "client_id"])
        if len(m) >= 5:
            rho = m["score_FAIR"].corr(m["fuji_FAIR"], method="spearman")
            fig, ax = plt.subplots(figsize=(4.6, 4.2))
            ax.scatter(m["score_FAIR"], m["fuji_FAIR"], s=22, color=BLUE, alpha=0.7, edgecolor="white")
            ax.set_xlabel("metadata-level FAIR score (this study)"); ax.set_ylabel("F-UJI FAIR score (%)")
            ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.grid(color="#e3e7eb", lw=0.8)
            ax.set_title(f"Cross-check with F-UJI (n={len(m)}, Spearman rho={rho:.2f})",
                         loc="left", fontsize=10, weight="bold")
            fig.savefig(fig_dir / "fig3_fuji_comparison.png"); plt.close(fig)
            fuji_note = (f"F-UJI cross-check on {len(m)} datasets: mean F-UJI FAIR score "
                         f"{m['fuji_FAIR'].mean():.1f} %, Spearman correlation with the "
                         f"metadata-level score {rho:.2f}.")

    # ---- auto summary ------------------------------------------------------
    info = json.loads((ROOT / "data" / "harvest_info.json").read_text())
    pooled = (df[ind].mean() * 100).round(0).sort_values()
    lines = ["# Results summary (auto-generated by scripts/04_analyse.py)", "",
             f"- Harvest date (UTC): {info['harvested_utc']}",
             f"- Datasets assessed: {len(df)} from {df['repo'].nunique()} repositories",
             f"- Mean overall score (pooled sample): {df['score_FAIR'].mean():.1f} / 100",
             f"- {fuji_note}", "", "## Mean scores per repository", "",
             by_repo.to_markdown() if hasattr(by_repo, "to_markdown") and _has_tabulate() else by_repo.to_string(),
             "", "## Weakest indicators (pooled, % of datasets passing)", ""]
    lines += [f"- {INDICATORS[k][1]} ({k}): {v:.0f} %" for k, v in pooled.head(5).items()]
    lines += ["", "## Strongest indicators (pooled)", ""]
    lines += [f"- {INDICATORS[k][1]} ({k}): {v:.0f} %" for k, v in pooled.tail(5)[::-1].items()]
    (RESULTS / "summary.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


def _has_tabulate():
    try:
        import tabulate  # noqa: F401
        return True
    except ImportError:
        return False


if __name__ == "__main__":
    main()
