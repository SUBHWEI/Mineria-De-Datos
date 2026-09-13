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