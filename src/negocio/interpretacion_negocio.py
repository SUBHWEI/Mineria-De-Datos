from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent.parent
CARPETA_DATA = RAIZ / "data"
CARPETA_DOCS = RAIZ / "docs"
CARPETA_TABLA = CARPETA_DOCS / "tabla"
CARPETA_DOCS.mkdir(parents=True, exist_ok=True)
CARPETA_TABLA.mkdir(parents=True, exist_ok=True)

ARCHIVO_LIMPIO = CARPETA_DATA / "healthcare_dataset_limpio.csv"
ARCHIVO_ENRIQUECIDO = CARPETA_DATA / "healthcare_dataset_enriquecido.csv"

# Mapeo manual medicamento -> sintomas/enfermedades tratadas (validacion clinica)
SINTOMAS = {
    "Aspirin": "Dolor, fiebre, inflamacion, prevencion trombotica / cardiovascular.",
    "Ibuprofen": "Dolor, inflamacion, fiebre (antiinflamatorio no esteroideo).",
    "Lipitor": "Hipercolesterolemia, riesgo cardiovascular.",
    "Paracetamol": "Dolor y fiebre (analgesico/antipiretico).",
    "Penicillin": "Infecciones bacterianas.",
}

BANDAS_EDAD = [12, 19, 29, 39, 49, 59, 69, 89]
ETIQUETAS_EDAD = ["13-19", "20-29", "30-39", "40-49", "50-59", "60-69", "70-89"]


def tabla_medicamento_clase():
    df = pd.read_csv(ARCHIVO_ENRIQUECIDO)
    filas = []
    for med in sorted(df["Medication"].unique() if "Medication" in df.columns else []):
        pass
    # Medicamentos del dataset limpio (mas estable)
    dfh = pd.read_csv(ARCHIVO_LIMPIO)
    for med in sorted(dfh["Medication"].unique()):
        col = f"Medication_{med}_PHARM_CLASSES"
        clase = None
        if col in df.columns:
            vals = df.loc[df[f"Medication_{med}"] == 1, col].dropna().unique()
            clase = vals[0] if len(vals) else None
        # condiciones atendidas
        conds = dfh[dfh["Medication"] == med]["Medical Condition"].value_counts()
        filas.append(
            {
                "Medicamento": med,
                "Clase_terapeutica_principal": clase,
                "Sintomas_enfermedades_tratadas": SINTOMAS.get(med, "No definido"),
                "Condiciones_atendidas": int(conds.shape[0]),
                "Total_admisiones": int(len(dfh[dfh["Medication"] == med])),
                "Exclusivo_de_una_condicion": "No" if conds.shape[0] > 1 else "Si",
            }
        )
    return pd.DataFrame(filas)


def politica_stock():
    df = pd.read_csv(ARCHIVO_LIMPIO)
    df["AgeBand"] = pd.cut(df["Age"], bins=BANDAS_EDAD, labels=ETIQUETAS_EDAD, include_lowest=True)
    filas = []
    for banda in ETIQUETAS_EDAD:
        sub = df[df["AgeBand"] == banda]
        total = len(sub)
        for med in sorted(df["Medication"].unique()):
            demanda = int((sub["Medication"] == med).sum())
            pct = demanda / total if total else 0.0
            stock_base = int(round(pct * 1000))
            # stock de seguridad +20% si la demanda es menor al 20%
            seguridad = int(round(stock_base * 0.20)) if pct < 0.20 else 0
            filas.append(
                {
                    "Banda_edad": banda,
                    "Medicamento": med,
                    "Admisiones_banda": total,
                    "Demanda_observada": demanda,
                    "Porcentaje_demanda": round(pct, 4),
                    "Stock_base (unidades)": stock_base,
                    "Stock_seguridad (unidades)": seguridad,
                    "Stock_total (unidades)": stock_base + seguridad,
                }
            )
    return pd.DataFrame(filas)


def main():
    # Tabla medicamento -> clase -> sintomas
    tabla_mc = tabla_medicamento_clase()
    tabla_mc.to_csv(CARPETA_TABLA / "tabla_medicamento_clase_sintomas.csv", index=False)
    print("=== Medicamento -> clase terapeutica -> sintomas ===")
    print(tabla_mc.to_string(index=False))

    # Politica de stock
    stock = politica_stock()
    stock.to_csv(CARPETA_TABLA / "politica_stock.csv", index=False)
    print("\n=== Politica de stock por banda de edad ===")
    print(stock.to_string(index=False))

    # Limitaciones
    limitaciones = """# Limitaciones del modelo y del analisis

1. El dataset Healthcare es sintetico: las variables son independientes, por lo que los arboles
   originales quedan en baseline (sin señal predictiva real).
2. El catalogo Drugs_product es un catalogo de productos; el mapeo por texto puede asignar
   clases terapeuticas inesperadas (validar manualmente).
3. El modelo derivado usa una etiqueta simulada (reglas clinicas + ruido) y debe presentarse
   como escenario, no como prediccion clinica real.
4. Ningun medicamento es exclusivo de una sola enfermedad en los datos actuales.
5. La politica de stock se basa en demanda observada (proporcional) y stock de seguridad
   del 20% para medicamentos de baja demanda; ajustar segun capacidad real del centro.
"""
    (CARPETA_DOCS / "limitaciones.md").write_text(limitaciones, encoding="utf-8")

    print("\nArchivos generados:")
    print(" -", CARPETA_TABLA / "tabla_medicamento_clase_sintomas.csv")
    print(" -", CARPETA_TABLA / "politica_stock.csv")
    print(" -", CARPETA_DOCS / "limitaciones.md")


if __name__ == "__main__":
    main()
