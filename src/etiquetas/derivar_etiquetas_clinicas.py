# Derivacion de etiquetas clinicas simuladas (Fase C del plan de predicciones cruzadas)

from pathlib import Path
import random
import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent.parent
CARPETA_DATA = RAIZ / "data"
CARPETA_DATA.mkdir(parents=True, exist_ok=True)

ARCHIVO_LIMPIO = CARPETA_DATA / "healthcare_dataset_limpio.csv"
ARCHIVO_CRUZADO = CARPETA_DATA / "healthcare_dataset_cruzado.csv"
SEMILLA = 42
random.seed(SEMILLA)
np.random.seed(SEMILLA)


def enfermedad_sugerida(edad):
    if edad <= 19:
        base = "Asthma"
    elif edad <= 39:
        base = "Diabetes"
    elif edad <= 59:
        base = "Hypertension"
    elif edad <= 79:
        base = "Arthritis"
    else:
        base = "Obesity"
    if random.random() < 0.15:
        base = random.choice(["Asthma", "Diabetes", "Hypertension", "Arthritis", "Obesity", "Cancer"])
    return base


def medicamento_sugerido(fila):
    cond = fila["Enfermedad_Sugerida"]
    test = fila["Test Results"]
    edad = fila["Age"]
    if cond == "Arthritis":
        med = "Ibuprofen"
    elif cond in ("Diabetes", "Hypertension", "Obesity"):
        med = "Lipitor"
    elif cond in ("Cancer", "Asthma"):
        med = "Paracetamol"
    else:
        med = "Aspirin"
    if test == "Abnormal" and random.random() < 0.70:
        med = "Penicillin"
    if edad >= 70 and med == "Paracetamol":
        med = "Aspirin"
    if random.random() < 0.15:
        med = random.choice(["Aspirin", "Ibuprofen", "Lipitor", "Paracetamol", "Penicillin"])
    return med


def main():
    df = pd.read_csv(ARCHIVO_LIMPIO)
    df["Enfermedad_Sugerida"] = df["Age"].apply(enfermedad_sugerida)
    df["Medicamento_Sugerido"] = df.apply(medicamento_sugerido, axis=1)

    df.to_csv(ARCHIVO_CRUZADO, index=False)
    print("Dataset cruzado derivado:", df.shape)
    print("\nDistribucion Enfermedad_Sugerida:")
    print(df["Enfermedad_Sugerida"].value_counts().to_string())
    print("\nDistribucion Medicamento_Sugerido:")
    print(df["Medicamento_Sugerido"].value_counts().to_string())
    print("\nArchivo guardado:", ARCHIVO_CRUZADO)


if __name__ == "__main__":
    main()
