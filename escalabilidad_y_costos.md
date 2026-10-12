##ESCALABILIDAD##

Propuesta de escalabidad:

Para generar un número por segundo durante un año (31,536,000 números, unos 86,400 por día), se propone un dispositivo fijo y siempre encendido, por ejemplo una Raspberry Pi con micrófono USB, que graba audio crudo, sin supresión de ruido ni control automático de ganancia, y a la frecuencia nativa del micrófono para evitar el remuestreo que nos dio problemas. Cada segundo se pasa una ventana de audio por SHA-256 y se obtiene un byte (0-255). Como un segundo de audio contiene mucho más ruido del que se consume, queda margen si alguna parte sale mala. Cada ventana se revisa con controles de salud (desviación estándar, porcentaje de ceros y bloques repetidos), y se descarta si falla, con una alerta. Además, cada dos días, cuando se acumulan unos 160,000 números, se corre un verificador para saber que todo esté yendo normal. Los números se envían en lotes de 60 por minuto por HTTPS a un Worker de Cloudflare, que los guarda en D1 y en archivos diarios en R2; si se cae el internet, el dispositivo los guarda en disco y los reenvía cuando vuelva la conexión. Para que funcione sin interrupción se usa arranque automático con reinicio ante fallas, una fuente de respaldo (UPS), un segundo dispositivo en espera y monitoreo que avise si un lote no llega. El volumen es pequeño: unos 31.5 MB al año con un byte por número y unas 525,600 peticiones al año. Queda como límite que la entropía real por ventana de audio no se ha medido, y para demostrarla haría falta una prueba como NIST SP 800-90B.

##COSTOS##

Presupuesto estimado para mantener el sistema un año completo sin interrupción. Todas las cifras están en USD. Las marcadas como *fuente* salen de la documentación oficial consultada el 11 de octubre de 2026. Las marcadas como *estimación* **no están verificadas**: son supuestos que hay que reemplazar por una cotización real.

### Infraestructura en la nube (Cloudflare)

| Concepto | Límite o precio publicado | Nuestro uso | Costo |
|---|---|---|---|
| Workers, plan Free | 100,000 peticiones por día | 1,440 por día | USD 0/año (fuente) |
| D1, plan Free | 100,000 filas escritas por día, 5 GB de almacenamiento | 1,440 filas por día, ~0.03 GB | USD 0/año (fuente) |
| R2, capa gratuita | 10 GB-mes de almacenamiento, 1 millón de operaciones Clase A y 10 millones de Clase B por mes | ~0.03 GB, menos de 50,000 escrituras por mes | USD 0/año (fuente) |
| Workers Paid (opcional) | mínimo USD 5/mes por cuenta, con 10 millones de peticiones al mes incluidas | 43,200 peticiones por mes | USD 60/año (fuente) |

El plan Free alcanza con mucho margen. Su desventaja es que, si se llegara al límite diario, las operaciones fallan hasta el siguiente día, así que el plan Paid es una opción de tranquilidad y no una necesidad. Importante: guardar **una fila por lote** y no una por número, porque 86,400 filas por día quedaría a solo el 86 % del límite gratuito de D1.

### Hardware (una sola vez)

Se contemplan dos equipos: uno principal y otro en espera.

| Concepto | Cantidad | Costo unitario | Total | Estado |
|---|---|---|---|---|
| Raspberry Pi Zero 2 W | 2 | USD 15 | USD 30 | fuente |
| Micrófono USB | 2 | USD 15 | USD 30 | estimación |
| Fuente de alimentación | 2 | USD 10 | USD 20 | estimación |
| Tarjeta microSD | 2 | USD 10 | USD 20 | estimación |
| UPS pequeño (respaldo de energía) | 1 | USD 40 | USD 40 | estimación |
| **Subtotal hardware** | | | **USD 140** | |

Si se prefiere una Raspberry Pi 4 (desde USD 35 según la página oficial) el subtotal sube unos USD 40.

### Electricidad (anual)

El consumo de la Raspberry Pi no aparece en las páginas oficiales consultadas, así que se calcula con un supuesto:

costo anual = vatios × 8,760 horas ÷ 1,000 × tarifa por kWh

Con el supuesto de **5 W** por equipo y **USD 0.15 por kWh** (ambos *estimación*): 5 × 8,760 ÷ 1,000 = 43.8 kWh al año, que son unos USD 6.57 por equipo, o **unos USD 13 al año** con los dos encendidos.

Se asume que ya existe una conexión a internet en el lugar, así que su costo adicional se toma como USD 0.

### Resumen del primer año

| Escenario | Hardware (una vez) | Cloudflare | Electricidad | Total primer año |
|---|---|---|---|---|
| Con plan Free | USD 140 | USD 0 | USD 13 | **≈ USD 153** |
| Con Workers Paid | USD 140 | USD 60 | USD 13 | **≈ USD 213** |

Desde el segundo año el costo baja a unos USD 13 con plan Free, o USD 73 con Workers Paid, siempre que el hardware no se tenga que reemplazar.

De todo el presupuesto, solo las cifras de Cloudflare y el precio de la Raspberry Pi Zero 2 W (USD 30 en total) vienen de una fuente publicada. El resto de la tabla hay que cotizarlo antes de presentarlo.

### Fuentes

- Workers: https://developers.cloudflare.com/workers/platform/pricing/
- D1: https://developers.cloudflare.com/d1/platform/pricing/
- R2: https://developers.cloudflare.com/r2/pricing/
- Raspberry Pi Zero 2 W: https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/
- Raspberry Pi 4: https://www.raspberrypi.com/products/raspberry-pi-4-model-b/

