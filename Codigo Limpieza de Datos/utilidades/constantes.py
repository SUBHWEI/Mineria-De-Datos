from pathlib import Path

CARPETA_UTILIDADES = Path(__file__).resolve().parent
CARPETA_CODIGO = CARPETA_UTILIDADES.parent
CARPETA_PROYECTO = CARPETA_CODIGO.parent

ARCHIVO_CRUDO = CARPETA_PROYECTO / "healthcare_dataset_original.csv"
ARCHIVO_LIMPIO = CARPETA_PROYECTO / "healthcare_dataset_limpio.csv"

COLUMNAS_NUMERICAS = ["Age", "Billing Amount"]
COLUMNAS_TEXTO = ["Name", "Doctor", "Hospital"]
COLUMNA_FLAG_FACTURA_NEGATIVA = "Factura_Negativa"