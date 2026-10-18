from pathlib import Path

CARPETA_UTILIDADES = Path(__file__).resolve().parent
CARPETA_CODIGO = CARPETA_UTILIDADES.parent
CARPETA_PROYECTO = CARPETA_CODIGO.parent

ARCHIVO_CRUDO = CARPETA_PROYECTO / "healthcare_dataset_original.csv"
ARCHIVO_LIMPIO = CARPETA_PROYECTO / "healthcare_dataset_limpio.csv"
ARCHIVO_TRANSFORMADO = CARPETA_PROYECTO / "healthcare_dataset_transformado.csv"
ARCHIVO_ENRIQUECIDO = CARPETA_PROYECTO / "healthcare_dataset_enriquecido.csv"
ARCHIVO_ANALISIS = CARPETA_PROYECTO / "analisis_edad_medicamento.csv"

# Dataset de fármacos (catálogo) usado para el cruce
ARCHIVO_DRUGS_PRODUCT = Path(
    r"C:\Users\major\OneDrive\Documentos\manuel\Universidad\octavo semestre\mineria de datos\Proyecto healtcare\proyecto\data\raw\Drugs_product.csv"
)

COLUMNAS_NUMERICAS = ["Age", "Billing Amount"]
COLUMNAS_TEXTO = ["Name", "Doctor", "Hospital"]
COLUMNA_FLAG_FACTURA_NEGATIVA = "Factura_Negativa"

# Mapeo: flag one-hot del healthcare -> términos de búsqueda en Drugs_product
# (se buscan en NONPROPRIETARYNAME, PROPRIETARYNAME y SUBSTANCENAME, en minúsculas)
MEDICAMENTOS_MAPEO = {
    "Aspirin": ["aspirin", "acetylsalicylic"],
    "Ibuprofen": ["ibuprofen"],
    "Lipitor": ["lipitor", "atorvastatin"],
    "Paracetamol": ["paracetamol", "acetaminophen"],
    "Penicillin": ["penicillin"],
}

# Columnas del catálogo de fármacos a traer al enriquecimiento
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

# Atributos de bajo nivel a codificar one-hot en Drugs (nominales, sin orden)
DRUGS_NOMINALES_ONEHOT = [
    "PRODUCTTYPENAME",
    "MARKETINGCATEGORYNAME",
]
