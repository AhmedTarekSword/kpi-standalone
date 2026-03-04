import streamlit as st
import pandas as pd
import base64
import json
from datetime import date
from report_generator import ReportGenerator
from gemini_integration.gemini_client import GeminiClient
from gemini_integration.prompts import (
    build_executive_summary_prompt,
    build_performance_analysis_prompt,
    build_root_causes_prompt,
    build_recommendations_prompt,
)

st.set_page_config(page_title="KPI Data Entry Application", layout="wide")

with st.sidebar:
    st.header("خيارات إضافية")
    st.markdown("تحميل تقرير تجريبي للتعرف على شكل المخرجات النهائية.")
    
    export_type_demo = st.radio("نوع الملف للتقرير التجريبي:", ["Word (DOCX)", "PDF"], horizontal=True, key="demo_export_type")
    if st.button("توليد التقرير التجريبي", type="secondary", use_container_width=True):
        demo_metadata = {
            "kpi_name_ar": "مؤشر السعادة الوظيفية (تجريبي)",
            "entity_name_ar": "جهة حكومية تجريبية"
        }
        demo_analysis = {
            "arabic": {
                "executive_summary": "هذا تقرير تجريبي يوضح شكل مخرجات النظام. المؤشر يظهر أداءً مستقراً بشكل عام متجاوزاً المستهدفات المحددة.",
                "performance_analysis": "من خلال البيانات التجريبية، يتضح أن هناك نمواً بنسبة 5% في الربع الأخير مقارنة بخط الأساس مما يعكس فعالية المبادرات المنفذة.",
                "root_causes": ["سبب تجريبي 1: تحسين بيئة العمل وتطبيق نظام إدارة الأداء الجديد", "سبب تجريبي 2: حوافز مادية وتدريب الكوادر البشرية"],
                "recommendations": ["توصية تجريبية 1: الاستمرار في المراقبة الدورية للأداء", "توصية تجريبية 2: توسيع نطاق المبادرات الناجحة وعمل استبيانات دورية"]
            }
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

    if 'demo_report_bytes' in st.session_state:
        st.download_button(
            label=f"📥 تحميل التقرير ({st.session_state.demo_file_ext.upper()})",
            data=st.session_state.demo_report_bytes,
            file_name=f"Demo_Analysis_Report.{st.session_state.demo_file_ext}",
            mime=st.session_state.demo_mime_type,
            type="primary",
            use_container_width=True
        )

st.title("KPI Data Entry Page")
st.markdown("Enter KPI information below, and add the corresponding data points in the table. Submit everything together for analysis.")

col3, col2, col1 = st.columns(3)

with col1:
    st.subheader("معلومات عامة عن الجهة")
    general_info = st.text_input("المعلومات الأساسية عن الجهة", placeholder="...أدخل المعلومات الأساسية")
    strategic_context = st.text_input("السياق الاستراتيجي (اختياري)", placeholder="...أدخل السياق الاستراتيجي")
    tasks_and_services = st.text_input("المهام والخدمات", placeholder="...أدخل المهام والخدمات")
    organizational_context = st.text_input("السياق التنظيمي وإدارة الأداء (اختياري)", placeholder="...أدخل السياق التنظيمي")
    
with col2:
    st.subheader("معلومات المؤشر")
    kpi_type = st.text_input("نوع المؤشر", placeholder="...أدخل نوع المؤشر")
    kpi_name_ar = st.text_input("اسم المؤشر بالعربية", placeholder="...أدخل اسم المؤشر بالعربية")
    kpi_name_en = st.text_input("اسم المؤشر بالإنجليزية (اختياري)", placeholder="...أدخل اسم المؤشر بالإنجليزية")
    description_ar = st.text_input("الوصف بالعربية", placeholder="...أدخل الوصف بالعربية")
    description_en = st.text_input("الوصف بالإنجليزية (اختياري)", placeholder="...أدخل الوصف بالإنجليزية")
    entity_name_ar = st.text_input("اسم الجهة بالعربية", placeholder="...أدخل اسم الجهة بالعربية")
    entity_name_en = st.text_input("اسم الجهة بالإنجليزية (اختياري)", placeholder="...أدخل اسم الجهة بالإنجليزية")
    organizational_unit_ar = st.text_input("الوحدة التنظيمية بالعربية", placeholder="...أدخل الوحدة التنظيمية بالعربية")
    organizational_unit_en = st.text_input("الوحدة التنظيمية بالإنجليزية (اختياري)", placeholder="...أدخل الوحدة التنظيمية بالإنجليزية")
    strategic_objective = st.text_input("الهدف الاستراتيجي المرتبط بالمؤشر (إن وجد)", placeholder="...أدخل الهدف الاستراتيجي")
    initiative = st.text_input("المبادرة المرتبطة بالمؤشر (إن وجد)", placeholder="...أدخل المبادرة")
    dubai_government_kpi = st.text_input("ارتباطه بمؤشرات حكومة دبي (إن وجد)", placeholder="...أدخل الارتباط بمؤشرات حكومة دبي")
    affected_kpis = st.text_input("المؤشرات المأثرة (إن وجد)", placeholder="...أدخل المؤشرات المأثرة")
    affecting_kpis = st.text_input("المؤشرات المتأثرة (إن وجد)", placeholder="...أدخل المؤشرات المتأثرة")
    benchmarking_references = st.text_input("مراجع ومصادر معتمدة للمقارنة المعيارية بالذكاء الاصطناعي (اختياري)", placeholder="...أدخل المراجع والمصادر")
    
with col3:
    st.subheader("تفاصيل القياس")
    unit_of_measurement = st.text_input("وحدة القياس", placeholder="نسبة مئوية")
    frequency = st.text_input("دورية القياس", placeholder="ربع سنوي")
    primary_kpi = st.selectbox("مؤشر الأداء الرئيسي الأساسي", ["نعم", "لا"])
    baseline_years = st.text_input("سنوات الأساس", placeholder="...أدخل سنوات الأساس")
    measurement_mechanism = st.text_input("آلية القياس", placeholder="معادلة")
    target_calculation_method = st.text_input("طريقة إحتساب المستهدف السنوي", placeholder="متوسط القيم")
    formula = st.text_input("*المعادلة", placeholder="A+B")

st.divider()

st.subheader("KPI Data Points")
# st.markdown("Enter the specific data points (e.g. time period, target, actual) for this KPI below.")

# Initialize session state for the data points table
if 'kpi_data_points' not in st.session_state:
    st.session_state.kpi_data_points = []

# Table specifically for the KPI data points
empty_cols = [
    'الربع/الفترة', 'السنة', 'سنة الدورة الاستراتيجية', 'محقق الفترة',
    'مستهدف الفترة', 'أداء الفترة', 'المحقق السنوي', 'المستهدف السنوي',
    'الأداء السنوي', 'الأحداث الخارجية (إدخال يدوي/إن وجدت)',
    'نسبة أثر الحدث الخارجي المتوقعة على النتيجة', 'التحليل (إن وجد)',
    'التوصيات (إن وجد)', 'فرص التحسين (إن وجد)',
    'المقارنة المعيارية - الدولة/ المنطقة', 'المقارنة المعيارية - السنة', 'المقارنة المعيارية - القيمة'
]
if st.session_state.kpi_data_points:
    df = pd.DataFrame(st.session_state.kpi_data_points)
else:
    df = pd.DataFrame(columns=empty_cols)

edited_df = st.data_editor(
    df, 
    num_rows="dynamic", 
    use_container_width=True,
    key="data_points_editor"
)

st.session_state.kpi_data_points = edited_df.to_dict('records')

st.divider()

if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'analysis_metadata' not in st.session_state:
    st.session_state.analysis_metadata = None
if 'analysis_data_points' not in st.session_state:
    st.session_state.analysis_data_points = None

if st.button("Submit KPI for Analysis", type="primary", use_container_width=True):
    if not st.session_state.kpi_data_points:
        st.error("الرجاء إضافة نقاط بيانات للجدول أعلاه قبل الإرسال.")
    else:
        # Map the Arabic column names to English keys for the data points
        column_mapping = {
            'الربع/الفترة': 'period_quarter',
            'السنة': 'year',
            'سنة الدورة الاستراتيجية': 'strategic_cycle_year',
            'محقق الفترة': 'period_actual',
            'مستهدف الفترة': 'period_target',
            'أداء الفترة': 'period_performance',
            'المحقق السنوي': 'annual_actual',
            'المستهدف السنوي': 'annual_target',
            'الأداء السنوي': 'annual_performance',
            'الأحداث الخارجية (إدخال يدوي/إن وجدت)': 'external_events',
            'نسبة أثر الحدث الخارجي المتوقعة على النتيجة': 'external_event_impact_percentage',
            'التحليل (إن وجد)': 'analysis',
            'التوصيات (إن وجد)': 'recommendations',
            'فرص التحسين (إن وجد)': 'improvement_opportunities',
            'المقارنة المعيارية - الدولة/ المنطقة': 'benchmark_country_region',
            'المقارنة المعيارية - السنة': 'benchmark_year',
            'المقارنة المعيارية - القيمة': 'benchmark_value'
        }
        
        english_data_points = []
        for point in st.session_state.kpi_data_points:
            english_point = {}
            for ar_key, value in point.items():
                eng_key = column_mapping.get(ar_key, ar_key)
                english_point[eng_key] = value
            english_data_points.append(english_point)

        # All info is valid
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
            "formula": formula
        }
        
        with st.spinner("جاري تحليل البيانات باستخدام الذكاء الاصطناعي..."):
            try:
                gemini_client = GeminiClient()

                SECTIONS = [
                    (
                        "executive_summary",
                        build_executive_summary_prompt,
                        {"english": "", "arabic": ""},
                    ),
                    (
                        "performance_analysis",
                        build_performance_analysis_prompt,
                        {"english": "", "arabic": ""},
                    ),
                    (
                        "root_causes",
                        build_root_causes_prompt,
                        {"english": [], "arabic": []},
                    ),
                    (
                        "recommendations",
                        build_recommendations_prompt,
                        {"english": [], "arabic": []},
                    ),
                ]

                section_results = {}
                failed_sections = []

                for section_name, prompt_fn, fallback in SECTIONS:
                    result = gemini_client.run_section(
                        section_name, prompt_fn, kpi_metadata, english_data_points, fallback
                    )
                    section_results[section_name] = result
                    # Detect fallback by checking if content is empty/falsy
                    if result == fallback:
                        failed_sections.append(section_name)

                if failed_sections:
                    st.warning(
                        f"تعذّر توليد الأقسام التالية وتم استخدام قيم افتراضية: "
                        f"{', '.join(failed_sections)}"
                    )

                actual_analysis_result = {
                    "english": {
                        key: section_results[key]["english"] for key in section_results
                    },
                    "arabic": {
                        key: section_results[key]["arabic"] for key in section_results
                    },
                }

                st.session_state.analysis_metadata = kpi_metadata
                st.session_state.analysis_data_points = english_data_points
                st.session_state.analysis_result = actual_analysis_result

            except Exception as e:
                st.error(f"حدث خطأ أثناء التواصل مع نموذج الذكاء الاصطناعي: {str(e)}")
                st.session_state.analysis_metadata = None
                st.session_state.analysis_data_points = None
                st.session_state.analysis_result = None

