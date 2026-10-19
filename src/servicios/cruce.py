import pandas as pd

from utilidades.constantes import MEDICAMENTOS_MAPEO, COLUMNAS_DRUGS, DRUGS_NOMINALES_ONEHOT


def _coincide(row, terminos):
    partes = []
    for col in ["NONPROPRIETARYNAME", "PROPRIETARYNAME", "SUBSTANCENAME"]:
        v = row.get(col, "")
        if pd.isna(v):
            continue
        partes.append(str(v))
    texto = " ".join(partes).lower()
    return any(t in texto for t in terminos)


class EnriquecedorHealthcareDrugs:
    def __init__(self, dfDrugs):
        self.dfDrugs = dfDrugs.copy()
        # columna auxiliar de texto combinado en minúsculas para matching vectorizado
        cols = ["NONPROPRIETARYNAME", "PROPRIETARYNAME", "SUBSTANCENAME"]
        self.dfDrugs["_texto"] = ""
        for c in cols:
            if c in self.dfDrugs.columns:
                self.dfDrugs["_texto"] = self.dfDrugs["_texto"] + " " + self.dfDrugs[c].fillna("").astype(str)
        self.dfDrugs["_texto"] = self.dfDrugs["_texto"].str.lower()

    def _mask(self, terminos):
        m = pd.Series(False, index=self.dfDrugs.index)
        for t in terminos:
            m = m | self.dfDrugs["_texto"].str.contains(t, regex=False, na=False)
        return m

    def construir_perfil(self, terminos):
        """Devuelve un dict con valores representativos (moda) para un medicamento."""
        mask = self._mask(terminos)
        sub = self.dfDrugs.loc[mask]
        perfil = {"n_productos": len(sub)}
        for col in COLUMNAS_DRUGS:
            if col in sub.columns and len(sub) > 0:
                serie = sub[col].dropna()
                if len(serie) > 0:
                    perfil[col] = serie.mode().iloc[0]
                else:
                    perfil[col] = None
            else:
                perfil[col] = None
        # clases terapéuticas únicas (top)
        if "PHARM_CLASSES" in sub.columns and len(sub) > 0:
            clases = set()
            for v in sub["PHARM_CLASSES"].dropna():
                for c in str(v).split(","):
                    c = c.strip()
                    if c:
                        clases.add(c)
            perfil["CLASES_UNICAS"] = "; ".join(sorted(clases)[:8])
        else:
            perfil["CLASES_UNICAS"] = None
        return perfil

    def enriquecer(self, dfHealthcare):
        df = dfHealthcare.copy()
        perfiles = {}
        for medicamento, terminos in MEDICAMENTOS_MAPEO.items():
            perfiles[medicamento] = self.construir_perfil(terminos)

        # columnas enriquecidas por medicamento (solo donde el flag es 1)
        for medicamento in MEDICAMENTOS_MAPEO:
            colFlag = f"Medication_{medicamento}"
            perfil = perfiles[medicamento]
            for attr in ["PHARM_CLASSES", "DOSAGEFORMNAME", "ROUTENAME", "DEASCHEDULE", "CLASES_UNICAS"]:
                colNueva = f"{colFlag}_{attr}"
                df[colNueva] = None
                if colFlag in df.columns:
                    mask = df[colFlag] == 1
                    df.loc[mask, colNueva] = perfil.get(attr)

        # columna combinada: clases terapéuticas de los medicamentos activos
        def clases_activas(fila):
            clases = []
            for medicamento in MEDICAMENTOS_MAPEO:
                colFlag = f"Medication_{medicamento}"
                if colFlag in fila and fila[colFlag] == 1:
                    p = perfiles[medicamento]
                    if p.get("CLASES_UNICAS"):
                        clases.append(f"{medicamento}: {p['CLASES_UNICAS']}")
            return " | ".join(clases) if clases else None

        df["Medicamentos_Clases_Terapeuticas"] = df.apply(clases_activas, axis=1)

        # conteo de medicamentos activos por fila
        flags = [f"Medication_{m}" for m in MEDICAMENTOS_MAPEO if f"Medication_{m}" in df.columns]
        df["Num_Medicamentos"] = df[flags].sum(axis=1) if flags else 0

        return df, perfiles

    def resumen_cobertura(self):
        out = []
        for medicamento, terminos in MEDICAMENTOS_MAPEO.items():
            p = self.construir_perfil(terminos)
            out.append({"Medicamento": medicamento, "Productos_en_catalogo": p["n_productos"]})
        return pd.DataFrame(out)
