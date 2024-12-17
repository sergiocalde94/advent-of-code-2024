from collections import defaultdict
from pathlib import Path

import numpy as np

START_POSITION = 0
FINISH_POSITION = 9

def _read_and_process_file(filename: Path) -> list:
    """Reads a topographic map from a file and converts it into a
    2D numpy array.

    Each line in the file corresponds to a row in the topographic map,
    and each character in the line is converted into an integer.

    Args:
        filename (Path): Path to the file containing the topographic map.

    Returns:
        np.array: A 2D numpy array representing the topographic map.
    """
    with open(filename) as f:
        topographic_map_raw = (
            f
            .read()
            .split("\n")
        )

    return np.array([
        [int(char) for char in row]
        for row in topographic_map_raw
    ])

def _start_indexes(topographic_map: np.array) -> np.array:
    """Finds the coordinates of all starting positions in the topographic map.

    The starting positions are represented by the value `START_POSITION`.

    Args:
        topographic_map (np.array): The topographic map as a 2D numpy array.

    Returns:
        zip: A zip object containing the (x, y) coordinates of all starting positions.
    """
    return zip(*np.where(topographic_map == START_POSITION))

def _get_neighbors(topographic_map: np.array,
                   x: int,
                   y: int) -> list:
    """Gets the neighboring positions of a given cell in the topographic map.

    Only orthogonal neighbors (up, down, left, right) are considered; diagonal
    neighbors are excluded.

    Args:
        topographic_map (np.array): The topographic map as a 2D numpy array.
        x (int): The x-coordinate of the current position.
        y (int): The y-coordinate of the current position.

    Returns:
        list: A list of tuples representing the coordinates of the neighboring
            positions.
    """
    neighbors = []

    for x_offset in [-1, 0, 1]:
        for y_offset in [-1, 0, 1]:
            is_diagonal = (abs(x_offset) == abs(y_offset))

            if x_offset == 0 and y_offset == 0 or is_diagonal:
                continue

            x_neighbor = x + x_offset
            y_neighbor = y + y_offset

            if (
                0 <= x_neighbor < topographic_map.shape[0]
                and 0 <= y_neighbor < topographic_map.shape[1]
            ):
                neighbors.append((x_neighbor, y_neighbor))

    return neighbors

def _recursive_search(topographic_map: np.array,
                      x: int,
                      y: int,
                      current_position: int,
                      hiking_trail: list = []) -> list:
    """Recursively searches for hiking trails that follow sequential
    topographic values.

    The function explores neighboring positions and continues the search if the
    next position has a value equal to the current position + 1. The search ends
    when the `FINISH_POSITION` value is reached.

    Args:
        topographic_map (np.array): The topographic map as a 2D numpy array.
        x (int): The x-coordinate of the current position.
        y (int): The y-coordinate of the current position.
        current_position (int): The current topographic value being checked.
        hiking_trail (list, optional): A list of positions in the current trail.

    Returns:
        list: A list of positions representing the completed hiking trail.
    """
    if topographic_map[x, y] == FINISH_POSITION:
        return hiking_trail + [(x, y)]

    routes = []
    for neighbor in _get_neighbors(topographic_map, x, y):
        if topographic_map[neighbor] == current_position + 1:
            routes.extend(
                _recursive_search(
                    topographic_map,
                    x=neighbor[0],
                    y=neighbor[1],
                    current_position=current_position + 1,
                    hiking_trail=hiking_trail + [(x, y)]
                )
            )
    else:
        return routes

def _split_hiking_routes(routes: list, x: int, y: int) -> list:
    """Splits the hiking routes into distinct sub-routes.

    Routes are split whenever they return to the starting position `(x, y)`.

    Args:
        routes (list): A list of positions representing the hiking routes.
        x (int): The x-coordinate of the starting position.
        y (int): The y-coordinate of the starting position.

    Returns:
        list: A list of sub-routes, where each sub-route is a list of positions.
    """
    split_routes = []
    current_route = []

    for position in routes:
        if position == (x, y) and current_route:
            split_routes.append(current_route)
            current_route = []
        current_route.append(position)

    if current_route:
        split_routes.append(current_route)

    return split_routes

def first_exercise(filename: Path):
    topographic_map = _read_and_process_file(filename)
    dict_routes = defaultdict(list)

    for x, y in _start_indexes(topographic_map):
        dict_routes[(x, y)] = _split_hiking_routes(
            _recursive_search(
                topographic_map, x, y, current_position=START_POSITION
            ), x, y
        )

    routes_uniques = {
        (route[0], route[-1])
        for routes in dict_routes.values()
        for route in routes
    }

    return len(routes_uniques)

def second_exercise(filename: Path):
    topographic_map = _read_and_process_file(filename)
    dict_routes = defaultdict(list)

    for x, y in _start_indexes(topographic_map):
        dict_routes[(x, y)] = _split_hiking_routes(
            _recursive_search(
                topographic_map, x, y, current_position=START_POSITION
            ), x, y
        )

    return sum(
        len(routes)
        for routes in dict_routes.values()
    )
