import os

from src.hill_climbing import TestSuiteMinimizer


def main():
    """
    Función principal para probar la carga de datos.
    """
    # Ejemplo de uso - Usamos rutas absolutas desde el directorio del script

    script_dir = os.path.dirname(os.path.abspath(__file__))
    matrix_file = os.path.join(script_dir, "matrices", "matrix_7_60_1.txt")

    print("\n\nIniciando Test Suite Minimizer...")
    minimizer = TestSuiteMinimizer(matrix_file)

    # Cargar la matriz
    minimizer.load_matrix()

    # Mostrar información
    minimizer.print_matrix_info()


if __name__ == "__main__":
    main()
