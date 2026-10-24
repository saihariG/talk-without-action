"""Exploratory checks added on 2026-10-24, after the freeze: label sensitivity and slope robustness.

Not pre-registered. Nothing here changes a frozen number. It reads analysis/out/detectors/runs.csv
(written by detectors.py) and the raw auction logs, and writes analysis/out/robustness/robustness.json.

Usage (from the repo root, after analysis/detectors.py):
  .venv/bin/python analysis/robustness.py

1. Label sensitivity. The causal label marks a channel, not its use. In the two oversight conditions an
   overseer gags every seller within rounds 2-8, so the frozen causal metrics (cases A, A', B, D) are
   re-run with those 20 runs (a) left out and (b) labelled 0.
2. Slope robustness for D4 (ask(i,t) - ask(i,t-1) on m(t-1) - ask(i,t-1)).
   - placebo: the same slope with the median ask of round t-1 (all five sellers) in place of the
     message price m(t-1), over every round pair. It is defined for runs without messages too.
   - controlled: one OLS with an intercept, the message gap and the median-ask gap, on D4's points
     (round pairs whose round t-1 messages name a price). The message coefficient is the check.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

import detectors as det

OUT = det.ROOT / "analysis" / "out" / "robustness"
GAGGED = ("oversight", "boss_pressure-oversight")


def run_dir(name):
    released = det.DATA / name
    return released if released.exists() else det.OURS / name


def slopes(rounds):
    """Returns (placebo beta, controlled message coefficient, controlled median-ask coefficient)."""
    px, py, cx, cy = [], [], [], []
    for prev, cur in zip(rounds, rounds[1:]):
        asks0 = {s: a for s, a in prev["seller_asks"].items() if isinstance(a, (int, float))}
        if not asks0:
            continue
        med = float(np.median(list(asks0.values())))
        amounts = [v for m in (prev.get("seller_messages") or {}).values() if det.is_msg(m)
                   for v in det.dollar_amounts(m)]
        m = float(np.median(amounts)) if amounts else None
        for seller, ask in cur["seller_asks"].items():
            a0 = asks0.get(seller)
            if isinstance(ask, (int, float)) and a0 is not None:
                px.append(med - a0)
                py.append(ask - a0)
                if m is not None:
                    cx.append([1.0, m - a0, med - a0])
                    cy.append(ask - a0)
    placebo = float(np.polyfit(px, py, 1)[0]) if len(px) >= 3 and np.var(px) > 0 else np.nan
    if len(cx) >= 4 and np.linalg.matrix_rank(np.array(cx)) == 3:
        coef = np.linalg.lstsq(np.array(cx), np.array(cy), rcond=None)[0]
        return placebo, float(coef[1]), float(coef[2])
    return placebo, np.nan, np.nan


def by_case(df, col):
    return {c: {"mean": float(g[col].mean()), "n": int(g[col].notna().sum()), "n_positive": int((g[col] > 0).sum())}
            for c, g in df.groupby("case")}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(det.OUT / "runs.csv")
    for d in ("D1", "D2a", "D2b", "D3a", "D3b", "D4", "D5a", "D5b"):
        df[d] = df[d].astype(bool)
    prim = df[df.case.isin(det.FROZEN)].copy()

    # 1. label sensitivity
    gag = prim.condition.isin(GAGGED)
    relabelled = prim.copy()
    relabelled.loc[gag, "causal"] = 0
    label = {
        "n_gagged": int(gag.sum()),
        "frozen": det.metrics(prim, "causal"),
        "gagged_excluded": det.metrics(prim[~gag], "causal"),
        "gagged_as_0": det.metrics(relabelled, "causal"),
    }

    # 2. slope robustness
    rows = []
    for name in df.run:
        rounds = [json.loads(b) for b in det.JSON_BLOCK.findall((run_dir(name) / "auction_results.md").read_text())]
        rows.append(dict(zip(("placebo_beta", "ctrl_msg_beta", "ctrl_med_beta"), slopes(rounds)), run=name))
    df = df.merge(pd.DataFrame(rows), on="run")
    prim = df[df.case.isin(det.FROZEN)]
    test = prim[prim.split == "test"]
    ok = test.ctrl_msg_beta.notna()
    y, s = test.causal[ok].to_numpy(), test.ctrl_msg_beta[ok].to_numpy()
    d = df[df.case == "D"].sort_values("seed")
    slope = {
        "d4_check_max_abs_diff": None,
        "placebo_by_case": by_case(df, "placebo_beta"),
        "ctrl_msg_by_case": by_case(df, "ctrl_msg_beta"),
        "ctrl_med_by_case": by_case(df, "ctrl_med_beta"),
        "D_by_seed": {int(r.seed): {"d4_beta": r.d4_beta, "placebo": r.placebo_beta, "ctrl_msg": r.ctrl_msg_beta,
                                    "ctrl_med": r.ctrl_med_beta} for r in d.itertuples()},
        "ctrl_msg_auroc_test": {"auroc": det.auroc(y, s), "auroc_ci": det.auroc_ci(y, s),
                                "n_pos": int((y == 1).sum()), "n_neg": int((y == 0).sum())},
    }
    # the controlled fit uses D4's points, so refitting D4 alone on them must give runs.csv's d4_beta
    refit = []
    for name in df[df.d4_beta.notna()].run:
        rounds = [json.loads(b) for b in det.JSON_BLOCK.findall((run_dir(name) / "auction_results.md").read_text())]
        refit.append(abs(det.action_dependence(rounds)[0] - df.loc[df.run == name, "d4_beta"].item()))
    slope["d4_check_max_abs_diff"] = float(max(refit))

    res = {"label_sensitivity": label, "slope_robustness": slope}
    (OUT / "robustness.json").write_text(json.dumps(res, indent=2, default=float))
    df[["run", "case", "split", "causal", "d4_beta", "placebo_beta", "ctrl_msg_beta", "ctrl_med_beta"]].to_csv(
        OUT / "slopes.csv", index=False)

    pd.set_option("display.width", 200)
    for k in ("frozen", "gagged_excluded", "gagged_as_0"):
        t = pd.DataFrame(label[k]).T
        print(f"\nlabel: {k}")
        print(t[[c for c in ("n_pos", "n_neg", "tpr_k", "fpr_k", "auroc", "auroc_ci") if c in t]])
    print("\nslope means by case")
    print(pd.DataFrame({k: {c: v["mean"] for c, v in slope[k].items()}
                        for k in ("placebo_by_case", "ctrl_msg_by_case", "ctrl_med_by_case")}).round(3))
    print("\nD by seed\n", pd.DataFrame(slope["D_by_seed"]).T.round(3))
    print("\ncontrolled message coefficient, test AUROC:", slope["ctrl_msg_auroc_test"])
    print("D4 refit check, max abs diff:", slope["d4_check_max_abs_diff"])


if __name__ == "__main__":
    main()
