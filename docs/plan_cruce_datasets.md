# Plan de cruce de datasets: Healthcare + Drugs

**Repositorio:** https://github.com/SUBHWEI/Mineria-De-Datos.git  
**Objetivo de negocio:** Analizar comportamiento por edades y tipo de drogas/medicamentos usados por la población, y a partir de ese análisis observar qué tipo de enfermedades se pueden tratar.

---

## 1. Dataset base (Mineria-De-Datos-main)

Archivo: `healthcare_dataset_transformado.csv` (resultado del pipeline actual).

Campos relevantes para el cruce:

| Campo | Tipo | Uso para cruce |
|---|---|---|
| `Age`, `Age Segmento`, `Age Robusto` | Numérico/Categórico | Clave demográfica (comportamiento por edades). |
| `Gender_Female`, `Gender_Male` | One-hot | Segmentación poblacional. |
| `Medication_Aspirin`, `Medication_Ibuprofen`, `Medication_Lipitor`, `Medication_Paracetamol`, `Medication_Penicillin` | One-hot (0/1) | Clave directa con fármacos. |
| `Medical Condition Nivel` | Categórico (transformado) | Condición médica asociada al ingreso (enfermedades tratables). |
| `Admission Type Nivel`, `Test Results_*`, `Insurance Provider_*`, `Blood Type_*`, `Billing Amount` | Contexto | Soporte de análisis (no claves primarias). |
| `Date of Admission`, `Discharge Date` | Fechas | Contexto temporal. |

---

## 2. Datasets candidatos en `proyecto/data/raw/`

| Dataset | Columnas clave | Utilidad para cruce |
|---|---|---|
| `Drugs_product.csv` (18 cols) | `PRODUCTID`, `PRODUCTNDC`, `PRODUCTTYPENAME`, `PROPRIETARYNAME`, `NONPROPRIETARYNAME`, `DOSAGEFORMNAME`, `ROUTENAME`, `SUBSTANCENAME`, `ACTIVE_NUMERATOR_STRENGTH`, `ACTIVE_INGRED_UNIT`, `PHARM_CLASSES`, `MARKETINGCATEGORYNAME`, `LABELERNAME`, `DEASCHEDULE` | Muy útil. Permite agrupar por principio activo, clase farmacológica, forma y vía. |
| `Drugs_package.csv` (4 cols) | `PRODUCTID`, `PRODUCTNDC`, `NDCPACKAGECODE`, `PACKAGEDESCRIPTION` | Complementario (presentaciones). No necesario en cruce inicial. |
| `Drugs_unfinished_product.csv` / `Drugs_unfinished_package.csv` | Similares a anteriores | Parciales (encoding distinto). No usar en cruce inicial. |
| `Nhanes_2005_2006.csv` (465 cols) | Demografía, medicamentos prescritos/OTC, condiciones, laboratorio | Útil para validación/agregados poblacionales. No hay join paciente-a-paciente con healthcare sintético. |
| `Nhanes_2007_2008`, `2009_2010`, `2011_2012`, `2013_2014` | Mismos bloques temáticos | Mismo caso: benchmark agregado por grupos de edad/sexo. |

---

## 3. Qué datos cruzar (recomendación)

### Cruce prioritario: Healthcare (transformado) ↔ Drugs_product.csv

- **Tipo:** Enriquecimiento por mapeo de nombres (no join por ID; join por medicamento).
- **Claves (flags → fármaco):**
  - `Medication_Aspirin` → `Aspirin` / `acetylsalicylic acid` (`NONPROPRIETARYNAME`/`SUBSTANCENAME`)
  - `Medication_Ibuprofen` → `ibuprofen`
  - `Medication_Lipitor` → `Lipitor` (`PROPRIETARYNAME`) / `atorvastatin` (`SUBSTANCENAME`)
  - `Medication_Paracetamol` → `paracetamol` / `acetaminophen`
  - `Medication_Penicillin` → familia `penicillin` en `SUBSTANCENAME`/`PHARM_CLASSES`
- **Qué ganar:** Agrupar por **clase terapéutica** (`PHARM_CLASSES`), vía (`ROUTENAME`), forma (`DOSAGEFORMNAME`), principio activo (`SUBSTANCENAME`). Permite responder: "¿qué familias de fármacos usan más por grupo etario?" y ligarlo a `Medical Condition Nivel`.

### Cruce complementario (agregado): Healthcare agregado ↔ NHANES agregado

- **Tipo:** Cruce a nivel **grupo etario/sexo** (no paciente). Crear agregados de prevalencia de uso de fármacos/condiciones en NHANES vs distribución de admisiones en healthcare.
- **Uso:** Validación de hipótesis y contexto poblacional. No es para modelado paciente-a-paciente.

**Recomendación:** Empezar con el Cruce prioritario (Drugs_product). NHANES queda como apoyo para validación agregada.

---

## 4. Plan de implementación (siguiendo lógica de Mineria-De-Datos-main)

Estructura por capas del pipeline actual:

| Capa | Acción |
|---|---|
| `repositorios/cargador.py` | Añadir carga de `Drugs_product.csv` (encoding UTF-8; `latin-1` para archivos unfinished si se usan). |
| `utilidades/constantes.py` | Añadir rutas y columnas clave; definir mapping entre flags healthcare y términos de búsqueda. |
| `servicios/limpieza.py` | Normalizar nombres de `Drugs_product` (lowercase, strip) para facilitar mapeo. |
| `servicios/calidad.py` (opcional) | Validar cobertura del mapeo (% de medicamentos del healthcare encontrados en Drugs_product). |
| `transformaciones.py` / `main.py` | Crear bridge table de mapeo (flag → producto(s) enriquecidos) y fusionar: añadir columnas enriquecidas al healthcare transformado (ej. `Aspirin_PHARM_CLASSES`, etc.) o columnas agrupadas por clase terapéutica. |

**Estrategia de mapeo:** Mapeo explícito por los 5 medicamentos (más fiable y trazable), alineado con el enfoque CRISP-DM documentado.

---

## 5. Resumen: qué se va a cruzar

- **Dataset A (izquierda):** `healthcare_dataset_transformado.csv` (filas = admisiones/pacientes). Campos: `Age/Segmento`, `Medication_*` (flags), `Medical Condition Nivel`.
- **Dataset B (derecha):** `Drugs_product.csv` (catálogo de fármacos). Campos a traer: `SUBSTANCENAME`, `NONPROPRIETARYNAME`, `PHARM_CLASSES`, `DOSAGEFORMNAME`, `ROUTENAME`, `DEASCHEDULE`.
- **Join lógico:** `healthcare.Medication_* = 1` ↔ `Drugs_product` (match por nombre/principio activo del medicamento correspondiente). Enriquecimiento condicional por cada medicamento, coherente con el patrón one-hot existente.

---

## 6. Siguientes pasos

1. Confirmar mapeo: listar 1-2 resultados por cada uno de los 5 fármacos en `Drugs_product.csv`.
2. Crear bridge table `medicamento_mapping.csv` (flag → términos de búsqueda → campos a enriquecer).
3. Extender pipeline (repositorios + constantes + servicios) siguiendo `main.py` como orquestador.
4. Generar dataset enriquecido y analizar: por `Age Segmento` + `PHARM_CLASSES` + `Medical Condition Nivel` para ver qué enfermedades se podrían tratar con qué familias terapéuticas.
