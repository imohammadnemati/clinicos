import pytest

from handlers.facial_analysis import _safe_analysis_data, _build_safe_report_text


def test_unsafe_structured_units_and_free_text_are_blocked():
    raw = {
        "summary": "Features look normal.",
        "recommendations": [{
            "treatment_type": "Botox",
            "area": "Forehead",
            "estimated_units": "20",
            "estimated_volume": "1ml",
            "description": "Administer 20 units to smooth wrinkles.",
        }],
        "disclaimer": "Info only.",
    }

    safe = _safe_analysis_data(raw)
    rec = safe["recommendations"][0]
    report = _build_safe_report_text(safe)

    assert rec["estimated_units"] is None
    assert rec["estimated_volume"] is None
    assert "20 units" not in rec["description"]
    assert "1ml" not in report
    assert "20 units" not in report
    assert "Safety blocked" in rec["description"]


def test_unparseable_llm_output_never_becomes_persisted_raw_text():
    safe = _safe_analysis_data("not valid JSON")
    report = _build_safe_report_text(safe)

    assert safe["recommendations"] == []
    assert "not valid JSON" not in report
    assert "informational only" in report


def test_nested_prescriptive_fields_are_removed():
    raw = {
        "summary": "ok",
        "recommendations": [{
            "treatment_type": "Filler",
            "area": "Lips",
            "details": {
                "dose": "2 ml",
                "nested": "Inject 30 units",
            },
        }],
    }

    safe = _safe_analysis_data(raw)
    rec = safe["recommendations"][0]

    assert rec["estimated_units"] is None
    assert rec["estimated_volume"] is None
