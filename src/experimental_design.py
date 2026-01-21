"""
Módulo para diseño experimental del algoritmo Hill Climbing.

Permite ejecutar el algoritmo con múltiples semillas y calcular estadísticas
como media, mínimo, máximo, desviación estándar y tiempo de ejecución.
"""

import time
from typing import Dict, List, Literal, Optional

import numpy as np

from src.test_suite_minimizer import TestSuiteMinimizer


class ExperimentalDesign:
    """
    Clase para realizar experimentos con múltiples ejecuciones del algoritmo.
    """

    def __init__(
        self,
        matrix_path: str,
        max_iterations: int = 1000,
        initial_strategy: Literal["all", "greedy", "essential", "random"] = "all",
    ):
        """
        Inicializa el diseño experimental.

        Args:
            matrix_path: Ruta al archivo de matriz de cobertura
            max_iterations: Número máximo de iteraciones para el algoritmo
            initial_strategy: Estrategia inicial para el algoritmo
        """
        self.matrix_path = matrix_path
        self.max_iterations = max_iterations
        self.initial_strategy = initial_strategy

    def run_single_experiment(
        self,
        seed: Optional[int],
        mode: Literal["A", "B", "C"] = "A",
        verbose: bool = False,
        apply_preprocessing: bool = True,
    ) -> Dict:
        """
        Ejecuta una única ejecución del algoritmo con una semilla específica.

        Args:
            seed: Semilla para reproducibilidad (None si es determinista)
            mode: Modo de preprocesamiento
            verbose: Mostrar información detallada
            apply_preprocessing: Si se debe aplicar preprocesamiento (True) o no (False)

        Returns:
            Diccionario con los resultados de la ejecución
        """
        if seed is not None:
            np.random.seed(seed)

        # Crear minimizador
        minimizer = TestSuiteMinimizer(
            self.matrix_path,
            max_iterations=self.max_iterations,
            initial_strategy=self.initial_strategy,
        )

        # Medir tiempo de ejecución
        start_time = time.time()
        result = minimizer.run(mode=mode, apply_preprocessing=apply_preprocessing)
        execution_time = time.time() - start_time

        # Extraer métricas relevantes
        optimization = result["optimization"]

        return {
            "seed": seed,
            "execution_time": execution_time,
            "solution_size": optimization["solution_size"],
            "original_size": optimization["original_size"],
            "reduction": optimization["reduction"],
            "reduction_percentage": optimization["reduction_percentage"],
            "tssr": optimization["tssr"],
            "fdcloss": optimization["fdcloss"],
            "iterations": optimization["iterations"],
            "improvements": optimization["improvements"],
            "coverage": optimization["coverage"],
            "preprocessing": result["preprocessing"],
        }

    def run_multiple_experiments(
        self,
        seeds: Optional[List[int]] = None,
        num_runs: int = 5,
        mode: Literal["A", "B", "C"] = "A",
        verbose: bool = False,
        apply_preprocessing: bool = True,
    ) -> Dict:
        """
        Ejecuta múltiples experimentos con diferentes semillas.

        Args:
            seeds: Lista de semillas (None para usar valores por defecto)
            num_runs: Número de ejecuciones si seeds es None
            mode: Modo de preprocesamiento
            verbose: Mostrar información detallada
            apply_preprocessing: Si se debe aplicar preprocesamiento (True) o no (False)

        Returns:
            Diccionario con estadísticas agregadas y resultados individuales
        """
        # Generar semillas por defecto si no se proporcionan
        if seeds is None:
            seeds = list(range(42, 42 + num_runs))

        if len(seeds) < 5:
            print(
                f"⚠️  Advertencia: Se recomienda usar al menos 5 semillas (actual: {len(seeds)})"
            )

        print(f"\n{'=' * 80}")
        print("DISEÑO EXPERIMENTAL - HILL CLIMBING TEST SUITE MINIMIZATION")
        print(f"{'=' * 80}")
        print(f"Archivo de matriz: {self.matrix_path}")
        print(f"Modo de preprocesamiento: {mode}")
        print(f"Estrategia inicial: {self.initial_strategy}")
        print(f"Número de ejecuciones: {len(seeds)}")
        print(f"Semillas: {seeds}")
        print(f"{'=' * 80}\n")

        results = []
        for i, seed in enumerate(seeds, 1):
            print(f"\n--- Ejecución {i}/{len(seeds)} (Semilla: {seed}) ---")
            result = self.run_single_experiment(
                seed, mode, verbose, apply_preprocessing
            )
            results.append(result)

            # Mostrar resumen de esta ejecución
            print(f"✓ Completada en {result['execution_time']:.4f}s")

        # Calcular estadísticas
        statistics = self._calculate_statistics(results)

        return {
            "individual_results": results,
            "statistics": statistics,
            "configuration": {
                "matrix_path": self.matrix_path,
                "mode": mode,
                "initial_strategy": self.initial_strategy,
                "max_iterations": self.max_iterations,
                "seeds": seeds,
                "num_runs": len(seeds),
            },
        }

    def _calculate_statistics(self, results: List[Dict]) -> Dict:
        """
        Calcula estadísticas agregadas de múltiples ejecuciones.

        Args:
            results: Lista de resultados individuales

        Returns:
            Diccionario con estadísticas (media, min, max, std)
        """
        metrics = [
            "execution_time",
            "solution_size",
            "reduction",
            "reduction_percentage",
            "tssr",
            "fdcloss",
            "iterations",
            "improvements",
        ]

        statistics = {}
        for metric in metrics:
            values = [r[metric] for r in results]
            statistics[metric] = {
                "mean": np.mean(values),
                "min": np.min(values),
                "max": np.max(values),
                "std": np.std(values),
                "values": values,
            }

        return statistics

    def print_statistics_report(self, experiment_results: Dict):
        """
        Imprime un reporte detallado de las estadísticas del experimento.

        Args:
            experiment_results: Resultado de run_multiple_experiments
        """
        stats = experiment_results["statistics"]
        config = experiment_results["configuration"]

        print(f"\n{'=' * 80}")
        print("REPORTE DE ESTADÍSTICAS - DISEÑO EXPERIMENTAL")
        print(f"{'=' * 80}")
        print(f"\nCONFIGURACIÓN:")
        print(f"  Archivo: {config['matrix_path']}")
        print(f"  Modo de preprocesamiento: {config['mode']}")
        print(f"  Estrategia inicial: {config['initial_strategy']}")
        print(f"  Número de ejecuciones: {config['num_runs']}")
        print(f"  Semillas: {config['seeds']}")

        print(f"\n{'=' * 80}")
        print("RESULTADOS AGREGADOS")
        print(f"{'=' * 80}\n")

        # Tiempo de ejecución
        exec_time = stats["execution_time"]
        print("TIEMPO DE EJECUCIÓN (segundos):")
        print(f"  Media:           {exec_time['mean']:>10.4f}s")
        print(f"  Mínimo:          {exec_time['min']:>10.4f}s")
        print(f"  Máximo:          {exec_time['max']:>10.4f}s")
        print(f"  Desv. Estándar:  {exec_time['std']:>10.4f}s")

        # Tamaño de solución
        sol_size = stats["solution_size"]
        print("\nTAMAÑO DE SOLUCIÓN (tests):")
        print(f"  Media:           {sol_size['mean']:>10.2f}")
        print(f"  Mínimo:          {sol_size['min']:>10.0f}")
        print(f"  Máximo:          {sol_size['max']:>10.0f}")
        print(f"  Desv. Estándar:  {sol_size['std']:>10.2f}")

        # Reducción
        reduction = stats["reduction"]
        print("\nREDUCCIÓN (tests eliminados):")
        print(f"  Media:           {reduction['mean']:>10.2f}")
        print(f"  Mínimo:          {reduction['min']:>10.0f}")
        print(f"  Máximo:          {reduction['max']:>10.0f}")
        print(f"  Desv. Estándar:  {reduction['std']:>10.2f}")

        # Porcentaje de reducción
        red_pct = stats["reduction_percentage"]
        print("\nPORCENTAJE DE REDUCCIÓN (%):")
        print(f"  Media:           {red_pct['mean']:>10.2f}%")
        print(f"  Mínimo:          {red_pct['min']:>10.2f}%")
        print(f"  Máximo:          {red_pct['max']:>10.2f}%")
        print(f"  Desv. Estándar:  {red_pct['std']:>10.2f}%")

        # TSSR
        tssr = stats["tssr"]
        print("\nTSSR (Test Suite Size Reduction):")
        print(f"  Media:           {tssr['mean']:>10.4f}")
        print(f"  Mínimo:          {tssr['min']:>10.4f}")
        print(f"  Máximo:          {tssr['max']:>10.4f}")
        print(f"  Desv. Estándar:  {tssr['std']:>10.4f}")

        # FDCLOSS
        fdcloss = stats["fdcloss"]
        print("\nFDCLOSS (Fault Detection Capability Loss):")
        print(f"  Media:           {fdcloss['mean']:>10.4f}")
        print(f"  Mínimo:          {fdcloss['min']:>10.4f}")
        print(f"  Máximo:          {fdcloss['max']:>10.4f}")
        print(f"  Desv. Estándar:  {fdcloss['std']:>10.4f}")

        # Iteraciones
        iterations = stats["iterations"]
        print("\nITERACIONES:")
        print(f"  Media:           {iterations['mean']:>10.2f}")
        print(f"  Mínimo:          {iterations['min']:>10.0f}")
        print(f"  Máximo:          {iterations['max']:>10.0f}")
        print(f"  Desv. Estándar:  {iterations['std']:>10.2f}")

        # Mejoras
        improvements = stats["improvements"]
        print("\nMEJORAS:")
        print(f"  Media:           {improvements['mean']:>10.2f}")
        print(f"  Mínimo:          {improvements['min']:>10.0f}")
        print(f"  Máximo:          {improvements['max']:>10.0f}")
        print(f"  Desv. Estándar:  {improvements['std']:>10.2f}")

        print(f"\n{'=' * 80}\n")

    def run_deterministic_experiment(
        self, seed: int = 42, mode: Literal["A", "B", "C"] = "A"
    ) -> Dict:
        """
        Ejecuta un experimento con algoritmo determinista (una sola semilla).

        Para algoritmos deterministas como greedy puro, solo se necesita
        una ejecución con una semilla fija.

        Args:
            seed: Semilla fija
            mode: Modo de preprocesamiento

        Returns:
            Diccionario con el resultado único
        """
        print(f"\n{'=' * 80}")
        print("EXPERIMENTO DETERMINISTA - HILL CLIMBING TSM")
        print(f"{'=' * 80}")
        print(f"Archivo de matriz: {self.matrix_path}")
        print(f"Modo de preprocesamiento: {mode}")
        print(f"Estrategia inicial: {self.initial_strategy}")
        print(f"Semilla fija: {seed}")
        print("(Algoritmo determinista - una sola ejecución)")
        print(f"{'=' * 80}\n")

        result = self.run_single_experiment(seed, mode, verbose=True)

        print(f"\n{'=' * 80}")
        print("RESULTADO ÚNICO")
        print(f"{'=' * 80}")
        print(f"Tiempo de ejecución: {result['execution_time']:.4f}s")
        print(f"Tamaño de solución: {result['solution_size']} tests")
        print(
            f"Reducción: {result['reduction']} tests ({result['reduction_percentage']:.2f}%)"
        )
        print(f"TSSR: {result['tssr']:.4f}")
        print(f"FDCLOSS: {result['fdcloss']:.4f}")
        print(f"Iteraciones: {result['iterations']}")
        print(f"Mejoras: {result['improvements']}")
        print(f"{'=' * 80}\n")

        return result
