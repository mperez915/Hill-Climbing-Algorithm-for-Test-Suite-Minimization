"""
Test Suite Minimization - Hill Climbing Algorithm

Módulos principales:
- hill_climbing: Clase TestSuiteMinimizer para el algoritmo principal
- preprocessing: Modos A, B y C de preprocesamiento
- experimental_design: Diseño experimental con múltiples semillas y estadísticas
- utils: Funciones auxiliares
"""

from .experimental_design import ExperimentalDesign
from .hill_climbing_optimizer import HillClimbingOptimizer
from .preprocessing import PreprocessingModes
from .test_suite_minimizer import TestSuiteMinimizer
from .utils import (
    calculate_coverage_percentage,
    check_full_coverage,
    find_critical_requirements,
    get_essential_tests,
    list_available_matrices,
)

__all__ = [
    "TestSuiteMinimizer",
    "HillClimbingOptimizer",
    "PreprocessingModes",
    "ExperimentalDesign",
    "find_critical_requirements",
    "get_essential_tests",
    "calculate_coverage_percentage",
    "check_full_coverage",
    "list_available_matrices",
]
