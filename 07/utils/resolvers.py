import itertools as it
import operator
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

MAP_OPERATORS = {
    0: operator.add,
    1: operator.mul,
    2: operator.concat
}

@dataclass
class Equation:
    """Represents a mathematical equation with a target result and a
    list of numbers.

    Attributes:
        result (int): The target result of the equation.
        numbers (list): A list of integers used in the equation.
    """
    result: int
    numbers: list

    def __post_init__(self):
        self.result = int(self.result)
        self.numbers = [int(number) for number in self.numbers]

def _read_and_process_file(filename: Path) -> list:
    """Reads and processes a file containing equations.

    The file is expected to have equations in the format
    `result: num1 num2 ...`, where `result` is the target value, and `num1`,
    `num2`, etc., are numbers to be used with operators to reach the target.

    Args:
        filename (Path): Path to the file containing the equations.

    Returns:
        list: A list of `Equation` objects parsed from the file.
    """
    with open(filename) as f:
        equations = [
            Equation(i[0], i[1].split(" "))
            for i in [
                element.split(": ")
                for element in f.read().split("\n")
            ]
        ]

    return equations

def _solve_equations(equations: list, operators: list):
    """Solves a list of equations by finding combinations of operators
    that satisfy them.

    For each equation, tries all possible combinations of the provided operators
    to determine if the target result can be achieved. Tracks unique solutions
    to avoid duplicates.

    Args:
        equations (list): A list of `Equation` objects to solve.
        operators (list): A list of operator keys (0 for addition, 1 for
            multiplication, 2 for concatenation).

    Returns:
        int: The sum of the results of all solved equations.
    """
    dict_equations_solved = defaultdict(list)
    result = 0

    for equation in equations:
        operator_combinations = (
            it
            .product(
                operators,
                repeat=len(equation.numbers) - 1
            )
        )

        for operator_combination in operator_combinations:
            operations = zip(
                equation.numbers,
                equation.numbers[1:],
                operator_combination
            )

            operation_result = 0
            for index, operation in enumerate(operations):
                if equation.numbers in dict_equations_solved[equation.result]:
                    continue

                if index == 0:
                    left_number = operation[0]
                else:
                    left_number = operation_result

                right_number = operation[1]
                operator_key = operation[2]

                if operator_key != 2:
                    operation_result = MAP_OPERATORS[operator_key](
                        left_number, right_number
                    )
                else:
                    operation_result = int(
                        MAP_OPERATORS[operator_key](
                            str(left_number), str(right_number)
                        )
                    )

                if operation_result > equation.result:
                    break

            if equation.result == operation_result:
                result += equation.result
                dict_equations_solved[equation.result].append(
                    equation.numbers
                )
    return result

def first_exercise(filename: Path):
    equations = _read_and_process_file(filename)

    return _solve_equations(
        equations,
        operators=list(MAP_OPERATORS.keys())[:2]
    )

def second_exercise(filename: Path):
    equations = _read_and_process_file(filename)

    return _solve_equations(
        equations,
        operators=MAP_OPERATORS.keys()
    )
