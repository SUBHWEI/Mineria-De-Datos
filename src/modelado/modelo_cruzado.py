# Arbol de decision cruzado: predecir Medication a partir de Age + Medical Condition
from pathlib import Path
import pickle

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.tree import DecisionTreeClassifier, plot_tree, export_text
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix

RAIZ = Path(__file__).resolve().parent.parent.parent
CARPETA_DATA = RAIZ / "data"
CARPETA_DOCS = RAIZ / "docs"
CARPETA_FIGURAS = CARPETA_DOCS / "figuras"
CARPETA_REGLAS = CARPETA_DOCS / "reglas"
CARPETA_ARBOL = CARPETA_DOCS / "arbol"
CARPETA_MODELS = RAIZ / "models"
for c in (CARPETA_DOCS, CARPETA_FIGURAS, CARPETA_REGLAS, CARPETA_ARBOL, CARPETA_MODELS):
    c.mkdir(parents=True, exist_ok=True)

ARCHIVO_LIMPIO = CARPETA_DATA / "healthcare_dataset_limpio.csv"
SEMILLA = 42


def preparar():
    df = pd.read_csv(ARCHIVO_LIMPIO)
    X = pd.get_dummies(df[["Age", "Medical Condition"]], columns=["Medical Condition"], drop_first=False)
    y = df["Medication"]
    return X, y


def graficar_matriz(y_true, y_pred, clases, ruta, titulo):
    cm = confusion_matrix(y_true, y_pred, labels=clases)
    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks(range(len(clases)))
    ax.set_yticks(range(len(clases)))
    ax.set_xticklabels(clases, rotation=45, ha="right")
    ax.set_yticklabels(clases)
    ax.set_xlabel("Predicho")
    ax.set_ylabel("Real")
    ax.set_title(titulo)
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, cm[i, j], ha="center", va="center", fontsize=8)
    fig.colorbar(im, ax=ax)
    fig.tight_layout()
    fig.savefig(ruta, dpi=150, bbox_inches="tight")
    plt.close(fig)


def graficar_importancia(importancias, ruta, titulo):
    fig, ax = plt.subplots(figsize=(8, 6))
    importancias[::-1].plot.barh(ax=ax, color="steelblue")
    ax.set_title(titulo)
    ax.set_xlabel("Importancia")
    fig.tight_layout()
    fig.savefig(ruta, dpi=150, bbox_inches="tight")
    plt.close(fig)


def main():
    X, y = preparar()
    print("Dataset:", X.shape, "| Clases:", sorted(y.unique().tolist()))

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.30, random_state=SEMILLA, stratify=y
    )
    baseline = y_train.value_counts(normalize=True).max()
    print(f"Baseline (clase mayoritaria): {baseline:.4f}")

    grid = GridSearchCV(
        DecisionTreeClassifier(random_state=SEMILLA),
        {"criterion": ["gini", "entropy"],
         "max_depth": [3, 4, 5, 6],
         "min_samples_leaf": [20, 50, 100]},
        cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=SEMILLA),
        scoring="f1_macro",
        n_jobs=-1,
    )
    grid.fit(X_train, y_train)
    modelo = grid.best_estimator_
    pred = modelo.predict(X_test)

    print("Mejores hiperparametros:", grid.best_params_)
    print(f"Accuracy train: {accuracy_score(y_train, modelo.predict(X_train)):.4f}")
    print(f"Accuracy test : {accuracy_score(y_test, pred):.4f}")
    print(f"F1-macro test : {f1_score(y_test, pred, average='macro'):.4f}")
    print("\nReporte de clasificacion (test):")
    print(classification_report(y_test, pred))

    graficar_matriz(y_test, pred, modelo.classes_,
                    CARPETA_FIGURAS / "matriz_confusion_cruzado.png",
                    "Matriz de confusion - Cruzado (Medication)")

    importancias = pd.Series(modelo.feature_importances_, index=X.columns).sort_values(ascending=False).head(15)
    graficar_importancia(importancias,
                         CARPETA_FIGURAS / "importancia_cruzado.png",
                         "Importancia de variables - Cruzado")

    reglas = export_text(modelo, feature_names=list(X.columns), max_depth=4)
    (CARPETA_REGLAS / "reglas_cruzado.txt").write_text(reglas, encoding="utf-8")

    fig, ax = plt.subplots(figsize=(18, 10))
    plot_tree(modelo, feature_names=X.columns, class_names=modelo.classes_,
              filled=True, rounded=True, max_depth=3, fontsize=8, ax=ax)
    fig.tight_layout()
    fig.savefig(CARPETA_ARBOL / "arbol_cruzado.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    with open(CARPETA_MODELS / "arbol_cruzado.pkl", "wb") as f:
        pickle.dump({"modelo": modelo, "features": list(X.columns)}, f)

    print("\nArchivos generados:")
    print(" -", CARPETA_FIGURAS / "matriz_confusion_cruzado.png")
    print(" -", CARPETA_FIGURAS / "importancia_cruzado.png")
    print(" -", CARPETA_ARBOL / "arbol_cruzado.png")
    print(" -", CARPETA_REGLAS / "reglas_cruzado.txt")
    print(" -", CARPETA_MODELS / "arbol_cruzado.pkl")


if __name__ == "__main__":
    main()