if st.session_state.analysis_result is not None:
    st.success("تم إرسال بيانات المؤشر بنجاح للتحليل!")
    
    st.json({
        "kpi_metadata": st.session_state.analysis_metadata,
        "kpi_data_points": st.session_state.analysis_data_points,
        "analysis_result": st.session_state.analysis_result
    })
    
    st.divider()
    st.subheader("تصدير تقرير التحليل")
    st.markdown("اختر نوع الملف لتحميل تقرير التحليل الشامل:")
    
    export_type = st.radio("نوع الملف:", ["Word (DOCX)", "PDF"], horizontal=True)
    
    try:
        generator = ReportGenerator()
        if export_type == "Word (DOCX)":
            b64_data = generator.generate_docx_base64(st.session_state.analysis_metadata, st.session_state.analysis_result, language="arabic")
            file_ext = "docx"
            mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        else:
            b64_data = generator.generate_pdf_base64(st.session_state.analysis_metadata, st.session_state.analysis_result, language="arabic")
            file_ext = "pdf"
            mime_type = "application/pdf"
            
        # Provide download link using base64
        report_bytes = base64.b64decode(b64_data)
        kpi_name_ar_session = st.session_state.analysis_metadata.get("kpi_name_ar", "KPI")
        kpi_safe_name = str(kpi_name_ar_session).replace(' ', '_') if kpi_name_ar_session else "KPI"
        filename = f"Analysis_Report_{kpi_safe_name}.{file_ext}"
        
        st.download_button(
            label=f"📥 تحميل كملف {export_type}",
            data=report_bytes,
            file_name=filename,
            mime=mime_type,
            type="primary"
        )
    except Exception as e:
        st.error(f"حدث خطأ أثناء إعداد التقرير: {str(e)}")
