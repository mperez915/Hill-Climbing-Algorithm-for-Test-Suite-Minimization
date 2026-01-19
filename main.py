import os

from src.experimental_design import ExperimentalDesign


def main():
    """
    Función principal que ejecuta el diseño experimental del algoritmo Hill Climbing.

    Opciones de ejecución:
    1. Experimento con múltiples semillas (recomendado): run_multiple_experiments()
    2. Experimento determinista (semilla fija): run_deterministic_experiment()
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    matrix_file = os.path.join(script_dir, "matrices", "matrix_7_60_1.txt")

    # Crear diseño experimental
    experiment = ExperimentalDesign(
        matrix_path=matrix_file,
        max_iterations=1000,
        initial_strategy="random",  # Opciones: "all", "greedy", "essential", "random"
    )

    # OPCIÓN 1: Ejecutar con múltiples semillas (al menos 5)
    # Se reportan: media, mínimo, máximo, desviación estándar y tiempo de ejecución
    print("\n>>> Ejecutando experimento con múltiples semillas...")
    results = experiment.run_multiple_experiments(
        seeds=[42, 123, 456, 789, 1024],  # Al menos 5 semillas distintas
        mode="A",  # Opciones: "A", "B", "C"
        verbose=False,  # True para ver detalles de cada ejecución
    )

    # Imprimir reporte estadístico
    experiment.print_statistics_report(results)

    # OPCIÓN 2: Si el algoritmo es determinista, usar una sola semilla
    # Descomentar las siguientes líneas para usar esta opción:
    # print("\n>>> Ejecutando experimento determinista...")
    # result = experiment.run_deterministic_experiment(seed=42, mode="A")


if __name__ == "__main__":
    main()
