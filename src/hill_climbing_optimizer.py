"""
Hill Climbing Optimizer for Test Suite Minimization

Este módulo implementa el algoritmo de Hill Climbing para optimizar
conjuntos de tests, manteniendo la cobertura completa de requisitos.
"""

import numpy as np


class HillClimbingOptimizer:
    """
    Optimizador basado en Hill Climbing para minimización de test suites.

    Esta clase implementa el algoritmo de búsqueda local Hill Climbing
    que busca reducir el número de tests manteniendo la cobertura completa.
    """

    def __init__(self, minimizer):
        """
        Inicializa el optimizador con un TestSuiteMinimizer.

        Args:
            minimizer: Instancia de TestSuiteMinimizer con matriz cargada
        """
        self.minimizer = minimizer
        self.coverage_matrix = minimizer.coverage_matrix
        self.num_requirements = minimizer.num_requirements
        self.num_tests = minimizer.num_tests

        if self.coverage_matrix is None:
            raise ValueError("El minimizer debe tener una matriz cargada")

    def generate_initial_solution(self, strategy="all"):
        """
        Genera una solución inicial para el algoritmo.

        Args:
            strategy (str): Estrategia para generar la solución inicial
                          'all' - Todos los tests
                          'greedy' - Selección greedy (mejor test primero)
                          'essential' - Solo tests esenciales

        Returns:
            list: Lista de índices de tests en la solución inicial
        """
        if strategy == "all":
            # Todos los tests
            return list(range(self.num_tests))

        elif strategy == "greedy":
            # Estrategia greedy: añadir el test que cubre más requisitos no cubiertos
            solution = []
            uncovered = set(range(self.num_requirements))

            while uncovered:
                best_test = -1
                best_coverage = 0

                for test_idx in range(self.num_tests):
                    if test_idx in solution:
                        continue

                    # Contar cuántos requisitos no cubiertos cubre este test
                    covered_by_test = set(
                        np.where(self.coverage_matrix[:, test_idx] == 1)[0]
                    )
                    new_coverage = len(covered_by_test & uncovered)

                    if new_coverage > best_coverage:
                        best_coverage = new_coverage
                        best_test = test_idx

                if best_test == -1:
                    break

                solution.append(best_test)
                covered_by_best = set(
                    np.where(self.coverage_matrix[:, best_test] == 1)[0]
                )
                uncovered -= covered_by_best

            return solution

        elif strategy == "essential":
            # Solo tests esenciales (cubren requisitos únicos)
            from utils import get_essential_tests

            essential = get_essential_tests(self.coverage_matrix)
            return sorted(list(essential))

        else:
            raise ValueError(f"Estrategia desconocida: {strategy}")

    def generate_neighbors(self, current_solution):
        """
        Genera vecinos de la solución actual.

        Un vecino se genera:
        - Eliminando un test de la solución actual, O
        - Añadiendo un test no incluido en la solución

        Args:
            current_solution (list): Solución actual

        Returns:
            list: Lista de soluciones vecinas (cada una es una lista de índices)
        """
        neighbors = []
        current_set = set(current_solution)

        # Vecinos por ELIMINACIÓN: quitar un test
        for test_idx in current_solution:
            neighbor = [t for t in current_solution if t != test_idx]
            # Solo considerar si no deja la solución vacía
            if neighbor:
                neighbors.append(neighbor)

        # Vecinos por ADICIÓN: añadir un test no incluido
        for test_idx in range(self.num_tests):
            if test_idx not in current_set:
                neighbor = sorted(current_solution + [test_idx])
                neighbors.append(neighbor)

        return neighbors

    def evaluate_solution(self, solution):
        """
        Evalúa la calidad de una solución.

        Para TSM, queremos:
        1. Minimizar el número de tests
        2. Mantener cobertura completa (100%)

        Args:
            solution (list): Lista de índices de tests

        Returns:
            tuple: (fitness, is_valid)
                  fitness: Valor de fitness (menor es mejor)
                  is_valid: True si mantiene cobertura completa
        """
        if not solution:
            return float("inf"), False

        # Verificar cobertura
        is_valid = self.minimizer.check_solution_coverage(solution)

        # Fitness: número de tests (menor es mejor)
        # Si no es válida, penalizar fuertemente
        if is_valid:
            fitness = len(solution)
        else:
            # Penalización: tests + porcentaje faltante * factor
            coverage_pct = self.minimizer.calculate_coverage_percentage(solution)
            missing_pct = 100 - coverage_pct
            fitness = len(solution) + missing_pct * 100  # Penalización alta

        return fitness, is_valid

    def optimize(
        self,
        initial_solution=None,
        initial_strategy="greedy",
        max_iterations=1000,
        verbose=True,
    ):
        """
        Algoritmo Hill Climbing para Test Suite Minimization.

        El algoritmo:
        1. Parte de una solución inicial
        2. Genera vecinos (añadir/quitar un test)
        3. Evalúa todos los vecinos
        4. Si encuentra un mejor vecino válido, se mueve a él
        5. Repite hasta que no haya mejora (máximo local) o max_iterations

        Args:
            initial_solution (list): Solución inicial (None para generar automáticamente)
            initial_strategy (str): Estrategia si initial_solution es None
            max_iterations (int): Número máximo de iteraciones
            verbose (bool): Mostrar progreso

        Returns:
            dict: Resultado con la mejor solución encontrada y estadísticas
        """
        # Generar solución inicial
        if initial_solution is None:
            current_solution = self.generate_initial_solution(initial_strategy)
        else:
            current_solution = initial_solution.copy()

        current_fitness, current_valid = self.evaluate_solution(current_solution)

        if verbose:
            print(f"\n{'=' * 70}")
            print(f"HILL CLIMBING - TEST SUITE MINIMIZATION")
            print(f"{'=' * 70}")
            print(f"\nSolución inicial: {len(current_solution)} tests")
            print(
                f"Cobertura inicial: {self.minimizer.calculate_coverage_percentage(current_solution):.2f}%"
            )
            print(f"Fitness inicial: {current_fitness:.2f}")

        # Estadísticas
        iteration = 0
        improvements = 0
        evaluations = 1  # Contamos la evaluación inicial
        best_solution = current_solution.copy()
        best_fitness = current_fitness

        history = [
            {
                "iteration": 0,
                "solution_size": len(current_solution),
                "fitness": current_fitness,
                "valid": current_valid,
            }
        ]

        # Bucle principal
        while iteration < max_iterations:
            iteration += 1

            # Generar vecinos
            neighbors = self.generate_neighbors(current_solution)
            evaluations += len(neighbors)

            # Evaluar vecinos
            best_neighbor = None
            best_neighbor_fitness = float("inf")
            best_neighbor_valid = False

            for neighbor in neighbors:
                fitness, is_valid = self.evaluate_solution(neighbor)

                # Solo considerar vecinos válidos (cobertura completa)
                if is_valid and fitness < best_neighbor_fitness:
                    best_neighbor = neighbor
                    best_neighbor_fitness = fitness
                    best_neighbor_valid = is_valid

            # Si encontramos un mejor vecino, movernos a él
            if best_neighbor is not None and best_neighbor_fitness < current_fitness:
                current_solution = best_neighbor
                current_fitness = best_neighbor_fitness
                current_valid = best_neighbor_valid
                improvements += 1

                if verbose and improvements % 10 == 0:
                    print(
                        f"Iteración {iteration}: {len(current_solution)} tests (fitness: {current_fitness:.2f})"
                    )

                # Actualizar mejor solución global
                if current_fitness < best_fitness:
                    best_solution = current_solution.copy()
                    best_fitness = current_fitness

                history.append(
                    {
                        "iteration": iteration,
                        "solution_size": len(current_solution),
                        "fitness": current_fitness,
                        "valid": current_valid,
                    }
                )
            else:
                # No hay mejora - máximo local alcanzado
                if verbose:
                    print(f"\n✓ Máximo local alcanzado en iteración {iteration}")
                break

        # Resultado final
        final_coverage = self.minimizer.calculate_coverage_percentage(best_solution)
        reduction_pct = (1 - len(best_solution) / self.num_tests) * 100

        result = {
            "solution": sorted(best_solution),
            "solution_size": len(best_solution),
            "original_size": self.num_tests,
            "reduction": self.num_tests - len(best_solution),
            "reduction_percentage": reduction_pct,
            "coverage": final_coverage,
            "fitness": best_fitness,
            "iterations": iteration,
            "improvements": improvements,
            "evaluations": evaluations,
            "history": history,
        }

        if verbose:
            print(f"\n{'=' * 70}")
            print(f"RESULTADO FINAL")
            print(f"{'=' * 70}")
            print(f"Tests originales: {self.num_tests}")
            print(f"Tests en solución: {len(best_solution)}")
            print(f"Tests eliminados: {self.num_tests - len(best_solution)}")
            print(f"Reducción: {reduction_pct:.2f}%")
            print(f"Cobertura: {final_coverage:.2f}%")
            print(f"Iteraciones: {iteration}")
            print(f"Mejoras realizadas: {improvements}")
            print(f"Evaluaciones totales: {evaluations}")
            print(f"{'=' * 70}\n")

        return result
