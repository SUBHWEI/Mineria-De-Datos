# Arboles derivados: etiquetas clinicas simuladas
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

ARCHIVO_CRUZADO = CARPETA_DATA / "healthcare_dataset_cruzado.csv"
SEMILLA = 42


def preparar_modelo_a(df):
    X = df[["Age"]]
    y = df["Enfermedad_Sugerida"]
    return X, y


def preparar_modelo_b(df):
    X = pd.get_dummies(df[["Age", "Enfermedad_Sugerida", "Test Results"]],
                       columns=["Enfermedad_Sugerida", "Test Results"], drop_first=False)
    y = df["Medicamento_Sugerido"]
    return X, y


def entrenar(X, y, nombre):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.30, random_state=SEMILLA, stratify=y
    )
    baseline = y_train.value_counts(normalize=True).max()
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
    print(f"=== {nombre} ===")
    print("Hiperparametros:", grid.best_params_)
    print(f"Baseline: {baseline:.4f}")
    print(f"Accuracy train: {accuracy_score(y_train, modelo.predict(X_train)):.4f}")
    print(f"Accuracy test : {accuracy_score(y_test, pred):.4f}")
    print(f"F1-macro test : {f1_score(y_test, pred, average='macro'):.4f}")
    print(classification_report(y_test, pred))
    return modelo, X, X_train, X_test, y_train, y_test, pred


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
    df = pd.read_csv(ARCHIVO_CRUZADO)
    print("Dataset cruzado derivado:", df.shape)

    # Modelo A
    Xa, ya = preparar_modelo_a(df)
    modelo_a, Xa_full, Xa_tr, Xa_te, ya_tr, ya_te, pred_a = entrenar(
        Xa, ya, "Modelo A - Enfermedad_Sugerida por Age"
    )
    graficar_matriz(ya_te, pred_a, modelo_a.classes_,
                    CARPETA_FIGURAS / "matriz_confusion_enfermedad_derivada.png",
                    "Matriz de confusion - Enfermedad derivada")
    imp_a = pd.Series(modelo_a.feature_importances_, index=Xa.columns).sort_values(ascending=False)
    graficar_importancia(imp_a,
                         CARPETA_FIGURAS / "importancia_enfermedad_derivada.png",
                         "Importancia - Enfermedad derivada")
    reglas_a = export_text(modelo_a, feature_names=list(Xa.columns), max_depth=4)
    (CARPETA_REGLAS / "reglas_enfermedad_derivada.txt").write_text(reglas_a, encoding="utf-8")
    fig, ax = plt.subplots(figsize=(12, 7))
    plot_tree(modelo_a, feature_names=Xa.columns, class_names=modelo_a.classes_,
              filled=True, rounded=True, max_depth=3, fontsize=9, ax=ax)
    fig.tight_layout()
    fig.savefig(CARPETA_ARBOL / "arbol_enfermedad_derivada.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    with open(CARPETA_MODELS / "arbol_enfermedad_derivada.pkl", "wb") as f:
        pickle.dump({"modelo": modelo_a, "features": list(Xa.columns)}, f)

    # Modelo B
    Xb, yb = preparar_modelo_b(df)
    modelo_b, Xb_full, Xb_tr, Xb_te, yb_tr, yb_te, pred_b = entrenar(
        Xb, yb, "Modelo B - Medicamento_Sugerido por Age + Enfermedad_Sugerida"
    )
    graficar_matriz(yb_te, pred_b, modelo_b.classes_,
                    CARPETA_FIGURAS / "matriz_confusion_cruzado_derivado.png",
                    "Matriz de confusion - Cruzado derivado")
    imp_b = pd.Series(modelo_b.feature_importances_, index=Xb.columns).sort_values(ascending=False).head(15)
    graficar_importancia(imp_b,
                         CARPETA_FIGURAS / "importancia_cruzado_derivado.png",
                         "Importancia - Cruzado derivado")
    reglas_b = export_text(modelo_b, feature_names=list(Xb.columns), max_depth=4)
    (CARPETA_REGLAS / "reglas_cruzado_derivado.txt").write_text(reglas_b, encoding="utf-8")
    fig, ax = plt.subplots(figsize=(16, 9))
    plot_tree(modelo_b, feature_names=Xb.columns, class_names=modelo_b.classes_,
              filled=True, rounded=True, max_depth=3, fontsize=8, ax=ax)
    fig.tight_layout()
    fig.savefig(CARPETA_ARBOL / "arbol_cruzado_derivado.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    with open(CARPETA_MODELS / "arbol_cruzado_derivado.pkl", "wb") as f:
        pickle.dump({"modelo": modelo_b, "features": list(Xb.columns)}, f)

    print("\nArchivos generados (Fase C):")
    print(" -", CARPETA_FIGURAS / "matriz_confusion_enfermedad_derivada.png")
    print(" -", CARPETA_FIGURAS / "importancia_enfermedad_derivada.png")
    print(" -", CARPETA_ARBOL / "arbol_enfermedad_derivada.png")
    print(" -", CARPETA_REGLAS / "reglas_enfermedad_derivada.txt")
    print(" -", CARPETA_MODELS / "arbol_enfermedad_derivada.pkl")
    print(" -", CARPETA_FIGURAS / "matriz_confusion_cruzado_derivado.png")
    print(" -", CARPETA_FIGURAS / "importancia_cruzado_derivado.png")
    print(" -", CARPETA_ARBOL / "arbol_cruzado_derivado.png")
    print(" -", CARPETA_REGLAS / "reglas_cruzado_derivado.txt")
    print(" -", CARPETA_MODELS / "arbol_cruzado_derivado.pkl")


if __name__ == "__main__":
    main()
