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