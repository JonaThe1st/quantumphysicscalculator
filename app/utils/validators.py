import re
from typing import Dict, Tuple


class ValidationError(Exception):
    pass


SUPPORTED_UNITS = {"ev", "j", "nm", "t", "k", "hz", "rad_s"}

PREFIX_FACTORS = {
    "": 1.0,
    "m": 1e-3,
    "k": 1e3,
    "M": 1e6,
    "G": 1e9,
    "T": 1e12,
    "mu": 1e-6,
    "u": 1e-6,
    "µ": 1e-6,
}

AUTO_PREFIX_VALUE = "auto"

DISPLAY_PREFIXES = ["T", "G", "M", "k", "", "m", "mu"]

UNIT_SYMBOLS = {
    "ev": "eV",
    "j": "J",
    "nm": "nm",
    "t": "T",
    "k": "K",
    "hz": "Hz",
    "rad_s": "rad/s",
}

UNIT_SUFFIXES = ["rad/s", "rad_s", "hz", "ev", "nm", "j", "t", "k"]

UNIT_ALIASES = {
    "rad/s": "rad_s",
    "rad_s": "rad_s",
    "hz": "hz",
    "ev": "ev",
    "nm": "nm",
    "j": "j",
    "t": "t",
    "k": "k",
}

SCIENTIFIC_NOTATION_PATTERN = re.compile(
    r"^\s*([+-]?(?:\d+(?:\.\d+)?|\.\d+))\s*[xX\*]\s*10\s*\^\s*([+-]?\d+)\s*$"
)


def _parse_numeric_component(text_value: str) -> float:
    # Support friendly input like 2*10^5 or 2x10^-3.
    match = SCIENTIFIC_NOTATION_PATTERN.match(text_value)
    if match:
        base = float(match.group(1))
        exponent = int(match.group(2))
        return base * (10 ** exponent)

    return float(text_value)


def parse_numeric_value(value) -> float:
    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, str):
        text_value = value.strip()
        if not text_value:
            raise ValidationError("Field 'value' must not be empty.")

        normalized_value = text_value.replace("μ", "µ")
        candidate_prefixes = ["mu", "u", "µ", "m", "k", "M", "G", "T"]
        for prefix in candidate_prefixes:
            if not normalized_value.endswith(prefix):
                continue

            numeric_portion = normalized_value[: -len(prefix)].strip()
            if not numeric_portion:
                continue

            try:
                numeric_value = _parse_numeric_component(numeric_portion)
            except ValueError:
                continue

            return numeric_value * PREFIX_FACTORS[prefix]

        try:
            return _parse_numeric_component(normalized_value)
        except ValueError:
            raise ValidationError(
                "Field 'value' must be numeric (examples: 12.5, 1e-3, 2*10^5, 1G, 250m)."
            )

    raise ValidationError("Field 'value' must be numeric.")


def _normalize_prefix(prefix: str) -> str:
    normalized = (prefix or "").strip()
    if normalized == AUTO_PREFIX_VALUE:
        return AUTO_PREFIX_VALUE
    if normalized not in PREFIX_FACTORS:
        raise ValidationError(
            "Unsupported prefix. Use one of: k, M, G, T, m, mu (or u)."
        )
    return normalized


def _parse_unit_with_optional_prefix(
    unit_text: str, prefix_override: str | None = None
) -> Tuple[str, float, str, bool]:
    if not isinstance(unit_text, str) or not unit_text.strip():
        raise ValidationError("Unit is required.")

    cleaned_unit = unit_text.strip().replace("μ", "µ")

    if cleaned_unit.lower() == "nm" and not prefix_override:
        return "nm", 1.0, "nm", False

    if prefix_override is not None and prefix_override.strip() != "":
        prefix = _normalize_prefix(prefix_override.replace("μ", "µ"))
        if prefix == AUTO_PREFIX_VALUE:
            prefix = ""
            explicit_prefix = False
        else:
            explicit_prefix = True

        base_key = cleaned_unit.lower()
        base_unit = UNIT_ALIASES.get(base_key)
        if not base_unit:
            raise ValidationError(f"Unsupported unit '{unit_text}'.")

        display_prefix = "u" if prefix in {"u", "µ"} else prefix
        display_unit = f"{display_prefix}{UNIT_SYMBOLS[base_unit]}"
        return base_unit, PREFIX_FACTORS[prefix], display_unit, explicit_prefix

    lowered = cleaned_unit.lower()
    for suffix in UNIT_SUFFIXES:
        if not lowered.endswith(suffix):
            continue

        prefix_text = cleaned_unit[: len(cleaned_unit) - len(suffix)]
        if suffix == "nm" and prefix_text:
            continue

        if prefix_text not in PREFIX_FACTORS:
            continue

        base_unit = UNIT_ALIASES[suffix]
        display_prefix = "u" if prefix_text in {"u", "µ"} else prefix_text
        display_unit = f"{display_prefix}{UNIT_SYMBOLS[base_unit]}"
        explicit_prefix = prefix_text != ""
        return base_unit, PREFIX_FACTORS[prefix_text], display_unit, explicit_prefix

    raise ValidationError(f"Unsupported unit '{unit_text}'.")


def format_with_si_prefix(value: float, base_unit: str) -> Tuple[float, str]:
    symbol = UNIT_SYMBOLS[base_unit]
    if base_unit == "nm" or value == 0:
        return value, symbol

    absolute_value = abs(value)
    for prefix in DISPLAY_PREFIXES:
        factor = PREFIX_FACTORS[prefix if prefix != "mu" else "mu"]
        scaled = absolute_value / factor
        if 1 <= scaled < 1000:
            signed_value = value / factor
            display_prefix = "u" if prefix == "mu" else prefix
            return signed_value, f"{display_prefix}{symbol}"

    # Fallback to base unit if no prefix range matches.
    return value, symbol


def validate_conversion_payload(payload: Dict) -> Tuple[float, str, str, float, str, str, bool]:
    if not isinstance(payload, dict):
        raise ValidationError("Request body must be a JSON object.")

    value = payload.get("value")
    source_unit = str(payload.get("source_unit", "")).strip()
    target_unit = str(payload.get("target_unit", "")).strip()
    source_prefix = str(payload.get("source_prefix", "")).strip()
    target_prefix = str(payload.get("target_prefix", "")).strip()

    if value is None:
        raise ValidationError("Field 'value' is required.")

    numeric_value = parse_numeric_value(value)

    if not source_unit:
        raise ValidationError("Field 'source_unit' is required.")

    if not target_unit:
        raise ValidationError("Field 'target_unit' is required.")

    source_base, source_factor, source_display_unit, _ = _parse_unit_with_optional_prefix(
        source_unit,
        source_prefix if source_prefix else None,
    )
    target_base, target_factor, target_display_unit, target_has_explicit_prefix = (
        _parse_unit_with_optional_prefix(
            target_unit,
            target_prefix if target_prefix else None,
        )
    )

    value_in_base_source = numeric_value * source_factor

    if source_base == "nm" and value_in_base_source <= 0:
        raise ValidationError("Field 'value' must be greater than 0 for wavelength.")

    return (
        value_in_base_source,
        source_base,
        target_base,
        target_factor,
        source_display_unit,
        target_display_unit,
        target_has_explicit_prefix,
    )
