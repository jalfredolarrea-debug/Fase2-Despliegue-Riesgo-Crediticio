import csv
import json
from collections import Counter
from pathlib import Path

metadata = json.loads(
    Path("artifacts/metadata.json").read_text(encoding="utf-8")
)

with open("data/creditos.csv", newline="", encoding="utf-8") as f:
    registros = list(csv.DictReader(f))

numericas = {"duration", "amount", "age"}
schema = []

for nombre in metadata["variables"]:
    valores = [int(float(r[nombre])) for r in registros]

    if nombre in numericas:
        ordenados = sorted(valores)
        campo = {
            "nombre": nombre,
            "tipo": "numerica",
            "minimo": min(valores),
            "maximo": max(valores),
            "predeterminado": ordenados[len(ordenados) // 2]
        }
    else:
        moda = Counter(valores).most_common(1)[0][0]
        campo = {
            "nombre": nombre,
            "tipo": "categorica",
            "opciones": sorted(set(valores)),
            "predeterminado": moda
        }

    schema.append(campo)

Path("frontend/form_schema.json").write_text(
    json.dumps(schema, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print("Formulario generado:", len(schema), "variables")
