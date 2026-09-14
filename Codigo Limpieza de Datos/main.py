"""
Punto de entrada unico de la limpieza del Healthcare Dataset.

Fusion del antiguo pipeline.py + main.py en un solo modulo que orquesta
los servicios por capas:
- repositorios/cargador.py  -> acceso a datos (lectura del CSV crudo)
- servicios/*.py            -> logica de negocio, un servicio por tarea
                              (diagnostico, duplicados, texto, valores
                              imposibles, outliers, validacion)
- utilidades/constantes.py  -> rutas y nombres de columnas

Convencion de nombres:
- Clases: UpperCamelCase.
- Metodos y variables: lowerCamelCase.
- Constantes: MAYUSCULAS.

Ejecutar desde la raiz del proyecto (para que los CSV queden junto a esta):
    python "Codigo Limpieza de Datos/main.py"
"""

from repositorios.cargador import CargadorDataset
from servicios.diagnosticador import Diagnosticador
from servicios.duplicados import TratadorDuplicados
from servicios.texto import NormalizadorTexto
from servicios.imposibles import TratadorValoresImposibles
from servicios.outliers import AnalizadorOutliers
from servicios.validador import Validador
from utilidades.constantes import COLUMNAS_NUMERICAS, COLUMNAS_TEXTO, ARCHIVO_CRUDO, ARCHIVO_LIMPIO


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


if __name__ == "__main__":
    PipelineLimpieza(ARCHIVO_CRUDO, ARCHIVO_LIMPIO).ejecutar()