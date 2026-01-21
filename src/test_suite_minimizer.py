from pathlib import Path
from typing import Literal, Optional

import numpy as np

from src.hill_climbing_optimizer import HillClimbingOptimizer
from src.preprocessing import PreprocessingModes


class TestSuiteMinimizer:
    def __init__(
        self,
        matrix_path,
        max_iterations: Optional[int] = 1000,
        initial_strategy: Optional[
            Literal["all", "greedy", "essential", "random"]
        ] = "all",
    ):
        """
        Inicializa el minimizador con una matriz de cobertura.

        Args:
            matrix_path (str): Ruta al archivo de matriz binaria
        """
        self.matrix_path = Path(matrix_path)
        self.coverage_matrix = None
        self.num_requirements = 0
        self.num_tests = 0
        self.max_iterations = max_iterations
        self.initial_strategy = initial_strategy

    def load_matrix(self):
        """
        Carga la matriz de cobertura desde el archivo.

        IMPORTANTE: En el archivo, cada FILA representa un TEST y cada COLUMNA un REQUISITO.
        La matriz se transpone para que internamente sea: requisitos x tests

        Returns:
            numpy.ndarray: Matriz de cobertura (requisitos x tests)
        """
        # Leer el archivo línea por línea
        with open(self.matrix_path, "r") as f:
            lines = f.readlines()

        # Convertir cada línea en una lista de enteros
        matrix_data = []
        for line in lines:
            line = line.strip()
            if line:  # Ignorar líneas vacías
                row = [int(char) for char in line if char in "01"]
                matrix_data.append(row)

        # Convertir a numpy array: cada fila es un test, cada columna un requisito
        matrix_tests_x_reqs = np.array(matrix_data, dtype=int)

        # TRANSPONER: necesitamos requisitos x tests internamente
        self.coverage_matrix = matrix_tests_x_reqs.T

        self.num_requirements = self.coverage_matrix.shape[0]
        self.num_tests = self.coverage_matrix.shape[1]

        print(
            f"Matriz cargada: {self.num_requirements} requisitos x {self.num_tests} tests"
        )
        return self.coverage_matrix

    def get_requirement_coverage(self):
        """
        Calcula cuántos tests cubren cada requisito.

        Returns:
            numpy.ndarray: Array con el número de tests que cubren cada requisito
        """
        # Sumar por filas (axis=1): suma todos los tests para cada requisito
        coverage_per_requirement = np.sum(self.coverage_matrix, axis=1)  # type: ignore
        return coverage_per_requirement

    def get_test_coverage(self):
        """
        Calcula cuántos requisitos cubre cada test.

        Returns:
            numpy.ndarray: Array con el número de requisitos que cubre cada test
        """
        # Sumar por columnas (axis=0): suma todos los requisitos para cada test
        coverage_per_test = np.sum(self.coverage_matrix, axis=0)  # type: ignore
        return coverage_per_test

    def print_matrix_info(self):
        """
        Muestra información detallada sobre la matriz de cobertura.
        """
        if self.coverage_matrix is None:
            print("Error: Primero debes cargar la matriz con load_matrix()")
            return

        req_coverage = self.get_requirement_coverage()
        test_coverage = self.get_test_coverage()

        print("\n" + "=" * 60)
        print("INFORMACIÓN DE LA MATRIZ DE COBERTURA")
        print("=" * 60)
        print(
            f"\nDimensiones: {self.num_requirements} requisitos x {self.num_tests} tests"
        )
        print(f"\nTotal de requisitos: {self.num_requirements}")
        print(f"Total de tests: {self.num_tests}")

        print("\n--- COBERTURA POR REQUISITO ---")
        print(f"Requisitos cubiertos por al menos 1 test: {np.sum(req_coverage > 0)}")
        print(f"Requisitos no cubiertos: {np.sum(req_coverage == 0)}")
        print(f"Cobertura media por requisito: {np.mean(req_coverage):.2f} tests")
        print(f"Cobertura mínima: {np.min(req_coverage)} tests")
        print(f"Cobertura máxima: {np.max(req_coverage)} tests")

        print("\n--- COBERTURA POR TEST ---")
        print(f"Tests que cubren al menos 1 requisito: {np.sum(test_coverage > 0)}")
        print(f"Tests que no cubren nada: {np.sum(test_coverage == 0)}")
        print(f"Cobertura media por test: {np.mean(test_coverage):.2f} requisitos")
        print(f"Cobertura mínima: {np.min(test_coverage)} requisitos")
        print(f"Cobertura máxima: {np.max(test_coverage)} requisitos")

    def check_solution_coverage(self, test_subset):
        """
        Verifica si un subconjunto de tests cubre todos los requisitos cubiertos originalmente.

        Args:
            test_subset (list): Lista de índices de tests

        Returns:
            bool: True si cubre todos los requisitos, False en caso contrario
        """
        if not test_subset:
            return False

        # Obtener requisitos cubiertos por el subconjunto
        subset_matrix = self.coverage_matrix[:, test_subset]
        covered_requirements = np.sum(subset_matrix, axis=1) > 0

        # Obtener requisitos originalmente cubiertos
        original_covered = np.sum(self.coverage_matrix, axis=1) > 0

        # Verificar que todos los requisitos originales sigan cubiertos
        return np.all(covered_requirements >= original_covered)

    def calculate_coverage_percentage(self, test_subset):
        """
        Calcula el porcentaje de requisitos cubiertos por un subconjunto.

        Args:
            test_subset (list): Lista de índices de tests

        Returns:
            float: Porcentaje de cobertura (0-100)
        """
        if not test_subset:
            return 0.0

        subset_matrix = self.coverage_matrix[:, test_subset]
        covered_requirements = np.sum(subset_matrix, axis=1) > 0
        total_requirements = np.sum(np.sum(self.coverage_matrix, axis=1) > 0)

        if total_requirements == 0:
            return 100.0

        return (np.sum(covered_requirements) / total_requirements) * 100

    def run(self, mode: Literal["A", "B", "C"] = "A", apply_preprocessing: bool = True):
        print("\n\nIniciando Test Suite Minimizer...")

        # Cargar la matriz
        self.load_matrix()

        # Mostrar información
        self.print_matrix_info()

        # Aplicar preprocesamiento según el modo seleccionado si apply_preprocessing es True
        preprocessing_result = None
        if apply_preprocessing:
            match mode:
                case "A":
                    preprocessing_result = (
                        PreprocessingModes().apply_preprocessing_to_minimizer(
                            self, mode
                        )
                    )
                case "B":
                    preprocessing_result = (
                        PreprocessingModes().apply_preprocessing_to_minimizer(
                            self, mode
                        )
                    )
                case "C":
                    preprocessing_result = (
                        PreprocessingModes().apply_preprocessing_to_minimizer(
                            self, mode
                        )
                    )

            # IMPORTANTE: Actualizar la matriz del minimizer con la matriz preprocesada
            # Esto asegura que el Hill Climbing use la matriz reducida
            if preprocessing_result is not None:
                self.coverage_matrix = preprocessing_result["reduced_matrix"]
        else:
            print("\n⚠️  PREPROCESAMIENTO DESACTIVADO - Usando matriz original")
            print(
                f"Dimensiones: {self.coverage_matrix.shape[0]} requisitos x {self.coverage_matrix.shape[1]} tests\n"
            )
            self.num_requirements = self.coverage_matrix.shape[0]
            self.num_tests = self.coverage_matrix.shape[1]

            print(
                f"\nMatriz después del preprocesamiento: {self.num_requirements} requisitos x {self.num_tests} tests"
            )

        # Ejecutar Hill Climbing Optimizer
        optimizer = HillClimbingOptimizer(self)
        optimization_result = optimizer.optimize(
            initial_strategy=self.initial_strategy,  # type: ignore
            max_iterations=self.max_iterations,  # type: ignore
            verbose=True,
        )

        return {
            "preprocessing": preprocessing_result,
            "optimization": optimization_result,
        }
