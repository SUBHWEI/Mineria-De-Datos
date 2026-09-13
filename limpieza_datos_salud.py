import pandas as pd
from pathlib import Path

CARPETA = Path(__file__).parent
ARCHIVO_CRUDO = CARPETA / "healthcare_dataset_original.csv"
ARCHIVO_LIMPIO = CARPETA / "healthcare_dataset_limpio.csv"
COLUMNAS_NUMERICAS = ["Age", "Billing Amount"]
COLUMNAS_TEXTO = ["Name", "Doctor", "Hospital"]


class Diagnosticador:
    def __init__(self, columnasNumericas):
        self.columnasNumericas = columnasNumericas

    def diagnosticar(self, df, etiqueta):
        print(f"=== {etiqueta} ===")
        print("Filas:", len(df))
        print("Duplicados:", df.duplicated().sum())
        print("Nulos:", df.isna().sum().sum())
        print(df[self.columnasNumericas].describe().round(2))


class TratadorDuplicados:
    def __init__(self):
        pass

    def quitar(self, df):
        antes = len(df)
        df = df.drop_duplicates().reset_index(drop=True)
        print("Duplicados eliminados:", antes - len(df))
        return df


class NormalizadorTexto:
    def __init__(self, columnasTexto):
        self.columnasTexto = columnasTexto

    def normalizar(self, df):
        for columna in self.columnasTexto:
            df[columna] = df[columna].str.strip().str.title()
        return df


class TratadorValoresImposibles:
    def __init__(self):
        pass

    def corregirFacturacion(self, df):
        negativos = df["Billing Amount"] < 0
        if negativos.sum() > 0:
            mediana = df.loc[~negativos, "Billing Amount"].median()
            df.loc[negativos, "Billing Amount"] = mediana
            print("Facturas negativas corregidas:", int(negativos.sum()))
            print("Valor de reemplazo (mediana):", round(mediana, 2))
        return df


class AnalizadorOutliers:
    def __init__(self, columnasNumericas):
        self.columnasNumericas = columnasNumericas

    def revisarIQR(self, df):
        for columna in self.columnasNumericas:
            q1, q3 = df[columna].quantile([0.25, 0.75])
            iqr = q3 - q1
            limiteInferior = q1 - 1.5 * iqr
            limiteSuperior = q3 + 1.5 * iqr
            fuera = int(((df[columna] < limiteInferior) | (df[columna] > limiteSuperior)).sum())
            print(f"{columna}: limites [{limiteInferior:.2f}, {limiteSuperior:.2f}], fuera de rango: {fuera}")


class Validador:
    def __init__(self):
        pass

    def validar(self, df):
        print("Duplicados:", df.duplicated().sum())
        print("Nulos:", df.isna().sum().sum())
        print("Facturas negativas:", int((df["Billing Amount"] < 0).sum()))
        print("Edades fuera de rango:", int((~df["Age"].between(0, 120)).sum()))


class PipelineLimpieza:
    def __init__(self, archivoCrudo, archivoLimpio):
        self.archivoCrudo = archivoCrudo
        self.archivoLimpio = archivoLimpio
        self.diagnosticador = Diagnosticador(COLUMNAS_NUMERICAS)
        self.tratadorDuplicados = TratadorDuplicados()
        self.normalizadorTexto = NormalizadorTexto(COLUMNAS_TEXTO)
        self.tratadorImposibles = TratadorValoresImposibles()
        self.analizadorOutliers = AnalizadorOutliers(COLUMNAS_NUMERICAS)
        self.validador = Validador()

    def ejecutar(self):
        df = pd.read_csv(self.archivoCrudo)
        self.diagnosticador.diagnosticar(df, "Dataset crudo")
        df = self.tratadorDuplicados.quitar(df)
        df = self.normalizadorTexto.normalizar(df)
        df = self.tratadorImposibles.corregirFacturacion(df)
        self.analizadorOutliers.revisarIQR(df)
        self.diagnosticador.diagnosticar(df, "Dataset limpio")
        self.validador.validar(df)
        df.to_csv(self.archivoLimpio, index=False)
        print("Archivo guardado:", self.archivoLimpio)


if __name__ == "__main__":
    PipelineLimpieza(ARCHIVO_CRUDO, ARCHIVO_LIMPIO).ejecutar()