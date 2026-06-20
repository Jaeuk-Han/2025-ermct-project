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
            "HOSPITAL_STATUS_SYNC_TARGETS",
            "HOSPITAL_STATUS_SYNC_TARGET_DELAY_SECONDS",
        ):
            self.assertIn(f"{name}=", env_template)
        self.assertIn("HOSPITAL_STATUS_SYNC_TARGETS=", env_template.splitlines())
        self.assertIn("# Seoul example (all districts):", env_template)
        self.assertNotIn("VITE_SUPABASE_SERVICE_ROLE_KEY", env_template)


if __name__ == "__main__":
    unittest.main()
