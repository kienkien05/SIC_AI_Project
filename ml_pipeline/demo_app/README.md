# Dịch vụ AI điểm danh

Dịch vụ FastAPI ghép YOLO face detector (`face_best.pt`) và FaceNet recognition (`facenet_best.pt`), chạy tại cổng `8503`.

Đăng ký tự động lấy 8 ảnh hợp lệ theo bốn tư thế: `thẳng → trái → phải → thẳng` (2 ảnh/tư thế). MTCNN landmark căn chỉnh face crop trước khi tạo FaceNet embedding 512-D.

Xem [README gốc](../../README.md) để cài đầy đủ hệ thống, đặt model và tích hợp cổng học vụ.

## Chạy riêng AI service

```powershell
python -m pip install -r requirements.txt
python -m uvicorn server:app --host 127.0.0.1 --port 8503
```

Đặt biến `FACE_DETECTOR_PATH` và `FACE_RECOGNITION_PATH` nếu model không nằm trong thư mục `models/`.

## Dữ liệu cục bộ

`data/gallery.npz` và `data/enrollment_crops/` chứa embedding/ảnh khuôn mặt đã đăng ký. Các dữ liệu này cùng model bị `.gitignore` loại trừ và không được đưa lên GitHub.

## Kiểm tra nhanh

```powershell
python model_check.py
python self_check.py
```
