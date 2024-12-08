import itertools as it
from pathlib import Path

import numpy as np

XMAS = "XMAS"
XMAS_2 = "MAS"
CHAR_TO_INT = {"X": 0, "M": 1, "A": 2, "S": 3}

def _read_and_process_file(filename: Path) -> np.ndarray:
    """
    Reads a CSV file and processes its content into a NumPy array.

    Args:
        filename (Path): The path to the CSV file to be read.

    Returns:
        np.ndarray: A NumPy array with processed data where each character
            is converted to an integer (CHAR_TO_INT mapping).
    """
    with open(filename) as f:
        lines = f.read().splitlines()

    return np.array(
        [[CHAR_TO_INT[char] for char in line] for line in lines]
    )

def _is_xmas(arr, xmas: str = XMAS, check_reverse: bool = False) -> bool:
    """
    Checks if a given array represents the encoded form of the specified
    `xmas` string.

    This function compares the input array with the numerical encoding
    of the `xmas` string, using a predefined mapping `CHAR_TO_INT`.
    Optionally, it can also check the reverse encoding of the string.

    Args:
        arr (list[int]): The array to check, where each element is an integer
            representation of a character.
        xmas (str): The target string to compare against, defaulting to a
            predefined constant `XMAS`.
        check_reverse (bool): Whether to check if `arr` matches the reverse
            encoding of `xmas`.

    Returns:
        bool: True if `arr` matches the encoded or reverse-encoded `xmas`,
            False otherwise.
    """
    if len(arr) != len(xmas):
        return False

    if check_reverse:
        return (
            arr == [CHAR_TO_INT[char] for char in xmas] or arr
            == [CHAR_TO_INT[char] for char in xmas[::-1]]
        )
    else:
        return arr == [CHAR_TO_INT[char] for char in xmas]

def first_exercise(filename: Path):
    input_matrix = _read_and_process_file(filename)
    directions_each = list(it.product(range(-1, 2, 1), repeat=2))

    matrix_comparisons = np.empty(input_matrix.shape, dtype=object)
    for (i, j), value in np.ndenumerate(input_matrix):
        matrix_comparisons[i, j] = np.array(
            [
                [
                    (i + direction[0] * step, j + direction[1] * step)
                    for step in range(len(XMAS))
                ]
                for direction in directions_each
                if direction != (0, 0)
            ]
        )

    matrix_with_checks = np.zeros(input_matrix.shape, dtype=int)

    for (i, j), value in np.ndenumerate(matrix_comparisons):
        matrix_with_checks[i, j] = 0

        for array in value:
            array_to_check = [
                input_matrix[i, j]
                for i, j in array
                if (
                    0 <= i < input_matrix.shape[0]
                    and 0 <= j < input_matrix.shape[1]
                )
            ]

            if _is_xmas(array_to_check):
                matrix_with_checks[i, j] += 1

    return int(matrix_with_checks.sum())

def second_exercise(filename: Path):
    input_matrix = _read_and_process_file(filename)

    matrix_comparisons = np.empty(input_matrix.shape, dtype=object)
    for (i, j), _ in np.ndenumerate(input_matrix):
        matrix_comparisons[i, j] = np.array(
            [
                [
                    (i + direction[0], j + direction[1])
                    for direction in directions_each
                ]
                for directions_each in [
                    [(-1, -1), (0, 0), (1, 1)],
                    [(1, -1), (0, 0), (-1, 1)]
                ]
            ]
        )

    matrix_with_checks = np.zeros(input_matrix.shape, dtype=int)

    for (i, j), value in np.ndenumerate(matrix_comparisons):
        matrix_with_checks[i, j] = 0

        for array in value:
            array_to_check = [
                input_matrix[i, j]
                for i, j in array
                if (
                    0 <= i < input_matrix.shape[0]
                    and 0 <= j < input_matrix.shape[1]
                )
            ]

            if _is_xmas(array_to_check, xmas=XMAS_2, check_reverse=True):
                matrix_with_checks[i, j] += 1

    return int((matrix_with_checks == 2).sum())
