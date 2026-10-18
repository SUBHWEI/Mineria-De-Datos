import pandas as pd

from repositorios.cargador import CargadorDataset
from servicios.limpieza import NormalizadorDrugs
from servicios.cruce import EnriquecedorHealthcareDrugs
from utilidades.constantes import (
    ARCHIVO_TRANSFORMADO,
    ARCHIVO_ENRIQUECIDO,
    ARCHIVO_ANALISIS,
    ARCHIVO_DRUGS_PRODUCT,
    MEDICAMENTOS_MAPEO,
)


class PipelineCruce:
    def __init__(self):
        self.cargadorHealthcare = CargadorDataset(ARCHIVO_TRANSFORMADO)
        self.cargadorDrugs = CargadorDataset(ARCHIVO_DRUGS_PRODUCT, encoding="latin-1")
        self.normalizadorDrugs = NormalizadorDrugs()
        self.enriquecedor = None

    def ejecutar(self):
        print("=== Cargando healthcare transformado ===")
        dfHealthcare = self.cargadorHealthcare.cargar()
        print("Filas:", len(dfHealthcare), "Columnas:", len(dfHealthcare.columns))

        print("\n=== Cargando Drugs_product.csv ===")
        dfDrugs = self.cargadorDrugs.cargar()
        print("Filas:", len(dfDrugs), "Columnas:", len(dfDrugs.columns))

        print("\n=== Normalizando Drugs ===")
        dfDrugs = self.normalizadorDrugs.normalizar(dfDrugs)

        print("\n=== Enriqueciendo healthcare con Drugs ===")
        self.enriquecedor = EnriquecedorHealthcareDrugs(dfDrugs)
        print(self.enriquecedor.resumen_cobertura().to_string(index=False))

        dfEnriquecido, perfiles = self.enriquecedor.enriquecer(dfHealthcare)
        print("\nForma enriquecida:", dfEnriquecido.shape)
        print("Columnas nuevas:", [c for c in dfEnriquecido.columns if c not in dfHealthcare.columns])

        print("\n=== Diagnostico del dataset cruzado ===")
        print("Duplicados:", dfEnriquecido.duplicated().sum())
        print("Nulos totales:", int(dfEnriquecido.isna().sum().sum()))
        nulos = dfEnriquecido.isna().sum()
        print("Columnas con nulos:\n", nulos[nulos > 0].to_string())
        print("\nDescribe numericas:")
        print(dfEnriquecido[["Age", "Billing Amount", "Num_Medicamentos"]].describe().round(2).to_string())

        print("\nClasificacion de faltantes: los NaN en columnas enriquecidas son MNAR")
        print("(informacion no disponible en el catalogo, no error de captura). No se imputan.")

        print("\n=== Outliers (IQR) del cruzado ===")
        from servicios.calidad import AnalizadorOutliers
        AnalizadorOutliers(["Age", "Billing Amount"]).revisarIQR(dfEnriquecido)

        dfEnriquecido.to_csv(ARCHIVO_ENRIQUECIDO, index=False)
        print("Archivo guardado:", ARCHIVO_ENRIQUECIDO)

        print("\n=== Analisis edad x medicamento ===")
        flags = [f"Medication_{m}" for m in MEDICAMENTOS_MAPEO if f"Medication_{m}" in dfEnriquecido.columns]
        filas = []
        for segmento in sorted(dfEnriquecido["Age Segmento"].unique()):
            sub = dfEnriquecido[dfEnriquecido["Age Segmento"] == segmento]
            fila = {"Age Segmento": int(segmento), "Admisiones": len(sub)}
            for f in flags:
                fila[f] = int((sub[f] == 1).sum())
            filas.append(fila)
        dfAnalisis = pd.DataFrame(filas)
        dfAnalisis.to_csv(ARCHIVO_ANALISIS, index=False)
        print(dfAnalisis.to_string(index=False))
        print("Archivo guardado:", ARCHIVO_ANALISIS)

        # resumen de enfermedades por medicamento activo
        print("\n=== Medicamento vs Medical Condition Nivel (conteos) ===")
        for m in MEDICAMENTOS_MAPEO:
            col = f"Medication_{m}"
            if col in dfEnriquecido.columns:
                tab = dfEnriquecido[dfEnriquecido[col] == 1]["Medical Condition Nivel"].value_counts()
                print(f"\n{m}:")
                print(tab.to_string())


if __name__ == "__main__":
    PipelineCruce().ejecutar()
