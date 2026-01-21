import argparse
import os
from datetime import datetime
from pathlib import Path

from src.experimental_design import ExperimentalDesign


def parse_arguments():
    """
    Parsea los argumentos de línea de comandos.

    Returns:
        argparse.Namespace: Argumentos parseados
    """
    parser = argparse.ArgumentParser(
        description="Hill Climbing Algorithm para Test Suite Minimization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python main.py                                    # Configuración por defecto
  python main.py --mode A --verbose                 # Modo A con salida detallada
  python main.py --mode C --initial-strategy greedy # Modo C con estrategia greedy
  python main.py --seeds 10 20 30 40 50             # Con semillas personalizadas
  python main.py --mode B --seeds 1 2 3 --verbose   # Combinación de parámetros
        """,
    )

    parser.add_argument(
        "--mode",
        type=str,
        choices=["A", "B", "C"],
        default="B",
        help="Modo de preprocesamiento (default: B). A=Reducción de tests, B=Reducción de requisitos, C=Iterativo",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Mostrar información detallada de cada ejecución (default: False)",
    )

    parser.add_argument(
        "--initial-strategy",
        type=str,
        choices=["all", "greedy", "essential", "random"],
        default="random",
        help="Estrategia inicial del algoritmo (default: random)",
    )

    parser.add_argument(
        "--seeds",
        type=int,
        nargs="+",
        default=[42, 123, 456, 789, 1024],
        help="Lista de semillas para múltiples ejecuciones (default: 42 123 456 789 1024)",
    )

    parser.add_argument(
        "--max-iterations",
        type=int,
        default=1000,
        help="Número máximo de iteraciones del algoritmo (default: 1000)",
    )

    parser.add_argument(
        "--no-preprocessing",
        action="store_true",
        help="Ejecutar sin aplicar preprocesamiento a la matriz (default: False)",
    )

    return parser.parse_args()


def main():
    """
    Función principal que ejecuta el diseño experimental del algoritmo Hill Climbing.

    Ejecuta experimentos para cada matriz disponible y guarda los resultados
    en archivos individuales en la carpeta 'results/'.
    """
    # Parsear argumentos de línea de comandos
    args = parse_arguments()

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
    print("\n--- CONFIGURACIÓN ---")
    if args.no_preprocessing:
        print(f"Preprocesamiento: DESACTIVADO")
    else:
        print(f"Modo de preprocesamiento: {args.mode}")
    print(f"Estrategia inicial: {args.initial_strategy}")
    print(f"Semillas: {args.seeds}")
    print(f"Verbose: {args.verbose}")
    print(f"Iteraciones máximas: {args.max_iterations}")
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
            max_iterations=args.max_iterations,
            initial_strategy=args.initial_strategy,
        )

        # Redirigir salida a archivo
        with open(output_path, "w", encoding="utf-8") as f:
            # Escribir encabezado
            f.write(f"{'=' * 80}\n")
            f.write(f"RESULTADOS EXPERIMENTALES - {matrix_filename}\n")
            f.write(
                f"Fecha de ejecución: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            f.write(f"{'=' * 80}\n")
            f.write("Configuración:\n")
            if args.no_preprocessing:
                f.write(f"  - Preprocesamiento: DESACTIVADO\n")
            else:
                f.write(f"  - Modo de preprocesamiento: {args.mode}\n")
            f.write(f"  - Estrategia inicial: {args.initial_strategy}\n")
            f.write(f"  - Semillas: {args.seeds}\n")
            f.write(f"  - Iteraciones máximas: {args.max_iterations}\n")
            f.write(f"  - Verbose: {args.verbose}\n")
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
                    seeds=args.seeds,
                    mode=args.mode,
                    verbose=args.verbose,
                    apply_preprocessing=not args.no_preprocessing,
                )

                # Imprimir reporte estadístico
                experiment.print_statistics_report(results)

            finally:
                # Restaurar stdout
                sys.stdout = original_stdout

        print(f"     ✓ Completado: {output_filename}")

    print(f"\n{'=' * 80}")
    print("✓ TODOS LOS EXPERIMENTOS COMPLETADOS")
    print(f"{'=' * 80}")
    print(f"Resultados guardados en: {results_dir}/")
    print(f"Total de archivos generados: {len(matrix_files)}")
    print(f"{'=' * 80}\n")


if __name__ == "__main__":
    main()
