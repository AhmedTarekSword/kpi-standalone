import streamlit as st
import pandas as pd
import base64
import json
from datetime import date
import os
from core.report_generator import ReportGenerator
from gemini_integration.gemini_client import GeminiClient
from gemini_integration.prompts import (
    build_executive_summary_prompt,
    build_performance_analysis_prompt,
    build_root_causes_prompt,
    build_recommendations_prompt,
)
from scripts.parse_kpi_excel import parse_kpi_excel

st.set_page_config(page_title="KPI Data Entry Application", layout="wide")

# ===========================================================================
# SAMPLE DATA
# ===========================================================================
SAMPLE_METADATA = {
    "general_info": "جهة حكومية تُعنى بتطوير وتنفيذ مبادرات تحسين جودة الخدمات للمواطنين.",
    "strategic_context": "ضمن خطة الحكومة 2030 لرفع مستوى الكفاءة وتحقيق التحول الرقمي.",
    "tasks_and_services": "تقديم الخدمات الإدارية الإلكترونية، ومعالجة الطلبات الحكومية، وإصدار التراخيص.",
    "organizational_context": "تُطبّق الجهة منهجية الأداء المتوازن (BSC) وإطار OKR لإدارة الأداء.",
    "kpi_type": "مؤشر كفاءة تشغيلية",
    "kpi_name_ar": "مؤشر رضا المتعاملين عن الخدمات الإلكترونية",
    "kpi_name_en": "Digital Services Customer Satisfaction Index",
    "description_ar": "يقيس نسبة المتعاملين الراضين عن الخدمات الإلكترونية المقدمة من الجهة.",
    "description_en": "Measures the percentage of customers satisfied with the entity's digital services.",
    "entity_name_ar": "دائرة تطوير الخدمات الحكومية",
    "entity_name_en": "Government Services Development Department",
    "organizational_unit_ar": "إدارة التحول الرقمي",
    "organizational_unit_en": "Digital Transformation Division",
    "strategic_objective": "تعزيز تجربة المتعامل وتحسين جودة الخدمات الإلكترونية",
    "initiative": "مبادرة تحول رقمي متكامل 2024-2026",
    "dubai_government_kpi": "مؤشر دبي للبيانات والذكاء الاصطناعي - رضا المستخدم",
    "affected_kpis": "مؤشر معدل إتمام المعاملات الإلكترونية",
    "affecting_kpis": "مؤشر وقت الاستجابة للطلبات",
    "benchmarking_references": "تقرير الأمم المتحدة للحكومة الإلكترونية 2024، ITU Digital Services Index",
    "unit_of_measurement": "نسبة مئوية (%)",
    "frequency": "ربع سنوي",
    "primary_kpi": "نعم",
    "baseline_years": "2022",
    "measurement_mechanism": "استبيان إلكتروني بعد إتمام الخدمة",
    "target_calculation_method": "متوسط قيم الأرباع الأربعة",
    "formula": "(عدد المتعاملين الراضين / إجمالي المتعاملين) × 100",
}

