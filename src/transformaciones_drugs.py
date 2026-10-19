# Transformacion y codificacion del catalogo de farmacos (Drugs_product.csv)
# One-hot (nominales de baja cardinalidad): PRODUCTTYPENAME, MARKETINGCATEGORYNAME
# Ordinal (orden de control DEA): DEASCHEDULE (CV < CIV < CIII < CII)
# Ejecutar desde la raiz del proyecto: python transformaciones_drugs.py

from pathlib import Path
import sys

CARPETA_PROYECTO = Path(__file__).resolve().parent.parent
(CARPETA_PROYECTO / "data").mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(CARPETA_PROYECTO / "src"))
from utilidades.constantes import ARCHIVO_DRUGS_PRODUCT

ARCHIVO_DRUGS_CRUDO = ARCHIVO_DRUGS_PRODUCT
ARCHIVO_DRUGS_LIMPIO = CARPETA_PROYECTO / "data" / "drugs_product_limpio.csv"
ARCHIVO_DRUGS_TRANSFORMADO = CARPETA_PROYECTO / "data" / "drugs_product_transformado.csv"

import pandas as pd

NOMINALES_ONEHOT = ["PRODUCTTYPENAME", "MARKETINGCATEGORYNAME"]
MAPEO_DEA = {"CV": 1, "CIV": 2, "CIII": 3, "CII": 4}

COLUMNAS_RESTANTES = [
    "PRODUCTID", "PRODUCTNDC", "PROPRIETARYNAME", "NONPROPRIETARYNAME",
    "DOSAGEFORMNAME", "ROUTENAME", "SUBSTANCENAME", "ACTIVE_NUMERATOR_STRENGTH",
    "ACTIVE_INGRED_UNIT", "PHARM_CLASSES", "LABELERNAME", "DEASCHEDULE",
    "STARTMARKETINGDATE", "ENDMARKETINGDATE",
]


def codificar_one_hot(df):
    return pd.get_dummies(df[NOMINALES_ONEHOT], prefix=NOMINALES_ONEHOT, dtype=int)


def codificar_ordinal(df):
    return pd.DataFrame({"DEASCHEDULE_Nivel": df["DEASCHEDULE"].map(MAPEO_DEA)})


def ejecutar():
    df = pd.read_csv(ARCHIVO_DRUGS_CRUDO, encoding="latin-1")
    print("Drugs crudo:", df.shape)

    for c in ["PROPRIETARYNAME", "NONPROPRIETARYNAME", "SUBSTANCENAME",
              "PHARM_CLASSES", "DOSAGEFORMNAME", "ROUTENAME",
              "MARKETINGCATEGORYNAME", "PRODUCTTYPENAME"]:
        if c in df.columns:
            df[c] = df[c].astype("string").str.strip()

    df.to_csv(ARCHIVO_DRUGS_LIMPIO, index=False)
    print("Limpio guardado:", ARCHIVO_DRUGS_LIMPIO, df.shape)

    print("\n--- One-hot (nominales baja cardinalidad) ---")
    one_hot = codificar_one_hot(df)
    print("Columnas one-hot:", len(one_hot.columns))

    print("\n--- Ordinal (DEASCHEDULE) ---")
    ordinal = codificar_ordinal(df)
    print(ordinal["DEASCHEDULE_Nivel"].value_counts(dropna=False).to_dict())

    df_transformado = pd.concat(
        [df[COLUMNAS_RESTANTES].reset_index(drop=True),
         one_hot.reset_index(drop=True),
         ordinal.reset_index(drop=True)],
        axis=1,
    )
    print("\n--- Drugs transformado ---")
    print("Forma:", df_transformado.shape)
    df_transformado.to_csv(ARCHIVO_DRUGS_TRANSFORMADO, index=False)
    print("Guardado:", ARCHIVO_DRUGS_TRANSFORMADO)


if __name__ == "__main__":
    ejecutar()