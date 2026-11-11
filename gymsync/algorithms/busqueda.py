"""Búsqueda binaria genérica, O(log n) (RNF2)."""
from typing import Callable


def busqueda_binaria(lista_ordenada: list, clave, key: Callable = lambda x: x) -> int:
    """Devuelve el índice del elemento cuya key es igual a clave, o -1 si no está.
    La lista debe estar ordenada ascendentemente por esa misma key."""
    inicio, fin = 0, len(lista_ordenada) - 1
    while inicio <= fin:
        medio = (inicio + fin) // 2
        valor = key(lista_ordenada[medio])
        if valor == clave:
            return medio
        if valor < clave:
            inicio = medio + 1
        else:
            fin = medio - 1
    return -1
