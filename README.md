# Hill Climbing Algorithm for Test Suite Minimization

## Descripción

Implementación del algoritmo **Hill Climbing** para minimización de conjuntos de test (Test Suite Minimization - TSM). El algoritmo reduce el número de tests manteniendo la cobertura completa de requisitos, con tres modos de preprocesamiento configurables.

---

## Lenguaje y Versión

- **Lenguaje**: Python
- **Versión**: 3.12.10

---

## Dependencias

El proyecto requiere las siguientes bibliotecas de Python:

| Paquete | Versión | Descripción |
|---------|---------|-------------|
| `numpy` | 2.4.1 | Operaciones con matrices y arrays |
| `pandas` | 2.3.3 | Análisis de datos (opcional para estadísticas) |
| `python-dateutil` | 2.9.0.post0 | Manejo de fechas |
| `pytz` | 2025.2 | Zonas horarias |
| `typing` | 3.7.4.3 | Type hints |

### Instalación de Dependencias

#### Opción 1: Usando `requirements.txt`

```bash
pip install -r requirements.txt
```

#### Opción 2: Usando entorno virtual (recomendado)

```bash
# Crear entorno virtual
python3 -m venv .venv

# Activar entorno virtual
# En macOS/Linux:
source .venv/bin/activate
# En Windows:
.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

## Estructura del Proyecto

```
Hill-Climbing-Algorithm-for-Test-Suite-Minimization/
│
├── main.py                    # Script principal para ejecución experimental
├── test_integration.py        # Tests de integración completos
├── requirements.txt           # Dependencias del proyecto
├── README.md                 # Este archivo
│
├── matrices/                 # Matrices de cobertura de entrada
│   ├── matrix_7_60_1.txt
│   ├── matrix_18_213_1.txt
│   ├── matrix_33_890_1.txt
│   ├── matrix_36_508_1.txt
│   └── matrix_94_3647_1.txt
│
├── results/                  # Resultados de experimentos (generados)
│   └── *.txt
│
└── src/                      # Código fuente
    ├── __init__.py
    ├── test_suite_minimizer.py    # Clase principal
    ├── hill_climbing_optimizer.py  # Optimizador Hill Climbing
    ├── preprocessing.py            # Modos de preprocesamiento (A, B, C)
    ├── experimental_design.py      # Diseño experimental
    └── utils.py                    # Funciones auxiliares
```

## Ejecución

### 1. Ejecución del Experimento Completo

Ejecuta el algoritmo para todas las matrices disponibles en la carpeta `matrices/`:

```bash
python main.py
```

**Salida**: Genera archivos de resultados en la carpeta `results/` con el formato:
```
matrix_<nombre>_<timestamp>.txt
```

#### Parámetros de línea de comandos:

El script acepta los siguientes parámetros opcionales:

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `--mode` | A\|B\|C | B | Modo de preprocesamiento |
| `--verbose` | flag | False | Mostrar información detallada |
| `--initial-strategy` | all\|greedy\|essential\|random | random | Estrategia inicial |
| `--seeds` | int... | 42 123 456 789 1024 | Lista de semillas |
| `--max-iterations` | int | 1000 | Iteraciones máximas |

#### Ejemplos de uso:

```bash
# Configuración por defecto
python main.py

# Modo A con salida detallada
python main.py --mode A --verbose

# Modo C con estrategia greedy
python main.py --mode C --initial-strategy greedy

# Con semillas personalizadas
python main.py --seeds 10 20 30 40 50

# Combinación de parámetros
python main.py --mode B --seeds 1 2 3 --verbose --max-iterations 500

# Ver ayuda completa
python main.py --help
```

### 2. Ejecución para una Matriz Específica

Crear un script personalizado:

```python
from src.test_suite_minimizer import TestSuiteMinimizer

# Cargar y ejecutar
minimizer = TestSuiteMinimizer(
    matrix_path="matrices/matrix_7_60_1.txt",
    max_iterations=1000,
    initial_strategy="greedy"
)

result = minimizer.run(mode="A")