SAMPLE_DATA_POINTS = [
    {
        "الربع/الفترة": "Q1",
        "السنة": "2024",
        "سنة الدورة الاستراتيجية": "2024",
        "محقق الفترة": "78%",
        "مستهدف الفترة": "80%",
        "أداء الفترة": "97.5%",
        "المحقق السنوي": "",
        "المستهدف السنوي": "85%",
        "الأداء السنوي": "",
        "الأحداث الخارجية (إدخال يدوي/إن وجدت)": "إطلاق نسخة جديدة من البوابة الإلكترونية في يناير",
        "نسبة أثر الحدث الخارجي المتوقعة على النتيجة": "10%",
        "التحليل (إن وجد)": "انخفاض مؤقت بسبب تعوّد المتعاملين على الواجهة الجديدة",
        "التوصيات (إن وجد)": "تعزيز دعم المستخدم خلال فترات الإطلاق",
        "فرص التحسين (إن وجد)": "تحسين تجربة التهيئة الأولية للمستخدم",
        "المقارنة المعيارية - الدولة/ المنطقة": "سنغافورة",
        "المقارنة المعيارية - السنة": "2023",
        "المقارنة المعيارية - القيمة": "84%",
    },
    {
        "الربع/الفترة": "Q2",
        "السنة": "2024",
        "سنة الدورة الاستراتيجية": "2024",
        "محقق الفترة": "82%",
        "مستهدف الفترة": "82%",
        "أداء الفترة": "100%",
        "المحقق السنوي": "",
        "المستهدف السنوي": "85%",
        "الأداء السنوي": "",
        "الأحداث الخارجية (إدخال يدوي/إن وجدت)": "",
        "نسبة أثر الحدث الخارجي المتوقعة على النتيجة": "",
        "التحليل (إن وجد)": "تسقق الأداء بعد اعتياد المتعاملين على الواجهة الجديدة",
        "التوصيات (إن وجد)": "",
        "فرص التحسين (إن وجد)": "إضافة خاصية التغذية الراجعة الفورية",
        "المقارنة المعيارية - الدولة/ المنطقة": "إستونيا",
        "المقارنة المعيارية - السنة": "2023",
        "المقارنة المعيارية - القيمة": "88%",
    },
    {
        "الربع/الفترة": "Q3",
        "السنة": "2024",
        "سنة الدورة الاستراتيجية": "2024",
        "محقق الفترة": "85%",
        "مستهدف الفترة": "83%",
        "أداء الفترة": "102.4%",
        "المحقق السنوي": "",
        "المستهدف السنوي": "85%",
        "الأداء السنوي": "",
        "الأحداث الخارجية (إدخال يدوي/إن وجدت)": "إطلاق برنامج ولاء المتعاملين",
        "نسبة أثر الحدث الخارجي المتوقعة على النتيجة": "5%",
        "التحليل (إن وجد)": "تجاوز الهدف للمرة الأولى بفضل برنامج الولاء",
        "التوصيات (إن وجد)": "توسيع برنامج الولاء ليشمل جميع الخدمات",
        "فرص التحسين (إن وجد)": "",
        "المقارنة المعيارية - الدولة/ المنطقة": "كوريا الجنوبية",
        "المقارنة المعيارية - السنة": "2023",
        "المقارنة المعيارية - القيمة": "91%",
    },
    {
        "الربع/الفترة": "Q4",
        "السنة": "2024",
        "سنة الدورة الاستراتيجية": "2024",
        "محقق الفترة": "87%",
        "مستهدف الفترة": "85%",
        "أداء الفترة": "102.4%",
        "المحقق السنوي": "83%",
        "المستهدف السنوي": "85%",
        "الأداء السنوي": "97.6%",
        "الأحداث الخارجية (إدخال يدوي/إن وجدت)": "",
        "نسبة أثر الحدث الخارجي المتوقعة على النتيجة": "",
        "التحليل (إن وجد)": "أفضل ربع سنوي على الإطلاق، لكن المتوسط السنوي لم يبلغ الهدف",
        "التوصيات (إن وجد)": "تحليل فجوة Q1 واستيعاب أثرها في تخطيط 2025",
        "فرص التحسين (إن وجد)": "تقييم أثر انخفاض Q1 على المتوسط السنوي وتحسين خطط بداية العام",
        "المقارنة المعيارية - الدولة/ المنطقة": "الإمارات - متوسط القطاع",
        "المقارنة المعيارية - السنة": "2024",
        "المقارنة المعيارية - القيمة": "80%",
    },
]

# Column mapping (Arabic UI → English keys for analysis)
_COLUMN_MAPPING = {
    "الربع/الفترة": "period_quarter",
    "السنة": "year",
    "سنة الدورة الاستراتيجية": "strategic_cycle_year",
    "محقق الفترة": "period_actual",
    "مستهدف الفترة": "period_target",
    "أداء الفترة": "period_performance",
    "المحقق السنوي": "annual_actual",
    "المستهدف السنوي": "annual_target",
    "الأداء السنوي": "annual_performance",
    "الأحداث الخارجية (إدخال يدوي/إن وجدت)": "external_events",
    "نسبة أثر الحدث الخارجي المتوقعة على النتيجة": "external_event_impact_percentage",
    "التحليل (إن وجد)": "analysis",
    "التوصيات (إن وجد)": "recommendations",
    "فرص التحسين (إن وجد)": "improvement_opportunities",
    "المقارنة المعيارية - الدولة/ المنطقة": "benchmark_country_region",
    "المقارنة المعيارية - السنة": "benchmark_year",
    "المقارنة المعيارية - القيمة": "benchmark_value",
}

