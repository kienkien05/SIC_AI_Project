import { spawn } from "node:child_process";

const root = new URL("..", import.meta.url).pathname.slice(1);
const environment = { ...process.env, INTERNAL_SERVICE_TOKEN: "local-test-internal-token-123456", SESSION_SECRET: "local-test-session-secret-1234567890" };
const services = ["identity-service", "attendance-service", "api-gateway"].map((name) => spawn("node", ["dist/index.js"], { cwd: `${root}/services/${name}`, env: environment, stdio: "ignore" }));
const wait = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds));

try {
  await wait(1500);
  const blocked = await fetch("http://127.0.0.1:3001/internal/users");
  if (blocked.status !== 401) throw new Error(`Expected internal 401, got ${blocked.status}`);
  const studentLogin = await fetch("http://127.0.0.1:8080/api/auth/login", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ userId: "SV001", password: "sv123" }) });
  const studentCookie = studentLogin.headers.get("set-cookie");
  const forbidden = await fetch("http://127.0.0.1:8080/api/attendance", { method: "POST", headers: { "content-type": "application/json", cookie: studentCookie ?? "" }, body: JSON.stringify({ sectionId: 1, studentId: "SV001", status: "present" }) });
  if (forbidden.status !== 403) throw new Error(`Expected student 403, got ${forbidden.status}`);
  const teacherLogin = await fetch("http://127.0.0.1:8080/api/auth/login", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ userId: "GV001", password: "gv123" }) });
  const teacherCookie = teacherLogin.headers.get("set-cookie");
  const sections = await fetch("http://127.0.0.1:8080/api/sections", { headers: { cookie: teacherCookie ?? "" } });
  if (!sections.ok || !(await sections.text()).includes("INT101")) throw new Error("Teacher cannot access assigned sections");
  console.log("RBAC smoke test passed.");
} finally {
  services.forEach((service) => service.kill());
}
