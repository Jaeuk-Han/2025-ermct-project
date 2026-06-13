from __future__ import annotations

import unittest
from io import StringIO
from unittest.mock import patch

from app.stt_cleaner import is_likely_stt_hallucination, transcribe_clean_and_match_hospital


class STTCleanerTests(unittest.TestCase):
    def test_invalid_thanks_only(self) -> None:
        self.assertTrue(is_likely_stt_hallucination("감사합니다."))

    def test_invalid_repeated_thanks(self) -> None:
        self.assertTrue(is_likely_stt_hallucination("감사합니다. 감사합니다."))

    def test_invalid_youtube_outro(self) -> None:
        self.assertTrue(is_likely_stt_hallucination("시청해주셔서 감사합니다."))

    def test_invalid_short_fillers(self) -> None:
        for text in ("네", "음", "어", ""):
            with self.subTest(text=text):
                self.assertTrue(is_likely_stt_hallucination(text))

    def test_valid_symptom_text(self) -> None:
        self.assertFalse(
            is_likely_stt_hallucination("환자가 숨을 잘 못 쉬고 산소포화도가 낮습니다.")
        )

    def test_valid_chest_pain_text(self) -> None:
        self.assertFalse(
            is_likely_stt_hallucination("가슴 통증이 심하고 식은땀이 납니다.")
        )

    def test_valid_long_sentence_with_thanks_is_not_blocked(self) -> None:
        self.assertFalse(
            is_likely_stt_hallucination(
                "환자가 호흡곤란이 있고 산소포화도가 낮습니다 감사합니다"
            )
        )


    def test_audio_flow_does_not_print_sensitive_text_or_hospital_names(self) -> None:
        raw_text = "PRIVATE_RAW_PATIENT has chest pain and dyspnea"
        clean_text = "PRIVATE_CLEAN_PATIENT has chest pain and dyspnea"
        raw_hospital = "PRIVATE_RAW_HOSPITAL"
        final_hospital = "PRIVATE_FINAL_HOSPITAL"

        with (
            patch("app.stt_cleaner.speech_to_text", return_value=raw_text),
            patch("app.stt_cleaner.llm_clean_text", return_value=clean_text),
            patch("app.stt_cleaner.extract_followup_hospital", return_value=raw_hospital),
            patch("app.stt_cleaner.best_match_hospital", return_value=final_hospital),
            patch("app.stt_cleaner.run_ktas_engine", return_value={"ktas": 3}),
            patch("sys.stdout", new_callable=StringIO) as stdout,
        ):
            transcribe_clean_and_match_hospital("audio.webm", ktas_method="rag_based")

        output = stdout.getvalue()
        self.assertNotIn(raw_text, output)
        self.assertNotIn(clean_text, output)
        self.assertNotIn(raw_hospital, output)
        self.assertNotIn(final_hospital, output)


if __name__ == "__main__":
    unittest.main()
