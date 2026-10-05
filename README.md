# Qwen-Image-Edit-2511 · RunPod Serverless worker

Một endpoint lo 6 chức năng: `enhance` (Cải thiện), `reconstruct` (Tái tạo), `colorize` (Tô màu),
`scratch` (Xóa xước), `brighten` (Làm sáng), `merge` (Kết hợp hai ảnh).
Làm sống động vẫn dùng endpoint MINIMAX-H3 hiện có.

## Bước 1 — Giải phóng worker
Tài khoản đang 20/20 workers. Vào endpoint **MINIMAX-H3 → Manage → Edit Endpoint**, giảm
**Max Workers** từ 17 xuống 14 (hoặc xoá `runpod-flux-schnell` nếu không dùng nữa).

## Bước 2 — Đưa code lên GitHub
Tạo repo private mới (vd `Qwen-Image-Edit`), đẩy **nội dung thư mục này** lên làm gốc repo
(Dockerfile nằm ở root).

## Bước 3 — Tạo endpoint
Serverless → **New Endpoint → Import GitHub Repository** → chọn repo, branch `main`,
Dockerfile path `Dockerfile`. Cấu hình:

| Mục | Giá trị |
|---|---|
| GPU | **80 GB** (A100/H100) hoặc **96 GB**. Model + text encoder ≈ 58 GB VRAM ở bf16 |
| **Model** (Cached model) | `Qwen/Qwen-Image-Edit-2511` — RunPod tải sẵn lên máy, không tính tiền lúc tải |
| Container disk | 20 GB |
| Active workers | 0 (lúc chạy thật có traffic thì cân nhắc 1 để bỏ cold start) |
| Max workers | 3 |
| Idle timeout | 60 s |
| Execution timeout | 300 s |
| FlashBoot | Bật |

Build image lần đầu mất khoảng 10–20 phút.

## Bước 4 — Test
```bat
set RUNPOD_API_KEY=rpa_xxx
set ENDPOINT_ID=abc123
pip install requests pillow
python test_client.py anh_cu.jpg colorize
python test_client.py anh_ong.jpg merge anh_toi.jpg
```
Lần gọi đầu sẽ chậm (cold start: nạp ~58 GB vào GPU, khoảng 1–3 phút). Các lần sau là vài giây.

## API
```json
POST https://api.runpod.ai/v2/{ENDPOINT_ID}/run
{ "input": {
    "feature": "colorize",
    "images": ["<base64 hoặc URL>"],
    "fast": true,
    "seed": 123
}}
```
- `fast: true` → Lightning 4 bước, nhanh ~10 lần, rẻ. `fast: false` → 40 bước, đẹp hơn (dùng cho gói Pro).
- `merge`: ảnh 1 = ảnh cũ (tổ tiên), ảnh 2 = ảnh người dùng.
- `prompt`: ghi đè prompt mặc định nếu cần.
- Kết quả: `output.image` là JPEG base64.
- Giới hạn payload của RunPod: `/run` 10 MB, `/runsync` 20 MB → app nên thu ảnh về cạnh dài ≤ 1600–2048 px trước khi gửi.

## Tinh chỉnh
- Sửa prompt trong `prompts.py` rồi push → RunPod tự build lại.
- Khi so sánh chất lượng, cố định `seed` để so công bằng giữa fast và 40 bước.
