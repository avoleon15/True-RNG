"""Pruebas estadísticas y comparación visual de los números generados.

Uso (después de generar.py):
    .venv/bin/python pruebas.py

Pruebas (umbral p >= 0.01, como en NIST SP 800-22):
  - Frecuencia (monobit): ¿hay tantos 0 como 1?
  - Rachas (runs): ¿los bits alternan como se espera?
  - Chi-cuadrada: ¿los 256 valores salen con la misma frecuencia?
  - Correlación entre vecinos (lag 1).
Se corren sobre los números finales y sobre el ruido crudo (antes del hash),
porque un hash puede hacer pasar las pruebas aunque la entrada sea mala.
"""
from math import erfc, sqrt

import cv2
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

from generar import BITS_BAJOS, LADO, foto_mas_reciente, salida

ALFA = 0.01


def monobit(bits: np.ndarray) -> float:
    n = len(bits)
    s = abs(int(bits.sum()) * 2 - n)
    return erfc(s / sqrt(n) / sqrt(2))


def rachas(bits: np.ndarray) -> float:
    n = len(bits)
    pi = bits.mean()
    if abs(pi - 0.5) >= 2 / sqrt(n):
        return 0.0  # la prueba de frecuencia ya falla; NIST da p = 0
    v = 1 + int(np.count_nonzero(bits[1:] != bits[:-1]))
    return erfc(abs(v - 2 * n * pi * (1 - pi)) / (2 * sqrt(2 * n) * pi * (1 - pi)))


def correlacion(x: np.ndarray) -> float:
    x = x.astype(np.float64)
    return float(np.corrcoef(x[:-1], x[1:])[0, 1])


def entropia(x: np.ndarray, valores: int) -> float:
    p = np.bincount(x, minlength=valores) / len(x)
    p = p[p > 0]
    return float(-(p * np.log2(p)).sum())


def linea(nombre: str, p: float) -> str:
    return f"  {nombre:<28} p = {p:.4f}   {'PASA' if p >= ALFA else 'FALLA'}"


def main() -> None:
    numeros = np.load(salida / "numeros.npy")
    crudo = np.load(salida / "crudo.npy")
    imagen = cv2.imread(str(foto_mas_reciente()))

    out = []
    out.append(f"NÚMEROS FINALES ({len(numeros):,} bytes, 0-255)")
    bits = np.unpackbits(numeros)
    chi = stats.chisquare(np.bincount(numeros, minlength=256))
    r = correlacion(numeros)
    out.append(linea("Frecuencia (monobit)", monobit(bits)))
    out.append(linea("Rachas", rachas(bits)))
    out.append(linea("Chi-cuadrada (256 valores)", chi.pvalue))
    out.append(f"  Correlación con el vecino    r = {r:+.4f}   (esperado ~ 0, tolerancia ±{3 / sqrt(len(numeros)):.4f})")
    out.append(f"  Entropía de Shannon          {entropia(numeros, 256):.4f} de 8 bits")
    out.append(f"  Media                        {numeros.mean():.2f} (esperado 127.5)")
    out.append(f"  Valores repetidos juntos     {int((numeros[1:] == numeros[:-1]).sum())} de {len(numeros) - 1} (esperado ~{(len(numeros) - 1) / 256:.0f})")

    out.append("")
    out.append("RUIDO CRUDO (bits bajos de la foto, antes del hash)")
    bits_crudos = np.unpackbits(crudo)
    muestras = (imagen & (2**BITS_BAJOS - 1)).reshape(-1)
    out.append(linea("Frecuencia (monobit)", monobit(bits_crudos)))
    out.append(linea("Rachas", rachas(bits_crudos)))
    out.append(f"  Correlación con el vecino    r = {correlacion(muestras):+.4f}   (esperado ~ 0)")
    out.append(f"  Entropía de Shannon          {entropia(muestras, 2**BITS_BAJOS):.4f} de {BITS_BAJOS} bits por muestra")

    out.append("")
    out.append("Nota: el hash reparte bien los bits aunque la entrada tenga poca entropía.")
    out.append("Por eso importa el bloque 'RUIDO CRUDO': si ahí la entropía es baja, hay que")
    out.append("aumentar los bits crudos por número (usar fotos más grandes o varias fotos).")

    reporte = "\n".join(out)
    print(reporte)
    (salida / "reporte.txt").write_text(reporte + "\n", encoding="utf-8")

    # Comparación visual: escena, ruido crudo amplificado y números finales.
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    h, w = gris.shape
    y0, x0 = (h - LADO) // 2, (w - LADO) // 2
    recorte = gris[y0:y0 + LADO, x0:x0 + LADO]
    ruido = (recorte & (2**BITS_BAJOS - 1)) * (255 // (2**BITS_BAJOS - 1))
    final = numeros.reshape(LADO, LADO)
    fig, ejes = plt.subplots(1, 3, figsize=(15, 5.4))
    paneles = [
        (recorte, "Foto (bits altos): se ve la escena"),
        (ruido, f"Bits bajos de la foto ({BITS_BAJOS}): ruido crudo"),
        (final, "160,000 números finales (400x400)"),
    ]
    for eje, (img, titulo) in zip(ejes, paneles):
        eje.imshow(img, cmap="gray", vmin=0, vmax=255, interpolation="nearest")
        eje.set_title(titulo, fontsize=11)
        eje.axis("off")
    fig.tight_layout()
    fig.savefig(salida / "comparacion.png", dpi=110)
    print("\nImágenes: salida/cuadricula_400x400.png, salida/comparacion.png")
    print("Reporte: salida/reporte.txt")


if __name__ == "__main__":
    main()
