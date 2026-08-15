import type { Role } from "@spas/contracts";

export type SeedUser = { id: string; fullName: string; role: Role; password: string };

export const seedUsers: SeedUser[] = [
  { id: "ADMIN001", fullName: "Quản trị SPAS", role: "admin", password: "admin123" },
  { id: "GV001", fullName: "Nguyễn Minh An", role: "teacher", password: "gv123" },
  { id: "GV002", fullName: "Trần Thu Hà", role: "teacher", password: "gv123" },
  { id: "SV001", fullName: "Trương Trung Kiên", role: "student", password: "sv123" },
  { id: "SV002", fullName: "Lê Minh Quang", role: "student", password: "sv123" },
  { id: "SV003", fullName: "Nguyễn Lan Anh", role: "student", password: "sv123" }
];
