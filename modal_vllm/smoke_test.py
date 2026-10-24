"""Check the Modal vLLM endpoint answers and returns parseable JSON.

Usage: python modal_vllm/smoke_test.py   (reads OPENROUTER_BASE_URL, OPENROUTER_API_KEY, MODEL from .env)
"""
import json
import os
import time
from pathlib import Path

from openai import OpenAI

ENV = Path(__file__).parent.parent / ".env"
for line in (ENV.read_text().splitlines() if ENV.exists() else []):
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

client = OpenAI(base_url=os.environ["OPENROUTER_BASE_URL"], api_key=os.environ["OPENROUTER_API_KEY"], timeout=900)
model = os.environ.get("MODEL", "Qwen/Qwen2.5-7B-Instruct")

t = time.time()
resp = client.chat.completions.create(
    model=model,
    messages=[{"role": "user", "content": 'You are a seller with cost $80. Reply ONLY with JSON: {"ask": <float>, "reason": "<one sentence>"}'}],
    temperature=0.7,
    max_completion_tokens=200,
)
text = resp.choices[0].message.content
print(f"{time.time() - t:.1f}s (includes cold start if the container was idle)")
print(text)
print("parsed:", json.loads(text.strip().strip("`").removeprefix("json")))
