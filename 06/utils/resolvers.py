from collections import defaultdict
from pathlib import Path

import numpy as np

MAP_DIRECTIONS = {
    "^": np.array([-1, 0]),
    ">": np.array([0, 1]),
    "v": np.array([1, 0]),
    "<": np.array([0, -1])
}

TOGGLE_DIRECTION = {
    "^": ">",
    ">": "v",
    "v": "<",
    "<": "^"
}

def _read_and_process_file(filename: Path) -> list:
    """Reads a file and processes its contents into a padded numpy array representation.

    The function converts characters in the file to numerical representations:
    - "." becomes `0` (walkable path).
    - "^" becomes `1` (starting position).
    - "#" becomes `NaN` (obstacle).

    Pads the resulting matrix with a border of `-1` values to simplify boundary handling.

    Args:
        filename (Path): The path to the input file.

    Returns:
        np.array: A padded numpy array representing the map, where:
                  - `0` indicates walkable paths.
                  - `1` indicates the starting position.
                  - `NaN` indicates obstacles.
                  - `-1` indicates the padded boundary.
    """
    with open(filename) as f:
        map_matrix_raw = (
            f
            .read()
            .replace(".", "0")
            .replace("^", "1")
            .split("\n")
        )

    map_matrix = np.array([
        [np.nan if char == "#" else int(char) for char in row]
        for row in map_matrix_raw
    ])

    return np.pad(
        map_matrix, pad_width=1, mode="constant", constant_values=-1
    )

def _compute_distinct_positions(map_positions: np.array) -> int:
    """Computes the number of distinct positions visited based on the input map.

    Starting at the position marked `1`, the function traverses the map
    following the specified directions and tracks all distinct positions
    visited. It toggles direction when encountering an obstacle (`NaN`).

    Args:
        map_positions (np.array): A numpy array representing the map, where:
                                  - `0` indicates walkable paths.
                                  - `1` indicates the starting position.
                                  - `NaN` indicates obstacles.
                                  - `-1` indicates boundaries.

    Returns:
        int: The count of distinct positions visited during the traversal.
    """
    position = np.argwhere(map_positions == 1)[0]
    current_position = map_positions[*position]
    direction = "^"
    dict_distinct_positions = {}

    while current_position != -1:
        dict_distinct_positions[tuple(position)] = 1

        row, column = position

        position_front = position + MAP_DIRECTIONS[direction]

        if np.isnan(map_positions[*position_front]):
            direction = TOGGLE_DIRECTION[direction]
        else:
            position = position_front

        current_position = map_positions[*position]

    return dict_distinct_positions

def first_exercise(filename: Path):
    map_positions = _read_and_process_file(filename)

    dict_distinct_positions = _compute_distinct_positions(map_positions)

    return sum(dict_distinct_positions.values())

def second_exercise(filename: Path):
    map_positions = _read_and_process_file(filename)

    dict_distinct_positions = _compute_distinct_positions(map_positions)

    visited_positions = [
        np.array(k)
        for k in dict_distinct_positions.keys()
    ]
    n_obstructions = 0
    first_position = np.argwhere(map_positions == 1)[0]

    for i, j in visited_positions:
        position = first_position
        direction = "^"
        dict_distinct_positions_and_directions = defaultdict(list)

        map_positions_temp = map_positions.copy()

        if map_positions_temp[i, j] == 1:
            continue

        map_positions_temp[i, j] = np.nan

        while True:
            loop_key = (tuple(position), direction)

            if direction in dict_distinct_positions_and_directions[loop_key]:
                n_obstructions += 1
                break

            dict_distinct_positions_and_directions[loop_key].append(
                direction
            )

            row, column = position

            position_front = position + MAP_DIRECTIONS[direction]

            if np.isnan(map_positions_temp[*position_front]):
                direction = TOGGLE_DIRECTION[direction]
            else:
                position = position_front

            if map_positions_temp[*position] == -1:
                break

    return n_obstructions
