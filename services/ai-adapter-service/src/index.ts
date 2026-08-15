import express from "express";
import multer from "multer";
import { requireInternal } from "@spas/service-security";

function required(name: string): string { const value = process.env[name]; if (!value) throw new Error(`${name} is required`); return value; }
const aiUrl = required("FACE_AI_URL").replace(/\/$/, "");
const aiToken = required("FACE_AI_TOKEN");
const upload = multer({ storage: multer.memoryStorage(), limits: { fileSize: 5 * 1024 * 1024, files: 8 }, fileFilter: (_request, file, callback) => callback(null, ["image/jpeg", "image/png"].includes(file.mimetype)) });

function form(fields: Record<string, string>, files: Express.Multer.File[]): FormData {
  const data = new FormData();
  Object.entries(fields).forEach(([key, value]) => data.append(key, value));
  files.forEach((file) => data.append(file.fieldname, new Blob([file.buffer as unknown as BlobPart], { type: file.mimetype }), file.originalname));
  return data;
}
async function forward(path: string, fields: Record<string, string>, files: Express.Multer.File[], method = "POST"): Promise<Response> {
  return fetch(`${aiUrl}${path}`, { method, headers: { "x-spas-ai-token": aiToken }, body: method === "DELETE" ? undefined : form(fields, files) });
}

const app = express();
app.get("/health", async (_request, response) => {
  const upstream = await fetch(`${aiUrl}/health`, { headers: { "x-spas-ai-token": aiToken } });
  response.status(upstream.ok ? 200 : 503).json({ service: "ai-adapter", status: upstream.ok ? "ok" : "unavailable" });
});
app.use("/internal", requireInternal);
app.post("/internal/recognize", upload.single("image"), async (request, response) => {
  if (!request.file) return response.status(400).json({ error: "Image is required" });
  const upstream = await forward("/api/recognize", {}, [request.file]);
  response.status(upstream.status).json(await upstream.json());
});
app.post("/internal/face-pose", upload.single("image"), async (request, response) => {
  if (!request.file) return response.status(400).json({ error: "Image is required" });
  const upstream = await forward("/api/face-pose", {}, [request.file]);
  response.status(upstream.status).json(await upstream.json());
});
app.post("/internal/enrollment", upload.array("frames", 8), async (request, response) => {
  const frames = request.files as Express.Multer.File[];
  const studentId = String(request.body.studentId ?? ""); const name = String(request.body.name ?? "");
  if (!studentId || !name || frames.length !== 8) return response.status(400).json({ error: "Eight enrollment frames are required" });
  const upstream = await forward("/api/enroll", { student_id: studentId, name }, frames);
  response.status(upstream.status).json(await upstream.json());
});
app.delete("/internal/enrollment/:studentId", async (request, response) => {
  const upstream = await forward(`/api/enrollment/${encodeURIComponent(request.params.studentId)}`, {}, [], "DELETE");
  if (upstream.status === 204) return response.status(204).end(); response.status(upstream.status).json(await upstream.json());
});
app.get("/internal/enrollment/:studentId/previews", async (request, response) => {
  const upstream = await fetch(`${aiUrl}/api/enrollment/${encodeURIComponent(request.params.studentId)}/previews`, { headers: { "x-spas-ai-token": aiToken } });
  response.status(upstream.status).json(await upstream.json());
});
app.listen(Number(process.env.PORT ?? 3003));
