import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { once } from "node:events";
import { mkdtemp, rm } from "node:fs/promises";
import net from "node:net";
import { tmpdir } from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

async function freePort() {
  const server = net.createServer();
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  const port = server.address().port;
  await new Promise((resolve, reject) => server.close((error) => error ? reject(error) : resolve()));
  return port;
}

test("camera recognition keeps on-time status and marks a new late student", async (t) => {
  const directory = await mkdtemp(path.join(tmpdir(), "spas-demo-clock-"));
  const port = await freePort();
  const token = "demo-clock-test-token";
  const service = spawn(process.execPath, [fileURLToPath(new URL("../dist/index.js", import.meta.url))], {
    env: { ...process.env, PORT: String(port), ATTENDANCE_DB_PATH: path.join(directory, "attendance.db"), INTERNAL_SERVICE_TOKEN: token, DEMO_CLOCK_ENABLED: "true" },
    stdio: "ignore",
  });
  t.after(async () => {
    if (service.exitCode === null && service.signalCode === null) {
      const exited = once(service, "exit");
      service.kill();
      await exited;
    }
    await rm(directory, { recursive: true, force: true });
  });

  const request = async (route, method = "GET", body) => {
    const response = await fetch(`http://127.0.0.1:${port}${route}`, {
      method,
      headers: { "x-spas-internal-token": token, ...(body ? { "content-type": "application/json" } : {}) },
      ...(body ? { body: JSON.stringify(body) } : {}),
    });
    const data = response.status === 204 ? undefined : await response.json();
    if (!response.ok) throw new Error(`${method} ${route} failed (${response.status}): ${data?.error ?? "request failed"}`);
    return { response, data };
  };

  let ready = false;
  for (let attempt = 0; attempt < 50 && !ready; attempt += 1) {
    if (service.exitCode !== null) throw new Error(`Attendance service exited with ${service.exitCode}`);
    try { ready = (await request("/health")).response.ok; }
    catch { await new Promise((resolve) => setTimeout(resolve, 100)); }
  }
  assert.equal(ready, true, "attendance service becomes healthy");

  await request("/internal/courses", "POST", { code: "CLOCKTEST", title: "Clock test" });
  const { data: sectionData } = await request("/internal/sections", "POST", { courseCode: "CLOCKTEST", teacherId: "DEMO_TEACHER", room: "TEST", weekday: 0, period: 1 });
  const sectionId = sectionData.section.id;
  await request(`/internal/sections/${sectionId}/enrollments`, "POST", { studentId: "DEMO_ON_TIME" });
  await request(`/internal/sections/${sectionId}/enrollments`, "POST", { studentId: "DEMO_LATE" });

  await request(`/internal/sections/${sectionId}/demo-clock`, "POST", { action: "start" });
  await request("/internal/attendance", "POST", { sectionId, studentId: "DEMO_ON_TIME", automatic: true });
  const { data: onTimeBefore } = await request(`/internal/sections/${sectionId}/students`);
  const firstSeenAt = onTimeBefore.students.find((student) => student.studentId === "DEMO_ON_TIME").firstSeenAt;

  await request(`/internal/sections/${sectionId}/demo-clock`, "POST", { action: "advance" });
  await request("/internal/attendance", "POST", { sectionId, studentId: "DEMO_ON_TIME", automatic: true });
  await request("/internal/attendance", "POST", { sectionId, studentId: "DEMO_LATE", automatic: true });
  const { data: roster } = await request(`/internal/sections/${sectionId}/students`);
  const statuses = new Map(roster.students.map((student) => [student.studentId, student]));

  assert.equal(statuses.get("DEMO_ON_TIME").status, "present");
  assert.equal(statuses.get("DEMO_ON_TIME").firstSeenAt, firstSeenAt);
  assert.equal(statuses.get("DEMO_LATE").status, "late");
});
