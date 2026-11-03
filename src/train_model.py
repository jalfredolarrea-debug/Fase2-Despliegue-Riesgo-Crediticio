import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import confusion_matrix, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

SALIDA = Path("artifacts")
SALIDA.mkdir(exist_ok=True)

df = pd.read_csv("data/creditos.csv")
referencia = pd.read_csv("evidence/predicciones.csv")
particiones = pd.read_csv("evidence/particiones.csv")

assert df.shape == (1000, 21)
assert df.isna().sum().sum() == 0
assert df.duplicated().sum() == 0
assert df["credit_risk"].value_counts().sort_index().to_dict() == {0: 300, 1: 700}

X = df.drop(columns=["credit_risk"])
y = (1 - df["credit_risk"]).astype(int)

indices_train, indices_test = train_test_split(
    X.index.to_numpy(),
    test_size=0.20,
    stratify=y.to_numpy(),
    random_state=42
)

assert len(indices_train) == 800
assert len(indices_test) == 200
assert set(indices_train).isdisjoint(set(indices_test))

indices_ref = referencia["indice_original"].to_numpy()
assert np.array_equal(indices_test, indices_ref), "Orden de prueba distinto al historico"

indices_particion = set(
    particiones.loc[
        particiones["particion"] == "prueba", "indice_original"
    ]
)
assert set(indices_test) == indices_particion, "Particiones no coinciden"

X_train = X.loc[indices_train]
y_train = y.loc[indices_train]
X_test = X.loc[indices_test]
y_test = y.loc[indices_test]

assert np.array_equal(
    y_test.to_numpy(),
    referencia["riesgo_alto_real"].to_numpy()
), "Etiquetas de prueba no coinciden"

numericas = ["duration", "amount", "age"]
categoricas = [c for c in X.columns if c not in numericas]

preprocesamiento = ColumnTransformer(
    [
        ("numericas", Pipeline([
            ("imputacion", SimpleImputer(strategy="median")),
            ("escalado", StandardScaler())
        ]), numericas),
        ("categoricas", Pipeline([
            ("imputacion", SimpleImputer(strategy="most_frequent")),
            ("codificacion", OneHotEncoder(handle_unknown="ignore"))
        ]), categoricas)
    ],
    remainder="drop",
    sparse_threshold=0.0
)

modelo = Pipeline([
    ("preprocesamiento", preprocesamiento),
    ("clasificador", RandomForestClassifier(
        n_estimators=160,
        min_samples_leaf=3,
        random_state=42,
        n_jobs=1
    ))
])

modelo.fit(X_train, y_train)

probabilidades = modelo.predict_proba(X_test)[:, 1]
predicciones = (probabilidades >= 0.28).astype(int)

diferencia = float(np.max(np.abs(
    probabilidades - referencia["probabilidad_forest"].to_numpy()
)))

tn, fp, fn, tp = confusion_matrix(
    y_test, predicciones, labels=[0, 1]
).ravel()

auc = float(roc_auc_score(y_test, probabilidades))

print("=== VALIDACION FASE 2 ===")
print("scikit-learn:", sklearn.__version__)
print("Datos:", df.shape)
print("Entrenamiento:", len(X_train))
print("Prueba:", len(X_test))
print("Diferencia maxima contra referencia:", diferencia)
print("TN:", tn, "FP:", fp, "FN:", fn, "TP:", tp)
print("ROC-AUC:", round(auc, 4))

assert diferencia < 1e-8, "Las probabilidades no reproducen la referencia"
assert (tn, fp, fn, tp) == (79, 61, 13, 47), "Matriz de confusion distinta"
assert np.array_equal(
    predicciones,
    referencia["prediccion_forest"].to_numpy()
), "Clasificaciones diferentes"

ruta = SALIDA / "modelo_riesgo.joblib"
joblib.dump(modelo, ruta)

metadata = {
    "modelo": "Random Forest",
    "version": "fase2-academica-1",
    "umbral": 0.28,
    "variables": X.columns.tolist(),
    "registros_entrenamiento": len(X_train),
    "registros_prueba": len(X_test),
    "scikit_learn": sklearn.__version__,
    "matriz_confusion": {
        "TN": int(tn), "FP": int(fp),
        "FN": int(fn), "TP": int(tp)
    },
    "roc_auc": auc,
    "dictamen": "NO-GO para uso bancario real",
    "uso": "Demostracion academica exclusivamente"
}

(SALIDA / "metadata.json").write_text(
    json.dumps(metadata, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print("MODELO RECONSTRUIDO Y VERIFICADO")
print("Guardado en:", ruta)
