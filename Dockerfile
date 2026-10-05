# RunPod Serverless worker - Qwen-Image-Edit-2511
# CUDA 12.8 -> chạy được cả A100/H100 và RTX PRO 6000 (Blackwell)
FROM pytorch/pytorch:2.7.0-cuda12.8-cudnn9-runtime

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HUB_ENABLE_HF_TRANSFER=1

RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

# LoRA Lightning (4 bước, Apache 2.0) - nhỏ nên nhúng thẳng vào image
RUN python -c "from huggingface_hub import hf_hub_download; hf_hub_download('lightx2v/Qwen-Image-Edit-2511-Lightning', 'Qwen-Image-Edit-2511-Lightning-4steps-V1.0-bf16.safetensors', local_dir='/lora')"

COPY handler.py prompts.py ./

CMD ["python", "-u", "handler.py"]
