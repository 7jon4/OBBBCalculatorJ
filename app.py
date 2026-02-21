"""
============================================================
OBBB TAX CALCULATOR - STREAMLIT FRONTEND
============================================================

FUNCIONALIDADES:

- Muestra planes si no hay token
- Redirige a Stripe
- Valida token con Cloudflare Worker
- Muestra contador restante
- Ejecuta lógica de cálculo
- Consume token solo si cálculo válido
- Muestra mensajes amigables
============================================================
"""

import streamlit as st
import requests
from datetime import datetime

# ============================================================
# CONFIGURACIÓN
# ============================================================

WORKER_BASE = "https://obbb-tax-calculator.joncamacaro.workers.dev"

st.set_page_config(
    page_title="OBBBT Tax Calculator",
    layout="centered"
)

# ============================================================
# FUNCIONES API
# ============================================================

def validate_token(token):
    """
    Llama al Worker para validar token.
    No consume uso.
    """
    try:
        r = requests.get(
            f"{WORKER_BASE}/validate",
            params={"token": token},
            timeout=10
        )
        return r.json()
    except:
        return {"valid": False, "message": "Error de conexión con el servidor."}


def consume_token(token):
    """
    Consume 1 uso si todo está correcto.
    """
    try:
        r = requests.post(
            f"{WORKER_BASE}/consume",
            json={"token": token},
            timeout=10
        )
        return r.json()
    except:
        return {"allowed": False, "message": "Error de conexión con el servidor."}


def create_checkout(plan_type):
    """
    Crea sesión Stripe y devuelve URL de pago.
    """
    try:
        r = requests.post(
            f"{WORKER_BASE}/create-checkout-session",
            json={"type": plan_type},
            timeout=10
        )
        data = r.json()
        return data.get("url")
    except:
        return None


# ============================================================
# DETECTAR TOKEN EN URL
# ============================================================

query_params = st.query_params
token = query_params.get("token")

# ============================================================
# SI NO HAY TOKEN → MOSTRAR PLANES
# ============================================================

if not token:

    st.title("OBBBT Tax Calculator")

    st.subheader("Selecciona tu plan")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Acceso Único")
        st.write("1 cálculo válido por 6 meses.")

        if st.button("Comprar Single"):
            checkout_url = create_checkout("single")
            if checkout_url:
                st.markdown(f"[Ir a pagar]({checkout_url})")
            else:
                st.error("Error creando sesión de pago.")

    with col2:
        st.markdown("### Suscripción Mensual")
        st.write("Hasta 100 cálculos por mes.")

        if st.button("Suscribirse"):
            checkout_url = create_checkout("sub")
            if checkout_url:
                st.markdown(f"[Ir a pagar]({checkout_url})")
            else:
                st.error("Error creando sesión de pago.")

    st.stop()

# ============================================================
# VALIDAR TOKEN
# ============================================================

validation = validate_token(token)

if not validation.get("valid"):
    st.error(validation.get("message", "Acceso inválido."))
    st.stop()

remaining = validation["remaining"]
expires = datetime.fromtimestamp(validation["expires_at"] / 1000)

st.success("Acceso activo")
st.info(f"Te quedan {remaining} usos disponibles.")
st.caption(f"Válido hasta: {expires.strftime('%Y-%m-%d')} UTC")

st.divider()

# ============================================================
# AQUÍ VA TU LÓGICA REAL
# ============================================================

st.subheader("Calculadora OBBBT")

# EJEMPLO DE INPUT (REEMPLAZAR POR TU LÓGICA REAL)
valor = st.number_input(
    "Valor de ejemplo",
    min_value=0.0
)

if st.button("Calcular"):

    # --------------------------------------------------------
    # 1. VALIDACIÓN INTERNA DE TU LÓGICA
    # --------------------------------------------------------

    if valor <= 0:
        st.error("El valor debe ser mayor que cero.")
        st.stop()

    # Aquí debe ir tu validación real del equipo de lógica
    # Si algo falla, NO consumimos token

    # --------------------------------------------------------
    # 2. CONSUMIR TOKEN SOLO SI TODO ES CORRECTO
    # --------------------------------------------------------

    consumo = consume_token(token)

    if not consumo.get("allowed"):
        st.error(consumo.get("message", "No permitido."))
        st.stop()

    # --------------------------------------------------------
    # 3. REALIZAR CÁLCULO
    # --------------------------------------------------------

    resultado = valor * 2  # Reemplazar por lógica real

    st.success("Cálculo realizado correctamente.")
    st.write("Resultado:", resultado)

    st.info(f"Te quedan {consumo['remaining']} usos restantes.")
