import { createRoot } from "react-dom/client";
import { useCallback, useEffect, useRef, useState, type FormEvent, type ReactNode } from "react";
import type { Role, User } from "@spas/contracts";
import "./styles.css";

type Section = { id: number; course_code: string; title: string; room: string; weekday: number; period: number; start_time: string; end_time: string; teacher_id?: string };
type Attendance = { date: string; status: string; firstSeenAt?: string; faceImage?: string; course_code: string; title: string };
type StoredUser = User & { enrolledAt?: string };
type RosterStudent = { studentId: string; fullName: string; status?: "present" | "late" | "absent"; firstSeenAt?: string };
type Course = { code: string; title: string };
type Page = "overview" | "enrollment" | "attendance" | "scan" | "users" | "classes" | "profile";
type Pose = "front" | "left" | "right";

const weekdays = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ nhật"];
const periods = [[1, "07:00", "07:50"], [2, "07:55", "08:45"], [3, "08:50", "09:40"], [4, "09:50", "10:40"], [5, "10:45", "11:35"], [6, "11:40", "12:30"], [7, "13:30", "14:20"], [8, "14:25", "15:15"], [9, "15:20", "16:10"], [10, "16:20", "17:10"], [11, "17:15", "18:05"], [12, "18:20", "19:10"], [13, "19:15", "20:05"]] as const;
const roleLabel: Record<Role, string> = { admin: "Quản trị viên", teacher: "Giảng viên", student: "Sinh viên" };
const attendanceLabel: Record<"present" | "late" | "absent", string> = { present: "Đúng giờ", late: "Đi muộn", absent: "Vắng" };
const enrollmentSteps: Array<{ pose: Pose; label: string; arrow: string }> = [
  { pose: "front", label: "Nhìn thẳng vào camera", arrow: "↑" },
  { pose: "left", label: "Quay nhẹ sang trái", arrow: "←" },
  { pose: "right", label: "Quay nhẹ sang phải", arrow: "→" },
  { pose: "front", label: "Quay lại nhìn thẳng", arrow: "↑" },
];

async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, init);
  const body = response.status === 204 ? null : await response.json();
  if (!response.ok) throw new Error(body?.error ?? "Không thể xử lý yêu cầu.");
  return body as T;
}

function matchesSearch(query: string, ...values: Array<string | number | undefined>) { const keyword = query.trim().toLocaleLowerCase("vi-VN"); return !keyword || values.some((value) => String(value ?? "").toLocaleLowerCase("vi-VN").includes(keyword)); }
function ListSearch({ id, value, onChange, placeholder }: { id: string; value: string; onChange: (value: string) => void; placeholder: string }) { return <div className="list-search"><label className="sr-only" htmlFor={id}>{placeholder}</label><input id={id} type="search" value={value} onChange={(event) => onChange(event.target.value)} placeholder={placeholder} /></div>; }

function capture(video: HTMLVideoElement): Promise<Blob> {
  return new Promise((resolve, reject) => {
    if (!video.videoWidth) return reject(new Error("Camera chưa sẵn sàng."));
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth; canvas.height = video.videoHeight;
    const context = canvas.getContext("2d");
    if (!context) return reject(new Error("Không tạo được ảnh camera."));
    context.translate(canvas.width, 0); context.scale(-1, 1); context.drawImage(video, 0, 0);
    canvas.toBlob((blob) => blob ? resolve(blob) : reject(new Error("Không chụp được ảnh.")), "image/jpeg", 0.9);
  });
}

function stopCamera(video?: HTMLVideoElement) {
  const stream = video?.srcObject;
  if (stream instanceof MediaStream) stream.getTracks().forEach((track) => track.stop());
  if (video) video.srcObject = null;
}

function Camera({ onReady }: { onReady: (video: HTMLVideoElement | undefined) => void }) {
  const reference = useRef<HTMLVideoElement>(null);
  const [message, setMessage] = useState("");
  useEffect(() => {
    const video = reference.current;
    if (!video || !navigator.mediaDevices?.getUserMedia) { setMessage("Trình duyệt không hỗ trợ camera."); return; }
    if (!window.isSecureContext && location.hostname !== "localhost") { setMessage("Camera trên mạng LAN cần HTTPS. Mở bằng localhost hoặc cấu hình HTTPS."); return; }
    navigator.mediaDevices.getUserMedia({ video: { facingMode: "user", width: { ideal: 1280 }, height: { ideal: 720 } }, audio: false })
      .then((stream) => { video.srcObject = stream; onReady(video); })
      .catch(() => setMessage("Không mở được camera. Hãy cấp quyền và kiểm tra thiết bị."));
    return () => { onReady(undefined); (video.srcObject as MediaStream | null)?.getTracks().forEach((track) => track.stop()); };
  }, [onReady]);
  return message ? <p className="notice warning" role="alert">{message}</p> : <video className="camera" ref={reference} autoPlay muted playsInline />;
}

