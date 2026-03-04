import json
from typing import Any, Dict, List, Tuple

# ---------------------------------------------------------------------------
# Shared system instruction
# ---------------------------------------------------------------------------

_SYSTEM_INSTRUCTION = (
    "You are an expert performance and strategy analyst specialising in KPI evaluation, "
    "benchmarking, and organisational performance management. "
    "Generate native, professional insights in both English and Arabic matching the tone "
    "of executive business reports. "
    "Output ONLY valid JSON matching the provided schema. Do not enclose the JSON in markdown code blocks."
)

# ---------------------------------------------------------------------------
# Shared context builder
# ---------------------------------------------------------------------------

def _context_block(kpi_metadata: Dict[str, Any], kpi_data_points: List[Dict[str, Any]]) -> str:
    """Return the common KPI context block used by every section prompt."""
    return (
        f"===== KPI METADATA & CONTEXT =====\n"
        f"{json.dumps(kpi_metadata, ensure_ascii=False, indent=2)}\n\n"
        f"===== KPI DATA POINTS (PERIODIC ACTUALS VS TARGETS) =====\n"
        f"{json.dumps(kpi_data_points, ensure_ascii=False, indent=2)}\n\n"
    )

# ---------------------------------------------------------------------------
# Section 1: Executive Summary
# ---------------------------------------------------------------------------

def build_executive_summary_prompt(
    kpi_metadata: Dict[str, Any],
    kpi_data_points: List[Dict[str, Any]]
) -> Tuple[str, str]:
    """Build the prompt for the Executive Summary section (bilingual)."""
    schema = {
        "type": "object",
        "required": ["english", "arabic"],
        "properties": {
            "english": {
                "type": "string",
                "description": (
                    "Detailed executive summary structured with: an introductory paragraph, "
                    "'Quarter-by-Quarter Actuals Analysis' (bullet points comparing each period's actual "
                    "to the previous period's, noting the difference), 'Target Achievement Analysis' "
                    "(bullet points comparing each period's actual against the target, calculating the exact "
                    "variance), a concluding paragraph with future outlook, and a 'Confidence Level' "
                    "(High / Medium / Low)."
                )
            },
            "arabic": {
                "type": "string",
                "description": (
                    "ملخص تنفيذي تفصيلي مهيكل يحتوي على: فقرة تمهيدية، 'تحليل القيم الفعلية ربعًا بربع' "
                    "(نقاط مقارنة لكل فترة بالفترة السابقة مع الفارق)، 'تحليل تحقيق الهدف' "
                    "(نقاط تقارن الفعلي بالمستهدف مع الانحراف الدقيق)، فقرة خاتمة بالتوقعات المستقبلية، "
                    "و'مستوى الثقة' (مرتفع / متوسط / منخفض)."
                )
            }
        }
    }

    user_msg = (
        "KPI EXECUTIVE SUMMARY REQUEST\n\n"
        + _context_block(kpi_metadata, kpi_data_points)
        + "INSTRUCTIONS:\n"
        "Write a highly detailed executive summary that follows this exact structure:\n"
        "  1. An introductory paragraph summarising the overall performance and trend.\n"
        "  2. 'Quarter-by-Quarter Actuals Analysis': Bullet points comparing each period's actual "
        "to the previous period, noting the exact difference.\n"
        "  3. 'Target Achievement Analysis': Bullet points comparing each period's actual against "
        "its target, calculating the exact variance.\n"
        "  4. A concluding paragraph with future expectations and outlook.\n"
        "  5. 'Confidence Level': e.g. High, Medium, or Low.\n\n"
        "Provide the output in both English and Arabic.\n\n"
        f"REQUIRED OUTPUT SCHEMA:\n{json.dumps(schema, ensure_ascii=False, indent=2)}\n\n"
        "Provide ONLY valid JSON matching this schema. No additional text."
    )

    return _SYSTEM_INSTRUCTION, user_msg


# ---------------------------------------------------------------------------
# Section 2: Performance Analysis
# ---------------------------------------------------------------------------

