# =============================================================================
#   VINCULAR_NPY_DATASET.py
#   ─────────────────────────────────────────────────────────────
#   Conecta automáticamente los archivos .npy de profundidad REALES
#   (capturados con la RealSense) con las imágenes ya exportadas del
#   dataset de Roboflow (train/valid/test).
#
#   Problema que resuelve:
#     Roboflow renombra tus fotos al exportarlas, agregando un sufijo
#     hash: color_20260718_104500.png  →  color_20260718_104500_png.rf.HASH.jpg
#     Por eso el auto-detector de la GUI (que busca "depth_" junto a
#     "color_" en la MISMA carpeta) nunca encuentra el .npy original,
#     que sigue en tu carpeta de capturas con el nombre sin el hash.
#
#   Qué hace este script:
#     1. Recorre dataset/train, dataset/valid, dataset/test
#     2. Para cada imagen color_YYYYMMDD_HHMMSS_png.rf.HASH.jpg
#     3. Busca en tu carpeta de capturas el archivo
#        depth_YYYYMMDD_HHMMSS.npy correspondiente
#     4. Si existe, lo COPIA (no mueve — conserva el original) a la
#        carpeta del dataset con el nombre exacto que espera el
#        auto-detector: depth_YYYYMMDD_HHMMSS_png.rf.HASH.npy
#
#   Resultado: todas las imágenes del dataset que sí tengan su
#   captura de profundidad real quedan con el .npy disponible ahí
#   mismo, sin tener que hacerlo manualmente una por una.
# =============================================================================

import os
import re
import shutil

# ── CONFIGURA ESTAS DOS RUTAS ANTES DE CORRER ────────────────────────────────
RUTA_CAPTURAS = r"D:\Python\CLAUDE\CAPTURA_REALSENSE"
RUTA_DATASET  = r"D:\Python\CLAUDE\DRTCA_ONLY_MTC\dataset"
# ──────────────────────────────────────────────────────────────────────────────

# Si tus .npy están en una subcarpeta "capturas" dentro de DATASET_REALSENSE,
# descomenta la siguiente línea:
# RUTA_CAPTURAS = os.path.join(RUTA_CAPTURAS, "capturas")

PATRON_COLOR = re.compile(r'^color_(\d{8}_\d{6})_png\.rf\.([a-f0-9]+)\.(jpg|jpeg|png)$', re.IGNORECASE)


def vincular_split(carpeta_split, nombre_split):
    """Procesa un split (train/valid/test) y copia los .npy que encuentre."""
    if not os.path.isdir(carpeta_split):
        print(f"  [{nombre_split}] ⚠ Carpeta no encontrada: {carpeta_split}")
        return 0, 0

    encontrados = 0
    no_encontrados = 0
    faltantes = []

    for nombre in sorted(os.listdir(carpeta_split)):
        m = PATRON_COLOR.match(nombre)
        if not m:
            continue

        timestamp = m.group(1)      # ej. "20260718_104500"
        hash_rf   = m.group(2)      # ej. "d2ee43afedd36359511a7e497b0fcb47"

        ruta_npy_original = os.path.join(RUTA_CAPTURAS, f"depth_{timestamp}.npy")

        if os.path.isfile(ruta_npy_original):
            nombre_npy_destino = f"depth_{timestamp}_png.rf.{hash_rf}.npy"
            ruta_destino = os.path.join(carpeta_split, nombre_npy_destino)

            if not os.path.isfile(ruta_destino):
                shutil.copy2(ruta_npy_original, ruta_destino)
            encontrados += 1
        else:
            no_encontrados += 1
            faltantes.append(timestamp)

    print(f"  [{nombre_split}] ✓ Vinculados: {encontrados}  |  ✗ Sin .npy real: {no_encontrados}")
    if faltantes and len(faltantes) <= 15:
        print(f"      Timestamps sin .npy: {', '.join(faltantes)}")
    elif faltantes:
        print(f"      Timestamps sin .npy (primeros 15 de {len(faltantes)}): {', '.join(faltantes[:15])}")

    return encontrados, no_encontrados


def main():
    print("=" * 60)
    print("  VINCULACIÓN DE PROFUNDIDAD REAL — dataset PAVESCAN")
    print("=" * 60)
    print(f"  Carpeta de capturas (.npy reales): {RUTA_CAPTURAS}")
    print(f"  Carpeta del dataset (Roboflow):    {RUTA_DATASET}")
    print("=" * 60)

    if not os.path.isdir(RUTA_CAPTURAS):
        print(f"\n❌ ERROR: no existe la carpeta de capturas: {RUTA_CAPTURAS}")
        print("   Ajusta la variable RUTA_CAPTURAS al inicio del script.")
        return

    if not os.path.isdir(RUTA_DATASET):
        print(f"\n❌ ERROR: no existe la carpeta del dataset: {RUTA_DATASET}")
        print("   Ajusta la variable RUTA_DATASET al inicio del script.")
        return

    total_ok, total_faltan = 0, 0
    for split in ["train", "valid", "test"]:
        carpeta = os.path.join(RUTA_DATASET, split)
        ok, faltan = vincular_split(carpeta, split)
        total_ok += ok
        total_faltan += faltan

    print("=" * 60)
    print(f"  TOTAL: {total_ok} imágenes ahora tienen profundidad real")
    print(f"         {total_faltan} imágenes no tienen .npy original disponible")
    print("=" * 60)


if __name__ == "__main__":
    main()
