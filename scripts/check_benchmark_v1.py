"""Comprueba la integridad del borrador y la partición fijada de benchmark-v1."""

import hashlib
import json
from collections import Counter
from pathlib import Path

from evalia.validation import validate_jsonl

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "datasets/benchmark-v1.jsonl"
MANIFEST = ROOT / "datasets/benchmark-v1-manifest.json"
SEED = ROOT / "datasets/seed.jsonl"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"Benchmark inválido: {message}")


def main() -> None:
    count, issues = validate_jsonl(DATASET)
    require(not issues, f"{len(issues)} problema(s) de contrato; ejecute evalia validate")
    cases = [json.loads(line) for line in DATASET.read_text(encoding="utf-8").splitlines()]
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    require(
        set(manifest) == {"version", "phase", "created_at", "sha256_lf", "test_ids"},
        "manifiesto incompleto o con claves desconocidas",
    )
    canonical = DATASET.read_text(encoding="utf-8").encode("utf-8")
    require(
        hashlib.sha256(canonical).hexdigest() == manifest["sha256_lf"],
        "el hash del JSONL con saltos LF no coincide con el manifiesto",
    )
    require(30 <= count <= 40, "se esperan entre 30 y 40 casos")
    require(
        [case["id"] for case in cases] == [f"bench-{n:03}" for n in range(1, count + 1)],
        "IDs u orden inesperados",
    )
    test_ids = [case["id"] for case in cases if case["split"] == "test"]
    require(test_ids == manifest["test_ids"], "la partición test cambió")
    require(len(test_ids) == 9 and count == 36, "la partición inicial debe ser 27 dev / 9 test")
    require(Counter(case["split"] for case in cases) == {"dev": 27, "test": 9}, "división inválida")
    test_cases = [case for case in cases if case["split"] == "test"]
    require(
        Counter(case["expected"]["student_required"] for case in test_cases)
        == {True: 3, False: 3, None: 3},
        "test debe cubrir true, false y null del requisito de estudiante",
    )
    require(
        any(not case["expected"]["skills"] for case in test_cases),
        "test requiere al menos un caso sin habilidad obligatoria",
    )
    require(
        any(case["expected"]["modality"] is None for case in test_cases),
        "test requiere al menos una modalidad no determinable",
    )
    require(manifest["phase"] in {"draft", "reviewed"}, "fase desconocida")
    if manifest["phase"] == "draft":
        require(
            all(case["review_status"] == "draft" for case in cases),
            "la fase draft no puede declarar casos revisados",
        )
    else:
        require(
            all(case["review_status"] == "reviewed" for case in cases),
            "la fase reviewed requiere revisión registrada de todos los casos",
        )
    require(
        all(
            case["source_url"] is None
            and case["source_license"] == "LicenseRef-EvalIA-Original"
            and case["redistribution_allowed"] is True
            for case in cases
        ),
        "procedencia o permiso de publicación inesperado",
    )
    seed_texts = {
        case["text"] for case in map(json.loads, SEED.read_text(encoding="utf-8").splitlines())
    }
    require(not seed_texts.intersection(case["text"] for case in cases), "texto repetido del seed")
    absence_count = sum(
        case["expected"]["closing_date"] is None
        or case["expected"]["modality"] is None
        or not case["expected"]["skills"]
        or case["expected"]["student_required"] is None
        for case in cases
    )
    require(absence_count >= 10, "faltan casos con ausencias o información no determinable")
    print(
        f"Benchmark {manifest['phase']} conforme: {count} casos; "
        f"27 dev / 9 test; {absence_count} con alguna ausencia o valor no determinable; "
        f"SHA-256 LF {manifest['sha256_lf']}."
    )


if __name__ == "__main__":
    main()
