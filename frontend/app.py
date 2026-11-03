import json
import os
from pathlib import Path

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://fase2-api:8000")

SCHEMA = json.loads(
    (Path(__file__).parent / "form_schema.json").read_text(
        encoding="utf-8"
    )
)

st.set_page_config(
    page_title="Fase 2 | Riesgo Crediticio",
    page_icon="📊",
    layout="wide"
)

st.title("Evaluación académica de riesgo crediticio")
st.caption("FASE 2 | Modelo Random Forest | South German Credit")

st.warning(
    "Prototipo exclusivamente académico. "
    "El modelo obtuvo un dictamen NO-GO para uso bancario real. "
    "No debe utilizarse para aprobar, rechazar ni modificar créditos."
)

with st.sidebar:
    st.header("Información técnica")
    st.write("**Modelo:** Random Forest")
    st.write("**Variables:** 20")
    st.write("**Umbral de clasificación:** 0.28")
    st.write("**Backend:** FastAPI")
    st.write("**Infraestructura:** Docker")

    try:
        respuesta = requests.get(API_URL + "/health", timeout=5)
        respuesta.raise_for_status()
        st.success("API conectada")
    except requests.RequestException:
        st.error("API no disponible")

st.subheader("Datos del solicitante")
st.caption(
    "Las variables categóricas conservan los códigos originales "
    "del conjunto de datos. Los valores iniciales son ejemplos "
    "estadísticos, no información de una persona real."
)

entrada = {}

with st.form("formulario_crediticio"):
    columnas = st.columns(2)

    for i, campo in enumerate(SCHEMA):
        nombre = campo["nombre"]

        with columnas[i % 2]:
            if campo["tipo"] == "numerica":
                valor = st.number_input(
                    nombre,
                    min_value=int(campo["minimo"]),
                    max_value=int(campo["maximo"]),
                    value=int(campo["predeterminado"]),
                    step=1
                )
            else:
                opciones = campo["opciones"]
                indice = opciones.index(campo["predeterminado"])

                valor = st.selectbox(
                    nombre,
                    options=opciones,
                    index=indice,
                    help="Categoría codificada del dataset original"
                )

            entrada[nombre] = int(valor)

    enviar = st.form_submit_button(
        "Calcular riesgo",
        use_container_width=True
    )

if enviar:
    try:
        respuesta = requests.post(
            API_URL + "/predict",
            json=entrada,
            timeout=30
        )
        respuesta.raise_for_status()
        resultado = respuesta.json()

        st.divider()
        st.subheader("Resultado de la inferencia")

        probabilidad = resultado["probabilidad_riesgo_alto"]

        st.metric(
            "Probabilidad estimada de riesgo alto",
            f"{probabilidad * 100:.2f}%"
        )

        if resultado["clasificacion"] == "RIESGO ALTO":
            st.error("Clasificación del modelo: RIESGO ALTO")
        else:
            st.info("Clasificación del modelo: RIESGO NO ALTO")

        st.caption(
            "La clasificación depende del umbral académico de 0.28. "
            "No equivale a una recomendación crediticia."
        )

        with st.expander("Respuesta JSON de FastAPI"):
            st.json(resultado)

    except requests.RequestException as error:
        st.error(f"Error de comunicación con la API: {error}")