def build_performance_analysis_prompt(
    kpi_metadata: Dict[str, Any],
    kpi_data_points: List[Dict[str, Any]]
) -> Tuple[str, str]:
    """Build the prompt for the Performance Analysis section (bilingual)."""
    schema = {
        "type": "object",
        "required": ["english", "arabic"],
        "properties": {
            "english": {
                "type": "string",
                "description": (
                    "Detailed analysis of data-point trends, gaps between targets and actuals, "
                    "and the impact of external events noted in the data."
                )
            },
            "arabic": {
                "type": "string",
                "description": (
                    "تحليل تفصيلي لنقاط البيانات والاتجاهات والفجوات بين المستهدف والمحقق "
                    "وتأثير الأحداث الخارجية المذكورة في البيانات."
                )
            }
        }
    }

    user_msg = (
        "KPI PERFORMANCE ANALYSIS REQUEST\n\n"
        + _context_block(kpi_metadata, kpi_data_points)
        + "INSTRUCTIONS:\n"
        "Analyse the performance trends across all provided periods. Cover:\n"
        "  - Where performance exceeded, met, or fell short of targets.\n"
        "  - Trend direction (improving, declining, flat) and its magnitude.\n"
        "  - The role of any external events or contextual notes in the data.\n"
        "  - Notable gaps between period actuals and annual targets.\n\n"
        "Provide the output in both English and Arabic.\n\n"
        f"REQUIRED OUTPUT SCHEMA:\n{json.dumps(schema, ensure_ascii=False, indent=2)}\n\n"
        "Provide ONLY valid JSON matching this schema. No additional text."
    )

    return _SYSTEM_INSTRUCTION, user_msg


# ---------------------------------------------------------------------------
# Section 3: Root Causes
# ---------------------------------------------------------------------------

def build_root_causes_prompt(
    kpi_metadata: Dict[str, Any],
    kpi_data_points: List[Dict[str, Any]]
) -> Tuple[str, str]:
    """Build the prompt for the Root Causes section (bilingual)."""
    schema = {
        "type": "object",
        "required": ["english", "arabic"],
        "properties": {
            "english": {
                "type": "array",
                "items": {"type": "string"},
                "description": "2–4 identified root causes explaining the performance variance."
            },
            "arabic": {
                "type": "array",
                "items": {"type": "string"},
                "description": "2–4 أسباب جذرية محتملة تفسر التباين في الأداء."
            }
        }
    }

    user_msg = (
        "KPI ROOT CAUSES REQUEST\n\n"
        + _context_block(kpi_metadata, kpi_data_points)
        + "INSTRUCTIONS:\n"
        "Identify 2–4 root causes that best explain why the KPI performed as it did "
        "across the given periods. Each cause should be specific, evidence-based, "
        "and directly linked to the data or contextual notes provided.\n\n"
        "Provide the output in both English and Arabic.\n\n"
        f"REQUIRED OUTPUT SCHEMA:\n{json.dumps(schema, ensure_ascii=False, indent=2)}\n\n"
        "Provide ONLY valid JSON matching this schema. No additional text."
    )

    return _SYSTEM_INSTRUCTION, user_msg


# ---------------------------------------------------------------------------
# Section 4: Recommendations
# ---------------------------------------------------------------------------

def build_recommendations_prompt(
    kpi_metadata: Dict[str, Any],
    kpi_data_points: List[Dict[str, Any]]
) -> Tuple[str, str]:
    """Build the prompt for the Recommendations section (bilingual)."""
    schema = {
        "type": "object",
        "required": ["english", "arabic"],
        "properties": {
            "english": {
                "type": "array",
                "items": {"type": "string"},
                "description": "3–5 strategic, actionable recommendations for future improvement or sustaining momentum."
            },
            "arabic": {
                "type": "array",
                "items": {"type": "string"},
                "description": "3–5 توصيات استراتيجية وقابلة للتنفيذ للتحسين المستقبلي أو الحفاظ على الزخم."
            }
        }
    }

    user_msg = (
        "KPI RECOMMENDATIONS REQUEST\n\n"
        + _context_block(kpi_metadata, kpi_data_points)
        + "INSTRUCTIONS:\n"
        "Suggest 3–5 actionable recommendations to either course-correct underperformance "
        "or sustain/accelerate positive momentum. Recommendations must be specific, "
        "feasible, and directly related to the KPI's context and performance patterns.\n\n"
        "Provide the output in both English and Arabic.\n\n"
        f"REQUIRED OUTPUT SCHEMA:\n{json.dumps(schema, ensure_ascii=False, indent=2)}\n\n"
        "Provide ONLY valid JSON matching this schema. No additional text."
    )

    return _SYSTEM_INSTRUCTION, user_msg