# ===========================================================================
# SIDEBAR – Demo Report
# ===========================================================================
with st.sidebar:
    st.header("خيارات إضافية")
    st.markdown("تحميل تقرير تجريبي للتعرف على شكل المخرجات النهائية.")

    export_type_demo = st.radio(
        "نوع الملف للتقرير التجريبي:",
        ["Word (DOCX)", "PDF"],
        horizontal=True,
        key="demo_export_type",
    )
    if st.button("توليد التقرير التجريبي", type="secondary", width='stretch'):
        demo_metadata = {
            "kpi_name_ar": "مؤشر السعادة الوظيفية (تجريبي)",
            "entity_name_ar": "جهة حكومية تجريبية",
        }
        demo_analysis = {
            "arabic": {
                "executive_summary": "هذا تقرير تجريبي يوضح شكل مخرجات النظام. المؤشر يظهر أداءً مستقراً بشكل عام متجاوزاً المستهدفات المحددة.",
                "performance_analysis": "من خلال البيانات التجريبية، يتضح أن هناك نمواً بنسبة 5% في الربع الأخير مقارنة بخط الأساس مما يعكس فعالية المبادرات المنفذة.",
                "root_causes": ["سبب تجريبي 1: تحسين بيئة العمل وتطبيق نظام إدارة الأداء الجديد", "سبب تجريبي 2: حوافز مادية وتدريب الكوادر البشرية"],
                "recommendations": ["توصية تجريبية 1: الاستمرار في المراقبة الدورية للأداء", "توصية تجريبية 2: توسيع نطاق المبادرات الناجحة وعمل استبيانات دورية"],
            },
            "english": {
                "executive_summary": "This is a demo report illustrating the system output format. The KPI shows stable performance generally exceeding set targets.",
                "performance_analysis": "Demo data analysis shows 5% growth in the last quarter compared to baseline, reflecting the effectiveness of implemented initiatives.",
                "root_causes": ["Demo root cause 1: Improved work environment and new performance management system", "Demo root cause 2: Financial incentives and workforce training"],
                "recommendations": ["Demo recommendation 1: Continue periodic performance monitoring", "Demo recommendation 2: Expand successful initiatives and conduct regular surveys"],
            },
        }
        try:
            generator = ReportGenerator()
            if export_type_demo == "Word (DOCX)":
                b64_data = generator.generate_docx_base64(demo_metadata, demo_analysis, language="arabic")
                file_ext = "docx"
                mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            else:
                b64_data = generator.generate_pdf_base64(demo_metadata, demo_analysis, language="arabic")
                file_ext = "pdf"
                mime_type = "application/pdf"

            report_bytes = base64.b64decode(b64_data)
            st.session_state.demo_report_bytes = report_bytes
            st.session_state.demo_file_ext = file_ext
            st.session_state.demo_mime_type = mime_type
        except Exception as e:
            st.sidebar.error(f"حدث خطأ أثناء إعداد التقرير التجريبي: {str(e)}")

    if "demo_report_bytes" in st.session_state:
        st.download_button(
            label=f"📥 تحميل التقرير ({st.session_state.demo_file_ext.upper()})",
            data=st.session_state.demo_report_bytes,
            file_name=f"Demo_Analysis_Report.{st.session_state.demo_file_ext}",
            mime=st.session_state.demo_mime_type,
            type="primary",
            width='stretch',
        )

# ===========================================================================
# PAGE HEADER + SAMPLE DATA BUTTON
# ===========================================================================
st.title("KPI Analysis")
st.markdown(
    "Enter KPI information. "
    "Submit everything together for analysis."
)

# --- Input Method Toggle ---
input_method = st.radio(
    "Choose Input Method:",
    ["Manual Entry", "Upload Excel"],
    horizontal=True,
    key="input_method"
)

