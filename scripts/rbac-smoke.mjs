import { spawn } from "node:child_process";

const root = new URL("..", import.meta.url).pathname.slice(1);
const environment = { ...process.env, INTERNAL_SERVICE_TOKEN: "local-test-internal-token-123456", SESSION_SECRET: "local-test-session-secret-1234567890" };
const services = ["identity-service", "attendance-service", "api-gateway"].map((name) => spawn("node", ["dist/index.js"], { cwd: `${root}/services/${name}`, env: environment, stdio: "ignore" }));
const wait = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds));

try {
  await wait(1500);
  const identityBlocked = await fetch("http://127.0.0.1:3001/internal/users");
  if (identityBlocked.status !== 401) throw new Error(`Expected identity internal 401, got ${identityBlocked.status}`);
  const attendanceBlocked = await fetch("http://127.0.0.1:3002/internal/attendance");
  if (attendanceBlocked.status !== 401) throw new Error(`Expected attendance internal 401, got ${attendanceBlocked.status}`);
  const anonymous = await fetch("http://127.0.0.1:8080/api/sections");
  if (anonymous.status !== 401) throw new Error(`Expected anonymous 401, got ${anonymous.status}`);
  const studentLogin = await fetch("http://127.0.0.1:8080/api/auth/login", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ userId: "SV001", password: "sv123" }) });
  const studentCookie = studentLogin.headers.get("set-cookie");
  const tamperedCookie = `${studentCookie?.split(";")[0] ?? "spas_session=missing"}x`;
  const tampered = await fetch("http://127.0.0.1:8080/api/auth/me", { headers: { cookie: tamperedCookie } });
  if (tampered.status !== 401) throw new Error(`Expected tampered session 401, got ${tampered.status}`);
  const forbidden = await fetch("http://127.0.0.1:8080/api/attendance", { method: "POST", headers: { "content-type": "application/json", cookie: studentCookie ?? "" }, body: JSON.stringify({ sectionId: 1, studentId: "SV001", status: "present" }) });
  if (forbidden.status !== 403) throw new Error(`Expected student 403, got ${forbidden.status}`);
  const studentRoster = await fetch("http://127.0.0.1:8080/api/sections/1/students", { headers: { cookie: studentCookie ?? "" } });
  if (studentRoster.status !== 403) throw new Error(`Expected student roster 403, got ${studentRoster.status}`);
  const teacherLogin = await fetch("http://127.0.0.1:8080/api/auth/login", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ userId: "GV001", password: "gv123" }) });
  const teacherCookie = teacherLogin.headers.get("set-cookie");
  const sections = await fetch("http://127.0.0.1:8080/api/sections", { headers: { cookie: teacherCookie ?? "" } });
  const sectionData = await sections.json();
  if (!sections.ok || !sectionData.sections?.some((section) => section.course_code === "INT101" && section.period === 1)) throw new Error("Teacher timetable is missing assigned period");
  const otherTeacherSection = await fetch("http://127.0.0.1:8080/api/attendance", { method: "POST", headers: { "content-type": "application/json", cookie: teacherCookie ?? "" }, body: JSON.stringify({ sectionId: 2, studentId: "SV001", status: "present" }) });
  if (otherTeacherSection.status !== 403) throw new Error(`Expected unassigned teacher section 403, got ${otherTeacherSection.status}`);
  const otherTeacherRoster = await fetch("http://127.0.0.1:8080/api/sections/2/students", { headers: { cookie: teacherCookie ?? "" } });
  if (otherTeacherRoster.status !== 403) throw new Error(`Expected unassigned teacher roster 403, got ${otherTeacherRoster.status}`);
  const ownTeacherSection = await fetch("http://127.0.0.1:8080/api/attendance", { method: "POST", headers: { "content-type": "application/json", cookie: teacherCookie ?? "" }, body: JSON.stringify({ sectionId: 1, studentId: "SV001", status: "present" }) });
  if (ownTeacherSection.status !== 204) throw new Error(`Expected assigned teacher section 204, got ${ownTeacherSection.status}`);
  const adminLogin = await fetch("http://127.0.0.1:8080/api/auth/login", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ userId: "ADMIN001", password: "admin123" }) });
  const adminCookie = adminLogin.headers.get("set-cookie");
  const adminWrite = await fetch("http://127.0.0.1:8080/api/attendance", { method: "POST", headers: { "content-type": "application/json", cookie: adminCookie ?? "" }, body: JSON.stringify({ sectionId: 2, studentId: "SV001", status: "present" }) });
  if (adminWrite.status !== 204) throw new Error(`Expected admin attendance 204, got ${adminWrite.status}`);
  console.log("RBAC smoke test passed.");
} finally {
  services.forEach((service) => service.kill());
}
