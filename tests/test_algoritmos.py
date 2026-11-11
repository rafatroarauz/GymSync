import random

from gymsync.algorithms.busqueda import busqueda_binaria
from gymsync.algorithms.ordenamiento import merge_sort


def test_merge_sort_ordena_igual_que_sorted():
    datos = [random.randint(-100, 100) for _ in range(200)]
    assert merge_sort(datos) == sorted(datos)


def test_merge_sort_no_modifica_original_y_casos_borde():
    datos = [3, 1, 2]
    merge_sort(datos)
    assert datos == [3, 1, 2]
    assert merge_sort([]) == []
    assert merge_sort([7]) == [7]


def test_merge_sort_con_key_reverso_y_estable():
    pares = [("b", 1), ("a", 2), ("c", 1), ("d", 2)]
    assert merge_sort(pares, key=lambda p: p[1]) == [("b", 1), ("c", 1), ("a", 2), ("d", 2)]
    assert merge_sort(pares, key=lambda p: p[1], reverso=True) == [("a", 2), ("d", 2), ("b", 1), ("c", 1)]


def test_busqueda_binaria_encuentra_y_falla():
    lista = list(range(0, 100, 2))
    assert busqueda_binaria(lista, 0) == 0
    assert busqueda_binaria(lista, 98) == 49
    assert busqueda_binaria(lista, 50) == 25
    assert busqueda_binaria(lista, 51) == -1
    assert busqueda_binaria([], 1) == -1


def test_busqueda_binaria_con_key():
    socios = [{"id": "A-1001"}, {"id": "A-1002"}, {"id": "A-1005"}]
    assert busqueda_binaria(socios, "A-1005", key=lambda s: s["id"]) == 2
