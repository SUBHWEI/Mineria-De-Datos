# Documentacion CRISP-DM aplicada al proyecto de Limpieza de Datos

---

## 1. Contexto general del proyecto

### 1.1 El dataset
Se trabajo con el Healthcare Dataset de Kaggle (prasad22, 2024). Es un
conjunto de datos publicos con **55.500 admisiones hospitalarias**, 15
columnas y datos del paciente, de la admision y de la parte administrativa
de la cuenta:

- **Paciente:** Name, Age, Gender, Blood Type, Medical Condition.
- **Admision:** Date of Admission, Admission Type, Discharge Date, Medication, Test Results.
- **Administrativo:** Doctor, Hospital, Insurance Provider, Billing Amount, Room Number.

### 1.2 El problema a resolver
El dataset crudo no es confiable para analisis ni modelado: aunque no tiene
valores nulos, la revision completa revela tres problemas de calidad:

- **534 filas duplicadas exactas**, que inflan conteos y sesgan estadisticas.
- **Nombres con mayusculas y minusculas mezcladas** (ej. "Bobby JacksOn"),
  que impiden busquedas y agrupaciones consistentes.
- **106 facturas con monto negativo** (ej. -2008.49), un valor imposible para
  el negocio que distorsiona cualquier calculo financiero.

### 1.3 El objetivo
Entregar una version limpia y confiable del dataset, lista para la siguiente
etapa (modelado), conservando la mayor cantidad de informacion valida: solo
se eliminan repeticiones exactas y se imputan los valores imposibles, sin
borrar registros completos.

### 1.4 La solucion implementada
Se construyo un pipeline de limpieza por capas en Python (pandas), versionado
en la carpeta `Codigo Limpieza de Datos` con una arquitectura multiservicio:

- **Repositorios:** `cargador.py` — acceso a datos (lectura del CSV).
- **Servicios:** `limpieza.py` (duplicados, texto, valores imposibles) y
  `calidad.py` (diagnostico, outliers, validacion).
- **Utilidades:** `constantes.py` — rutas y nombres de columnas.
- **Orquestador:** `main.py` — define el orden del proceso.

Entregables: `healthcare_dataset_limpio.csv` (54.966 filas), informe del
proceso en Word y cuaderno de evidencia en Jupyter
(`limpieza_datos_salud.ipynb`).

---

## 2. Que es CRISP-DM

CRISP-DM (CRoss-Industry Standard Process for Data Mining) es el proceso
estandar de mineria de datos. Tiene 6 fases en total, pero esta documentacion
cubre las **fases 1 a 3**, que son las que el proyecto desarrolla: el
entendimiento del negocio, el entendimiento de los datos y la preparacion de
los datos (limpieza). Las siguientes fases (modelado, evaluacion y despliegue)
quedan como trabajo futuro.

---

## 3. Las fases 1 a 3 aplicadas a este proyecto

### Fase 1 — Business Understanding (Entendimiento del negocio)

**Contexto:** el sector salud maneja datos administrativos y clinicos en
volumen. Para tomar decisiones (costos, calidad, predicciones) los datos deben
ser confiables.

**Objetivo del proyecto:** entregar una version limpia y confiable del
Healthcare Dataset (55.500 admisiones hospitalarias), lista para analisis
estadistico o modelado, conservando la mayor cantidad de informacion valida.

**Criterios de exito (medibles):**
- 0 filas duplicadas.
- 0 valores nulos.
- 0 facturas con monto negativo (valor imposible).
- Edades dentro de un rango humano (0-120 anos).
- No perder informacion valida: solo se eliminan repeticiones exactas y se
  imputan los valores imposibles, no se borran registros completos.

**Salida de esta fase:** el problema = el dataset crudo no es confiable para
su uso. El exito se mide con los 4 criterios anteriores.

### Fase 2 — Data Understanding (Entendimiento de los datos)

**Actividades realizadas:**
- Carga del archivo `healthcare_dataset_original.csv` (55.500 filas x 15 columnas).
- Diagnostico inicial con el servicio `Diagnosticador`: `describe()` sobre
  `Age` y `Billing Amount`, `duplicated().sum()` para filas repetidas,
  `isna().sum().sum()` para celdas vacias.

