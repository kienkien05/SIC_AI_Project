import type { AttendanceStatus } from "@spas/contracts";

export type DemoClockAction = "start" | "advance" | "reset";

export function updateDemoClock(current: number | null, action: DemoClockAction): number | null {
  if (action === "start") return 0;
  if (action === "reset") return null;
  if (current === null) throw new Error("Demo clock must start before advancing");
  return current + 5;
}

export function demoAttendanceStatus(minutesAfterStart: number): AttendanceStatus {
  if (minutesAfterStart <= 0) return "present";
  return minutesAfterStart <= 15 ? "late" : "absent";
}
