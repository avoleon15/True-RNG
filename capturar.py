"""Captura una foto con la cámara del iPhone (Continuity Camera) y la guarda en fotos/.

Uso:
    .venv/bin/python capturar.py          # usa la cámara 0 (iPhone)
    .venv/bin/python capturar.py 1        # 1 = cámara del Mac
"""
import sys
import time
from pathlib import Path

import cv2

indice = int(sys.argv[1]) if len(sys.argv) > 1 else 0
carpeta = Path(__file__).parent / "fotos"
carpeta.mkdir(exist_ok=True)

cam = cv2.VideoCapture(indice)
if not cam.isOpened():
    sys.exit(f"No se pudo abrir la cámara {indice}. Revisa el permiso de cámara y el índice.")

# La cámara necesita unos fotogramas para ajustar exposición y enfoque.
for _ in range(30):
    cam.read()
    time.sleep(0.05)

ok, frame = cam.read()
cam.release()
if not ok:
    sys.exit("La cámara abrió pero no entregó imagen.")

alto, ancho = frame.shape[:2]
ruta = carpeta / f"foto_{time.strftime('%Y%m%d_%H%M%S')}.png"
cv2.imwrite(str(ruta), frame)  # PNG: sin pérdida, conserva los bits bajos
print(f"Cámara {indice}: {ancho}x{alto} -> {ruta}")
