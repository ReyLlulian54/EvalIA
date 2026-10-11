"""Línea base conservadora por reglas; recibe texto, nunca valores esperados."""

import re
from functools import cache

from evalia.normalization import normalize_date, normalize_skill, skill_aliases

BASELINE_VERSION = "0.1.0"

_CLAUSE = re.compile(r"[^.!?;\n]+")
_DATE = re.compile(
    r"\b(?:[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}|"
    r"[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}|"
    r"[0-9]{1,2}\s+de\s+[a-záéíóúñ]+\s+de\s+[0-9]{4})\b",
    re.IGNORECASE,
)
_CLOSING_CUE = re.compile(
    r"\b(?:postula(?:r|ciones)?|postulaciones|cierran|cierre|cierra|plazo|"
    r"fecha\s+l[ií]mite)\b",
    re.IGNORECASE,
)
_EXTENSION = re.compile(r"\b(?:actualizaci[oó]n|se\s+ampl[ií]a|se\s+prorroga)\b", re.I)
_MODALITY = re.compile(
    r"\bremot[oa]s?\b|\bh[ií]brid[oa]s?\b|\bpresencial(?:es)?\b|\ba\s+distancia\b",
    re.IGNORECASE,
)
_MANDATORY = re.compile(
    r"\b(?:exig(?:e|ir)|requiere|obligatori[oa]s?|debe(?:n)?\s+(?:conocer|dominar))\b",
    re.IGNORECASE,
)
_NEGATED_MANDATORY = re.compile(r"\bno\s+(?:se\s+)?(?:exige|requiere)\b", re.I)
_STUDENT_NO = re.compile(
    r"\bno\s+(?:es\s+necesario|se\s+(?:exige|requiere))\s+ser\s+estudiante\b",
    re.IGNORECASE,
)
_STUDENT_YES = re.compile(
    r"\b(?:es\s+obligatorio|se\s+(?:exige|requiere)|debe)\s+ser\s+estudiante\b",
    re.IGNORECASE,
)


def _clauses(text: str) -> list[tuple[str, int, int]]:
    clauses: list[tuple[str, int, int]] = []
    for match in _CLAUSE.finditer(text):
        raw = match.group()
        stripped = raw.strip()
        if stripped:
            start = match.start() + len(raw) - len(raw.lstrip())
            clauses.append((stripped, start, start + len(stripped)))
    return clauses


def _span(text: str, start: int, end: int) -> dict:
    return {"quote": text[start:end], "start": start, "end": end}


def _closing_date(clauses: list[tuple[str, int, int]], text: str) -> tuple[str | None, dict | None]:
    candidates: list[tuple[str, dict, bool]] = []
    for clause, start, end in clauses:
        if not _CLOSING_CUE.search(clause):
            continue
        for match in _DATE.finditer(clause):
            try:
                normalized = normalize_date(match.group())
            except ValueError:
                continue
            if normalized is not None:
                candidates.append(
                    (normalized, _span(text, start, end), bool(_EXTENSION.search(clause)))
                )

    if not candidates:
        return None, None
    if len({value for value, _, _ in candidates}) == 1:
        value, evidence, _ = candidates[0]
        return value, evidence
    extensions = [candidate for candidate in candidates if candidate[2]]
    if len(extensions) == 1:
        value, evidence, _ = extensions[0]
        return value, evidence
    return None, None


def _modality(clauses: list[tuple[str, int, int]], text: str) -> tuple[str | None, dict | None]:
    mentions: list[tuple[str, dict]] = []
    for clause, start, end in clauses:
        for match in _MODALITY.finditer(clause):
            token = match.group().casefold()
            if token.startswith(("remot", "a distancia")):
                value = "remota"
            elif token.startswith(("hibrid", "híbr")):
                value = "hibrida"
            else:
                value = "presencial"
            mentions.append((value, _span(text, start, end)))
    if len({value for value, _ in mentions}) != 1:
        return None, None
    return mentions[0]


@cache
def _skill_pattern() -> re.Pattern[str]:
    alternatives = "|".join(re.escape(alias).replace(r"\ ", r"\s+") for alias in skill_aliases())
    return re.compile(rf"(?<!\w)(?:{alternatives})(?!\w)", re.IGNORECASE)


def _skills(clauses: list[tuple[str, int, int]], text: str) -> tuple[list[str], list[dict]]:
    skills: list[str] = []
    evidence: list[dict] = []
    seen: set[str] = set()
    for clause, start, end in clauses:
        if not _MANDATORY.search(clause) or _NEGATED_MANDATORY.search(clause):
            continue
        for match in _skill_pattern().finditer(clause):
            skill = normalize_skill(match.group())
            if skill not in seen:
                seen.add(skill)
                skills.append(skill)
                evidence.append({"skill": skill, **_span(text, start, end)})
    return skills, evidence


def _student(clauses: list[tuple[str, int, int]], text: str) -> tuple[bool | None, dict | None]:
    mentions: list[tuple[bool, dict]] = []
    for clause, start, end in clauses:
        if _STUDENT_NO.search(clause):
            mentions.append((False, _span(text, start, end)))
        elif _STUDENT_YES.search(clause):
            mentions.append((True, _span(text, start, end)))
    if len({value for value, _ in mentions}) != 1:
        return None, None
    return mentions[0]


def baseline_prediction(case_id: str, text: str) -> dict:
    """Extrae solo menciones explícitas y devuelve citas con índices Unicode de Python."""
    clauses = _clauses(text)
    closing_date, closing_span = _closing_date(clauses, text)
    modality, modality_span = _modality(clauses, text)
    skills, skill_spans = _skills(clauses, text)
    student_required, student_span = _student(clauses, text)
    return {
        "case_id": case_id,
        "extraction": {
            "closing_date": closing_date,
            "modality": modality,
            "skills": skills,
            "student_required": student_required,
        },
        "evidence": {
            "closing_date": closing_span,
            "modality": modality_span,
            "skills": skill_spans,
            "student_required": student_span,
        },
    }
