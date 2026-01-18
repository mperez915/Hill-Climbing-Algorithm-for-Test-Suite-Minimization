"""
Script de prueba para verificar la configuración del proyecto
"""

import os
import sys

# Añadir el directorio src al path si es necesario
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from hill_climbing import TestSuiteMinimizer
from utils import (
    calculate_coverage_percentage,
    get_essential_tests,
    list_available_matrices,
)


def test_configuration():
    """Prueba que todo está configurado correctamente"""
    print("=" * 60)
    print("TEST DE CONFIGURACIÓN DEL PROYECTO")
    print("=" * 60)

    # Verificar que podemos listar las matrices
    print("\n1. Listando matrices disponibles...")
    matrices = list_available_matrices()
    print(f"   ✓ Encontradas {len(matrices)} matrices:")
    for matrix in matrices:
        print(f"     - {os.path.basename(matrix)}")

    if not matrices:
        print("   ✗ ERROR: No se encontraron matrices")
        return False

    # Probar cargar una matriz
    print(f"\n2. Cargando matriz: {os.path.basename(matrices[0])}")
    minimizer = TestSuiteMinimizer(matrices[0])
    matrix = minimizer.load_matrix()
    print(f"   ✓ Matriz cargada correctamente")

    # Probar las utilidades
    print("\n3. Probando funciones de utilidad...")
    essential = get_essential_tests(matrix)
    print(f"   ✓ Tests esenciales encontrados: {len(essential)}")

    coverage = calculate_coverage_percentage(matrix, list(range(matrix.shape[1])))
    print(f"   ✓ Cobertura total: {coverage:.2f}%")

    print("\n" + "=" * 60)
    print("✓ TODAS LAS PRUEBAS PASARON CORRECTAMENTE")
    print("=" * 60)
    print("\nEl proyecto está configurado correctamente y listo para usar.")
    print(f"Python: {sys.executable}")
    print(f"Directorio de trabajo: {os.getcwd()}")

    return True


if __name__ == "__main__":
    try:
        success = test_configuration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
