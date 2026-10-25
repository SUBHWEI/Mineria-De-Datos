import random
import numpy as np
import pandas as pd
import sys
from pathlib import Path
from sklearn.tree import DecisionTreeClassifier

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.stdout = open(str(RAIZ / "docs" / "arbol" / "arboles_texto.txt"), "w", encoding="utf-8")

random.seed(42)
np.random.seed(42)

df = pd.read_csv(RAIZ / "data" / "healthcare_dataset_limpio.csv")


def enf_sugerida(edad):
    if edad <= 19:
        base = "Asthma"
    elif edad <= 39:
        base = "Diabetes"
    elif edad <= 59:
        base = "Hypertension"
    elif edad <= 79:
        base = "Arthritis"
    else:
        base = "Obesity"
    if random.random() < 0.15:
        base = random.choice(["Asthma", "Diabetes", "Hypertension", "Arthritis", "Obesity", "Cancer"])
    return base


df["Enfermedad_Sugerida"] = df["Age"].apply(enf_sugerida)


def med_sugerido(fila):
    cond = fila["Medical Condition"]
    test = fila["Test Results"]
    edad = fila["Age"]
    if cond == "Arthritis":
        med = "Ibuprofen"
    elif cond in ("Diabetes", "Hypertension", "Obesity"):
        med = "Lipitor"
    elif cond in ("Cancer", "Asthma"):
        med = "Paracetamol"
    else:
        med = "Aspirin"
    if test == "Abnormal" and random.random() < 0.70:
        med = "Penicillin"
    if edad >= 70 and med == "Paracetamol":
        med = "Aspirin"
    if random.random() < 0.15:
        med = random.choice(["Aspirin", "Ibuprofen", "Lipitor", "Paracetamol", "Penicillin"])
    return med


df["Medicamento_Sugerido"] = df.apply(med_sugerido, axis=1)

# ---------- Arbol 1: Enfermedad por edad ----------
X1 = df[["Age"]]
y1 = df["Enfermedad_Sugerida"]
t1 = DecisionTreeClassifier(max_depth=3, min_samples_leaf=50, random_state=42)
t1.fit(X1, y1)

# ---------- Arbol 2: Medicamento por enfermedad (+ edad) ----------
X2 = pd.get_dummies(df[["Medical Condition", "Age"]], columns=["Medical Condition"], drop_first=False)
y2 = df["Medicamento_Sugerido"]
t2 = DecisionTreeClassifier(max_depth=3, min_samples_leaf=50, random_state=42)
t2.fit(X2, y2)


def imprimir_arbol(modelo, feature_names, class_names, titulo):
    tree = modelo.tree_
    print("\n" + "=" * 80)
    print(titulo)
    print("=" * 80)

    def recurse(node, depth, prefix):
        if depth > 3:
            return
        if tree.children_left[node] == -1:
            cls = class_names[np.argmax(tree.value[node])]
            print(prefix + "└── CLASE: " + str(cls))
            return
        feat = feature_names[tree.feature[node]]
        thr = tree.threshold[node]
        print(prefix + "¿" + feat + " <= " + f"{thr:.2f}" + "?")
        print(prefix + "   ├── SÍ:")
        recurse(tree.children_left[node], depth + 1, prefix + "   │   ")
        print(prefix + "   └── NO:")
        recurse(tree.children_right[node], depth + 1, prefix + "       ")

    recurse(0, 0, "")
    print()


imprimir_arbol(t1, ["Age"], list(t1.classes_), "ARBOL 1 - Enfermedad sugerida por edad (profundidad 3)")
imprimir_arbol(t2, list(X2.columns), list(t2.classes_), "ARBOL 2 - Medicamento sugerido por enfermedad + edad (profundidad 3)")