# Ver resultados
print(f"Solución: {result['optimization']['solution']}")
print(f"Tamaño original: {result['optimization']['original_size']}")
print(f"Tamaño solución: {result['optimization']['solution_size']}")
print(f"Reducción: {result['optimization']['reduction_percentage']:.2f}%")
print(f"Cobertura: {result['optimization']['coverage']:.2f}%")
```

## Modos de Preprocesamiento

### Modo A: Reducción de Tests
Elimina tests:
- Vacíos (no cubren requisitos)
- Duplicados (misma cobertura)
- Dominados (otro test cubre los mismos requisitos y más)

```python
result = minimizer.run(mode="A")
```

### Modo B: Reducción de Requisitos
Elimina requisitos:
- No cubiertos (ningún test los cubre)
- Dominados (sus tests son subconjunto de los de otro requisito)

```python
result = minimizer.run(mode="B")
```

### Modo C: Reducción Iterativa
Aplica los Modos A y B de forma alternada e iterativa hasta que no haya más reducciones posibles.

```python
result = minimizer.run(mode="C")
```

---

## Estrategias Iniciales

El algoritmo soporta diferentes estrategias para generar la solución inicial:

| Estrategia | Descripción |
|------------|-------------|
| `"all"` | Comienza con todos los tests |
| `"greedy"` | Selección greedy (mejor test primero) |
| `"essential"` | Solo tests esenciales (cubren requisitos críticos) |
| `"random"` | Selección aleatoria manteniendo cobertura |

```python
minimizer = TestSuiteMinimizer(
    matrix_path="...",
    initial_strategy="greedy"  # Cambiar aquí
)
```

---

## Formato de Matrices de Entrada

Las matrices deben ser archivos de texto plano (`.txt`) con el siguiente formato:

- Cada **fila** representa un **test**
- Cada **columna** representa un **requisito**
- `1` = el test cubre el requisito
- `0` = el test NO cubre el requisito

**Ejemplo** (`matrix_ejemplo.txt`):
```
10110
01101
11010
00111
```

Esto representa:
- 4 tests (filas)
- 5 requisitos (columnas)
- Test 0 cubre requisitos: 0, 2, 3
- Test 1 cubre requisitos: 1, 2, 4
- etc.

---

## Métricas Calculadas

El algoritmo calcula las siguientes métricas:

### TSSR (Test Suite Size Reduction)
```
TSSR = (tamaño_original - tamaño_solución) / tamaño_original
```
- Rango: [0, 1]
- Interpretación: Mayor es mejor (más reducción)
- Ejemplo: TSSR = 0.75 significa 75% de reducción

### FDCLOSS (Fault Detection Capability Loss)
```
FDCLOSS = 1 - (requisitos_cubiertos_solución / requisitos_cubiertos_original)
```
- Rango: [0, 1]
- Interpretación: Menor es mejor (menos pérdida)
- Ideal: 0.0 (sin pérdida de cobertura)

### Cobertura
```
Cobertura = (requisitos_cubiertos / total_requisitos) × 100
```
- Rango: [0, 100]
- Objetivo: 100% (cobertura completa)

---

## Ejemplo de Uso Completo

```python
from src.experimental_design import ExperimentalDesign

# 1. Crear experimento
experiment = ExperimentalDesign(
    matrix_path="matrices/matrix_7_60_1.txt",
    max_iterations=1000,
    initial_strategy="greedy"
)

# 2. Ejecutar con múltiples semillas
results = experiment.run_multiple_experiments(
    seeds=[42, 123, 456, 789, 1024],
    mode="C",
    verbose=False
)

# 3. Ver estadísticas
print(f"\nEstadísticas del experimento:")
print(f"Media solución: {results['statistics']['mean']['solution_size']:.2f} tests")
print(f"Mejor solución: {results['statistics']['min']['solution_size']} tests")
print(f"TSSR medio: {results['statistics']['mean']['tssr']:.4f}")
print(f"FDCLOSS medio: {results['statistics']['mean']['fdcloss']:.4f}")

# 4. Imprimir reporte completo
experiment.print_statistics_report(results)
```