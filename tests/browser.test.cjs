"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { evaluate } = require("../web/app.js");
const input = {
  task_id: "T1", target_identifier: "DEVICE-1",
  primary_metric: 0, secondary_metric: 0,
  status_descriptor: "NOMINAL", is_critical_flag: false
};

test("nominal data produces no alerts", () => {
  const result = evaluate(input);
  assert.equal(result.overall_status, "NOMINAL_OPTIMAL");
  assert.equal(result.total_alerts, 0);
});
test("primary and secondary thresholds are exclusive", () => {
  assert.equal(evaluate({ ...input, primary_metric: 25, secondary_metric: 10 }).total_alerts, 0);
  const result = evaluate({ ...input, primary_metric: 26, secondary_metric: 11 });
  assert.equal(result.total_alerts, 2);
  assert.equal(result.warning_count, 2);
});
test("critical flag takes precedence", () => {
  const result = evaluate({ ...input, is_critical_flag: true });
  assert.equal(result.overall_status, "CRITICAL_INTERVENTION_REQUIRED");
  assert.equal(result.critical_count, 1);
});
test("anomaly matching is case insensitive", () => {
  assert.equal(evaluate({ ...input, status_descriptor: "lockout_ViOlAtIoN" }).total_alerts, 1);
});
test("invalid payload is rejected rather than labeled nominal", () => {
  for (const invalid of [
    { ...input, primary_metric: NaN },
    { ...input, secondary_metric: Infinity },
    { ...input, primary_metric: 1e10 },
    { ...input, task_id: " " },
    { ...input, target_identifier: "X".repeat(257) },
    { ...input, status_descriptor: "" },
    { ...input, is_critical_flag: "false" },
    { ...input, primary_metric: "20" }
  ]) assert.throws(() => evaluate(invalid));
});
test("browser entrypoint and offline script exist", () => {
  const root = fs.readFileSync(path.join(__dirname, "..", "index.html"), "utf8");
  const page = fs.readFileSync(path.join(__dirname, "..", "web", "index.html"), "utf8");
  assert.match(root, /\.\/web\//);
  assert.match(page, /src="\.\/app\.js"/);
  assert.match(page, /id="audit-form"/);
  assert.doesNotMatch(page, /fetch\s*\(/);
});
