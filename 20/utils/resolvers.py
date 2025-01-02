from collections import deque
from pathlib import Path

import numpy as np

START = "S"
END = "E"
WALL = "#"
COST_MOVEMENT = 1
MAX_CHEAT_SIZE_AFTER_DEPRECATION = 20


def _read_and_process_file(filename: Path) -> tuple:
    """Reads and processes the input maze file into a 2D numpy array.

    Args:
        filename (Path): Path to the input file containing the maze.

    Returns:
        np.array: A 2D numpy array representing the maze.
    """
    with open(filename) as f:
        maze_raw = f.read().split()

    maze = np.array([list(line) for line in maze_raw])

    return maze

def _solve_maze_best_score(maze: np.array,
                           start: tuple,
                           end: tuple,
                           visited_scores=dict) -> int:
    """Solves the maze using BFS and calculates the shortest path cost
    from start to end.

    Args:
        maze (np.array): A 2D numpy array representing the maze.
        start (tuple): The starting coordinates (x, y).
        end (tuple): The ending coordinates (x, y).
        visited_scores (dict): A dictionary to store the cost for each
            visited cell.

    Returns:
        int: The cost of the shortest path, or `float("inf")` if no path exists.
    """
    queue = deque([(*start, 0)])

    max_y, max_x = maze.shape

    while queue:
        x, y, score = queue.popleft()

        if (x, y) == end:
            visited_scores[(x, y)] = score
            return score

        is_visited = (x, y) in visited_scores
        is_out_of_bounds = x < 0 or y < 0 or x >= max_x or y >= max_y

        if is_visited or is_out_of_bounds:
            continue

        if maze[x, y] == WALL:
            continue

        visited_scores[(x, y)] = score

        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            queue.append((x + dx, y + dy, score + COST_MOVEMENT))

    return float("inf")

def _number_of_cheats(maze: np.array,
                      visited_scores: dict,
                      at_least: int) -> list:
    """Counts the number of cheat moves (skipping over walls) in the maze.

    Args:
        maze (np.array): A 2D numpy array representing the maze.
        visited_scores (dict): A dictionary of scores for visited cells.
        at_least (int): The minimum time threshold to classify as a cheat.

    Returns:
        int: The number of cheat moves detected.
    """
    all_movements = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    all_movements_next = [(2, 0), (-2, 0), (0, 2), (0, -2)]

    number_of_cheats = 0
    for position, time in visited_scores.items():
        x, y = position
        for movement, movement_next in zip(all_movements, all_movements_next):
            dx, dy = movement
            dx_next, dy_next = movement_next

            if maze[x + dx, y + dy] != WALL:
                continue

            cheat_time = visited_scores.get((x + dx_next, y + dy_next), time)
            if cheat_time - time > at_least:
                number_of_cheats += 1

    return number_of_cheats

def _number_of_cheats_after_deprecation(maze: np.array,
                                        visited_scores: dict,
                                        at_least: int) -> list:
    """Counts the number of cheats after a defined deprecation period.

    Args:
        maze (np.array): A 2D numpy array representing the maze.
        visited_scores (dict): A dictionary of scores for visited cells.
        at_least (int): The minimum time threshold to classify as a cheat.

    Returns:
        int: The number of cheats detected after the deprecation period.
    """
    number_of_cheats = 0

    non_cheating_path = sorted(visited_scores, key=visited_scores.get)

    for later_index in range(at_least + 1, len(non_cheating_path)):
        for earlier_index in range(later_index - at_least):
            point_a = non_cheating_path[earlier_index]
            point_b = non_cheating_path[later_index]

            manhattan_distance = sum(
                abs(a - b) for a, b in zip(point_a, point_b)
            )

            is_le_max_cheat_size = (
                manhattan_distance <= MAX_CHEAT_SIZE_AFTER_DEPRECATION
            )

            # later - earlier is the distance without cheating
            is_lt_threshold = (
                later_index - earlier_index - manhattan_distance
            ) >= at_least

            if is_le_max_cheat_size and is_lt_threshold:
                number_of_cheats += 1

    return number_of_cheats

def first_exercise(filename: Path, at_least: int = 100) -> int:
    maze = _read_and_process_file(filename)

    start_x, start_y = map(int, np.where(maze == START))
    end_x, end_y = map(int, np.where(maze == END))

    visited_scores = {}

    _ = _solve_maze_best_score(
        maze=maze,
        start=(start_x, start_y),
        end=(end_x, end_y),
        visited_scores=visited_scores,
    )

    return _number_of_cheats(maze, visited_scores, at_least)

def second_exercise(filename: Path, at_least: int = 100):
    maze = _read_and_process_file(filename)

    start_x, start_y = map(int, np.where(maze == START))
    end_x, end_y = map(int, np.where(maze == END))

    visited_scores = {}

    _ = _solve_maze_best_score(
        maze=maze,
        start=(start_x, start_y),
        end=(end_x, end_y),
        visited_scores=visited_scores,
    )

    return _number_of_cheats_after_deprecation(maze, visited_scores, at_least)
