from __future__ import annotations

import json
import math
from pathlib import Path
from types import SimpleNamespace
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from scripts.build_ktas_detail_embedding_index import (
    EmbeddingBuildError,
    build_embedding_index,
    load_detail_items,
    main,
)


def detail(key: str, row_code: str, text: str) -> dict:
    category_code, complaint_code, detail_code = key.split(":")
    return {
        "row_code": row_code,
        "detail_key": key,
        "category_code": category_code,
        "category_label": "환경손상",
        "complaint_code": complaint_code,
        "complaint_label": "저체온증",
        "detail_code": detail_code,
        "detail_label": "중증 호흡곤란",
        "canonical_path": "환경손상 > 저체온증 > 중증 호흡곤란",
        "ktas": 1,
        "routing_text": text,
    }


class StubEmbeddings:
    def __init__(self, fail: Exception | None = None) -> None:
        self.inputs: list[list[str]] = []
        self.models: list[str] = []
        self.fail = fail

    def create(self, *, model: str, input: list[str]):
        if self.fail:
            raise self.fail
        self.models.append(model)
        self.inputs.append(input)
        data = [
            SimpleNamespace(index=index, embedding=[float(index + 1), 0.5])
            for index in reversed(range(len(input)))
        ]
        return SimpleNamespace(data=data)


class StubClient:
    def __init__(self, fail: Exception | None = None) -> None:
        self.embeddings = StubEmbeddings(fail)


class LoadDetailItemsTests(unittest.TestCase):
    def write(self, directory: str, payload: object) -> Path:
        path = Path(directory) / "routing.json"
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        return path

    def test_loads_only_sorted_detail_index(self) -> None:
        with TemporaryDirectory() as directory:
            path = self.write(directory, {
                "category_index": [{"routing_text": "DO NOT EMBED CATEGORY"}],
                "complaint_index": [{"routing_text": "DO NOT EMBED COMPLAINT"}],
                "detail_index": [
                    detail("P:B:AD", "CPBAD", "shock text"),
                    detail("O:F:AA", "COFAA", "breathing text"),
                ],
            })
            items = load_detail_items(path)
        self.assertEqual(["COFAA", "CPBAD"], [item["row_code"] for item in items])

    def test_rejects_missing_or_invalid_detail_data(self) -> None:
        with TemporaryDirectory() as directory:
            for payload, message in (
                ({}, "detail_index"),
                ({"detail_index": {}}, "detail_index"),
                ({"detail_index": [{**detail("O:F:AA", "COFAA", "x"), "row_code": None}]}, "row_code"),
                ({"detail_index": [detail("O:F:AA", "COFAA", " ")]}, "routing_text"),
            ):
                with self.subTest(message=message):
                    with self.assertRaisesRegex(ValueError, message):
                        load_detail_items(self.write(directory, payload))


class BuildEmbeddingIndexTests(unittest.TestCase):
    def test_batches_text_and_preserves_metadata(self) -> None:
        client = StubClient()
        details = [
            detail("O:F:AA", "COFAA", "breathing text"),
            detail("P:A:BG", "CPABG", "pain text"),
            detail("P:B:AD", "CPBAD", "shock text"),
        ]
        result = build_embedding_index(details, client, "text-embedding-3-large", 2, "data/ktas_routing_index.json")
        self.assertEqual([["breathing text", "pain text"], ["shock text"]], client.embeddings.inputs)
        self.assertEqual("COFAA", result["items"][0]["row_code"])
        self.assertEqual("O:F:AA", result["items"][0]["detail_key"])
        self.assertEqual(1, result["items"][0]["ktas"])
        self.assertEqual([1.0, 0.5], result["items"][0]["embedding"])
        self.assertEqual(result["stats"]["detail_row_count"], result["stats"]["embedding_count"])

    def test_wraps_api_failure_clearly(self) -> None:
        with self.assertRaisesRegex(EmbeddingBuildError, "embedding API request failed: RuntimeError: unavailable"):
            build_embedding_index([detail("O:F:AA", "COFAA", "text")], StubClient(RuntimeError("unavailable")), "model", 100, "source")

    def test_rejects_invalid_batch_size_and_vectors(self) -> None:
        with self.assertRaisesRegex(ValueError, "batch_size"):
            build_embedding_index([], StubClient(), "model", 0, "source")
        client = StubClient()
        client.embeddings.create = lambda **_: SimpleNamespace(data=[SimpleNamespace(index=0, embedding=[math.inf])])
        with self.assertRaisesRegex(EmbeddingBuildError, "finite numeric"):
            build_embedding_index([detail("O:F:AA", "COFAA", "text")], client, "model", 1, "source")


class CliTests(unittest.TestCase):
    def test_cli_loads_project_dotenv_when_environment_is_not_injected(self) -> None:
        with TemporaryDirectory() as directory:
            source = Path(directory) / "routing.json"
            output = Path(directory) / "index.json"
            source.write_text(json.dumps({"detail_index": [detail("O:F:AA", "COFAA", "text")]}), encoding="utf-8")
            args = ["--input", str(source), "--output", str(output)]

            def load_key(*_args, **_kwargs):
                import os
                os.environ["OPENAI_API_KEY"] = "loaded-test-key"

            with (
                patch.dict("os.environ", {}, clear=True),
                patch("scripts.build_ktas_detail_embedding_index.load_dotenv", side_effect=load_key) as loader,
            ):
                result = main(args, client_factory=lambda **_: StubClient())

            self.assertEqual(0, result)
            loader.assert_called_once()
            self.assertTrue(output.exists())

    def test_cli_creates_deterministic_output_without_network(self) -> None:
        with TemporaryDirectory() as directory:
            source = Path(directory) / "routing.json"
            output = Path(directory) / "index.json"
            source.write_text(json.dumps({"detail_index": [detail("O:F:AA", "COFAA", "text")]}), encoding="utf-8")
            factory = lambda **_: StubClient()
            args = ["--input", str(source), "--output", str(output), "--batch-size", "1"]
            self.assertEqual(0, main(args, client_factory=factory, environ={"OPENAI_API_KEY": "test"}))
            first = output.read_bytes()
            self.assertEqual(0, main(args, client_factory=factory, environ={"OPENAI_API_KEY": "test"}))
            self.assertEqual(first, output.read_bytes())

    def test_cli_fails_without_api_key_or_on_api_failure(self) -> None:
        with TemporaryDirectory() as directory:
            source = Path(directory) / "routing.json"
            output = Path(directory) / "index.json"
            source.write_text(json.dumps({"detail_index": [detail("O:F:AA", "COFAA", "text")]}), encoding="utf-8")
            args = ["--input", str(source), "--output", str(output)]
            self.assertEqual(1, main(args, client_factory=lambda **_: StubClient(), environ={}))
            self.assertEqual(1, main(args, client_factory=lambda **_: StubClient(RuntimeError("down")), environ={"OPENAI_API_KEY": "test"}))
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
