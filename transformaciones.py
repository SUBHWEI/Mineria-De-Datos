# Transformacion y codificacion de variables categoricas
# Dataset: healthcare_dataset_limpio.csv
# One-hot (nominales): Gender, Blood Type, Insurance Provider, Medication, Test Results
# Ordinal (orden definido por prioridad de triaje): Medical Condition, Admission Type
# Edad: KBinsDiscretizer (segmentos) -> RobustScaler sobre los datos discretizados
# Factura_Negativa: convertida a binario 0/1
# Ejecutar desde esta carpeta:  python transformaciones.py

from pathlib import Path

import pandas as pd
from sklearn.preprocessing import KBinsDiscretizer, RobustScaler

CARPETA_PROYECTO = Path(__file__).resolve().parent
ARCHIVO_LIMPIO = CARPETA_PROYECTO / "healthcare_dataset_limpio.csv"
ARCHIVO_TRANSFORMADO = CARPETA_PROYECTO / "healthcare_dataset_transformado.csv"

# Columnas nominales -> codificacion one-hot (binaria 0/1)
CATEGORICAS_NOMINALES = [
    "Gender",
    "Blood Type",
    "Insurance Provider",
    "Medication",
    "Test Results",
]

# Columnas ordinales -> prioridad de triaje (1 la mas prioritaria)
MAPEO_MEDICAL_CONDITION = {
    "Asthma": 1,
    "Cancer": 2,
    "Diabetes": 3,
    "Hypertension": 4,
    "Arthritis": 5,
    "Obesity": 6,
}

MAPEO_ADMISSION_TYPE = {
    "Emergency": 1,
    "Urgent": 2,
    "Elective": 3,
}

# Columnas que no se codifican ni escalan y se conservan tal cual
COLUMNAS_RESTANTES = [
    "Name",
    "Age",
    "Date of Admission",
    "Doctor",
    "Hospital",
    "Billing Amount",
    "Room Number",
    "Discharge Date",
    "Factura_Negativa",
]

NUMERO_SEGMENTOS_EDAD = 4


def codificar_one_hot(df):
    return pd.get_dummies(df[CATEGORICAS_NOMINALES], prefix=CATEGORICAS_NOMINALES, dtype=int)


def codificar_ordinal(df):
    return pd.DataFrame(
        {
            "Medical Condition Nivel": df["Medical Condition"].map(MAPEO_MEDICAL_CONDITION),
            "Admission Type Nivel": df["Admission Type"].map(MAPEO_ADMISSION_TYPE),
        }
    )


def discretizar_edad(df):
    discretizador = KBinsDiscretizer(
        n_bins=NUMERO_SEGMENTOS_EDAD, encode="ordinal", strategy="quantile"
    )
    segmentos = discretizador.fit_transform(df[["Age"]]).astype(int)
    return pd.DataFrame({"Age Segmento": segmentos.ravel()}), discretizador


def escalar_edad_robust(segmentos):
    return pd.DataFrame(
        RobustScaler().fit_transform(segmentos[["Age Segmento"]]),
        columns=["Age Robusto"],
    )


def convertir_factura_binaria(df):
    df["Factura_Negativa"] = df["Factura_Negativa"].astype(int)


def ejecutar():
    df = pd.read_csv(ARCHIVO_LIMPIO)
    print("Dataset limpio:", df.shape)

    convertir_factura_binaria(df)

    print("\n--- Factura_Negativa binaria ---")
    print(df["Factura_Negativa"].value_counts().to_dict())

    print("\n--- Codificacion one-hot (nominales) ---")
    one_hot = codificar_one_hot(df)
    print("Columnas one-hot:", len(one_hot.columns), "->", one_hot.columns.tolist())

    print("\n--- Codificacion ordinal (triage) ---")
    ordinal = codificar_ordinal(df)
    print("Valores unicos de Medical Condition ->",
          df["Medical Condition"].map(MAPEO_MEDICAL_CONDITION).value_counts().sort_index().to_dict())
    print("Valores unicos de Admission Type  ->",
          df["Admission Type"].map(MAPEO_ADMISSION_TYPE).value_counts().sort_index().to_dict())

    print("\n--- Edad: segmentos con KBinsDiscretizer ---")
    edad_segmento, discretizador = discretizar_edad(df)
    print("Bordes de los segmentos:", discretizador.bin_edges_[0].round(1))
    print(edad_segmento.value_counts().sort_index().to_string())

    print("\n--- Edad: RobustScaler sobre los datos discretizados ---")
    edad_robust = escalar_edad_robust(edad_segmento)
    print("Mediana tras escalar :", edad_robust.median().round(4).tolist())
    print("IQR tras escalar     :", edad_robust.quantile(0.75).sub(edad_robust.quantile(0.25)).round(4).tolist())

    df_transformado = pd.concat(
        [
            df[COLUMNAS_RESTANTES].reset_index(drop=True),
            one_hot.reset_index(drop=True),
            ordinal.reset_index(drop=True),
            edad_segmento.reset_index(drop=True),
            edad_robust.reset_index(drop=True),
        ],
        axis=1,
    )
    print("\n--- Dataset transformado ---")
    print("Forma:", df_transformado.shape)
    print("Columnas:", df_transformado.columns.tolist())
    print(df_transformado.head(3).to_string())

    df_transformado.to_csv(ARCHIVO_TRANSFORMADO, index=False)
    print("Archivo guardado:", ARCHIVO_TRANSFORMADO)


if __name__ == "__main__":
    ejecutar()