function Login({ onLogin }: { onLogin: (user: User) => Promise<void> }) {
  const [userId, setUserId] = useState("SV001");
  const [password, setPassword] = useState("sv123");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const submit = async (event: FormEvent) => {
    event.preventDefault(); setBusy(true); setError("");
    try { await onLogin((await api<{ user: User }>("/api/auth/login", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ userId, password }) })).user); }
    catch (cause) { setError(cause instanceof Error ? cause.message : "Đăng nhập thất bại."); }
    finally { setBusy(false); }
  };
  return <main className="login-page"><form className="login-card" onSubmit={submit}><p className="portal-name">CỔNG THÔNG TIN ĐÀO TẠO</p><h1>Đăng nhập SPAS</h1><p>Dùng MSSV, mã giảng viên hoặc mã quản trị làm tên đăng nhập.</p><label htmlFor="user-id">Mã tài khoản</label><input id="user-id" value={userId} onChange={(event) => setUserId(event.target.value)} autoComplete="username" required /><label htmlFor="password">Mật khẩu</label><input id="password" value={password} onChange={(event) => setPassword(event.target.value)} type="password" autoComplete="current-password" required /><button disabled={busy}>{busy ? "Đang đăng nhập..." : "Đăng nhập"}</button>{error && <p className="notice error" role="alert">{error}</p>}<small>Demo: SV001/sv123 · GV001/gv123 · ADMIN001/admin123</small></form></main>;
}

function Timetable({ sections, selected, onSelect }: { sections: Section[]; selected?: Section; onSelect?: (section: Section) => void }) {
  return <section className="panel timetable-panel"><div className="panel-heading"><div><h2>Thời khóa biểu tuần</h2><p>Lịch học theo ca cố định của trường.</p></div></div><div className="timetable-wrap"><div className="timetable"><div className="time-head">Ca học</div>{weekdays.map((day) => <div className="day-head" key={day}>{day}</div>)}{periods.map(([period, start, end]) => <div className="timetable-row" key={period}><div className="period"><strong>Ca {period}</strong><span>{start} – {end}</span></div>{weekdays.map((_, day) => { const section = sections.find((item) => item.weekday === day && item.period === period); return <div className="slot" key={day}>{section && (onSelect ? <button type="button" className={`lesson selectable ${selected?.id === section.id ? "selected" : ""}`} onClick={() => onSelect(section)}><b>{section.course_code}</b><span>{section.title}</span><small>{section.room}</small></button> : <article className="lesson"><b>{section.course_code}</b><span>{section.title}</span><small>{section.room}</small></article>)}</div>; })}</div>)}</div></div></section>;
}

function AttendanceHistory() {
  const [rows, setRows] = useState<Attendance[]>([]); const [error, setError] = useState(""); const [query, setQuery] = useState("");
  useEffect(() => { api<{ attendance: Attendance[] }>("/api/attendance/me").then((data) => setRows(data.attendance)).catch((cause) => setError(cause.message)); }, []);
  const filteredRows = rows.filter((row) => matchesSearch(query, row.date, row.course_code, row.title, attendanceLabel[row.status as keyof typeof attendanceLabel] ?? row.status));
  return <section className="panel"><div className="panel-heading"><div><h2>Lịch sử điểm danh</h2></div><ListSearch id="attendance-search" value={query} onChange={setQuery} placeholder="Tìm môn học, ngày, trạng thái" /></div>{error ? <p className="notice error">{error}</p> : <table><thead><tr><th>Ngày</th><th>Môn học</th><th>Trạng thái</th><th>Thời gian</th><th>Xác minh</th></tr></thead><tbody>{filteredRows.length ? filteredRows.map((row) => <tr key={`${row.date}-${row.course_code}`}><td>{row.date}</td><td><b>{row.course_code}</b><br /><small>{row.title}</small></td><td><span className={`status ${row.status}`}>{attendanceLabel[row.status as keyof typeof attendanceLabel] ?? row.status}</span></td><td>{row.firstSeenAt ? new Date(row.firstSeenAt).toLocaleTimeString("vi-VN") : "—"}</td><td>{row.faceImage ? <img className="attendance-proof" src={`data:image/jpeg;base64,${row.faceImage}`} alt={`Ảnh xác minh điểm danh ${row.course_code}`} /> : "—"}</td></tr>) : <tr><td colSpan={5} className="empty">{rows.length ? "Không tìm thấy dữ liệu phù hợp." : "Chưa có dữ liệu điểm danh."}</td></tr>}</tbody></table>}</section>;
}

