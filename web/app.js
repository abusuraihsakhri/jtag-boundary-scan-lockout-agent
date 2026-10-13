/* Deterministic offline telemetry classification. No hardware communication occurs. */
"use strict";
(function (root) {
  const LIMIT = 1e9;
  const MAX_TEXT = 256;
  const SPEC = "IEEE 1149.1 / IEEE 1149.7 (context only; no conformance certification)";

  function validateText(value, field) {
    if (typeof value !== "string" || !value.trim() || value.length > MAX_TEXT) {
      throw new Error(field + " must be 1–256 non-whitespace characters.");
    }
    return value.trim();
  }

  function validateMetric(value, field) {
    if (typeof value !== "number" || !Number.isFinite(value) || Math.abs(value) > LIMIT) {
      throw new Error(field + " must be a finite number with absolute value at most 1e9.");
    }
    return value;
  }

  function evaluate(input) {
    if (!input || typeof input !== "object") throw new Error("A task payload is required.");
    const task_id = validateText(input.task_id, "Task ID");
    const target_identifier = validateText(input.target_identifier, "Target identifier");
    const status_descriptor = validateText(input.status_descriptor, "Status descriptor");
    const primary_metric = validateMetric(input.primary_metric, "Primary metric");
    const secondary_metric = validateMetric(input.secondary_metric, "Secondary metric");
    if (typeof input.is_critical_flag !== "boolean") throw new Error("Critical flag must be boolean.");
    const alerts = [];
    function push(origin, status, summary, details, remediation) {
      alerts.push({
        origin_agent: origin, status, summary,
        technical_details: details, actionable_remediation: remediation,
        standard_reference: SPEC
      });
    }

    if (primary_metric > 25) {
      push("TAPStateMachineAgent", "ELEVATED_RISK_WARNING",
        "Primary Domain Boundary Deviation",
        "Parameter " + primary_metric.toFixed(3) + " exceeds illustrative threshold 25.0.",
        "Review source telemetry and applicable device-specific limits.");
    }
    if (secondary_metric > 10 || input.is_critical_flag) {
      push("BoundaryScanRegisterAgent",
        input.is_critical_flag ? "CRITICAL_INTERVENTION_REQUIRED" : "ELEVATED_RISK_WARNING",
        "Critical Domain Condition Triggered",
        "Secondary index " + secondary_metric.toFixed(3) + "; CriticalFlag=" + input.is_critical_flag + ".",
        "Review lockout status and escalate to an authorized hardware engineer.");
    }
    if (["VIOLATION", "DISCORDANT", "ANOMALY", "MUTANT", "LEAK"].some(x => status_descriptor.toUpperCase().includes(x))) {
      push("eFuseLockoutAuditorAgent", "ELEVATED_RISK_WARNING",
        "Specification / Protocol Anomaly Identified",
        "Telemetry descriptor '" + status_descriptor + "' contains an anomaly indicator.",
        "Confirm using authenticated device logs and manufacturer documentation.");
    }

    const critical_count = alerts.filter(a => a.status === "CRITICAL_INTERVENTION_REQUIRED").length;
    const warning_count = alerts.length - critical_count;
    const overall_status = critical_count ? "CRITICAL_INTERVENTION_REQUIRED" :
      warning_count ? "ELEVATED_RISK_WARNING" : "NOMINAL_OPTIMAL";
    return {
      system: "jtag-boundary-scan-lockout-agent", domain: "Hardware Security",
      task_id, target_identifier, overall_status,
      total_alerts: alerts.length, critical_count, warning_count, alerts,
      standard_specification: SPEC,
      consensus_summary: "Rule-based evaluation across 3 checks: " + overall_status + ".",
      limitations: "Illustrative thresholds only. No JTAG/SWD probe, hardware access, eFuse readout, or IEEE certification."
    };
  }

  if (typeof module === "object" && module.exports) module.exports = { evaluate };
  root.JtagAudit = { evaluate };
  if (typeof document === "undefined") return;

  const form = document.getElementById("audit-form");
  if (!form) return;
  const output = document.getElementById("output");
  const status = document.getElementById("status");
  const counter = document.getElementById("count");
  const download = document.getElementById("download");
  let lastResult = null;
  let count = 0;

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    try {
      const payload = {
        task_id: form.elements.task_id.value,
        target_identifier: form.elements.target_identifier.value,
        primary_metric: Number(form.elements.primary_metric.value),
        secondary_metric: Number(form.elements.secondary_metric.value),
        status_descriptor: form.elements.status_descriptor.value,
        is_critical_flag: form.elements.is_critical_flag.checked
      };
      if (!form.elements.primary_metric.value.trim() || !form.elements.secondary_metric.value.trim()) {
        throw new Error("Both metrics are required.");
      }
      lastResult = evaluate(payload);
      output.textContent = JSON.stringify(lastResult, null, 2);
      status.textContent = lastResult.overall_status;
      count += 1;
      counter.textContent = String(count);
      download.disabled = false;
    } catch (error) {
      lastResult = null;
      output.textContent = "Validation error: " + error.message;
      status.textContent = "INPUT ERROR";
      download.disabled = true;
    }
  });

  download.addEventListener("click", function () {
    if (!lastResult) return;
    const blob = new Blob([JSON.stringify(lastResult, null, 2) + "\n"], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "jtag-audit.json";
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(url);
  });
})(typeof globalThis !== "undefined" ? globalThis : this);
