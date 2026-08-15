import { createServer } from "node:http";
import { spawn } from "node:child_process";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL("..", import.meta.url));
const runtime = mkdtempSync(join(tmpdir(), "spas-system-smoke-"));
const environment = {
  ...process.env,
  INTERNAL_SERVICE_TOKEN: "local-test-internal-token-123456",
  SESSION_SECRET: "local-test-session-secret-1234567890",
  FACE_AI_TOKEN: "local-test-face-ai-token-123456",
  IDENTITY_DB_PATH: join(runtime, "identity.db"),
  ATTENDANCE_DB_PATH: join(runtime, "attendance.db")
};

function json(response, status, body) {
  response.writeHead(status, { "content-type": "application/json" });
  response.end(JSON.stringify(body));
}

const faceAi = createServer((request, response) => {
  if (request.headers["x-spas-ai-token"] !== environment.FACE_AI_TOKEN) return json(response, 401, { error: "Invalid Face AI token" });
  if (request.method === "GET" && request.url === "/health") return json(response, 200, { status: "ok" });
  if (request.method === "POST" && request.url === "/api/face-pose") return json(response, 200, { pose: "front", confidence: 0.99, detail: "" });
  if (request.method === "POST" && request.url === "/api/enroll") return json(response, 200, { accepted: 8, previews: [] });
  if (request.method === "POST" && request.url === "/api/recognize") return json(response, 200, { faces: 1, results: [{ student_id: "SV001", name: "Trương Trung Kiên", score: 0.99 }] });
  return json(response, 404, { error: "Unknown Face AI route" });
});

const children = [];
const wait = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds));
const cookie = (response) => response.headers.get("set-cookie") ?? "";
const image = () => new Blob(["test-image"], { type: "image/jpeg" });

async function freePort() {
  const server = createServer();
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  const address = server.address();
  await new Promise((resolve) => server.close(resolve));
  return address.port;
}

async function waitFor(url) {
  for (let attempt = 0; attempt < 30; attempt += 1) {
    try { if ((await fetch(url)).ok) return; } catch { }
    await wait(200);
  }
  throw new Error(`Timed out waiting for ${url}`);
}

try {
  const [identityPort, attendancePort, adapterPort, gatewayPort] = await Promise.all([freePort(), freePort(), freePort(), freePort()]);
  await new Promise((resolve) => faceAi.listen(0, "127.0.0.1", resolve));
  const faceAiAddress = faceAi.address();
  environment.FACE_AI_URL = `http://127.0.0.1:${faceAiAddress.port}`;
  const serviceEnvironment = { ...environment, IDENTITY_SERVICE_URL: `http://127.0.0.1:${identityPort}`, ATTENDANCE_SERVICE_URL: `http://127.0.0.1:${attendancePort}`, AI_ADAPTER_SERVICE_URL: `http://127.0.0.1:${adapterPort}` };
  [["identity-service", identityPort], ["attendance-service", attendancePort], ["ai-adapter-service", adapterPort], ["api-gateway", gatewayPort]].forEach(([name, port]) => children.push(spawn("node", ["dist/index.js"], { cwd: `${root}/services/${name}`, env: { ...serviceEnvironment, PORT: String(port) }, stdio: "ignore" })));
  await Promise.all([identityPort, attendancePort, adapterPort, gatewayPort].map((port) => waitFor(`http://127.0.0.1:${port}/health`)));

  const directAdapter = await fetch(`http://127.0.0.1:${adapterPort}/internal/recognize`, { method: "POST" });
  if (directAdapter.status !== 401) throw new Error(`Expected direct adapter 401, got ${directAdapter.status}`);

  const studentLogin = await fetch(`http://127.0.0.1:${gatewayPort}/api/auth/login`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ userId: "SV001", password: "sv123" }) });
  if (!studentLogin.ok) throw new Error("Student login failed");
  const studentCookie = cookie(studentLogin);

  const poseForm = new FormData();
  poseForm.append("image", image(), "pose.jpg");
  const pose = await fetch(`http://127.0.0.1:${gatewayPort}/api/face/pose`, { method: "POST", headers: { cookie: studentCookie }, body: poseForm });
  if (!pose.ok || (await pose.json()).pose !== "front") throw new Error("Face pose gateway flow failed");

  const enrollmentForm = new FormData();
  for (let index = 0; index < 8; index += 1) enrollmentForm.append("frames", image(), `frame-${index}.jpg`);
  const enrollment = await fetch(`http://127.0.0.1:${gatewayPort}/api/face/enrollment`, { method: "POST", headers: { cookie: studentCookie }, body: enrollmentForm });
  if (!enrollment.ok || (await enrollment.json()).accepted !== 8) throw new Error("Enrollment gateway flow failed");
  const user = await fetch(`http://127.0.0.1:${identityPort}/internal/users/SV001`, { headers: { "x-spas-internal-token": environment.INTERNAL_SERVICE_TOKEN } });
  if (!user.ok || !(await user.json()).user.enrolledAt) throw new Error("Enrollment state was not persisted");

  const teacherLogin = await fetch(`http://127.0.0.1:${gatewayPort}/api/auth/login`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ userId: "GV001", password: "gv123" }) });
  if (!teacherLogin.ok) throw new Error("Teacher login failed");
  const scanForm = new FormData();
  scanForm.append("image", image(), "classroom.jpg");
  const scan = await fetch(`http://127.0.0.1:${gatewayPort}/api/sections/1/recognize`, { method: "POST", headers: { cookie: cookie(teacherLogin) }, body: scanForm });
  const scanData = await scan.json();
  if (!scan.ok || !scanData.markedIds?.includes("SV001")) throw new Error("Classroom recognition flow failed");

  console.log("System smoke test passed.");
} finally {
  await Promise.all(children.map((child) => new Promise((resolve) => { if (child.exitCode !== null) return resolve(); child.once("exit", resolve); child.kill(); })));
  await new Promise((resolve) => faceAi.close(resolve));
  rmSync(runtime, { recursive: true, force: true });
}
