import pandas as pd


class CargadorDataset:
    def __init__(self, archivo):
        self.archivo = archivo

    def cargar(self):
        return pd.read_csv(self.archivo)