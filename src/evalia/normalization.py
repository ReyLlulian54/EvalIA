"""Normalización conservadora de fechas y nombres de habilidades."""

import json
import re
from collections.abc import Iterable
from datetime import date
from functools import cache
from importlib import resources

DATE_RULES_VERSION = "1.0.0"

_MONTHS = {
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "setiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12,
}
_MONTH_PATTERN = "|".join(_MONTHS)
_ISO_DATE = re.compile(r"([0-9]{4})-([0-9]{1,2})-([0-9]{1,2})")
_NUMERIC_DATE = re.compile(r"([0-9]{1,2})/([0-9]{1,2})/([0-9]{4})")
_TEXT_DATE = re.compile(rf"([0-9]{{1,2}}) de ({_MONTH_PATTERN}) de ([0-9]{{4}})")
_NUMERIC_WITHOUT_YEAR = re.compile(r"([0-9]{1,2})/([0-9]{1,2})")
_TEXT_WITHOUT_YEAR = re.compile(rf"([0-9]{{1,2}}) de ({_MONTH_PATTERN})")


def normalize_date(value: str | None) -> str | None:
    """Devuelve fecha ISO; una fecha sin año queda desconocida, no inferida."""
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError("La fecha debe ser texto o None")

    candidate = " ".join(value.split()).casefold()
    if not candidate:
        return None

    if match := _ISO_DATE.fullmatch(candidate):
        year, month, day = map(int, match.groups())
    elif match := _NUMERIC_DATE.fullmatch(candidate):
        day, month, year = map(int, match.groups())
    elif match := _TEXT_DATE.fullmatch(candidate):
        day = int(match.group(1))
        month = _MONTHS[match.group(2)]
        year = int(match.group(3))
    elif match := _NUMERIC_WITHOUT_YEAR.fullmatch(candidate):
        day, month = map(int, match.groups())
        date(2000, month, day)  # Comprueba que sea posible en algún año.
        return None
    elif match := _TEXT_WITHOUT_YEAR.fullmatch(candidate):
        date(2000, _MONTHS[match.group(2)], int(match.group(1)))
        return None
    else:
        raise ValueError(f"Formato de fecha no admitido: {value!r}")

    return date(year, month, day).isoformat()


@cache
def _skill_vocabulary() -> dict:
    artifact = resources.files("evalia").joinpath("vocabularies/skills-v1.json")
    return json.loads(artifact.read_text(encoding="utf-8"))


def skill_vocabulary_version() -> str:
    """Devuelve la versión declarada en el vocabulario autoritativo."""
    return _skill_vocabulary()["version"]


def normalize_skill(value: str) -> str:
    """Aplica solo equivalencias publicadas; conserva otros términos explícitos."""
    if not isinstance(value, str):
        raise TypeError("La habilidad debe ser texto")
    cleaned = " ".join(value.split())
    if not cleaned:
        raise ValueError("La habilidad no puede estar vacía")
    return _skill_vocabulary()["aliases"].get(cleaned.casefold(), cleaned)


def normalize_skills(values: Iterable[str]) -> list[str]:
    """Normaliza una colección y elimina equivalentes repetidos conservando orden."""
    if isinstance(values, (str, bytes)):
        raise TypeError("Las habilidades deben venir en una colección, no en texto")

    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        skill = normalize_skill(value)
        if skill not in seen:
            seen.add(skill)
            result.append(skill)
    return result
