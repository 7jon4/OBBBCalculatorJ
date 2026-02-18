import streamlit as st
import requests

WORKER_BASE = "https://obbb-tax-calculator.joncamacaro.workers.dev"
VALIDATE_URL = f"{WORKER_BASE}/validate-token"
CONSUME_URL = f"{WORKER_BASE}/consume-token"

st.set_page_config(page_title="OBBB Tax Calculator", layout="centered")

query_params = st.query_params
token = query_params.get("token")

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
    st.query_params.clear()

st.title("OBBB Tax Calculator")

st.subheader("Ingrese sus datos")

income = st.number_input("Ingreso anual", min_value=0.0, value=0.0)
expenses = st.number_input("Gastos anuales", min_value=0.0, value=0.0)

calculate_button = st.button("Calcular")

if calculate_button:

    if st.session_state.get("used", False):
        st.error("Este acceso ya fue utilizado.")
        st.stop()

    confirm = st.checkbox(
        "Confirmo que los datos ingresados son completos y correctos. Entiendo que al continuar se consumirá mi acceso y no podrá recuperarse."
    )

    if not confirm:
        st.warning("Debes confirmar antes de continuar.")
        st.stop()

    r = requests.post(
        CONSUME_URL,
        json={"token": st.session_state.token}
    )

    if r.status_code != 200 or not r.json().get("success"):
        st.error("Token inválido o ya utilizado.")
        st.stop()

    st.session_state.used = True

    # === AQUÍ VA TU LÓGICA REAL ===
    result = income - expenses

    st.success("Cálculo completado")
    st.write("Resultado:", result)
