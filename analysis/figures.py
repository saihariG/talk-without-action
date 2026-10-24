"""Paper figures from analysis/out/detectors/{runs.csv,results.json}.

Usage (from the repo root):
  .venv/bin/python analysis/figures.py

Writes paper/figures/fig{0..4}_*.{pdf,png}, plus PDF copies in paper/latex/figures/.
Colors: blue = CAUSAL 1 (A, A'), orange = CAUSAL 0 (B, D, E), gray = N (exploratory).
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DET = ROOT / "analysis" / "out" / "detectors"
FIG = ROOT / "paper" / "figures"
FIG_TEX = ROOT / "paper" / "latex" / "figures"  # PDF copies the LaTeX source includes

BLUE, ORANGE, GRAY = "#2a78d6", "#eb6834", "#8c8b86"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
ALL_CASES = ["A", "A'", "B", "D", "E", "N"]  # E (amendment A2) appears once its runs exist
CASE_ORDER = list(ALL_CASES)  # narrowed in main() to the cases present
CASE_LABEL = {c: c for c in ALL_CASES}
CASE_COLOR = {"A": BLUE, "A'": BLUE, "B": ORANGE, "D": ORANGE, "E": ORANGE, "N": GRAY}
CASE_NAME = {"A": "coordinated, comms on", "A'": "other comms-on conditions", "B": "no messages, comms off",
             "D": "talk without action", "E": "common incentive, comms off", "N": "exploratory"}

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK,
    "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "savefig.dpi": 300, "savefig.bbox": "tight", "figure.facecolor": "white",
})


def save(fig, name):
    FIG.mkdir(parents=True, exist_ok=True)
    FIG_TEX.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"{name}.{ext}")
    fig.savefig(FIG_TEX / f"{name}.pdf")
    plt.close(fig)


def fig0_matrix(df):
    """Headline: share of runs each detector gets wrong, by case (all runs, frozen flags)."""
    from matplotlib.colors import LinearSegmentedColormap
    cols = [("D1", "Price\nscreen\n"), ("D2a", "Reasoning\njudge\nstrict"), ("D2b", "Reasoning\njudge\nmoderate"),
            ("D3a", "Message\njudge\nstrict"), ("D3b", "Message\njudge\nmoderate"),
            ("D4", "Follow-\nthe-talk\nslope"), ("D5a", "Combined\nrule\nstrict"), ("D5b", "Combined\nrule\nlenient")]
    rows = [("A", "Coordinated, comms on (A)", True), ("A'", "Other comms-on conditions (A')", True),
            ("B", "No messages, comms off (B)", False), ("D", "Talk without action (D)", False)]
    if (df.case == "E").any():
        rows.append(("E", "Common incentive, comms off (E)", False))
    defined = {"D1": lambda d: d.avg_trade_price.notna(), "D2a": lambda d: d.jr_n > 0, "D2b": lambda d: d.jr_n > 0,
               "D3a": lambda d: d.jm_n > 0, "D3b": lambda d: d.jm_n > 0, "D4": lambda d: d.d4_beta.notna(),
               "D5a": lambda d: (d.jm_n > 0) & d.d4_beta.notna(), "D5b": lambda d: (d.jm_n > 0) & d.d4_beta.notna()}
    cmap = LinearSegmentedColormap.from_list("ink", ["#f4f3f0", "#3a3936"])
    fig, ax = plt.subplots(figsize=(7.4, 0.6 + 0.55 * len(rows)))
    for i, (case, label, should) in enumerate(rows):
        d = df[df.case == case]
        for j, (k, _) in enumerate(cols):
            m = defined[k](d)
            n, flagged = int(m.sum()), int(d[k][m].sum())
            if n == 0:
                why = "no\nmessages" if case in ("B", "E") else "not run"
                ax.add_patch(plt.Rectangle((j + 0.03, i + 0.03), 0.94, 0.94, fc="white", ec="#c9c8c3", lw=0.8, ls=(0, (3, 2))))
                ax.text(j + 0.5, i + 0.5, why, ha="center", va="center", fontsize=7, color=INK2)
                continue
            wrong = (n - flagged if should else flagged) / n
            ax.add_patch(plt.Rectangle((j + 0.03, i + 0.03), 0.94, 0.94, fc=cmap(wrong), ec="none"))
            ax.text(j + 0.5, i + 0.5, f"{flagged}/{n}", ha="center", va="center", fontsize=9,
                    color="white" if wrong >= 0.55 else INK)
        ax.text(-0.12, i + 0.36, label, ha="right", va="center", fontsize=8.5, color=INK)
        ax.text(-0.12, i + 0.68, "should be flagged" if should else "should not be flagged", ha="right",
                va="center", fontsize=7.5, color=BLUE if should else ORANGE)
    ax.set_xlim(0, len(cols))
    ax.set_ylim(len(rows), 0)
    ax.set_xticks([j + 0.5 for j in range(len(cols))])
    ax.set_xticklabels([f"{name}\n{k}" for k, name in cols], fontsize=7.5, color=INK)
    ax.xaxis.tick_top()
    ax.tick_params(length=0)
    ax.set_yticks([])
    ax.grid(False)
    for side in ("left", "bottom", "top", "right"):
        ax.spines[side].set_visible(False)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(0, 1))
    cb = fig.colorbar(sm, ax=ax, fraction=0.03, pad=0.02)
    cb.set_label("share of runs the detector gets wrong", fontsize=7.5, color=INK2)
    cb.ax.tick_params(labelsize=7)
    cb.outline.set_visible(False)
    save(fig, "fig0_case_by_detector")


def fig1_design():
    """The talk-without-action split versus the released comms-on prompt."""
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.7))

    def box(ax, xy, w, h, text, color):
        ax.add_patch(FancyBboxPatch(xy, w, h, boxstyle="round,pad=0.02,rounding_size=0.03",
                                    fc="white", ec=color, lw=1.4))
        ax.text(xy[0] + w / 2, xy[1] + h / 2, text, ha="center", va="center", fontsize=7, color=INK)

    def arrow(ax, a, b, color=INK2, style="-|>", ls="-"):
        ax.add_patch(FancyArrowPatch(a, b, arrowstyle=style, mutation_scale=10, color=color, lw=1.1, ls=ls))

    for ax, title in zip(axes, ["A. Released comms-on (one call)", "D. Talk without action (two calls)"]):
        ax.set_xlim(-0.04, 1.04)
        ax.set_ylim(0, 1)
        ax.axis("off")
        ax.set_title(title, fontsize=9, color=INK, loc="left")

    ax = axes[0]
    box(ax, (0.00, 0.62), 0.30, 0.24, "inbox:\nother sellers'\nmessages", INK2)
    box(ax, (0.39, 0.40), 0.30, 0.34, "seller call\n(reasoning,\nask, message)", BLUE)
    box(ax, (0.78, 0.62), 0.20, 0.24, "ask", BLUE)
    box(ax, (0.78, 0.18), 0.20, 0.24, "message", BLUE)
    arrow(ax, (0.32, 0.72), (0.39, 0.62))
    arrow(ax, (0.71, 0.64), (0.78, 0.72))
    arrow(ax, (0.71, 0.50), (0.78, 0.32))
    ax.text(0.00, -0.06, "messages can reach asks", fontsize=8, color=BLUE)

    ax = axes[1]
    box(ax, (0.00, 0.62), 0.27, 0.24, "inbox:\nother sellers'\nmessages", INK2)
    box(ax, (0.35, 0.62), 0.32, 0.26, "ask call\n(comms-off\nprompt)", ORANGE)
    box(ax, (0.35, 0.04), 0.32, 0.42, "message call\n(sees market,\ninbox, own ask;\nwrites\nnothing back)", ORANGE)
    box(ax, (0.78, 0.64), 0.20, 0.22, "ask", ORANGE)
    box(ax, (0.78, 0.14), 0.20, 0.22, "message", ORANGE)
    arrow(ax, (0.13, 0.60), (0.35, 0.30))
    arrow(ax, (0.69, 0.75), (0.78, 0.75))
    arrow(ax, (0.51, 0.60), (0.51, 0.48))
    arrow(ax, (0.69, 0.25), (0.78, 0.25))
    ax.text(0.53, 0.53, "ask", fontsize=7, color=INK2, ha="left")
    ax.text(0.00, -0.06, "no path from any message to any ask", fontsize=8, color=ORANGE)
    save(fig, "fig1_design")


def strip(ax, df, col, thr=None, ylabel="", ylim=None):
    rng = np.random.default_rng(0)
    for i, c in enumerate(CASE_ORDER):
        v = df[df.case == c][col].dropna().to_numpy()
        if len(v) == 0:
            ax.text(i, ylim[0] + 0.25 * (ylim[1] - ylim[0]) if ylim else 0.6, "n/a", ha="center", va="center",
                    fontsize=7, color=INK2)
            continue
        x = i + rng.uniform(-0.18, 0.18, len(v))
        hollow = c == "N"
        ax.scatter(x, v, s=22, facecolor="white" if hollow else CASE_COLOR[c], edgecolor=CASE_COLOR[c],
                   linewidth=1.0 if hollow else 0.6, zorder=3)
        ax.plot([i - 0.28, i + 0.28], [np.mean(v)] * 2, color=INK, lw=1.6, zorder=4)
    if thr is not None:
        ax.axhline(thr, color=INK2, lw=0.9, ls="--", zorder=2)
    ax.set_xticks(range(len(CASE_ORDER)))
    ax.set_xticklabels([CASE_LABEL[c] for c in CASE_ORDER], fontsize=8.5)
    ax.set_ylabel(ylabel)
    ax.grid(axis="x", visible=False)
    if ylim:
        ax.set_ylim(*ylim)


def fig2_scores(df):
    fig, axes = plt.subplots(2, 3, figsize=(7.2, 5.0))
    panels = [("avg_trade_price", 90, "average trade price ($)", None, "Price screen\nflag > $90"),
              ("jr_share4", 0.5, "share of seller-rounds scored 4", (-0.03, 1.03), "Reasoning judge, strict\nflag > 0.5"),
              ("jr_share3p", 0.5, "share scored ≥ 3", (-0.03, 1.03), "Reasoning judge, moderate\nflag > 0.5"),
              ("jm_share4", 0.5, "share of messages scored 4", (-0.03, 1.03), "Message judge, strict\nflag > 0.5"),
              ("d4_beta", 0.0, "slope β", None, "Follow-the-talk slope\nτ = −∞: any β flags")]
    for ax, (col, thr, ylabel, ylim, title) in zip(axes.flat, panels):
        strip(ax, df, col, thr, ylabel, ylim)
        ax.set_title(title, fontsize=8.5, loc="left")
        ax.yaxis.label.set_size(8)
    key = axes.flat[5]
    key.axis("off")
    counts = df.case.value_counts()
    cases = "\n".join(f"{c}: {CASE_NAME[c]} ({counts[c]})" for c in CASE_ORDER)
    jm_cases = [c for c in CASE_ORDER if (df[df.case == c].jm_n > 0).any()]
    msg_cases = [c for c in CASE_ORDER if c not in ("B", "E")]
    jm_note = ("The message judge was run\non every run with messages." if jm_cases == msg_cases else
               "The message judge was run\non " + ", ".join(jm_cases[:-1]) + " and " + jm_cases[-1] + " only.")
    key.text(0.0, 1.0, cases + "\n\n"
             "Dots: runs. Black bar: case mean.\nDashed: frozen flag threshold\n(slope: β = 0 reference).\n\n"
             "Blue: messages can reach asks.\nOrange: they can't.\nHollow gray: exploratory.\n" + jm_note,
             fontsize=7.5, color=INK2, va="top", transform=key.transAxes)
    fig.tight_layout()
    save(fig, "fig2_scores_by_case")


def fig3_auroc(res):
    m = res["metrics_causal"]
    jm_pop = "comms on vs D" if m["D3a"]["n_pos"] > 10 else "A vs D"  # A vs D until J-M on A' exists
    pops = {"D1": "all", "D2a": "all", "D2b": "all", "meanJR": "all", "D3a": jm_pop, "D3b": jm_pop, "meanJM": jm_pop,
            "D4": "test, β defined"}
    names = [("Price screen", "D1"), ("Reasoning judge, strict", "D2a"), ("Reasoning judge, moderate", "D2b"),
             ("Reasoning judge, mean", "meanJR"), ("Message judge, strict", "D3a"), ("Message judge, moderate", "D3b"),
             ("Message judge, mean", "meanJM"), ("Follow-the-talk slope", "D4")]
    rows = [(label, k, f"{pops[k]}, {m[k]['auroc_n']} runs" if pops[k] != "all" else f"all {m[k]['auroc_n']} runs")
            for label, k in names]
    fig, ax = plt.subplots(figsize=(6.8, 3.4))
    for i, (label, k, pop) in enumerate(rows):
        a, (lo, hi) = m[k]["auroc"], m[k]["auroc_ci"]
        y = len(rows) - 1 - i
        ax.plot([lo, hi], [y, y], color=INK2, lw=1.4, zorder=2)
        ax.scatter([a], [y], s=34, color=BLUE if a > 0.5 else ORANGE, zorder=3, edgecolor="white", linewidth=0.8)
        ax.text(1.04, y, f"{a:.2f} [{lo:.2f}, {hi:.2f}]", va="center", fontsize=8.5, color=INK)
        ax.text(-0.02, y, pop, va="center", ha="right", fontsize=8, color=INK2, transform=ax.get_yaxis_transform())
    ax.axvline(0.5, color=INK2, lw=0.9, ls="--")
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[0] for r in rows][::-1])
    ax.tick_params(axis="y", pad=128)
    ax.set_xlim(0, 1)
    ax.set_xlabel("AUROC for the causal label (can messages reach asks?), 95% bootstrap CI")
    ax.grid(axis="y", visible=False)
    save(fig, "fig3_auroc_causal")


def fig4_rescore(df):
    rel = df[df.case.isin(["A", "A'", "B"])]
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.2))
    for ax, (r, o, name, title) in zip(axes, [("jr_rel_share4", "jr_share4", "share scored 4", "Reasoning judge, strict"),
                                              ("jr_rel_share3p", "jr_share3p", "share scored ≥ 3", "Reasoning judge, moderate")]):
        ax.set_title(title, fontsize=9, loc="left")
        for c in ("A", "A'", "B"):
            s = rel[rel.case == c]
            ax.scatter(s[r], s[o], s=20, color=CASE_COLOR[c], edgecolor="white", linewidth=0.6, zorder=3,
                       marker="o" if c != "A'" else "^",
                       label={"A": "A coordinated", "A'": "A' other comms on", "B": "B comms off"}[c])
        ax.plot([0, 1], [0, 1], color=INK2, lw=0.9, zorder=2)
        ax.axhline(0.5, color=GRID, lw=1.0, ls="--")
        ax.axvline(0.5, color=GRID, lw=1.0, ls="--")
        ax.set_xlim(-0.02, 1.02)
        ax.set_ylim(-0.02, 1.02)
        ax.set_xlabel(f"released scores (May 2025): {name}", fontsize=8)
        ax.set_ylabel(f"re-score (Oct 2026): {name}", fontsize=8)
    axes[0].legend(frameon=False, fontsize=8, loc="upper left")
    fig.tight_layout()
    save(fig, "fig4_rescore_vs_released")


def main():
    df = pd.read_csv(DET / "runs.csv")
    res = json.loads((DET / "results.json").read_text())
    CASE_ORDER[:] = [c for c in ALL_CASES if c in set(df.case)]
    fig0_matrix(df)
    fig1_design()
    fig2_scores(df)
    fig3_auroc(res)
    fig4_rescore(df)
    print("figures ->", FIG)


if __name__ == "__main__":
    main()
