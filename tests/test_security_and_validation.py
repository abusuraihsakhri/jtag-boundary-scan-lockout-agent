"""
Security and input validation tests for jtag-boundary-scan-lockout-agent.
"""
import sys
import math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.models import SystemTaskPayload
from jtag_lockout.models import FrontierPayload


class TestSystemTaskPayloadValidation:
    """Tests for Pydantic model validation on SystemTaskPayload."""

    def test_valid_payload(self):
        p = SystemTaskPayload(task_id="T1", target_identifier="K1", primary_metric=10.0)
        assert p.task_id == "T1"
        assert p.primary_metric == 10.0

    def test_nan_metric_rejected(self):
        with pytest.raises(ValueError, match="finite"):
            SystemTaskPayload(task_id="T1", target_identifier="K1", primary_metric=float("nan"))

    def test_infinity_metric_rejected(self):
        with pytest.raises(ValueError, match="finite"):
            SystemTaskPayload(task_id="T1", target_identifier="K1", primary_metric=float("inf"))

    def test_negative_infinity_rejected(self):
        with pytest.raises(ValueError, match="finite"):
            SystemTaskPayload(task_id="T1", target_identifier="K1", primary_metric=float("-inf"))

    def test_excessive_metric_rejected(self):
        with pytest.raises(ValueError, match="exceeds maximum"):
            SystemTaskPayload(task_id="T1", target_identifier="K1", primary_metric=1e10)

    def test_empty_task_id_rejected(self):
        with pytest.raises(ValueError):
            SystemTaskPayload(task_id="", target_identifier="K1", primary_metric=10.0)

    def test_whitespace_only_task_id_rejected(self):
        with pytest.raises(ValueError):
            SystemTaskPayload(task_id="   ", target_identifier="K1", primary_metric=10.0)

    def test_string_field_stripped(self):
        p = SystemTaskPayload(task_id="  T1  ", target_identifier="  K1  ", primary_metric=10.0)
        assert p.task_id == "T1"
        assert p.target_identifier == "K1"


class TestFrontierPayloadValidation:
    """Tests for dataclass validation on FrontierPayload."""

    def test_valid_payload(self):
        p = FrontierPayload(task_id="T1", target_identifier="K1", primary_metric=10.0,
                            secondary_metric=5.0, status_descriptor="NOMINAL")
        assert p.task_id == "T1"

    def test_nan_metric_rejected(self):
        with pytest.raises(ValueError, match="finite"):
            FrontierPayload(task_id="T1", target_identifier="K1", primary_metric=float("nan"),
                            secondary_metric=5.0, status_descriptor="NOMINAL")

    def test_infinity_metric_rejected(self):
        with pytest.raises(ValueError, match="finite"):
            FrontierPayload(task_id="T1", target_identifier="K1", primary_metric=10.0,
                            secondary_metric=float("inf"), status_descriptor="NOMINAL")

    def test_excessive_metric_rejected(self):
        with pytest.raises(ValueError, match="exceeds maximum"):
            FrontierPayload(task_id="T1", target_identifier="K1", primary_metric=1e10,
                            secondary_metric=5.0, status_descriptor="NOMINAL")

    def test_empty_task_id_rejected(self):
        with pytest.raises(ValueError, match="non-empty"):
            FrontierPayload(task_id="", target_identifier="K1", primary_metric=10.0,
                            secondary_metric=5.0, status_descriptor="NOMINAL")

    def test_empty_target_rejected(self):
        with pytest.raises(ValueError, match="non-empty"):
            FrontierPayload(task_id="T1", target_identifier="", primary_metric=10.0,
                            secondary_metric=5.0, status_descriptor="NOMINAL")

    def test_empty_status_rejected(self):
        with pytest.raises(ValueError, match="non-empty"):
            FrontierPayload(task_id="T1", target_identifier="K1", primary_metric=10.0,
                            secondary_metric=5.0, status_descriptor="")
