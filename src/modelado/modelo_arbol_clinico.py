# Arbol de decision con target derivado por reglas clinicas (escenario simulado)
import os
import random
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.tree import DecisionTreeClassifier, plot_tree, export_text
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder

CARPETA_PROYECTO = Path(__file__).resolve().parent.parent.parent
CARPETA_DATA = CARPETA_PROYECTO / "data"
CARPETA_DOCS = CARPETA_PROYECTO / "docs"
CARPETA_FIGURAS = CARPETA_DOCS / "figuras"
CARPETA_REGLAS = CARPETA_DOCS / "reglas"
CARPETA_ARBOL = CARPETA_DOCS / "arbol"
CARPETA_MODELS = CARPETA_PROYECTO / "models"
for c in (CARPETA_DOCS, CARPETA_FIGURAS, CARPETA_REGLAS, CARPETA_ARBOL, CARPETA_MODELS):
    c.mkdir(parents=True, exist_ok=True)
CARPETA_MODELS.mkdir(parents=True, exist_ok=True)
CARPETA_DOCS.mkdir(parents=True, exist_ok=True)

ARCHIVO_LIMPIO = CARPETA_DATA / "healthcare_dataset_limpio.csv"
ARCHIVO_CLINICO = CARPETA_DATA / "healthcare_dataset_clinico.csv"
SEMILLA = 42
random.seed(SEMILLA)
np.random.seed(SEMILLA)


def sugerir_medicamento(fila):
    """Regla clinica simulada para asignar un medicamento sugerido.

    Se usa para crear un escenario con patron predictivo (el dataset original
    asigna el medicamento casi al azar). Se documenta como etiqueta derivada.
    """
    condicion = fila["Medical Condition"]
    test = fila["Test Results"]
    edad = fila["Age"]

    # Regla base por condicion medica
    if condicion == "Arthritis":
        med = "Ibuprofen"
    elif condicion in ("Diabetes", "Hypertension", "Obesity"):
        med = "Lipitor"
    elif condicion in ("Cancer", "Asthma"):
        med = "Paracetamol"
    else:
        med = "Aspirin"

    # Si hay resultado anormal, priorizar antibiotico (infeccion probable)
    if test == "Abnormal" and random.random() < 0.70:
        med = "Penicillin"

    # Ajuste por edad: pacientes mayores -> prevencion cardiovascular
    if edad >= 70 and med in ("Paracetamol",):
        med = "Aspirin"

    # Ruido del 15% para simular variabilidad clinica real
    if random.random() < 0.15:
        med = random.choice(["Aspirin", "Ibuprofen", "Lipitor", "Paracetamol", "Penicillin"])

    return med


def preparar_datos():
    df = pd.read_csv(ARCHIVO_LIMPIO)
    df["Medicamento_Sugerido"] = df.apply(sugerir_medicamento, axis=1)
    df.to_csv(ARCHIVO_CLINICO, index=False)

    # Features (sin fuga): todo excepto el medicamento original y el sugerido
    y = df["Medicamento_Sugerido"]
    X = pd.get_dummies(
        df[["Age", "Gender", "Blood Type", "Medical Condition",
            "Admission Type", "Test Results", "Insurance Provider",
            "Billing Amount", "Factura_Negativa"]],
        columns=["Gender", "Blood Type", "Medical Condition", "Admission Type",
                 "Test Results", "Insurance Provider"],
        drop_first=True,
    )
    # Factura_Negativa a 0/1 si viene como texto
    if X["Factura_Negativa"].dtype == bool or X["Factura_Negativa"].dtype == object:
        X["Factura_Negativa"] = X["Factura_Negativa"].astype(int)
    return X, y, df


