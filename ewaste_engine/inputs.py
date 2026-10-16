import csv
import math
from pathlib import Path

from .models import ItemLine, PickupRequest, Rate, Source


class InputError(ValueError):
    """Raised when a command input file is malformed or inconsistent."""


def _rows(path: Path) -> list[dict[str, str]]:
    try:
        with path.open(newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            if not reader.fieldnames:
                raise InputError(f"{path}: missing CSV header")
            return list(reader)
    except OSError as exc:
        raise InputError(f"Cannot read {path}: {exc}") from exc


def _required(row: dict[str, str], key: str, path: Path) -> str:
    value = (row.get(key) or "").strip()
    if not value:
        raise InputError(f"{path}: missing value for {key}")
    return value


def load_sources(path: Path) -> dict[str, Source]:
    result = {}
    for line, row in enumerate(_rows(path), start=2):
        try:
            source_id = _required(row, "source_id", path)
            source_type = _required(row, "type", path).upper()
            distance = float(_required(row, "distance_km", path))
            if source_type not in {"BULK", "HOUSEHOLD"}:
                raise InputError(f"{path}:{line}: type must be BULK or HOUSEHOLD")
            if not math.isfinite(distance) or distance < 0:
                raise InputError(f"{path}:{line}: distance_km must be a non-negative number")
            if source_id in result:
                raise InputError(f"{path}:{line}: duplicate source_id {source_id}")
            result[source_id] = Source(source_id, source_type, distance)
        except ValueError as exc:
            if isinstance(exc, InputError):
                raise
            raise InputError(f"{path}:{line}: invalid numeric value") from exc
    if not result:
        raise InputError(f"{path}: no sources found")
    return result


def load_rates(path: Path) -> dict[str, Rate]:
    result = {}
    for line, row in enumerate(_rows(path), start=2):
        category = _required(row, "category", path).upper()
        try:
            value = float(_required(row, "credit_per_kg", path))
        except ValueError as exc:
            raise InputError(f"{path}:{line}: invalid credit_per_kg") from exc
        hazard_text = _required(row, "hazardous", path).lower()
        if not math.isfinite(value) or value < 0:
            raise InputError(f"{path}:{line}: credit_per_kg must be non-negative")
        if hazard_text not in {"true", "false"}:
            raise InputError(f"{path}:{line}: hazardous must be true or false")
        if category in result:
            raise InputError(f"{path}:{line}: duplicate category {category}")
        result[category] = Rate(category, value, hazard_text == "true")
    if not result:
        raise InputError(f"{path}: no rates found")
    return result


def load_requests(path: Path, rates: dict[str, Rate], sources: dict[str, Source]) -> list[PickupRequest]:
    result = []
    seen_ids = set()
    for line, row in enumerate(_rows(path), start=2):
        request_id = _required(row, "request_id", path)
        source_id = _required(row, "source_id", path)
        if request_id in seen_ids:
            raise InputError(f"{path}:{line}: duplicate request_id {request_id}")
        if source_id not in sources:
            raise InputError(f"{path}:{line}: unknown source_id {source_id}")
        seen_ids.add(request_id)
        parsed_items = []
        for token in _required(row, "items", path).split(";"):
            try:
                category, count_text, weight_text = [part.strip() for part in token.split(":")]
                category = category.upper()
                count, weight = int(count_text), float(weight_text)
            except (ValueError, TypeError) as exc:
                raise InputError(f"{path}:{line}: invalid item {token!r}; expected CATEGORY:COUNT:WEIGHT") from exc
            if category not in rates:
                raise InputError(f"{path}:{line}: no rate for category {category}")
            if count <= 0 or not math.isfinite(weight) or weight <= 0:
                raise InputError(f"{path}:{line}: item count and weight must be positive")
            parsed_items.append(ItemLine(category, count, weight))
        if not parsed_items:
            raise InputError(f"{path}:{line}: request must contain at least one item")
        result.append(PickupRequest(request_id, source_id, tuple(parsed_items)))
    return result
