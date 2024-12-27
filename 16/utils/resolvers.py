from collections import defaultdict
from pathlib import Path

import numpy as np

START = "S"
END = "E"
EMPTY = "."
WALL = "#"

COST_STEP = 1
COST_ROTATION = 1_000
DIRECTIONS = ["<", ">", "^", "v"]
START_DIRECTION = ">"

DICT_MOVEMENTS = {
    "<": np.array([0, -1]),
    ">": np.array([0, 1]),
    "^": np.array([-1, 0]),
    "v": np.array([1, 0]),
}

TOGGLE_DIRECTION_RIGHT = {"^": ">", ">": "v", "v": "<", "<": "^"}
TOGGLE_DIRECTION_LEFT = {"^": "<", "<": "v", "v": ">", ">": "^"}


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
                           x: int,
                           y: int,
                           direction: str = ">",
                           score: int = 0,
                           visited_scores: set = None) -> int:
    """Recursively solves the maze to find the best score.

    The score accounts for the number of steps and rotations required to reach
    the end of the maze.

    Args:
        maze (np.array): A 2D numpy array representing the maze.
        x (int): The starting x-coordinate.
        y (int): The starting y-coordinate.
        direction (str, optional): The initial direction. Defaults to ">".
        score (int, optional): The initial score. Defaults to 0.
        visited_scores (dict, optional): A dictionary to store visited cells
            and scores.

    Returns:
        int: The best score to reach the end of the maze.
    """
    global best_global

    if score >= best_global:
        return np.inf

    if visited_scores is None:
        visited_scores = defaultdict(int)

    visited_scores_key = (int(x), int(y), direction)

    if visited_scores_key in visited_scores:
        if score >= visited_scores[visited_scores_key]:
            return np.inf

    visited_scores[visited_scores_key] = score

    next_position = maze[x, y]

    if next_position == END:
        if score < best_global:
            best_global = score
        return score

    if next_position == WALL:
        return np.inf

    solutions = []

    possible_directions = [
        TOGGLE_DIRECTION_LEFT[direction],
        direction,
        TOGGLE_DIRECTION_RIGHT[direction]
    ]

    for direction_next in possible_directions:
        direction_x, direction_y = DICT_MOVEMENTS[direction_next]

        solutions.append(
            _solve_maze_best_score(
                maze,
                x=x + direction_x,
                y=y + direction_y,
                direction=direction_next,
                score=score + (
                    COST_STEP + (
                        COST_ROTATION if direction_next != direction
                        else 0
                    )
                ),
                visited_scores=visited_scores
            )
        )

    return min(solutions)

def _backtrack_paths(maze: np.array,
                     start: tuple,
                     end: tuple,
                     visited_scores: dict,
                     known_best_score: int) -> list:
    """Backtracks through the maze to find all optimal paths.

    Args:
        maze (np.array): A 2D numpy array representing the maze.
        start (tuple): The starting position (x, y).
        end (tuple): The ending position (x, y).
        visited_scores (dict): A dictionary of visited cells and their scores.
        known_best_score (int): The best score found in the maze.

    Returns:
        list: A list of all optimal paths.
    """
    start_x, start_y = start
    end_x, end_y = end

    dict_cells = {}
    for cell, score in visited_scores.items():
        position_x, position_y, _ = cell
        if score <= known_best_score:
            if maze[position_x, position_y] == WALL:
                continue

            dict_cells[(position_x, position_y)] = [
                score
                for cell, score in visited_scores.items()
                if cell[:2] == (position_x, position_y)
            ]

    all_paths = []

    def _find_paths(current_cell, current_path, remaining_score):
        if current_cell == start:
            all_paths.append(current_path[::-1])
            return None

        x, y = current_cell

        for direction, movement in DICT_MOVEMENTS.items():
            dx, dy = movement
            prev_x = int(x - dx)
            prev_y = int(y - dy)
            prev_cell = (prev_x, prev_y)

            if prev_cell in dict_cells:
                expected_score = remaining_score - COST_STEP
                expected_score_with_rotation = expected_score - COST_ROTATION

                if expected_score in dict_cells[prev_cell]:
                    _find_paths(
                        prev_cell,
                        current_path + [prev_cell],
                        expected_score
                    )

                if expected_score_with_rotation in dict_cells[prev_cell]:
                    _find_paths(
                        prev_cell,
                        current_path + [prev_cell],
                        expected_score_with_rotation
                    )

    _find_paths((end_x, end_y), [(end_x, end_y)], known_best_score)

    return all_paths

def _wrap_global_variable(func):
    """Wrapper to reset the global best score variable.

    Args:
        func (function): The function to wrap.

    Returns:
        function: The wrapped function.
    """
    def wrapper(*args, **kwargs):
        global best_global
        best_global = float("inf")
        result = func(*args, **kwargs)
        best_global = float("inf")
        return result
    return wrapper

@_wrap_global_variable
def first_exercise(filename: Path):
    maze = _read_and_process_file(filename)

    start_x, start_y = map(int, np.where(maze == START))

    best_score = _solve_maze_best_score(
        maze=maze, x=start_x, y=start_y
    )

    return best_score

@_wrap_global_variable
def second_exercise(filename: Path):
    maze = _read_and_process_file(filename)

    start_x, start_y = map(int, np.where(maze == START))
    end_x, end_y = map(int, np.where(maze == END))

    visited_scores = defaultdict(int)

    best_score = _solve_maze_best_score(
        maze=maze, x=start_x, y=start_y, visited_scores=visited_scores
    )

    all_seats = _backtrack_paths(
        maze=maze,
        start=(start_x, start_y),
        end=(end_x, end_y),
        visited_scores=visited_scores,
        known_best_score=best_score
    )

    number_of_seats = len({(x, y) for path in all_seats for x, y in path})

    return number_of_seats
