import type { Role } from "@spas/contracts";

export type SeedUser = { id: string; fullName: string; role: Role; password: string };

export const seedUsers: SeedUser[] = [
  { id: "ADMIN001", fullName: "Quản trị SPAS", role: "admin", password: "admin123" },
  { id: "GV001", fullName: "Nguyễn Minh An", role: "teacher", password: "gv123" },
  { id: "GV002", fullName: "Trần Thu Hà", role: "teacher", password: "gv123" },
  { id: "GV003", fullName: "Lê Hoài Nam", role: "teacher", password: "gv123" },
  { id: "SV001", fullName: "Trương Trung Kiên", role: "student", password: "sv123" },
  { id: "SV002", fullName: "Lê Minh Quang", role: "student", password: "sv123" },
  { id: "SV003", fullName: "Nguyễn Lan Anh", role: "student", password: "sv123" },
  { id: "SV004", fullName: "Phạm Gia Huy", role: "student", password: "sv123" },
  { id: "SV005", fullName: "Vũ Ngọc Mai", role: "student", password: "sv123" },
  { id: "SV006", fullName: "Đỗ Thành Long", role: "student", password: "sv123" },
  { id: "SV007", fullName: "Hoàng Thu Trang", role: "student", password: "sv123" },
  { id: "SV008", fullName: "Bùi Đức Anh", role: "student", password: "sv123" }
];
