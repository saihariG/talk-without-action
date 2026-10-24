"""Go/no-go: does a Qwen game with seller messaging look like the released GPT-4.1 games?

Usage: python -I analysis/compare_positive_control.py <run_dir> [<run_dir> ...]
Compares against the released GPT-4.1 `base-seller_comms` (messaging on) and
`base` (messaging off) runs. The competitive equilibrium price is $90 and the
joint-profit-maximising price is $100 (from the released collusion_metrics.json).
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from parse_runs import parse_run  # noqa: E402

RELEASED = Path(__file__).parent.parent / "llm-agent-collusion" / "data"
COLS = ["avg_trade_price", "num_trades", "average_pcm", "avg_seller_ask_dispersion", "n_messages", "n_rounds"]


def table(dirs, label):
    rows = []
    for d in dirs:
        run, seller_rounds = parse_run(d)
        sr = pd.DataFrame(seller_rounds)
        run["mean_ask_last10"] = sr[sr["round"] > sr["round"].max() - 10]["ask"].mean()
        run["group"] = label
        rows.append(run)
    return pd.DataFrame(rows)


def main():
    # label from the env so the same script serves every model tried
    import os
    new = table([Path(p) for p in sys.argv[1:]], os.getenv("LABEL", "new"))
    released = [p for p in RELEASED.iterdir() if p.is_dir()]
    on = table([p for p in released if p.name.split("_", 2)[2].startswith("base-seller_comms-")], "gpt-4.1 comms ON")
    off = table([p for p in released if p.name.split("_", 2)[2].startswith("base-") and "comms" not in p.name], "gpt-4.1 comms OFF")
    df = pd.concat([new, on, off])
    cols = COLS + ["mean_ask_last10"]
    print("mean (min-max) per group; competitive price = 90, joint-profit price = 100\n")
    for g, sub in df.groupby("group", sort=False):
        print(f"{g}  (n={len(sub)})")
        for c in cols:
            v = sub[c].astype(float)
            print(f"  {c:28s} {v.mean():8.2f}   ({v.min():.2f} to {v.max():.2f})")
    out = Path(__file__).parent / "out" / "positive_control.csv"
    df.to_csv(out, index=False)
    print(f"\nsaved {out}")


if __name__ == "__main__":
    main()
