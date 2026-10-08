"""Genera 160,000 números (bytes 0-255) a partir del ruido de una fotografía.

Pasos:
  1. Lee la foto (por defecto la más reciente de fotos/).
  2. Se queda con los 2 bits menos significativos de cada byte de la imagen
     (ruido del sensor; los bits altos solo describen la escena).
  3. Empaqueta esos bits en bytes ("flujo crudo").
  4. Divide el flujo crudo en 160,000 trozos iguales y de cada trozo toma un
     byte de su SHA-256. Cada número sale de ~77 bits crudos, no de una semilla.

Uso:
    .venv/bin/python generar.py                  # foto más reciente
    .venv/bin/python generar.py fotos/foto_X.png
"""
import hashlib
import sys
from pathlib import Path

import cv2
import numpy as np

N = 160_000      # cantidad de números que pide el profesor
LADO = 400       # cuadrícula visual: 400 x 400 = 160,000
BITS_BAJOS = 2   # cuántos bits menos significativos se aprovechan por byte

raiz = Path(__file__).parent
salida = raiz / "salida"


def foto_mas_reciente() -> Path:
    fotos = sorted((raiz / "fotos").glob("*.png"))
    if not fotos:
        sys.exit("No hay fotos en fotos/. Corre primero capturar.py")
    return fotos[-1]


def flujo_crudo(imagen: np.ndarray) -> np.ndarray:
    """Bits bajos de todos los bytes de la imagen, empaquetados en bytes."""
    datos = imagen.reshape(-1)
    bajos = datos & (2**BITS_BAJOS - 1)
    por_byte = 8 // BITS_BAJOS
    usable = len(bajos) - len(bajos) % por_byte
    grupos = bajos[:usable].reshape(-1, por_byte)
    crudo = np.zeros(len(grupos), dtype=np.uint8)
    for i in range(por_byte):
        crudo |= (grupos[:, i] << (BITS_BAJOS * i)).astype(np.uint8)
    return crudo


def condensar(crudo: np.ndarray, n: int = N) -> np.ndarray:
    """n números: el primer byte del SHA-256 de cada trozo del flujo crudo."""
    trozo = len(crudo) // n
    if trozo < 8:
        sys.exit("La foto es muy pequeña para producir tantos números con margen.")
    numeros = np.empty(n, dtype=np.uint8)
    for i in range(n):
        numeros[i] = hashlib.sha256(crudo[i * trozo:(i + 1) * trozo].tobytes()).digest()[0]
    return numeros


def main() -> None:
    ruta = Path(sys.argv[1]) if len(sys.argv) > 1 else foto_mas_reciente()
    imagen = cv2.imread(str(ruta))
    if imagen is None:
        sys.exit(f"No se pudo leer {ruta}")
    alto, ancho = imagen.shape[:2]

    crudo = flujo_crudo(imagen)
    numeros = condensar(crudo)

    salida.mkdir(exist_ok=True)
    np.save(salida / "numeros.npy", numeros)
    np.save(salida / "crudo.npy", crudo)
    np.savetxt(salida / "numeros.csv", numeros, fmt="%d")
    cv2.imwrite(str(salida / "cuadricula_400x400.png"), numeros.reshape(LADO, LADO))

    trozo = len(crudo) // N
    print(f"Foto: {ruta.name} ({ancho}x{alto})")
    print(f"Flujo crudo: {len(crudo):,} bytes ({BITS_BAJOS} bits bajos por byte de imagen)")
    print(f"Cada número sale de {trozo} bytes crudos = {trozo * 8} bits")
    print(f"Números generados: {len(numeros):,} (0-255) -> salida/numeros.csv")
    print("Cuadrícula visual -> salida/cuadricula_400x400.png")


if __name__ == "__main__":
    main()
