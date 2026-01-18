"""
Hill Climbing Algorithm for Test Suite Minimization (TSM)

Este módulo implementa el algoritmo de Hill Climbing para minimizar
un conjunto de tests manteniendo la misma cobertura de requisitos.
"""

from pathlib import Path
from typing import Literal

import numpy as np

from src.preprocessing import PreprocessingModes


class TestSuiteMinimizer:
    def __init__(self, matrix_path):
        """
        Inicializa el minimizador con una matriz de cobertura.

        Args:
            matrix_path (str): Ruta al archivo de matriz binaria
        """
        self.matrix_path = Path(matrix_path)
        self.coverage_matrix = None
        self.num_requirements = 0
        self.num_tests = 0

    def load_matrix(self):
        """
        Carga la matriz de cobertura desde el archivo.

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

        # Convertir a numpy array
        self.coverage_matrix = np.array(matrix_data, dtype=int)
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
        print("=" * 60 + "\n")

    def run(self, mode: Literal["A", "B", "C"] = "A"):
        print("\n\nIniciando Test Suite Minimizer...")

        # Cargar la matriz
        self.load_matrix()

        # Mostrar información
        self.print_matrix_info()

        # Aplicar preprocesamiento según el modo seleccionado
        match mode:
            case "A":
                print("Aplicando Preprocesamiento Modo A...")
                preprocessing_result = (
                    PreprocessingModes().apply_preprocessing_to_minimizer(self, mode)
                )
            case "B":
                print("Aplicando Preprocesamiento Modo B...")
                preprocessing_result = (
                    PreprocessingModes().apply_preprocessing_to_minimizer(self, mode)
                )
            case "C":
                print("Aplicando Preprocesamiento Modo C...")
                preprocessing_result = (
                    PreprocessingModes().apply_preprocessing_to_minimizer(self, mode)
                )
