from collections import deque
from pathlib import Path

import numpy as np

START = (0, 0)
SAFE = "."
CORRUPTED = "#"


def _read_and_process_file(filename: Path) -> tuple:
    """Reads and processes the input file into a memory space and a
    list of corrupted coordinates.

    The input file contains a list of corrupted memory locations in
    the format `x,y`.

    Args:
        filename (Path): Path to the input file.

    Returns:
        tuple: A tuple containing:
            - memory_space (np.array): A 2D numpy array initialized to `SAFE`.
            - fails (list): A list of tuples representing corrupted memory
                locations.
    """
    with open(filename) as f:
        fails_raw = f.read().split()

    fails = [tuple(map(int, fail.split(","))) for fail in fails_raw]

    max_y = max([fail[1] for fail in fails]) + 1
    max_x = max([fail[0] for fail in fails]) + 1

    memory_space = np.full((max_y, max_x), SAFE, dtype=str)

    return memory_space, fails

def _solve_memory_space(memory_space: np.array,
                        start: tuple,
                        end: tuple) -> int:
    """Finds the shortest path from `start` to `end` in the memory space
    using BFS.

    The memory space consists of safe (`SAFE`) and corrupted (`CORRUPTED`)
    cells. Movement is restricted to safe cells.

    Args:
        memory_space (np.array): A 2D numpy array representing the memory space.
        start (tuple): The starting coordinates (x, y).
        end (tuple): The target coordinates (x, y).

    Returns:
        int: The number of steps in the shortest path, or `float("inf")`
            if no path exists.
    """
    queue = deque([(*start, 0)])

    max_y, max_x = memory_space.shape

    visited = set()

    while queue:
        x, y, steps = queue.popleft()

        if (x, y) == end:
            return steps

        if (x, y) in visited or x < 0 or y < 0 or x >= max_x or y >= max_y:
            continue

        if memory_space[x, y] == CORRUPTED:
            continue

        visited.add((x, y))

        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            queue.append((x + dx, y + dy, steps + 1))

    return float("inf")

def first_exercise(filename: Path, bytes: int = 1_024):
    memory_space, fails = _read_and_process_file(filename)

    coords_x, coords_y = zip(*fails[:bytes])
    memory_space[coords_y, coords_x] = CORRUPTED

    end_x, end_y = memory_space.shape
    end = (end_x - 1, end_y - 1)

    return _solve_memory_space(
        memory_space, start=START, end=end
    )


def second_exercise(filename: Path):
    _, fails = _read_and_process_file(filename)

    number_of_bytes = 1
    while True:
        if first_exercise(filename, bytes=number_of_bytes) == float("inf"):
            break
        else:
            number_of_bytes += 1

    return ",".join(map(str, fails[number_of_bytes - 1]))
