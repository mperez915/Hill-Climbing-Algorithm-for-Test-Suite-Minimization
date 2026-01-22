"""
Módulo de Preprocesamiento para Test Suite Minimization

Implementa los tres modos de reducción:
- Modo A: Reducción de tests (elimina tests redundantes o dominados)
- Modo B: Reducción de requisitos (elimina requisitos redundantes o dominados)
- Modo C: Aplica ambas reducciones de forma iterativa
"""

from typing import Literal

import numpy as np


class PreprocessingModes:
    """
    Clase para aplicar diferentes modos de preprocesamiento a la matriz de cobertura.
    """

    @staticmethod
    def _apply_mode_a(coverage_matrix):
        """
        Modo A: Reducción de tests

        Elimina:
        1. Tests que no cubren ningún requisito (tests vacíos)
        2. Tests duplicados (cubren exactamente los mismos requisitos)
        3. Tests dominados (otro test cubre todos sus requisitos y más)

        Dominancia: t1 domina a t2 si cubre todos los requisitos de t2 y al menos uno más.

        Args:
            coverage_matrix (numpy.ndarray): Matriz original (tests x requisitos)

        Returns:
            tuple: (matriz_reducida, indices_tests_mantenidos, info_eliminacion)
        """
        num_tests, num_requirements = coverage_matrix.shape
        tests_to_keep = []

        # Información de eliminación
        empty_tests = []
        duplicate_tests = []
        dominated_tests = []

        # 1. Identificar tests vacíos (no cubren ningún requisito)
        for test_idx in range(num_tests):
            if np.sum(coverage_matrix[test_idx, :]) == 0:
                empty_tests.append(test_idx)

        # Tests no vacíos
        non_empty_tests = [i for i in range(num_tests) if i not in empty_tests]

        # 2 y 3. Identificar duplicados y dominados
        # Marcamos tests para eliminar
        to_remove = set()

        for i in range(len(non_empty_tests)):
            test_i = non_empty_tests[i]

            if test_i in to_remove:
                continue

            coverage_i = coverage_matrix[test_i, :]

            for j in range(i + 1, len(non_empty_tests)):
                test_j = non_empty_tests[j]

                if test_j in to_remove:
                    continue

                coverage_j = coverage_matrix[test_j, :]

                # Verificar si son duplicados
                if np.array_equal(coverage_i, coverage_j):
                    # Duplicado - eliminar el segundo (j)
                    duplicate_tests.append(test_j)
                    to_remove.add(test_j)
                else:
                    # Verificar dominancia (SOLO UNIDIRECCIONAL: i -> j)
                    # test_i domina a test_j si cubre todo lo de j y más
                    i_covers_j = np.all(coverage_j <= coverage_i)
                    i_covers_more = not np.array_equal(coverage_i, coverage_j)

                    if i_covers_j and i_covers_more:
                        # test_i domina a test_j, eliminar test_j
                        dominated_tests.append(test_j)
                        to_remove.add(test_j)
                    # NOTA: No permitimos que test_j elimine a test_i
                    # porque test_i ya fue validado contra todos los tests anteriores.
                    # Esto previene cadenas de dominancia que reducen demasiado la suite.

        # Tests que se mantienen
        tests_to_keep = [t for t in non_empty_tests if t not in to_remove]

        # Si no queda ningún test, mantener al menos uno
        if len(tests_to_keep) == 0:
            tests_to_keep = non_empty_tests[:1] if non_empty_tests else [0]

        # Crear matriz reducida
        reduced_matrix = coverage_matrix[tests_to_keep, :]

        elimination_info = {
            "empty": empty_tests,
            "duplicate": duplicate_tests,
            "dominated": dominated_tests,
            "total_eliminated": len(empty_tests)
            + len(duplicate_tests)
            + len(dominated_tests),
            "original_tests": num_tests,
            "remaining_tests": len(tests_to_keep),
        }

        return reduced_matrix, tests_to_keep, elimination_info

    @staticmethod
    def _apply_mode_b(coverage_matrix):
        """
        Modo B: Reducción de requisitos

        Elimina:
        1. Requisitos no cubiertos por ningún test
        2. Requisitos dominados

        Dominancia: r1 domina a r2 si el conjunto de tests que cubre r2 es un
        subconjunto estricto de los tests que cubren r1 (r1 es más difícil de satisfacer).

        Args:
            coverage_matrix (numpy.ndarray): Matriz original (tests x requisitos)

        Returns:
            tuple: (matriz_reducida, indices_requisitos_mantenidos, info_eliminacion)
        """
        num_tests, num_requirements = coverage_matrix.shape
        requirements_to_keep = []

        # Información de eliminación
        uncovered_reqs = []
        dominated_reqs = []

        # 1. Identificar requisitos no cubiertos
        for req_idx in range(num_requirements):
            if np.sum(coverage_matrix[:, req_idx]) == 0:
                uncovered_reqs.append(req_idx)

        # Requisitos cubiertos
        covered_reqs = [i for i in range(num_requirements) if i not in uncovered_reqs]

        # 2. Identificar requisitos dominados
        to_remove = set()

        for i in range(len(covered_reqs)):
            req_i = covered_reqs[i]

            if req_i in to_remove:
                continue

            # Obtener tests que cubren req_i
            tests_covering_i = set(np.where(coverage_matrix[:, req_i] == 1)[0])

            for j in range(len(covered_reqs)):
                if i == j:
                    continue

                req_j = covered_reqs[j]

                if req_j in to_remove:
                    continue

                # Obtener tests que cubren req_j
                tests_covering_j = set(np.where(coverage_matrix[:, req_j] == 1)[0])

                # req_i domina a req_j si:
                # - tests_covering_j es subconjunto estricto de tests_covering_i
                # - req_i es más difícil de satisfacer (más tests lo cubren)
                if tests_covering_j < tests_covering_i:  # < es subconjunto estricto
                    # req_i domina a req_j, eliminar req_j
                    dominated_reqs.append(req_j)
                    to_remove.add(req_j)

        # Requisitos que se mantienen
        requirements_to_keep = [r for r in covered_reqs if r not in to_remove]

        # Si no queda ningún requisito, mantener al menos uno
        if len(requirements_to_keep) == 0:
            requirements_to_keep = covered_reqs[:1] if covered_reqs else [0]

        # Crear matriz reducida
        reduced_matrix = coverage_matrix[:, requirements_to_keep]

        elimination_info = {
            "uncovered": uncovered_reqs,
            "dominated": dominated_reqs,
            "total_eliminated": len(uncovered_reqs) + len(dominated_reqs),
            "original_requirements": num_requirements,
            "remaining_requirements": len(requirements_to_keep),
        }

        return reduced_matrix, requirements_to_keep, elimination_info

    @staticmethod
    def _apply_mode_c(coverage_matrix, max_iterations=10):
        """
        Modo C: Aplica ambas reducciones (A y B) de forma iterativa

        Aplica reducción de tests y requisitos alternadamente hasta que:
        - No se puedan hacer más reducciones, o
        - Se alcance el número máximo de iteraciones

        Args:
            coverage_matrix (numpy.ndarray): Matriz original (tests x requisitos)
            max_iterations (int): Número máximo de iteraciones

        Returns:
            tuple: (matriz_reducida, indices_tests_mantenidos, indices_reqs_mantenidos, info)
        """
        current_matrix = coverage_matrix.copy()
        original_test_indices = list(range(coverage_matrix.shape[0]))
        original_req_indices = list(range(coverage_matrix.shape[1]))

        iteration = 0
        total_tests_eliminated = 0
        total_reqs_eliminated = 0

        iteration_details = []

        while iteration < max_iterations:
            iteration += 1
            changes_made = False
            iter_info = {
                "iteration": iteration,
                "start_shape": current_matrix.shape,
                "tests_eliminated": 0,
                "reqs_eliminated": 0,
            }

            # Aplicar reducción de tests (Modo A)
            reduced_matrix_a, kept_test_indices, test_info = (
                PreprocessingModes._apply_mode_a(current_matrix)
            )

            if test_info["total_eliminated"] > 0:
                changes_made = True
                total_tests_eliminated += test_info["total_eliminated"]
                iter_info["tests_eliminated"] = test_info["total_eliminated"]

                # Actualizar índices originales
                original_test_indices = [
                    original_test_indices[i] for i in kept_test_indices
                ]
                current_matrix = reduced_matrix_a

            # Aplicar reducción de requisitos (Modo B)
            reduced_matrix_b, kept_req_indices, req_info = (
                PreprocessingModes._apply_mode_b(current_matrix)
            )

            if req_info["total_eliminated"] > 0:
                changes_made = True
                total_reqs_eliminated += req_info["total_eliminated"]
                iter_info["reqs_eliminated"] = req_info["total_eliminated"]

                # Actualizar índices originales
                original_req_indices = [
                    original_req_indices[i] for i in kept_req_indices
                ]
                current_matrix = reduced_matrix_b

            iter_info["end_shape"] = current_matrix.shape
            iteration_details.append(iter_info)

            # Si no hubo cambios, terminar
            if not changes_made:
                break

        combined_info = {
            "iterations": iteration,
            "iteration_details": iteration_details,
            "total_tests_eliminated": total_tests_eliminated,
            "total_reqs_eliminated": total_reqs_eliminated,
            "original_shape": coverage_matrix.shape,
            "final_shape": current_matrix.shape,
            "reduction_percentage_tests": (
                1 - current_matrix.shape[0] / coverage_matrix.shape[0]
            )
            * 100
            if coverage_matrix.shape[0] > 0
            else 0,
            "reduction_percentage_reqs": (
                1 - current_matrix.shape[1] / coverage_matrix.shape[1]
            )
            * 100
            if coverage_matrix.shape[1] > 0
            else 0,
        }

        return (
            current_matrix,
            original_test_indices,
            original_req_indices,
            combined_info,
        )

    @staticmethod
    def _print_preprocessing_results(mode, result_info):
        """
        Imprime los resultados del preprocesamiento de forma legible.

        Args:
            mode (str): Modo aplicado ('A', 'B', 'C')
            result_info (dict): Información retornada por el modo de preprocesamiento
        """
        print(f"\n{'=' * 70}")
        print(f"RESULTADOS DEL PREPROCESAMIENTO - MODO {mode}")
        print(f"{'=' * 70}")

        if mode == "A":
            info = result_info
            print("\n--- REDUCCIÓN DE TESTS ---")
            print(f"Tests originales: {info['original_tests']}")
            print(f"Tests vacíos eliminados: {len(info['empty'])}")
            print(f"Tests duplicados eliminados: {len(info['duplicate'])}")
            print(f"Tests dominados eliminados: {len(info['dominated'])}")
            print(f"Total tests eliminados: {info['total_eliminated']}")
            print(f"Tests restantes: {info['remaining_tests']}")

            if info["original_tests"] > 0:
                reduction_pct = (
                    info["total_eliminated"] / info["original_tests"]
                ) * 100
                print(f"Reducción: {reduction_pct:.2f}%")

            if info["empty"]:
                print(
                    f"\nTests vacíos: {info['empty'][:10]}{'...' if len(info['empty']) > 10 else ''}"
                )
            if info["duplicate"]:
                print(
                    f"Tests duplicados: {info['duplicate'][:10]}{'...' if len(info['duplicate']) > 10 else ''}"
                )
            if info["dominated"]:
                print(
                    f"Tests dominados: {info['dominated'][:10]}{'...' if len(info['dominated']) > 10 else ''}"
                )

        elif mode == "B":
            info = result_info
            print("\n--- REDUCCIÓN DE REQUISITOS ---")
            print(f"Requisitos originales: {info['original_requirements']}")
            print(f"Requisitos no cubiertos eliminados: {len(info['uncovered'])}")
            print(f"Requisitos dominados eliminados: {len(info['dominated'])}")
            print(f"Total requisitos eliminados: {info['total_eliminated']}")
            print(f"Requisitos restantes: {info['remaining_requirements']}")

            if info["original_requirements"] > 0:
                reduction_pct = (
                    info["total_eliminated"] / info["original_requirements"]
                ) * 100
                print(f"Reducción: {reduction_pct:.2f}%")

            if info["uncovered"]:
                print(
                    f"\nRequisitos no cubiertos: {info['uncovered'][:10]}{'...' if len(info['uncovered']) > 10 else ''}"
                )
            if info["dominated"]:
                print(
                    f"Requisitos dominados: {info['dominated'][:10]}{'...' if len(info['dominated']) > 10 else ''}"
                )

        elif mode == "C":
            info = result_info
            print("\n--- REDUCCIÓN COMBINADA (ITERATIVA) ---")
            print(f"Iteraciones realizadas: {info['iterations']}")
            print(
                f"\nDimensiones originales: {info['original_shape'][0]} tests x {info['original_shape'][1]} requisitos"
            )
            print(
                f"Dimensiones finales: {info['final_shape'][0]} tests x {info['final_shape'][1]} requisitos"
            )

            print("\nTests:")
            print(f"  Total eliminados: {info['total_tests_eliminated']}")
            print(f"  Reducción: {info['reduction_percentage_tests']:.2f}%")

            print("\nRequisitos:")
            print(f"  Total eliminados: {info['total_reqs_eliminated']}")
            print(f"  Reducción: {info['reduction_percentage_reqs']:.2f}%")

            print("\n--- DETALLE POR ITERACIÓN ---")
            for detail in info["iteration_details"]:
                if detail["tests_eliminated"] > 0 or detail["reqs_eliminated"] > 0:
                    print(
                        f"Iteración {detail['iteration']}: "
                        f"{detail['tests_eliminated']} tests, "
                        f"{detail['reqs_eliminated']} requisitos eliminados "
                        f"→ {detail['end_shape'][0]}x{detail['end_shape'][1]}"
                    )

        print(f"{'=' * 70}\n")

    def apply_preprocessing_to_minimizer(
        self, minimizer, mode: Literal["A", "B", "C"] = "A"
    ):
        """
        Aplica preprocesamiento a un objeto TestSuiteMinimizer.

        Args:
            minimizer: Objeto TestSuiteMinimizer con matriz cargada
            mode (str): Modo de preprocesamiento ('A', 'B', 'C')

        Returns:
            dict: Diccionario con la información del preprocesamiento
        """
        if minimizer.coverage_matrix is None:
            print("Error: Primero debes cargar la matriz con load_matrix()")
            return None

        mode = mode.upper()  # type: ignore
        original_matrix = minimizer.coverage_matrix.copy()

        result = {
            "mode": mode,
            "original_matrix": original_matrix,
            "original_shape": original_matrix.shape,
        }

        if mode == "A":
            reduced_matrix, kept_tests, info = self._apply_mode_a(original_matrix)
            result.update(
                {
                    "reduced_matrix": reduced_matrix,
                    "kept_test_indices": kept_tests,
                    "kept_req_indices": list(range(original_matrix.shape[1])),
                    "info": info,
                }
            )
            self._print_preprocessing_results("A", info)

        elif mode == "B":
            reduced_matrix, kept_reqs, info = self._apply_mode_b(original_matrix)
            result.update(
                {
                    "reduced_matrix": reduced_matrix,
                    "kept_test_indices": list(range(original_matrix.shape[0])),
                    "kept_req_indices": kept_reqs,
                    "info": info,
                }
            )
            self._print_preprocessing_results("B", info)

        elif mode == "C":
            reduced_matrix, kept_tests, kept_reqs, info = self._apply_mode_c(
                original_matrix
            )
            result.update(
                {
                    "reduced_matrix": reduced_matrix,
                    "kept_test_indices": kept_tests,
                    "kept_req_indices": kept_reqs,
                    "info": info,
                }
            )
            self._print_preprocessing_results("C", info)

        else:
            print(f"Error: Modo '{mode}' no reconocido. Use 'A', 'B' o 'C'.")
            return None

        return result
