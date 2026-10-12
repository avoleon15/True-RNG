# True RNG: instrucciones del proyecto

Proyecto de clase: un sistema que genera **números verdaderamente aleatorios** (true randomness) en lugar de depender de generadores pseudoaleatorios.
Fecha límite (apuntada en la pizarra): **11 de octubre**. Se trabaja solo o en pareja: _[llenar]_.

## Qué pide el profesor

| # | Entregable | Detalle |
|---|---|---|
| 1 | Generación y pruebas | Muestra inicial de **160,000 números**. Debe superar pruebas estadísticas y una prueba visual en una cuadrícula de **400x400 píxeles**. |
| 2 | Método de captura | Alimentarse de factores físicos o externos (ejemplos: grabar tráfico, tomar una foto, grabar una pizarra). **Nosotros: ruido del micrófono.** |
| 3 | Propuesta de escalabilidad | Teórica: cómo mantener el sistema "vivo" generando **un número por segundo durante un año completo**. |
| 4 | Análisis de costos | Presupuesto estimado de mantener esa infraestructura sin interrupción durante el año (mencionar opciones como Cloudflare). |
| 5 | Entrega | Video demostrativo. |

## Reglas del proyecto

- Los números salen del ruido del micrófono. **Nunca** usar `random()`, `numpy.random` ni ningún PRNG como fuente de los números finales.
- La fuente física es el ruido térmico (eléctrico) del micrófono y su circuito. Se usa el audio crudo, sin supresión de ruido.
- Si se procesan los datos (hash), explicar por qué no los vuelve pseudoaleatorios.
- No afirmar que la muestra "pasa" sin correr las pruebas y mostrar el resultado real.
- Toda cifra de costo lleva moneda y periodicidad (ej. USD/año). Los precios salen de fuentes publicadas; lo no verificado se marca como estimación.

## Cómo funciona el prototipo (Python)

Todo está en un solo archivo, `trng_mic.py`:

1. **Grabar.** `obtener_entropia()` graba 30 s de micrófono (mono, `int16`, 48000 Hz). Es la única función que toca la fuente de entropía, para poder sumar otra (por ejemplo, la cámara) después.
2. **Revisar el micrófono.** Avisa si el audio es casi plano o está en ceros (señal de silenciado o supresión de ruido).
3. **Generar.** Parte el audio en bloques de 256 muestras. De cada bloque se calcula SHA-256, que da 32 bytes, es decir, 32 números de 0 a 255. Se repite hasta tener 160,000 números (5,000 bloques) y se guardan en `numeros.txt`.
4. **Pruebas propias.** Frecuencia de bits, chi-cuadrado y rachas (Wald-Wolfowitz).
5. **Imágenes.** `cuadricula_400x400.png` (números finales: blanco si ≥ 128) y `cuadricula_sin_hash.png` (bit menos significativo del audio crudo, sin SHA-256) para comparar.

```bash
py -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe trng_mic.py
```

Cada corrida reemplaza `numeros.txt` y las dos imágenes.

### Verificador del profesor

`Verificador_TRNG.ipynb` corre chi-cuadrado, rachas y pares consecutivos, más una prueba visual. La celda de datos ya lee `numeros.txt` con rango 0-255. Necesita `matplotlib` e `ipykernel` además de `requirements.txt`.

```bash
.venv/Scripts/python.exe -m pip install matplotlib ipykernel nbconvert
.venv/Scripts/python.exe -m nbconvert --to notebook --execute --inplace Verificador_TRNG.ipynb
```

## Estado

| Entregable | Avance |
|---|---|
| Captura con micrófono | Hecho |
| 160,000 números + cuadrícula 400x400 | Hecho |
| Pruebas estadísticas (verificador del profesor) | Hecho: pasa las tres pruebas |
| Observación visual (celda final del notebook) | Pendiente |
| Escalabilidad (1 número/segundo, 1 año) | Falta escribirla |
| Análisis de costos | Cifras de Cloudflare reunidas, falta la tabla final |
| Video demostrativo | Pendiente |

### Resultados con el verificador del profesor (48000 Hz)

| Corrida | Chi cuadrado | Rachas | Pares consecutivos |
|---|---|---|---|
| 1 | p = 0.6698 | p = 0.6496 | p = 0.3021 |
| 2 | p = 0.5963 | p = 0.4295 | p = 0.3178 |
| 3 | p = 0.3070 | p = 0.2045 | p = 0.0228 |

Las tres pasan (nivel 0.01). En la corrida 3 aparecieron 4 hashes repetidos de 5,000.

Las pruebas no demuestran que el ruido del micrófono sea aleatorio: el hash hace que casi cualquier entrada pase. Por eso se compara con `cuadricula_sin_hash.png`. Para demostrar la entropía de la fuente haría falta NIST SP 800-90B.

### Problema encontrado: frecuencia de muestreo

Con el script grabando a 44100 Hz, la prueba de pares consecutivos fallaba (p ≈ 0) porque el audio traía bloques repetidos: entre el 2 % y el 8 % de los hashes salía repetido según la corrida. Windows tiene el micrófono en 48000 Hz y remuestreaba el audio a 44100. Al grabar a la frecuencia nativa (48000 Hz) desaparecieron los repetidos. Si se usa otro equipo, revisar su frecuencia en Configuración → Sonido → Entrada → Formato y ajustar `FS` en `trng_mic.py`.

## Pendiente

1. Escribir la propuesta de escalabilidad: 31,536,000 números al año (~252 MB a 8 bytes). Hay que decidir cómo se capturaría el audio de forma continua (micrófono fijo, un número por segundo), el envío en lotes y el almacenamiento (por ejemplo, un Worker de Cloudflare con D1 y R2).
2. Tabla de costos. Referencias de Cloudflare (documentación oficial): Workers Paid USD 5/mes = USD 60/año; Workers Free USD 0/año con límites diarios. R2 y D1 quedan dentro de lo incluido. Hardware y electricidad: sin verificar.
3. Guion y grabación del video: captura en vivo, generación, pruebas, cuadrículas con y sin hash, escalabilidad y costos.
4. Escribir la observación visual en la celda final del notebook.
5. Opcionales: descartar bloques de audio repetidos antes del hash, pruebas NIST completas, repetir en otro equipo.

## Decisiones tomadas (confirmar con el profesor)

- Cada número es un byte (0-255), así que la cuadrícula de 400x400 tiene un número por celda.
- Cada bloque de 256 muestras de audio produce 32 números (un hash SHA-256).
- El prototipo anterior con fotografías (cámara del iPhone) se quitó del proyecto. Sigue en el historial de git (commit `a4604f7`).
