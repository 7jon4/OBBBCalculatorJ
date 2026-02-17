import streamlit as st
import requests

# =========================
# CONFIG
# =========================

WORKER_BASE = "https://obbb-tax-calculator.joncamacaro.workers.dev"
VALIDATE_URL = f"{WORKER_BASE}/validate-token"
CONSUME_URL = f"{WORKER_BASE}/consume-token"

st.set_page_config(page_title="OBBB Tax Calculator", layout="centered")

# =========================
# TOKEN SECURITY
# =========================

query_params = st.query_params
token = query_params.get("token")

if "access_granted" not in st.session_state:

    if not token:
        st.error("❌ Acceso no autorizado. Debes completar el pago.")
        st.stop()

    try:
        r = requests.get(
            VALIDATE_URL,
            params={"token": token},
            timeout=5
        )
    except Exception:
        st.error("Error de conexión con el sistema.")
        st.stop()

    if r.status_code != 200 or not r.json().get("valid"):
        st.error("❌ Token inválido, expirado o suspendido.")
        st.stop()

    st.session_state.access_granted = True
    st.session_state.token = token
    st.session_state.used = False

    # Limpiar URL
    st.query_params.clear()


# =========================
# APP UI
# =========================

st.title("OBBB Tax Calculator")

st.write("Secure Access Granted")

# =========================
# ⬇⬇⬇ AQUI VAN LOS INPUTS DE TU CALCULADORA ⬇⬇⬇
# =========================

st.subheader("Enter your data")

income = st.number_input("Annual Income", min_value=0.0, value=0.0)
expenses = st.number_input("Annual Expenses", min_value=0.0, value=0.0)

# Aquí puedes agregar más inputs según tu lógica


# =========================
# 🔥 BOTON PRINCIPAL DE CALCULO
# =========================

calculate_button = st.button("Calculate")

if calculate_button:

    # =========================
    # CONSUMO DE TOKEN (solo afecta single)
    # =========================

    if not st.session_state.used:

        try:
            r = requests.post(
                CONSUME_URL,
                json={"token": st.session_state.token},
                timeout=5
            )
        except Exception:
            st.error("Error de conexión con el sistema.")
            st.stop()

        if r.status_code != 200 or not r.json().get("success"):
            st.error("❌ Token inválido o ya utilizado.")
            st.stop()

        st.session_state.used = True

    # =========================
    # ⬇⬇⬇ AQUI VA TU LOGICA DE CALCULO REAL ⬇⬇⬇
    # =========================

    # EJEMPLO SIMPLE (BORRAR DESPUES)
    result = income - expenses

    # =========================
    # MOSTRAR RESULTADOS
    # =========================

    st.success("Calculation Complete")
    st.write("Result:", result)


# =========================
# INFO EXTRA
# =========================

st.caption("If you have issues accessing your calculator, contact support.")
