"""Respaldo de la carpeta de datos (RF7)."""
import shutil
from datetime import datetime
from pathlib import Path


def respaldar(carpeta_datos: Path, carpeta_respaldos: Path, ahora: datetime | None = None) -> Path:
    """Copia todos los .dat a backups/AAAA-MM-DD_HHMMSS/ y devuelve la ruta creada."""
    carpeta_datos = Path(carpeta_datos)
    if not carpeta_datos.exists() or not any(carpeta_datos.glob("*.dat")):
        raise ValueError("No hay datos que respaldar todavía.")
    ahora = ahora or datetime.now()
    destino = Path(carpeta_respaldos) / ahora.strftime("%Y-%m-%d_%H%M%S")
    destino.mkdir(parents=True, exist_ok=False)
    for archivo in carpeta_datos.glob("*.dat"):
        shutil.copy2(archivo, destino / archivo.name)
    return destino
