import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def analizar_correlaciones(
    df,
    columnas=None,
    metodo='pearson',
    top_n=15,
    figsize=(9, 7),
    annot=False,
    fmt='.2f',
    triangulo=True,
    cmap='coolwarm',
    centro=0,
    guardar_ruta=None,
    mostrar=True,
):
    if columnas is None:
        df_num = df.select_dtypes(include=['number']).copy()
    else:
        df_num = df[columnas].select_dtypes(include=['number']).copy()

    matriz_corr = df_num.corr(method=metodo)

    pares = []
    cols = matriz_corr.columns
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            r = matriz_corr.iloc[i, j]
            if pd.notna(r):
                pares.append((cols[i], cols[j], float(r), abs(float(r))))

    pares_ordenados = sorted(pares, key=lambda x: x[3], reverse=True)

    plt.figure(figsize=figsize)
    if triangulo:
        mask = np.triu(np.ones_like(matriz_corr, dtype=bool))
    else:
        mask = None
    sns.heatmap(
        matriz_corr,
        mask=mask,
        annot=annot,
        fmt=fmt,
        cmap=cmap,
        center=centro,
        square=True,
        linewidths=0.5,
        cbar_kws={'shrink': 0.8},
    )
    plt.title(f'Mapa de calor de correlaciones ({metodo})')
    plt.tight_layout()

    if guardar_ruta is not None:
        plt.savefig(guardar_ruta, dpi=150, bbox_inches='tight')
        print(f'Figura guardada: {guardar_ruta}')

    if mostrar:
        try:
            plt.show()
        except Exception:
            pass
    else:
        plt.close()

    top = pares_ordenados[:top_n] if top_n > 0 else pares_ordenados
    df_pares = pd.DataFrame(
        top,
        columns=['Variable 1', 'Variable 2', 'r', '|r|'],
    ).round(4)

    return {
        'matriz': matriz_corr,
        'pares_ordenados': pares_ordenados,
        'top_pares': df_pares,
    }

