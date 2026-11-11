"""Merge sort genérico, estable, O(n log n)."""
from typing import Callable


def merge_sort(lista: list, key: Callable = lambda x: x, reverso: bool = False) -> list:
    """Devuelve una NUEVA lista ordenada según key (no modifica la original)."""
    if len(lista) <= 1:
        return list(lista)
    medio = len(lista) // 2
    izquierda = merge_sort(lista[:medio], key, reverso)
    derecha = merge_sort(lista[medio:], key, reverso)
    return _mezclar(izquierda, derecha, key, reverso)


def _mezclar(izquierda: list, derecha: list, key: Callable, reverso: bool) -> list:
    resultado = []
    i = j = 0
    while i < len(izquierda) and j < len(derecha):
        a, b = key(izquierda[i]), key(derecha[j])
        # "<=" en orden ascendente (y ">=" en descendente) mantiene la estabilidad
        tomar_izquierda = a >= b if reverso else a <= b
        if tomar_izquierda:
            resultado.append(izquierda[i])
            i += 1
        else:
            resultado.append(derecha[j])
            j += 1
    resultado.extend(izquierda[i:])
    resultado.extend(derecha[j:])
    return resultado
