class Diagnosticador:
    def __init__(self, columnasNumericas):
        self.columnasNumericas = columnasNumericas

    def diagnosticar(self, df, etiqueta):
        print(f"=== {etiqueta} ===")
        print("Filas:", len(df))
        print("Duplicados:", df.duplicated().sum())
        print("Nulos:", df.isna().sum().sum())
        print(df[self.columnasNumericas].describe().round(2))


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