function Enrollment() {
  const [video, setVideo] = useState<HTMLVideoElement>(); const [cameraEnabled, setCameraEnabled] = useState(false); const [started, setStarted] = useState(false); const [step, setStep] = useState(0); const [captured, setCaptured] = useState(0); const [message, setMessage] = useState("Bấm bật camera để bắt đầu đăng ký khuôn mặt."); const [submitting, setSubmitting] = useState(false); const [enrolledAt, setEnrolledAt] = useState<string>();
  const frames = useRef<Blob[]>([]); const inFlight = useRef(false); const finished = useRef(false);
  const current = enrollmentSteps[step] ?? enrollmentSteps.at(-1)!;
  const submitFrames = useCallback(async (items: Blob[]) => {
    setSubmitting(true); setMessage("Đủ pose hợp lệ. Đang tạo enrollment...");
    try { const form = new FormData(); items.forEach((frame, index) => form.append("frames", frame, `pose-${index + 1}.jpg`)); const result = await api<{ accepted: number }>("/api/face/enrollment", { method: "POST", body: form }); stopCamera(video); setVideo(undefined); setEnrolledAt(new Date().toISOString()); setMessage(`Đăng ký thành công: ${result.accepted} ảnh đạt chuẩn. Camera đã tắt và đăng ký đã được khóa.`); }
    catch (cause) { finished.current = false; setStarted(false); setMessage(cause instanceof Error ? cause.message : "Đăng ký thất bại."); }
    finally { setSubmitting(false); }
  }, [video]);
  const collect = useCallback(async () => {
    if (!video || !started || inFlight.current || finished.current) return;
    inFlight.current = true;
    try {
      const frame = await capture(video); const form = new FormData(); form.append("image", frame, "pose.jpg");
      const result = await api<{ pose: string; confidence: number; detail: string }>("/api/face/pose", { method: "POST", body: form });
      if (result.pose !== current.pose || result.confidence < 0.6) { setMessage(`Bước ${step + 1}/4: ${current.label}. ${result.detail || "Giữ mặt rõ trong khung."}`); return; }
      const items = [...frames.current, frame]; frames.current = items; const phaseCount = items.length - step * 2; setCaptured(phaseCount);
      if (items.length === 8) { finished.current = true; setStarted(false); await submitFrames(items); return; }
      if (phaseCount === 2) { setStep((index) => index + 1); setCaptured(0); setMessage(`Tốt. Tiếp theo: ${enrollmentSteps[step + 1].label}.`); }
      else setMessage(`Bước ${step + 1}/4: ${current.label} · đã chụp ${phaseCount}/2 ảnh.`);
    } catch (cause) { setMessage(cause instanceof Error ? cause.message : "Không theo dõi được pose."); }
    finally { inFlight.current = false; }
  }, [current.label, current.pose, started, step, submitFrames, video]);
  useEffect(() => { if (!started || !video || finished.current) return; const timer = window.setInterval(() => void collect(), 800); return () => window.clearInterval(timer); }, [collect, started, video]);
  useEffect(() => { api<{ user: StoredUser }>("/api/profile").then((data) => setEnrolledAt(data.user.enrolledAt)).catch(() => undefined); }, []);
  const toggleCamera = () => { if (cameraEnabled) { stopCamera(video); setVideo(undefined); setCameraEnabled(false); setStarted(false); frames.current = []; setStep(0); setCaptured(0); setMessage("Camera đã tắt."); } else { setCameraEnabled(true); setMessage("Đang mở camera. Hãy cấp quyền nếu trình duyệt yêu cầu."); } };
  const begin = () => { frames.current = []; finished.current = false; setStep(0); setCaptured(0); setStarted(true); setMessage("Bước 1/4: Nhìn thẳng vào camera. AI sẽ tự chụp khi pose đúng."); };
  if (enrolledAt) return <section className="panel locked-enrollment"><h2>Đăng ký khuôn mặt thành công</h2><p>Camera đã tắt. Bạn đã đăng ký khuôn mặt vào {new Date(enrolledAt).toLocaleString("vi-VN")}.</p><p>Mỗi tài khoản chỉ được đăng ký một lần để tránh một khuôn mặt thuộc nhiều tài khoản. Muốn đăng ký lại, liên hệ quản trị viên để reset.</p></section>;
  return <section className="panel enrollment"><div className="panel-heading"><div><h2>Đăng ký khuôn mặt</h2><p>Mỗi tài khoản chỉ được đăng ký một lần; AI tự lấy 8 frame đạt chuẩn.</p></div><span className="tag">AI enrollment</span></div><button className={`camera-toggle ${cameraEnabled ? "active" : ""}`} disabled={submitting} onClick={toggleCamera}>{cameraEnabled ? "● Camera đang bật — bấm để tắt" : "Bật camera đăng ký khuôn mặt"}</button>{cameraEnabled && <><div className={`pose-cue ${finished.current ? "complete" : ""}`}><span aria-hidden="true">{finished.current ? "✓" : current.arrow}</span><div><strong>{finished.current ? "Đã hoàn tất" : current.label}</strong><small>Bước {Math.min(step + 1, 4)}/4 · {captured}/2 ảnh</small></div></div><div className="pose-guide">{enrollmentSteps.map((item, index) => <span className={index === step ? "current" : index < step ? "done" : ""} key={`${item.pose}-${index}`}>{index + 1}. {item.label}</span>)}</div><Camera onReady={setVideo} /><button disabled={!video || started || submitting || finished.current} onClick={begin}>{submitting ? "Đang đăng ký..." : started ? "Đang theo dõi pose..." : finished.current ? "Đã đăng ký khuôn mặt" : "Bắt đầu đăng ký khuôn mặt"}</button></>}<p className="notice" aria-live="polite">{message}</p></section>;
}

