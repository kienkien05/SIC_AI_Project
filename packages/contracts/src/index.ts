export type Role = "admin" | "teacher" | "student";
export type AttendanceStatus = "present" | "late" | "absent";

export interface User { id: string; fullName: string; role: Role; }
export interface FaceMatch { studentId?: string; name?: string; score: number; }
export interface AttendanceResult { faces: number; recognizedIds: string[]; markedIds: string[]; }
