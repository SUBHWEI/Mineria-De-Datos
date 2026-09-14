class Validador:
    def __init__(self):
        pass

    def validar(self, df):
        print("Duplicados:", df.duplicated().sum())
        print("Nulos:", df.isna().sum().sum())
        print("Facturas negativas:", int((df["Billing Amount"] < 0).sum()))
        print("Edades fuera de rango:", int((~df["Age"].between(0, 120)).sum()))