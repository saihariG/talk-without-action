# Talk Without Action

**"Talk Is Not Coordination: Testing LLM-Collusion Detectors Against a Causal Control"**, by Sai Hari Krishnan Gopikrishnan (University of Maryland, College Park), written for the Apart AI Collusion Research Sprint, Oct 23-25, 2026.

## What the project does

Work on LLM collusion often detects it from what agents say. An LLM judge scores how coordinated their reasoning or messages sound. This project tests whether such detectors can tell coordination that *causes* conduct from talk that doesn't.

It adds two controls to the continuous double auction of Agrawal et al. (2025, arXiv:2507.01413).
- **Talk without action:** GPT-4.1 sellers message each other as usual, but each seller's ask comes from a separate call that never sees a message. In 6 games the sellers openly agree to hold prices, yet average trade prices ($86.83, range $84.83 to $89.34) resemble the released no-messaging runs.
- **Harm without agreement** (amendment A2): Sellers can't message, but each privately gets the released CEO message to keep margins high. In 6 games prices rise to $95.73 (range $94.51 to $96.38).

Five detector families were pre-registered and scored on these 12 games and the 75 released runs:
- The published rubric applied to messages flags all 6 talk-without-action games. Across all 65 comms-on runs, its score is at chance (AUROC 0.49). Without the 20 runs whose channel an overseer gagged, it is 0.70 (exploratory).
- A slope of ask changes on the price discussed in the previous round is positive in all 6 talk-without-action games, and ranks them above real coordination (AUROC 0.32). Controlling for the previous round's median ask, the message coefficient stays positive in talk without action (exploratory).
- The price screen and a moderate reasoning-judge threshold flag all 6 harm-without-agreement games.
- Among single signals, only the strict published reasoning judge rejects both controls. Against talk without action it does so only because it reads reasoning that, by construction, never saw a message.
- The combined price-and-talk rules also reject both, but only because talk-without-action prices stay below $90 and harm-without-agreement runs have no messages.

## Upstream code

- **Upstream code and data are not in this repo.** `setup.sh` clones Agrawal et al.'s repository ([andyjliu/llm-agent-collusion](https://github.com/andyjliu/llm-agent-collusion), commit `2bb2a7e`) into `llm-agent-collusion/` and applies the patch. That repository has no licence file, so its code and its 75 released runs are not redistributed here. The MIT licence covers only the files in this repo.

## Layout

| path | contents |
|---|---|
| `setup.sh` | clones upstream at the pinned commit, applies the patch, links this repo's runs into it |
| `upstream_patch/` | the diff against upstream |
| `data/runs/` | the 17 new games in the upstream log format: 6 talk-without-action and 6 harm-without-agreement (GPT-4.1), and 5 exploratory (Qwen2.5-7B, Qwen2.5-32B-AWQ, gpt-4.1-mini x3) |
| `data/smoke/` | two 3-round smoke tests: ask prompts contain no message text (talk without action), and every seller prompt has the CEO message and no messaging (harm without agreement) |
| `runs/` | the game runner and billed token counts per game (`usage/`, and `_failed/` for games that stopped partway) |
| `analysis/` | parser, judge runner, message-judge prompt, detectors, figures, exploratory robustness checks (`robustness.py`), and the evidence notebook (`paper_evidence.ipynb`) |
| `analysis/out/` | judge outputs, the re-score comparison, detector results (`detectors/RESULTS.md`), robustness checks (`robustness/`) |
| `modal_vllm/` | vLLM server on Modal for the Qwen games |
| `PREREG.md` | the frozen analysis plan; `PREREG.sha256` holds its hash. `PREREG_AMENDMENTS.md` holds amendments A1 and A2, and `PREREG_AMENDMENTS.sha256` its hash at the A2 freeze |
| `LEGAL_SOURCES.md` | every legal quote with its pin cite |
| `NOVELTY.md` | prior-work check |
| `paper/` | LaTeX source and PDF (`paper/latex/`), figures (`paper/figures/`) |

## Reproduce

Requires Python 3.12 and git.

```bash
./setup.sh
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

**Re-run the analysis from the saved judge outputs.** This is free and needs no API key. It rewrites `analysis/out/detectors/`, `analysis/out/robustness/` and `paper/figures/`.

```bash
.venv/bin/python analysis/detectors.py
.venv/bin/python analysis/robustness.py
.venv/bin/python analysis/figures.py
```

**Check the pre-registration hashes.**

```bash
shasum -a 256 -c PREREG.sha256 PREREG_AMENDMENTS.sha256
```

**Re-run the judges.** This costs money. Copy `.env.example` to `.env` and add `OPENAI_API_KEY`. The runner skips any run that already has an output, so delete an output file to score that run again. The original costs are under "Cost".

```bash
.venv/bin/pip install -e llm-agent-collusion
RUNS=$(ls -d llm-agent-collusion/results/2026*)
A=$(ls -d llm-agent-collusion/data/*_base-seller_comms-*)
.venv/bin/python analysis/judge/run_judges.py drift                 # drift check, 100 reliability items
.venv/bin/python analysis/judge/run_judges.py jr $RUNS              # reasoning judge on this repo's runs
APRIME=$(cat analysis/out/judge/aprime_runs.txt)
WITH_MSGS=$(ls -d llm-agent-collusion/results/2026* | grep -v boss_nocomms)
.venv/bin/python analysis/judge/run_judges.py jm $A $APRIME $WITH_MSGS   # message judge on every run with messages
.venv/bin/python analysis/judge/run_judges.py jr_rescore llm-agent-collusion/data/2025*    # the 75 released runs
.venv/bin/python analysis/judge/compare_rescore.py
```

**Run a game.** Run one game at a time. Talk without action costs about $3.14 per game, and harm without agreement about $2.07.

```bash
M=gpt-4.1
.venv/bin/python runs/run_game.py --tag gpt41-talk_without_action-1 --seller_comms_enabled --talk_without_action --rounds 30 \
  --seller_models $M $M $M $M $M --buyer_models $M $M $M $M $M
.venv/bin/python runs/run_game.py --tag gpt41-boss_nocomms-1 --boss_pressure --rounds 30 \
  --seller_models $M $M $M $M $M --buyer_models $M $M $M $M $M
```

## Data notes

- **Judge outputs for the released runs are stored as scores only** (seller, round, status, score, type). Their text fields quote the released runs, which live upstream. The new runs keep the full judge output.
- **Messages that are empty or the literal string `null` count as no message.** These occur 31 times in the Qwen-32B game and never in the released runs.
- **The released `llm_eval_full.json` files are untouched.** `analysis/out/judge/released_eval_sha256_before.txt` holds their hashes before the re-score.

## Cost

Total OpenAI spend was around $50 (components rounded):
- $18.81 for the 6 talk-without-action games;
- $12.41 for the 6 harm-without-agreement games;
- $16.42 for the judges, including $9.06 for the re-score of the released runs and $3.91 for the message judge on the other comms-on runs;
- $1.49 for the gpt-4.1-mini games;

The Qwen games ran on Modal GPU credits.

## Licence

MIT for the files in this repo (`LICENSE`). Upstream code and data are not covered. Court opinions quoted in `LEGAL_SOURCES.md` are public domain.
