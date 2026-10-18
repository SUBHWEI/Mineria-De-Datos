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


class NormalizadorDrugs:
    """Normaliza columnas de texto del catálogo de fármacos para facilitar el mapeo."""

    COLUMNAS_TEXTO = [
        "PROPRIETARYNAME",
        "NONPROPRIETARYNAME",
        "SUBSTANCENAME",
        "PHARM_CLASSES",
        "DOSAGEFORMNAME",
        "ROUTENAME",
        "MARKETINGCATEGORYNAME",
        "PRODUCTTYPENAME",
    ]

    def normalizar(self, df):
        for columna in self.COLUMNAS_TEXTO:
            if columna in df.columns:
                df[columna] = df[columna].astype("string").str.strip()
        return df