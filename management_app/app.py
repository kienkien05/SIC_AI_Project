from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import re
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime
from html import escape
from pathlib import Path
from urllib.parse import quote
from urllib.error import URLError
from urllib.request import Request as UrlRequest, urlopen

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from starlette.middleware.sessions import SessionMiddleware

APP_DIR = Path(__file__).resolve().parent
DATABASE_PATH = Path(os.getenv("SPAS_DATABASE_PATH", APP_DIR / "spas.db"))
SESSION_SECRET = os.getenv("SPAS_SESSION_SECRET", "local-demo-change-before-deploy")
app = FastAPI(title="SPAS - Smart Passive Attendance System")
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET, same_site="lax", https_only=False)

ROLE_LABELS = {"admin": "Quản trị viên", "teacher": "Giảng viên", "student": "Sinh viên"}
STATUS_LABELS = {"present": "Đúng giờ", "late": "Đi muộn", "absent": "Vắng mặt", "excused": "Nghỉ có phép"}
STATUS_CLASS = {"present": "ok", "late": "late", "absent": "bad", "excused": "info"}
WEEKDAYS = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ nhật"]


@contextmanager
def database():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def password_hash(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000)
    return base64.b64encode(salt + digest).decode()


def password_matches(password: str, stored: str) -> bool:
    raw = base64.b64decode(stored.encode())
    return hmac.compare_digest(password_hash(password, raw[:16]), stored)


def valid_id(value: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9_-]{3,30}", value))


def ai_post(path: str, fields: list[tuple[str, str]], files: list[tuple[str, str, bytes]]) -> dict:
    boundary = "----SPAS" + secrets.token_hex(12)
    parts: list[bytes] = []
    for name, value in fields:
        parts.extend([f"--{boundary}".encode(), f'Content-Disposition: form-data; name="{name}"'.encode(), b"", value.encode()])
    for name, filename, content in files:
        safe_name = re.sub(r"[^A-Za-z0-9_.-]", "_", filename)
        parts.extend([f"--{boundary}".encode(), f'Content-Disposition: form-data; name="{name}"; filename="{safe_name}"'.encode(), b"Content-Type: image/jpeg", b"", content])
    parts.extend([f"--{boundary}--".encode(), b""])
    body = b"\r\n".join(parts)
    request = UrlRequest(
        f"http://127.0.0.1:8503{path}",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read())


def recognize_with_ai(image: bytes, filename: str) -> list[dict]:
    return ai_post("/api/recognize", [], [("image", filename, image)])["results"]


def enroll_with_ai(student_id: str, full_name: str, frames: list[bytes]) -> dict:
    return ai_post("/api/enroll", [("student_id", student_id), ("name", full_name)], [("frames", f"frame_{index}.jpg", frame) for index, frame in enumerate(frames, 1)])


def check_enrollment_with_ai(student_id: str, frames: list[bytes]) -> dict:
    return ai_post("/api/check-enrollment", [("student_id", student_id)], [("frames", f"frame_{index}.jpg", frame) for index, frame in enumerate(frames, 1)])


def face_pose_with_ai(image: bytes, filename: str) -> dict:
    return ai_post("/api/face-pose", [], [("image", filename, image)])


def reset_enrollment_with_ai(student_id: str) -> None:
    request = UrlRequest(f"http://127.0.0.1:8503/api/enrollment/{quote(student_id)}", method="DELETE")
    with urlopen(request, timeout=30):
        pass


def enrollment_previews_with_ai(student_id: str) -> list[str]:
    request = UrlRequest(f"http://127.0.0.1:8503/api/enrollment/{quote(student_id)}/previews")
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read())["previews"]


def record_ai_attendance(teacher_id: str, section_id: int, image: bytes, filename: str) -> dict:
    with database() as db:
        owns = db.execute("SELECT 1 FROM sections WHERE id=? AND teacher_id=?", (section_id, teacher_id)).fetchone()
    if not owns:
        raise PermissionError("Không có quyền với lớp này.")
    results = recognize_with_ai(image, filename)
    recognized_ids = {item["student_id"] for item in results if item.get("student_id")}
    marked_ids: list[str] = []
    with database() as db:
        for student_id in recognized_ids:
            enrolled = db.execute("SELECT 1 FROM enrollments WHERE section_id=? AND student_id=?", (section_id, student_id)).fetchone()
            if enrolled:
                db.execute("INSERT INTO attendance(section_id,student_id,attendance_date,status,first_seen_at,updated_by) VALUES(?,?,?,?,?,?) ON CONFLICT(section_id,student_id,attendance_date) DO UPDATE SET status=excluded.status,first_seen_at=excluded.first_seen_at,updated_by=excluded.updated_by", (section_id, student_id, date.today().isoformat(), "present", datetime.now().strftime("%H:%M:%S"), teacher_id))
                marked_ids.append(student_id)
    return {"faces": len(results), "recognized_ids": sorted(recognized_ids), "marked_ids": sorted(marked_ids)}


