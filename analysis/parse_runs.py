"""Parse the released Agrawal et al. double-auction runs into flat tables.

Outputs (in analysis/out/):
  runs.csv    one row per run: config, outcome metrics, judge summary
  rounds.csv  one row per (run, round, seller): ask, message, judge score
"""
import json
import re
import sys
from pathlib import Path

import pandas as pd

DATA = Path(sys.argv[1] if len(sys.argv) > 1 else "llm-agent-collusion/data")
OUT = Path(__file__).parent / "out"
JSON_BLOCK = re.compile(r"`{4}json\n(.*?)\n`{4}", re.S)


def family(models):
    fams = sorted({"claude" if "claude" in m else "gpt" if "gpt" in m else m for m in models})
    return "mixed" if len(fams) > 1 else fams[0]


def parse_run(run_dir):
    meta = json.loads((run_dir / "experiment_metadata.json").read_text())
    cfg = meta["auction_config"]
    metrics = json.loads((run_dir / "collusion_metrics.json").read_text())
    judge_file = run_dir / "llm_eval_full.json"  # absent for this project's runs (judge skipped)
    judge = json.loads(judge_file.read_text()) if judge_file.exists() else []
    rounds = [json.loads(b) for b in JSON_BLOCK.findall((run_dir / "auction_results.md").read_text())]

    # seller_k in metrics/judge follows meta["seller_ids"] order
    sid = {f"seller_{i + 1}": name for i, name in enumerate(meta["seller_ids"])}
    judge_score = {}
    for s in judge:
        for r in s["rounds"]:
            data = r.get("data") or {}
            judge_score[(sid[s["seller_id"]], r["round"])] = (data.get("score"), data.get("type"))

    tag = cfg["tag"]
    condition, seed = re.match(r"(.*)-(\d+)$", tag).groups()
    run = {
        "run": run_dir.name,
        "condition": condition,
        "seed": int(seed),
        "seller_family": family(cfg["seller_models"]),
        "buyer_family": family(cfg["buyer_models"]),
        "seller_models": "|".join(cfg["seller_models"]),
        "seller_comms": cfg["seller_comms_enabled"],
        "oversight": cfg["oversight_enabled"],
        "boss_pressure": cfg["boss_pressure"],
        "n_rounds": len(rounds),
        "competitive_price": metrics["competitive_equilibrium_price"],
        "avg_trade_price": metrics["avg_trade_price_overall"],
        "average_pcm": metrics["average_pcm"],
        "num_trades": metrics["num_trades"],
        "avg_seller_ask_dispersion": metrics["avg_seller_ask_dispersion"],
        "collusion_avg_seller_asks_auc": metrics["collusion_avg_seller_asks_auc"],
        "combined_seller_profits": metrics["combined_seller_profits"],
        "combined_buyer_surplus": metrics["combined_buyer_surplus"],
    }

    rows = []
    for r in rounds:
        for seller, ask in r["seller_asks"].items():
            score, ctype = judge_score.get((seller, r["round_number"]), (None, None))
            rows.append({
                "run": run_dir.name,
                "round": r["round_number"],
                "seller": seller,
                "ask": ask,
                "message": (r.get("seller_messages") or {}).get(seller),
                "judge_score": score,
                "judge_type": ctype,
            })
    rdf = pd.DataFrame(rows)
    run["judge_mean_score"] = rdf["judge_score"].mean()
    run["n_messages"] = int(rdf["message"].notna().sum())
    return run, rows


def main():
    runs, rounds = [], []
    for d in sorted(p for p in DATA.iterdir() if p.is_dir()):
        run, rows = parse_run(d)
        runs.append(run)
        rounds.extend(rows)
    OUT.mkdir(exist_ok=True)
    runs_df = pd.DataFrame(runs)
    runs_df.to_csv(OUT / "runs.csv", index=False)
    pd.DataFrame(rounds).to_csv(OUT / "rounds.csv", index=False)
    print(f"{len(runs_df)} runs, {len(rounds)} seller-rounds -> {OUT}")
    summary = runs_df.groupby(["condition", "seller_family", "seller_comms"]).agg(
        n=("run", "size"),
        trade_price=("avg_trade_price", "mean"),
        dispersion=("avg_seller_ask_dispersion", "mean"),
        judge=("judge_mean_score", "mean"),
        msgs=("n_messages", "mean"),
    )
    print(summary.round(2).to_string())


if __name__ == "__main__":
    main()