if input_method == "Upload Excel":
    uploaded_file = st.file_uploader("Upload KPI Excel File", type=["xlsx"])
    if uploaded_file is not None:
        if st.button("Parse Excel File", type="primary"):
            try:
                # Save the uploaded file to the data folder
                data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
                os.makedirs(data_dir, exist_ok=True)
                save_path = os.path.join(data_dir, uploaded_file.name)
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                parsed_data = parse_kpi_excel(uploaded_file)
                st.success(f"Data parsed and file saved to data/{uploaded_file.name} successfully!")
                
                # Update session state with parsed metadata
                for key, value in parsed_data["metadata"].items():
                    st.session_state[f"field_{key}"] = value
                    
                # The data_points need to map to our session state
                st.session_state.kpi_data_points = parsed_data["data_points"]
                
                # Optional: We might still want to manually map Arabic keys to our specific english field names
                # or we just rely on whatever matched. For robustness, we will map known ones.
                meta = parsed_data["metadata"]
                st.session_state["field_general_info"] = meta.get("المعلومات الأساسية عن الجهة", "")
                st.session_state["field_strategic_context"] = meta.get("السياق الاستراتيجي", "")
                st.session_state["field_tasks_and_services"] = meta.get("المهام والخدمات", "")
                st.session_state["field_organizational_context"] = meta.get("السياق التنظيمي وإدارة الأداء", "")
                st.session_state["field_kpi_type"] = meta.get("نوع المؤشر", "")
                st.session_state["field_kpi_name_ar"] = meta.get("اسم المؤشر بالعربية", "")
                st.session_state["field_kpi_name_en"] = meta.get("اسم المؤشر بالإنجليزية", "")
                st.session_state["field_description_ar"] = meta.get("الوصف بالعربية", "")
                st.session_state["field_description_en"] = meta.get("الوصف بالإنجليزية", "")
                st.session_state["field_entity_name_ar"] = meta.get("اسم الجهة بالعربية", "")
                st.session_state["field_entity_name_en"] = meta.get("اسم الجهة بالإنجليزية", "")
                st.session_state["field_organizational_unit_ar"] = meta.get("الوحدة التنظيمية بالعربية", "")
                st.session_state["field_organizational_unit_en"] = meta.get("الوحدة التنظيمية بالإنجليزية", "")
                st.session_state["field_strategic_objective"] = meta.get("الهدف الاستراتيجي المرتبط بالمؤشر/  إن وجد", "")
                st.session_state["field_initiative"] = meta.get("المبادرة المرتبطة بالمؤشر/  إن وجد", "")
                st.session_state["field_dubai_government_kpi"] = meta.get("ارتباطه بمؤشرات حكومة دبي /  إن وجد", "")
                st.session_state["field_affected_kpis"] = meta.get("المؤشرات المأثرة  /  إن وجد", "")
                st.session_state["field_affecting_kpis"] = meta.get("المؤشرات المتأثرة /  إن وجد", "")
                st.session_state["field_benchmarking_references"] = meta.get("مراجع ومصادر معتمدة للمقارنة المعيارية بالذكاء الاصطناعي", "")
                st.session_state["field_unit_of_measurement"] = meta.get("وحدة القياس", "")
                st.session_state["field_frequency"] = meta.get("دورية القياس", "")
                st.session_state["field_primary_kpi"] = meta.get("مؤشر الأداء الرئيسي الأساسي", "نعم")
                st.session_state["field_baseline_years"] = meta.get("سنوات الأساس", "")
                st.session_state["field_measurement_mechanism"] = meta.get("آلية القياس", "")
                st.session_state["field_target_calculation_method"] = meta.get("طريقة إحتساب المستهدف السنوي", "")
                st.session_state["field_formula"] = meta.get("المعادلة*", "")

                st.rerun()
            except Exception as e:
                st.error(f"Error parsing file: {e}")
else:
    # --- Sample Data Loader ---
    if st.button("📋 Load Sample Data", help="Pre-fill all fields with realistic demo data for quick testing"):
        for key, value in SAMPLE_METADATA.items():
            st.session_state[f"field_{key}"] = value
        st.session_state.kpi_data_points = SAMPLE_DATA_POINTS
        st.rerun()

st.divider()

# ===========================================================================
# FORM FIELDS (read defaults from session state so sample data appears)
# ===========================================================================

def _field(key: str, default: str = "") -> str:
    """Return the session-state value for a form field, falling back to default."""
    return st.session_state.get(f"field_{key}", default)

