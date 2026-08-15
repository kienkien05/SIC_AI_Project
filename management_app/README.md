# Cổng học vụ SPAS

Cổng học vụ Flask cho sinh viên, giáo viên và quản trị, chạy ở cổng `8600`. Cổng gọi dịch vụ AI cục bộ tại `http://127.0.0.1:8503` để đăng ký khuôn mặt và điểm danh realtime.

Xem [README gốc](../README.md) để cài đủ hai dịch vụ, chuẩn bị model và kiểm tra quy tắc dữ liệu nhạy cảm.

## Tài khoản demo

- Quản trị: `ADMIN001` / `admin123`
- Giáo viên: `GV001` / `gv123`
- Sinh viên: `SV001` / `sv123`

Đổi các tài khoản và đặt `SPAS_SESSION_SECRET` riêng trước khi triển khai.

## Chạy riêng portal

```powershell
python -m pip install -r requirements.txt
python -m uvicorn app:app --host 127.0.0.1 --port 8600
```

## Kiểm tra nhanh

```powershell
python self_check.py
```

Lệnh dùng database cục bộ `spas.db`; không chạy trên database triển khai thật.
