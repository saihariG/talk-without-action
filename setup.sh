#!/usr/bin/env bash
# Clone Agrawal et al.'s code and data at the pinned commit, apply upstream_patch/,
# and link this repo's runs into its results/ folder, where the analysis expects them.
set -euo pipefail
cd "$(dirname "$0")"

UPSTREAM="${UPSTREAM:-https://github.com/andyjliu/llm-agent-collusion.git}"
COMMIT=2bb2a7e22860160d1fddb5d2e5cb460cc6ec6aff
PATCH="$PWD/upstream_patch/talk_without_action.patch"

if [ ! -d llm-agent-collusion ]; then
  git -c core.autocrlf=false clone -q "$UPSTREAM" llm-agent-collusion
fi
cd llm-agent-collusion
git -c advice.detachedHead=false checkout -q "$COMMIT"
if git apply --reverse --check "$PATCH" 2>/dev/null; then
  echo "patch already applied"
else
  git apply "$PATCH"
  echo "patch applied"
fi

mkdir -p results
for d in ../data/runs/*/; do
  name=$(basename "$d")
  ln -sfn "../../data/runs/$name" "results/$name"
done
echo "linked $(ls -d ../data/runs/*/ | wc -l | tr -d ' ') runs into llm-agent-collusion/results/"
