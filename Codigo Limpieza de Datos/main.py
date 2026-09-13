"""
Punto de entrada de la limpieza del Healthcare Dataset.

Convencion de nombres en todo el codigo:
- Clases: UpperCamelCase.
- Metodos y variables: lowerCamelCase.
- Constantes: MAYUSCULAS.

Ejecutar desde cualquier carpeta con:
    python "Codigo Limpieza de Datos/main.py"
"""

from pipeline import PipelineLimpieza
from constantes import ARCHIVO_CRUDO, ARCHIVO_LIMPIO

if __name__ == "__main__":
    PipelineLimpieza(ARCHIVO_CRUDO, ARCHIVO_LIMPIO).ejecutar()