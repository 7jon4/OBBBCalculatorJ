import streamlit as st
import requests

WORKER_BASE = "https://obbb-tax-calculator.joncamacaro.workers.dev"
VALIDATE_URL = f"{WORKER_BASE}/validate-token"
CONSUME_URL = f"{WORKER_BASE}/consume-token"

st.set_page_config(page_title="OBBB Tax Calculator", layout="centered")

query_params = st.query_params
token = query_params.get("token")

# =============================
# VALIDACIÓN INICIAL (solo una vez)
# =============================
if "initialized" not in st.session_state:

    if not token:
        st.error("Acceso no autorizado.")
        st.stop()

    r = requests.get(VALIDATE_URL, params={"token": token})

    if r.status_code != 200 or not r.json().get("valid"):
        st.error("Token inválido o expirado.")
        st.stop()

    st.session_state.initialized = True
    st.session_state.token = token
    st.session_state.used = False
    st.session_state.confirmed = False
    st.session_state.result = None

    st.query_params.clear()

# =============================
# INTERFAZ
# =============================
st.title("OBBB Tax Calculator")
st.subheader("Ingrese sus datos")

income = st.number_input("Ingreso anual", min_value=0.0, value=0.0)
expenses = st.number_input("Gastos anuales", min_value=0.0, value=0.0)

# Confirmación siempre visible
confirmed = st.checkbox(
    "Confirmo que los datos ingresados son completos y correctos. "
    "Entiendo que al continuar se consumirá mi acceso y no podrá recuperarse.",
    disabled=st.session_state.used
)

# Botón se deshabilita si:
# - No confirmó
# - Ya fue usado
calculate_button = st.button(
    "Calcular",
    disabled=(not confirmed) or st.session_state.used
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
    else:
        # Marcar como usado en frontend
        st.session_state.used = True

        # === TU LÓGICA REAL AQUÍ ===
        st.session_state.result = income - expenses

# =============================
# MOSTRAR RESULTADO SI EXISTE
# =============================
if st.session_state.result is not None:
    st.success("Cálculo completado")
    st.write("Resultado:", st.session_state.result)

# =============================
# MENSAJE SI YA FUE USADO
# =============================
if st.session_state.used:
    st.warning("Este acceso ya fue utilizado. El cálculo no puede volver a ejecutarse.")
