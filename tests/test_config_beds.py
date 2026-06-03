from __future__ import annotations

import unittest

from app.config_beds import BED_TYPE_FUNCS
from app.procedure_groups import PROCEDURE_GROUPS
from app.schemas import HospitalRealtime


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


class ConfigBedsTests(unittest.TestCase):
    def test_all_procedure_group_bed_types_have_configured_functions(self) -> None:
        referenced = {
            bed_type
            for group in PROCEDURE_GROUPS.values()
            for bed_type in group["bed_types"]
        }

        missing = referenced - set(BED_TYPE_FUNCS)

        self.assertEqual(missing, set())

    def test_missing_bed_values_return_zero(self) -> None:
        rt = realtime()

        for bed_type, func in BED_TYPE_FUNCS.items():
            with self.subTest(bed_type=bed_type):
                self.assertEqual(func(rt), 0)

    def test_invalid_bed_values_return_zero(self) -> None:
        cases = [
            ("er", {"er_beds": "not-a-number"}),
            ("or", {"or_beds": "not-a-number"}),
            ("icu_general", {"general_icu_beds": "not-a-number"}),
            ("icu_neonatal", {"neonatal_icu_beds": "not-a-number"}),
            ("ward", {"ward_beds": "not-a-number"}),
            ("icu_neuro", {"raw_hv": {"hv6": "not-a-number"}}),
            ("ward_psych", {"raw_hv": {"hv40": "not-a-number"}}),
        ]

        for bed_type, overrides in cases:
            with self.subTest(bed_type=bed_type):
                self.assertEqual(BED_TYPE_FUNCS[bed_type](realtime(**overrides)), 0)

    def test_negative_raw_er_value_is_preserved_on_realtime_model(self) -> None:
        rt = realtime(er_beds=-1)

        self.assertEqual(rt.er_beds, -1)

    def test_negative_bed_values_are_zero_effective_capacity(self) -> None:
        cases = [
            ("er", {"er_beds": -1}),
            ("or", {"or_beds": -1}),
            ("icu_general", {"general_icu_beds": -1}),
            ("icu_neonatal", {"neonatal_icu_beds": -1}),
            ("ward", {"ward_beds": -1}),
            ("icu_neuro", {"neuro_icu_beds": -1}),
            ("ward_psych", {"raw_hv": {"hv40": -1}}),
        ]

        for bed_type, overrides in cases:
            with self.subTest(bed_type=bed_type):
                self.assertEqual(BED_TYPE_FUNCS[bed_type](realtime(**overrides)), 0)

    def test_burn_icu_uses_hv8_as_effective_capacity(self) -> None:
        self.assertEqual(
            BED_TYPE_FUNCS["icu_burn"](realtime(raw_hv={"hv8": 4})),
            4,
        )

    def test_raw_bed_values_are_capped_by_baseline_capacity(self) -> None:
        cases = [
            (
                "icu_neuro",
                {"raw_hv": {"hv6": 5}, "baseline_hvs": {"hvs12": 3}},
                3,
            ),
            (
                "ward_psych",
                {"raw_hv": {"hv40": 7}, "baseline_hvs": {"hvs24": 2}},
                2,
            ),
        ]

        for bed_type, overrides, expected in cases:
            with self.subTest(bed_type=bed_type):
                self.assertEqual(BED_TYPE_FUNCS[bed_type](realtime(**overrides)), expected)


if __name__ == "__main__":
    unittest.main()
