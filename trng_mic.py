"""Generador de números verdaderamente aleatorios con el micrófono.

Idea: el ruido térmico del micrófono (y del circuito) es impredecible, así que
sirve como fuente física de entropía. Ese ruido puede tener sesgos, por eso
se pasa por SHA-256, que reparte los bits de forma uniforme (whitening).
"""
import hashlib

import numpy as np
import sounddevice as sd
from PIL import Image
from scipy import stats

FS = 44100          # frecuencia de muestreo (Hz)
SEGUNDOS = 30       # duración de cada grabación
CANTIDAD = 160_000  # números a generar (400 x 400)
BLOQUE = 256        # muestras de audio por cada hash
ALFA = 0.01         # umbral de las pruebas


def obtener_entropia():
    """Graba el micrófono y devuelve el audio crudo (numpy array int16)."""
    print("Grabando...")
    audio = sd.rec(FS * SEGUNDOS, samplerate=FS, channels=1, dtype="int16")
    sd.wait()
    print("Listo")
    return audio.reshape(-1)


def revisar_microfono(audio):
    """Avisa si el micrófono parece silenciado o con supresión de ruido."""
    if audio.std() < 0.5 or np.mean(audio == 0) > 0.9:
        print("ADVERTENCIA: El micrófono parece tener supresión de ruido o está silenciado")


def generar_numeros(audio):
    """SHA-256 de cada bloque de audio -> 32 números (0-255) por bloque."""
    numeros = bytearray()
    pos = 0
    while len(numeros) < CANTIDAD:
        if pos + BLOQUE > len(audio):  # se acabó el audio: grabar más
            audio = np.concatenate([audio, obtener_entropia()])
        bloque = audio[pos:pos + BLOQUE]
        numeros += hashlib.sha256(bloque.tobytes()).digest()
        pos += BLOQUE
    return np.frombuffer(bytes(numeros[:CANTIDAD]), dtype=np.uint8)


def pruebas(numeros):
    bits = np.unpackbits(numeros)
    n = len(bits)

    # Frecuencia de bits
    unos = bits.sum()
    print(f"\nFrecuencia de bits: {100 * (n - unos) / n:.2f}% ceros, {100 * unos / n:.2f}% unos")

    # Chi-cuadrado sobre los 256 valores
    p = stats.chisquare(np.bincount(numeros, minlength=256)).pvalue
    print(f"Chi-cuadrado: p = {p:.4f}  {'PASA' if p > ALFA else 'FALLA'}")

    # Prueba de rachas (Wald-Wolfowitz) sobre los bits
    n1, n0 = int(unos), int(n - unos)
    rachas = 1 + int(np.count_nonzero(bits[1:] != bits[:-1]))
    esperadas = 2 * n1 * n0 / n + 1
    varianza = 2 * n1 * n0 * (2 * n1 * n0 - n) / (n**2 * (n - 1))
    z = (rachas - esperadas) / np.sqrt(varianza)
    p = 2 * stats.norm.sf(abs(z))
    print(f"Rachas: {rachas} observadas, {esperadas:.0f} esperadas, z = {z:.3f}, p = {p:.4f}  {'PASA' if p > ALFA else 'FALLA'}")


def guardar_imagen(matriz_bool, nombre):
    """Blanco donde es True, negro donde es False."""
    Image.fromarray(matriz_bool.astype(np.uint8) * 255).save(nombre)


def main():
    audio = obtener_entropia()
    revisar_microfono(audio)

    numeros = generar_numeros(audio)
    np.savetxt("numeros.txt", numeros, fmt="%d")
    print(f"Se guardaron {len(numeros):,} números en numeros.txt")

    pruebas(numeros)

    # Imagen con SHA-256: blanco si el número es >= 128
    guardar_imagen((numeros >= 128).reshape(400, 400), "cuadricula_400x400.png")
    # Comparación sin hash: bit menos significativo del audio crudo
    guardar_imagen((audio[:CANTIDAD] & 1).astype(bool).reshape(400, 400), "cuadricula_sin_hash.png")
    print("Imágenes: cuadricula_400x400.png, cuadricula_sin_hash.png")


if __name__ == "__main__":
    main()
