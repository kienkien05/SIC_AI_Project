import { createHmac, pbkdf2Sync, randomBytes, timingSafeEqual } from "node:crypto";
import { mkdirSync } from "node:fs";
import { dirname } from "node:path";
import { DatabaseSync } from "node:sqlite";
import express from "express";
import type { Role, User } from "@spas/contracts";
import { requireInternal } from "@spas/service-security";
import { seedUsers } from "./seed.js";

type StoredUser = { id: string; full_name: string; role: Role; password_hash: string; enrolled_at?: string };
const databasePath = process.env.IDENTITY_DB_PATH ?? "./runtime/identity.db";
mkdirSync(dirname(databasePath), { recursive: true });
const database = new DatabaseSync(databasePath);
database.exec(`
  CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, full_name TEXT NOT NULL, role TEXT NOT NULL, password_hash TEXT NOT NULL, enrolled_at TEXT);
`);

function hashPassword(password: string, salt = randomBytes(16)): string {
  return Buffer.concat([salt, pbkdf2Sync(password, salt, 200_000, 32, "sha256")]).toString("base64");
}

function matchesPassword(password: string, stored: string): boolean {
  const raw = Buffer.from(stored, "base64");
  return timingSafeEqual(raw.subarray(16), Buffer.from(hashPassword(password, raw.subarray(0, 16)), "base64").subarray(16));
}

function publicUser(row: StoredUser): User & { enrolledAt?: string } {
  return { id: row.id, fullName: row.full_name, role: row.role, enrolledAt: row.enrolled_at };
}

const count = database.prepare("SELECT COUNT(*) AS total FROM users").get() as { total: number };
if (!count.total) {
  const insert = database.prepare("INSERT INTO users(id, full_name, role, password_hash) VALUES(?,?,?,?)");
  seedUsers.forEach((user) => insert.run(user.id, user.fullName, user.role, hashPassword(user.password)));
}

const app = express();
app.use(express.json());
app.get("/health", (_request, response) => response.json({ service: "identity", status: "ok" }));
app.use("/internal", requireInternal);
app.post("/internal/login", (request, response) => {
  const row = database.prepare("SELECT id, full_name, role, password_hash, enrolled_at FROM users WHERE id=?").get(String(request.body.userId ?? "")) as StoredUser | undefined;
  if (!row || !matchesPassword(String(request.body.password ?? ""), row.password_hash)) return response.status(401).json({ error: "Invalid credentials" });
  return response.json({ user: publicUser(row) });
});
app.get("/internal/users", (_request, response) => {
  const rows = database.prepare("SELECT id, full_name, role, password_hash, enrolled_at FROM users ORDER BY id").all() as unknown as StoredUser[];
  response.json({ users: rows.map(publicUser) });
});
app.get("/internal/users/:id", (request, response) => {
  const row = database.prepare("SELECT id, full_name, role, password_hash, enrolled_at FROM users WHERE id=?").get(request.params.id) as StoredUser | undefined;
  return row ? response.json({ user: publicUser(row) }) : response.status(404).json({ error: "User not found" });
});
app.post("/internal/users", (request, response) => {
  const { id, fullName, role, password } = request.body as { id?: string; fullName?: string; role?: Role; password?: string };
  if (!id || !fullName || !password || !["student", "teacher"].includes(role ?? "")) return response.status(400).json({ error: "Invalid user" });
  try { database.prepare("INSERT INTO users(id, full_name, role, password_hash) VALUES(?,?,?,?)").run(id.toUpperCase(), fullName.trim(), role as Role, hashPassword(password)); }
  catch { return response.status(409).json({ error: "User exists" }); }
  response.status(201).json({ user: { id: id.toUpperCase(), fullName, role } });
});
app.post("/internal/users/:id/enrollment", (request, response) => {
  database.prepare("UPDATE users SET enrolled_at=? WHERE id=? AND role='student'").run(new Date().toISOString(), request.params.id);
  response.status(204).end();
});
app.delete("/internal/users/:id/enrollment", (request, response) => {
  database.prepare("UPDATE users SET enrolled_at=NULL WHERE id=? AND role='student'").run(request.params.id);
  response.status(204).end();
});
app.listen(Number(process.env.PORT ?? 3001));
