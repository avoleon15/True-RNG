# True-RNG

Generador de números verdaderamente aleatorios (TRNG) que usa el **ruido del micrófono** como fuente física. Produce 160,000 números (0-255), los prueba estadísticamente y los muestra como una imagen de 400×400 píxeles.

## Cómo funciona

1. Graba 30 s de audio crudo del micrófono (mono, 16 bits, 48000 Hz).
2. Corta el audio en bloques de 256 muestras. Cada bloque pasa por SHA-256, que da 32 bytes (32 números de 0 a 255).
3. Repite hasta juntar 160,000 números y los guarda en `numeros.txt`.

El ruido térmico del micrófono es la fuente de aleatoriedad. SHA-256 solo elimina sesgos: reparte los bits de forma uniforme, pero no inventa entropía.

## Cómo correrlo

Requiere Python 3 y un micrófono. Desde esta carpeta:

```bash
py -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe trng_mic.py
```

La frecuencia de muestreo (`FS` en `trng_mic.py`) debe coincidir con la del micrófono en Windows (Configuración → Sonido → Entrada → Formato). Si no, Windows remuestrea el audio y aparecen bloques repetidos que hacen fallar las pruebas.

## Archivos

| Archivo | Qué es |
|---|---|
| `trng_mic.py` | Todo el generador: graba, genera, prueba y dibuja. |
| `numeros.txt` | Los 160,000 números, uno por línea. |
| `cuadricula_400x400.png` | Números finales como imagen (blanco si ≥ 128). Debe verse como estática. |
| `cuadricula_sin_hash.png` | Audio crudo sin SHA-256, para comparar. |
| `Verificador_TRNG.ipynb` | Verificador del profesor: chi cuadrado, rachas y pares consecutivos. |
| `escalabilidad_y_costos.md` | Propuesta de un número por segundo durante un año y su presupuesto. |
| `INSTRUCCIONES.md` | Requisitos del proyecto, estado y pendientes. |

Cada corrida reemplaza `numeros.txt` y las dos imágenes.

## Verificar los resultados

El notebook necesita librerías extra:

```bash
.venv/Scripts/python.exe -m pip install matplotlib ipykernel nbconvert
.venv/Scripts/python.exe -m nbconvert --to notebook --execute --inplace Verificador_TRNG.ipynb
```

Con 48000 Hz, las tres pruebas pasaron en tres corridas seguidas (nivel 0.01). Pasar las pruebas no demuestra que la fuente sea aleatoria: por eso se compara con la imagen sin hash.
