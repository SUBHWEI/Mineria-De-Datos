# Analisis descriptivo cruzado: edad x enfermedad x medicamento
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

RAIZ = Path(__file__).resolve().parent.parent.parent
CARPETA_DATA = RAIZ / "data"
CARPETA_DOCS = RAIZ / "docs"
CARPETA_TABLA = CARPETA_DOCS / "tabla"
CARPETA_FIGURAS = CARPETA_DOCS / "figuras"
for c in (CARPETA_DOCS, CARPETA_TABLA, CARPETA_FIGURAS):
    c.mkdir(parents=True, exist_ok=True)

ARCHIVO_LIMPIO = CARPETA_DATA / "healthcare_dataset_limpio.csv"

BANDAS_EDAD = [12, 19, 29, 39, 49, 59, 69, 89]
ETIQUETAS_EDAD = ["13-19", "20-29", "30-39", "40-49", "50-59", "60-69", "70-89"]


def cargar_datos():
    df = pd.read_csv(ARCHIVO_LIMPIO)
    df["AgeBand"] = pd.cut(df["Age"], bins=BANDAS_EDAD, labels=ETIQUETAS_EDAD, include_lowest=True)
    return df


def tabla_edad_enfermedad(df):
    conteos = pd.crosstab(df["AgeBand"], df["Medical Condition"])
    probabilidades = conteos.div(conteos.sum(axis=1), axis=0).round(4)
    return conteos, probabilidades


def tabla_enfermedad_medicamento(df):
    conteos = pd.crosstab(df["Medical Condition"], df["Medication"])
    probabilidades = conteos.div(conteos.sum(axis=1), axis=0).round(4)
    return conteos, probabilidades


def tabla_exclusividad(df):
    filas = []
    for medicamento in sorted(df["Medication"].unique()):
        sub = df[df["Medication"] == medicamento]
        condiciones = sub["Medical Condition"].value_counts()
        filas.append(
            {
                "Medicamento": medicamento,
                "Condiciones_atendidas": int(condiciones.shape[0]),
                "Total_admisiones": int(len(sub)),
                "Condiciones": ", ".join(sorted(condiciones.index.tolist())),
                "Exclusivo": "Si" if condiciones.shape[0] == 1 else "No",
            }
        )
    return pd.DataFrame(filas)


def ejemplo_diabetes(df):
    sub = df[(df["Age"] >= 35) & (df["Age"] <= 39)]
    n = len(sub)
    n_diabetes = int((sub["Medical Condition"] == "Diabetes").sum())
    prob = n_diabetes / n if n else 0.0
    med_principal = None
    if n_diabetes > 0:
        med_principal = sub[sub["Medical Condition"] == "Diabetes"]["Medication"].value_counts().idxmax()
    return {
        "Rango_edad": "35-39",
        "Admisiones": n,
        "Casos_diabetes": n_diabetes,
        "Probabilidad_diabetes": round(prob, 4),
        "Medicamento_principal_diabetes": med_principal,
    }


def guardar_heatmap(matriz, titulo, ruta, xlabel, ylabel, fmt="{:.2f}"):
    fig, ax = plt.subplots(figsize=(9, 6))
    im = ax.imshow(matriz.values, cmap="YlOrRd", aspect="auto")
    ax.set_xticks(range(len(matriz.columns)))
    ax.set_yticks(range(len(matriz.index)))
    ax.set_xticklabels(matriz.columns, rotation=45, ha="right")
    ax.set_yticklabels(matriz.index)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(titulo)
    for i in range(matriz.shape[0]):
        for j in range(matriz.shape[1]):
            ax.text(j, i, fmt.format(matriz.iloc[i, j]), ha="center", va="center", fontsize=8)
    fig.colorbar(im, ax=ax, shrink=0.8)
    fig.tight_layout()
    fig.savefig(ruta, dpi=150, bbox_inches="tight")
    plt.close(fig)


def main():
    df = cargar_datos()
    print("Dataset limpio:", df.shape)

    # Tabla edad x enfermedad
    conteos_ee, prob_ee = tabla_edad_enfermedad(df)
    conteos_ee.to_csv(CARPETA_TABLA / "tabla_edad_enfermedad_conteos.csv")
    prob_ee.to_csv(CARPETA_TABLA / "tabla_edad_enfermedad.csv")
    print("\n=== Probabilidad de enfermedad por banda de edad ===")
    print(prob_ee.to_string())
    guardar_heatmap(
        prob_ee,
        "Probabilidad de enfermedad por banda de edad",
        CARPETA_FIGURAS / "heatmap_edad_enfermedad.png",
        "Enfermedad",
        "Banda de edad",
    )

    # Tabla enfermedad x medicamento
    conteos_em, prob_em = tabla_enfermedad_medicamento(df)
    conteos_em.to_csv(CARPETA_TABLA / "tabla_enfermedad_medicamento_conteos.csv")
    prob_em.to_csv(CARPETA_TABLA / "tabla_enfermedad_medicamento.csv")
    print("\n=== Probabilidad de medicamento por enfermedad ===")
    print(prob_em.to_string())
    guardar_heatmap(
        prob_em,
        "Probabilidad de medicamento por enfermedad",
        CARPETA_FIGURAS / "heatmap_enfermedad_medicamento.png",
        "Medicamento",
        "Enfermedad",
    )

    # Exclusividad
    exclusividad = tabla_exclusividad(df)
    exclusividad.to_csv(CARPETA_TABLA / "tabla_exclusividad_medicamentos.csv", index=False)
    print("\n=== Exclusividad de medicamentos ===")
    print(exclusividad.to_string(index=False))

    # Ejemplo diabetes 35-39
    ejemplo = ejemplo_diabetes(df)
    print("\n=== Ejemplo: diabetes en 35-39 años ===")
    for k, v in ejemplo.items():
        print(f"{k}: {v}")

    print("\nArchivos generados en docs/:")
    print(" - tabla_edad_enfermedad.csv (y conteos)")
    print(" - tabla_enfermedad_medicamento.csv (y conteos)")
    print(" - tabla_exclusividad_medicamentos.csv")
    print(" - heatmap_edad_enfermedad.png")
    print(" - heatmap_enfermedad_medicamento.png")


if __name__ == "__main__":
    main()
