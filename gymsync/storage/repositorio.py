"""Repositorio genérico: mantiene una lista en memoria sincronizada con su archivo binario."""
from pathlib import Path
from typing import Callable, Optional

from gymsync.storage import archivo_binario


class Repositorio:
    def __init__(self, ruta: Path, clave: str):
        """ruta: archivo .dat; clave: nombre del atributo que identifica cada objeto."""
        self.ruta = Path(ruta)
        self.clave = clave
        self._items = archivo_binario.cargar(self.ruta)

    def _guardar(self) -> None:
        archivo_binario.guardar(self._items, self.ruta)

    def todos(self) -> list:
        return list(self._items)

    def cantidad(self) -> int:
        return len(self._items)

    def obtener(self, valor_clave) -> Optional[object]:
        return self.buscar_por(self.clave, valor_clave)

    def buscar_por(self, campo: str, valor) -> Optional[object]:
        """Búsqueda secuencial por cualquier campo (las búsquedas rápidas usan índices ordenados)."""
        for item in self._items:
            if getattr(item, campo) == valor:
                return item
        return None

    def filtrar(self, condicion: Callable[[object], bool]) -> list:
        return [item for item in self._items if condicion(item)]

    def agregar(self, item) -> None:
        if self.obtener(getattr(item, self.clave)) is not None:
            raise ValueError(f"Ya existe un registro con {self.clave} = {getattr(item, self.clave)}.")
        self._items.append(item)
        self._guardar()

    def anexar(self, item) -> None:
        """Agrega sin verificar clave única (para bitácoras como las entradas)."""
        self._items.append(item)
        self._guardar()

    def actualizar(self, item) -> None:
        valor = getattr(item, self.clave)
        for i, actual in enumerate(self._items):
            if getattr(actual, self.clave) == valor:
                self._items[i] = item
                self._guardar()
                return
        raise ValueError(f"No existe un registro con {self.clave} = {valor}.")

    def eliminar(self, valor_clave) -> None:
        item = self.obtener(valor_clave)
        if item is None:
            raise ValueError(f"No existe un registro con {self.clave} = {valor_clave}.")
        self._items.remove(item)
        self._guardar()
