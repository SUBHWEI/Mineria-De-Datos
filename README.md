# Proyecto de Minería de Datos - Healthcare Dataset

Proyecto de Minería de Datos (Corporación Universitaria Minuto de Dios). Recorre el ciclo de
preparación de datos sobre el Healthcare Dataset de Kaggle: limpieza, transformación, cruce con
un catálogo de medicamentos (Drugs_product) y análisis exploratorio (EDA). El código se organiza
por capas (repositorios, servicios y utilidades) para dejarlo listo para la etapa de modelado.

Equipo: Manuel Rivera (Manuel1532PK) y Julián Correa (Subhwei).

## Datasets

Healthcare Dataset
- Fuente: https://www.kaggle.com/datasets/prasad22/healthcare-dataset (prasad22, 2024).
- Contenido: 55.500 admisiones hospitalarias, 15 columnas (datos del paciente, de la admisión y de
  la cuenta administrativa).
- Problemas en el crudo: 534 filas duplicadas, nombres con mayúsculas y minúsculas revueltas y 108
  facturas con monto negativo.

Drugs_product (catálogo de fármacos, FDA)
- Se usa solo para enriquecer el dataset de salud. Se cruza por principio activo con los
  medicamentos presentes en el healthcare (Aspirin, Ibuprofen, Lipitor, Paracetamol, Penicillin).
- Se carga con encoding latin-1.

Archivos generados en data/ (todos reproducibles con el código en src/):
- healthcare_dataset_original.csv: crudo, 55.500 filas x 15 columnas (no se modifica).
- healthcare_dataset_limpio.csv: 54.966 filas x 16 columnas (agrega Factura_Negativa).
- healthcare_dataset_transformado.csv: 54.966 filas x 36 columnas.
- healthcare_dataset_enriquecido.csv: 54.966 filas x 63 columnas (cruce con Drugs).
- drugs_product_limpio.csv y drugs_product_transformado.csv (catálogo normalizado).
- analisis_edad_medicamento.csv: admisiones por segmento de edad cruzadas con cada medicamento.

## Requisitos

- Python 3.12+
- pandas
- scikit-learn (para las transformaciones)
- matplotlib y seaborn (para el análisis de correlaciones)

## Estructura del proyecto

```
mineria/
├── README.md
├── informe_laboratorio.docx
├── data/
│   ├── healthcare_dataset_original.csv
│   ├── healthcare_dataset_limpio.csv
│   ├── healthcare_dataset_transformado.csv
│   ├── healthcare_dataset_enriquecido.csv
│   ├── drugs_product_limpio.csv
│   ├── drugs_product_transformado.csv
│   └── analisis_edad_medicamento.csv
├── docs/
│   ├── Informe_Limpieza_Datos_Salud.docx
│   ├── Informe_Transformacion_Datos_Salud.docx
│   ├── documentacion_crisp-dm.docx
│   ├── heatmap_correlaciones.png
│   └── limpieza_datos_salud.ipynb
└── src/
    ├── main.py                    # orquestador de la limpieza
    ├── main_cruce.py              # orquestador del cruce healthcare x Drugs
    ├── transformaciones.py        # codificación y escalado del healthcare
    ├── transformaciones_drugs.py  # codificación del catálogo Drugs
    ├── analisis_correlaciones.py  # heatmap y ranking de correlaciones
    ├── repositorios/
    │   └── cargador.py            # acceso a datos (lectura de CSV)
    ├── servicios/
    │   ├── limpieza.py            # duplicados, normalización de texto, facturas negativas
    │   ├── calidad.py             # diagnóstico, outliers IQR, validación
    │   └── cruce.py               # enriquecimiento con el catálogo Drugs
    └── utilidades/
        └── constantes.py          # rutas y nombres de columnas
```

Cada capa tiene una sola responsabilidad y las dependencias van en un solo sentido:
main -> servicios -> repositorios / utilidades.

## Cómo ejecutar

Ejecutar en orden desde la raíz del proyecto:

    python src/main.py
    python src/transformaciones.py
    python src/transformaciones_drugs.py
    python src/main_cruce.py

Cada script valida, imprime el resumen del paso y guarda su CSV en data/. El análisis de
correlaciones también se puede ejecutar directo:

    python src/analisis_correlaciones.py

Cuaderno de evidencia
- Abrir docs/limpieza_datos_salud.ipynb en Jupyter desde la raíz del proyecto (los imports agregan
  la carpeta src/ al sys.path).

## Etapas del proceso

