"""Run the frozen judges from PREREG.md section 3.

Usage (from the repo root):
  .venv/bin/python analysis/judge/run_judges.py drift
  .venv/bin/python analysis/judge/run_judges.py jr <run_dir> [<run_dir> ...]
  .venv/bin/python analysis/judge/run_judges.py jm <run_dir> [<run_dir> ...]

drift  re-scores the first 100 items of the released reliability study and applies the 0.94 rule
jr     the Agrawal judge, via the repo's own run_llm_eval, written to <run_dir>/llm_eval_full.json
jm     the same rubric on each non-null outgoing message, written to analysis/out/judge/jm/<run>.json
jr_rescore  J-R on released runs, written to analysis/out/judge/jr_rescore/<run>.json (released files untouched)
Finished runs are skipped, so a crashed job can be rerun. Billed tokens go to analysis/out/judge/usage_<mode>.json.
"""
import json
import os
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
REPO = ROOT / "llm-agent-collusion"
OUT = ROOT / "analysis" / "out" / "judge"
for line in ((ROOT / ".env").read_text().splitlines() if (ROOT / ".env").exists() else []):
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(ROOT / "analysis"))
sys.modules["wandb"] = mock.MagicMock(name="wandb")  # same stand-in as runs/run_game.py

from jinja2 import Environment, FileSystemLoader, select_autoescape  # noqa: E402
from openai.resources.chat import completions as _oa  # noqa: E402

from src.continuous_double_auction.evaluation import evaluate  # noqa: E402
from src.continuous_double_auction.util.misc import get_client  # noqa: E402
from parse_runs import parse_run  # noqa: E402

USAGE = {"calls": 0, "input": 0, "cached": 0, "output": 0}
_create = _oa.Completions.create


def _counted_create(self, *args, **kwargs):
    resp = _create(self, *args, **kwargs)
    u = getattr(resp, "usage", None)
    if u is not None:
        USAGE["calls"] += 1
        USAGE["input"] += u.prompt_tokens or 0
        details = getattr(u, "prompt_tokens_details", None)
        USAGE["cached"] += (getattr(details, "cached_tokens", 0) or 0) if details else 0
        USAGE["output"] += u.completion_tokens or 0
    return resp


_oa.Completions.create = _counted_create


def _env(template_dir):
    # same Environment settings as evaluate.run_llm_eval, so both judges escape text identically
    return Environment(loader=FileSystemLoader(searchpath=template_dir),
                       autoescape=select_autoescape(["html", "xml", "jinja2"]))


def _client():
    return get_client(evaluate.DEFAULT_EVAL_MODEL, temperature=evaluate.DEFAULT_EVAL_TEMPERATURE)


def drift():
    rel = json.loads((REPO / "data" / "llm_judge_reliability_analysis.json").read_text())
    items = [e["log"] for e in rel["eval_results"][0][:100]]
    released = [[s for s in rep[:100]] for rep in rel["scores"]]
    mode = [Counter(rep[j] for rep in released).most_common(1)[0][0] for j in range(100)]
    floor = min(sum(rep[j] == mode[j] for j in range(100)) / 100 for rep in released)
    tpl = _env(REPO / "src" / "continuous_double_auction" / "prompt_templates").get_template("seller_individual_eval.jinja2")
    client = _client()
    with ThreadPoolExecutor(max_workers=evaluate.MAX_WORKERS) as ex:
        results = list(ex.map(lambda log: evaluate.perform_single_eval(
            client, tpl.render(hour=log.get("hour"), hour_reasoning_data=log)), items))
    scores = [r[0].get("score") if r[0] else None for r in results]
    agree = sum(o == m for o, m in zip(scores, mode)) / 100
    out = {"n": 100, "errors": sum(o is None for o in scores), "agreement_with_released_mode": agree,
           "bar": floor, "pass": agree >= floor, "ours": scores, "released_mode": mode,
           "confusion_ours_vs_mode": {f"{m}->{o}": c for (m, o), c in Counter(zip(mode, scores)).items()}}
    (OUT / "drift.json").write_text(json.dumps(out, indent=2))
    print(f"drift: agreement {agree:.2f} vs bar {floor:.2f} -> {'PASS' if out['pass'] else 'FAIL'}, errors {out['errors']}")


def jr(run_dirs, out_dir=None):
    # out_dir: write <out_dir>/<run>.json instead of into the run folder (re-scoring released runs
    # must never overwrite the authors' llm_eval_full.json)
    for d in map(Path, run_dirs):
        path = (out_dir / f"{d.name}.json") if out_dir else d / "llm_eval_full.json"
        if path.exists():
            print(f"skip {d.name} (done)")
            continue
        meta = json.loads((d / "experiment_metadata.json").read_text())
        results = evaluate.run_llm_eval(meta, d / "unified.log")
        # same file format as compute_collusion_metrics writes
        path.write_text(json.dumps([{"seller_id": k, "rounds": v} for k, v in results.items()], indent=2))
        n_err = sum(r.get("status") != "success" for v in results.values() for r in v)
        print(f"jr {d.name}: {sum(len(v) for v in results.values())} seller-rounds, {n_err} errors")


def jm(run_dirs):
    tpl = _env(ROOT / "analysis" / "judge").get_template("message_judge.jinja2")
    client = _client()
    (OUT / "jm").mkdir(parents=True, exist_ok=True)
    for d in map(Path, run_dirs):
        path = OUT / "jm" / f"{d.name}.json"
        if path.exists():
            print(f"skip {d.name} (done)")
            continue
        _, rows = parse_run(d)
        msgs = [r for r in rows
                if r["message"] and str(r["message"]).strip().lower() not in ("null", "none", "nan")]
        with ThreadPoolExecutor(max_workers=evaluate.MAX_WORKERS) as ex:
            results = list(ex.map(lambda r: evaluate.perform_single_eval(
                client, tpl.render(hour=r["round"], message=r["message"])), msgs))
        out = []
        for r, (data, _raw, err) in zip(msgs, results):
            row = {"seller": r["seller"], "round": r["round"], "message": r["message"]}
            row.update({"status": "success", "data": data} if data else {"status": "error", "error": err})
            out.append(row)
        path.write_text(json.dumps(out, indent=2))
        print(f"jm {d.name}: {len(out)} messages, {sum(o['status'] != 'success' for o in out)} errors")


if __name__ == "__main__":
    mode, args = sys.argv[1], sys.argv[2:]
    OUT.mkdir(parents=True, exist_ok=True)
    try:
        (OUT / "jr_rescore").mkdir(parents=True, exist_ok=True)
        {"drift": lambda: drift(), "jr": lambda: jr(args), "jm": lambda: jm(args),
         "jr_rescore": lambda: jr(args, OUT / "jr_rescore")}[mode]()
    finally:
        prev = OUT / f"usage_{mode}.json"
        total = json.loads(prev.read_text()) if prev.exists() else {k: 0 for k in USAGE}
        prev.write_text(json.dumps({k: total[k] + USAGE[k] for k in USAGE}, indent=2))
        print("usage this call:", USAGE)
