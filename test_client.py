"""Gửi 1 ảnh lên endpoint và lưu kết quả.
Dùng:  set RUNPOD_API_KEY=...  &  set ENDPOINT_ID=...
       python test_client.py old.jpg colorize
       python test_client.py old.jpg merge me.jpg
"""
import base64, io, os, sys, time, requests
from PIL import Image, ImageOps

API_KEY = os.environ["RUNPOD_API_KEY"]
ENDPOINT = os.environ["ENDPOINT_ID"]
H = {"Authorization": f"Bearer {API_KEY}"}


def to_b64(path, max_side=1600):
    img = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    img.thumbnail((max_side, max_side))           # giữ payload dưới giới hạn 10MB của RunPod
    buf = io.BytesIO(); img.save(buf, "JPEG", quality=90)
    return base64.b64encode(buf.getvalue()).decode()


img1, feature = sys.argv[1], sys.argv[2]
images = [to_b64(img1)] + ([to_b64(sys.argv[3])] if len(sys.argv) > 3 else [])
payload = {"input": {"feature": feature, "images": images, "fast": True}}

job = requests.post(f"https://api.runpod.ai/v2/{ENDPOINT}/run", json=payload, headers=H).json()
print("job:", job)
while True:
    s = requests.get(f"https://api.runpod.ai/v2/{ENDPOINT}/status/{job['id']}", headers=H).json()
    if s["status"] in ("COMPLETED", "FAILED", "CANCELLED", "TIMED_OUT"):
        break
    print(s["status"]); time.sleep(3)

if s["status"] != "COMPLETED" or "image" not in (s.get("output") or {}):
    print(s); sys.exit(1)
out = f"out_{feature}.jpg"
open(out, "wb").write(base64.b64decode(s["output"]["image"]))
print(f"Đã lưu {out} - {s['output']['seconds']}s, seed {s['output']['seed']}")
