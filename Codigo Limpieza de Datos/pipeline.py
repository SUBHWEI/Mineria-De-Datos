import pandas as pd

from cargador import CargadorDataset
from diagnosticador import Diagnosticador
from duplicados import TratadorDuplicados
from texto import NormalizadorTexto
from imposibles import TratadorValoresImposibles
from outliers import AnalizadorOutliers
from validador import Validador
from constantes import COLUMNAS_NUMERICAS, COLUMNAS_TEXTO


class PipelineLimpieza:
    def __init__(self, archivoCrudo, archivoLimpio):
        self.archivoCrudo = archivoCrudo
        self.archivoLimpio = archivoLimpio
        self.cargador = CargadorDataset(archivoCrudo)
        self.diagnosticador = Diagnosticador(COLUMNAS_NUMERICAS)
        self.tratadorDuplicados = TratadorDuplicados()
        self.normalizadorTexto = NormalizadorTexto(COLUMNAS_TEXTO)
        self.tratadorImposibles = TratadorValoresImposibles()
        self.analizadorOutliers = AnalizadorOutliers(COLUMNAS_NUMERICAS)
        self.validador = Validador()

    def ejecutar(self):
        df = self.cargador.cargar()
        self.diagnosticador.diagnosticar(df, "Dataset crudo")
        df = self.tratadorDuplicados.quitar(df)
        df = self.normalizadorTexto.normalizar(df)
        df = self.tratadorImposibles.corregirFacturacion(df)
        self.analizadorOutliers.revisarIQR(df)
        self.diagnosticador.diagnosticar(df, "Dataset limpio")
        self.validador.validar(df)
        df.to_csv(self.archivoLimpio, index=False)
        print("Archivo guardado:", self.archivoLimpio)