def seed_database() -> None:
    with database() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY, full_name TEXT NOT NULL, role TEXT NOT NULL CHECK(role IN ('admin','teacher','student')),
                password_hash TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS courses (
                code TEXT PRIMARY KEY, title TEXT NOT NULL, credits INTEGER NOT NULL DEFAULT 3
            );
            CREATE TABLE IF NOT EXISTS sections (
                id INTEGER PRIMARY KEY AUTOINCREMENT, course_code TEXT NOT NULL REFERENCES courses(code),
                teacher_id TEXT NOT NULL REFERENCES users(id), room TEXT NOT NULL, weekday INTEGER NOT NULL CHECK(weekday BETWEEN 0 AND 6),
                start_time TEXT NOT NULL, end_time TEXT NOT NULL, semester TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS enrollments (
                section_id INTEGER NOT NULL REFERENCES sections(id) ON DELETE CASCADE,
                student_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                PRIMARY KEY(section_id, student_id)
            );
            CREATE TABLE IF NOT EXISTS attendance (
                section_id INTEGER NOT NULL REFERENCES sections(id) ON DELETE CASCADE,
                student_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                attendance_date TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('present','late','absent','excused')),
                first_seen_at TEXT, updated_by TEXT NOT NULL REFERENCES users(id),
                PRIMARY KEY(section_id, student_id, attendance_date)
            );
            CREATE TABLE IF NOT EXISTS face_enrollments (
                student_id TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
                enrolled_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                reset_by TEXT REFERENCES users(id), reset_at TEXT
            );
            """
        )
        if db.execute("SELECT COUNT(*) FROM users").fetchone()[0]:
            return
        users = [
            ("ADMIN001", "Quản trị SPAS", "admin", "admin123"),
            ("GV001", "Nguyễn Minh An", "teacher", "gv123"),
            ("GV002", "Trần Thu Hà", "teacher", "gv123"),
            ("SV001", "Trương Trung Kiên", "student", "sv123"),
            ("SV002", "Lê Minh Quang", "student", "sv123"),
            ("SV003", "Nguyễn Lan Anh", "student", "sv123"),
        ]
        db.executemany("INSERT INTO users(id,full_name,role,password_hash) VALUES(?,?,?,?)", [(id_, name, role, password_hash(password)) for id_, name, role, password in users])
        db.executemany("INSERT INTO courses(code,title,credits) VALUES(?,?,?)", [("INT101", "Nhập môn Trí tuệ nhân tạo", 3), ("WEB201", "Lập trình Web", 3), ("DAT102", "Cơ sở dữ liệu", 3)])
        db.executemany(
            "INSERT INTO sections(course_code,teacher_id,room,weekday,start_time,end_time,semester) VALUES(?,?,?,?,?,?,?)",
            [("INT101", "GV001", "A2-301", 0, "07:30", "09:30", "HK1 2026-2027"), ("WEB201", "GV002", "A2-203", 2, "13:00", "15:00", "HK1 2026-2027"), ("DAT102", "GV001", "B1-105", 4, "09:45", "11:45", "HK1 2026-2027")],
        )
        db.executemany("INSERT INTO enrollments(section_id,student_id) VALUES(?,?)", [(section, student) for section in (1, 2, 3) for student in ("SV001", "SV002", "SV003")])


def user_from_request(request: Request) -> sqlite3.Row | None:
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    with database() as db:
        return db.execute("SELECT id,full_name,role FROM users WHERE id=?", (user_id,)).fetchone()


def redirect(path: str) -> RedirectResponse:
    return RedirectResponse(path, status_code=303)


def notice(request: Request) -> str:
    message = request.query_params.get("message")
    return f'<div class="notice">{escape(message)}</div>' if message else ""


def badge(status: str) -> str:
    return f'<span class="badge {STATUS_CLASS[status]}">{STATUS_LABELS[status]}</span>'


def layout(title: str, body: str, user: sqlite3.Row | None = None) -> HTMLResponse:
    navigation = ""
    header_account = ""
    pinned_notice = ""
    if user:
        links = {
            "admin": [("⌂", "/", "Tổng quan"), ("◫", "/admin/users", "Tài khoản"), ("☷", "/admin/students", "Quản lý sinh viên"), ("▦", "/admin/sections", "Môn & lớp học phần"), ("◉", "/profile", "Tài khoản cá nhân")],
            "teacher": [("⌂", "/", "Lớp giảng dạy"), ("◉", "/teacher/attendance", "Điểm danh AI"), ("◉", "/profile", "Tài khoản cá nhân")],
            "student": [("⌂", "/", "Trang chủ"), ("▣", "/student/face", "Đăng ký khuôn mặt"), ("◉", "/student/attendance", "Kết quả điểm danh"), ("◉", "/profile", "Thông tin cá nhân")],
        }[user["role"]]
        navigation = "".join(f'<a href="{href}"><i aria-hidden="true">{icon}</i>{label}</a>' for icon, href, label in links)
        with database() as db:
            enrolled = db.execute("SELECT enrolled_at FROM face_enrollments WHERE student_id=?", (user["id"],)).fetchone()
        if enrolled:
            pinned_notice = f'<div class="pinned-notice" role="status"><span aria-hidden="true">✓</span><div><strong>Đăng ký khuôn mặt thành công</strong><small>Đã xác nhận lúc {escape(enrolled["enrolled_at"][:16])}. Chỉ quản trị viên mới có thể reset.</small></div></div>'
        sidebar = f'''<aside><div class="user-brief"><span class="avatar" aria-hidden="true">{escape(user['full_name'][:1].upper())}</span><div><strong>{escape(user['full_name'])}</strong><small>{escape(user['id'])}</small></div></div><nav><span class="nav-title">HỌC VỤ</span>{navigation}</nav><div class="account"><span>{ROLE_LABELS[user['role']]} · Hệ thống điểm danh AI</span></div></aside>'''
        header_account = '''<div class="header-account"><button class="header-avatar" type="button" aria-label="Mở menu tài khoản" aria-expanded="false" aria-controls="account-menu"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg></button><div id="account-menu" class="account-dropdown" hidden><a href="/profile">Tài khoản</a><form method="post" action="/logout"><button class="dropdown-logout">Đăng xuất</button></form></div></div>'''
    else:
        sidebar = '<aside><p class="muted">Quản lý lịch học và điểm danh bằng nhận diện khuôn mặt.</p></aside>'
    body = '''<style>
        :root { --accent:#2563eb; --accent-soft:#eff6ff; }
        header, button, .button { background:#a10000; }
        nav a:hover { background:#fff1f1; color:#a10000; }
        nav a.active { background:#fff1f1; color:#a10000; font-weight:700; }
        nav a.active i { color:#a10000; }
        .header-account { position:relative; }
        .header-avatar { width:36px; height:36px; padding:7px; border-radius:50%; background:#fff; color:#4b5563; }
        .header-avatar:hover, .header-avatar:focus-visible { background:#f3f4f6; outline:2px solid #fff; outline-offset:2px; }
        .header-avatar svg { width:100%; height:100%; fill:currentColor; }
        .account-dropdown { position:absolute; z-index:10; right:0; top:calc(100% + 10px); width:150px; padding:6px; background:#fff; border:1px solid var(--line); border-radius:4px; box-shadow:0 8px 20px rgba(0,0,0,.14); }
        .account-dropdown[hidden] { display:none; }
        .account-dropdown a, .dropdown-logout { display:block; width:100%; padding:9px 10px; background:transparent; color:var(--ink); border:0; border-radius:3px; text-align:left; text-decoration:none; font:inherit; cursor:pointer; }
        .account-dropdown a:hover, .dropdown-logout:hover { background:#f3f4f6; color:#a10000; }
        .pose-cue { display:flex; align-items:center; justify-content:center; gap:14px; margin-bottom:12px; padding:10px 16px; border:2px solid #a10000; border-radius:4px; background:#fff1f1; color:#7f1d1d; }
        .pose-cue span { display:grid; place-items:center; width:48px; height:48px; border-radius:50%; background:#a10000; color:#fff; font-size:34px; line-height:1; }
        .pose-cue strong { font-size:17px; }
        .pose-cue.complete { border-color:#166534; background:#ecfdf3; color:#166534; }
        .pose-cue.complete span { background:#166534; }
        .face-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(150px,1fr)); gap:12px; }
        .face-grid img { display:block; width:100%; aspect-ratio:1; object-fit:cover; border:1px solid var(--line); border-radius:4px; }
        .pinned-notice { position:sticky; top:12px; z-index:5; display:flex; align-items:center; gap:11px; margin-bottom:16px; padding:11px 14px; border:1px solid #86efac; border-radius:4px; background:#ecfdf3; color:#166534; box-shadow:0 2px 8px rgba(22,101,52,.12); }
        .pinned-notice span { display:grid; place-items:center; width:26px; height:26px; border-radius:50%; background:#166534; color:#fff; font-weight:800; }
        .pinned-notice strong, .pinned-notice small { display:block; }
        .pinned-notice small { color:#166534; font-size:12px; }
        h1::before { content:none; display:none; }
    </style>''' + pinned_notice + body + '''<script>document.querySelectorAll('nav a').forEach(link=>{const href=link.getAttribute('href');if(href===location.pathname||(href!=='/'&&location.pathname.startsWith(href+'/')))link.classList.add('active')});const accountButton=document.querySelector('.header-avatar'),accountMenu=document.querySelector('.account-dropdown');if(accountButton&&accountMenu){const closeMenu=()=>{accountMenu.hidden=true;accountButton.setAttribute('aria-expanded','false')};accountButton.addEventListener('click',event=>{event.stopPropagation();accountMenu.hidden=!accountMenu.hidden;accountButton.setAttribute('aria-expanded',String(!accountMenu.hidden))});document.addEventListener('click',event=>{if(!event.target.closest('.header-account'))closeMenu()});document.addEventListener('keydown',event=>{if(event.key==='Escape')closeMenu()})}</script>'''
    return HTMLResponse(f'''<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)} · SPAS</title><style>
    :root{{--accent:#2563eb;--accent-soft:#eff6ff;--paper:#fff;--page:#f8fafc;--ink:#1f2937;--muted:#6b7280;--line:#dbe1e8;--success:#166534;--warning:#92400e;--danger:#b91c1c}}*{{box-sizing:border-box}}body{{margin:0;font:15px/1.5 Inter,Segoe UI,Arial,sans-serif;color:var(--ink);background:var(--page)}}.shell{{display:grid;grid-template-columns:260px 1fr;min-height:100vh}}aside{{background:var(--paper);border-right:1px solid var(--line);padding:20px 0;display:flex;flex-direction:column}}.brand{{padding:0 24px 20px;color:var(--ink);text-decoration:none;display:grid;grid-template-columns:38px 1fr;column-gap:10px;align-items:center}}.brand-mark{{grid-row:span 2;width:38px;height:38px;display:grid;place-items:center;border:1px solid var(--line);border-radius:50%;font-size:20px;color:var(--accent)}}.brand strong{{font-size:15px;letter-spacing:.02em}}.brand small{{font-size:11px;color:var(--muted)}}.user-brief{{border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:18px 24px;display:flex;align-items:center;gap:11px}}.avatar{{width:36px;height:36px;display:grid;place-items:center;border-radius:50%;background:#e5e7eb;color:#374151;font-weight:800}}.user-brief strong,.user-brief small{{display:block}}.user-brief small,.account span,.muted,.small{{color:var(--muted)}}nav{{display:grid;gap:2px;padding:18px 12px}}.nav-title{{font-size:11px;font-weight:800;color:var(--muted);padding:0 12px 8px}}nav a{{color:#4b5563;text-decoration:none;padding:10px 12px;display:flex;gap:10px;align-items:center;border-radius:4px}}nav a:hover{{background:var(--accent-soft);color:var(--accent)}}nav i{{font-style:normal;width:14px;text-align:center;color:#9ca3af}}.account{{margin-top:auto;padding:16px 24px;border-top:1px solid var(--line);display:grid;gap:8px;font-size:12px}}.link{{padding:0;background:none;border:0;color:var(--muted);text-align:left;cursor:pointer;font:inherit}}.app{{min-width:0}}header{{height:60px;background:#111827;color:#fff;padding:0 30px;display:flex;align-items:center;justify-content:space-between;gap:18px}}.portal-name{{font-size:16px;font-weight:700;letter-spacing:.02em}}.header-account{{display:flex;align-items:center;gap:9px;text-align:right;font-size:13px}}.header-account strong,.header-account small{{display:block}}.header-account small{{color:#cbd5e1;font-size:11px}}.header-dot{{font-size:13px;color:#93c5fd}}main{{padding:28px 30px;max-width:1440px;width:100%;margin:auto}}h1{{margin:0 0 5px;font-size:26px;color:var(--ink)}}h1::before{{content:'›';display:inline-grid;place-items:center;width:29px;height:29px;margin-right:8px;border-radius:50%;background:var(--accent);color:#fff;vertical-align:2px}}h2{{font-size:17px;margin:0 0 14px}}.sub{{margin:0 0 22px;color:var(--muted)}}.grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}}.card{{background:var(--paper);border:1px solid var(--line);border-radius:4px;padding:18px}}.number{{font-size:30px;font-weight:700;color:var(--accent)}}.wide{{grid-column:span 2}}.actions{{display:flex;gap:8px;flex-wrap:wrap}}button,.button{{display:inline-block;background:var(--accent);color:#fff;border:0;border-radius:4px;padding:9px 12px;text-decoration:none;font:inherit;cursor:pointer}}button.secondary,.button.secondary{{background:#f3f4f6;color:var(--ink)}}button.danger{{background:var(--danger)}}table{{width:100%;border-collapse:collapse;background:#fff;border:1px solid var(--line);border-radius:4px;overflow:hidden}}th,td{{padding:11px 12px;text-align:left;border-bottom:1px solid var(--line);vertical-align:middle}}th{{font-size:12px;color:#4b5563;background:#f8fafc;text-transform:uppercase;letter-spacing:.04em}}tr:last-child td{{border-bottom:0}}.badge{{display:inline-block;padding:3px 8px;border-radius:999px;font-size:12px;font-weight:700}}.ok{{background:#ecfdf3;color:var(--success)}}.late{{background:#fffbeb;color:var(--warning)}}.bad{{background:#fef2f2;color:var(--danger)}}.info{{background:var(--accent-soft);color:#1d4ed8}}form.stack{{display:grid;gap:10px}}input,select{{width:100%;padding:9px 10px;border:1px solid #cbd5e1;border-radius:4px;background:#fff;font:inherit}}label{{font-weight:600;font-size:13px}}.form-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}}.notice{{padding:10px 12px;background:#ecfdf3;color:var(--success);border-radius:4px;margin:0 0 16px}}.empty{{color:var(--muted);padding:18px 0}}.row{{display:flex;align-items:center;justify-content:space-between;gap:16px}}.schedule{{display:grid;gap:10px}}.session{{border-left:3px solid var(--accent);background:#fff;padding:13px 15px}}.session strong{{display:block}}.small{{font-size:12px}}.timetable{{display:grid;grid-template-columns:90px repeat(6,minmax(145px,1fr));min-width:960px;border:1px solid var(--line);border-radius:4px;overflow:hidden}}.timetable-wrap{{overflow-x:auto}}.timetable-head,.slot-time{{background:#f8fafc;border-bottom:1px solid var(--line);padding:10px 12px;font-size:12px;font-weight:700;color:#4b5563}}.timetable-head{{text-align:center}}.slot-time{{display:flex;align-items:center;justify-content:center;text-align:center}}.timetable-cell{{min-height:106px;border-left:1px solid var(--line);border-bottom:1px solid var(--line);padding:8px;background:#fff}}.timetable-cell:nth-last-child(-n+6){{border-bottom:0}}.lesson{{height:100%;border-left:3px solid var(--accent);padding:8px 9px;background:var(--accent-soft);font-size:13px}}.lesson strong,.lesson span{{display:block}}.lesson span{{color:#4b5563;font-size:12px;margin-top:3px}}.lesson-empty{{color:#cbd5e1;text-align:center;padding-top:32px;font-size:12px}}@media(max-width:800px){{.shell{{grid-template-columns:1fr}}aside{{padding:12px 0}}.brand{{padding-bottom:12px}}.user-brief{{padding:12px 24px}}nav{{grid-template-columns:repeat(2,minmax(0,1fr));padding:12px}}.nav-title{{grid-column:1/-1}}.account{{display:none}}header{{padding:0 18px}}.header-account small{{display:none}}main{{padding:20px}}.grid,.form-grid{{grid-template-columns:1fr}}.wide{{grid-column:auto}}.row{{align-items:flex-start;flex-direction:column}}table{{font-size:13px;display:block;overflow-x:auto}}}}
    </style></head><body><div class="shell">{sidebar}<div class="app"><header><div class="portal-name">CỔNG THÔNG TIN ĐÀO TẠO</div>{header_account}</header><main>{body}</main></div></div></body></html>''')


def require(request: Request, role: str | None = None) -> sqlite3.Row | RedirectResponse:
    user = user_from_request(request)
    if not user or role and user["role"] != role:
        return redirect("/login")
    return user


@app.on_event("startup")
def startup() -> None:
    seed_database()


@app.get("/login")
def login_form(request: Request) -> Response:
    if user_from_request(request):
        return redirect("/")
    return layout("Đăng nhập", f'''<section class="card" style="max-width:460px;margin:8vh auto"><h1>Đăng nhập SPAS</h1><p class="sub">Dùng MSSV, mã giảng viên hoặc mã quản trị làm tên đăng nhập.</p>{notice(request)}<form class="stack" method="post" action="/login"><label>Mã tài khoản<input name="user_id" required autofocus placeholder="VD: SV001"></label><label>Mật khẩu<input name="password" type="password" required></label><button>Đăng nhập</button></form><p class="small">Chưa có tài khoản? <a href="/register">Đăng ký bằng ID được cấp</a></p><p class="small">Demo: `ADMIN001/admin123`, `GV001/gv123`, `SV001/sv123`.</p></section>''')


@app.post("/login")
def login(request: Request, user_id: str = Form(), password: str = Form()) -> RedirectResponse:
    with database() as db:
        user = db.execute("SELECT * FROM users WHERE id=?", (user_id.strip().upper(),)).fetchone()
    if not user or not password_matches(password, user["password_hash"]):
        return redirect("/login?message=" + quote("Sai mã tài khoản hoặc mật khẩu."))
    request.session["user_id"] = user["id"]
    return redirect("/")


@app.get("/register")
def register_form(request: Request) -> HTMLResponse:
    return layout("Đăng ký", f'''<section class="card" style="max-width:520px;margin:6vh auto"><h1>Đăng ký tài khoản</h1><p class="sub">MSSV là tên đăng nhập sinh viên. Mã giảng viên là tên đăng nhập giảng viên. Tài khoản quản trị chỉ do admin tạo.</p>{notice(request)}<form class="stack" method="post" action="/register"><div class="form-grid"><label>Vai trò<select name="role"><option value="student">Sinh viên</option><option value="teacher">Giảng viên</option></select></label><label>Mã được cấp<input name="user_id" required placeholder="SV004 hoặc GV003"></label></div><label>Họ và tên<input name="full_name" required></label><label>Mật khẩu<input name="password" type="password" minlength="6" required></label><button>Tạo tài khoản</button></form><p class="small"><a href="/login">Quay lại đăng nhập</a></p></section>''')


@app.post("/register")
def register(role: str = Form(), user_id: str = Form(), full_name: str = Form(), password: str = Form()) -> RedirectResponse:
    user_id = user_id.strip().upper()
    if role not in ("student", "teacher") or not valid_id(user_id) or not full_name.strip() or len(password) < 6:
        return redirect("/register?message=" + quote("Dữ liệu không hợp lệ. Mã 3-30 ký tự, mật khẩu từ 6 ký tự."))
    with database() as db:
        try:
            db.execute("INSERT INTO users(id,full_name,role,password_hash) VALUES(?,?,?,?)", (user_id, full_name.strip(), role, password_hash(password)))
        except sqlite3.IntegrityError:
            return redirect("/register?message=" + quote("Mã tài khoản đã tồn tại."))
    return redirect("/login?message=" + quote("Đăng ký thành công. Đăng nhập bằng ID vừa tạo."))


@app.post("/logout")
def logout(request: Request) -> RedirectResponse:
    request.session.clear()
    return redirect("/login")


@app.get("/profile")
def profile(request: Request) -> Response:
    user = require(request)
    if isinstance(user, RedirectResponse): return user
    return layout("Tài khoản cá nhân", f'''<h1>Tài khoản cá nhân</h1><p class="sub">{escape(user['full_name'])} · {ROLE_LABELS[user['role']]} · {escape(user['id'])}</p>{notice(request)}<section class="card" style="max-width:560px"><h2>Đổi mật khẩu</h2><form class="stack" method="post" action="/profile/password"><label>Mật khẩu hiện tại<input name="current_password" type="password" required></label><label>Mật khẩu mới<input name="new_password" type="password" minlength="6" required></label><button>Cập nhật mật khẩu</button></form></section>''', user)


@app.post("/profile/password")
def change_password(request: Request, current_password: str = Form(), new_password: str = Form()) -> RedirectResponse:
    user = require(request)
    if isinstance(user, RedirectResponse): return user
    if len(new_password) < 6:
        return redirect("/profile?message=" + quote("Mật khẩu mới cần từ 6 ký tự."))
    with database() as db:
        stored = db.execute("SELECT password_hash FROM users WHERE id=?", (user["id"],)).fetchone()["password_hash"]
        if not password_matches(current_password, stored):
            return redirect("/profile?message=" + quote("Mật khẩu hiện tại không đúng."))
        db.execute("UPDATE users SET password_hash=? WHERE id=?", (password_hash(new_password), user["id"]))
    return redirect("/profile?message=" + quote("Đã đổi mật khẩu."))


@app.get("/")
def dashboard(request: Request) -> Response:
    user = require(request)
    if isinstance(user, RedirectResponse):
        return user
    if user["role"] == "admin":
        with database() as db:
            counts = [db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] for table in ("users", "courses", "sections")]
            teachers = db.execute("SELECT s.*,c.title,u.full_name FROM sections s JOIN courses c ON c.code=s.course_code JOIN users u ON u.id=s.teacher_id ORDER BY s.weekday,s.start_time").fetchall()
        rows = "".join(f"<tr><td>{escape(r['course_code'])}</td><td>{escape(r['title'])}</td><td>{escape(r['full_name'])}</td><td>{WEEKDAYS[r['weekday']]} · {r['start_time']}-{r['end_time']}</td><td>{escape(r['room'])}</td></tr>" for r in teachers)
        return layout("Tổng quan", f'''<h1>Điều hành hệ thống</h1><p class="sub">Quản lý tài khoản, môn học, lớp học phần và lịch dạy.</p>{notice(request)}<section class="grid"><div class="card"><div class="number">{counts[0]}</div>Tài khoản</div><div class="card"><div class="number">{counts[1]}</div>Môn học</div><div class="card"><div class="number">{counts[2]}</div>Lớp học phần</div></section><section class="card" style="margin-top:16px"><div class="row"><h2>Lịch giảng dạy đã cấu hình</h2><a class="button" href="/admin/sections">Quản lý lớp học phần</a></div><table><thead><tr><th>Mã môn</th><th>Môn học</th><th>Giảng viên</th><th>Lịch</th><th>Phòng</th></tr></thead><tbody>{rows or '<tr><td colspan="5" class="empty">Chưa có lớp học phần.</td></tr>'}</tbody></table></section>''', user)
    if user["role"] == "teacher":
        return teacher_dashboard(request, user)
    return student_dashboard(request, user)


def teacher_sections(teacher_id: str) -> list[sqlite3.Row]:
    with database() as db:
        return db.execute("SELECT s.*,c.title,COUNT(e.student_id) AS student_count FROM sections s JOIN courses c ON c.code=s.course_code LEFT JOIN enrollments e ON e.section_id=s.id WHERE s.teacher_id=? GROUP BY s.id ORDER BY s.weekday,s.start_time", (teacher_id,)).fetchall()


def teacher_dashboard(request: Request, user: sqlite3.Row) -> HTMLResponse:
    rows = teacher_sections(user["id"])
    cards = "".join(f'''<div class="session"><strong>{escape(row['course_code'])} · {escape(row['title'])}</strong><span>{WEEKDAYS[row['weekday']]} · {row['start_time']}–{row['end_time']} · {escape(row['room'])} · {row['student_count']} sinh viên</span><div class="actions" style="margin-top:8px"><a class="button" href="/teacher/section/{row['id']}">Điểm danh lớp</a></div></div>''' for row in rows)
    return layout("Lớp giảng dạy", f'''<h1>Lớp giảng dạy</h1><p class="sub">Chọn lớp để ghi nhận điểm danh. Nút AI camera mở dịch vụ YOLO + FaceNet hiện tại.</p>{notice(request)}<section class="card"><div class="schedule">{cards or '<p class="empty">Chưa được phân công lớp học phần.</p>'}</div></section>''', user)


def student_dashboard(request: Request, user: sqlite3.Row) -> HTMLResponse:
    with database() as db:
        rows = db.execute("SELECT s.*,c.title,u.full_name FROM enrollments e JOIN sections s ON s.id=e.section_id JOIN courses c ON c.code=s.course_code JOIN users u ON u.id=s.teacher_id WHERE e.student_id=? ORDER BY s.weekday,s.start_time", (user["id"],)).fetchall()
        attendance = db.execute("SELECT status,COUNT(*) AS total FROM attendance WHERE student_id=? GROUP BY status", (user["id"],)).fetchall()
    summary = {row["status"]: row["total"] for row in attendance}
    total_sessions = sum(summary.values())
    present_sessions = summary.get("present", 0)
    attendance_rate = round(present_sessions * 100 / total_sessions) if total_sessions else 0
    start_times = sorted({row["start_time"] for row in rows})
    lessons = {(row["weekday"], row["start_time"]): row for row in rows}
    timetable_rows = []
    for start_time in start_times:
        end_time = next(row["end_time"] for row in rows if row["start_time"] == start_time)
        timetable_rows.append(f'<div class="slot-time">{start_time}<br>{end_time}</div>')
        for weekday in range(6):
            lesson = lessons.get((weekday, start_time))
            if lesson:
                timetable_rows.append(f'''<div class="timetable-cell"><div class="lesson"><strong>{escape(lesson['course_code'])}</strong><span>{escape(lesson['title'])}</span><span>{escape(lesson['room'])} · GV {escape(lesson['full_name'])}</span></div></div>''')
            else:
                timetable_rows.append('<div class="timetable-cell lesson-empty">—</div>')
    headers = '<div class="timetable-head">Thời gian</div>' + ''.join(f'<div class="timetable-head">{WEEKDAYS[weekday]}</div>' for weekday in range(6))
    timetable = f'<div class="timetable-wrap"><div class="timetable">{headers}{"".join(timetable_rows)}</div></div>' if rows else '<p class="empty">Chưa được xếp lớp học phần.</p>'
    return layout("Trang chủ", f'''<h1>Trang chủ</h1><p class="sub">HK1 2026–2027 · MSSV {escape(user['id'])}</p>{notice(request)}<section class="grid"><div class="card"><div class="number">{len(rows)}</div>Học phần đang học</div><div class="card"><div class="number">{attendance_rate}%</div>Tỷ lệ điểm danh</div><div class="card"><div class="number">{summary.get('late', 0) + summary.get('absent', 0)}</div>Buổi cần lưu ý</div></section><section class="card" style="margin-top:16px"><div class="row"><h2>Thời khóa biểu tuần</h2><a href="/student/attendance">Xem điểm danh</a></div>{timetable}</section><section class="card" style="margin-top:16px"><div class="row"><div><h2>Điểm danh AI</h2><p class="small">Đăng ký khuôn mặt một lần để hệ thống xác nhận sự có mặt trong lớp.</p></div><div class="actions"><a class="button" href="/student/face">Đăng ký khuôn mặt</a><a class="button secondary" href="/student/attendance">Kết quả</a></div></div></section>''', user)


@app.get("/admin/users")
def admin_users(request: Request) -> Response:
    user = require(request, "admin")
    if isinstance(user, RedirectResponse): return user
    with database() as db: rows = db.execute("SELECT u.id,u.full_name,u.role,u.created_at,f.enrolled_at FROM users u LEFT JOIN face_enrollments f ON f.student_id=u.id ORDER BY u.role,u.id").fetchall()
    table_rows = []
    for row in rows:
        reset = "-"
        if row["role"] == "student" and row["enrolled_at"]:
            reset = f'<form method="post" action="/admin/face-reset"><input type="hidden" name="student_id" value="{escape(row["id"])}"><button class="danger">Reset khuôn mặt</button></form>'
        table_rows.append(f"<tr><td>{escape(row['id'])}</td><td>{escape(row['full_name'])}</td><td>{ROLE_LABELS[row['role']]}</td><td>{'Đã đăng ký' if row['enrolled_at'] else '-'}</td><td>{reset}</td></tr>")
    table_rows = "".join(table_rows)
    return layout("Tài khoản", f'''<h1>Tài khoản</h1><p class="sub">Sinh viên và giảng viên có thể tự đăng ký bằng ID được cấp; admin kiểm soát reset khuôn mặt.</p>{notice(request)}<section class="grid"><div class="card wide"><table><thead><tr><th>ID đăng nhập</th><th>Họ tên</th><th>Vai trò</th><th>Khuôn mặt</th><th>Quản trị</th></tr></thead><tbody>{table_rows}</tbody></table></div><div class="card"><h2>Tạo nhanh</h2><p class="small">Dùng trang đăng ký cho sinh viên và giảng viên.</p><a class="button" href="/register">Đăng ký tài khoản</a></div></section>''', user)


@app.get("/admin/students")
def admin_students(request: Request) -> Response:
    user = require(request, "admin")
    if isinstance(user, RedirectResponse): return user
    with database() as db:
        rows = db.execute("SELECT u.id,u.full_name,u.created_at,f.enrolled_at FROM users u LEFT JOIN face_enrollments f ON f.student_id=u.id WHERE u.role='student' ORDER BY u.id").fetchall()
    table_rows = "".join(f'<tr><td>{escape(row["id"])}</td><td>{escape(row["full_name"])}</td><td>{escape(row["created_at"][:10])}</td><td>{"Đã đăng ký" if row["enrolled_at"] else "Chưa đăng ký"}</td><td><a class="button secondary" href="/admin/students/{quote(row["id"])}">Xem hồ sơ</a></td></tr>' for row in rows)
    return layout("Quản lý sinh viên", f'''<h1>Quản lý sinh viên</h1><p class="sub">Mở hồ sơ để xem thông tin học tập và ảnh khuôn mặt đã enrollment.</p>{notice(request)}<section class="card"><table><thead><tr><th>MSSV</th><th>Họ tên</th><th>Tạo tài khoản</th><th>Khuôn mặt</th><th></th></tr></thead><tbody>{table_rows or '<tr><td colspan="5" class="empty">Chưa có sinh viên.</td></tr>'}</tbody></table></section>''', user)


@app.get("/admin/students/{student_id}")
def admin_student_detail(request: Request, student_id: str) -> Response:
    user = require(request, "admin")
    if isinstance(user, RedirectResponse): return user
    with database() as db:
        student = db.execute("SELECT u.id,u.full_name,u.created_at,f.enrolled_at FROM users u LEFT JOIN face_enrollments f ON f.student_id=u.id WHERE u.id=? AND u.role='student'", (student_id,)).fetchone()
        classes = db.execute("SELECT c.code,c.title,s.room,s.start_time,s.end_time FROM enrollments e JOIN sections s ON s.id=e.section_id JOIN courses c ON c.code=s.course_code WHERE e.student_id=? ORDER BY c.code", (student_id,)).fetchall()
    if not student:
        return redirect("/admin/students?message=" + quote("Không tìm thấy sinh viên."))
    previews: list[str] = []
    error = ""
    try:
        previews = enrollment_previews_with_ai(student["id"])
    except (URLError, TimeoutError, OSError):
        error = '<p class="notice">Không kết nối được AI service để tải ảnh khuôn mặt.</p>'
    images = "".join(f'<img src="data:image/jpeg;base64,{escape(preview)}" alt="Ảnh enrollment {index} của {escape(student["id"])}">' for index, preview in enumerate(previews, 1))
    class_rows = "".join(f'<tr><td>{escape(course["code"])}</td><td>{escape(course["title"])}</td><td>{escape(course["room"])}</td><td>{escape(course["start_time"])}–{escape(course["end_time"])}</td></tr>' for course in classes)
    enrollment_text = escape(student["enrolled_at"][:16]) if student["enrolled_at"] else ("Đã lưu gallery" if previews else "Chưa đăng ký")
    reset = f'''<form method="post" action="/admin/face-reset"><input type="hidden" name="student_id" value="{escape(student['id'])}"><input type="hidden" name="return_to" value="student"><button class="danger">Reset khuôn mặt</button></form>''' if student["enrolled_at"] or previews else ""
    return layout("Hồ sơ sinh viên", f'''<div class="row"><div><h1>{escape(student['full_name'])}</h1><p class="sub">MSSV {escape(student['id'])}</p></div><div class="actions"><a class="button secondary" href="/admin/students">Quay lại</a>{reset}</div></div>{notice(request)}{error}<section class="grid"><div class="card"><strong>MSSV</strong><p>{escape(student['id'])}</p></div><div class="card"><strong>Tạo tài khoản</strong><p>{escape(student['created_at'][:16])}</p></div><div class="card"><strong>Enrollment</strong><p>{enrollment_text}</p></div></section><section class="card" style="margin-top:16px"><h2>Học phần</h2><table><thead><tr><th>Mã môn</th><th>Học phần</th><th>Phòng</th><th>Thời gian</th></tr></thead><tbody>{class_rows or '<tr><td colspan="4" class="empty">Chưa được xếp lớp.</td></tr>'}</tbody></table></section><section class="card" style="margin-top:16px"><h2>Ảnh khuôn mặt đã đăng ký</h2><div class="face-grid">{images or '<p class="empty">Chưa có ảnh khuôn mặt để hiển thị.</p>'}</div></section>''', user)


@app.get("/admin/faces")
def admin_faces(request: Request) -> Response:
    user = require(request, "admin")
    if isinstance(user, RedirectResponse): return user
    with database() as db:
        rows = db.execute("SELECT u.id,u.full_name,f.enrolled_at FROM users u LEFT JOIN face_enrollments f ON f.student_id=u.id WHERE u.role='student' ORDER BY u.id").fetchall()
    table_rows = []
    for row in rows:
        action = f'<a class="button secondary" href="/admin/faces/{quote(row["id"])}">Xem ảnh</a>' if row["enrolled_at"] else "-"
        table_rows.append(f"<tr><td>{escape(row['id'])}</td><td>{escape(row['full_name'])}</td><td>{escape(row['enrolled_at'][:16]) if row['enrolled_at'] else '-'}</td><td>{action}</td></tr>")
    table_rows = "".join(table_rows)
    return layout("Dữ liệu khuôn mặt", f'''<h1>Dữ liệu khuôn mặt</h1><p class="sub">Chọn sinh viên đã enrollment để xem các ảnh crop khuôn mặt và reset khi cần.</p>{notice(request)}<section class="card"><table><thead><tr><th>MSSV</th><th>Họ tên</th><th>Đăng ký lúc</th><th></th></tr></thead><tbody>{table_rows or '<tr><td colspan="4" class="empty">Chưa có sinh viên.</td></tr>'}</tbody></table></section>''', user)


@app.get("/admin/faces/{student_id}")
def admin_face_detail(request: Request, student_id: str) -> Response:
    user = require(request, "admin")
    if isinstance(user, RedirectResponse): return user
    with database() as db:
        student = db.execute("SELECT u.id,u.full_name,f.enrolled_at FROM users u LEFT JOIN face_enrollments f ON f.student_id=u.id WHERE u.id=? AND u.role='student'", (student_id,)).fetchone()
    if not student:
        return redirect("/admin/faces?message=" + quote("Không tìm thấy sinh viên."))
    previews: list[str] = []
    error = ""
    if student["enrolled_at"]:
        try:
            previews = enrollment_previews_with_ai(student["id"])
        except (URLError, TimeoutError, OSError):
            error = '<p class="notice">Không kết nối được AI service để tải ảnh khuôn mặt.</p>'
    images = "".join(f'<img src="data:image/jpeg;base64,{escape(preview)}" alt="Ảnh enrollment {index} của {escape(student["id"])}">' for index, preview in enumerate(previews, 1))
    reset = f'''<form method="post" action="/admin/face-reset"><input type="hidden" name="student_id" value="{escape(student['id'])}"><input type="hidden" name="return_to" value="faces"><button class="danger">Reset khuôn mặt</button></form>''' if student["enrolled_at"] else ""
    return layout("Ảnh khuôn mặt", f'''<div class="row"><div><h1>{escape(student['full_name'])}</h1><p class="sub">MSSV {escape(student['id'])} · {f"Đăng ký {escape(student['enrolled_at'][:16])}" if student['enrolled_at'] else 'Chưa đăng ký khuôn mặt'}</p></div><div class="actions"><a class="button secondary" href="/admin/faces">Quay lại</a>{reset}</div></div>{notice(request)}{error}<section class="card"><h2>Ảnh enrollment</h2><div class="face-grid">{images or '<p class="empty">Chưa có ảnh khuôn mặt để hiển thị.</p>'}</div></section>''', user)


@app.post("/admin/face-reset")
def admin_face_reset(request: Request, student_id: str = Form(), return_to: str = Form("users")) -> RedirectResponse:
    admin = require(request, "admin")
    if isinstance(admin, RedirectResponse): return admin
    destination = f"/admin/students/{quote(student_id)}" if return_to == "student" else f"/admin/{'faces' if return_to == 'faces' else 'users'}"
    with database() as db:
        student = db.execute("SELECT id FROM users WHERE id=? AND role='student'", (student_id,)).fetchone()
    if not student:
        return redirect(destination + "?message=" + quote("Không tìm thấy tài khoản sinh viên."))
    try:
        reset_enrollment_with_ai(student_id)
    except (URLError, TimeoutError, OSError):
        return redirect(destination + "?message=" + quote("Không kết nối được AI service để reset gallery."))
    with database() as db:
        db.execute("DELETE FROM face_enrollments WHERE student_id=?", (student_id,))
    return redirect(destination + "?message=" + quote(f"Đã reset khuôn mặt cho {student_id}."))


@app.get("/admin/sections")
def admin_sections(request: Request) -> Response:
    user = require(request, "admin")
    if isinstance(user, RedirectResponse): return user
    with database() as db:
        courses = db.execute("SELECT * FROM courses ORDER BY code").fetchall()
        teachers = db.execute("SELECT id,full_name FROM users WHERE role='teacher' ORDER BY id").fetchall()
        students = db.execute("SELECT id,full_name FROM users WHERE role='student' ORDER BY id").fetchall()
        sections = db.execute("SELECT s.*,c.title,u.full_name,COUNT(e.student_id) AS student_count FROM sections s JOIN courses c ON c.code=s.course_code JOIN users u ON u.id=s.teacher_id LEFT JOIN enrollments e ON e.section_id=s.id GROUP BY s.id ORDER BY s.weekday,s.start_time").fetchall()
    course_options = ''.join(f'<option value="{escape(c["code"])}">{escape(c["code"])} · {escape(c["title"])}</option>' for c in courses)
    teacher_options = ''.join(f'<option value="{escape(t["id"])}">{escape(t["id"])} · {escape(t["full_name"])}</option>' for t in teachers)
    section_options = ''.join(f'<option value="{s["id"]}">{escape(s["course_code"])} · {escape(s["title"])}</option>' for s in sections)
    student_options = ''.join(f'<option value="{escape(s["id"])}">{escape(s["id"])} · {escape(s["full_name"])}</option>' for s in students)
    rows = ''.join(f'<tr><td>{escape(s["course_code"])}<br><span class="small">{escape(s["title"])}</span></td><td>{escape(s["full_name"])}</td><td>{WEEKDAYS[s["weekday"]]} {s["start_time"]}–{s["end_time"]}</td><td>{escape(s["room"])}</td><td>{s["student_count"]}</td></tr>' for s in sections)
    return layout("Môn & lớp học phần", f'''<h1>Môn học và lớp học phần</h1><p class="sub">Tạo môn, phân giảng viên và đưa sinh viên vào lớp.</p>{notice(request)}<section class="grid"><div class="card"><h2>Thêm môn học</h2><form class="stack" method="post" action="/admin/courses"><label>Mã môn<input name="code" required placeholder="ML301"></label><label>Tên môn<input name="title" required></label><label>Số tín chỉ<input name="credits" type="number" min="1" max="10" value="3"></label><button>Thêm môn</button></form></div><div class="card"><h2>Tạo lớp học phần</h2><form class="stack" method="post" action="/admin/sections"><label>Môn<select name="course_code">{course_options}</select></label><label>Giảng viên<select name="teacher_id">{teacher_options}</select></label><div class="form-grid"><label>Thứ<select name="weekday">{''.join(f'<option value="{i}">{day}</option>' for i, day in enumerate(WEEKDAYS[:6]))}</select></label><label>Phòng<input name="room" required placeholder="A2-301"></label><label>Bắt đầu<input name="start_time" type="time" value="07:30" required></label><label>Kết thúc<input name="end_time" type="time" value="09:30" required></label></div><button>Tạo lớp</button></form></div><div class="card"><h2>Xếp sinh viên</h2><form class="stack" method="post" action="/admin/enrollments"><label>Lớp<select name="section_id">{section_options}</select></label><label>Sinh viên<select name="student_id">{student_options}</select></label><button>Thêm vào lớp</button></form></div></section><section class="card" style="margin-top:16px"><h2>Danh sách lớp học phần</h2><table><thead><tr><th>Môn</th><th>Giảng viên</th><th>Lịch</th><th>Phòng</th><th>Sĩ số</th></tr></thead><tbody>{rows}</tbody></table></section>''', user)


@app.post("/admin/courses")
def add_course(request: Request, code: str = Form(), title: str = Form(), credits: int = Form()) -> RedirectResponse:
    if isinstance(require(request, "admin"), RedirectResponse): return redirect("/login")
    try:
        with database() as db: db.execute("INSERT INTO courses(code,title,credits) VALUES(?,?,?)", (code.strip().upper(), title.strip(), credits))
        message = "Đã thêm môn học."
    except sqlite3.IntegrityError: message = "Mã môn đã tồn tại."
    return redirect("/admin/sections?message=" + quote(message))


@app.post("/admin/sections")
def add_section(request: Request, course_code: str = Form(), teacher_id: str = Form(), room: str = Form(), weekday: int = Form(), start_time: str = Form(), end_time: str = Form()) -> RedirectResponse:
    if isinstance(require(request, "admin"), RedirectResponse): return redirect("/login")
    with database() as db: db.execute("INSERT INTO sections(course_code,teacher_id,room,weekday,start_time,end_time,semester) VALUES(?,?,?,?,?,?,?)", (course_code, teacher_id, room.strip(), weekday, start_time, end_time, "HK1 2026-2027"))
    return redirect("/admin/sections?message=" + quote("Đã tạo lớp học phần."))


@app.post("/admin/enrollments")
def add_enrollment(request: Request, section_id: int = Form(), student_id: str = Form()) -> RedirectResponse:
    if isinstance(require(request, "admin"), RedirectResponse): return redirect("/login")
    try:
        with database() as db: db.execute("INSERT INTO enrollments(section_id,student_id) VALUES(?,?)", (section_id, student_id))
        message = "Đã xếp sinh viên vào lớp."
    except sqlite3.IntegrityError: message = "Sinh viên đã có trong lớp này."
    return redirect("/admin/sections?message=" + quote(message))


@app.get("/teacher/attendance")
def teacher_attendance_index(request: Request) -> Response:
    user = require(request, "teacher")
    if isinstance(user, RedirectResponse): return user
    return teacher_dashboard(request, user)


@app.get("/teacher/section/{section_id}")
def teacher_section(request: Request, section_id: int) -> Response:
    user = require(request, "teacher")
    if isinstance(user, RedirectResponse): return user
    with database() as db:
        section = db.execute("SELECT s.*,c.title FROM sections s JOIN courses c ON c.code=s.course_code WHERE s.id=? AND s.teacher_id=?", (section_id, user["id"])).fetchone()
        students = db.execute("SELECT u.id,u.full_name,a.status,a.first_seen_at FROM enrollments e JOIN users u ON u.id=e.student_id LEFT JOIN attendance a ON a.section_id=e.section_id AND a.student_id=e.student_id AND a.attendance_date=? WHERE e.section_id=? ORDER BY u.id", (date.today().isoformat(), section_id)).fetchall()
    if not section: return redirect("/?message=" + quote("Không có quyền với lớp này."))
    rows = ''.join(f'''<tr data-student-id="{escape(student['id'])}"><td>{escape(student['id'])}</td><td>{escape(student['full_name'])}</td><td class="attendance-state">{badge(student['status']) if student['status'] else '<span class="small">Chưa ghi nhận</span>'}</td><td><form method="post" action="/teacher/attendance"><input type="hidden" name="section_id" value="{section_id}"><input type="hidden" name="student_id" value="{escape(student['id'])}"><select name="status">{''.join(f'<option value="{value}" {"selected" if student["status"] == value else ""}>{label}</option>' for value, label in STATUS_LABELS.items())}</select></td><td><button>Lưu</button></form></td></tr>''' for student in students)
    camera = f'''<div class="card wide"><h2>Camera lớp học · quét realtime</h2><video id="classCamera" autoplay playsinline muted style="width:100%;max-height:360px;object-fit:cover;background:#102a43;border-radius:8px;transform:scaleX(-1)"></video><canvas id="classCanvas" hidden></canvas><p id="cameraStatus" class="small">Mở camera, sau đó bắt đầu quét realtime. AI xử lý tuần tự để không tạo hàng đợi.</p><div class="actions"><button id="openCamera" type="button" class="secondary">Mở camera lớp</button><button id="startScan" type="button" disabled>Bắt đầu quét realtime</button><button id="stopScan" type="button" class="danger" disabled>Dừng quét</button></div></div><script>const video=document.querySelector('#classCamera'),canvas=document.querySelector('#classCanvas'),openButton=document.querySelector('#openCamera'),startButton=document.querySelector('#startScan'),stopButton=document.querySelector('#stopScan'),status=document.querySelector('#cameraStatus');let scanning=false,frames=0;const sleep=ms=>new Promise(resolve=>setTimeout(resolve,ms));function showPresent(ids){{ids.forEach(id=>{{const row=document.querySelector('[data-student-id="'+CSS.escape(id)+'"]');if(row)row.querySelector('.attendance-state').innerHTML='<span class="badge ok">Đúng giờ</span>'}})}}async function scanFrame(){{if(!scanning||!video.videoWidth)return;canvas.width=video.videoWidth;canvas.height=video.videoHeight;const context=canvas.getContext('2d');context.save();context.translate(canvas.width,0);context.scale(-1,1);context.drawImage(video,0,0);context.restore();const blob=await new Promise(resolve=>canvas.toBlob(resolve,'image/jpeg',.82));if(!blob){{if(scanning)setTimeout(scanFrame,1000);return}}const form=new FormData();form.append('section_id','{section_id}');form.append('image',blob,'live-frame.jpg');try{{const response=await fetch('/teacher/ai-live-frame',{{method:'POST',body:form}}),data=await response.json();if(!response.ok)throw new Error(data.detail||'Lỗi AI');frames++;showPresent(data.marked_ids||[]);status.textContent='Đang quét realtime · frame '+frames+' · thấy '+data.faces+' mặt · cập nhật '+data.marked_ids.length+' sinh viên.'}}catch(error){{status.textContent='Lỗi quét: '+error.message}}finally{{if(scanning){{await sleep(1000);scanFrame()}}}}}}openButton.onclick=async()=>{{try{{video.srcObject=await navigator.mediaDevices.getUserMedia({{video:{{facingMode:{{ideal:'environment'}},width:{{ideal:1920}},height:{{ideal:1080}}}},audio:false}});status.textContent='Camera sẵn sàng.';startButton.disabled=false}}catch(error){{status.textContent='Không mở được camera: '+error.message}}}};startButton.onclick=()=>{{scanning=true;startButton.disabled=true;stopButton.disabled=false;status.textContent='Đang quét realtime...';scanFrame()}};stopButton.onclick=()=>{{scanning=false;startButton.disabled=false;stopButton.disabled=true;status.textContent='Đã dừng quét sau '+frames+' frame.'}};</script>'''
    upload = f'''<div class="card"><h2>Tải ảnh lớp</h2><p class="small">Dùng khi ảnh snapshot đã có sẵn.</p><form class="stack" method="post" action="/teacher/ai-snapshot" enctype="multipart/form-data"><input type="hidden" name="section_id" value="{section_id}"><input name="image" type="file" accept="image/*" capture="environment" required><button>Quét ảnh</button></form></div>'''
    rules = '''<div class="card"><h2>Quy tắc nhận diện</h2><p class="small">AI chỉ ghi nhận ID đã đăng ký mặt và thuộc lớp. Unknown không tự chấm; giảng viên luôn có thể sửa tay.</p></div>'''
    return layout("Điểm danh", f'''<div class="row"><div><h1>{escape(section['course_code'])} · {escape(section['title'])}</h1><p class="sub">{WEEKDAYS[section['weekday']]} · {section['start_time']}–{section['end_time']} · {escape(section['room'])} · Ngày {date.today().strftime('%d/%m/%Y')}</p></div></div>{notice(request)}<section class="grid">{camera}{upload}{rules}</section><section class="card" style="margin-top:16px"><table><thead><tr><th>MSSV</th><th>Họ tên</th><th>Hiện tại</th><th>Trạng thái</th><th></th></tr></thead><tbody>{rows or '<tr><td colspan="5" class="empty">Lớp chưa có sinh viên.</td></tr>'}</tbody></table></section>''', user)


@app.post("/teacher/ai-snapshot")
async def ai_snapshot(request: Request, section_id: int = Form(), image: UploadFile = File()) -> RedirectResponse:
    user = require(request, "teacher")
    if isinstance(user, RedirectResponse): return user
    image_bytes = await image.read()
    if not image_bytes:
        return redirect(f"/teacher/section/{section_id}?message=" + quote("Ảnh snapshot trống."))
    try:
        result = record_ai_attendance(user["id"], section_id, image_bytes, image.filename or "snapshot.jpg")
    except PermissionError:
        return redirect("/?message=" + quote("Không có quyền với lớp này."))
    except (URLError, TimeoutError, OSError, KeyError, json.JSONDecodeError):
        return redirect(f"/teacher/section/{section_id}?message=" + quote("Không kết nối được AI service. Hãy chạy demo AI ở cổng 8503."))
    return redirect(f"/teacher/section/{section_id}?message=" + quote(f"AI nhận diện và cập nhật {len(result['marked_ids'])} sinh viên thuộc lớp."))


@app.post("/teacher/ai-live-frame")
async def ai_live_frame(request: Request, section_id: int = Form(), image: UploadFile = File()) -> dict:
    user = require(request, "teacher")
    if isinstance(user, RedirectResponse):
        raise HTTPException(401, "Hãy đăng nhập bằng tài khoản giảng viên.")
    image_bytes = await image.read()
    if not image_bytes:
        raise HTTPException(400, "Frame camera trống.")
    try:
        return record_ai_attendance(user["id"], section_id, image_bytes, image.filename or "live-frame.jpg")
    except PermissionError as error:
        raise HTTPException(403, str(error)) from error
    except (URLError, TimeoutError, OSError, KeyError, json.JSONDecodeError) as error:
        raise HTTPException(503, "Không kết nối được AI service ở cổng 8503.") from error


@app.post("/teacher/attendance")
def save_attendance(request: Request, section_id: int = Form(), student_id: str = Form(), status: str = Form()) -> RedirectResponse:
    user = require(request, "teacher")
    if isinstance(user, RedirectResponse): return user
    if status not in STATUS_LABELS: return redirect(f"/teacher/section/{section_id}")
    with database() as db:
        owns = db.execute("SELECT 1 FROM sections WHERE id=? AND teacher_id=?", (section_id, user["id"])).fetchone()
        enrolled = db.execute("SELECT 1 FROM enrollments WHERE section_id=? AND student_id=?", (section_id, student_id)).fetchone()
        if owns and enrolled:
            db.execute("INSERT INTO attendance(section_id,student_id,attendance_date,status,first_seen_at,updated_by) VALUES(?,?,?,?,?,?) ON CONFLICT(section_id,student_id,attendance_date) DO UPDATE SET status=excluded.status,first_seen_at=excluded.first_seen_at,updated_by=excluded.updated_by", (section_id, student_id, date.today().isoformat(), status, datetime.now().strftime('%H:%M:%S'), user["id"]))
    return redirect(f"/teacher/section/{section_id}?message=" + quote("Đã lưu điểm danh."))


@app.get("/student/attendance")
def student_attendance(request: Request) -> Response:
    user = require(request, "student")
    if isinstance(user, RedirectResponse): return user
    with database() as db:
        rows = db.execute("SELECT a.*,s.course_code,c.title FROM attendance a JOIN sections s ON s.id=a.section_id JOIN courses c ON c.code=s.course_code WHERE a.student_id=? ORDER BY a.attendance_date DESC", (user["id"],)).fetchall()
    body_rows = ''.join(f'<tr><td>{escape(row["attendance_date"])}</td><td>{escape(row["course_code"])} · {escape(row["title"])}</td><td>{badge(row["status"])}</td><td>{escape(row["first_seen_at"] or "-")}</td></tr>' for row in rows)
    return layout("Kết quả điểm danh", f'''<h1>Kết quả điểm danh</h1><p class="sub">Theo dõi các buổi học đã được giảng viên hoặc AI ghi nhận.</p><section class="card"><table><thead><tr><th>Ngày</th><th>Môn học</th><th>Trạng thái</th><th>Thời điểm ghi nhận</th></tr></thead><tbody>{body_rows or '<tr><td colspan="4" class="empty">Chưa có bản ghi điểm danh.</td></tr>'}</tbody></table></section>''', user)


@app.get("/student/face/legacy")
def student_face(request: Request) -> Response:
    user = require(request, "student")
    if isinstance(user, RedirectResponse): return user
    with database() as db:
        enrolled = db.execute("SELECT enrolled_at FROM face_enrollments WHERE student_id=?", (user["id"],)).fetchone()
    if enrolled:
        return layout("Đăng ký khuôn mặt", f'''<h1>Đăng ký khuôn mặt</h1><p class="sub">MSSV <strong>{escape(user['id'])}</strong></p><section class="card" style="max-width:640px"><h2>Đã khóa đăng ký khuôn mặt</h2><p>Bạn đã đăng ký khuôn mặt vào {escape(enrolled['enrolled_at'][:16])}. Mỗi tài khoản chỉ được đăng ký một lần để tránh một khuôn mặt thuộc nhiều tài khoản.</p><p class="small">Nếu cần đăng ký lại, liên hệ quản trị viên để reset khuôn mặt.</p></section>''', user)
    return layout("Đăng ký khuôn mặt", f'''<h1>Đăng ký khuôn mặt</h1><p class="sub">Dữ liệu được gắn tự động với MSSV <strong>{escape(user['id'])}</strong>. Không nhập ID khác.</p><section class="grid"><div class="card wide"><video id="video" autoplay playsinline muted style="width:100%;max-height:420px;object-fit:cover;background:#102a43;border-radius:8px;transform:scaleX(-1)"></video><canvas id="canvas" hidden></canvas><p id="status" class="small">Bấm mở camera, sau đó hệ thống sẽ chụp 12 frame trong 8 giây.</p><div class="actions"><button id="openCamera" type="button" class="secondary">Mở camera</button><button id="enroll" type="button" disabled>Đăng ký khuôn mặt</button></div></div><div class="card"><h2>Hướng dẫn</h2><p class="small">Mỗi 3 frame: nhìn thẳng, quay nhẹ trái, quay nhẹ phải, cúi nhẹ. Hệ thống chỉ nhận frame có đúng một khuôn mặt rõ.</p><p class="small">Một tài khoản chỉ đăng ký một lần. Admin phải reset nếu cần đăng ký lại.</p></div></section><script>const video=document.querySelector('#video'),canvas=document.querySelector('#canvas'),status=document.querySelector('#status'),openButton=document.querySelector('#openCamera'),enrollButton=document.querySelector('#enroll');const sleep=ms=>new Promise(resolve=>setTimeout(resolve,ms));async function openCamera(){{try{{video.srcObject=await navigator.mediaDevices.getUserMedia({{video:{{facingMode:'user',width:{{ideal:1280}},height:{{ideal:720}}}},audio:false}});status.textContent='Camera sẵn sàng.';enrollButton.disabled=false}}catch(error){{status.textContent='Không mở được camera: '+error.message}}}}function capture(){{return new Promise(resolve=>{{canvas.width=video.videoWidth;canvas.height=video.videoHeight;const context=canvas.getContext('2d');context.save();context.translate(canvas.width,0);context.scale(-1,1);context.drawImage(video,0,0);context.restore();canvas.toBlob(resolve,'image/jpeg',.9)}})}}openButton.onclick=openCamera;enrollButton.onclick=async()=>{{if(!video.videoWidth)return;enrollButton.disabled=true;openButton.disabled=true;const actions=['Nhìn thẳng','Quay nhẹ sang trái','Quay nhẹ sang phải','Cúi nhẹ rồi nhìn thẳng'],form=new FormData();for(let index=0;index<12;index++){{status.textContent=actions[Math.floor(index/3)]+' ('+(index+1)+'/12)';form.append('frames',await capture(),'frame_'+index+'.jpg');await sleep(650)}}try{{const response=await fetch('/student/face-enrollment',{{method:'POST',body:form}}),data=await response.json();status.textContent=response.ok?'Đăng ký thành công: '+data.accepted+' ảnh mặt đạt chuẩn.':'Lỗi: '+data.detail}}catch(error){{status.textContent='Lỗi kết nối: '+error.message}}finally{{enrollButton.disabled=false;openButton.disabled=false}}}};</script>''', user)


@app.get("/student/face")
def guided_student_face(request: Request) -> Response:
    user = require(request, "student")
    if isinstance(user, RedirectResponse):
        return user
    with database() as db:
        enrolled = db.execute("SELECT enrolled_at FROM face_enrollments WHERE student_id=?", (user["id"],)).fetchone()
    if enrolled:
        return layout("Đăng ký khuôn mặt", f'''<h1>Đăng ký khuôn mặt</h1><p class="sub">MSSV <strong>{escape(user['id'])}</strong></p><section class="card" style="max-width:640px"><h2>Đã khóa đăng ký khuôn mặt</h2><p>Bạn đã đăng ký khuôn mặt vào {escape(enrolled['enrolled_at'][:16])}. Mỗi tài khoản chỉ được đăng ký một lần để tránh một khuôn mặt thuộc nhiều tài khoản.</p><p class="small">Cần đăng ký lại? Liên hệ quản trị viên để reset khuôn mặt.</p></section>''', user)
    return layout("Đăng ký khuôn mặt", f'''<h1>Đăng ký khuôn mặt</h1><p class="sub">Dữ liệu tự gắn với MSSV <strong>{escape(user['id'])}</strong>. Hệ thống chỉ lưu ảnh khi pose khuôn mặt đúng.</p><section class="grid"><div class="card wide"><div id="poseCue" class="pose-cue" aria-live="polite"><span id="poseArrow" aria-hidden="true">◎</span><strong id="poseLabel">Nhìn thẳng</strong></div><video id="video" autoplay playsinline muted style="width:100%;max-height:420px;object-fit:cover;background:#111827;border-radius:4px;transform:scaleX(-1)"></video><canvas id="canvas" hidden></canvas><p id="status" class="small">Mở camera, sau đó làm theo hướng dẫn: nhìn thẳng, quay trái, quay phải, nhìn thẳng.</p><div class="actions"><button id="openCamera" type="button" class="secondary">Mở camera</button><button id="enroll" type="button" disabled>Bắt đầu đăng ký</button></div></div><div class="card"><h2>Quy trình tự chụp</h2><p class="small">Mỗi pose cần 2 frame đạt yêu cầu. Frame không đúng pose, có nhiều mặt hoặc mặt quá nhỏ sẽ bị bỏ qua.</p><p class="small">Trình tự: nhìn thẳng → quay trái → quay phải → nhìn thẳng.</p><p class="small">MTCNN 5 landmark theo dõi hướng mặt; YOLO kiểm tra chỉ có một khuôn mặt.</p></div></section><script>
const video=document.querySelector('#video'),canvas=document.querySelector('#canvas'),status=document.querySelector('#status'),openButton=document.querySelector('#openCamera'),enrollButton=document.querySelector('#enroll'),poseCue=document.querySelector('#poseCue'),poseArrow=document.querySelector('#poseArrow'),poseLabel=document.querySelector('#poseLabel');
const targets=[{{pose:'front',label:'Nhìn thẳng'}},{{pose:'left',label:'Quay nhẹ sang trái'}},{{pose:'right',label:'Quay nhẹ sang phải'}},{{pose:'front',label:'Nhìn thẳng lần cuối'}}],poseLabels={{front:'nhìn thẳng',left:'quay trái',right:'quay phải',unknown:'chưa xác định'}};
const showTarget=()=>{{const target=targets[step];poseArrow.textContent={{front:'◎',left:'←',right:'→'}}[target.pose];poseLabel.textContent=target.label;}};
let step=0,captured=0,collecting=false,frames=[];
const sleep=ms=>new Promise(resolve=>setTimeout(resolve,ms));
async function openCamera(){{try{{video.srcObject=await navigator.mediaDevices.getUserMedia({{video:{{facingMode:'user',width:{{ideal:1280}},height:{{ideal:720}}}},audio:false}});status.textContent='Camera sẵn sàng.';enrollButton.disabled=false}}catch(error){{status.textContent='Không mở được camera: '+error.message}}}}
function capture(){{return new Promise(resolve=>{{canvas.width=video.videoWidth;canvas.height=video.videoHeight;const context=canvas.getContext('2d');context.save();context.translate(canvas.width,0);context.scale(-1,1);context.drawImage(video,0,0);context.restore();canvas.toBlob(resolve,'image/jpeg',.9)}})}}
async function submitFrames(){{const form=new FormData();frames.forEach((frame,index)=>form.append('frames',frame,'pose_'+index+'.jpg'));const response=await fetch('/student/face-enrollment',{{method:'POST',body:form}}),data=await response.json();if(!response.ok)throw new Error(data.detail||'Không thể đăng ký khuôn mặt.');collecting=false;enrollButton.disabled=true;openButton.disabled=true;video.srcObject?.getTracks().forEach(track=>track.stop());poseCue.classList.add('complete');poseArrow.textContent='✓';poseLabel.textContent='Đã hoàn tất';status.textContent='Đăng ký thành công: '+data.accepted+' ảnh đạt chuẩn. Đăng ký đã được khóa.';setTimeout(()=>location.reload(),1200);}}
async function collectFrame(){{if(!collecting||!video.videoWidth)return;const target=targets[step],frame=await capture();if(!frame){{setTimeout(collectFrame,350);return}}const form=new FormData();form.append('image',frame,'pose.jpg');try{{const response=await fetch('/student/face-pose',{{method:'POST',body:form}}),data=await response.json();if(!response.ok)throw new Error(data.detail||'Lỗi theo dõi pose.');if(data.pose!==target.pose){{status.textContent='Bước '+(step+1)+'/'+targets.length+': '+target.label+' · đang thấy '+(poseLabels[data.pose]||data.pose)+'. '+(data.detail||'');setTimeout(collectFrame,350);return}}frames.push(frame);captured++;status.textContent='Bước '+(step+1)+'/'+targets.length+': '+target.label+' · đã chụp '+captured+'/2 frame.';if(captured<2){{await sleep(500);collectFrame();return}}step++;captured=0;showTarget();if(step<targets.length){{status.textContent='Tốt. Tiếp theo: '+targets[step].label+'.';await sleep(900);collectFrame();return}}status.textContent='Đủ pose hợp lệ, đang tạo enrollment...';await submitFrames()}}catch(error){{collecting=false;status.textContent='Lỗi: '+error.message;enrollButton.disabled=false;openButton.disabled=false}}}}
openButton.onclick=openCamera;
enrollButton.onclick=()=>{{if(!video.videoWidth)return;step=0;captured=0;frames=[];collecting=true;enrollButton.disabled=true;openButton.disabled=true;showTarget();status.textContent='Bước 1/4: '+targets[0].label+'. Giữ đúng hướng để hệ thống tự chụp.';collectFrame()}};
</script>''', user)


@app.post("/student/face-pose")
async def student_face_pose(request: Request, image: UploadFile = File()) -> dict:
    user = require(request, "student")
    if isinstance(user, RedirectResponse):
        raise HTTPException(401, "Hãy đăng nhập bằng tài khoản sinh viên.")
    image_bytes = await image.read()
    if not image_bytes:
        raise HTTPException(400, "Frame camera trống.")
    try:
        return face_pose_with_ai(image_bytes, image.filename or "pose.jpg")
    except (URLError, TimeoutError, OSError, KeyError, json.JSONDecodeError) as error:
        raise HTTPException(503, "Không kết nối được AI service ở cổng 8503.") from error


@app.post("/student/face-enrollment")
async def student_face_enrollment(request: Request, frames: list[UploadFile] = File()) -> dict:
    user = require(request, "student")
    if isinstance(user, RedirectResponse):
        raise HTTPException(401, "Hãy đăng nhập bằng tài khoản sinh viên.")
    with database() as db:
        if db.execute("SELECT 1 FROM face_enrollments WHERE student_id=?", (user["id"],)).fetchone():
            raise HTTPException(409, "Tài khoản đã đăng ký khuôn mặt. Chỉ admin mới có thể reset.")
    if len(frames) < 5:
        raise HTTPException(400, "Cần tối thiểu 5 frame camera.")
    frame_bytes = [await frame.read() for frame in frames]
    if any(not frame for frame in frame_bytes):
        raise HTTPException(400, "Có frame camera trống.")
    try:
        duplicate = check_enrollment_with_ai(user["id"], frame_bytes)
        if duplicate["duplicate"]:
            raise HTTPException(409, f"Khuôn mặt này đã thuộc tài khoản {duplicate['student_id']} ({duplicate['name']}).")
        result = enroll_with_ai(user["id"], user["full_name"], frame_bytes)
    except (URLError, TimeoutError, OSError, KeyError, json.JSONDecodeError) as error:
        raise HTTPException(503, "Không kết nối được AI service ở cổng 8503.") from error
    with database() as db:
        db.execute("INSERT INTO face_enrollments(student_id) VALUES(?)", (user["id"],))
    return {"accepted": result["accepted"]}
