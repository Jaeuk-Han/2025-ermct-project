from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
API_CLIENT = ROOT / "front" / "src" / "utils" / "api.ts"


class FrontendApiBaseUrlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = API_CLIENT.read_text(encoding="utf-8")

    def test_production_fallback_uses_api_prefix(self) -> None:
        self.assertIn('"/api"', self.source)
        self.assertNotIn('"http://localhost:8000"', self.source)

    def test_paths_do_not_double_prefix_api(self) -> None:
        self.assertIn('"/ktas/route/seoul"', self.source)
        self.assertNotIn('"/api/ktas/route/seoul"', self.source)
        self.assertNotIn('"/api/ktas/predict-text"', self.source)


if __name__ == "__main__":
    unittest.main()