function TeacherScan({ sections }: { sections: Section[] }) {
  const [selected, setSelected] = useState<Section>(); const [video, setVideo] = useState<HTMLVideoElement>(); const [message, setMessage] = useState("Chọn một lớp học phần rồi mở camera để quét điểm danh."); const [busy, setBusy] = useState(false); const [scanning, setScanning] = useState(false); const [roster, setRoster] = useState<RosterStudent[]>([]); const [rosterQuery, setRosterQuery] = useState(""); const scanInFlight = useRef(false);
  const loadRoster = useCallback(async () => { if (!selected) return; const data = await api<{ students: RosterStudent[] }>(`/api/sections/${selected.id}/students`); setRoster(data.students); }, [selected]);
  useEffect(() => { setScanning(false); setRoster([]); if (selected) void loadRoster().catch((cause) => setMessage(cause.message)); }, [loadRoster, selected]);
  const scanImage = useCallback(async (image: Blob) => { if (!selected || scanInFlight.current) return; scanInFlight.current = true; setBusy(true); try { const form = new FormData(); form.append("image", image, "classroom.jpg"); const result = await api<{ faces: number; markedIds: string[] }>(`/api/sections/${selected.id}/recognize`, { method: "POST", body: form }); setMessage(`Phát hiện ${result.faces} khuôn mặt. Đã ghi nhận: ${result.markedIds.join(", ") || "không có"}.`); await loadRoster(); } catch (cause) { setMessage(cause instanceof Error ? cause.message : "Quét thất bại."); } finally { scanInFlight.current = false; setBusy(false); } }, [loadRoster, selected]);
  const scan = useCallback(async () => { if (!video) return; await scanImage(await capture(video)); }, [scanImage, video]);
  useEffect(() => { if (!scanning) return; void scan(); const timer = window.setInterval(() => void scan(), 1500); return () => window.clearInterval(timer); }, [scan, scanning]);
  const mark = async (studentId: string, status: RosterStudent["status"]) => { if (!selected || !status) return; try { await api("/api/attendance", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ sectionId: selected.id, studentId, status }) }); await loadRoster(); } catch (cause) { setMessage(cause instanceof Error ? cause.message : "Không lưu được điểm danh."); } };
  const filteredRoster = roster.filter((student) => matchesSearch(rosterQuery, student.studentId, student.fullName, student.status ? attendanceLabel[student.status] : "Chưa điểm danh"));
  return <div className="stack"><Timetable sections={sections} selected={selected} onSelect={setSelected} /><section className="panel scan"><div className="panel-heading"><div><h2>{selected ? `${selected.course_code} · ${selected.title}` : "Chọn lớp để quét"}</h2><p>{selected ? `${selected.room} · ${selected.start_time} – ${selected.end_time}` : message}</p></div><span className="tag">Camera trực tiếp</span></div><Camera onReady={setVideo} /><div className="actions"><button disabled={!selected || !video || busy} onClick={() => void scan()}>{busy ? "Đang nhận diện..." : "Quét một frame"}</button><button className="secondary" disabled={!selected || !video} onClick={() => setScanning((value) => !value)}>{scanning ? "Dừng quét realtime" : "Bắt đầu quét realtime"}</button><label className="upload-image">Quét ảnh chụp<input type="file" accept="image/jpeg,image/png" disabled={!selected || busy} onChange={(event) => { const image = event.currentTarget.files?.[0]; if (image) void scanImage(image); event.currentTarget.value = ""; }} /></label></div><p className="notice" aria-live="polite">{scanning ? `Đang quét realtime. ${message}` : message}</p></section>{selected && <section className="panel roster"><div className="panel-heading"><div><h2>Danh sách điểm danh</h2><p>Chưa điểm danh là trạng thái chưa có bản ghi; AI sẽ tự phân loại khi nhận diện.</p></div><ListSearch id="roster-search" value={rosterQuery} onChange={setRosterQuery} placeholder="Tìm MSSV, họ tên, trạng thái" /></div><table><thead><tr><th>MSSV</th><th>Họ tên</th><th>Trạng thái</th><th>Ghi nhận</th></tr></thead><tbody>{filteredRoster.length ? filteredRoster.map((student) => <tr key={student.studentId}><td>{student.studentId}</td><td>{student.fullName}</td><td><select value={student.status ?? ""} onChange={(event) => void mark(student.studentId, event.target.value as RosterStudent["status"])}><option value="">Chưa điểm danh</option><option value="present">Đúng giờ</option><option value="late">Đi muộn</option><option value="absent">Vắng</option></select></td><td>{student.firstSeenAt ? new Date(student.firstSeenAt).toLocaleTimeString("vi-VN") : "—"}</td></tr>) : <tr><td colSpan={4} className="empty">{roster.length ? "Không tìm thấy sinh viên phù hợp." : "Lớp chưa có sinh viên."}</td></tr>}</tbody></table></section>}</div>;
}

