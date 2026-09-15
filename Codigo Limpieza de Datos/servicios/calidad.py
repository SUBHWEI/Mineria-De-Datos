class Diagnosticador:
    def __init__(self, columnasNumericas, columnaFlag=None):
        self.columnasNumericas = columnasNumericas
        self.columnaFlag = columnaFlag

    def diagnosticar(self, df, etiqueta):
        print(f"=== {etiqueta} ===")
        print("Filas:", len(df))
        print("Duplicados:", df.duplicated().sum())
        print("Nulos:", df.isna().sum().sum())
        if self.columnaFlag is not None and self.columnaFlag in df.columns:
            print("Facturas negativas marcadas:", int(df[self.columnaFlag].sum()))
            df = df.loc[~df[self.columnaFlag]]
        print(df[self.columnasNumericas].describe().round(2))


class AnalizadorOutliers:
    def __init__(self, columnasNumericas, columnaFlag=None):
        self.columnasNumericas = columnasNumericas
        self.columnaFlag = columnaFlag

    def revisarIQR(self, df):
        base = df
        if self.columnaFlag is not None and self.columnaFlag in df.columns:
            base = df.loc[~df[self.columnaFlag]]
        for columna in self.columnasNumericas:
            q1, q3 = base[columna].quantile([0.25, 0.75])
            iqr = q3 - q1
            limiteInferior = q1 - 1.5 * iqr
            limiteSuperior = q3 + 1.5 * iqr
            fuera = int(((base[columna] < limiteInferior) | (base[columna] > limiteSuperior)).sum())
            print(f"{columna}: limites [{limiteInferior:.2f}, {limiteSuperior:.2f}], fuera de rango: {fuera}")


class Validador:
    def __init__(self, columnaFlag=None):
        self.columnaFlag = columnaFlag

    def validar(self, df):
        print("Duplicados:", df.duplicated().sum())
        print("Nulos:", df.isna().sum().sum())
        negativos = int((df["Billing Amount"] < 0).sum())
        print("Facturas negativas:", negativos)
        if self.columnaFlag is not None and self.columnaFlag in df.columns:
            marcadas = int(df[self.columnaFlag].sum())
            print("Todas marcadas:", marcadas == negativos)
            print("Monto original conservado:", int((df.loc[df[self.columnaFlag], "Billing Amount"] < 0).sum()) == negativos)
        print("Edades fuera de rango:", int((~df["Age"].between(0, 120)).sum()))