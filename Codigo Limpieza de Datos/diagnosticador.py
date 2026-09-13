class Diagnosticador:
    def __init__(self, columnasNumericas):
        self.columnasNumericas = columnasNumericas

    def diagnosticar(self, df, etiqueta):
        print(f"=== {etiqueta} ===")
        print("Filas:", len(df))
        print("Duplicados:", df.duplicated().sum())
        print("Nulos:", df.isna().sum().sum())
        print(df[self.columnasNumericas].describe().round(2))