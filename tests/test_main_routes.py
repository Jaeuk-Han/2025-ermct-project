from __future__ import annotations

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _route_sources() -> list[Path]:
    sources = [ROOT / "app" / "main.py"]
    routers_dir = ROOT / "app" / "routers"
    if routers_dir.exists():
        sources.extend(sorted(routers_dir.glob("*.py")))
    return sources


def _call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _response_model(node: ast.Call) -> str | None:
    for keyword in node.keywords:
        if keyword.arg == "response_model":
            return ast.unparse(keyword.value)
    return None


def _declared_routes() -> dict[tuple[str, str], str | None]:
    routes: dict[tuple[str, str], str | None] = {}
    for source in _route_sources():
        tree = ast.parse(source.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for decorator in node.decorator_list:
                if not isinstance(decorator, ast.Call):
                    continue
                method = _call_name(decorator.func)
                if method not in {"get", "post"}:
                    continue
                if not decorator.args or not isinstance(decorator.args[0], ast.Constant):
                    continue
                path = decorator.args[0].value
                if not isinstance(path, str):
                    continue
                routes[(path, method.upper())] = _response_model(decorator)
    return routes


class MainRouteContractTests(unittest.TestCase):
    def test_cors_origins_are_environment_driven(self) -> None:
        source = (ROOT / "app" / "main.py").read_text(encoding="utf-8")

        self.assertIn("CORS_ALLOW_ORIGINS", source)
        self.assertNotIn('allow_origins=["*"]', source)

    def test_existing_route_methods_and_response_models_are_declared(self) -> None:
        expected = {
            ("/health", "GET"): None,
            ("/api/hospitals/realtime", "GET"): "list[HospitalRealtime]",
            ("/debug/hospitals/realtime/xml", "GET"): None,
            ("/api/hospitals/basic", "GET"): "HospitalBasicInfo | None",
            ("/api/hospitals/serious", "GET"): "list[SeriousDiseaseStatus]",
            ("/api/hospitals/messages", "GET"): "list[HospitalMessage]",
            ("/api/hospitals/summary", "GET"): "HospitalSummary",
            ("/debug/hospitals/serious/xml", "GET"): None,
            ("/api/hospitals/summary/by-region", "GET"): "list[HospitalSummary]",
            ("/api/triage/recommend", "POST"): "list[RecommendedHospital]",
            ("/api/hospitals/trauma/by-region", "GET"): "List[TraumaCenter]",
            (
                "/api/hospitals/complaint-coverage/by-region",
                "GET",
            ): "list[HospitalComplaintCoverage]",
            ("/api/triage/candidates", "POST"): "RoutingCandidateResponse",
            (
                "/api/hospitals/procedure-beds/by-region",
                "GET",
            ): "List[HospitalProcedureBeds]",
            ("/api/triage/reservations", "POST"): None,
            ("/api/triage/reservations/release", "POST"): None,
            ("/debug/triage/pending-assignments", "GET"): None,
            ("/api/ktas/route/seoul", "POST"): "RoutingCandidateResponse",
            ("/api/ktas/route/seoul/nearest", "POST"): "RoutingCandidateResponse",
            ("/api/ktas/route/path", "POST"): "RoutePathResponse",
            ("/api/ktas/predict-audio", "POST"): "RoutingCandidateResponse",
            ("/api/ktas/predict-text", "POST"): "RoutingCandidateResponse",
        }

        routes = _declared_routes()

        self.assertEqual({key: routes.get(key) for key in expected}, expected)


if __name__ == "__main__":
    unittest.main()
