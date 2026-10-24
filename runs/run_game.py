"""Run one Agrawal et al. double-auction game, with OpenAI models or a Modal vLLM endpoint.

Same simulation and metrics as the repo, with two things removed:
  - the repo's gpt-4.1-mini judge (the judge is chosen and frozen separately)
  - the wandb upload to the authors' team
Logs land in llm-agent-collusion/results/<experiment_id>/ in the same format as the released data.

Usage (from the repo root):
  python runs/run_game.py --tag qwen7b-seller_comms-1 --seller_comms_enabled \
      --seller_models Qwen/Qwen2.5-7B-Instruct x5 --buyer_models ... x5
Any simulation.py flag works.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for line in ((ROOT / ".env").read_text().splitlines() if (ROOT / ".env").exists() else []):
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())
os.environ["WANDB_MODE"] = "disabled"
# prompt templates are loaded relative to the repo root, so run from there;
# ExperimentLogger then writes to llm-agent-collusion/results/
REPO = ROOT / "llm-agent-collusion"
os.chdir(REPO)
sys.path.insert(0, str(REPO))

import runpy  # noqa: E402
from unittest import mock  # noqa: E402

# wandb 0.19's docker helper imports distutils, which Python 3.12 removed; nothing
# is uploaded, so a do-nothing stand-in replaces the whole package.
sys.modules["wandb"] = mock.MagicMock(name="wandb")

from src.continuous_double_auction.evaluation import evaluate  # noqa: E402

# simulation imports compute_metrics_for_exp_dir, which looks up run_llm_eval in this
# cached module at call time, so the patch survives runpy re-executing simulation.

evaluate.run_llm_eval = lambda metadata, log_file: None

# The repo's wrappers throw away response.usage, so tally the billed tokens here.
# Written to runs/usage/<tag>.json, per model: calls, input, cached input, output.
import atexit  # noqa: E402
import json  # noqa: E402
from openai.resources.chat import completions as _oa  # noqa: E402

USAGE = {}
_create = _oa.Completions.create


def _counted_create(self, *args, **kwargs):
    resp = _create(self, *args, **kwargs)
    u = getattr(resp, "usage", None)
    if u is not None:
        m = USAGE.setdefault(kwargs.get("model", "?"), {"calls": 0, "input": 0, "cached": 0, "output": 0})
        m["calls"] += 1
        m["input"] += u.prompt_tokens or 0
        details = getattr(u, "prompt_tokens_details", None)
        m["cached"] += (getattr(details, "cached_tokens", 0) or 0) if details else 0
        m["output"] += u.completion_tokens or 0
    return resp


_oa.Completions.create = _counted_create


def _write_usage():
    tag = sys.argv[sys.argv.index("--tag") + 1] if "--tag" in sys.argv else "untagged"
    out = ROOT / "runs" / "usage" / f"{tag}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(USAGE, indent=2))


atexit.register(_write_usage)

if __name__ == "__main__":
    sys.argv[0] = "simulation.py"
    runpy.run_module("src.continuous_double_auction.simulation", run_name="__main__")