function Users() {
  const [users, setUsers] = useState<StoredUser[]>([]); const [selected, setSelected] = useState<StoredUser>(); const [previews, setPreviews] = useState<string[]>([]); const [sections, setSections] = useState<Section[]>([]); const [message, setMessage] = useState(""); const [query, setQuery] = useState("");
  const load = useCallback(async () => { const data = await api<{ users: StoredUser[] }>("/api/users"); setUsers(data.users); }, []);
  useEffect(() => { void load().catch((cause) => setMessage(cause.message)); }, [load]);
  useEffect(() => { if (!selected || selected.role !== "student") return; Promise.all([api<{ previews: string[] }>(`/api/face/enrollment/${selected.id}/previews`), api<{ sections: Section[] }>(`/api/users/${selected.id}/sections`)]).then(([faces, classes]) => { setPreviews(faces.previews); setSections(classes.sections); }).catch((cause) => setMessage(cause.message)); }, [selected]);
  const create = async (event: FormEvent<HTMLFormElement>) => { event.preventDefault(); const form = new FormData(event.currentTarget); try { await api("/api/users", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ id: form.get("id"), fullName: form.get("fullName"), role: form.get("role"), password: form.get("password") }) }); event.currentTarget.reset(); await load(); setMessage("Đã tạo tài khoản."); } catch (cause) { setMessage(cause instanceof Error ? cause.message : "Không tạo được tài khoản."); } };
  const reset = async () => { if (!selected) return; try { await api(`/api/face/enrollment/${selected.id}`, { method: "DELETE" }); setSelected({ ...selected, enrolledAt: undefined }); setPreviews([]); await load(); setMessage("Đã reset khuôn mặt. Sinh viên có thể đăng ký lại."); } catch (cause) { setMessage(cause instanceof Error ? cause.message : "Không reset được khuôn mặt."); } };
  const students = users.filter((item) => item.role === "student"); const filteredStudents = students.filter((student) => matchesSearch(query, student.id, student.fullName, student.enrolledAt ? "Đã đăng ký" : "Chưa đăng ký"));
  return <div className="stack">
    <section className="panel admin-form"><div className="panel-heading"><div><h2>Tạo tài khoản</h2><p>Admin tạo tài khoản sinh viên hoặc giảng viên.</p></div></div><form className="inline-form" onSubmit={create}><input name="id" placeholder="Mã được cấp" required /><input name="fullName" placeholder="Họ và tên" required /><select name="role" defaultValue="student"><option value="student">Sinh viên</option><option value="teacher">Giảng viên</option></select><input name="password" type="password" minLength={6} placeholder="Mật khẩu" required /><button>Tạo tài khoản</button></form></section>
    <section className="panel"><div className="panel-heading"><div><h2>Quản lý sinh viên</h2><p>Mở hồ sơ để xem lớp học và ảnh enrollment.</p></div><ListSearch id="students-search" value={query} onChange={setQuery} placeholder="Tìm MSSV, họ tên, trạng thái mặt" /></div><table><thead><tr><th>MSSV</th><th>Họ tên</th><th>Khuôn mặt</th><th></th></tr></thead><tbody>{filteredStudents.length ? filteredStudents.map((item) => <tr key={item.id}><td><b>{item.id}</b></td><td>{item.fullName}</td><td>{item.enrolledAt ? "Đã đăng ký" : "Chưa đăng ký"}</td><td><button className="secondary small-button" onClick={() => setSelected(item)}>Hồ sơ</button></td></tr>) : <tr><td colSpan={4} className="empty">{students.length ? "Không tìm thấy sinh viên phù hợp." : "Chưa có sinh viên."}</td></tr>}</tbody></table></section>
    {selected ? <section className="panel student-detail"><div className="panel-heading"><div><h2>{selected.fullName}</h2><p>{selected.id} · {selected.enrolledAt ? `Đã đăng ký ${new Date(selected.enrolledAt).toLocaleString("vi-VN")}` : "Chưa đăng ký khuôn mặt"}</p></div><div className="actions"><button className="secondary" onClick={() => setSelected(undefined)}>Đóng</button>{selected.enrolledAt ? <button onClick={() => void reset()}>Reset khuôn mặt</button> : null}</div></div><div className="detail-grid"><article><h3>Học phần</h3>{sections.length ? sections.map((section) => <p key={section.id}><b>{section.course_code}</b> · {section.title}<br /><small>{weekdays[section.weekday]} · Ca {section.period} · {section.room}</small></p>) : <p>Chưa được xếp lớp.</p>}</article><article><h3>Ảnh khuôn mặt đã đăng ký</h3>{previews.length ? <div className="face-grid">{previews.map((image, index) => <img key={index} src={`data:image/jpeg;base64,${image}`} alt={`Khuôn mặt enrollment ${index + 1}`} />)}</div> : <p>Chưa có ảnh khuôn mặt để hiển thị.</p>}</article></div></section> : null}
    {message && <p className="notice" role="status">{message}</p>}
  </div>;
}