def main():
    X, y, df = preparar_datos()
    print("Dataset clinico:", df.shape)
    print("Distribucion Medicamento_Sugerido:")
    print(y.value_counts().to_string())
    print()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.30, random_state=SEMILLA, stratify=y
    )

    # Baseline: clase mayoritaria
    baseline_acc = y_train.value_counts(normalize=True).max()
    print(f"Baseline (clase mayoritaria): {baseline_acc:.4f}")

    # Grid search
    param_grid = {
        "criterion": ["gini", "entropy"],
        "max_depth": [3, 4, 5, 6],
        "min_samples_leaf": [20, 50, 100],
    }
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEMILLA)
    grid = GridSearchCV(
        DecisionTreeClassifier(random_state=SEMILLA),
        param_grid,
        cv=cv,
        scoring="f1_macro",
        n_jobs=-1,
    )
    grid.fit(X_train, y_train)
    print("Mejores hiperparametros:", grid.best_params_)
    print(f"Mejor F1-macro (CV): {grid.best_score_:.4f}")

    modelo = grid.best_estimator_
    pred_train = modelo.predict(X_train)
    pred_test = modelo.predict(X_test)

    print("\n=== Metricas ===")
    print(f"Accuracy train: {accuracy_score(y_train, pred_train):.4f}")
    print(f"Accuracy test : {accuracy_score(y_test, pred_test):.4f}")
    print(f"F1-macro test : {f1_score(y_test, pred_test, average='macro'):.4f}")
    print("\nReporte de clasificacion (test):")
    print(classification_report(y_test, pred_test))

    # Matriz de confusion
    cm = confusion_matrix(y_test, pred_test, labels=modelo.classes_)
    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks(range(len(modelo.classes_)))
    ax.set_yticks(range(len(modelo.classes_)))
    ax.set_xticklabels(modelo.classes_, rotation=45, ha="right")
    ax.set_yticklabels(modelo.classes_)
    ax.set_xlabel("Predicho")
    ax.set_ylabel("Real")
    ax.set_title("Matriz de confusion - Arbol clinico")
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, cm[i, j], ha="center", va="center", color="black", fontsize=9)
    fig.colorbar(im, ax=ax)
    fig.tight_layout()
    fig.savefig(CARPETA_FIGURAS / "matriz_confusion_arbol_clinico.png", dpi=150)
    plt.close(fig)

    # Importancia de variables
    importancias = pd.Series(modelo.feature_importances_, index=X.columns).sort_values(ascending=False).head(15)
    fig, ax = plt.subplots(figsize=(8, 6))
    importancias[::-1].plot.barh(ax=ax, color="steelblue")
    ax.set_title("Importancia de variables (Gini)")
    ax.set_xlabel("Importancia")
    fig.tight_layout()
    fig.savefig(CARPETA_FIGURAS / "importancia_variables_arbol_clinico.png", dpi=150)
    plt.close(fig)

    # Visualizacion del arbol (profundidad limitada para legibilidad)
    fig, ax = plt.subplots(figsize=(18, 10))
    plot_tree(
        modelo,
        feature_names=X.columns,
        class_names=modelo.classes_,
        filled=True,
        rounded=True,
        max_depth=3,
        fontsize=8,
        ax=ax,
    )
    fig.tight_layout()
    fig.savefig(CARPETA_ARBOL / "arbol_decision_clinico.png", dpi=150)
    plt.close(fig)

    # Reglas en texto
    reglas = export_text(modelo, feature_names=list(X.columns), max_depth=4)
    (CARPETA_REGLAS / "reglas_arbol_clinico.txt").write_text(reglas, encoding="utf-8")

    # Guardar modelo
    import pickle
    with open(CARPETA_MODELS / "arbol_decision_clinico.pkl", "wb") as f:
        pickle.dump({"modelo": modelo, "features": list(X.columns)}, f)

    print("\nArchivos generados:")
    print(" -", ARCHIVO_CLINICO)
    print(" -", CARPETA_FIGURAS / "matriz_confusion_arbol_clinico.png")
    print(" -", CARPETA_FIGURAS / "importancia_variables_arbol_clinico.png")
    print(" -", CARPETA_ARBOL / "arbol_decision_clinico.png")
    print(" -", CARPETA_REGLAS / "reglas_arbol_clinico.txt")
    print(" -", CARPETA_MODELS / "arbol_decision_clinico.pkl")


if __name__ == "__main__":
    main()
