"""Lectura y escritura de listas de objetos en archivos binarios (pickle)."""
import os
import pickle
from pathlib import Path


class ErrorArchivo(Exception):
    """El archivo de datos existe pero no se puede leer (corrupto o incompatible)."""


def guardar(datos: list, ruta: Path) -> None:
    """Escribe la lista en disco. Primero escribe un archivo temporal y luego lo
    reemplaza, para no dejar el archivo a medias si el programa se cierra."""
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    temporal = ruta.with_suffix(ruta.suffix + ".tmp")
    with open(temporal, "wb") as archivo:
        pickle.dump(datos, archivo)
    os.replace(temporal, ruta)


def cargar(ruta: Path) -> list:
    """Devuelve la lista guardada, o una lista vacía si el archivo aún no existe."""
    ruta = Path(ruta)
    if not ruta.exists():
        return []
    try:
        with open(ruta, "rb") as archivo:
            datos = pickle.load(archivo)
    except (pickle.UnpicklingError, EOFError, AttributeError, ImportError) as error:
        raise ErrorArchivo(f"No se pudo leer '{ruta.name}': archivo dañado ({error}).") from error
    if not isinstance(datos, list):
        raise ErrorArchivo(f"'{ruta.name}' no tiene el formato esperado.")
    return datos