general_info = _field("general_info")
strategic_context = _field("strategic_context")
tasks_and_services = _field("tasks_and_services")
organizational_context = _field("organizational_context")
kpi_type = _field("kpi_type")
kpi_name_ar = _field("kpi_name_ar")
kpi_name_en = _field("kpi_name_en")
description_ar = _field("description_ar")
description_en = _field("description_en")
entity_name_ar = _field("entity_name_ar")
entity_name_en = _field("entity_name_en")
organizational_unit_ar = _field("organizational_unit_ar")
organizational_unit_en = _field("organizational_unit_en")
strategic_objective = _field("strategic_objective")
initiative = _field("initiative")
dubai_government_kpi = _field("dubai_government_kpi")
affected_kpis = _field("affected_kpis")
affecting_kpis = _field("affecting_kpis")
benchmarking_references = _field("benchmarking_references")
unit_of_measurement = _field("unit_of_measurement")
frequency = _field("frequency")
primary_kpi_default = _field("primary_kpi") or "نعم"
primary_kpi = primary_kpi_default
baseline_years = _field("baseline_years")
measurement_mechanism = _field("measurement_mechanism")
target_calculation_method = _field("target_calculation_method")
formula = _field("formula")

if input_method == "Manual Entry":
    col3, col2, col1 = st.columns(3)

    with col1:
        st.subheader("معلومات عامة عن الجهة")
        general_info = st.text_input("المعلومات الأساسية عن الجهة", value=general_info, placeholder="...أدخل المعلومات الأساسية")
        strategic_context = st.text_input("السياق الاستراتيجي (اختياري)", value=strategic_context, placeholder="...أدخل السياق الاستراتيجي")
        tasks_and_services = st.text_input("المهام والخدمات", value=tasks_and_services, placeholder="...أدخل المهام والخدمات")
        organizational_context = st.text_input("السياق التنظيمي وإدارة الأداء (اختياري)", value=organizational_context, placeholder="...أدخل السياق التنظيمي")

    with col2:
        st.subheader("معلومات المؤشر")
        kpi_type = st.text_input("نوع المؤشر", value=kpi_type, placeholder="...أدخل نوع المؤشر")
        kpi_name_ar = st.text_input("اسم المؤشر بالعربية", value=kpi_name_ar, placeholder="...أدخل اسم المؤشر بالعربية")
        kpi_name_en = st.text_input("اسم المؤشر بالإنجليزية (اختياري)", value=kpi_name_en, placeholder="...أدخل اسم المؤشر بالإنجليزية")
        description_ar = st.text_input("الوصف بالعربية", value=description_ar, placeholder="...أدخل الوصف بالعربية")
        description_en = st.text_input("الوصف بالإنجليزية (اختياري)", value=description_en, placeholder="...أدخل الوصف بالإنجليزية")
        entity_name_ar = st.text_input("اسم الجهة بالعربية", value=entity_name_ar, placeholder="...أدخل اسم الجهة بالعربية")
        entity_name_en = st.text_input("اسم الجهة بالإنجليزية (اختياري)", value=entity_name_en, placeholder="...أدخل اسم الجهة بالإنجليزية")
        organizational_unit_ar = st.text_input("الوحدة التنظيمية بالعربية", value=organizational_unit_ar, placeholder="...أدخل الوحدة التنظيمية بالعربية")
        organizational_unit_en = st.text_input("الوحدة التنظيمية بالإنجليزية (اختياري)", value=organizational_unit_en, placeholder="...أدخل الوحدة التنظيمية بالإنجليزية")
        strategic_objective = st.text_input("الهدف الاستراتيجي المرتبط بالمؤشر (إن وجد)", value=strategic_objective, placeholder="...أدخل الهدف الاستراتيجي")
        initiative = st.text_input("المبادرة المرتبطة بالمؤشر (إن وجد)", value=initiative, placeholder="...أدخل المبادرة")
        dubai_government_kpi = st.text_input("ارتباطه بمؤشرات حكومة دبي (إن وجد)", value=dubai_government_kpi, placeholder="...أدخل الارتباط بمؤشرات حكومة دبي")
        affected_kpis = st.text_input("المؤشرات المأثرة (إن وجد)", value=affected_kpis, placeholder="...أدخل المؤشرات المأثرة")
        affecting_kpis = st.text_input("المؤشرات المتأثرة (إن وجد)", value=affecting_kpis, placeholder="...أدخل المؤشرات المتأثرة")
        benchmarking_references = st.text_input("مراجع ومصادر معتمدة للمقارنة المعيارية بالذكاء الاصطناعي (اختياري)", value=benchmarking_references, placeholder="...أدخل المراجع والمصادر")

    with col3:
        st.subheader("تفاصيل القياس")
        unit_of_measurement = st.text_input("وحدة القياس", value=unit_of_measurement, placeholder="نسبة مئوية")
        frequency = st.text_input("دورية القياس", value=frequency, placeholder="ربع سنوي")
        primary_kpi_options = ["نعم", "لا"]
        primary_kpi_idx = primary_kpi_options.index(primary_kpi_default) if primary_kpi_default in primary_kpi_options else 0
        primary_kpi = st.selectbox("مؤشر الأداء الرئيسي الأساسي", primary_kpi_options, index=primary_kpi_idx)
        baseline_years = st.text_input("سنوات الأساس", value=baseline_years, placeholder="...أدخل سنوات الأساس")
        measurement_mechanism = st.text_input("آلية القياس", value=measurement_mechanism, placeholder="معادلة")
        target_calculation_method = st.text_input("طريقة إحتساب المستهدف السنوي", value=target_calculation_method, placeholder="متوسط القيم")
        formula = st.text_input("*المعادلة", value=formula, placeholder="A+B")

