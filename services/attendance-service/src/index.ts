import { mkdirSync } from "node:fs";
import { dirname } from "node:path";
import { DatabaseSync } from "node:sqlite";
import express from "express";
import type { AttendanceStatus } from "@spas/contracts";
import { requireInternal } from "@spas/service-security";
import { seedCourses, seedEnrollments, seedSections } from "./seed.js";

const file = process.env.ATTENDANCE_DB_PATH ?? "./runtime/attendance.db";
mkdirSync(dirname(file), { recursive: true });
const db = new DatabaseSync(file);
const periods: Record<number, [string, string]> = { 1: ["07:00", "07:50"], 2: ["07:55", "08:45"], 3: ["08:50", "09:40"], 4: ["09:50", "10:40"], 5: ["10:45", "11:35"], 6: ["11:40", "12:30"], 7: ["13:30", "14:20"], 8: ["14:25", "15:15"], 9: ["15:20", "16:10"], 10: ["16:20", "17:10"], 11: ["17:15", "18:05"], 12: ["18:20", "19:10"], 13: ["19:15", "20:05"] };
db.exec(`
  CREATE TABLE IF NOT EXISTS courses (code TEXT PRIMARY KEY, title TEXT NOT NULL);
  CREATE TABLE IF NOT EXISTS sections (id INTEGER PRIMARY KEY, course_code TEXT NOT NULL, teacher_id TEXT NOT NULL, room TEXT NOT NULL, weekday INTEGER NOT NULL, period INTEGER NOT NULL, start_time TEXT NOT NULL, end_time TEXT NOT NULL);
  CREATE TABLE IF NOT EXISTS enrollments (section_id INTEGER NOT NULL, student_id TEXT NOT NULL, PRIMARY KEY(section_id, student_id));
  CREATE TABLE IF NOT EXISTS attendance (section_id INTEGER NOT NULL, student_id TEXT NOT NULL, date TEXT NOT NULL, status TEXT NOT NULL, first_seen_at TEXT, proof_image TEXT, PRIMARY KEY(section_id, student_id, date));
`);
const sectionColumns = db.prepare("PRAGMA table_info(sections)").all() as Array<{ name: string }>;
if (!sectionColumns.some((column) => column.name === "period")) db.exec("ALTER TABLE sections ADD COLUMN period INTEGER");
const attendanceColumns = db.prepare("PRAGMA table_info(attendance)").all() as Array<{ name: string }>;
if (!attendanceColumns.some((column) => column.name === "proof_image")) db.exec("ALTER TABLE attendance ADD COLUMN proof_image TEXT");
const backfillPeriod = db.prepare("UPDATE sections SET period=?,start_time=?,end_time=? WHERE id=? AND period IS NULL");
[[1, "07:00", "07:50", 1], [8, "14:25", "15:15", 2], [4, "09:50", "10:40", 3]].forEach((row) => backfillPeriod.run(...row));
const empty = db.prepare("SELECT COUNT(*) AS total FROM courses").get() as { total: number };
if (!empty.total) {
  const course = db.prepare("INSERT INTO courses(code,title) VALUES(?,?)");
  seedCourses.forEach((row) => course.run(...row));
  const section = db.prepare("INSERT INTO sections(id,course_code,teacher_id,room,weekday,period,start_time,end_time) VALUES(?,?,?,?,?,?,?,?)");
  seedSections.forEach((row) => section.run(...row));
  const enrollment = db.prepare("INSERT INTO enrollments(section_id,student_id) VALUES(?,?)");
  seedEnrollments.forEach((row) => enrollment.run(...row));
}

