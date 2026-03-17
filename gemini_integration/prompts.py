import json
from typing import Any, Dict, List, Tuple

# ---------------------------------------------------------------------------
# Shared system instruction
# ---------------------------------------------------------------------------

_SYSTEM_INSTRUCTION = (
    "You are a senior performance and strategy analyst with deep expertise in KPI evaluation, "
    "benchmarking, and organisational performance management for government and public-sector entities. "
    "Your role is to produce rigorous, evidence-based analysis that a C-suite executive can rely on "
    "when making strategic decisions. "
    "Always ground every insight in the specific numbers, periods, and contextual notes provided — "
    "never invent data or make generic statements that could apply to any KPI. "
    "Write in a clear, authoritative executive tone. "
    "CRITICAL LANGUAGE SEPARATION & TRANSLATION: "
    "1. The value for the 'english' key MUST be written entirely in polished business English, with zero Arabic words. "
    "If any input data values (like external events or analysis notes) are in Arabic, you MUST translate them into English for the English output. "
    "2. The value for the 'arabic' key MUST be written entirely in formal Modern Standard Arabic (فصحى), with zero English words. "
    "If any input data keys (like 'period_actual') or values are in English, you MUST translate them into Arabic for the Arabic output. "
    "Both language versions must convey identical meaning and equal depth. "
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
                    "A structured executive summary with the following clearly labelled sub-sections:\n"
                    "1. Overview paragraph: State the KPI name, entity, measurement period(s), unit of "
                    "measurement, and an overall one-sentence verdict (e.g. 'The KPI demonstrated consistent "
                    "outperformance / underperformance / mixed results across the reporting period.').\n"
                    "2. 'Period-by-Period Actuals Analysis' (bullet list): For EACH period row in the data, "
                    "state the actual value, the change vs. the prior period (absolute and % change), and "
                    "whether this represents an improvement or decline.\n"
                    "3. 'Target Achievement Analysis' (bullet list): For EACH period row, state the actual "
                    "vs. the target, the exact variance (absolute and %), and whether the period met/exceeded/"
                    "missed the target.\n"
                    "4. Overall Performance Classification: Label the KPI as one of — 'Consistently "
                    "Achieving', 'Improving Trajectory', 'Declining Trajectory', 'Volatile', or 'Consistently "
                    "Underperforming' — with a one-sentence justification.\n"
                    "5. Forward Outlook paragraph: A brief forward-looking statement based on the trend.\n"
                    "6. 'Confidence Level': State High, Medium, or Low with a one-sentence reason "
                    "(e.g. data completeness, recency, external noise)."
                )
            },
            "arabic": {
                "type": "string",
                "description": (
                    "ملخص تنفيذي مهيكل يحتوي على الأقسام الفرعية التالية بشكل صريح:\n"
                    "1. فقرة تمهيدية: اسم المؤشر، الجهة، فترات القياس، وحدة القياس، وحكم إجمالي "
                    "في جملة واحدة.\n"
                    "2. 'تحليل القيم الفعلية فترة بفترة' (نقاط): لكل صف بيانات: القيمة الفعلية، "
                    "الفرق عن الفترة السابقة (مطلق ونسبي)، وهل يمثل تحسناً أم تراجعاً.\n"
                    "3. 'تحليل تحقيق الهدف' (نقاط): لكل فترة: الفعلي مقابل المستهدف، "
                    "الانحراف الدقيق (مطلق ونسبي)، وهل تحقق الهدف أم تجاوزه أم قصّر عنه.\n"
                    "4. تصنيف الأداء الإجمالي: أحد التصنيفات — 'تحقيق مستمر' / 'مسار تصاعدي' / "
                    "'مسار تراجعي' / 'أداء متذبذب' / 'قصور مستمر' — مع جملة تبرير.\n"
                    "5. فقرة التوقعات المستقبلية: بيان استشرافي مبني على الاتجاه الحالي.\n"
                    "6. 'مستوى الثقة': مرتفع / متوسط / منخفض مع سبب موجز."
                )
            }
        }
    }

    user_msg = (
        "KPI EXECUTIVE SUMMARY REQUEST\n\n"
        + _context_block(kpi_metadata, kpi_data_points)
        + "INSTRUCTIONS:\n"
        "Produce a detailed, data-driven executive summary. Rules:\n"
        "  - Every numerical claim must be derived from the supplied data — do NOT fabricate figures.\n"
        "  - Calculate and state absolute and percentage differences explicitly for each period.\n"
        "  - Use the KPI's unit of measurement (e.g. %, score, count) consistently.\n"
        "  - Reference any external events or benchmarking notes provided in the data where relevant.\n"
        "  - STRICTLY ENFORCE LANGUAGE SEPARATION: The 'english' response must be 100% English, and the 'arabic' response 100% Arabic.\n"
        "  - TRANSLATE DATA: Translate Arabic input data into English for the English response. Translate English JSON keys/data into Arabic for the Arabic response.\n\n"
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
                    "A detailed performance analysis organised into the following paragraphs:\n"
                    "1. Trend Analysis: Describe the overall trend direction (improving, declining, flat, "
                    "volatile) with supporting figures across all periods.\n"
                    "2. Gap Analysis: Identify the period(s) with the largest positive and negative "
                    "variances from target, state the exact values, and explain what they signal.\n"
                    "3. External Events Impact: Assess the influence of any external events listed in the "
                    "data on the results; if none, explicitly state that no external events were noted.\n"
                    "4. Formula & Measurement Quality: Comment on whether the measurement formula, "
                    "frequency, and mechanism appear suitable for capturing this KPI; flag any data "
                    "completeness concerns.\n"
                    "5. Benchmarking Insight: If benchmark data (country/region/year/value) is present, "
                    "compare the entity's performance against benchmarks; if absent, note the omission."
                )
            },
            "arabic": {
                "type": "string",
                "description": (
                    "تحليل أداء تفصيلي منظّم في الفقرات التالية:\n"
                    "1. تحليل الاتجاه: توصيف الاتجاه العام مع الأرقام الداعمة عبر جميع الفترات.\n"
                    "2. تحليل الفجوات: تحديد الفترات ذات أكبر انحراف إيجابي وسلبي عن الهدف مع "
                    "القيم الدقيقة وما تعنيه.\n"
                    "3. أثر الأحداث الخارجية: تقييم تأثير أي أحداث خارجية واردة في البيانات؛ "
                    "وإذا لم توجد، يُصرَّح بذلك صراحةً.\n"
                    "4. جودة المعادلة والقياس: التعليق على مدى ملاءمة معادلة القياس وتكراره وآليته؛ "
                    "والإشارة إلى أي قصور في اكتمال البيانات.\n"
                    "5. رؤية المقارنة المعيارية: إذا وُجدت بيانات معيارية، تُجرى المقارنة بأرقام دقيقة؛ "
                    "وإن غابت، تُشار إلى هذا الغياب."
                )
            }
        }
    }

    user_msg = (
        "KPI PERFORMANCE ANALYSIS REQUEST\n\n"
        + _context_block(kpi_metadata, kpi_data_points)
        + "INSTRUCTIONS:\n"
        "Write a rigorous, paragraph-form performance analysis. Rules:\n"
        "  - Anchor every statement to specific period data, field names, or numeric values.\n"
        "  - Clearly distinguish between period-level and annual-level metrics when both exist.\n"
        "  - Do not repeat the raw data table; instead interpret and contextualise the numbers.\n"
        "  - If benchmarking data is missing, mention this as a limitation.\n"
        "  - STRICTLY ENFORCE LANGUAGE SEPARATION: The 'english' response must be 100% English, and the 'arabic' response 100% Arabic.\n"
        "  - TRANSLATE DATA: Translate Arabic input data into English for the English response. Translate English JSON keys/data into Arabic for the Arabic response.\n\n"
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
                "description": (
                    "3–5 root causes. Each item must follow this format: "
                    "'[Priority: Primary|Contributing] [Cause Title]: [One-sentence explanation] "
                    "— Evidence: [specific data point, field, or contextual note from the input that "
                    "supports this cause].'"
                )
            },
            "arabic": {
                "type": "array",
                "items": {"type": "string"},
                "description": (
                    "3–5 أسباب جذرية. كل عنصر يلتزم بالصيغة: "
                    "'[الأولوية: أساسي|مساهم] [عنوان السبب]: [جملة تفسيرية واحدة] "
                    "— الدليل: [نقطة البيانات أو الحقل أو الملاحظة السياقية المحددة من المدخلات التي تدعم هذا السبب].'"
                )
            }
        }
    }

    user_msg = (
        "KPI ROOT CAUSES REQUEST\n\n"
        + _context_block(kpi_metadata, kpi_data_points)
        + "INSTRUCTIONS:\n"
        "Identify 3–5 root causes explaining the KPI's performance. Rules:\n"
        "  - Classify each cause as 'Primary' (directly drives the variance) or 'Contributing' "
        "(amplifies or moderates it).\n"
        "  - Each cause MUST include a specific evidence reference — cite the period, field name, "
        "or exact figure from the data. Generic or unsupported causes are unacceptable.\n"
        "  - Causes that can be influenced by the entity's actions are preferred over purely "
        "external macro factors, unless the data strongly supports the latter.\n"
        "  - STRICTLY ENFORCE LANGUAGE SEPARATION: The 'english' response must be 100% English, and the 'arabic' response 100% Arabic.\n"
        "  - TRANSLATE EVIDENCE: Translate Arabic input data into English for the English response. Translate English JSON field keys/data into Arabic for the Arabic response.\n\n"
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
                "description": (
                    "4–6 recommendations split into two groups. "
                    "Short-term items (≤ 6 months) are marked '[Short-Term]' and "
                    "long-term items (> 6 months) are marked '[Long-Term]'. "
                    "Each item format: '[Timeframe] [Action Title]: [Specific action description] "
                    "— Addresses: [root cause or performance gap it targets].'"
                )
            },
            "arabic": {
                "type": "array",
                "items": {"type": "string"},
                "description": (
                    "4–6 توصيات مقسّمة إلى مجموعتين. "
                    "العناصر قصيرة المدى (≤ 6 أشهر) تُعلَّم بـ '[قصير المدى]' والطويلة (> 6 أشهر) بـ '[طويل المدى]'. "
                    "صيغة كل عنصر: '[الإطار الزمني] [عنوان الإجراء]: [وصف الإجراء المحدد] "
                    "— يعالج: [السبب الجذري أو فجوة الأداء المستهدفة].'"
                )
            }
        }
    }

    user_msg = (
        "KPI RECOMMENDATIONS REQUEST\n\n"
        + _context_block(kpi_metadata, kpi_data_points)
        + "INSTRUCTIONS:\n"
        "Produce 4–6 actionable recommendations. Rules:\n"
        "  - Split clearly into Short-Term (≤ 6 months) and Long-Term (> 6 months).\n"
        "  - Each recommendation must explicitly state which root cause or performance gap it targets.\n"
        "  - Recommendations must be specific, feasible, and relevant to the entity's context. "
        "Avoid generic advice that could apply to any KPI.\n"
        "  - Where benchmarking data is available, include at least one recommendation referencing it.\n"
        "  - STRICTLY ENFORCE LANGUAGE SEPARATION: The 'english' response must be 100% English, and the 'arabic' response 100% Arabic.\n"
        "  - TRANSLATE DATA: Translate Arabic input data into English for the English response. Translate English JSON keys/data into Arabic for the Arabic response.\n\n"
        f"REQUIRED OUTPUT SCHEMA:\n{json.dumps(schema, ensure_ascii=False, indent=2)}\n\n"
        "Provide ONLY valid JSON matching this schema. No additional text."
    )

    return _SYSTEM_INSTRUCTION, user_msg
