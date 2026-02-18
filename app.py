import streamlit as st
import requests

WORKER_BASE = "https://obbb-tax-calculator.joncamacaro.workers.dev"
VALIDATE_URL = f"{WORKER_BASE}/validate-token"
CONSUME_URL = f"{WORKER_BASE}/consume-token"

st.set_page_config(page_title="OBBB Tax Calculator", layout="centered")

query_params = st.query_params
token = query_params.get("token")

# =============================
# VALIDACIÓN INICIAL
# =============================
if "access_granted" not in st.session_state:

    if not token:
        st.error("Acceso no autorizado.")
        st.stop()

    r = requests.get(VALIDATE_URL, params={"token": token})

    if r.status_code != 200 or not r.json().get("valid"):
        st.error("Token inválido o expirado.")
        st.stop()

    st.session_state.access_granted = True
    st.session_state.token = token
    st.session_state.used = False
    st.session_state.confirmed = False
    st.query_params.clear()

# =============================
# BLOQUEAR SI YA FUE USADO
# =============================
if st.session_state.used:
    st.error("Este acceso ya fue utilizado y no puede volver a usarse.")
    st.stop()

# =============================
# INTERFAZ
# =============================
st.title("OBBB Tax Calculator")
st.subheader("Ingrese sus datos")

income = st.number_input("Ingreso anual", min_value=0.0, value=0.0)
expenses = st.number_input("Gastos anuales", min_value=0.0, value=0.0)

# Checkbox SIEMPRE visible
st.session_state.confirmed = st.checkbox(
    "Confirmo que los datos ingresados son completos y correctos. "
    "Entiendo que al continuar se consumirá mi acceso y no podrá recuperarse."
)

# Botón se deshabilita si no confirmó
calculate_button = st.button(
    "Calcular",
    disabled=not st.session_state.confirmed
)

# =============================
# ACCIÓN DE CÁLCULO
# =============================
if calculate_button:

    r = requests.post(
        CONSUME_URL,
        json={"token": st.session_state.token}
    )

    if r.status_code != 200 or not r.json().get("success"):
        st.error("Token inválido o ya utilizado.")
        st.stop()

    # Bloqueo inmediato en frontend
    st.session_state.used = True
    st.session_state.access_granted = False

    # === AQUÍ VA TU LÓGICA REAL ===
    result = income - expenses

    st.success("Cálculo completado")
    st.write("Resultado:", result)

    # Cortar ejecución para evitar reruns útiles
    st.stop()
