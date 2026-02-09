import streamlit as st
import requests
from datetime import datetime
from logic import calculate_ot_premium, apply_phaseout
from pdf_utils import extract_amounts
from pdf_export import generate_pdf

# =========================
# CONFIG
# =========================
WORKER_VALIDATE_URL = "https://obbb-tax-calculator.joncamacaro.workers.dev/validate-token"
WORKER_CONSUME_URL = "https://obbb-tax-calculator.joncamacaro.workers.dev/consume-token"

st.set_page_config(
    page_title="OBBB 2025 Calculator",
    layout="centered"
)

# =========================
# SEGURIDAD: TOKEN (1 VEZ)
# =========================
query_params = st.query_params

if "token" not in st.session_state:
    token = query_params.get("token")
    if not token:
        st.error("❌ Acceso no autorizado. Debes completar el pago.")
        st.stop()

    # Validar token al entrar
    try:
        r = requests.get(
            WORKER_VALIDATE_URL,
            params={"token": token},
            timeout=5
        )
    except Exception:
        st.error("Error de conexión con el sistema de validación.")
        st.stop()

    if r.status_code != 200:
        st.error("❌ Token inválido o ya utilizado.")
        st.stop()

    # Guardar token en sesión
    st.session_state.token = token
    st.session_state.used = False

    # Limpiar URL (anti copia)
    st.query_params.clear()

# =========================
# TEXTOS
# =========================
update_version_date = datetime.now().strftime('%Y-%m-%d')

texts = {
    "es": {
        "title": "Calculadora de Deducciones OBBB",
        "desc": "Herramienta para estimar deducciones por propinas y horas extras según la Ley OBBB 2025.\nIMPORTANTE: Esto NO es asesoría fiscal oficial.",
        "upload_label": "1️⃣ Sube tus documentos",
        "upload_instructions": "PDFs (W-2, 1099, paystubs) – máx. 5",
        "income_label": "2️⃣ Información de Ingresos",
        "filing_status_label": "Estado civil",
        "filing_options": ["Soltero / Cabeza de familia", "Casado declarando conjuntamente"],
        "magi_label": "MAGI estimado ($)",
        "tips_label": "Propinas calificadas ($)",
        "ot_label": "Pago total de horas extras ($)",
        "multiplier_label": "Multiplicador OT",
        "calc_button": "Calcular deducciones",
        "results_title": "📊 Resultados",
        "tips_ded": "Deducción por propinas",
        "ot_ded": "Deducción por OT",
        "total_ded": "💰 Total Aproximado:",
        "footer": "Hecho por Carlos E. Martinez",
    },
    "en": {
        "title": "OBBB Deductions Calculator",
        "desc": "Tool to estimate deductions for tips and overtime under OBBB Act 2025. Not tax advice.",
        "upload_label": "1️⃣ Upload documents",
        "upload_instructions": "PDFs (W-2, 1099, paystubs) – max 5",
        "income_label": "2️⃣ Income Information",
        "filing_status_label": "Filing Status",
        "filing_options": ["Single / Head of Household", "Married Filing Jointly"],
        "magi_label": "Estimated MAGI ($)",
        "tips_label": "Qualified Tips ($)",
        "ot_label": "Total Overtime Pay ($)",
        "multiplier_label": "OT Multiplier",
        "calc_button": "Calculate deductions",
        "results_title": "📊 Results",
        "tips_ded": "Tips Deduction",
        "ot_ded": "OT Deduction",
        "total_ded": "💰 Total Estimated:",
        "footer": "Made by Carlos E. Martinez",
    }
}

language = st.selectbox("Idioma / Language", ["Español", "English"])
lang = "es" if language == "Español" else "en"
t = texts[lang]

# =========================
# UI
# =========================
st.title(t["title"])
st.info(t["desc"])

# -------------------------
# UPLOAD
# -------------------------
st.markdown("---")
st.subheader(t["upload_label"])

uploaded_files = st.file_uploader(
    t["upload_instructions"],
    type="pdf",
    accept_multiple_files=True
)

extracted_magi = extracted_tips = extracted_ot = 0.0

if uploaded_files:
    extracted_magi, extracted_tips, extracted_ot = extract_amounts(uploaded_files)

# -------------------------
# INPUTS
# -------------------------
st.markdown("---")
st.subheader(t["income_label"])

magi = st.number_input(
    t["magi_label"],
    min_value=0.0,
    value=extracted_magi,
    step=1000.0
)

filing_status = st.selectbox(
    t["filing_status_label"],
    t["filing_options"]
)

tips_amount = st.number_input(
    t["tips_label"],
    min_value=0.0,
    value=extracted_tips,
    step=100.0
)

ot_total = st.number_input(
    t["ot_label"],
    min_value=0.0,
    value=extracted_ot,
    step=100.0
)

ot_multiplier = st.number_input(
    t["multiplier_label"],
    min_value=1.0,
    value=1.5,
    step=0.5
)

# -------------------------
# CALCULATION (SE CONSUME AQUÍ)
# -------------------------
st.markdown("---")

if st.button(t["calc_button"], type="primary"):

    if st.session_state.used:
        st.warning("⚠️ Este cálculo ya fue utilizado.")
        st.stop()

    # Consumir token
    try:
        r = requests.post(
            WORKER_CONSUME_URL,
            json={"token": st.session_state.token},
            timeout=5
        )
    except Exception:
        st.error("Error de conexión con el sistema de consumo.")
        st.stop()

    if r.status_code != 200:
        st.error("❌ Token inválido o ya utilizado.")
        st.stop()

    st.session_state.used = True

    # ===== LÓGICA OBBB =====
    ot_premium = calculate_ot_premium(ot_total, ot_multiplier)

    if filing_status == t["filing_options"][1]:
        max_tips, max_ot, phase_start = 25000, 25000, 300000
    else:
        max_tips, max_ot, phase_start = 25000, 12500, 150000

    tips_ded = min(tips_amount, apply_phaseout(magi, max_tips, phase_start))
    ot_ded = min(ot_premium, apply_phaseout(magi, max_ot, phase_start))
    total = tips_ded + ot_ded

    # ===== RESULTADOS =====
    st.subheader(t["results_title"])
    st.success(f"{t['total_ded']} ${total:,.0f}")
    st.metric(t["tips_ded"], f"${tips_ded:,.0f}")
    st.metric(t["ot_ded"], f"${ot_ded:,.0f}")

    pdf_bytes = generate_pdf(total, tips_ded, ot_ded)

    st.download_button(
        "📄 Download PDF report",
        data=pdf_bytes,
        file_name="obbb_deduction_report.pdf",
        mime="application/pdf"
    )

    st.info("✅ Cálculo consumido. Para otro cálculo debes pagar nuevamente.")

# -------------------------
# FOOTER
# -------------------------
st.markdown("---")
st.caption(f"{t['footer']} • {update_version_date}")
