import itertools as it
from pathlib import Path

import numpy as np


def _read_and_process_file(filename: Path) -> list:
    """Reads and processes a file into a 2D numpy array of characters.

    Each line in the file is converted into a list of characters, and all lines
    are combined into a 2D numpy array.

    Args:
        filename (Path): The path to the file to be read.

    Returns:
        np.array: A 2D numpy array where each row corresponds to a line in
            the file, and each column is a character from that line.
    """
    with open(filename) as f:
        lines = f.read().splitlines()

    return np.array(
        [list(line) for line in lines]
    )

def first_exercise(filename: Path):
    matrix = _read_and_process_file(filename)
    antinode_positions = set()

    for element in np.unique(matrix):
        if element == ".":
            continue

        x, y = np.where(matrix == element)

        points = zip(x, y)

        combinations = it.combinations(points, r=2)

        for (x_a, y_a), (x_b, y_b) in combinations:
            antinode_first = np.array([2 * x_b - x_a, 2 * y_b - y_a])
            antinode_second = np.array([2 * x_a - x_b, 2 * y_a - y_b])

            is_inside_antinode_first = (
                (antinode_first < matrix.shape).all()
                and (antinode_first >= 0).all()
            )

            if is_inside_antinode_first:
                antinode_positions.add(tuple(antinode_first))

            is_inside_antinode_second = (
                (antinode_second < matrix.shape).all()
                and (antinode_second >= 0).all()
            )

            if is_inside_antinode_second:
                antinode_positions.add(tuple(antinode_second))

    return len(antinode_positions)

def second_exercise(filename: Path, verbose=False):
    matrix = _read_and_process_file(filename)
    antinode_positions = set()

    for element in np.unique(matrix):
        if element == ".":
            continue

        x, y = np.where(matrix == element)

        points = zip(x, y)

        combinations = it.combinations(points, r=2)

        for (x_a, y_a), (x_b, y_b) in combinations:
            dx = x_b - x_a
            dy = y_b - y_a

            is_inside_antinode_first = True
            antinode_first = np.array([x_a, y_a])

            while is_inside_antinode_first:
                antinode_positions.add(tuple(antinode_first))
                antinode_first = antinode_first - np.array([dx, dy])

                is_inside_antinode_first = (
                    (antinode_first < matrix.shape).all()
                    and (antinode_first >= 0).all()
                )

            is_inside_antinode_second = True
            antinode_second = np.array([x_b, y_b])

            while is_inside_antinode_second:
                antinode_positions.add(tuple(antinode_second))

                antinode_second = antinode_second + np.array([dx, dy])

                is_inside_antinode_second = (
                    (antinode_second < matrix.shape).all()
                    and (antinode_second >= 0).all()
                )

    return len(antinode_positions)
