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
