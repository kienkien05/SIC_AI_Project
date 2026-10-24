import assert from "node:assert/strict";
import test from "node:test";
import { demoAttendanceStatus, updateDemoClock } from "../src/demo-clock.ts";

test("demo clock starts at class time, advances by five minutes, and resets to real time", () => {
  assert.equal(updateDemoClock(null, "start"), 0);
  assert.equal(updateDemoClock(0, "advance"), 5);
  assert.equal(updateDemoClock(10, "reset"), null);
});

test("demo attendance status changes at the late-window boundaries", () => {
  assert.equal(demoAttendanceStatus(0), "present");
  assert.equal(demoAttendanceStatus(1), "late");
  assert.equal(demoAttendanceStatus(15), "late");
  assert.equal(demoAttendanceStatus(16), "absent");
});

test("demo clock cannot advance before it starts", () => {
  assert.throws(() => updateDemoClock(null, "advance"), /start/i);
});
