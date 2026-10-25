# Orquestador del modulo de arboles y predicciones cruzadas (Fases A, B y C)
# Ejecutar desde la raiz: python src/main_arbol.py

import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SRC = RAIZ / "src"
sys.path.insert(0, str(SRC))

from analisis import analisis_cruzado
from etiquetas import derivar_etiquetas_clinicas
from negocio import interpretacion_negocio
from modelado import (
    modelo_enfermedad_por_edad,
    modelo_medicamento_por_enfermedad,
    modelo_cruzado,
    modelo_arbol_clinico,
    modelo_cruzado_derivado,
)


def ejecutar_script(relpath):
    ruta = SRC / relpath
    resultado = subprocess.run(
        [sys.executable, str(ruta)],
        cwd=str(RAIZ),
        capture_output=True,
        text=True,
    )
    if resultado.returncode != 0:
        print(resultado.stdout)
        print(resultado.stderr)
        raise RuntimeError(f"Fallo al ejecutar {relpath}")
    return resultado


PASOS_FUNCION = [
    ("Fase 1 - Analisis descriptivo cruzado", analisis_cruzado.main),
    ("Fase 2 - Enfermedad por edad", modelo_enfermedad_por_edad.main),
    ("Fase 3 - Medicamento por enfermedad", modelo_medicamento_por_enfermedad.main),
    ("Fase 4 - Cruzado original", modelo_cruzado.main),
    ("Fase 5 - Derivacion de etiquetas clinicas", derivar_etiquetas_clinicas.main),
    ("Fase 6 - Modelo derivado (Medicamento_Sugerido)", modelo_arbol_clinico.main),
    ("Fase 7 - Cruzado derivado", modelo_cruzado_derivado.main),
    ("Fase 8 - Interpretacion de negocio", interpretacion_negocio.main),
]

PASOS_SCRIPT = [
    ("Visualizacion - Arboles en texto", "visualizacion/imprimir_arboles.py"),
    ("Visualizacion - Imagenes de arboles", "visualizacion/generar_imagenes_arboles.py"),
]


def main():
    for nombre, funcion in PASOS_FUNCION:
        print("\n" + "=" * 80)
        print(nombre)
        print("=" * 80)
        try:
            funcion()
        except Exception as exc:
            print(f"[ERROR] {nombre}: {exc}")
            raise

    for nombre, relpath in PASOS_SCRIPT:
        print("\n" + "=" * 80)
        print(nombre)
        print("=" * 80)
        ejecutar_script(relpath)
        print(f"Completado: {relpath}")

    print("\n" + "=" * 80)
    print("Pipeline de arboles completado.")
    print("=" * 80)


if __name__ == "__main__":
    main()
