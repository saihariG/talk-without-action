"""OpenAI-compatible vLLM endpoint on Modal.

Deploy:  MODEL=Qwen/Qwen2.5-7B-Instruct modal deploy modal_vllm/vllm_serve.py
The URL printed by `modal deploy` + "/v1" goes in OPENROUTER_BASE_URL.
The endpoint needs VLLM_API_KEY (from ../.env) as a bearer token.

Cost control: the container scales to zero after SCALEDOWN seconds idle,
so credits are only spent while games are running.
"""
import os
import subprocess

import modal

# SERVE_MODEL is baked into the image so the container never picks up MODEL from .env
MODEL = os.environ.get("SERVE_MODEL") or os.environ.get("MODEL", "Qwen/Qwen2.5-7B-Instruct")
GPU = os.environ.get("GPU", "L40S")
SCALEDOWN = 300
PORT = 8000
# one app per model, so two families can be served at once for the cross-family cells
APP_NAME = "vllm-" + MODEL.split("/")[-1].lower().replace(".", "-")

image = (
    modal.Image.debian_slim(python_version="3.12")
    .uv_pip_install("vllm==0.10.1.1", "huggingface_hub[hf_transfer]<1.0")
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1", "SERVE_MODEL": MODEL})
)
hf_cache = modal.Volume.from_name("hf-cache", create_if_missing=True)
vllm_cache = modal.Volume.from_name("vllm-cache", create_if_missing=True)
env_file = os.path.join(os.path.dirname(__file__), "..", ".env")

app = modal.App(APP_NAME)


@app.function(
    image=image,
    gpu=GPU,
    scaledown_window=SCALEDOWN,
    timeout=60 * 60,
    volumes={"/root/.cache/huggingface": hf_cache, "/root/.cache/vllm": vllm_cache},
    secrets=[modal.Secret.from_dotenv(env_file)],
)
@modal.concurrent(max_inputs=32)
@modal.web_server(port=PORT, startup_timeout=15 * 60)
def serve():
    cmd = [
        "vllm", "serve", MODEL,
        "--host", "0.0.0.0",
        "--port", str(PORT),
        "--api-key", os.environ["VLLM_API_KEY"],
        "--max-model-len", "16384",
        "--served-model-name", MODEL,
    ]
    subprocess.Popen(cmd)
