import itertools as it
from collections import defaultdict
from pathlib import Path

import numpy as np


def _read_and_process_file(filename: Path) -> np.array:
    """Reads a file and converts its contents into a 2D numpy array
    representing the garden.

    Each line in the file corresponds to a row, and each character in the line
    is converted into an element of the array.

    Args:
        filename (Path): Path to the file containing the garden data.

    Returns:
        np.array: A 2D numpy array representing the garden.
    """
    with open(filename) as f:
        garden_raw = np.array(f.read().split("\n"))

    garden = np.array([list(row) for row in garden_raw])

    return garden

def _recursive_build_garden_plant(garden: np.array,
                                  x: int,
                                  y: int,
                                  plant: str,
                                  visited: set = None,
                                  perimeter: set = None,
                                  direction: tuple = (0, 0)) -> list:
    """Recursively identifies all cells and the perimeter of a connected
    plant area.

    Args:
        garden (np.array): A 2D numpy array representing the garden.
        x (int): The x-coordinate of the current position.
        y (int): The y-coordinate of the current position.
        plant (str): The plant type to identify.
        visited (set, optional): A set of already visited cells.
            Defaults to None.
        perimeter (set, optional): A set of perimeter cells.
            Defaults to None.
        direction (tuple, optional): The direction of movement.
            Defaults to (0, 0).

    Returns:
        tuple: A tuple containing:
               - visited (set): All cells belonging to the plant area.
               - perimeter (set): The perimeter cells of the plant area.
    """
    if visited is None:
        visited = set()

    if perimeter is None:
        perimeter = set()

    n_rows, n_columns = garden.shape

    is_outside = x < 0 or y < 0 or x >= n_rows or y >= n_columns

    if is_outside or garden[x, y] != plant or (x, y) in visited:
        if is_outside or garden[x, y] != plant:
            perimeter.add((x, y, direction))
        return visited, perimeter

    visited.add((x, y))

    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        new_x, new_y = x + dx, y + dy

        _recursive_build_garden_plant(
            garden, new_x, new_y, plant, visited, perimeter, direction=(dx, dy)
        )

    return visited, perimeter

def _get_garden_plant(garden: np.array, plant: str) -> np.array:
    """Identifies all connected areas of a specific plant type in the garden.

    Args:
        garden (np.array): A 2D numpy array representing the garden.
        plant (str): The plant type to identify.

    Returns:
        dict: A dictionary where each key is a unique area ID, and each value is
              a tuple containing:
              - visited (set): All cells in the plant area.
              - perimeter (set): The perimeter cells of the plant area.
    """
    x, y = np.where(garden == plant)

    dict_gardens_plant = defaultdict(list)
    incremental_garden = 0

    visited, perimeter = _recursive_build_garden_plant(
        garden, x[0], y[0], plant
    )

    dict_gardens_plant[incremental_garden] = visited.copy(), perimeter.copy()

    for x, y in zip(x, y):
        while (x, y) not in visited:
            incremental_garden += 1

            visited_new, perimeter_new = _recursive_build_garden_plant(
                garden, x, y, plant
            )

            visited.update(visited_new)

            dict_gardens_plant[incremental_garden] = (
                visited_new.copy(),
                perimeter_new.copy(),
            )

    return dict_gardens_plant

def first_exercise(filename: Path):
    garden = _read_and_process_file(filename)

    return sum(
        len(visited) * len(perimeter)
        for plant in np.unique(garden)
        for visited, perimeter in _get_garden_plant(garden, plant).values()
    )

def second_exercise(filename: Path):
    garden = _read_and_process_file(filename)

    garden_plants_all = [
        _get_garden_plant(garden, plant)
        for plant in np.unique(garden)
    ]

    result = 0

    for garden_plants in garden_plants_all:
        for visited, perimeter in garden_plants.values():
            n_sides = 0

            perimeter_abs_directions = [
                (*point, (abs(point[2][0]), abs(point[2][1])))
                for point in perimeter
            ]

            perimeter_sorted_side = sorted(
                perimeter_abs_directions, key=lambda x: x[3]
            )

            for _, group in it.groupby(
                perimeter_sorted_side, key=lambda x: x[3]
            ):
                group_points_ = list(group)
                dx, dy = group_points_[0][2]

                if dx == 0:  # Vertical side
                    group_points = sorted(
                        group_points_, key=lambda x: (x[1], x[2], x[0])
                    )
                else:  # Horizontal side
                    group_points = sorted(
                        group_points_, key=lambda x: (x[0], x[2], x[1])
                    )

                n_sides += 1
                for position_current, position_next in zip(
                    group_points, group_points[1:]
                ):
                    point_a = np.array(position_current[:-2])
                    point_b = np.array(position_next[:-2])

                    manhattan_distance = np.sum(np.abs(point_a - point_b))

                    is_same_point = (manhattan_distance == 0)
                    is_not_adjacent = (manhattan_distance > 1)
                    follow_same_direction = (
                        position_current[2] == position_next[2]
                    )

                    mask_is_side = (
                        is_same_point
                        or is_not_adjacent
                        or not follow_same_direction
                    )

                    if mask_is_side:
                        n_sides += 1

            result += len(visited) * n_sides

    return result
