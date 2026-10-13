# JTAG Boundary Scan Lockout Agent

A rule-based evaluator for JTAG/SWD-related security telemetry. Includes a fully offline browser UI, two Python command-line interfaces, a FastAPI service, and regression tests.

**Scope:** The evaluator classifies user-supplied measurements and descriptors. It does **not** connect to JTAG hardware, read eFuses, establish chip security, verify debug-port lockout, or certify conformance to IEEE 1149.1/1149.7. The numeric thresholds are **illustrative application rules**, not IEEE limits.

## Browser application

Open `web/index.html` locally, or `index.html` for the repository-root entry point when it is published as a static website. The app needs no server or Python runtime.

1. Enter a task ID, device identifier, two numeric metrics, a status descriptor, and an optional critical flag.
2. Select **Evaluate** to get rule-based findings.
3. Select **Export JSON** to save the evaluation result.

The browser uses the legacy `jtag_lockout` thresholds: **primary > 25**, **secondary > 10**, critical flag escalation, and descriptor indicators `VIOLATION`, `DISCORDANT`, `ANOMALY`, `MUTANT`, or `LEAK`. Fields are validated before evaluation. Browser results do not contain a server-side HMAC audit signature.

**Privacy:** Browser data is processed locally and is not transmitted or retained by the app. Downloads are initiated in your browser. Do not enter confidential security or personal information on untrusted devices.

## Python setup

Requires Python 3.10 or newer.

```bash
python -m pip install -e ".[api,dev]"
python -m pytest -q
```

The project preserves two historical engines with **different** decision thresholds and result schemas:

| Entry point | Implementation | Secondary threshold | Output |
| --- | --- | --- | --- |
| `jtag-boundary-scan-lockout-engine` | `jtag_lockout` | > 10 | JTAG-oriented alert dossier |
| `jtag-lockout-agent` / `python cli.py` | `agents` | > 12 | Supervisor dossier with in-memory HMAC audit reference |

Both flag primary metrics > 25. A critical flag escalates. Do not assume outputs from the two engines are interchangeable.

### CLI examples

```bash
python cli.py audit --task-id T001 --target DEVICE-1 --primary 28 --secondary 13 --status DISCORDANT
python cli.py batch -i sample.csv -o results.csv
python cli.py chat "status"
python cli.py verify-audit
python -m jtag_lockout.cli audit --primary 28 --secondary 11
```

`verify-audit` checks the **current process's in-memory** audit trail; it does not recover previous runs from disk. The `chat` command is a deterministic reference reply, not a device interrogation or an external AI service.

### HTTP service

```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

Endpoints: `GET /health`, `GET /metrics` (JSON counters), `POST /api/audit`, `POST /api/chat`, and `GET /api/audit/logs`. Interactive API documentation is served at `/docs`.

**Deployment caution:** The API does not authenticate requests. Bind it to localhost or place it behind authenticated access controls. Its audit logs and task registry are process-local; the regex identifier filter is **not** complete PII/PHI de-identification. Never expose this service directly to the internet.

### Container usage

```bash
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
docker compose up --build
```

Compose binds the API to `127.0.0.1:8000`. Set your own persistent secret via a secret manager for deployments and rotate any previously published keys. Omitting the key fails Compose configuration rather than using a fixed repository credential.

## Verification

```bash
python -m pytest -q
node --test tests/browser.test.cjs
python -m compileall -q agents jtag_lockout
```

GitHub Actions exercises Python 3.10–3.13, browser rule tests, packaging, and HMAC tamper detection.

## Technical notes

- Python: Pydantic 2, optional FastAPI/Uvicorn service.
- Browser: plain JavaScript, HTML, and CSS. No Pyodide or server-side Python required.
- Browser compatibility: current evergreen desktop and mobile browsers supporting ES2017 and Blob downloads.
- Security assurance: HMAC chaining detects modifications to in-memory signed metadata, but it does not constitute a durable, externally anchored audit log.
- Hardware validation must be performed separately using authorized probes, device documentation, and target-specific test protocols.

## License

MIT; see [LICENSE](LICENSE).
