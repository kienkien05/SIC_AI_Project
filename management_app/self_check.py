from __future__ import annotations

import os
import tempfile
from pathlib import Path

from fastapi.testclient import TestClient


def login(client: TestClient, user_id: str, password: str) -> None:
    response = client.post("/login", data={"user_id": user_id, "password": password}, follow_redirects=False)
    assert response.status_code == 303


def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        os.environ["SPAS_DATABASE_PATH"] = str(Path(directory) / "spas.db")
        import app as spas
        from app import app

        with TestClient(app) as client:
            assert client.get("/login").status_code == 200
            response = client.post("/register", data={"role": "teacher", "user_id": "GV999", "full_name": "Giảng viên mới", "password": "password123"}, follow_redirects=False)
            assert response.status_code == 303
            login(client, "GV999", "password123")
            assert "Chưa được phân công lớp học phần" in client.get("/").text
            client.post("/logout")
            login(client, "ADMIN001", "admin123")
            assert "Điều hành hệ thống" in client.get("/").text
            assert "Tài khoản" in client.get("/admin/users").text
            assert "Môn học và lớp học phần" in client.get("/admin/sections").text
            client.post("/logout")
            login(client, "GV001", "gv123")
            assert "Lớp giảng dạy" in client.get("/").text
            response = client.post("/teacher/attendance", data={"section_id": 1, "student_id": "SV001", "status": "present"}, follow_redirects=False)
            assert response.status_code == 303
            client.post("/logout")
            login(client, "SV001", "sv123")
            assert "Trang chủ" in client.get("/").text
            assert "Tỷ lệ điểm danh" in client.get("/").text
            assert "Thời khóa biểu tuần" in client.get("/").text
            assert "Đúng giờ" in client.get("/student/attendance").text
            assert "Quy trình tự chụp" in client.get("/student/face").text
            assert client.get("/student/leave").status_code == 404
            assert client.get("/admin/users", follow_redirects=False).status_code == 303
            spas.face_pose_with_ai = lambda image, filename: {"pose": "left", "confidence": 0.9, "detail": ""}
            response = client.post("/student/face-pose", files={"image": ("pose.jpg", b"fake-jpeg", "image/jpeg")})
            assert response.status_code == 200
            assert response.json()["pose"] == "left"
            spas.check_enrollment_with_ai = lambda student_id, frames: {"duplicate": False}
            spas.enroll_with_ai = lambda student_id, full_name, frames: {"accepted": len(frames)}
            response = client.post("/student/face-enrollment", files=[("frames", (f"frame_{index}.jpg", b"fake-jpeg", "image/jpeg")) for index in range(5)])
            assert response.status_code == 200
            assert response.json()["accepted"] == 5
            response = client.post("/student/face-enrollment", files=[("frames", (f"frame_{index}.jpg", b"fake-jpeg", "image/jpeg")) for index in range(5)])
            assert response.status_code == 409
            client.post("/logout")
            login(client, "ADMIN001", "admin123")
            spas.reset_enrollment_with_ai = lambda student_id: None
            response = client.post("/admin/face-reset", data={"student_id": "SV001"}, follow_redirects=False)
            assert response.status_code == 303
            client.post("/logout")
            login(client, "SV001", "sv123")
            spas.check_enrollment_with_ai = lambda student_id, frames: {"duplicate": True, "student_id": "SV002", "name": "Sinh viên khác"}
            response = client.post("/student/face-enrollment", files=[("frames", (f"frame_{index}.jpg", b"fake-jpeg", "image/jpeg")) for index in range(5)])
            assert response.status_code == 409
            response = client.post("/profile/password", data={"current_password": "sv123", "new_password": "newpass123"}, follow_redirects=False)
            assert response.status_code == 303
            client.post("/logout")
            login(client, "GV001", "gv123")
            assert client.get("/teacher/requests").status_code == 404
            spas.recognize_with_ai = lambda image, filename: [{"student_id": "SV001"}, {"student_id": "UNKNOWN"}]
            response = client.post("/teacher/ai-live-frame", data={"section_id": 1}, files={"image": ("live.jpg", b"fake-jpeg", "image/jpeg")})
            assert response.status_code == 200
            assert response.json()["faces"] == 2
            assert response.json()["marked_ids"] == ["SV001"]
    print("SPAS management self-check passed.")


if __name__ == "__main__":
    main()
