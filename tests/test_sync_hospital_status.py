from __future__ import annotations

import argparse
import contextlib
import io
import os
import unittest
from unittest.mock import patch

from app.schemas import HospitalRealtime
from scripts.sync_hospital_status import (
    bed_services_summary,
    normalize_hospital_status,
    parse_args,
    parse_sync_targets,
    parse_target_delay_seconds,
    resolve_sync_targets,
    run_sync_cycle,
    main,
    status_summary,
    sanitize_error_text,
    verbose_status_line,
    safe_int,
)


def realtime(**overrides):
    values = {
        "id": "H001",
        "name": "Test Hospital",
        "raw_hv": {},
        "baseline_hvs": {},
    }
    values.update(overrides)

    construct = getattr(HospitalRealtime, "model_construct", None)
    if construct is not None:
        return construct(**values)
    return HospitalRealtime.construct(**values)


class SyncHospitalStatusTests(unittest.TestCase):
    def test_main_rejects_malformed_targets_before_sync(self) -> None:
        env = {
            "ERMCT_SERVICE_KEY": "test-only",
            "SUPABASE_URL": "https://example.supabase.co",
            "SUPABASE_SERVICE_ROLE_KEY": "test-only",
            "HOSPITAL_STATUS_SYNC_TARGETS": "서울특별시",
        }
        output = io.StringIO()

        with (
            patch.dict(os.environ, env, clear=True),
            patch("scripts.sync_hospital_status.run_sync_once") as sync_once,
            contextlib.redirect_stdout(output),
        ):
            result = main([])

        self.assertEqual(result, 2)
        sync_once.assert_not_called()
        self.assertIn("Invalid sync configuration", output.getvalue())
        self.assertIn("HOSPITAL_STATUS_SYNC_TARGETS", output.getvalue())

    def test_main_one_shot_runs_full_target_cycle(self) -> None:
        env = {
            "ERMCT_SERVICE_KEY": "test-only",
            "SUPABASE_URL": "https://example.supabase.co",
            "SUPABASE_SERVICE_ROLE_KEY": "test-only",
            "HOSPITAL_STATUS_SYNC_TARGETS": ("서울특별시:강남구,서울특별시:서초구"),
            "HOSPITAL_STATUS_SYNC_TARGET_DELAY_SECONDS": "4",
        }

        with (
            patch.dict(os.environ, env, clear=True),
            patch(
                "scripts.sync_hospital_status.run_sync_cycle",
                return_value=1,
            ) as sync_cycle,
            patch(
                "scripts.sync_hospital_status.run_sync_once",
                return_value=0,
            ),
        ):
            result = main([])

        self.assertEqual(result, 1)
        sync_cycle.assert_called_once()
        self.assertEqual(
            sync_cycle.call_args.args[1],
            [("서울특별시", "강남구"), ("서울특별시", "서초구")],
        )
        self.assertEqual(sync_cycle.call_args.args[2], 4)

    def test_main_interval_mode_retries_after_failed_cycle(self) -> None:
        env = {
            "ERMCT_SERVICE_KEY": "test-only",
            "SUPABASE_URL": "https://example.supabase.co",
            "SUPABASE_SERVICE_ROLE_KEY": "test-only",
            "HOSPITAL_STATUS_SYNC_TARGETS": "서울특별시:강남구",
        }

        with (
            patch.dict(os.environ, env, clear=True),
            patch(
                "scripts.sync_hospital_status.run_sync_cycle",
                return_value=1,
            ) as sync_cycle,
            patch(
                "scripts.sync_hospital_status.run_sync_once",
                return_value=1,
            ),
            patch(
                "scripts.sync_hospital_status.time.sleep",
                side_effect=StopIteration,
            ),
            self.assertRaises(StopIteration),
        ):
            main(["--interval-seconds", "900"])

        sync_cycle.assert_called_once()

    def test_parse_sync_targets_preserves_order_and_trims_values(self) -> None:
        self.assertEqual(
            parse_sync_targets(" 서울특별시:강남구,서울특별시:서초구 "),
            [("서울특별시", "강남구"), ("서울특별시", "서초구")],
        )

    def test_parse_sync_targets_rejects_malformed_or_empty_pairs(self) -> None:
        invalid_values = (
            "서울특별시",
            ":강남구",
            "서울특별시:",
            "서울특별시:강남구,",
            "서울특별시:강남구:extra",
        )

        for value in invalid_values:
            with (
                self.subTest(value=value),
                self.assertRaisesRegex(
                    ValueError,
                    "HOSPITAL_STATUS_SYNC_TARGETS",
                ),
            ):
                parse_sync_targets(value)

    def test_resolve_sync_targets_uses_legacy_single_region_when_targets_empty(
        self,
    ) -> None:
        args = argparse.Namespace(sido=None, sigungu=None)
        env = {
            "HOSPITAL_STATUS_SYNC_TARGETS": "  ",
            "HOSPITAL_STATUS_SYNC_SIDO": "경기도",
            "HOSPITAL_STATUS_SYNC_SIGUNGU": "성남시",
        }

        self.assertEqual(resolve_sync_targets(args, env), [("경기도", "성남시")])

    def test_resolve_sync_targets_prefers_multi_target_configuration(self) -> None:
        args = argparse.Namespace(sido="경기도", sigungu="성남시")
        env = {
            "HOSPITAL_STATUS_SYNC_TARGETS": ("서울특별시:강남구,서울특별시:서초구"),
        }

        self.assertEqual(
            resolve_sync_targets(args, env),
            [("서울특별시", "강남구"), ("서울특별시", "서초구")],
        )

    def test_target_delay_defaults_to_three_and_accepts_non_negative_values(
        self,
    ) -> None:
        self.assertEqual(parse_target_delay_seconds(None), 3)
        self.assertEqual(parse_target_delay_seconds(""), 3)
        self.assertEqual(parse_target_delay_seconds("0"), 0)
        self.assertEqual(parse_target_delay_seconds(" 7 "), 7)

    def test_target_delay_rejects_negative_or_non_integer_values(self) -> None:
        for value in ("-1", "abc", "1.5"):
            with (
                self.subTest(value=value),
                self.assertRaisesRegex(
                    ValueError,
                    "HOSPITAL_STATUS_SYNC_TARGET_DELAY_SECONDS",
                ),
            ):
                parse_target_delay_seconds(value)

    def test_run_sync_cycle_processes_targets_sequentially_and_delays_between(
        self,
    ) -> None:
        args = argparse.Namespace()
        calls = []
        sleeps = []

        def sync_fn(_args, *, sido, sigungu):
            calls.append((sido, sigungu))
            return 0

        result = run_sync_cycle(
            args,
            [("서울특별시", "강남구"), ("서울특별시", "서초구")],
            target_delay_seconds=3,
            sync_fn=sync_fn,
            sleep_fn=sleeps.append,
        )

        self.assertEqual(result, 0)
        self.assertEqual(
            calls,
            [("서울특별시", "강남구"), ("서울특별시", "서초구")],
        )
        self.assertEqual(sleeps, [3])

    def test_run_sync_cycle_continues_after_failure_and_reports_partial_failure(
        self,
    ) -> None:
        args = argparse.Namespace()
        calls = []

        def sync_fn(_args, *, sido, sigungu):
            calls.append((sido, sigungu))
            return 1 if sigungu == "강남구" else 0

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = run_sync_cycle(
                args,
                [("서울특별시", "강남구"), ("서울특별시", "서초구")],
                target_delay_seconds=0,
                sync_fn=sync_fn,
            )

        self.assertEqual(result, 1)
        self.assertEqual(
            calls,
            [("서울특별시", "강남구"), ("서울특별시", "서초구")],
        )
        self.assertIn("target=서울특별시:강남구 status=failed", output.getvalue())
        self.assertIn("target=서울특별시:서초구 status=success", output.getvalue())
        self.assertIn("total_targets=2", output.getvalue())
        self.assertIn("succeeded_targets=1", output.getvalue())
        self.assertIn("failed_targets=1", output.getvalue())
        self.assertIn("status=partial-failed", output.getvalue())

    def test_run_sync_cycle_catches_target_exception_and_continues(self) -> None:
        args = argparse.Namespace()
        calls = []

        def sync_fn(_args, *, sido, sigungu):
            calls.append((sido, sigungu))
            if sigungu == "강남구":
                raise RuntimeError("temporary failure")
            return 0

        result = run_sync_cycle(
            args,
            [("서울특별시", "강남구"), ("서울특별시", "서초구")],
            target_delay_seconds=0,
            sync_fn=sync_fn,
        )

        self.assertEqual(result, 1)
        self.assertEqual(len(calls), 2)

    def test_safe_int_handles_missing_and_invalid_values(self) -> None:
        self.assertEqual(safe_int(None), 0)
        self.assertEqual(safe_int(""), 0)
        self.assertEqual(safe_int("not-a-number"), 0)
        self.assertEqual(safe_int(" 7 "), 7)

    def test_normalize_hospital_status_clamps_negative_display_values(self) -> None:
        status = normalize_hospital_status(
            realtime(
                er_beds=-1,
                general_icu_beds="-2",
                neonatal_icu_beds=3,
                raw_hv={"hv29": "-4", "hv30": 5},
                baseline_hvs={"hvs01": 10, "hvs16": 4, "hvs17": 6},
            )
        )

        self.assertEqual(status["er_available_beds"], 0)
        self.assertEqual(status["icu_available_beds"], 3)
        self.assertEqual(status["isolation_available_beds"], 5)
        self.assertEqual(status["available_beds"], 8)
        self.assertTrue(status["is_accepting"])

    def test_normalize_hospital_status_builds_bed_services(self) -> None:
        status = normalize_hospital_status(
            realtime(
                er_beds="2",
                general_icu_beds="1",
                raw_hv={"hv29": 4},
                baseline_hvs={"hvs01": 7, "hvs16": 3},
            )
        )

        self.assertEqual(
            status["bed_services"],
            [
                {"name": "ER", "available": 2, "total": 7},
                {"name": "ICU", "available": 1, "total": 3},
                {"name": "Isolation", "available": 4, "total": 4},
            ],
        )

    def test_bed_services_summary_formats_services_compactly(self) -> None:
        services = [
            {"name": "ER", "available": 2, "total": 7},
            {"name": "ICU", "available": 1, "total": 3},
        ]

        self.assertEqual(bed_services_summary(services), "ER 2/7, ICU 1/3")

    def test_verbose_status_line_includes_required_fields(self) -> None:
        hospital = {"id": "A2116806", "name": "Seongnam Medical Center"}
        status = {
            "hospital_id": "A2116806",
            "available_beds": 3,
            "total_beds": 10,
            "bed_services": [
                {"name": "ER", "available": 2, "total": 7},
                {"name": "ICU", "available": 1, "total": 3},
            ],
        }

        self.assertEqual(
            verbose_status_line(hospital, status),
            "A2116806 | Seongnam Medical Center | available_beds=3 | "
            "total_beds=10 | services=ER 2/7, ICU 1/3",
        )

    def test_status_summary_counts_accepting_and_available_beds(self) -> None:
        rows = [
            {"available_beds": 3, "is_accepting": True},
            {"available_beds": 0, "is_accepting": False},
            {"available_beds": "4", "is_accepting": True},
        ]

        self.assertEqual(
            status_summary(rows),
            {
                "fetched_count": 3,
                "accepting_count": 2,
                "total_available_beds": 7,
            },
        )

    def test_normalize_hospital_status_never_reports_total_below_available(
        self,
    ) -> None:
        status = normalize_hospital_status(
            realtime(
                er_beds=11,
                raw_hv={"hv29": 34},
                baseline_hvs={"hvs01": 1, "hvs18": 5},
            )
        )

        self.assertEqual(status["er_total_beds"], 11)
        self.assertEqual(status["isolation_total_beds"], 34)
        self.assertEqual(status["total_beds"], status["available_beds"])

    def test_sanitize_error_text_redacts_service_key(self) -> None:
        raw = "url?serviceKey=secret-value&STAGE1=x"

        self.assertEqual(
            sanitize_error_text(raw),
            "url?serviceKey=<redacted>&STAGE1=x",
        )

    def test_parse_args_defaults_to_once_without_interval(self) -> None:
        args = parse_args([])

        self.assertTrue(args.once)
        self.assertIsNone(args.interval_seconds)

    def test_parse_args_accepts_positive_interval(self) -> None:
        args = parse_args(["--interval-seconds", "300"])

        self.assertEqual(args.interval_seconds, 300)

    def test_parse_args_rejects_non_positive_interval(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            parse_args(["--interval-seconds", "0"])


if __name__ == "__main__":
    unittest.main()