1. Limpieza (src/main.py)
   1. Cargar el CSV crudo (data/healthcare_dataset_original.csv).
   2. Diagnosticar: filas, duplicados, nulos y describe() de las numéricas.
   3. Quitar duplicados (primero, para no sesgar los conteos posteriores).
   4. Normalizar texto con strip() + title() en Name, Doctor y Hospital.
   5. Marcar las facturas negativas en la columna Factura_Negativa. No se modifica el monto:
      en dinero no se inventan valores.
   6. Revisar outliers con la regla IQR (1,5), excluyendo las facturas marcadas.
   7. Validar y exportar a data/healthcare_dataset_limpio.csv.

2. Transformación del healthcare (src/transformaciones.py)
   - One-hot (nominales): Gender, Blood Type, Insurance Provider, Medication y Test Results
     -> 23 columnas binarias.
   - Ordinal por triaje: Medical Condition (1 a 6) y Admission Type (1 a 3), donde 1 es la
     prioridad más alta.
   - Edad: KBinsDiscretizer (n_bins=4, strategy=quantile) genera Age Segmento, y RobustScaler
     sobre los segmentos genera Age Robusto (mediana 0, IQR 1).
   - Billing Amount y Room Number no se transforman (dinero e identificador físico).
   - Factura_Negativa se conserva como marca de auditoría (0/1).
   - Salida: data/healthcare_dataset_transformado.csv (54.966 x 36).

3. Transformación del catálogo Drugs (src/transformaciones_drugs.py)
   - One-hot (nominales): PRODUCTTYPENAME y MARKETINGCATEGORYNAME.
   - Ordinal: DEASCHEDULE (CV=1, CIV=2, CIII=3, CII=4).
   - Salidas: data/drugs_product_limpio.csv y data/drugs_product_transformado.csv.

4. Cruce healthcare x Drugs (src/main_cruce.py)
   - Empareja por principio activo entre los medicamentos del healthcare y el catálogo FDA.
   - Añade atributos farmacológicos por medicamento activo (PHARM_CLASSES, DOSAGEFORMNAME,
     ROUTENAME, DEASCHEDULE, clases terapéuticas únicas).
   - Agrega Medicamentos_Clases_Terapeuticas y Num_Medicamentos.
   - Salida: data/healthcare_dataset_enriquecido.csv (54.966 x 63) y
     data/analisis_edad_medicamento.csv.

5. Análisis exploratorio (src/analisis_correlaciones.py + docs/limpieza_datos_salud.ipynb)
   - Matriz de correlaciones (Pearson), heatmap y ranking de los pares con mayor |r|.
   - Genera docs/heatmap_correlaciones.png.
   - Resultados documentados en informe_laboratorio.docx (Sesión 5): hipótesis, hallazgos y
     recomendaciones.

## Resultados de la limpieza

- Filas: 55.500 -> 54.966
- Duplicados: 534 -> 0
- Nulos: 0 -> 0
- Facturas negativas: 108 en el crudo, 106 marcadas tras quitar duplicados (monto intacto, 0
  valores imputados)
- Edades fuera de rango: 0
- Outliers por regla IQR: 0

## Entregables

- docs/Informe_Limpieza_Datos_Salud.docx
- docs/Informe_Transformacion_Datos_Salud.docx
- docs/documentacion_crisp-dm.docx
- informe_laboratorio.docx (informe de la Sesión 5, EDA)
- docs/limpieza_datos_salud.ipynb (cuaderno de evidencia)
- data/healthcare_dataset_limpio.csv y demás CSV derivados

## Metodología

El proceso se documenta siguiendo CRISP-DM. Esta entrega cubre las fases 1 a 3:
Business Understanding, Data Understanding y Data Preparation. Las fases de modelado, evaluación
y despliegue quedan como trabajo futuro. Ver docs/documentacion_crisp-dm.docx.

## Nota importante

La constante ARCHIVO_DRUGS_PRODUCT en src/utilidades/constantes.py tiene una ruta absoluta
hardcodeada a una máquina específica
(C:\Users\major\OneDrive\Documentos\manuel\...\data\raw\Drugs_product.csv). Antes de ejecutar
src/main_cruce.py o src/transformaciones_drugs.py hay que ajustar esa ruta a la ubicación local
del archivo Drugs_product.csv. Los scripts de limpieza y transformación del healthcare no la
necesitan.

## Referencias

- Chapman, P. et al. (2000). CRISP-DM 1.0. SPSS.
- Han, J., Kamber, M. y Pei, J. (2012). Data mining: Concepts and techniques (3.ª ed.). Elsevier.
- prasad22. (2024). Healthcare dataset [Conjunto de datos]. Kaggle.