function AdminClasses() {
  const [courses, setCourses] = useState<Course[]>([]); const [users, setUsers] = useState<StoredUser[]>([]); const [sections, setSections] = useState<Section[]>([]); const [message, setMessage] = useState(""); const [query, setQuery] = useState("");
  const load = useCallback(async () => { const [courseData, userData, sectionData] = await Promise.all([api<{ courses: Course[] }>("/api/courses"), api<{ users: StoredUser[] }>("/api/users"), api<{ sections: Section[] }>("/api/sections")]); setCourses(courseData.courses); setUsers(userData.users); setSections(sectionData.sections); }, []);
  useEffect(() => { void load().catch((cause) => setMessage(cause.message)); }, [load]);
  const submit = (path: string) => async (event: FormEvent<HTMLFormElement>) => { event.preventDefault(); const form = new FormData(event.currentTarget); const body: Record<string, string | number> = {}; form.forEach((value, key) => { body[key] = String(value); }); if (body.weekday) body.weekday = Number(body.weekday); if (body.period) body.period = Number(body.period); try { await api(path, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) }); event.currentTarget.reset(); await load(); setMessage("Đã lưu dữ liệu."); } catch (cause) { setMessage(cause instanceof Error ? cause.message : "Không thể lưu dữ liệu."); } };
  const teachers = users.filter((item) => item.role === "teacher"); const students = users.filter((item) => item.role === "student"); const filteredSections = sections.filter((section) => matchesSearch(query, section.course_code, section.title, section.room, weekdays[section.weekday], `Ca ${section.period}`, section.start_time, section.end_time, users.find((item) => item.id === section.teacher_id)?.fullName, section.teacher_id));
  return <div className="stack"><section className="three-forms"><form className="panel compact-form" onSubmit={submit("/api/courses")}><h2>Thêm môn học</h2><input name="code" placeholder="Mã môn" required /><input name="title" placeholder="Tên môn" required /><button>Thêm môn</button></form><form className="panel compact-form" onSubmit={submit("/api/sections")}><h2>Tạo lớp học phần</h2><select name="courseCode" required defaultValue=""><option value="" disabled>Chọn môn</option>{courses.map((course) => <option key={course.code} value={course.code}>{course.code} · {course.title}</option>)}</select><select name="teacherId" required defaultValue=""><option value="" disabled>Chọn giảng viên</option>{teachers.map((teacher) => <option key={teacher.id} value={teacher.id}>{teacher.id} · {teacher.fullName}</option>)}</select><input name="room" placeholder="Phòng học" required /><select name="weekday" defaultValue="0">{weekdays.map((day, index) => <option key={day} value={index}>{day}</option>)}</select><select name="period" defaultValue="1">{periods.map(([period, start, end]) => <option key={period} value={period}>Ca {period} · {start}–{end}</option>)}</select><button>Tạo lớp</button></form><form className="panel compact-form" onSubmit={(event) => { event.preventDefault(); const form = new FormData(event.currentTarget); void api(`/api/sections/${form.get("sectionId")}/enrollments`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ studentId: form.get("studentId") }) }).then(() => { event.currentTarget.reset(); setMessage("Đã xếp sinh viên vào lớp."); }).catch((cause) => setMessage(cause.message)); }}><h2>Xếp sinh viên</h2><select name="sectionId" defaultValue="" required><option value="" disabled>Chọn lớp</option>{sections.map((section) => <option key={section.id} value={section.id}>{section.course_code} · {section.room}</option>)}</select><select name="studentId" defaultValue="" required><option value="" disabled>Chọn sinh viên</option>{students.map((student) => <option key={student.id} value={student.id}>{student.id} · {student.fullName}</option>)}</select><button>Thêm vào lớp</button></form></section><section className="panel"><div className="panel-heading"><div><h2>Danh sách lớp học phần</h2><p>Ca học tự điền theo thời khóa biểu của trường.</p></div><ListSearch id="sections-search" value={query} onChange={setQuery} placeholder="Tìm môn, giảng viên, phòng, ca" /></div><table><thead><tr><th>Môn</th><th>Giảng viên</th><th>Lịch</th><th>Phòng</th></tr></thead><tbody>{filteredSections.length ? filteredSections.map((section) => <tr key={section.id}><td><b>{section.course_code}</b><br /><small>{section.title}</small></td><td>{users.find((item) => item.id === section.teacher_id)?.fullName ?? section.teacher_id}</td><td>{weekdays[section.weekday]} · Ca {section.period}<br /><small>{section.start_time} – {section.end_time}</small></td><td>{section.room}</td></tr>) : <tr><td colSpan={4} className="empty">{sections.length ? "Không tìm thấy lớp học phần phù hợp." : "Chưa có lớp học phần."}</td></tr>}</tbody></table></section>{message && <p className="notice" role="status">{message}</p>}</div>;
}

