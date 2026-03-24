import json
import toons
import sys
import os

# Add the root directory to path to import gemini_integration
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from gemini_integration.prompts import build_executive_summary_prompt

try:
    import tiktoken
    has_tiktoken = True
    enc = tiktoken.get_encoding("cl100k_base")
except ImportError:
    has_tiktoken = False

def estimate_tokens(text: str) -> int:
    if has_tiktoken:
        return len(enc.encode(text))
    return len(text) // 4

def build_json_context_block(kpi_metadata, kpi_data_points):
    """Return the context block using JSON instead of TOON for comparison."""
    return (
        f"===== KPI METADATA & CONTEXT =====\n"
        f"{json.dumps(kpi_metadata, ensure_ascii=False, indent=2)}\n\n"
        f"===== KPI DATA POINTS (PERIODIC ACTUALS VS TARGETS) =====\n"
        f"{json.dumps(kpi_data_points, ensure_ascii=False, indent=2)}\n\n"
    )

def main():
    # Sample data representing KPI data points and metadata
    kpi_metadata = {
        "entity": "Ministry of Health",
        "kpi_name": "Patient Wait Time",
        "period": "Annual",
        "unit": "Minutes",
        "benchmark_available": True
    }
    
    kpi_data_points = [
        {
            "period": "Q1",
            "actual": "45",
            "target": "30",
            "variance": "+15",
            "notes": "High patient volume due to flu season"
        },
        {
            "period": "Q2",
            "actual": "35",
            "target": "30",
            "variance": "+5",
            "notes": "Added new triage staff"
        },
        {
            "period": "Q3",
            "actual": "28",
            "target": "30",
            "variance": "-2",
            "notes": "Process improvements implemented"
        },
        {
            "period": "Q4",
            "actual": "25",
            "target": "30",
            "variance": "-5",
            "notes": "Sustained improvement"
        }
    ]

    # Get the the TOON version of the prompt using the updated prompts.py
    sys_instruction_toon, user_msg_toon = build_executive_summary_prompt(kpi_metadata, kpi_data_points)
    
    # Extract the schema and instructions used in build_executive_summary_prompt directly
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

    old_context_block = build_json_context_block(kpi_metadata, kpi_data_points)
    
    # Match the prompt instructions precisely
    old_user_msg_json = (
        "KPI EXECUTIVE SUMMARY REQUEST\n\n"
        + old_context_block
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

    print("="*50)
    print("PROMPT TOKEN USAGE COMPARISON: JSON Input vs TOON Input")
    print("="*50)
    
    json_chars = len(old_user_msg_json)
    toon_chars = len(user_msg_toon)
    
    json_tokens = estimate_tokens(old_user_msg_json)
    toon_tokens = estimate_tokens(user_msg_toon)

    token_type = "Actual Tokens (tiktoken)" if has_tiktoken else "Estimated Tokens (~ chars / 4)"

    print(f"\n1. Character Count (User Prompt):")
    print(f"   JSON Input Prompt: {json_chars} chars")
    print(f"   TOON Input Prompt: {toon_chars} chars")
    print(f"   Total Savings: {json_chars - toon_chars} chars ({((json_chars - toon_chars) / json_chars) * 100:.1f}%)")

    print(f"\n2. Token Usage ({token_type}):")
    print(f"   JSON Input Prompt: {json_tokens} tokens")
    print(f"   TOON Input Prompt: {toon_tokens} tokens")
    print(f"   Total Savings: {json_tokens - toon_tokens} tokens ({((json_tokens - toon_tokens) / json_tokens) * 100:.1f}%)")

    print("\n" + "="*50)
    print("NEW OPTIMIZED PROMPT PREVIEW (TOON Data + JSON Schema):")
    print("="*50)
    print(user_msg_toon[:350] + "......\n")
    print(user_msg_toon[-350:])

if __name__ == "__main__":
    main()
