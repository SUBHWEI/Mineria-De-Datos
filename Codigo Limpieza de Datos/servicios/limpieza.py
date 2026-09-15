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


class MarcadorFacturasNegativas:
    def __init__(self, columnaFlag):
        self.columnaFlag = columnaFlag

    def marcar(self, df):
        negativos = df["Billing Amount"] < 0
        df[self.columnaFlag] = negativos
        print("Facturas negativas marcadas:", int(negativos.sum()))
        print("El monto original se conserva, no se imputa ningún valor.")
        return df