# st.divider()

# ===========================================================================
# KPI DATA POINTS TABLE
# ===========================================================================
    st.subheader("KPI Data Points")

    empty_cols = list(_COLUMN_MAPPING.keys())

    if "kpi_data_points" not in st.session_state:
        st.session_state.kpi_data_points = []

    if st.session_state.kpi_data_points:
        df = pd.DataFrame(st.session_state.kpi_data_points)
        # Ensure all expected columns exist (handles partial sample reloads)
        for col in empty_cols:
            if col not in df.columns:
                df[col] = ""
        df = df[empty_cols]
    else:
        df = pd.DataFrame(columns=empty_cols)

    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        width='stretch',
        key="data_points_editor",
    )

    st.session_state.kpi_data_points = edited_df.to_dict("records")

    st.divider()

# ===========================================================================
# SESSION STATE INITIALISATION FOR ANALYSIS
# ===========================================================================
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "analysis_metadata" not in st.session_state:
    st.session_state.analysis_metadata = None
if "analysis_data_points" not in st.session_state:
    st.session_state.analysis_data_points = None

# ===========================================================================
# SUBMIT BUTTON
# ===========================================================================
if st.button("Submit KPI for Analysis", type="primary", width='stretch'):
    if not st.session_state.kpi_data_points:
        st.error("الرجاء إضافة نقاط بيانات للجدول أعلاه قبل الإرسال.")
    else:
        english_data_points = []
        for point in st.session_state.kpi_data_points:
            english_point = {_COLUMN_MAPPING.get(ar_key, ar_key): value for ar_key, value in point.items()}
            english_data_points.append(english_point)

        kpi_metadata = {
            "entity_general_info": general_info,
            "strategic_context": strategic_context,
            "tasks_and_services": tasks_and_services,
            "organizational_and_performance_context": organizational_context,
            "kpi_type": kpi_type,
            "kpi_name_ar": kpi_name_ar,
            "kpi_name_en": kpi_name_en,
            "description_ar": description_ar,
            "description_en": description_en,
            "entity_name_ar": entity_name_ar,
            "entity_name_en": entity_name_en,
            "organizational_unit_ar": organizational_unit_ar,
            "organizational_unit_en": organizational_unit_en,
            "strategic_objective": strategic_objective,
            "initiative": initiative,
            "dubai_government_kpi_link": dubai_government_kpi,
            "affected_kpis": affected_kpis,
            "affecting_kpis": affecting_kpis,
            "benchmarking_references": benchmarking_references,
            "unit_of_measurement": unit_of_measurement,
            "measurement_frequency": frequency,
            "is_primary_kpi": primary_kpi,
            "baseline_years": baseline_years,
            "measurement_mechanism": measurement_mechanism,
            "target_calculation_method": target_calculation_method,
            "formula": formula,
        }

        with st.spinner("Processing data using AI..."):
            try:
                gemini_client = GeminiClient()

                SECTIONS = [
                    ("executive_summary",    build_executive_summary_prompt,    {"english": "", "arabic": ""}),
                    ("performance_analysis", build_performance_analysis_prompt, {"english": "", "arabic": ""}),
                    ("root_causes",          build_root_causes_prompt,          {"english": [], "arabic": []}),
                    ("recommendations",      build_recommendations_prompt,      {"english": [], "arabic": []}),
                ]

                section_results = {}
                failed_sections = []

                for section_name, prompt_fn, fallback in SECTIONS:
                    result = gemini_client.run_section(
                        section_name, prompt_fn, kpi_metadata, english_data_points, fallback
                    )
                    section_results[section_name] = result
                    if result == fallback:
                        failed_sections.append(section_name)

                if failed_sections:
                    st.warning(
                        f"تعذّر توليد الأقسام التالية وتم استخدام قيم افتراضية: "
                        f"{', '.join(failed_sections)}"
                    )

                actual_analysis_result = {
                    "english": {key: section_results[key]["english"] for key in section_results},
                    "arabic":  {key: section_results[key]["arabic"]  for key in section_results},
                }

                st.session_state.analysis_metadata = kpi_metadata
                st.session_state.analysis_data_points = english_data_points
                st.session_state.analysis_result = actual_analysis_result

            except Exception as e:
                st.error(f"حدث خطأ أثناء التواصل مع نموذج الذكاء الاصطناعي: {str(e)}")
                st.session_state.analysis_metadata = None
                st.session_state.analysis_data_points = None
                st.session_state.analysis_result = None

