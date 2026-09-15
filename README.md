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
mineria/
├── healthcare_dataset_original.csv   # datos crudos (no se modifica)
├── healthcare_dataset_limpio.csv     # resultado de la limpieza
├── Informe_Limpieza_Datos_Salud.docx # informe del proceso (entregable)
├── documentacion_crisp-dm.docx       # CRISP-DM aplicado, fases 1 a 3 (entregable)
├── limpieza_datos_salud.ipynb        # cuaderno de evidencia / recorrido paso a paso
└── Codigo Limpieza de Datos/         # código del pipeline por capas
    ├── main.py                       # orquestador: define el orden del proceso
    ├── repositorios/
    │   └── cargador.py               # acceso a datos: lectura del CSV
    ├── servicios/
    │   ├── limpieza.py               # duplicados, normalización de texto, marcado de facturas negativas
    │   └── calidad.py                # diagnóstico, outliers IQR, validación
    └── utilidades/
        └── constantes.py             # rutas y nombres de columnas
```

Cada capa tiene una sola responsabilidad y las dependencias van en un solo sentido: `main` → `servicios` → `repositorios`/`utilidades`.

## Cómo ejecutar el pipeline

```powershell
python "Codigo Limpieza de Datos/main.py"
```

El script carga el archivo crudo, aplica la limpieza en orden, valida y guarda `healthcare_dataset_limpio.csv`.

### Cuaderno de evidencia

Abrir `limpieza_datos_salud.ipynb` en Jupyter desde la raíz del proyecto (los imports ya agregan la carpeta `Codigo Limpieza de Datos` al `sys.path`).

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

## Referencias

- Chapman, P. et al. (2000). *CRISP-DM 1.0*. SPSS.
- Han, J., Kamber, M. y Pei, J. (2012). *Data mining: Concepts and techniques* (3.ª ed.). Elsevier.
- prasad22. (2024). *Healthcare dataset* [Conjunto de datos]. Kaggle.