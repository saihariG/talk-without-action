"""Count prompt and response tokens per game from logged agent transcripts.

Usage: python -I analysis/token_usage.py <run_dir> [<run_dir> ...]
Uses o200k_base, the gpt-4.1 family tokenizer. Prints one line per run and
the mean, so cost estimates come from measured games rather than guesses.
"""
import re
import sys
from pathlib import Path

import tiktoken

ENC = tiktoken.get_encoding("o200k_base")
HEADER = re.compile(r"^## (Prompt|Response): Round \d+ - .*$", re.M)


def count(run_dir):
    totals = {"Prompt": 0, "Response": 0, "calls": 0}
    for f in Path(run_dir).glob("*.md"):
        if not f.name.startswith(("Seller ", "Buyer ")):
            continue
        text = f.read_text()
        heads = list(HEADER.finditer(text))
        for i, h in enumerate(heads):
            end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
            totals[h.group(1)] += len(ENC.encode(text[h.end():end]))
            totals["calls"] += h.group(1) == "Prompt"
    return totals


if __name__ == "__main__":
    rows = []
    for d in sys.argv[1:]:
        t = count(d)
        rows.append(t)
        print(f"{Path(d).name:55s} calls={t['calls']:4d} input={t['Prompt']:8d} output={t['Response']:7d}")
    n = len(rows)
    print(f"{'MEAN':55s} calls={sum(r['calls'] for r in rows) / n:6.1f} "
          f"input={sum(r['Prompt'] for r in rows) / n:10.0f} output={sum(r['Response'] for r in rows) / n:9.0f}")
    print(f"{'MAX':55s} input={max(r['Prompt'] for r in rows):10d} output={max(r['Response'] for r in rows):9d}")