function Profile() {
  const [message, setMessage] = useState(""); const submit = async (event: FormEvent<HTMLFormElement>) => { event.preventDefault(); const form = new FormData(event.currentTarget); try { await api("/api/profile/password", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ currentPassword: form.get("currentPassword"), newPassword: form.get("newPassword") }) }); event.currentTarget.reset(); setMessage("Đã cập nhật mật khẩu."); } catch (cause) { setMessage(cause instanceof Error ? cause.message : "Không đổi được mật khẩu."); } };
  return <section className="panel profile"><h2>Tài khoản cá nhân</h2><p>Đổi mật khẩu của phiên đăng nhập hiện tại.</p><form className="compact-form password-form" onSubmit={submit}><label htmlFor="current-password">Mật khẩu hiện tại</label><input id="current-password" name="currentPassword" type="password" required /><label htmlFor="new-password">Mật khẩu mới</label><input id="new-password" name="newPassword" type="password" minLength={6} required /><button>Cập nhật mật khẩu</button></form>{message && <p className="notice" role="status">{message}</p>}</section>;
}

function Overview({ user, sections }: { user: User; sections: Section[] }) {
  const next = sections[0];
  return <div><h1>Trang chủ</h1><p className="sub">HK1 2026–2027 · {roleLabel[user.role]} {user.id}</p><section className="grid"><article className="card"><div className="number">{sections.length}</div>{user.role === "teacher" ? "Lớp giảng dạy" : user.role === "admin" ? "Lớp học phần" : "Học phần đang học"}</article><article className="card"><div className="number">{next ? `Ca ${next.period}` : "—"}</div>Ca học gần nhất</article><article className="card"><div className="number">{next?.room ?? "—"}</div>Phòng học gần nhất</article></section><Timetable sections={sections} /></div>;
}

