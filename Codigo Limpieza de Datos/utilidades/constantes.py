from pathlib import Path

CARPETA_UTILIDADES = Path(__file__).resolve().parent
CARPETA_CODIGO = CARPETA_UTILIDADES.parent
CARPETA_PROYECTO = CARPETA_CODIGO.parent
CARPETA_DATA = CARPETA_PROYECTO / "data"
CARPETA_DATA.mkdir(parents=True, exist_ok=True)

ARCHIVO_CRUDO = CARPETA_DATA / "healthcare_dataset_original.csv"
ARCHIVO_LIMPIO = CARPETA_DATA / "healthcare_dataset_limpio.csv"
ARCHIVO_TRANSFORMADO = CARPETA_DATA / "healthcare_dataset_transformado.csv"
ARCHIVO_ENRIQUECIDO = CARPETA_DATA / "healthcare_dataset_enriquecido.csv"
ARCHIVO_ANALISIS = CARPETA_DATA / "analisis_edad_medicamento.csv"

# Dataset de farmacos (catalogo) usado para el cruce
ARCHIVO_DRUGS_PRODUCT = Path(
    r"C:\Users\major\OneDrive\Documentos\manuel\Universidad\octavo semestre\mineria de datos\Proyecto healtcare\proyecto\data\raw\Drugs_product.csv"
)

COLUMNAS_NUMERICAS = ["Age", "Billing Amount"]
COLUMNAS_TEXTO = ["Name", "Doctor", "Hospital"]
COLUMNA_FLAG_FACTURA_NEGATIVA = "Factura_Negativa"

# Mapeo: flag one-hot del healthcare -> terminos de busqueda en Drugs_product
MEDICAMENTOS_MAPEO = {
    "Aspirin": ["aspirin", "acetylsalicylic"],
    "Ibuprofen": ["ibuprofen"],
    "Lipitor": ["lipitor", "atorvastatin"],
    "Paracetamol": ["paracetamol", "acetaminophen"],
    "Penicillin": ["penicillin"],
}

COLUMNAS_DRUGS = [
    "SUBSTANCENAME",
    "NONPROPRIETARYNAME",
    "PHARM_CLASSES",
    "DOSAGEFORMNAME",
    "ROUTENAME",
    "DEASCHEDULE",
    "MARKETINGCATEGORYNAME",
    "PRODUCTTYPENAME",
]

DRUGS_NOMINALES_ONEHOT = [
    "PRODUCTTYPENAME",
    "MARKETINGCATEGORYNAME",
]