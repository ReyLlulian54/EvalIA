"""Genera o comprueba el reporte público reproducible de la línea base seed."""

import argparse
import hashlib
import json
from dataclasses import asdict
from pathlib import Path

from evalia.graders.baseline import BASELINE_VERSION, baseline_prediction
from evalia.graders.dataset import evaluate_dataset
from evalia.normalization import DATE_RULES_VERSION, skill_vocabulary_version

ROOT = Path(__file__).resolve().parents[1]
DATASET = Path("datasets/seed.jsonl")
OUTPUT = Path("examples/results/seed-baseline-v1.json")


def _digest(path: Path) -> str:
    # read_text normaliza CRLF a LF en Windows y conserva caracteres Unicode.
    return hashlib.sha256(path.read_text(encoding="utf-8").encode("utf-8")).hexdigest()


def build_report(root: Path = ROOT) -> dict:
    """Reconstruye predicciones y métricas desde archivos versionados."""
    cases = [
        json.loads(line)
        for line in (root / DATASET).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    predictions = [
        baseline_prediction(case["id"], case["text"])
        for case in cases
        if case["review_status"] == "reviewed"
    ]
    results = evaluate_dataset(cases, predictions)
    if any(not case["redistribution_allowed"] for case in cases):
        raise ValueError("El reporte público exige permiso de redistribución en todos los casos")

    return {
        "report_version": "1.0.0",
        "kind": "rule_baseline_seed",
        "evaluation_scope": "development_smoke_not_held_out",
        "baseline_version": BASELINE_VERSION,
        "date_rules_version": DATE_RULES_VERSION,
        "skill_vocabulary_version": skill_vocabulary_version(),
        "inputs": {
            "dataset": DATASET.as_posix(),
            "dataset_sha256": _digest(root / DATASET),
            "baseline_code_sha256": _digest(root / "src/evalia/graders/baseline.py"),
            "case_schema_sha256": _digest(root / "schemas/evalia-case.schema.json"),
            "skill_vocabulary_sha256": _digest(root / "src/evalia/vocabularies/skills-v1.json"),
        },
        "case_count": len(cases),
        "predictions": predictions,
        "scored_case_ids": results.scored_case_ids,
        "excluded": [asdict(item) for item in results.excluded],
        "format_errors": [asdict(item) for item in results.format_errors],
        "metrics": {
            name: {
                "numerator": metric.ratio.numerator,
                "denominator": metric.ratio.denominator,
                "value": metric.ratio.value,
                "failed_case_ids": metric.failed_case_ids,
            }
            for name, metric in results.metrics.items()
        },
    }


def serialize_report(report: dict) -> str:
    """Serializa de forma estable para comparar el artefacto byte a byte."""
    return json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--write", action="store_true", help="escribe el reporte versionado")
    action.add_argument(
        "--check", action="store_true", help="comprueba que el reporte no esté obsoleto"
    )
    parser.add_argument("--output", type=Path, default=ROOT / OUTPUT)
    options = parser.parse_args()
    content = serialize_report(build_report())
    output = options.output

    if options.write:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(content, encoding="utf-8", newline="\n")
        print(f"Reporte escrito: {output}")
        return 0
    if not output.is_file() or output.read_text(encoding="utf-8") != content:
        print(f"Reporte obsoleto o ausente: {output}")
        return 1
    print(f"Reporte vigente: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
