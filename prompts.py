# Prompt cho từng chức năng. Sửa ở đây để tinh chỉnh chất lượng, không cần đụng handler.

KEEP_ID = ("Keep the exact same people: identical facial features, face shape, "
           "expression, age, pose, clothing and composition.")

FEATURES = {
    # Cải thiện - làm nét mặt, xóa mờ, thêm chi tiết
    "enhance": {
        "images": 1,
        "prompt": ("Restore this old photo into a sharp, high-quality photograph. "
                   "Enhance and sharpen the faces, remove blur and noise, add fine natural "
                   "detail to skin, hair and fabric. " + KEEP_ID + " Photorealistic."),
    },
    # Tái tạo - chân dung hư hại nặng
    "reconstruct": {
        "images": 1,
        "prompt": ("Fully restore this heavily damaged old portrait. Repair tears, cracks, "
                   "missing areas, stains, creases and fading, reconstructing missing parts "
                   "naturally. Colorize with realistic natural colors and produce a sharp, "
                   "clean studio-quality photograph. " + KEEP_ID),
    },
    # Tô màu - ảnh đen trắng
    "colorize": {
        "images": 1,
        "prompt": ("Colorize this black and white photo with realistic, natural, "
                   "period-accurate colors and natural skin tones. Do not change any "
                   "details, faces or composition, only add color."),
    },
    # Xóa xước - trầy xước, bụi bẩn
    "scratch": {
        "images": 1,
        "prompt": ("Remove all scratches, cracks, dust, spots, stains and creases from this "
                   "old photo. Keep everything else exactly the same, including faces, "
                   "colors, lighting and composition."),
    },
    # Làm sáng - chỉnh sáng
    "brighten": {
        "images": 1,
        "prompt": ("Correct the exposure of this photo: brighten dark and underexposed areas, "
                   "recover shadow detail, balance contrast and white balance naturally. "
                   "Keep the content and faces unchanged."),
    },
    # Kết hợp hai ảnh - ảnh chung với tổ tiên (ảnh 1 = ảnh cũ, ảnh 2 = người dùng)
    "merge": {
        "images": 2,
        "prompt": ("Create a realistic modern photograph of the person from image 1 and the "
                   "person from image 2 standing side by side close together, both smiling, "
                   "in a warm softly lit living room. Restore and colorize the person from "
                   "image 1 so both look photographed together at the same time with the same "
                   "camera and lighting. Preserve both people's facial identity exactly."),
    },
}

NEGATIVE = ("blurry, low quality, distorted face, deformed, different person, extra fingers, "
            "cartoon, painting, oversaturated, watermark, text")
