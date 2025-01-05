import itertools as it
import re
from collections import deque
from dataclasses import dataclass
from functools import cache
from pathlib import Path

import numpy as np

ACTIVATE = "A"

NUMERICAL_KEYPAD = np.array(
    [
        ["7", "8", "9"],
        ["4", "5", "6"],
        ["1", "2", "3"],
        [None, "0", ACTIVATE]
    ]
)

DIRECTIONAL_KEYPAD = np.array([[None, "^", ACTIVATE], ["<", "v", ">"]])

DICT_MOVEMENTS = {(-1, 0): "^", (1, 0): "v", (0, -1): "<", (0, 1): ">"}

ALL_MOVEMENTS = [(0, -1), (-1, 0), (1, 0), (0, 1)]

PRIORITY_MOVEMENTS_COST = {"<": 3, "^": 2, "v": 2, ">": 1}

REGEX_NUMERIC = re.compile(r"\d+")


@dataclass
class Code:
    """Represents an operation code with a complexity value.

    Attributes:
        operation (str): The sequence of movements.
        complexity (int): The complexity factor associated with the operation.
    """
    operation: str
    complexity: int


def _read_and_process_file(filename: Path) -> tuple:
    """Reads and processes the input file containing operation codes.

    Args:
        filename (Path): Path to the input file.

    Returns:
        list[Code]: A list of `Code` objects containing operations and their
            complexities.
    """
    with open(filename) as f:
        operations = f.read().split()

    codes = [
        Code(
            operation=operation,
            complexity=int(REGEX_NUMERIC.search(operation).group()),
        )
        for operation in operations
    ]

    return codes

def _compute_shortest_path(is_numerical_keyboard: bool,
                           operation: str,
                           position: str = ACTIVATE) -> list:
    """Computes the shortest path from the starting position to the
    target operation.

    Args:
        is_numerical_keyboard (bool): Whether to use a numerical keypad.
        operation (str): The target operation to reach.
        position (str, optional): The starting position. Defaults to ACTIVATE.

    Returns:
        list: The shortest sequence of movements to reach the target.
    """
    keypad = NUMERICAL_KEYPAD if is_numerical_keyboard else DIRECTIONAL_KEYPAD

    start_position = map(int, np.where(keypad == position))
    max_x, max_y = keypad.shape

    queue = deque([(*start_position, "")])

    best_so_far = float("inf")
    movements_candidates = []
    while queue:
        x, y, movements = queue.popleft()

        if len(movements) > best_so_far:
            return _fix_shortest_movements(movements_candidates)

        is_out_of_bounds = x < 0 or y < 0 or x >= max_x or y >= max_y

        if is_out_of_bounds or (keypad[x, y] is None):
            continue

        if keypad[x, y] == operation:
            if len(movements) < best_so_far:
                best_so_far = len(movements)
                movements_candidates = [movements]
            elif len(movements) == best_so_far:
                movements_candidates.append(movements)

        for dx, dy in ALL_MOVEMENTS:
            next_x, next_y = x + dx, y + dy

            queue.append((next_x, next_y, movements + DICT_MOVEMENTS[(dx, dy)]))

@cache
def _get_shortest_map(is_numerical_keyboard: bool) -> dict:
    """Generates a map of the shortest paths between all key combinations.

    Args:
        is_numerical_keyboard (bool): Whether to use a numerical keypad.

    Returns:
        dict: A dictionary mapping `(start, end)` to the shortest movement
            sequence.
    """
    keypad = NUMERICAL_KEYPAD if is_numerical_keyboard else DIRECTIONAL_KEYPAD
    flat_keypad = keypad.flatten()
    combinations = {}
    for char_previous, char in it.product(flat_keypad, repeat=2):
        if char_previous is None or char is None:
            continue

        combinations[(char_previous, char)] = _compute_shortest_path(
            is_numerical_keyboard=is_numerical_keyboard,
            operation=char,
            position=char_previous,
        ) + ACTIVATE

    return combinations

def _fix_shortest_movements(movements: str) -> list[str]:
    """Determines the most optimal movement sequence.

    Args:
        movements (str): The set of movement sequences.

    Returns:
        str: The optimal movement sequence.
    """
    if movements == [""]:
        return ""

    movements_cost = {
        movement: PRIORITY_MOVEMENTS_COST[movement[0]]
        for movement in movements
    }

    for movement in movements:
        for index, chars in enumerate(zip(movement[1:], movement)):
            char, prev_char = chars

            movements_cost[movement] += (
                PRIORITY_MOVEMENTS_COST[char] / (index + 2)
            )

            if char == prev_char:
                movements_cost[movement] *= 2

    return max(movements, key=movements_cost.get)

@cache
def _recursive_length(movements,
                      number_of_iterations,
                      is_numerical_keyboard=False) -> int:
    """Recursively calculates the total length of movement sequences.

    Args:
        movements (str): The movement sequence.
        number_of_iterations (int): The number of iterations to consider.
        is_numerical_keyboard (bool, optional): Whether to use a numerical
            keypad. Defaults to False.

    Returns:
        int: The total length of movements after the specified iterations.
    """
    if number_of_iterations == 0:
        return len(movements)

    char_previous = ACTIVATE
    total_length = 0
    shortest_mapping = _get_shortest_map(
        is_numerical_keyboard=is_numerical_keyboard
    )

    for char in movements:
        total_length += _recursive_length(
            shortest_mapping[(char_previous, char)],
            number_of_iterations - 1
        )

        char_previous = char
    return total_length

def _compute_complexity(number_of_directional_keypads: int,
                        codes: list[Code]) -> int:
    """Computes the total complexity for a given set of operation codes.

    Args:
        number_of_directional_keypads (int): The number of directional keypads.
        codes (list[Code]): A list of `Code` objects representing operations.

    Returns:
        int: The computed complexity value.
    """
    total_complexity = 0
    for code in codes:
        total_length_code = _recursive_length(
            movements=code.operation,
            number_of_iterations=number_of_directional_keypads + 1,
            is_numerical_keyboard=True,
        )

        total_complexity += (
            total_length_code * code.complexity
        )

    return total_complexity

def first_exercise(filename: Path) -> int:
    codes = _read_and_process_file(filename)

    complexity = _compute_complexity(
        number_of_directional_keypads=2,
        codes=codes,
    )

    return complexity

def second_exercise(filename: Path):
    codes = _read_and_process_file(filename)

    complexity = _compute_complexity(
        number_of_directional_keypads=25,
        codes=codes,
    )

    return complexity