**Hallazgos:**
| Hallazgo | Valor |
|---|---|
| Filas | 55.500 |
| Duplicados exactos | 534 |
| Nulos | 0 |
| Edad | min 13, max 89 (rango valido) |
| Billing Amount | min -2008.49, max 52764.28 |

**Interpretacion:** el dataset "parece limpio" por no tener nulos, pero la
revision completa revelo duplicados y valores imposibles: no tener NaN no
equivale a tener calidad.

**Refinamiento (iteracion hacia Fase 1):** ante las facturas negativas se
investigo si el error dependia de alguna variable (tipo de admision,
aseguradora, condicion medica). Al comparar la distribucion de las facturas
negativas contra el dataset completo, las proporciones son casi identicas:
el error es aleatorio e independiente (MCAR). Esto define el tratamiento en
la Fase 3.

| Proporcion por tipo de admision | Negativas | Dataset completo |
|---|---|---|
| Urgent | 35.8% | 33.5% |
| Elective | 34.0% | 33.6% |
| Emergency | 30.2% | 32.9% |

### Fase 3 — Data Preparation (Preparacion de los datos)

Es la fase central de este proyecto. Se ejecuta con el pipeline por capas de
la carpeta `Codigo Limpieza de Datos` (main.py orquesta repositorios,
servicios y utilidades).

| Paso | Servicio | Accion | Resultado |
|---|---|---|---|
| 1. Cargar | `repositorios/cargador.py` | Lectura del CSV crudo | 55.500 filas |
| 2. Quitar duplicados | `servicios/limpieza.py` (TratadorDuplicados) | `drop_duplicates()` | -534 filas |
| 3. Normalizar texto | `servicios/limpieza.py` (NormalizadorTexto) | `strip()` + `title()` sobre Name, Doctor, Hospital | Nombres unificados |
| 4. Corregir facturas | `servicios/limpieza.py` (TratadorValoresImposibles) | Reemplazo de 106 negativos con la mediana de los validos (25.593,87) | 0 montos negativos |
| 5. Revisar outliers | `servicios/calidad.py` (AnalizadorOutliers) | Regla IQR (Tukey) | 0 valores fuera de rango |
| 6. Validar | `servicios/calidad.py` (Validador) | Checks de calidad | 0 duplicados, 0 nulos, 0 negativos, edades en rango |
| 7. Exportar | main.py | `to_csv()` con 2 decimales | `healthcare_dataset_limpio.csv` |

**Decisiones tecnicas justificadas:**
- **Duplicados primero:** si no se eliminan antes, los calculos posteriores
  (medianas, proporciones) cuentan filas dobles y se sesgan.
- **Mediana y no media:** la mediana es robusta a valores extremos; la media
  se contamina con montos atipicos.
- **Imputar y no borrar:** al ser el error MCAR, es seguro imputar con la
  mediana de los valores validos; el registro del paciente se conserva.
- **IQR solo informa:** el IQR no detecto los negativos porque el limite
  inferior (-23414.78) quedo por debajo del minimo real. Son errores de
  negocio, por eso se trataron con la regla `Billing Amount < 0`.

---

## 4. Conclusiones

- El proyecto desarrolla las fases 1 a 3 de CRISP-DM: Business Understanding,
  Data Understanding y Data Preparation.
- El proceso ES iterativo: el analisis de tipo de admision (Data Understanding)
  definio el tratamiento de los negativos en la preparacion (Data Preparation).
- La sistematizacion por capas (repositorios/servicios/utilidades) hace el
  proceso repetible y auditable: cada paso es un servicio comprobable.
- El objetivo se expreso con criterios cuantitativos (0 duplicados, 0 nulos,
  0 negativos, edades en rango) y la preparacion los cumple sin destruir datos
  validos.
- La siguiente etapa seria Modelado (Fase 4), para la que el dataset limpio
  queda listo.

---

## 5. Referencias

- Chapman, P. et al. (2000). CRISP-DM 1.0. SPSS.
- Han, J., Kamber, M. y Pei, J. (2012). Data mining: Concepts and techniques (3. ed.). Elsevier.
- prasad22. (2024). Healthcare dataset [Conjunto de datos]. Kaggle.