import json
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    create_model,
    model_validator,
)

BASE = Path(__file__).resolve().parents[1]

METADATA = json.loads(
    (BASE / "artifacts/metadata.json").read_text(encoding="utf-8")
)
CAMPOS = json.loads(
    (BASE / "frontend/form_schema.json").read_text(encoding="utf-8")
)
MODELO = joblib.load(BASE / "artifacts/modelo_riesgo.joblib")

VARIABLES = METADATA["variables"]
UMBRAL = METADATA["umbral"]

if [c["nombre"] for c in CAMPOS] != VARIABLES:
    raise RuntimeError("Inconsistencia entre el modelo y los dominios")


class EntradaBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def verificar_dominios(self):
        for campo in CAMPOS:
            nombre = campo["nombre"]
            valor = getattr(self, nombre)

            if campo["tipo"] == "categorica":
                if valor not in campo["opciones"]:
                    raise ValueError(
                        f"{nombre}: categoria no permitida"
                    )
            else:
                if not campo["minimo"] <= valor <= campo["maximo"]:
                    raise ValueError(
                        f"{nombre}: fuera del rango documentado"
                    )
        return self


EntradaCredito = create_model(
    "EntradaCredito",
    __base__=EntradaBase,
    **{
        variable: (int, Field(..., strict=True, ge=0))
        for variable in VARIABLES
    },
)

app = FastAPI(
    title="Fase 2 | API de Riesgo Crediticio",
    description="Prototipo academico. NO-GO para uso bancario real.",
    version="1.1.0",
)


@app.get("/health")
def health():
    return {
        "estado": "operativo",
        "modelo": METADATA["modelo"],
        "variables": len(VARIABLES),
        "uso": "academico",
    }


@app.get("/schema")
def schema():
    return {
        "variables": VARIABLES,
        "umbral": UMBRAL,
        "advertencia": METADATA["dictamen"],
    }


@app.post("/predict")
def predict(entrada: EntradaCredito):
    datos = pd.DataFrame(
        [entrada.model_dump()],
        columns=VARIABLES,
    )

    probabilidad = float(MODELO.predict_proba(datos)[0, 1])
    riesgo_alto = probabilidad >= UMBRAL

    return {
        "probabilidad_riesgo_alto": round(probabilidad, 6),
        "umbral": UMBRAL,
        "clasificacion": (
            "RIESGO ALTO" if riesgo_alto else "RIESGO NO ALTO"
        ),
        "uso": "Demostracion academica",
        "dictamen": METADATA["dictamen"],
    }
