from pathlib import Path

import matplotlib.pyplot as plt

RAIZ = Path(__file__).resolve().parent.parent.parent
ARCHIVO_TEXTO = RAIZ / "docs" / "arbol" / "arboles_texto.txt"
CARPETA_DOCS = RAIZ / "docs"
CARPETA_ARBOL = CARPETA_DOCS / "arbol"
CARPETA_ARBOL.mkdir(parents=True, exist_ok=True)

texto = ARCHIVO_TEXTO.read_text(encoding="utf-8")

# Separar los dos arboles
partes = texto.split("=" * 80)
# partes: ['', titulo1, contenido1, titulo2, contenido2, ...]
bloques = []
for i in range(1, len(partes) - 1, 2):
    titulo = partes[i].strip()
    contenido = partes[i + 1].strip("\n")
    if titulo:
        bloques.append((titulo, contenido))

salidas = [
    ("arbol_enfermedad_texto.png", "Árbol 1 – Enfermedad sugerida por edad"),
    ("arbol_medicamento_texto.png", "Árbol 2 – Medicamento sugerido por enfermedad y edad"),
]


def renderizar(titulo, contenido, ruta):
    lineas = contenido.splitlines()
    n_lineas = max(len(lineas), 1)
    ancho = max(len(linea) for linea in lineas) if lineas else 60

    # Tamaño proporcional al contenido
    fig_w = min(max(10, ancho * 0.11), 22)
    fig_h = min(max(4, n_lineas * 0.28), 18)

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.axis("off")

    fig.text(
        0.02,
        0.97,
        titulo,
        fontsize=14,
        fontweight="bold",
        family="DejaVu Sans",
        va="top",
        ha="left",
    )
    fig.text(
        0.02,
        0.91,
        "\n".join(lineas),
        fontsize=9.5,
        family="DejaVu Sans Mono",
        va="top",
        ha="left",
        linespacing=1.35,
    )

    fig.savefig(ruta, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("Imagen generada:", ruta)


for (nombre, titulo), (titulo_bloque, contenido) in zip(salidas, bloques):
    renderizar(titulo, contenido, CARPETA_ARBOL / nombre)


# Imagen combinada (los dos arboles en una sola figura)
if len(bloques) >= 2:
    fig, axes = plt.subplots(1, 2, figsize=(24, 12))
    for ax, (titulo_bloque, contenido), (_, titulo) in zip(axes, bloques[:2], salidas):
        ax.axis("off")
        ax.set_title(titulo, fontsize=14, fontweight="bold", family="DejaVu Sans", loc="left")
        ax.text(
            0.0,
            1.0,
            contenido,
            fontsize=8.5,
            family="DejaVu Sans Mono",
            va="top",
            ha="left",
            linespacing=1.3,
            transform=ax.transAxes,
        )
    fig.tight_layout()
    ruta = CARPETA_ARBOL / "arboles_decision_texto.png"
    fig.savefig(ruta, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("Imagen generada:", ruta)