type SectionTiming = { id: number; weekday: number; start_time: string };
function vietnamClock(now = new Date()) {
  const parts = new Intl.DateTimeFormat("en-GB", { timeZone: "Asia/Ho_Chi_Minh", year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", hourCycle: "h23" }).formatToParts(now).reduce<Record<string, string>>((values, part) => { if (part.type !== "literal") values[part.type] = part.value; return values; }, {});
  const year = Number(parts.year); const month = Number(parts.month); const day = Number(parts.day);
  return { date: `${parts.year}-${parts.month}-${parts.day}`, weekday: (new Date(Date.UTC(year, month - 1, day)).getUTCDay() + 6) % 7, minute: Number(parts.hour) * 60 + Number(parts.minute) };
}
function startMinute(startTime: string): number { const [hour, minute] = startTime.split(":").map(Number); return hour * 60 + minute; }
function sectionTiming(sectionId: number): SectionTiming | undefined { return db.prepare("SELECT id,weekday,start_time FROM sections WHERE id=?").get(sectionId) as SectionTiming | undefined; }
function automaticStatus(sectionId: number, now = new Date()): AttendanceStatus | undefined {
  const section = sectionTiming(sectionId); if (!section) return undefined;
  const clock = vietnamClock(now); if (clock.weekday !== section.weekday || clock.minute <= startMinute(section.start_time)) return "present";
  return clock.minute <= startMinute(section.start_time) + 15 ? "late" : "absent";
}
function finalizeAbsences(sectionId: number, now = new Date()): void {
  const section = sectionTiming(sectionId); if (!section) return;
  const clock = vietnamClock(now); if (clock.weekday !== section.weekday || clock.minute <= startMinute(section.start_time) + 15) return;
  db.prepare("INSERT OR IGNORE INTO attendance(section_id,student_id,date,status,first_seen_at,proof_image) SELECT section_id,student_id,?, 'absent', NULL, NULL FROM enrollments WHERE section_id=?").run(clock.date, sectionId);
}
function finalizeCurrentAbsences(): void {
  const clock = vietnamClock();
  (db.prepare("SELECT id FROM sections WHERE weekday=?").all(clock.weekday) as Array<{ id: number }>).forEach((section) => finalizeAbsences(section.id));
}
finalizeCurrentAbsences();
setInterval(finalizeCurrentAbsences, 60_000).unref();

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
app.get("/internal/courses", (_request, response) => {
  response.json({ courses: db.prepare("SELECT code,title FROM courses ORDER BY code").all() });
});
app.post("/internal/courses", (request, response) => {
  const { code, title } = request.body as { code?: string; title?: string };
  if (!code?.trim() || !title?.trim()) return response.status(400).json({ error: "Course code and title are required" });
  try { db.prepare("INSERT INTO courses(code,title) VALUES(?,?)").run(code.trim().toUpperCase(), title.trim()); }
  catch { return response.status(409).json({ error: "Course exists" }); }
  response.status(201).json({ course: { code: code.trim().toUpperCase(), title: title.trim() } });
});
app.post("/internal/sections", (request, response) => {
  const { courseCode, teacherId, room, weekday, period } = request.body as { courseCode?: string; teacherId?: string; room?: string; weekday?: number; period?: number };
  const weekdayNumber = Number(weekday); const periodNumber = Number(period); const timing = periods[periodNumber];
  if (!courseCode || !teacherId || !room?.trim() || !Number.isInteger(weekdayNumber) || weekdayNumber < 0 || weekdayNumber > 6 || !timing) return response.status(400).json({ error: "Invalid section" });
  const [startTime, endTime] = timing;
  if (!db.prepare("SELECT 1 FROM courses WHERE code=?").get(courseCode)) return response.status(404).json({ error: "Course not found" });
  const created = db.prepare("INSERT INTO sections(course_code,teacher_id,room,weekday,period,start_time,end_time) VALUES(?,?,?,?,?,?,?)").run(courseCode, teacherId, room.trim(), weekdayNumber, periodNumber, startTime, endTime);
  response.status(201).json({ section: { id: Number(created.lastInsertRowid), course_code: courseCode, teacher_id: teacherId, room: room.trim(), weekday: weekdayNumber, period: periodNumber, start_time: startTime, end_time: endTime } });
});
app.post("/internal/sections/:id/enrollments", (request, response) => {
  const sectionId = Number(request.params.id); const studentId = String(request.body?.studentId ?? "");
  if (!Number.isSafeInteger(sectionId) || !studentId) return response.status(400).json({ error: "Invalid enrollment" });
  if (!db.prepare("SELECT 1 FROM sections WHERE id=?").get(sectionId)) return response.status(404).json({ error: "Section not found" });
  try { db.prepare("INSERT INTO enrollments(section_id,student_id) VALUES(?,?)").run(sectionId, studentId); }
  catch { return response.status(409).json({ error: "Student is already enrolled" }); }
  response.status(201).json({ sectionId, studentId });
});
app.get("/internal/sections/:id/students", (request, response) => {
  const sectionId = Number(request.params.id);
  finalizeAbsences(sectionId);
  const date = vietnamClock().date;
  const students = db.prepare("SELECT e.student_id AS studentId,a.status,a.first_seen_at AS firstSeenAt FROM enrollments e LEFT JOIN attendance a ON a.section_id=e.section_id AND a.student_id=e.student_id AND a.date=? WHERE e.section_id=? ORDER BY e.student_id").all(date, sectionId);
  response.json({ students });
});
app.post("/internal/attendance", (request, response) => {
  const { sectionId, studentId, status = "present", automatic = false, proofImage } = request.body as { sectionId?: number; studentId?: string; status?: AttendanceStatus; automatic?: boolean; proofImage?: unknown };
  if (!sectionId || !studentId || !["present", "late", "absent"].includes(status)) return response.status(400).json({ error: "Invalid attendance" });
  const enrolled = db.prepare("SELECT 1 FROM enrollments WHERE section_id=? AND student_id=?").get(sectionId, studentId);
  if (!enrolled) return response.status(404).json({ error: "Student is not enrolled" });
  const now = new Date(); const clock = vietnamClock(now); const resolvedStatus = automatic ? automaticStatus(sectionId, now) : status;
  if (!resolvedStatus) return response.status(404).json({ error: "Section not found" });
  const firstSeenAt = resolvedStatus === "absent" ? null : now.toISOString(); const image = automatic && typeof proofImage === "string" && proofImage.length <= 250_000 && /^[A-Za-z0-9+/=]+$/.test(proofImage) ? proofImage : null;
  const statement = automatic ? "INSERT OR IGNORE INTO attendance(section_id,student_id,date,status,first_seen_at,proof_image) VALUES(?,?,?,?,?,?)" : "INSERT INTO attendance(section_id,student_id,date,status,first_seen_at,proof_image) VALUES(?,?,?,?,?,NULL) ON CONFLICT(section_id,student_id,date) DO UPDATE SET status=excluded.status,first_seen_at=excluded.first_seen_at";
  db.prepare(statement).run(sectionId, studentId, clock.date, resolvedStatus, firstSeenAt, image);
  response.status(204).end();
});
app.get("/internal/attendance", (request, response) => {
  const studentId = String(request.query.studentId ?? "");
  const rows = db.prepare("SELECT a.date,a.status,a.first_seen_at AS firstSeenAt,a.proof_image AS faceImage,s.course_code,c.title,s.room,s.period,s.start_time AS startTime,s.end_time AS endTime FROM attendance a JOIN sections s ON s.id=a.section_id JOIN courses c ON c.code=s.course_code WHERE a.student_id=? ORDER BY a.date DESC,s.start_time DESC").all(studentId);
  response.json({ attendance: rows });
});
app.listen(Number(process.env.PORT ?? 3002));
