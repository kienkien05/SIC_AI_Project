import { createHmac, timingSafeEqual } from "node:crypto";
import { existsSync } from "node:fs";
import path from "node:path";
import express, { type NextFunction, type Request, type Response as ExpressResponse } from "express";
import multer from "multer";
import type { Role, User } from "@spas/contracts";

const identityUrl = process.env.IDENTITY_SERVICE_URL ?? "http://127.0.0.1:3001";
const attendanceUrl = process.env.ATTENDANCE_SERVICE_URL ?? "http://127.0.0.1:3002";
const aiAdapterUrl = process.env.AI_ADAPTER_SERVICE_URL ?? "http://127.0.0.1:3003";
function required(name: string): string { const value = process.env[name]; if (!value) throw new Error(`${name} is required`); return value; }
const internalToken = required("INTERNAL_SERVICE_TOKEN");
const sessionSecret = required("SESSION_SECRET");

type Session = { id: string; role: Role; fullName: string };
declare global { namespace Express { interface Request { user?: Session; } } }

function signature(value: string): string { return createHmac("sha256", sessionSecret).update(value).digest("base64url"); }
function readCookie(request: Request): string | undefined { return request.headers.cookie?.split(";").map((value) => value.trim()).find((value) => value.startsWith("spas_session="))?.slice(13); }
function readSession(request: Request): Session | undefined {
  const packed = readCookie(request); if (!packed) return undefined;
  const [payload, received] = packed.split("."); if (!payload || !received) return undefined;
  const expected = signature(payload); if (expected.length !== received.length || !timingSafeEqual(Buffer.from(expected), Buffer.from(received))) return undefined;
  try {
    const value = JSON.parse(Buffer.from(payload, "base64url").toString()) as Partial<Session>;
    return typeof value.id === "string" && typeof value.fullName === "string" && ["admin", "teacher", "student"].includes(value.role ?? "") ? value as Session : undefined;
  } catch { return undefined; }
}
function setSession(response: ExpressResponse, user: User): void { const payload = Buffer.from(JSON.stringify({ id: user.id, role: user.role, fullName: user.fullName })).toString("base64url"); response.cookie("spas_session", `${payload}.${signature(payload)}`, { httpOnly: true, sameSite: "lax", secure: process.env.NODE_ENV === "production", maxAge: 8 * 60 * 60 * 1000 }); }
async function internal(url: string, init?: RequestInit): Promise<globalThis.Response> { return fetch(url, { ...init, headers: { "x-spas-internal-token": internalToken, "content-type": "application/json", ...(init?.headers ?? {}) } }); }
async function internalUpload(path: string, fields: Record<string, string>, files: Express.Multer.File[]): Promise<globalThis.Response> { const data = new FormData(); Object.entries(fields).forEach(([key, value]) => data.append(key, value)); files.forEach((file) => data.append(file.fieldname, new Blob([file.buffer as unknown as BlobPart], { type: file.mimetype }), file.originalname)); return fetch(`${aiAdapterUrl}${path}`, { method: "POST", headers: { "x-spas-internal-token": internalToken }, body: data }); }
function authenticated(request: Request, response: ExpressResponse, next: NextFunction): void { const user = readSession(request); if (!user) { response.status(401).json({ error: "Login required" }); return; } request.user = user; next(); }
function allowed(...roles: Role[]) { return (request: Request, response: ExpressResponse, next: NextFunction): void => { if (!request.user || !roles.includes(request.user.role)) { response.status(403).json({ error: "Insufficient permission" }); return; } next(); }; }
function validSectionId(value: unknown): number | undefined { const sectionId = Number(value); return Number.isSafeInteger(sectionId) && sectionId > 0 ? sectionId : undefined; }
async function managesSection(user: Session, sectionId: number): Promise<boolean> {
  if (user.role === "admin") return true;
  if (user.role !== "teacher") return false;
  const upstream = await internal(`${attendanceUrl}/internal/sections?teacherId=${user.id}`);
  if (!upstream.ok) return false;
  const data = await upstream.json() as { sections: Array<{ id: number }> };
  return data.sections.some((section) => section.id === sectionId);
}

