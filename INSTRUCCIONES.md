# True RNG: instrucciones del proyecto

Proyecto de clase: un sistema que genera **números verdaderamente aleatorios** (true randomness) en lugar de depender de generadores pseudoaleatorios.
Fecha límite (apuntada en la pizarra): **11 de octubre**. Se trabaja solo o en pareja: _[llenar]_.

## Qué pide el profesor

| # | Entregable | Detalle |
|---|---|---|
| 1 | Generación y pruebas | Muestra inicial de **160,000 números**. Debe superar pruebas estadísticas y una prueba visual en una cuadrícula de **400x400 píxeles**. |
| 2 | Método de captura | Alimentarse de factores físicos o externos (ejemplos: grabar tráfico, tomar una foto, grabar una pizarra). **Nosotros: fotografías.** |
| 3 | Propuesta de escalabilidad | Teórica: cómo mantener el sistema "vivo" generando **un número por segundo durante un año completo**. |
| 4 | Análisis de costos | Presupuesto estimado de mantener esa infraestructura sin interrupción durante el año (mencionar opciones como Cloudflare). |
| 5 | Entrega | Video demostrativo. |

## Reglas del proyecto

- Los números salen de los píxeles de fotografías reales. **Nunca** usar `random()`, `numpy.random` ni ningún PRNG como fuente de los números finales.
- Los bits altos de un píxel describen la escena y no son aleatorios. Se usan los **bits bajos** (ruido del sensor).
- Si se procesan los datos (hash), explicar por qué no los vuelve pseudoaleatorios.
- No afirmar que la muestra "pasa" sin correr las pruebas y mostrar el resultado real.
- Toda cifra de costo lleva moneda y periodicidad (ej. USD/año). Los precios salen de fuentes publicadas; lo no verificado se marca como estimación.

## Cómo funciona el prototipo (Python)

1. `capturar.py` toma una foto con la cámara del iPhone (Continuity Camera) y la guarda en `fotos/`. Índice 0 = iPhone, 1 = cámara del Mac.
2. `generar.py` toma los 2 bits menos significativos de cada byte de la foto, forma un flujo crudo (1,555,200 bytes) y lo corta en 160,000 trozos de 9 bytes (72 bits). De cada trozo toma un byte del SHA-256. Resultado: 160,000 números de 0 a 255.
3. `pruebas.py` corre frecuencia, rachas, chi-cuadrada y correlación entre vecinos, sobre los números finales y sobre el ruido crudo.

```bash
python3 -m venv .venv && .venv/bin/pip install opencv-python numpy pillow scipy matplotlib
.venv/bin/python capturar.py     # foto nueva
.venv/bin/python generar.py      # 160,000 números
.venv/bin/python pruebas.py      # pruebas e imágenes
```

Salidas en `salida/`: `numeros.csv`, `cuadricula_400x400.png`, `comparacion.png`, `reporte.txt`.
La primera vez, macOS pide permiso de cámara para la app desde la que corres Python.

## Estado (≈ 65%)

| Entregable | Avance |
|---|---|
| Captura con fotografías | Hecho |
| 160,000 números + cuadrícula 400x400 | Hecho |
| Pruebas estadísticas | Hecho (4 pruebas); falta la suite NIST completa |
| Escalabilidad (1 número/segundo, 1 año) | Pensada, falta escribirla |
| Análisis de costos | Cifras de Cloudflare reunidas, falta la tabla final |
| Video demostrativo | Pendiente |

### Resultados de la primera corrida

- Números finales: frecuencia p = 0.0945, rachas p = 0.2650, chi-cuadrada p = 0.0397, correlación r = -0.0018, entropía 7.9987 de 8 bits. Todo pasa.
- Ruido crudo (antes del hash): frecuencia y rachas fallan por un sesgo mínimo (50.13% de unos), con 1.9999 de 2 bits de entropía por muestra. Se ven manchas en zonas planas, probablemente por la compresión del video.
- Las pruebas no demuestran la entropía del ruido. Para eso haría falta NIST SP 800-90B.

## Pendiente

1. Escribir la propuesta de escalabilidad: 31,536,000 números al año (~252 MB a 8 bytes). Cámara fija, un número por segundo, envío en lotes por minuto a un Worker de Cloudflare, con D1 y R2.
2. Tabla de costos. Referencias de Cloudflare (documentación oficial): Workers Paid USD 5/mes = USD 60/año; Workers Free USD 0/año con límites diarios. R2 y D1 quedan dentro de lo incluido. Hardware y electricidad: sin verificar.
3. Guion y grabación del video: captura en vivo, generación, pruebas, cuadrícula, escalabilidad y costos.
4. Opcionales: pruebas NIST completas, repetir con varias fotos, subir al repo de GitHub.

## Decisiones tomadas (confirmar con el profesor)

- Cada número es un byte (0-255), así que la cuadrícula de 400x400 tiene un número por celda.
- Cada número sale de 72 bits de ruido de la foto.