# ===========================================================================
# ANALYSIS RESULTS & EXPORT
# ===========================================================================
if st.session_state.analysis_result is not None:
    st.success("تم إرسال بيانات المؤشر بنجاح للتحليل!")

    st.json({
        "kpi_metadata": st.session_state.analysis_metadata,
        "kpi_data_points": st.session_state.analysis_data_points,
        "analysis_result": st.session_state.analysis_result,
    })

    st.divider()
    st.subheader("تصدير تقرير التحليل")
    st.markdown("اختر لغة التقرير ونوع الملف لتحميل تقرير التحليل الشامل:")

    exp_col1, exp_col2 = st.columns(2)
    with exp_col1:
        export_language = st.radio(
            "لغة التقرير:",
            ["العربية", "English"],
            horizontal=True,
            key="export_language",
        )
    with exp_col2:
        export_type = st.radio(
            "نوع الملف:",
            ["Word (DOCX)", "PDF"],
            horizontal=True,
            key="export_type",
        )

    # Map UI selection → internal language key
    _LANG_MAP = {"العربية": "arabic", "English": "english"}
    _LANG_SUFFIX = {"العربية": "AR", "English": "EN"}
    chosen_language = _LANG_MAP[export_language]
    lang_suffix = _LANG_SUFFIX[export_language]

    try:
        generator = ReportGenerator()
        if export_type == "Word (DOCX)":
            b64_data = generator.generate_docx_base64(
                st.session_state.analysis_metadata,
                st.session_state.analysis_result,
                language=chosen_language,
            )
            file_ext = "docx"
            mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        else:
            b64_data = generator.generate_pdf_base64(
                st.session_state.analysis_metadata,
                st.session_state.analysis_result,
                language=chosen_language,
            )
            file_ext = "pdf"
            mime_type = "application/pdf"

        report_bytes = base64.b64decode(b64_data)
        kpi_name_ar_session = st.session_state.analysis_metadata.get("kpi_name_ar", "KPI")
        kpi_safe_name = str(kpi_name_ar_session).replace(" ", "_") if kpi_name_ar_session else "KPI"
        filename = f"Analysis_Report_{lang_suffix}_{kpi_safe_name}.{file_ext}"

        st.download_button(
            label=f"📥 تحميل كملف {export_type} ({export_language})",
            data=report_bytes,
            file_name=filename,
            mime=mime_type,
            type="primary",
        )
    except Exception as e:
        st.error(f"حدث خطأ أثناء إعداد التقرير: {str(e)}")