function App() {
  const [user, setUser] = useState<User>(); const [sections, setSections] = useState<Section[]>([]); const [page, setPage] = useState<Page>("overview"); const [loading, setLoading] = useState(true); const [accountOpen, setAccountOpen] = useState(false);
  const load = async (current: User) => { const data = await api<{ sections: Section[] }>("/api/sections"); setUser(current); setSections(data.sections); setPage("overview"); };
  useEffect(() => { api<{ user: User | null }>("/api/auth/me").then((data) => data.user ? load(data.user) : undefined).catch(() => undefined).finally(() => setLoading(false)); }, []);
  if (loading) return <main className="loading">Đang tải cổng học vụ...</main>;
  if (!user) return <Login onLogin={load} />;
  const logout = async () => { await api("/api/auth/logout", { method: "POST" }); setUser(undefined); setSections([]); setAccountOpen(false); };
  const nav: Array<[Page, string]> = user.role === "student" ? [["overview", "Trang chủ"], ["enrollment", "Đăng ký khuôn mặt"], ["attendance", "Lịch sử điểm danh"], ["profile", "Tài khoản cá nhân"]] : user.role === "teacher" ? [["overview", "Tổng quan"], ["scan", "Quét điểm danh"], ["profile", "Tài khoản cá nhân"]] : [["overview", "Tổng quan"], ["users", "Quản lý sinh viên"], ["classes", "Môn & lớp học phần"], ["profile", "Tài khoản cá nhân"]];
  let content: ReactNode = <Overview user={user} sections={sections} />;
  if (page === "enrollment") content = <Enrollment />;
  if (page === "attendance") content = <AttendanceHistory />;
  if (page === "scan") content = <TeacherScan sections={sections} />;
  if (page === "users") content = <Users />;
  if (page === "classes") content = <AdminClasses />;
  if (page === "profile") content = <Profile />;
  return <div className="app-shell"><aside><div className="user-brief"><div className="avatar">{user.fullName.slice(0, 1)}</div><div><strong>{user.fullName}</strong><small>{roleLabel[user.role]} · {user.id}</small></div></div><nav aria-label="Điều hướng chính"><span className="nav-title">CHỨC NĂNG</span>{nav.map(([id, label]) => <button key={id} className={page === id ? "active" : ""} onClick={() => setPage(id)}>{label}</button>)}</nav></aside><main className="workspace"><header><div className="portal-name">CỔNG THÔNG TIN ĐÀO TẠO</div><div className="header-account"><button className="header-avatar" type="button" aria-label="Mở menu tài khoản" aria-expanded={accountOpen} onClick={() => setAccountOpen((value) => !value)}><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" /></svg></button>{accountOpen && <div className="account-dropdown"><button type="button" onClick={() => { setPage("profile"); setAccountOpen(false); }}>Tài khoản</button><button type="button" onClick={() => void logout()}>Đăng xuất</button></div>}</div></header><div className="page-content">{content}</div></main></div>;
}

createRoot(document.getElementById("root")!).render(<App />);
