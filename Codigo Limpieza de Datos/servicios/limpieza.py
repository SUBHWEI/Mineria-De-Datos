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