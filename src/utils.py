"""
Funciones auxiliares para el algoritmo de Test Suite Minimization
"""

from pathlib import Path

import numpy as np


def find_critical_requirements(coverage_matrix):
    """
    Identifica requisitos críticos (cubiertos por un solo test).

    Args:
        coverage_matrix (numpy.ndarray): Matriz de cobertura

    Returns:
        numpy.ndarray: Índices de los requisitos críticos
    """
    req_coverage = np.sum(coverage_matrix, axis=1)
    critical = np.where(req_coverage == 1)[0]
    return critical


def get_essential_tests(coverage_matrix):
    """
    Identifica tests esenciales (que cubren requisitos críticos).

    Args:
        coverage_matrix (numpy.ndarray): Matriz de cobertura

    Returns:
        set: Conjunto de índices de tests esenciales
    """
    critical_reqs = find_critical_requirements(coverage_matrix)
    essential_tests = set()

    for req_idx in critical_reqs:
        # Encontrar qué test cubre este requisito crítico
        test_idx = np.where(coverage_matrix[req_idx, :] == 1)[0][0]
        essential_tests.add(test_idx)

    return essential_tests


def calculate_coverage_percentage(coverage_matrix, test_subset):
    """
    Calcula el porcentaje de requisitos cubiertos por un subconjunto de tests.

    Args:
        coverage_matrix (numpy.ndarray): Matriz de cobertura completa
        test_subset (list): Índices de los tests en el subconjunto

    Returns:
        float: Porcentaje de cobertura (0-100)
    """
    if len(test_subset) == 0:
        return 0.0

    # Seleccionar solo las columnas de los tests en el subconjunto
    subset_matrix = coverage_matrix[:, test_subset]

    # Un requisito está cubierto si al menos un test lo cubre
    covered_requirements = np.sum(subset_matrix, axis=1) > 0

    total_requirements = coverage_matrix.shape[0]
    covered_count = np.sum(covered_requirements)

    return (covered_count / total_requirements) * 100


def check_full_coverage(coverage_matrix, test_subset):
    """
    Verifica si un subconjunto de tests cubre todos los requisitos.

    Args:
        coverage_matrix (numpy.ndarray): Matriz de cobertura completa
        test_subset (list): Índices de los tests en el subconjunto

    Returns:
        bool: True si cubre todos los requisitos, False en caso contrario
    """
    return calculate_coverage_percentage(coverage_matrix, test_subset) == 100.0


def list_available_matrices(matrices_dir=None):
    """
    Lista todas las matrices disponibles en el directorio.

    Args:
        matrices_dir (str): Ruta al directorio de matrices (opcional)

    Returns:
        list: Lista de rutas a los archivos de matriz
    """
    if matrices_dir is None:
        # Usar rutas absolutas desde el directorio del script
        import os

        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        matrices_dir = os.path.join(project_root, "matrices")

    matrices_path = Path(matrices_dir)
    if not matrices_path.exists():
        print(f"El directorio {matrices_dir} no existe")
        return []

    matrix_files = sorted(matrices_path.glob("matrix_*.txt"))
    return [str(f) for f in matrix_files]


def calculate_tssr(original_size, minimized_size):
    """
    Calcula la métrica TSSR (Test Suite Size Reduction).

    TSSR mide la reducción en el tamaño del conjunto de tests.
    Un valor más alto indica mayor reducción.

    Fórmula: TSSR = 1 - |S|/|T|
    Donde:
        |S| = tamaño del conjunto minimizado
        |T| = tamaño del conjunto original

    Args:
        original_size (int): Número de tests en el conjunto original |T|
        minimized_size (int): Número de tests en el conjunto minimizado |S|

    Returns:
        float: Valor de TSSR entre 0 y 1 (0 = sin reducción, 1 = reducción total)

    Examples:
        >>> calculate_tssr(100, 50)  # 50% de reducción
        0.5
        >>> calculate_tssr(100, 10)  # 90% de reducción
        0.9
    """
    if original_size == 0:
        return 0.0

    tssr = 1 - (minimized_size / original_size)
    return tssr


def calculate_fdcloss(coverage_matrix, original_tests, minimized_tests):
    """
    Calcula la métrica FDCLOSS (Fault Detection Capability Loss).

    FDCLOSS mide la pérdida de cobertura de requisitos entre el conjunto
    original y el minimizado. Un valor más bajo es mejor.

    Fórmula: FDCLOSS = 1 - |U(S)|/|U(T)|
    Donde:
        |U(S)| = requisitos cubiertos por el conjunto minimizado
        |U(T)| = requisitos cubiertos por el conjunto original

    Args:
        coverage_matrix (numpy.ndarray): Matriz de cobertura completa
        original_tests (list): Índices de los tests en el conjunto original
        minimized_tests (list): Índices de los tests en el conjunto minimizado

    Returns:
        float: Valor de FDCLOSS entre 0 y 1 (0 = sin pérdida, 1 = pérdida total)
              Idealmente debe ser 0.0 (sin pérdida de cobertura)

    Examples:
        >>> # Si ambos conjuntos cubren lo mismo: FDCLOSS = 0
        >>> calculate_fdcloss(matrix, [0,1,2], [0,1])  # Ambos cubren 100%
        0.0
        >>> # Si el minimizado cubre menos: FDCLOSS > 0
        >>> calculate_fdcloss(matrix, [0,1,2], [0])  # Pierde cobertura
        0.33
    """
    # Calcular requisitos cubiertos por el conjunto original
    if len(original_tests) == 0:
        return 1.0  # Pérdida total si no hay tests originales

    original_matrix = coverage_matrix[:, original_tests]
    original_covered = np.sum(original_matrix, axis=1) > 0
    u_t = np.sum(original_covered)  # |U(T)|

    if u_t == 0:
        return 0.0  # No hay requisitos cubiertos originalmente

    # Calcular requisitos cubiertos por el conjunto minimizado
    if len(minimized_tests) == 0:
        return 1.0  # Pérdida total si no hay tests minimizados

    minimized_matrix = coverage_matrix[:, minimized_tests]
    minimized_covered = np.sum(minimized_matrix, axis=1) > 0
    u_s = np.sum(minimized_covered)  # |U(S)|

    # Calcular FDCLOSS
    fdcloss = 1 - (u_s / u_t)
    return fdcloss


def calculate_metrics(coverage_matrix, original_tests, minimized_tests):
    """
    Calcula todas las métricas de evaluación para TSM.

    Args:
        coverage_matrix (numpy.ndarray): Matriz de cobertura completa
        original_tests (list): Índices de los tests en el conjunto original
        minimized_tests (list): Índices de los tests en el conjunto minimizado

    Returns:
        dict: Diccionario con las métricas calculadas:
            - tssr: Test Suite Size Reduction (0-1, mayor es mejor)
            - fdcloss: Fault Detection Capability Loss (0-1, menor es mejor)
            - original_size: Tamaño del conjunto original
            - minimized_size: Tamaño del conjunto minimizado
            - reduction_count: Número de tests eliminados
            - reduction_percentage: Porcentaje de reducción (0-100%)
    """
    original_size = len(original_tests)
    minimized_size = len(minimized_tests)

    tssr = calculate_tssr(original_size, minimized_size)
    fdcloss = calculate_fdcloss(coverage_matrix, original_tests, minimized_tests)

    return {
        "tssr": tssr,
        "fdcloss": fdcloss,
        "original_size": original_size,
        "minimized_size": minimized_size,
        "reduction_count": original_size - minimized_size,
        "reduction_percentage": tssr * 100,
    }
