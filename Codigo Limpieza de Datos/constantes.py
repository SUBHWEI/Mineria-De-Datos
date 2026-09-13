from pathlib import Path

CARPETA_CODIGO = Path(__file__).resolve().parent
CARPETA_PROYECTO = CARPETA_CODIGO.parent

ARCHIVO_CRUDO = CARPETA_PROYECTO / "healthcare_dataset_original.csv"
ARCHIVO_LIMPIO = CARPETA_PROYECTO / "healthcare_dataset_limpio.csv"

COLUMNAS_NUMERICAS = ["Age", "Billing Amount"]
COLUMNAS_TEXTO = ["Name", "Doctor", "Hospital"]