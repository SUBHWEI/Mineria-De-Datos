from repositorios.cargador import CargadorDataset
from servicios.calidad import Diagnosticador, AnalizadorOutliers, Validador
from servicios.limpieza import MarcadorFacturasNegativas, NormalizadorTexto, TratadorDuplicados
from utilidades.constantes import (
    COLUMNAS_NUMERICAS,
    COLUMNAS_TEXTO,
    COLUMNA_FLAG_FACTURA_NEGATIVA,
    ARCHIVO_CRUDO,
    ARCHIVO_LIMPIO,
)


class PipelineLimpieza:
    def __init__(self, archivoCrudo, archivoLimpio):
        self.archivoCrudo = archivoCrudo
        self.archivoLimpio = archivoLimpio
        self.cargador = CargadorDataset(archivoCrudo)
        self.diagnosticador = Diagnosticador(COLUMNAS_NUMERICAS, COLUMNA_FLAG_FACTURA_NEGATIVA)
        self.tratadorDuplicados = TratadorDuplicados()
        self.normalizadorTexto = NormalizadorTexto(COLUMNAS_TEXTO)
        self.marcadorNegativas = MarcadorFacturasNegativas(COLUMNA_FLAG_FACTURA_NEGATIVA)
        self.analizadorOutliers = AnalizadorOutliers(COLUMNAS_NUMERICAS, COLUMNA_FLAG_FACTURA_NEGATIVA)
        self.validador = Validador(COLUMNA_FLAG_FACTURA_NEGATIVA)

    def ejecutar(self):
        df = self.cargador.cargar()
        self.diagnosticador.diagnosticar(df, "Dataset crudo")
        df = self.tratadorDuplicados.quitar(df)
        df = self.normalizadorTexto.normalizar(df)
        df = self.marcadorNegativas.marcar(df)
        self.analizadorOutliers.revisarIQR(df)
        self.diagnosticador.diagnosticar(df, "Dataset limpio")
        self.validador.validar(df)
        df.to_csv(self.archivoLimpio, index=False, float_format="%.2f")
        print("Archivo guardado:", self.archivoLimpio)


if __name__ == "__main__":
    PipelineLimpieza(ARCHIVO_CRUDO, ARCHIVO_LIMPIO).ejecutar()