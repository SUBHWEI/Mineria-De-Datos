# Limpieza del Healthcare Dataset

Proyecto de **Minería de Datos** (Corporación Universitaria Minuto de Dios). Se limpia el Healthcare Dataset de Kaggle por capas (repositorios, servicios y utilidades) para dejarlo listo para la siguiente etapa de modelado.

**Equipo (MIMETIC):** Manuel José Rivera Guzmán · Julián Andrés Correa Cuevas

## Dataset

- Fuente: [Healthcare Dataset](https://www.kaggle.com/datasets/prasad22/healthcare-dataset) (prasad22, 2024).
- Contenido: 55.500 admisiones hospitalarias, 15 columnas (datos del paciente, de la admisión y de la cuenta administrativa).
- Problemas encontrados en el crudo: 534 filas duplicadas, nombres con mayúsculas revueltas y 108 facturas con monto negativo.

## Requisitos

- Python 3.12+
- `pandas`

## Estructura del proyecto

```
Mineria-De-Datos/
├── data/                             # datos crudos, limpios, transformados, enriquecidos y derivados
├── docs/                             # documentación, tablas, figuras, árboles y reglas
│   ├── tabla/
│   ├── figuras/
│   ├── arbol/
│   └── reglas/
├── models/                           # modelos serializados (.pkl)
├── src/
│   ├── main.py                       # orquestador de limpieza
│   ├── main_cruce.py                 # orquestador de cruce healthcare + Drugs
│   ├── main_arbol.py                 # orquestador de análisis y modelado de árboles
│   ├── analisis/                     # análisis descriptivo y correlaciones
│   ├── etiquetas/                    # derivación de etiquetas clínicas
│   ├── modelado/                     # árboles de decisión (originales y derivados)
│   ├── negocio/                      # interpretación de negocio y política de stock
│   ├── visualizacion/                # generación de imágenes y texto de árboles
│   ├── repositorios/                 # acceso a datos
│   ├── servicios/                    # limpieza y calidad
│   ├── transformaciones*.py          # codificación de variables
│   └── utilidades/                  # constantes y rutas
└── README.md
```

Cada capa tiene una sola responsabilidad y las dependencias van en un solo sentido: `main` → `servicios`/`modelado` → `repositorios`/`utilidades`.

## Cómo ejecutar el pipeline

```powershell
python src/main.py
```

El script carga el archivo crudo, aplica la limpieza en orden, valida y guarda `healthcare_dataset_limpio.csv`.

### Cuaderno de evidencia

Abrir `docs/limpieza_datos_salud.ipynb` en Jupyter desde la raíz del proyecto (los imports agregan `src` al `sys.path`).

## Pipeline (orden y por qué)

1. Cargar el CSV crudo.
2. Diagnosticar (duplicados, nulos, `describe()`).
3. Quitar duplicados (se hace primero para no sesgar las cuentas posteriores).
4. Normalizar texto (`strip()` + `title()` en `Name`, `Doctor`, `Hospital`).
5. Marcar facturas negativas en `Factura_Negativa` (no se modifica el monto: es dinero, un dato sensible, y no se inventan valores).
6. Revisar outliers con la regla IQR, excluyendo las facturas marcadas.
7. Validar y exportar el archivo limpio.

## Resultados

| Indicador | Crudo | Limpio |
|---|---|---|
| Filas | 55.500 | 54.966 |
| Duplicados | 534 | 0 |
| Nulos | 0 | 0 |
| Facturas negativas | 108 | 106 marcadas (monto intacto, 0 imputadas) |
| Edades fuera de rango | 0 | 0 |
| Outliers (regla IQR) | 0 | 0 |

## Metodología

El proceso se documenta siguiendo **CRISP-DM** (fases 1 a 3): *Business Understanding*, *Data Understanding* y *Data Preparation*. Ver `documentacion_crisp-dm.docx`.

## Modelado: árbol de decisión

Se implementan dos experimentos con el mismo pipeline y las mismas features, cambiando la variable objetivo:

| Experimento | Variable objetivo | Accuracy (test) | F1-macro (test) | Baseline |
|---|---|---:|---:|---:|
| 1 | `Medication` (original) | 0.204 | ~0.16 | 0.201 |
| 2 | `Medicamento_Sugerido` (derivado por reglas clínicas) | 0.744 | 0.728 | 0.356 |

- **Experimento 1:** demuestra que el dataset original es sintético y no contiene patrón predictivo real.
- **Experimento 2:** usa una etiqueta derivada por reglas clínicas (documentada como escenario simulado) para mostrar que el árbol aprende patrones interpretables.

### Cómo ejecutar el modelado

Pipeline completo de árboles (Fases A, B, C y D):

```powershell
python src/main_arbol.py
```

Fase A (análisis descriptivo cruzado):

```powershell
python src/analisis/analisis_cruzado.py
```

Fase B (árboles predictivos originales):

```powershell
python src/modelado/modelo_enfermedad_por_edad.py
python src/modelado/modelo_medicamento_por_enfermedad.py
python src/modelado/modelo_cruzado.py
```

Modelo derivado (escenario simulado):

```powershell
python src/modelado/modelo_arbol_clinico.py
```

Fase C (etiquetas derivadas y árboles cruzados derivados):

```powershell
python src/etiquetas/derivar_etiquetas_clinicas.py
python src/modelado/modelo_cruzado_derivado.py
```

Fase D (interpretación de negocio y política de stock):

```powershell
python src/negocio/interpretacion_negocio.py
```

Salidas generadas (organizadas en subcarpetas de `docs/`):

- `data/healthcare_dataset_clinico.csv`
- `data/healthcare_dataset_cruzado.csv`
- `docs/tabla/` (CSV de tablas cruzadas y política de stock)
- `docs/figuras/` (heatmaps, matrices de confusión, importancia de variables)
- `docs/arbol/` (árboles en PNG y texto)
- `docs/reglas/` (reglas de los árboles en TXT)
- `docs/limitaciones.md`
- `docs/Informe_Predicciones_Cruzadas.docx`
- `docs/modelado_arbol_decision.ipynb`
- `models/` (modelos serializados .pkl)

### Entregables de modelado

- Plan: `docs/plan_predicciones_cruzadas.md`
- Orquestador: `src/main_arbol.py`
- Notebook de evidencia: `docs/modelado_arbol_decision.ipynb`
- Documentación Word: `docs/Informe_Predicciones_Cruzadas.docx`
- Limitaciones: `docs/limitaciones.md`

## Referencias

- Chapman, P. et al. (2000). *CRISP-DM 1.0*. SPSS.
- Han, J., Kamber, M. y Pei, J. (2012). *Data mining: Concepts and techniques* (3.ª ed.). Elsevier.
- prasad22. (2024). *Healthcare dataset* [Conjunto de datos]. Kaggle.