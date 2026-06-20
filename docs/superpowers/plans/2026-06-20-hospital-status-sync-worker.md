# Hospital Status Sync Worker Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run the existing ERMCT-to-Supabase synchronization script as an independently managed production Docker Compose worker with a configurable 300-second default interval.

**Architecture:** The shared backend Dockerfile will include `scripts/`. A new Compose service will use the backend build context, load `.env.production`, and override the image command with the sync script. Compose interpolation supplies `HOSPITAL_STATUS_SYNC_INTERVAL_SECONDS`, defaulting to `300` without changing Python or frontend behavior.

**Tech Stack:** Docker, Docker Compose, Poetry, Python `unittest`

---

### Task 1: Add a failing deployment configuration test

**Files:**
- Create: `tests/test_production_sync_worker.py`
- Read: `Dockerfile`
- Read: `docker-compose.prod.yml`
- Read: `.env.production.example`

- [ ] **Step 1: Write the failing test**

```python
from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ProductionSyncWorkerConfigTests(unittest.TestCase):
    def test_backend_image_contains_scripts(self) -> None:
        dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
        self.assertIn("COPY scripts ./scripts", dockerfile)

    def test_compose_defines_periodic_sync_worker(self) -> None:
        compose = (ROOT / "docker-compose.prod.yml").read_text(encoding="utf-8")
        self.assertIn("hospital-status-sync:", compose)
        self.assertIn("dockerfile: Dockerfile", compose)
        self.assertIn("- .env.production", compose)
        self.assertIn('"scripts/sync_hospital_status.py"', compose)
        self.assertIn(
            '"${HOSPITAL_STATUS_SYNC_INTERVAL_SECONDS:-300}"',
            compose,
        )
        self.assertIn("restart: unless-stopped", compose)

    def test_production_env_template_has_server_only_sync_settings(self) -> None:
        env_template = (ROOT / ".env.production.example").read_text(encoding="utf-8")
        for name in (
            "SUPABASE_URL",
            "SUPABASE_SERVICE_ROLE_KEY",
            "HOSPITAL_STATUS_SYNC_SIDO",
            "HOSPITAL_STATUS_SYNC_SIGUNGU",
            "HOSPITAL_STATUS_SYNC_INTERVAL_SECONDS",
        ):
            self.assertIn(f"{name}=", env_template)
        self.assertNotIn("VITE_SUPABASE_SERVICE_ROLE_KEY", env_template)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test and verify RED**

Run:

```powershell
poetry run python -m unittest tests.test_production_sync_worker -v
```

Expected: three failures because the Docker image copy, Compose worker, and server-side environment template entries do not yet exist.

### Task 2: Implement the worker deployment configuration

**Files:**
- Modify: `Dockerfile`
- Modify: `docker-compose.prod.yml`
- Modify: `.env.production.example`
- Test: `tests/test_production_sync_worker.py`

- [ ] **Step 1: Include scripts in the backend image**

Add next to the existing application copy instructions:

```dockerfile
COPY app ./app
COPY scripts ./scripts
COPY data ./data
```

- [ ] **Step 2: Add the dedicated Compose service**

Add without changing the existing backend or frontend service behavior:

```yaml
  hospital-status-sync:
    build:
      context: .
      dockerfile: Dockerfile
    env_file:
      - .env.production
    command:
      - "poetry"
      - "run"
      - "python"
      - "scripts/sync_hospital_status.py"
      - "--interval-seconds"
      - "${HOSPITAL_STATUS_SYNC_INTERVAL_SECONDS:-300}"
    restart: unless-stopped
```

- [ ] **Step 3: Document server-side worker variables**

Add to the backend section of `.env.production.example`:

```dotenv
# Hospital status sync worker (server-side only)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
HOSPITAL_STATUS_SYNC_SIDO=경기도
HOSPITAL_STATUS_SYNC_SIGUNGU=성남시
# Optional; Docker Compose defaults to 300 seconds when omitted.
HOSPITAL_STATUS_SYNC_INTERVAL_SECONDS=300
```

Do not add any `VITE_SUPABASE_SERVICE_ROLE_KEY` variable.

- [ ] **Step 4: Run the deployment test and verify GREEN**

Run:

```powershell
poetry run python -m unittest tests.test_production_sync_worker -v
```

Expected: 3 tests pass.

### Task 3: Validate the complete patch

**Files:**
- Verify: `Dockerfile`
- Verify: `docker-compose.prod.yml`
- Verify: `.env.production.example`
- Verify: `tests/test_production_sync_worker.py`

- [ ] **Step 1: Run existing sync tests**

```powershell
poetry run python -m unittest tests.test_sync_hospital_status -v
```

Expected: all sync tests pass.

- [ ] **Step 2: Run the full backend test suite**

```powershell
poetry run python -m unittest discover -s tests -v
```

Expected: all tests pass.

- [ ] **Step 3: Compile Python modules**

```powershell
poetry run python -m py_compile app/main.py app/schemas.py app/procedure_groups.py app/services/ermct_client.py app/ktas_engine.py app/stt_cleaner.py scripts/sync_hospital_status.py
```

Expected: exit code 0 with no output.

- [ ] **Step 4: Render the production Compose configuration**

```powershell
docker compose --env-file .env.production -f docker-compose.prod.yml config
```

Expected: exit code 0; rendered `hospital-status-sync` command ends in `--interval-seconds`, `300` unless overridden, and its environment includes the required server-side values without exposing the service-role key as a frontend build argument.

- [ ] **Step 5: Review the final diff and scope**

```powershell
git diff -- Dockerfile docker-compose.prod.yml .env.production.example tests/test_production_sync_worker.py
```

Expected: only worker deployment configuration, its environment template, and its focused test are changed.

