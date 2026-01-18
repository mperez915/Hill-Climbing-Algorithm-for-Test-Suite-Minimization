import os

from src.hill_climbing import TestSuiteMinimizer


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    matrix_file = os.path.join(script_dir, "matrices", "matrix_7_60_1.txt")

    minimizer = TestSuiteMinimizer(matrix_file)
    minimizer.run("A")


if __name__ == "__main__":
    main()
