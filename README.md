# SPAS — Smart Passive Attendance System

Repository này là bản **chạy đầy đủ hệ thống**: cổng học vụ, AI nhận diện khuôn mặt, model đã train và Docker Compose. Clone về là có thể khởi động demo; notebook training, data nghiên cứu và báo cáo không nằm trong repository triển khai.

## Thành phần

| Service | Port | Vai trò |
| --- | ---: | --- |
| `portal` | `8600` | Đăng nhập theo role, lớp học, thời khóa biểu, enrollment và điểm danh |
| `ai` | `8503` | YOLO detection, MTCNN landmark alignment, FaceNet embedding/recognition |

Model runtime được lưu bằng Git LFS:

- `models/face_best.pt`: YOLO face detector.
- `models/facenet_best.pt`: FaceNet recognition 512-D đã fine-tune.

Database SQLite và dữ liệu enrollment/gallery chạy trong Docker volumes, không nằm trên GitHub.

## Yêu cầu

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) đang chạy.
- Git LFS. Cài lần đầu bằng `git lfs install`.
- Webcam và trình duyệt hiện đại để enrollment/điểm danh realtime.

## Clone và chạy

```powershell
git lfs install
git clone https://github.com/kienkien05/SIC_AI_Project.git
cd SIC_AI_Project
Copy-Item .env.example .env
docker compose up --build
```

Khi hai service có log `Application startup complete`, mở [http://127.0.0.1:8600](http://127.0.0.1:8600). Docker tự nối portal tới AI; không cần chạy hai terminal hay cấu hình đường dẫn model.

Nếu clone trước khi cài Git LFS, kéo model bằng:

```powershell
git lfs pull
```

## Tài khoản demo

- Quản trị: `ADMIN001` / `admin123`
- Giáo viên: `GV001` / `gv123`
- Sinh viên: `SV001` / `sv123`

## Luồng sử dụng

1. Đăng nhập sinh viên và mở **Tài khoản cá nhân** để đăng ký khuôn mặt.
2. Làm theo hướng dẫn `thẳng → trái → phải → thẳng`; hệ thống tự chụp 8 frame đạt điều kiện.
3. Đăng nhập giáo viên, mở lớp được phân công và bật **quét điểm danh realtime**.
4. AI phát hiện mọi khuôn mặt trong frame, căn chỉnh landmark, so embedding với gallery và portal ghi nhận sinh viên thuộc lớp đó.
5. Quản trị viên vào **Quản lý sinh viên** để xem trạng thái và reset enrollment khi cần.

## Dữ liệu persistent

| Dữ liệu | Nơi lưu | Xóa/reset |
| --- | --- | --- |
| Tài khoản, lớp và điểm danh | Docker volume `portal_data` | `docker compose down -v` |
| Face gallery và enrollment crops | Docker volume `ai_data` | `docker compose down -v` |

`docker compose down` chỉ dừng service và giữ dữ liệu. Dùng `docker compose down -v` chỉ khi muốn xóa toàn bộ dữ liệu demo.

## Cấu hình an toàn

Sửa `SPAS_SESSION_SECRET` trong `.env` trước khi đưa lên server thật. Không commit database, ảnh khuôn mặt, gallery hoặc file `.env`.

## Kiểm tra mã nguồn

```powershell
python management_app\self_check.py
python ml_pipeline\demo_app\self_check.py
```

Các lệnh self-check dùng dữ liệu local; không chạy chúng trên môi trường thật.
