from flask import Blueprint, jsonify, request

from app.services.conversion_service import ConversionService
from app.utils.validators import (
    ValidationError,
    format_with_si_prefix,
    validate_conversion_payload,
)

api_bp = Blueprint("api", __name__, url_prefix="/api/v1")


@api_bp.get("/health")
def health_check():
    return jsonify({"status": "ok"}), 200


@api_bp.post("/convert")
def convert_value():
    payload = request.get_json(silent=True) or {}

    try:
        (
            value,
            source_unit,
            target_unit,
            target_factor,
            source_display_unit,
            target_display_unit,
            target_has_explicit_prefix,
        ) = validate_conversion_payload(payload)
        result_in_target_base = ConversionService.convert(value, source_unit, target_unit)
        result = result_in_target_base / target_factor

        if target_has_explicit_prefix:
            result_display_value = result
            result_display_unit = target_display_unit
        else:
            result_display_value, result_display_unit = format_with_si_prefix(
                result_in_target_base,
                target_unit,
            )
    except ValidationError as error:
        return jsonify({"error": str(error)}), 400
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    return (
        jsonify(
            {
                "input": {
                    "value": value,
                    "source_unit": source_display_unit,
                    "target_unit": target_display_unit,
                },
                "result": result,
                "result_display": {
                    "value": result_display_value,
                    "unit": result_display_unit,
                    "text": f"{result_display_value:.12g} {result_display_unit}",
                },
            }
        ),
        200,
    )
