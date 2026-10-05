"""RunPod Serverless handler - Qwen-Image-Edit-2511 (Renew / Restore Old Photos).

Input:
{
  "input": {
    "feature": "enhance | reconstruct | colorize | scratch | brighten | merge",
    "images": ["<base64 hoặc URL>", ...],   # merge cần 2 ảnh, còn lại 1 ảnh
    "prompt": "(tuỳ chọn) ghi đè prompt mặc định",
    "fast": true,        # true = Lightning 4 bước (rẻ, nhanh); false = 40 bước (đẹp hơn)
    "steps": null,       # tuỳ chọn ghi đè số bước
    "seed": null,
    "quality": 92        # chất lượng JPEG trả về
  }
}
Output: {"image": "<base64 JPEG>", "seed": int, "feature": str, "seconds": float}
"""
import base64
import io
import os
import random
import time

import requests
import runpod
import torch
from PIL import Image, ImageOps
from diffusers import QwenImageEditPlusPipeline

from prompts import FEATURES, NEGATIVE

MODEL_ID = os.getenv("MODEL_ID", "Qwen/Qwen-Image-Edit-2511")
CACHE_HUB = os.getenv("RUNPOD_HF_CACHE", "/runpod-volume/huggingface-cache/hub")
LORA_DIR = "/lora"
LORA_FILE = "Qwen-Image-Edit-2511-Lightning-4steps-V1.0-bf16.safetensors"
MAX_SIDE = int(os.getenv("MAX_INPUT_SIDE", "2048"))


def resolve_model_path() -> str:
    """Ưu tiên model đã được RunPod cache sẵn (ô 'Model' của endpoint)."""
    snaps = os.path.join(CACHE_HUB, "models--" + MODEL_ID.replace("/", "--"), "snapshots")
    if os.path.isdir(snaps):
        dirs = [os.path.join(snaps, d) for d in os.listdir(snaps)]
        dirs = [d for d in dirs if os.path.isdir(d)]
        if dirs:
            path = max(dirs, key=os.path.getmtime)
            print(f"[init] dùng cached model: {path}")
            return path
    print(f"[init] không thấy cache, tải từ Hugging Face: {MODEL_ID}")
    return MODEL_ID


# ---- Load 1 lần khi worker khởi động ----
t0 = time.time()
pipe = QwenImageEditPlusPipeline.from_pretrained(resolve_model_path(), torch_dtype=torch.bfloat16)
pipe.to("cuda")
pipe.set_progress_bar_config(disable=True)

HAS_LORA = os.path.exists(os.path.join(LORA_DIR, LORA_FILE))
if HAS_LORA:
    pipe.load_lora_weights(LORA_DIR, weight_name=LORA_FILE, adapter_name="lightning")
print(f"[init] pipeline sẵn sàng sau {time.time() - t0:.1f}s (lightning={HAS_LORA})")


def load_image(src: str) -> Image.Image:
    if src.startswith("http://") or src.startswith("https://"):
        r = requests.get(src, timeout=30)
        r.raise_for_status()
        data = r.content
    else:
        if src.startswith("data:"):
            src = src.split(",", 1)[1]
        data = base64.b64decode(src)
    img = ImageOps.exif_transpose(Image.open(io.BytesIO(data))).convert("RGB")
    if max(img.size) > MAX_SIDE:
        img.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)
    return img


def handler(job):
    inp = job.get("input") or {}
    feature = inp.get("feature", "enhance")
    if feature not in FEATURES and not inp.get("prompt"):
        return {"error": f"feature không hợp lệ: {feature}. Chọn: {list(FEATURES)}"}

    cfg = FEATURES.get(feature, {"images": 1, "prompt": ""})
    srcs = inp.get("images") or ([inp["image"]] if inp.get("image") else [])
    if len(srcs) < cfg["images"]:
        return {"error": f"'{feature}' cần {cfg['images']} ảnh, nhận {len(srcs)}"}

    try:
        images = [load_image(s) for s in srcs[: max(cfg["images"], 1)]]
    except Exception as e:
        return {"error": f"không đọc được ảnh: {e}"}

    fast = bool(inp.get("fast", True)) and HAS_LORA
    if HAS_LORA:
        pipe.enable_lora() if fast else pipe.disable_lora()

    steps = int(inp.get("steps") or (4 if fast else 40))
    seed = int(inp["seed"]) if inp.get("seed") is not None else random.randint(0, 2**31 - 1)

    t = time.time()
    with torch.inference_mode():
        out = pipe(
            image=images if len(images) > 1 else images[0],
            prompt=inp.get("prompt") or cfg["prompt"],
            negative_prompt=NEGATIVE,
            true_cfg_scale=1.0 if fast else 4.0,
            guidance_scale=1.0,
            num_inference_steps=steps,
            generator=torch.Generator("cuda").manual_seed(seed),
            num_images_per_prompt=1,
        ).images[0]

    buf = io.BytesIO()
    out.save(buf, format="JPEG", quality=int(inp.get("quality", 92)))
    return {
        "image": base64.b64encode(buf.getvalue()).decode(),
        "seed": seed,
        "feature": feature,
        "fast": fast,
        "steps": steps,
        "seconds": round(time.time() - t, 2),
    }


runpod.serverless.start({"handler": handler})