const app = express();
app.use(express.json({ limit: "1mb" }));
const upload = multer({ storage: multer.memoryStorage(), limits: { fileSize: 5 * 1024 * 1024, files: 8 }, fileFilter: (_request, file, callback) => callback(null, ["image/jpeg", "image/png"].includes(file.mimetype)) });
app.get("/health", (_request, response) => response.json({ service: "gateway", status: "ok" }));
app.post("/api/auth/login", async (request, response) => {
  const upstream = await internal(`${identityUrl}/internal/login`, { method: "POST", body: JSON.stringify(request.body) });
  const data = await upstream.json() as { user?: User; error?: string };
  if (!upstream.ok || !data.user) return response.status(upstream.status).json({ error: data.error ?? "Login failed" });
  setSession(response, data.user); response.json({ user: data.user });
});
app.post("/api/auth/logout", (_request, response) => { response.clearCookie("spas_session"); response.status(204).end(); });
app.get("/api/auth/me", authenticated, (request, response) => response.json({ user: request.user }));
app.get("/api/sections", authenticated, async (request, response) => {
  const query = request.user!.role === "teacher" ? `?teacherId=${request.user!.id}` : request.user!.role === "student" ? `?studentId=${request.user!.id}` : "";
  const upstream = await internal(`${attendanceUrl}/internal/sections${query}`); response.status(upstream.status).json(await upstream.json());
});
app.get("/api/sections/:id/students", authenticated, allowed("teacher", "admin"), async (request, response) => {
  const sectionId = validSectionId(request.params.id);
  if (!sectionId) return response.status(400).json({ error: "Invalid section" });
  if (!(await managesSection(request.user!, sectionId))) return response.status(403).json({ error: "Section is not assigned" });
  const upstream = await internal(`${attendanceUrl}/internal/sections/${sectionId}/students`); response.status(upstream.status).json(await upstream.json());
});
app.post("/api/attendance", authenticated, allowed("teacher", "admin"), async (request, response) => {
  const sectionId = validSectionId(request.body?.sectionId);
  if (!sectionId) return response.status(400).json({ error: "Invalid section" });
  if (!(await managesSection(request.user!, sectionId))) return response.status(403).json({ error: "Section is not assigned" });
  const upstream = await internal(`${attendanceUrl}/internal/attendance`, { method: "POST", body: JSON.stringify({ ...request.body, sectionId }) });
  if (upstream.status === 204) return response.status(204).end(); response.status(upstream.status).json(await upstream.json());
});
app.get("/api/attendance/me", authenticated, allowed("student"), async (request, response) => {
  const upstream = await internal(`${attendanceUrl}/internal/attendance?studentId=${request.user!.id}`); response.status(upstream.status).json(await upstream.json());
});
app.post("/api/face/pose", authenticated, allowed("student"), upload.single("image"), async (request, response) => {
  if (!request.file) return response.status(400).json({ error: "Image is required" });
  const upstream = await internalUpload("/internal/face-pose", {}, [request.file]); response.status(upstream.status).json(await upstream.json());
});
app.post("/api/face/enrollment", authenticated, allowed("student"), upload.array("frames", 8), async (request, response) => {
  const frames = request.files as Express.Multer.File[];
  if (frames.length !== 8) return response.status(400).json({ error: "Eight frames are required" });
  const upstream = await internalUpload("/internal/enrollment", { studentId: request.user!.id, name: request.user!.fullName }, frames);
  if (!upstream.ok) return response.status(upstream.status).json(await upstream.json());
  await internal(`${identityUrl}/internal/users/${request.user!.id}/enrollment`, { method: "POST", body: "{}" });
  response.json(await upstream.json());
});
app.post("/api/sections/:id/recognize", authenticated, allowed("teacher"), upload.single("image"), async (request, response) => {
  if (!request.file) return response.status(400).json({ error: "Image is required" });
  const sectionId = validSectionId(request.params.id);
  if (!sectionId) return response.status(400).json({ error: "Invalid section" });
  if (!(await managesSection(request.user!, sectionId))) return response.status(403).json({ error: "Section is not assigned" });
  const upstream = await internalUpload("/internal/recognize", {}, [request.file]); const data = await upstream.json() as { results?: Array<{ student_id?: string }> };
  if (!upstream.ok) return response.status(upstream.status).json(data);
  const markedIds: string[] = [];
  for (const studentId of new Set(data.results?.map((result) => result.student_id).filter((id): id is string => Boolean(id)) ?? [])) { const marked = await internal(`${attendanceUrl}/internal/attendance`, { method: "POST", body: JSON.stringify({ sectionId, studentId, status: "present" }) }); if (marked.ok) markedIds.push(studentId); }
  response.json({ ...data, markedIds });
});
const webDist = process.env.WEB_DIST_DIR;
if (webDist && existsSync(webDist)) {
  app.use(express.static(webDist));
  app.get("/{*path}", (_request, response) => response.sendFile(path.join(webDist, "index.html")));
}
app.listen(Number(process.env.PORT ?? 8080));
