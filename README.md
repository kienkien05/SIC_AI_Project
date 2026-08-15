# SPAS Attendance

Web hệ thống điểm danh theo thời khóa biểu. React portal gọi gateway TypeScript; gateway chỉ điều phối, còn nhận diện khuôn mặt chạy tại endpoint AI riêng.

## Chạy local

Cần Docker Desktop với Docker Compose v2.

```powershell
git clone https://github.com/kienkien05/SIC_AI_Project.git
cd SIC_AI_Project
Copy-Item .env.example .env
```

Đặt token dài, khác nhau trong `.env`:

```text
INTERNAL_SERVICE_TOKEN=<long-random-internal-token>
SESSION_SECRET=<long-random-session-secret>
FACE_AI_TOKEN=<shared-token-for-ai>
```

Chạy toàn bộ, gồm AI local:

```powershell
docker compose -f docker-compose.local.yml --profile local-ai up --build
```

Mở `http://127.0.0.1:8600`. Tài khoản seed: `SV001/sv123`, `GV001/gv123`, `ADMIN001/admin123`.

## AI trên Hugging Face

Model repository chỉ là nơi lưu checkpoint, không tự là inference API. Để chạy model trên cloud, deploy thư mục `services/face-ai` thành Docker Space theo `services/face-ai/README.md`.

Sau khi Space ở trạng thái Running, đặt URL Space vào `.env`:

```text
FACE_AI_URL=https://<tai-khoan>-spas-face-ai.hf.space
FACE_AI_TOKEN=<same-token-as-Space-secret>
```

Sau đó chạy không kèm profile local:

```powershell
docker compose -f docker-compose.local.yml up --build
```

Khi đó `ai-adapter` gửi pose, enrollment và recognition tới Hugging Face; máy local chỉ chạy portal, dữ liệu người dùng và điểm danh. Hugging Face hiện yêu cầu gói trả phí để tạo Docker Space; nếu chưa dùng gói này, chạy `--profile local-ai` thay vì giả định cloud miễn phí. Disk Docker Space cũng tạm thời, nên gallery enrollment có thể mất khi Space restart. Dùng persistent storage hoặc chuyển gallery sang database trước khi triển khai thật.

## Tính năng

- Sinh viên: thời khóa biểu, enrollment 8 frame tự chụp theo pose thẳng–trái–phải, xem lịch sử điểm danh, đổi mật khẩu.
- Giảng viên: thời khóa biểu giảng dạy, quét realtime, quét ảnh chụp, điểm danh tay.
- Admin: tài khoản, môn học, lớp học phần, xếp sinh viên, ảnh enrollment và reset khuôn mặt.
- Bảo mật: session HTTP-only, phân quyền API, một face chỉ enrollment cho một tài khoản.

## Cấu trúc

```text
frontend/              React portal
services/api-gateway/  Session, RBAC, static portal
services/identity-service/
services/attendance-service/
services/ai-adapter-service/
services/face-ai/      Docker API deploy lên Hugging Face Space
packages/              Contracts và internal-service security
```

## Backup Python

Bản portal Python cũ được giữ trong Git tag `python-portal-backup`; không nằm trong working tree React. Xem lại bằng:

```powershell
git show python-portal-backup:management_app/app.py
```

## Dừng hệ thống

```powershell
docker compose -f docker-compose.local.yml down
```
