import { mkdirSync } from "node:fs";
import { dirname } from "node:path";
import { DatabaseSync } from "node:sqlite";
import express from "express";
import type { AttendanceStatus } from "@spas/contracts";
import { requireInternal } from "@spas/service-security";

const file = process.env.ATTENDANCE_DB_PATH ?? "./runtime/attendance.db";
mkdirSync(dirname(file), { recursive: true });
const db = new DatabaseSync(file);
db.exec(`
  CREATE TABLE IF NOT EXISTS courses (code TEXT PRIMARY KEY, title TEXT NOT NULL);
  CREATE TABLE IF NOT EXISTS sections (id INTEGER PRIMARY KEY, course_code TEXT NOT NULL, teacher_id TEXT NOT NULL, room TEXT NOT NULL, weekday INTEGER NOT NULL, period INTEGER NOT NULL, start_time TEXT NOT NULL, end_time TEXT NOT NULL);
  CREATE TABLE IF NOT EXISTS enrollments (section_id INTEGER NOT NULL, student_id TEXT NOT NULL, PRIMARY KEY(section_id, student_id));
  CREATE TABLE IF NOT EXISTS attendance (section_id INTEGER NOT NULL, student_id TEXT NOT NULL, date TEXT NOT NULL, status TEXT NOT NULL, first_seen_at TEXT, PRIMARY KEY(section_id, student_id, date));
`);
const sectionColumns = db.prepare("PRAGMA table_info(sections)").all() as Array<{ name: string }>;
if (!sectionColumns.some((column) => column.name === "period")) db.exec("ALTER TABLE sections ADD COLUMN period INTEGER");
const backfillPeriod = db.prepare("UPDATE sections SET period=?,start_time=?,end_time=? WHERE id=? AND period IS NULL");
[[1, "07:00", "07:50", 1], [8, "14:25", "15:15", 2], [4, "09:50", "10:40", 3]].forEach((row) => backfillPeriod.run(...row));
const empty = db.prepare("SELECT COUNT(*) AS total FROM courses").get() as { total: number };
if (!empty.total) {
  const course = db.prepare("INSERT INTO courses(code,title) VALUES(?,?)");
  [["INT101", "Nhập môn Trí tuệ nhân tạo"], ["WEB201", "Lập trình Web"], ["DAT102", "Cơ sở dữ liệu"]].forEach((row) => course.run(...row));
  const section = db.prepare("INSERT INTO sections(id,course_code,teacher_id,room,weekday,period,start_time,end_time) VALUES(?,?,?,?,?,?,?,?)");
  [[1, "INT101", "GV001", "A2-301", 0, 1, "07:00", "07:50"], [2, "WEB201", "GV002", "A2-203", 2, 8, "14:25", "15:15"], [3, "DAT102", "GV001", "B1-105", 4, 4, "09:50", "10:40"]].forEach((row) => section.run(...row));
  const enrollment = db.prepare("INSERT INTO enrollments(section_id,student_id) VALUES(?,?)");
  [1, 2, 3].forEach((sectionId) => ["SV001", "SV002", "SV003"].forEach((studentId) => enrollment.run(sectionId, studentId)));
}

const app = express();
app.use(express.json());
app.get("/health", (_request, response) => response.json({ service: "attendance", status: "ok" }));
app.use("/internal", requireInternal);
app.get("/internal/sections", (request, response) => {
  const teacherId = request.query.teacherId as string | undefined;
  const studentId = request.query.studentId as string | undefined;
  const sql = teacherId ? "SELECT s.*,c.title FROM sections s JOIN courses c ON c.code=s.course_code WHERE s.teacher_id=? ORDER BY weekday,start_time" : studentId ? "SELECT s.*,c.title FROM enrollments e JOIN sections s ON s.id=e.section_id JOIN courses c ON c.code=s.course_code WHERE e.student_id=? ORDER BY weekday,start_time" : "SELECT s.*,c.title FROM sections s JOIN courses c ON c.code=s.course_code ORDER BY weekday,start_time";
  const statement = db.prepare(sql);
  const sections = teacherId ? statement.all(teacherId) : studentId ? statement.all(studentId) : statement.all();
  response.json({ sections });
});
app.get("/internal/sections/:id/students", (request, response) => {
  const date = new Date().toISOString().slice(0, 10);
  const students = db.prepare("SELECT e.student_id AS studentId,a.status,a.first_seen_at AS firstSeenAt FROM enrollments e LEFT JOIN attendance a ON a.section_id=e.section_id AND a.student_id=e.student_id AND a.date=? WHERE e.section_id=? ORDER BY e.student_id").all(date, Number(request.params.id));
  response.json({ students });
});
app.post("/internal/attendance", (request, response) => {
  const { sectionId, studentId, status = "present" } = request.body as { sectionId?: number; studentId?: string; status?: AttendanceStatus };
  if (!sectionId || !studentId || !["present", "late", "absent", "excused"].includes(status)) return response.status(400).json({ error: "Invalid attendance" });
  const enrolled = db.prepare("SELECT 1 FROM enrollments WHERE section_id=? AND student_id=?").get(sectionId, studentId);
  if (!enrolled) return response.status(404).json({ error: "Student is not enrolled" });
  db.prepare("INSERT INTO attendance(section_id,student_id,date,status,first_seen_at) VALUES(?,?,?,?,?) ON CONFLICT(section_id,student_id,date) DO UPDATE SET status=excluded.status,first_seen_at=excluded.first_seen_at").run(sectionId, studentId, new Date().toISOString().slice(0, 10), status, new Date().toISOString());
  response.status(204).end();
});
app.get("/internal/attendance", (request, response) => {
  const studentId = String(request.query.studentId ?? "");
  const rows = db.prepare("SELECT a.date,a.status,a.first_seen_at AS firstSeenAt,s.course_code,c.title FROM attendance a JOIN sections s ON s.id=a.section_id JOIN courses c ON c.code=s.course_code WHERE a.student_id=? ORDER BY a.date DESC").all(studentId);
  response.json({ attendance: rows });
});
app.listen(Number(process.env.PORT ?? 3002));
