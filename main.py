import os
from datetime import datetime
from pathlib import Path

from src.experimental_design import ExperimentalDesign


def main():
    """
    Función principal que ejecuta el diseño experimental del algoritmo Hill Climbing.

    Ejecuta experimentos para cada matriz disponible y guarda los resultados
    en archivos individuales en la carpeta 'results/'.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    matrices_dir = os.path.join(script_dir, "matrices")
    results_dir = os.path.join(script_dir, "results")

    # Crear carpeta de resultados si no existe
    Path(results_dir).mkdir(exist_ok=True)

    # Obtener todas las matrices
    matrix_files = sorted([f for f in os.listdir(matrices_dir) if f.endswith(".txt")])

    print(f"\n{'=' * 80}")
    print(f"EJECUCIÓN DE EXPERIMENTOS PARA {len(matrix_files)} MATRICES")
    print(f"{'=' * 80}")
    print(f"Matrices encontradas: {', '.join(matrix_files)}")
    print(f"Carpeta de resultados: {results_dir}")
    print(f"{'=' * 80}\n")

    # Ejecutar experimento para cada matriz
    for i, matrix_filename in enumerate(matrix_files, 1):
        matrix_path = os.path.join(matrices_dir, matrix_filename)
        matrix_name = Path(matrix_filename).stem  # Nombre sin extensión

        # Generar timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Nombre del archivo de salida
        output_filename = f"{matrix_name}_{timestamp}.txt"
        output_path = os.path.join(results_dir, output_filename)

        print(f"\n[{i}/{len(matrix_files)}] Procesando: {matrix_filename}")
        print(f"     Guardando resultados en: {output_filename}")

        # Crear diseño experimental
        experiment = ExperimentalDesign(
            matrix_path=matrix_path,
            max_iterations=1000,
            initial_strategy="random",  # Opciones: "all", "greedy", "essential", "random"
        )

        # Redirigir salida a archivo
        with open(output_path, "w", encoding="utf-8") as f:
            # Escribir encabezado
            f.write(f"{'=' * 80}\n")
            f.write(f"RESULTADOS EXPERIMENTALES - {matrix_filename}\n")
            f.write(
                f"Fecha de ejecución: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            f.write(f"{'=' * 80}\n\n")

            # Guardar stdout original
            import sys

            original_stdout = sys.stdout

            try:
                # Redirigir stdout al archivo
                sys.stdout = f

                # Ejecutar experimento
                print(">>> Ejecutando experimento con múltiples semillas...")
                results = experiment.run_multiple_experiments(
                    seeds=[42, 123, 456, 789, 1024],  # Al menos 5 semillas distintas
                    mode="B",  # Opciones: "A", "B", "C"
                    verbose=False,  # True para ver detalles de cada ejecución
                )

                # Imprimir reporte estadístico
                experiment.print_statistics_report(results)

            finally:
                # Restaurar stdout
                sys.stdout = original_stdout

        print(f"     ✓ Completado: {output_filename}")

    print(f"\n{'=' * 80}")
    print(f"✓ TODOS LOS EXPERIMENTOS COMPLETADOS")
    print(f"{'=' * 80}")
    print(f"Resultados guardados en: {results_dir}/")
    print(f"Total de archivos generados: {len(matrix_files)}")
    print(f"{'=' * 80}\n")


if __name__ == "__main__":
    main()
