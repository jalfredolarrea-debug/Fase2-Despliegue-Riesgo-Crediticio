import csv
import json
import urllib.request
from urllib.error import HTTPError
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
URL = "http://127.0.0.1:8765"


def consultar(ruta, datos=None):
    contenido = None
    headers = {}

    if datos is not None:
        contenido = json.dumps(datos).encode("utf-8")
        headers["Content-Type"] = "application/json"

    solicitud = urllib.request.Request(
        URL + ruta,
        data=contenido,
        headers=headers,
        method="POST" if datos is not None else "GET"
    )

    try:
        with urllib.request.urlopen(solicitud, timeout=15) as r:
            return r.status, json.load(r)
    except HTTPError as e:
        return e.code, json.load(e)


def leer_csv(ruta):
    with open(BASE / ruta, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


metadata = json.loads(
    (BASE / "artifacts/metadata.json").read_text(encoding="utf-8")
)
variables = metadata["variables"]
datos = leer_csv("data/creditos.csv")
referencias = leer_csv("evidence/predicciones.csv")

def entrada(indice):
    return {
        v: int(float(datos[indice][v]))
        for v in variables
    }


print("=== ETAPA 3.1 | PRUEBAS AUTOMATIZADAS ===")

codigo, salud = consultar("/health")
assert codigo == 200 and salud["estado"] == "operativo"
print("PASS | Disponibilidad de la API")

codigo, esquema = consultar("/schema")
assert codigo == 200 and esquema["variables"] == variables
print("PASS | Esquema de 20 variables")

assert len(referencias) == 200

for referencia in referencias:
    indice = int(referencia["indice_original"])
    codigo, respuesta = consultar("/predict", entrada(indice))

    assert codigo == 200, f"HTTP incorrecto: {indice}"

    probabilidad = float(
        referencia["probabilidad_forest"]
    )
    observada = respuesta["probabilidad_riesgo_alto"]

    assert abs(observada - probabilidad) <= 0.0000006, (
        f"Probabilidad diferente: {indice}"
    )

    prediccion = int(
        respuesta["clasificacion"] == "RIESGO ALTO"
    )
    esperada = int(
        referencia["prediccion_forest"]
    )

    assert prediccion == esperada, (
        f"Clasificacion diferente: {indice}"
    )

print("PASS | 200 predicciones historicas reproducidas")

caso = entrada(0)

pruebas_invalidas = {
    "Variable faltante": {
        k: v for k, v in caso.items() if k != "age"
    },
    "Variable adicional": {
        **caso, "variable_inexistente": 1
    },
    "Valor negativo": {
        **caso, "amount": -1
    },
    "Tipo de dato incorrecto": {
        **caso, "amount": "texto_invalido"
    },
}

for nombre, datos_invalidos in pruebas_invalidas.items():
    codigo, _ = consultar("/predict", datos_invalidos)
    assert codigo == 422, (
        f"{nombre}: se esperaba HTTP 422 y se obtuvo {codigo}"
    )
    print(f"PASS | {nombre}: HTTP 422")

codigo, _ = consultar(
    "/predict", {**caso, "status": 99999}
)

assert codigo == 422, (
    f"Categoria fuera de dominio: HTTP {codigo}, esperado 422"
)
print("PASS | Categoria fuera de dominio rechazada")

print("=== PRUEBAS PRELIMINARES FINALIZADAS ===")
