"""
Data Models & Telemetry Definitions for JTAG / SWD Debug Port Lockout & Chip-Security Fuse Agent.
Domain: Hardware Security
Standard: IEEE 1149.1 / IEEE 1149.7 Standards
"""
import datetime
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any


class ExecutionStatus(str, Enum):
    NOMINAL = "NOMINAL_OPTIMAL"
    ELEVATED_RISK = "ELEVATED_RISK_WARNING"
    CRITICAL_INTERVENTION = "CRITICAL_INTERVENTION_REQUIRED"


MAX_STRING_FIELD_LENGTH = 256
MAX_METRIC_VALUE = 1e9


def _validate_payload_fields(task_id: str, target_identifier: str, primary_metric: float,
                             secondary_metric: float, status_descriptor: str) -> None:
    """Shared validation for payload fields."""
    if not task_id or not str(task_id).strip():
        raise ValueError("task_id must be a non-empty string")
    if not target_identifier or not str(target_identifier).strip():
        raise ValueError("target_identifier must be a non-empty string")
    if not status_descriptor or not str(status_descriptor).strip():
        raise ValueError("status_descriptor must be a non-empty string")
    for field_name, val in [("task_id", task_id), ("target_identifier", target_identifier), ("status_descriptor", status_descriptor)]:
        if len(str(val)) > MAX_STRING_FIELD_LENGTH:
            raise ValueError(f"{field_name} exceeds maximum length of {MAX_STRING_FIELD_LENGTH}")
    for field_name, val in [("primary_metric", primary_metric), ("secondary_metric", secondary_metric)]:
        if not math.isfinite(val):
            raise ValueError(f"{field_name} must be finite, got {val}")
        if abs(val) > MAX_METRIC_VALUE:
            raise ValueError(f"{field_name} magnitude exceeds maximum allowed ({MAX_METRIC_VALUE})")


@dataclass
class FrontierPayload:
    task_id: str
    target_identifier: str
    primary_metric: float
    secondary_metric: float
    status_descriptor: str
    is_critical_flag: bool = False
    attributes: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def __post_init__(self):
        _validate_payload_fields(
            self.task_id, self.target_identifier, self.primary_metric,
            self.secondary_metric, self.status_descriptor
        )


@dataclass
class AgentTelemetryAlert:
    alert_id: str
    origin_agent: str
    status: ExecutionStatus
    summary: str
    technical_details: str
    actionable_remediation: str
    standard_reference: str = "IEEE 1149.1 / IEEE 1149.7 Standards"
    timestamp: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "origin_agent": self.origin_agent,
            "status": self.status.value,
            "summary": self.summary,
            "technical_details": self.technical_details,
            "actionable_remediation": self.actionable_remediation,
            "standard_reference": self.standard_reference,
            "timestamp": self.timestamp,
        }
