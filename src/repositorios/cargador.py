import pandas as pd


class CargadorDataset:
    def __init__(self, archivo, encoding=None):
        self.archivo = archivo
        self.encoding = encoding

    def cargar(self):
        if self.encoding:
            return pd.read_csv(self.archivo, encoding=self.encoding)
        return pd.read_csv(self.archivo)