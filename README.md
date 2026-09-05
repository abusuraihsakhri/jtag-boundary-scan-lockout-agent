# Jtag Boundary Scan Lockout Agent

> **Domain:** Clinical Decision Support & Biomedical Computing  
> **Reference Guidelines & Standards:** `Standard Clinical Formulations & ISO/IEC Quality Frameworks`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

Jtag Boundary Scan Lockout Agent is an enterprise security platform that audits JTAG/SWD debug port lockout states and chip-security fuse configurations. It provides multi-agent evaluation of hardware security telemetry with HMAC-SHA256 tamper-evident audit trails and zero-PHI outbound data protection.

---

## ⚙️ Key Capabilities & Algorithmic Modules

- **JTAG/SWD Debug Port Lockout Engine**: Hardware security fuse audit and boundary scan register verification (IEEE 1149.1 / IEEE 1149.7).
- **Multi-Agent Clinical Evaluation**: InvariantQC, Safety Escalation, and Protocol Conformance workers with consensus dossier generation.
- **Zero-PHI Outbound Interceptor**: Regex-based detection blocking SSNs, MRNs, phone numbers, emails, and patient identifiers.
- **Tamper-Evident HMAC-SHA256 Audit Trail**: Chained, cryptographically signed logs for every evaluation and state transition.
- **Input Validation & Guardrails**: Finite-metric enforcement, bounds checking, and path-traversal protection on file operations.
- **Active Learning Bayesian Calibration**: Dynamic worker reliability weight tracking with Brier calibration drift monitoring.
- **FastAPI & Prometheus Telemetry**: REST endpoints with OpenAPI 3.1 spec and operational Prometheus metrics (`/metrics`).

---

## 💻 CLI Quickstart & Usage

### Installation

```bash
pip install fastapi uvicorn pydantic pytest
```

### 1. Run Single Audit Evaluation
```bash
python cli.py audit --task-id TASK-001 --target TARGET-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### 2. Batch Process CSV Records
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 3. Supervisory Chat Query
```bash
python cli.py chat "What is the system status?"
```

### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 5. Launch FastAPI REST Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Parameter Reference
| Argument | Description | Default |
|:---------|:------------|:--------|
| `--task-id` | Unique task/case identifier | `TASK-2026-001` |
| `--target` | Target entity or specimen key | `KEY-TARGET-01` |
| `--primary` | Primary domain measurement (must be finite) | `28.5` |
| `--secondary` | Secondary kinetic/confidence score (must be finite) | `14.2` |
| `--critical` | Trigger emergency escalation flag | `False` |
| `--status` | Status descriptor or phenotype code | `DISCORDANT` |
| `-i, --input` | Input CSV file path for batch processing | Required |
| `-o, --output` | Output CSV file path for batch results | `results.csv` |

### Input Data Schema

| Field | Type | Description | Requirement |
|:------|:-----|:------------|:------------|
| `task_id` | string | Unique task / case identifier (max 256 chars) | Required |
| `target_identifier` | string | Entity or specimen key (max 256 chars) | Required |
| `primary_metric` | float | Primary domain measurement (finite, ≤1e9) | Required |
| `secondary_metric` | float | Secondary kinetic score (finite, ≤1e9) | Optional (default 0.0) |
| `is_critical_flag` | bool | Emergency escalation trigger | Optional (default false) |
| `status_descriptor` | string | Status code or phenotype (max 256 chars) | Optional (default "NOMINAL") |

---

## 🛡️ Security & Architecture

* **Hardened Audit Key Management:** Uses `AUDIT_SECRET_KEY` environment variable; generates an ephemeral key with a runtime warning if unset (never hardcodes secrets).
* **Path Traversal Protection:** Batch CLI file operations are confined to the current working directory.
* **Input Sanitization:** All string fields are stripped and bounded; metric fields reject NaN, Infinity, and out-of-range values.
* **Zero-PHI Outbound Interceptor:** Blocks SSNs, MRNs, phone numbers, emails, DOB patterns, and common placeholder patient names.
* **Cryptographic HMAC-SHA256 Chaining:** Each audit entry chains to the previous hash, enabling integrity verification.
* **Prometheus Operational Metrics:** Real-time counters for tasks, alerts, PHI blocks, audit blocks, and latency.

### Environment Variables
| Variable | Description |
|:---------|:------------|
| `AUDIT_SECRET_KEY` | Secret key for HMAC-SHA256 audit signing (recommended in production) |
| `MODEL_PROVIDER` | LLM provider selection (`mock`, `ollama`, `claude`, `openai`) |

---

## 🧪 Testing & Verification

Run the full automated test suite:

```bash
pytest -v
```

Execute the high-throughput simulation benchmark (positional arg for iteration count):

```bash
python simulator.py 100
```

---

## 🐳 Container Deployment

```bash
docker build -t jtag-boundary-scan-lockout-agent .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=your-secret-key jtag-boundary-scan-lockout-agent
```
