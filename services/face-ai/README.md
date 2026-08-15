---
title: SPAS Face AI
emoji: 👁️
colorFrom: red
colorTo: gray
sdk: docker
app_port: 7860
pinned: false
---

# SPAS Face AI

FastAPI endpoint cho face pose, enrollment và recognition của SPAS. Khi thư mục này là root của một Hugging Face Docker Space, `Dockerfile` tự mở API trên port `7860`.

## Deploy thành Hugging Face Space

1. Tạo một **Docker Space** mới, ví dụ `spas-face-ai`. Docker Space hiện yêu cầu gói trả phí của Hugging Face.
2. Từ root project, tách đúng service này rồi push sang Space:

   ```powershell
   git subtree split --prefix=services/face-ai -b hf-face-ai
   git push https://huggingface.co/spaces/<tai-khoan>/spas-face-ai hf-face-ai:main
   ```

3. Trong Space Settings, tạo secret `FACE_AI_TOKEN`. Giá trị phải giống `FACE_AI_TOKEN` ở server SPAS.
4. Nếu model repository là private, thêm secret `HF_TOKEN` với quyền read. Model public không cần token này.
5. Chờ build xong, lấy URL `https://<tai-khoan>-spas-face-ai.hf.space` và gán vào `FACE_AI_URL` trong `.env` của SPAS.

## Endpoint được adapter gọi

- `POST /api/face-pose`
- `POST /api/enroll`
- `POST /api/recognize`
- `GET /api/enrollment/{student_id}/previews`
- `DELETE /api/enrollment/{student_id}`

Mọi route AI yêu cầu header `x-spas-ai-token`. Không public token này ở frontend hoặc Git.

## Lưu ý dữ liệu

Checkpoint được tải từ repository trong `seed.json`. Gallery embedding và ảnh enrollment nằm tại `FACE_AI_DATA_DIR`; disk Docker Space có thể bị reset khi service restart. Dùng Space cho demo/model inference; muốn dữ liệu enrollment bền vững cần persistent storage hoặc gallery database riêng.
